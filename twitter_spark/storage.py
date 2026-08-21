from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


def is_hdfs_uri(value: str | Path) -> bool:
    return urlparse(str(value)).scheme.lower() == "hdfs"


def is_remote_uri(value: str | Path) -> bool:
    return urlparse(str(value)).scheme.lower() in {
        "hdfs",
        "s3",
        "s3a",
        "gs",
        "abfs",
        "abfss",
    }


def ensure_local_parent(value: str | Path) -> None:
    if not is_remote_uri(value):
        Path(value).parent.mkdir(parents=True, exist_ok=True)


def spark_path_exists(spark, value: str | Path) -> bool:
    path = spark._jvm.org.apache.hadoop.fs.Path(str(value))
    filesystem = path.getFileSystem(spark._jsc.hadoopConfiguration())
    return bool(filesystem.exists(path))
