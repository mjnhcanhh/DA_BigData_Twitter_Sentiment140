from __future__ import annotations

import time
from pathlib import Path

from .charts import plot_confusion
from .evaluation import evaluate_predictions, metrics_from_cells
from .utils import spark_rows_to_dicts, write_csv, write_json


def _pipeline(classifier, num_features: int):
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import HashingTF, IDF, RegexTokenizer

    return Pipeline(
        stages=[
            RegexTokenizer(
                inputCol="clean_text",
                outputCol="tokens",
                pattern=r"\W+",
                minTokenLength=1,
            ),
            HashingTF(
                inputCol="tokens", outputCol="tf", numFeatures=num_features
            ),
            IDF(inputCol="tf", outputCol="features"),
            classifier,
        ]
    )


def _class_counts(frame) -> dict[str, int]:
    return {
        str(int(row["label"])): int(row["count"])
        for row in frame.groupBy("label").count().orderBy("label").collect()
    }


def _assert_two_classes(name: str, frame) -> dict[str, int]:
    counts = _class_counts(frame)
    if set(counts) != {"0", "1"}:
        raise ValueError(
            f"Split '{name}' does not contain both labels (counts={counts}). "
            "Increase --sample-fraction or use more data."
        )
    return counts


def prepare_ml_data(frame, sample_fraction: float, seed: int):
    from pyspark.sql import functions as F

    grouped = frame.groupBy("clean_text").agg(
        F.countDistinct("label").alias("nlabels"),
        F.min("label").alias("label"),
        F.count("*").alias("source_rows"),
    )
    conflicting_groups = grouped.filter(F.col("nlabels") > 1)
    conflict_stats = conflicting_groups.agg(
        F.count("*").alias("groups"), F.sum("source_rows").alias("rows")
    ).first()
    ml = grouped.filter(F.col("nlabels") == 1).select("clean_text", "label")
    if sample_fraction < 1:
        ml = ml.sampleBy(
            "label", {0.0: sample_fraction, 1.0: sample_fraction}, seed=seed
        )
    ml = ml.withColumn(
        "bucket", F.pmod(F.xxhash64("clean_text"), F.lit(1000))
    ).cache()
    train = ml.filter(F.col("bucket") < 700).select("clean_text", "label")
    valid = ml.filter((F.col("bucket") >= 700) & (F.col("bucket") < 850)).select(
        "clean_text", "label"
    )
    test = ml.filter(F.col("bucket") >= 850).select("clean_text", "label")
    split_counts = {
        "train": _assert_two_classes("train", train),
        "validation": _assert_two_classes("validation", valid),
        "test": _assert_two_classes("test", test),
    }
    return ml, train, valid, test, {
        "conflicting_text_groups_removed": int(conflict_stats["groups"] or 0),
        "conflicting_source_rows_removed": int(conflict_stats["rows"] or 0),
        "sample_fraction": sample_fraction,
        "split_rule": "pmod(xxhash64(clean_text), 1000): train <700, validation 700-849, test >=850",
        "split_label_counts": split_counts,
    }


def train_and_evaluate(
    frame,
    outputs_dir: Path,
    model_dir: Path,
    sample_fraction: float,
    seed: int,
    num_features: int,
    max_iter: int,
    include_naive_bayes: bool = True,
) -> dict:
    from pyspark.ml.classification import LogisticRegression, NaiveBayes
    from pyspark.sql import functions as F

    ml, train, valid, test, data_info = prepare_ml_data(
        frame, sample_fraction=sample_fraction, seed=seed
    )

    validation_log = []
    best_model = None
    best_score = -1.0
    best_reg = None
    for reg_param in (0.01, 0.1):
        estimator = _pipeline(
            LogisticRegression(
                maxIter=max_iter,
                regParam=reg_param,
                elasticNetParam=0.0,
                labelCol="label",
                featuresCol="features",
            ),
            num_features,
        )
        started = time.perf_counter()
        candidate = estimator.fit(train)
        fit_seconds = time.perf_counter() - started
        validation_metrics = evaluate_predictions(candidate.transform(valid))
        score = validation_metrics["macro_f1"]
        validation_log.append(
            {
                "model": "tfidf_logistic_regression",
                "reg_param": reg_param,
                "validation_macro_f1": score,
                "fit_seconds": fit_seconds,
            }
        )
        if score > best_score:
            best_model = candidate
            best_score = score
            best_reg = reg_param

    assert best_model is not None
    test_started = time.perf_counter()
    lr_predictions = best_model.transform(test).cache()
    lr_metrics = evaluate_predictions(lr_predictions)
    lr_prediction_seconds = time.perf_counter() - test_started
    lr_metrics["prediction_seconds"] = lr_prediction_seconds
    lr_metrics["selected_reg_param"] = best_reg
    lr_metrics["selection_metric"] = "validation_macro_f1"

    train_counts = _class_counts(train)
    majority_label = max((0, 1), key=lambda label: train_counts[str(label)])
    test_counts = _class_counts(test)
    baseline_cells = {
        (actual, majority_label): count
        for actual, count in ((0, test_counts["0"]), (1, test_counts["1"]))
    }
    baseline_metrics = metrics_from_cells(baseline_cells)
    baseline_metrics["majority_label_from_train"] = majority_label

    comparison = {
        "majority_class_baseline": baseline_metrics,
        "tfidf_logistic_regression": lr_metrics,
    }

    if include_naive_bayes:
        nb_estimator = _pipeline(
            NaiveBayes(
                smoothing=1.0,
                modelType="multinomial",
                labelCol="label",
                featuresCol="features",
            ),
            num_features,
        )
        nb_started = time.perf_counter()
        nb_model = nb_estimator.fit(train)
        nb_fit_seconds = time.perf_counter() - nb_started
        nb_validation = evaluate_predictions(nb_model.transform(valid))
        validation_log.append(
            {
                "model": "tfidf_naive_bayes",
                "reg_param": "",
                "validation_macro_f1": nb_validation["macro_f1"],
                "fit_seconds": nb_fit_seconds,
            }
        )
        nb_test_started = time.perf_counter()
        nb_metrics = evaluate_predictions(nb_model.transform(test))
        nb_metrics["prediction_seconds"] = time.perf_counter() - nb_test_started
        nb_metrics["smoothing"] = 1.0
        comparison["tfidf_naive_bayes"] = nb_metrics

    errors = (
        lr_predictions.filter(F.col("label") != F.col("prediction"))
        .select(
            F.col("label").cast("int").alias("actual_label"),
            F.col("prediction").cast("int").alias("predicted_label"),
            "clean_text",
        )
        .limit(50)
        .collect()
    )
    write_csv(
        outputs_dir / "tables" / "misclassified_examples.csv",
        spark_rows_to_dicts(errors),
        ["actual_label", "predicted_label", "clean_text"],
    )
    write_csv(
        outputs_dir / "tables" / "validation_results.csv",
        validation_log,
        ["model", "reg_param", "validation_macro_f1", "fit_seconds"],
    )
    plot_confusion(
        lr_metrics["confusion_matrix"], outputs_dir / "charts" / "confusion_matrix.png"
    )

    report = {
        "data": data_info,
        "feature_pipeline": {
            "steps": ["RegexTokenizer", "HashingTF", "IDF", "classifier"],
            "num_features": num_features,
            "stopwords_removed_for_model": False,
            "note": "Only clean_text is used as model input; user, target and label are not features.",
        },
        "validation": validation_log,
        "test_results": comparison,
        "test_policy": "Test was evaluated only after selecting Logistic Regression regularization on validation.",
    }
    write_json(outputs_dir / "evaluation.json", report)
    best_model.write().overwrite().save(str(model_dir))
    write_json(
        model_dir.parent / "sentiment_lr_metadata.json",
        {
            "model_path": str(model_dir),
            "selected_reg_param": best_reg,
            "validation_macro_f1": best_score,
            "label_mapping": {"0": "negative", "1": "positive"},
            "synthetic_or_real_data": "Determined by the input path recorded in outputs/data_quality.json.",
        },
    )
    lr_predictions.unpersist()
    ml.unpersist()
    return report


def predict_texts(spark, model_dir: Path, texts: list[str]) -> list[dict]:
    from pyspark.ml import PipelineModel
    from pyspark.sql import functions as F

    from .data import clean_text_expr

    if not model_dir.exists():
        raise FileNotFoundError(
            f"Saved model not found: {model_dir}. Run train or demo first."
        )
    model = PipelineModel.load(str(model_dir))
    examples = spark.createDataFrame([(text,) for text in texts], ["text"])
    examples = examples.withColumn("clean_text", clean_text_expr(F.col("text")))
    rows = model.transform(examples).select("text", "prediction", "probability").collect()
    return [
        {
            "text": row["text"],
            "prediction": int(row["prediction"]),
            "sentiment": "positive" if int(row["prediction"]) == 1 else "negative",
            "probability_negative": float(row["probability"][0]),
            "probability_positive": float(row["probability"][1]),
        }
        for row in rows
    ]
