from __future__ import annotations

import os
import sys


def create_spark(master: str, shuffle_partitions: int, enable_ui: bool = True):
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise RuntimeError(
            "PySpark is not installed. Run scripts/setup.ps1 or "
            "python -m pip install -r requirements.txt."
        ) from exc

    from .windows_support import build_local_filesystem_jar

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    builder = (
        SparkSession.builder.appName("TwitterSentimentBigData")
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", str(shuffle_partitions))
        .config("spark.hadoop.dfs.client.use.datanode.hostname", "true")
        .config("spark.ui.enabled", "true" if enable_ui else "false")
    )
    windows_jar = build_local_filesystem_jar()
    if windows_jar is not None:
        builder = (
            builder.config("spark.jars", str(windows_jar))
            .config("spark.driver.extraClassPath", str(windows_jar))
            .config("spark.executor.extraClassPath", str(windows_jar))
            .config(
                "spark.hadoop.fs.file.impl",
                "twitter_spark.NoPermissionLocalFileSystem",
            )
            .config("spark.hadoop.fs.file.impl.disable.cache", "true")
        )
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark
