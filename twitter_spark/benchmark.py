from __future__ import annotations

import statistics
import time
from pathlib import Path

from .charts import plot_benchmark
from .utils import write_csv, write_json


def _aggregate_action(frame) -> int:
    from pyspark.sql import functions as F

    return (
        frame.filter(F.col("posted_at").isNotNull())
        .groupBy(F.to_date("posted_at").alias("day"))
        .count()
        .count()
    )


def run_benchmark(
    frame,
    outputs_dir: Path,
    requested_sizes: list[int | None],
    repetitions: int = 3,
    seed: int = 42,
) -> list[dict]:
    total_rows = frame.count()
    if total_rows == 0:
        raise ValueError("Cannot benchmark an empty processed dataset.")

    subsets = []
    seen_actual = set()
    for requested in requested_sizes:
        if requested is None or requested >= total_rows:
            subset = frame
            label = "all"
        else:
            subset = frame.sample(False, requested / total_rows, seed=seed)
            label = str(requested)
        actual = subset.count()
        if actual == 0 or actual in seen_actual:
            continue
        seen_actual.add(actual)
        subsets.append((label, actual, subset))

    results = []
    for requested_label, actual_rows, subset in subsets:
        uncached_times = []
        for _ in range(repetitions):
            started = time.perf_counter()
            _aggregate_action(subset)
            uncached_times.append(time.perf_counter() - started)
        results.append(
            {
                "requested_rows": requested_label,
                "actual_rows": actual_rows,
                "mode": "uncached",
                "runs_seconds": uncached_times,
                "median_seconds": statistics.median(uncached_times),
            }
        )

        cached = subset.cache()
        cached.count()  # warm-up is intentionally outside the measured region
        cached_times = []
        for _ in range(repetitions):
            started = time.perf_counter()
            _aggregate_action(cached)
            cached_times.append(time.perf_counter() - started)
        results.append(
            {
                "requested_rows": requested_label,
                "actual_rows": actual_rows,
                "mode": "cached",
                "runs_seconds": cached_times,
                "median_seconds": statistics.median(cached_times),
            }
        )
        cached.unpersist()

    csv_rows = []
    for row in results:
        flat = {key: value for key, value in row.items() if key != "runs_seconds"}
        for index, value in enumerate(row["runs_seconds"], start=1):
            flat[f"run_{index}_seconds"] = value
        csv_rows.append(flat)
    fields = ["requested_rows", "actual_rows", "mode"] + [
        f"run_{index}_seconds" for index in range(1, repetitions + 1)
    ] + ["median_seconds"]
    write_csv(outputs_dir / "tables" / "performance.csv", csv_rows, fields)
    write_json(
        outputs_dir / "performance.json",
        {
            "scope": "Daily groupBy aggregation action; input read and sample creation are excluded.",
            "repetitions": repetitions,
            "seed": seed,
            "total_processed_rows": total_rows,
            "results": results,
        },
    )
    plot_benchmark(results, outputs_dir / "charts" / "performance.png")
    return results

