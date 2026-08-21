from __future__ import annotations

from pathlib import Path
from typing import Any

from .storage import ensure_local_parent, is_remote_uri, spark_path_exists
from .utils import write_json


COLUMNS = ["target", "id", "date", "flag", "user", "text"]


def sentiment140_schema():
    from pyspark.sql.types import IntegerType, StringType, StructField, StructType

    return StructType(
        [StructField("target", IntegerType(), True)]
        + [StructField(name, StringType(), True) for name in COLUMNS[1:]]
    )


def clean_text_expr(column):
    """Spark expression shared by training and prediction."""
    from pyspark.sql import functions as F

    cleaned = F.lower(column)
    cleaned = F.regexp_replace(cleaned, r"https?://\S+|www\.\S+", " ")
    cleaned = F.regexp_replace(cleaned, r"@\w+", " ")
    cleaned = F.regexp_replace(cleaned, r"[^\p{L}\p{N}'\s]", " ")
    return F.trim(F.regexp_replace(cleaned, r"\s+", " "))


def with_parsed_date(frame):
    from pyspark.sql import functions as F

    date_without_weekday = F.regexp_replace(F.col("date"), r"^\w{3}\s+", "")
    date_with_offset = F.regexp_replace(date_without_weekday, "PDT", "-0700")
    date_with_offset = F.regexp_replace(date_with_offset, "PST", "-0800")
    return frame.withColumn(
        "posted_at", F.to_timestamp(date_with_offset, "MMM dd HH:mm:ss Z yyyy")
    )


def read_raw(spark, data_path: str | Path):
    if not is_remote_uri(data_path) and not Path(data_path).is_file():
        raise FileNotFoundError(
            f"Input CSV not found: {data_path}. Download Sentiment140 and place "
            "the training CSV there, or run: python main.py demo"
        )
    if is_remote_uri(data_path):
        try:
            exists = spark_path_exists(spark, data_path)
        except Exception as exc:
            raise RuntimeError(
                f"Cannot connect to remote input {data_path}. Start HDFS and check the URI."
            ) from exc
        if not exists:
            raise FileNotFoundError(f"Remote input CSV not found: {data_path}")
    return (
        spark.read.option("header", False)
        .option("encoding", "ISO-8859-1")
        .option("quote", '"')
        .option("escape", '"')
        .option("mode", "FAILFAST")
        .schema(sentiment140_schema())
        .csv(str(data_path))
    )


def _label_counts(frame) -> dict[str, int]:
    return {
        str(row["target"]): int(row["count"])
        for row in frame.groupBy("target").count().orderBy("target").collect()
    }


def prepare_data(
    spark,
    data_path: str | Path,
    processed_path: str | Path,
    outputs_dir: Path,
):
    from pyspark.sql import functions as F

    raw = read_raw(spark, data_path).cache()
    raw_rows = raw.count()
    if raw_rows == 0:
        raw.unpersist()
        raise ValueError("The input CSV is empty.")

    missing_row = raw.agg(
        *[
            F.sum(F.when(F.col(name).isNull(), 1).otherwise(0)).alias(name)
            for name in COLUMNS
        ]
    ).first()
    missing_counts = {name: int(missing_row[name] or 0) for name in COLUMNS}
    duplicate_id_rows = (
        raw.filter(F.col("id").isNotNull())
        .groupBy("id")
        .count()
        .filter(F.col("count") > 1)
        .agg(F.sum(F.col("count") - 1).alias("duplicates"))
        .first()["duplicates"]
        or 0
    )
    empty_text_rows = raw.filter(
        F.col("text").isNotNull() & (F.length(F.trim(F.col("text"))) == 0)
    ).count()
    invalid_target_rows = raw.filter(~F.col("target").isin(0, 4)).count()

    prepared = (
        raw.filter(F.col("target").isin(0, 4))
        .filter(F.col("id").isNotNull())
        .filter(F.col("text").isNotNull())
        .dropDuplicates(["id"])
        .withColumn("clean_text", clean_text_expr(F.col("text")))
        .filter(F.length(F.col("clean_text")) > 0)
        .withColumn("label", (F.col("target") / F.lit(4)).cast("double"))
    )
    prepared = with_parsed_date(prepared).cache()
    clean_rows = prepared.count()
    clean_label_counts = {
        str(int(row["label"])): int(row["count"])
        for row in prepared.groupBy("label").count().orderBy("label").collect()
    }
    invalid_date_rows = prepared.filter(F.col("posted_at").isNull()).count()
    date_range = prepared.agg(
        F.min("posted_at").alias("min_posted_at"),
        F.max("posted_at").alias("max_posted_at"),
    ).first()

    quality: dict[str, Any] = {
        "source": str(data_path),
        "encoding": "ISO-8859-1",
        "expected_columns": COLUMNS,
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "removed_rows": raw_rows - clean_rows,
        "label_counts_raw": _label_counts(raw),
        "label_counts_clean": clean_label_counts,
        "missing_counts": missing_counts,
        "duplicate_id_rows_removed": int(duplicate_id_rows),
        "empty_text_rows": empty_text_rows,
        "invalid_target_rows": invalid_target_rows,
        "invalid_date_rows": invalid_date_rows,
        "date_parse_success_rate": (
            (clean_rows - invalid_date_rows) / clean_rows if clean_rows else 0.0
        ),
        "min_posted_at_utc": date_range["min_posted_at"],
        "max_posted_at_utc": date_range["max_posted_at"],
        "notes": [
            "Duplicate IDs are removed only from the cleaned analysis data.",
            "Rows with invalid dates remain available for sentiment modeling.",
            "The target distribution describes the dataset construction, not public opinion.",
        ],
    }

    ensure_local_parent(processed_path)
    prepared.write.mode("overwrite").parquet(str(processed_path))
    write_json(outputs_dir / "data_quality.json", quality)
    prepared.unpersist()
    raw.unpersist()
    return quality


def read_prepared(spark, processed_path: str | Path):
    if is_remote_uri(processed_path):
        try:
            exists = spark_path_exists(spark, processed_path)
        except Exception as exc:
            raise RuntimeError(
                f"Cannot connect to processed storage {processed_path}. Start HDFS first."
            ) from exc
    else:
        exists = Path(processed_path).exists()
    if not exists:
        raise FileNotFoundError(
            f"Processed Parquet not found: {processed_path}. Run the prepare command first."
        )
    return spark.read.parquet(str(processed_path))
