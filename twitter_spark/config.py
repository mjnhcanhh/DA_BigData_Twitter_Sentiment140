from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .storage import ensure_local_parent


@dataclass(frozen=True)
class AppConfig:
    data_path: str | Path = Path("data/raw/training.1600000.processed.noemoticon.csv")
    processed_path: str | Path = Path("data/processed/tweets")
    outputs_dir: Path = Path("outputs")
    model_dir: Path = Path("models/sentiment_lr")
    master: str = "local[2]"
    shuffle_partitions: int = 8
    sample_fraction: float = 0.10
    seed: int = 42
    num_features: int = 32768
    max_iter: int = 30
    benchmark_repetitions: int = 3

    def validate(self) -> "AppConfig":
        if not 0 < self.sample_fraction <= 1:
            raise ValueError("sample_fraction must be in the interval (0, 1].")
        if self.shuffle_partitions < 1:
            raise ValueError("shuffle_partitions must be at least 1.")
        if self.num_features < 128:
            raise ValueError("num_features must be at least 128.")
        if self.max_iter < 1:
            raise ValueError("max_iter must be at least 1.")
        if self.benchmark_repetitions < 1:
            raise ValueError("benchmark_repetitions must be at least 1.")
        return self

    def ensure_directories(self) -> None:
        ensure_local_parent(self.processed_path)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        (self.outputs_dir / "tables").mkdir(parents=True, exist_ok=True)
        (self.outputs_dir / "charts").mkdir(parents=True, exist_ok=True)
        self.model_dir.parent.mkdir(parents=True, exist_ok=True)
