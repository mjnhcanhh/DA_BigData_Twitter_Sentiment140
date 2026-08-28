from __future__ import annotations

from pathlib import Path

from .charts import (
    plot_daily,
    plot_hourly,
    plot_label_by_day,
    plot_top_words,
    plot_user_distribution,
)
from .utils import spark_rows_to_dicts, write_csv, write_json


# Negation words are deliberately absent because they matter for sentiment.
DISPLAY_STOPWORDS = [
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from",
    "has", "have", "he", "her", "his", "i", "in", "is", "it", "its", "me", "my", "of",
    "on", "or", "our", "she", "so", "that", "the", "their", "them", "they", "this", "to",
    "was", "we", "were", "with", "you", "your", "sample", "number",
]


def run_analysis(frame, outputs_dir: Path) -> dict:
    from pyspark.sql import Window, functions as F

    tables = outputs_dir / "tables"
    charts = outputs_dir / "charts"
    frame.createOrReplaceTempView("tweets")

    daily_counts = frame.filter(F.col("posted_at").isNotNull()).groupBy(
        F.to_date("posted_at").alias("day")
    ).count().select("day", F.col("count").alias("posts")).orderBy("day")
    day_bounds = daily_counts.agg(
        F.min("day").alias("min_day"), F.max("day").alias("max_day")
    )
    calendar = day_bounds.select(
        F.explode(F.sequence("min_day", "max_day")).alias("day")
    )
    daily = calendar.join(daily_counts, "day", "left").fillna(0, ["posts"]).orderBy("day")

    hourly_counts = frame.filter(F.col("posted_at").isNotNull()).groupBy(
        F.hour("posted_at").alias("hour_utc")
    ).count().select("hour_utc", F.col("count").alias("posts")).orderBy("hour_utc")
    hourly = (
        frame.sparkSession.range(24)
        .select(F.col("id").cast("int").alias("hour_utc"))
        .join(hourly_counts, "hour_utc", "left")
        .fillna(0, ["posts"])
        .orderBy("hour_utc")
    )

    user_counts = frame.groupBy("user").count().select(F.col("count").alias("posts"))
    user_distribution = user_counts.groupBy(
        F.least(F.col("posts"), F.lit(20)).alias("posts_per_user")
    ).count().select("posts_per_user", F.col("count").alias("users")).orderBy("posts_per_user")

    tokens = frame.select(
        "label",
        F.explode(F.split(F.col("clean_text"), r"\W+")).alias("word"),
    ).filter(
        (F.length("word") >= 2) & (~F.col("word").isin(DISPLAY_STOPWORDS))
    )
    word_counts = tokens.groupBy("label", "word").count().select(
        "label", "word", F.col("count").alias("occurrences")
    )
    ranked_words = word_counts.withColumn(
        "rank",
        F.row_number().over(
            Window.partitionBy("label").orderBy(F.desc("occurrences"), F.asc("word"))
        ),
    ).filter(F.col("rank") <= 20).orderBy("label", "rank")

    label_by_day = frame.filter(F.col("posted_at").isNotNull()).groupBy(
        F.to_date("posted_at").alias("day"), "label"
    ).count().select("day", "label", F.col("count").alias("posts")).orderBy("day", "label")

    sql_daily_sentiment = frame.sparkSession.sql(
        """
        SELECT to_date(posted_at) AS day,
               CAST(label AS INT) AS label,
               count(*) AS posts
        FROM tweets
        WHERE posted_at IS NOT NULL
        GROUP BY to_date(posted_at), CAST(label AS INT)
        ORDER BY day, label
        """
    )

    daily_rows = spark_rows_to_dicts(daily.collect())
    hourly_rows = spark_rows_to_dicts(hourly.collect())
    user_rows = spark_rows_to_dicts(user_distribution.collect())
    word_rows = spark_rows_to_dicts(ranked_words.collect())
    label_day_rows = spark_rows_to_dicts(label_by_day.collect())
    sql_rows = spark_rows_to_dicts(sql_daily_sentiment.collect())

    write_csv(tables / "posts_by_day.csv", daily_rows, ["day", "posts"])
    write_csv(tables / "posts_by_hour_utc.csv", hourly_rows, ["hour_utc", "posts"])
    write_csv(tables / "posts_per_user_distribution.csv", user_rows, ["posts_per_user", "users"])
    write_csv(tables / "top_words_by_label.csv", word_rows, ["label", "word", "occurrences", "rank"])
    write_csv(tables / "label_by_day.csv", label_day_rows, ["day", "label", "posts"])
    write_csv(tables / "sql_daily_sentiment.csv", sql_rows, ["day", "label", "posts"])

    if daily_rows:
        plot_daily(daily_rows, charts / "posts_by_day.png")
    if hourly_rows:
        plot_hourly(hourly_rows, charts / "posts_by_hour_utc.png")
    if user_rows:
        plot_user_distribution(user_rows, charts / "posts_per_user.png")
    if word_rows:
        plot_top_words(word_rows, charts / "top_words_by_label.png")
    if label_day_rows:
        plot_label_by_day(label_day_rows, charts / "label_by_day.png")

    account_count = user_counts.count()
    total_rows = frame.count()
    summary = {
        "analyzed_rows": total_rows,
        "distinct_accounts_in_sample": account_count,
        "days_with_valid_timestamps": len(daily_rows),
        "hours_with_posts_utc": len(hourly_rows),
        "sql_query": (
            "Count posts by UTC date and dataset label using the temporary view 'tweets'."
        ),
        "top_word_method": (
            "Token occurrence counts after display-only stopword filtering; negations are retained."
        ),
        "interpretation_limit": (
            "All results describe the analyzed dataset sample, not all Twitter users."
        ),
    }
    write_json(outputs_dir / "analysis_summary.json", summary)
    return summary
