from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from .storage import is_remote_uri
from .utils import write_csv


def get_dir_size_bytes(path: Path) -> int:
    total = 0
    if path.is_file():
        return path.stat().st_size
    for entry in path.rglob("*"):
        if entry.is_file():
            total += entry.stat().st_size
    return total


def run_storage_comparison(
    spark,
    csv_path: str | Path,
    parquet_path: str | Path,
    outputs_dir: Path,
) -> list[dict[str, Any]]:
    """Compare storage size and reading speed between raw CSV and Parquet."""
    results = []

    csv_p = Path(csv_path)
    parquet_p = Path(parquet_path)

    csv_size_mb = 0.0
    parquet_size_mb = 0.0

    if not is_remote_uri(csv_path) and csv_p.is_file():
        csv_size_mb = csv_p.stat().st_size / (1024 * 1024)

    if not is_remote_uri(parquet_path) and parquet_p.exists():
        parquet_size_mb = get_dir_size_bytes(parquet_p) / (1024 * 1024)

    ratio = (
        ((csv_size_mb - parquet_size_mb) / csv_size_mb * 100)
        if csv_size_mb > 0
        else 0.0
    )

    # Measure simple count / query speed if Spark session is available
    csv_read_sec = 0.0
    parquet_read_sec = 0.0
    if spark is not None:
        try:
            start = time.perf_counter()
            _ = spark.read.option("header", False).csv(str(csv_path)).count()
            csv_read_sec = time.perf_counter() - start
        except Exception:
            pass

        try:
            start = time.perf_counter()
            _ = spark.read.parquet(str(parquet_path)).count()
            parquet_read_sec = time.perf_counter() - start
        except Exception:
            pass

    speedup = (
        (csv_read_sec / parquet_read_sec)
        if parquet_read_sec > 0
        else 0.0
    )

    results.append(
        {
            "format": "Raw CSV (ISO-8859-1)",
            "size_mb": round(csv_size_mb, 2),
            "read_count_seconds": round(csv_read_sec, 3),
            "space_reduction_percent": "0.0%",
            "speedup": "1.0x (baseline)",
        }
    )
    results.append(
        {
            "format": "Cleaned Parquet (Snappy)",
            "size_mb": round(parquet_size_mb, 2),
            "read_count_seconds": round(parquet_read_sec, 3),
            "space_reduction_percent": f"{ratio:.1f}%",
            "speedup": f"{speedup:.2f}x faster" if speedup > 0 else "N/A",
        }
    )

    tables_dir = outputs_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        tables_dir / "storage_comparison.csv",
        results,
        ["format", "size_mb", "read_count_seconds", "space_reduction_percent", "speedup"],
    )
    return results

