from __future__ import annotations

from pathlib import Path
from typing import Sequence


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _finish(plt, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def plot_daily(rows: Sequence[dict], path: Path) -> None:
    plt = _plt()
    plt.figure(figsize=(10, 4.5))
    plt.plot([row["day"] for row in rows], [row["posts"] for row in rows], marker="o")
    plt.title("Posts by date in the analyzed sample")
    plt.xlabel("Date (UTC)")
    plt.ylabel("Number of posts")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.25)
    _finish(plt, path)


def plot_hourly(rows: Sequence[dict], path: Path) -> None:
    plt = _plt()
    plt.figure(figsize=(9, 4.5))
    plt.bar([row["hour_utc"] for row in rows], [row["posts"] for row in rows])
    plt.title("Posts by hour in the analyzed sample")
    plt.xlabel("Hour (UTC)")
    plt.ylabel("Number of posts")
    plt.xticks(range(24))
    plt.grid(axis="y", alpha=0.25)
    _finish(plt, path)


def plot_user_distribution(rows: Sequence[dict], path: Path) -> None:
    plt = _plt()
    labels = ["20+" if row["posts_per_user"] == 20 else str(row["posts_per_user"]) for row in rows]
    plt.figure(figsize=(9, 4.5))
    plt.bar(labels, [row["users"] for row in rows])
    plt.title("Distribution of posts per account in the sample")
    plt.xlabel("Posts per account (20 means 20+)")
    plt.ylabel("Number of accounts")
    plt.grid(axis="y", alpha=0.25)
    _finish(plt, path)


def plot_top_words(rows: Sequence[dict], path: Path) -> None:
    plt = _plt()
    negative = [row for row in rows if int(row["label"]) == 0][:15]
    positive = [row for row in rows if int(row["label"]) == 1][:15]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for axis, subset, title, color in [
        (axes[0], negative, "Negative label", "#d95f5f"),
        (axes[1], positive, "Positive label", "#4c9f70"),
    ]:
        shown = list(reversed(subset))
        axis.barh([row["word"] for row in shown], [row["occurrences"] for row in shown], color=color)
        axis.set_title(title)
        axis.set_xlabel("Token occurrences")
        axis.grid(axis="x", alpha=0.2)
    fig.suptitle("Most frequent informative tokens by dataset label")
    _finish(plt, path)


def plot_label_by_day(rows: Sequence[dict], path: Path) -> None:
    plt = _plt()
    days = sorted({row["day"] for row in rows})
    counts = {(row["day"], int(row["label"])): row["posts"] for row in rows}
    plt.figure(figsize=(10, 4.5))
    for label, name, color in [(0, "Negative", "#d95f5f"), (1, "Positive", "#4c9f70")]:
        plt.plot(days, [counts.get((day, label), 0) for day in days], marker="o", label=name, color=color)
    plt.title("Dataset labels by date in the analyzed sample")
    plt.xlabel("Date (UTC)")
    plt.ylabel("Number of posts")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(alpha=0.25)
    _finish(plt, path)


def plot_confusion(matrix: Sequence[Sequence[int]], path: Path) -> None:
    plt = _plt()
    figure, axis = plt.subplots(figsize=(5.5, 4.8))
    image = axis.imshow(matrix, cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set_xticks([0, 1], labels=["Negative", "Positive"])
    axis.set_yticks([0, 1], labels=["Negative", "Positive"])
    axis.set_xlabel("Predicted label")
    axis.set_ylabel("Actual label")
    axis.set_title("Logistic Regression confusion matrix")
    threshold = max(max(row) for row in matrix) / 2 if matrix else 0
    for actual in (0, 1):
        for predicted in (0, 1):
            value = matrix[actual][predicted]
            axis.text(predicted, actual, str(value), ha="center", va="center", color="white" if value > threshold else "black")
    _finish(plt, path)


def plot_benchmark(rows: Sequence[dict], path: Path) -> None:
    plt = _plt()
    plt.figure(figsize=(8, 4.8))
    for mode, marker in [("uncached", "o"), ("cached", "s")]:
        selected = sorted((row for row in rows if row["mode"] == mode), key=lambda row: row["actual_rows"])
        if selected:
            plt.plot(
                [row["actual_rows"] for row in selected],
                [row["median_seconds"] for row in selected],
                marker=marker,
                label=mode,
            )
    plt.title("Daily aggregation time by sample size")
    plt.xlabel("Actual rows")
    plt.ylabel("Median seconds")
    plt.legend()
    plt.grid(alpha=0.25)
    _finish(plt, path)

