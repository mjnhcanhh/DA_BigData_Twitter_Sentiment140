from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

from .analysis import run_analysis
from .benchmark import run_benchmark
from .config import AppConfig
from .data import prepare_data, read_prepared
from .demo_data import generate_demo_csv
from .modeling import predict_texts, train_and_evaluate
from .report_filler import populate_report
from .spark_session import create_spark
from .storage_comparison import run_storage_comparison
from .utils import write_json


DEMO_TEXTS = [
    "I really enjoyed this day.",
    "This experience was awful.",
    "The movie was not good.",
]


def _java_version() -> str:
    try:
        completed = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, timeout=10, check=False
        )
        return (completed.stderr or completed.stdout).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"Unavailable: {exc}"


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--processed",
        default="data/processed/tweets",
        help="local directory or hdfs:// URI for cleaned Parquet",
    )
    parser.add_argument("--outputs", type=Path, default=Path("outputs"))
    parser.add_argument("--model", type=Path, default=Path("models/sentiment_lr"))
    parser.add_argument("--master", default="local[2]")
    parser.add_argument("--shuffle-partitions", type=int, default=8)


def _config(args, data_path: str | Path | None = None, demo: bool = False) -> AppConfig:
    return AppConfig(
        data_path=data_path or getattr(args, "data", Path("data/raw/training.1600000.processed.noemoticon.csv")),
        processed_path=args.processed,
        outputs_dir=args.outputs,
        model_dir=args.model,
        master=args.master,
        shuffle_partitions=args.shuffle_partitions,
        sample_fraction=getattr(args, "sample_fraction", 1.0 if demo else 0.10),
        seed=getattr(args, "seed", 42),
        num_features=getattr(args, "num_features", 4096 if demo else 32768),
        max_iter=getattr(args, "max_iter", 15 if demo else 30),
        benchmark_repetitions=getattr(args, "repetitions", 3),
    ).validate()


def _spark_for(config: AppConfig):
    return create_spark(config.master, config.shuffle_partitions)


def _run_all(spark, config: AppConfig, include_nb: bool, skip_benchmark: bool) -> dict:
    print("[1/4] Preparing and validating data...")
    quality = prepare_data(
        spark, config.data_path, config.processed_path, config.outputs_dir
    )
    frame = read_prepared(spark, config.processed_path).cache()
    print("[2/4] Running Spark SQL analysis and creating charts...")
    analysis = run_analysis(frame, config.outputs_dir)
    print("[3/4] Training and evaluating models...")
    evaluation = train_and_evaluate(
        frame,
        config.outputs_dir,
        config.model_dir,
        config.sample_fraction,
        config.seed,
        config.num_features,
        config.max_iter,
        include_naive_bayes=include_nb,
    )
    performance = []
    if not skip_benchmark:
        print("[4/4] Benchmarking daily aggregation (3 runs per mode/size)...")
        performance = run_benchmark(
            frame,
            config.outputs_dir,
            [100_000, 500_000, None],
            config.benchmark_repetitions,
            config.seed,
        )
    else:
        print("[4/4] Benchmark skipped by command option.")
    frame.unpersist()
    run_storage_comparison(spark, config.data_path, config.processed_path, config.outputs_dir)
    template_path = Path("report/bao_cao_cuoi_ky_template.md")
    if template_path.is_file() and quality.get("raw_rows", 0) >= 100_000:
        try:
            populate_report(template_path, Path("report/bao_cao_cuoi_ky.md"), config.outputs_dir)
            print("Auto-updated report/bao_cao_cuoi_ky.md with latest real run outputs.")
        except Exception as exc:
            print(f"Note: Could not auto-populate report: {exc}")

    manifest = {
        "data_quality": quality,
        "analysis": analysis,
        "evaluation_file": str(config.outputs_dir / "evaluation.json"),
        "performance_rows": len(performance),
        "model_path": str(config.model_dir),
        "environment": {
            "python": sys.version,
            "java": _java_version(),
            "platform": platform.platform(),
            "spark": spark.version,
            "master": config.master,
        },
        "important_limit": (
            "Results describe the input sample. Synthetic demo results must not be used as experimental evidence."
        ),
    }
    write_json(config.outputs_dir / "run_manifest.json", manifest)
    return evaluation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sentiment140 analysis and sentiment classification with Apache Spark"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    make_demo = sub.add_parser("make-demo-data", help="create labelled synthetic smoke-test data")
    make_demo.add_argument("--output", type=Path, default=Path("data/demo/sentiment140_demo.csv"))
    make_demo.add_argument("--rows", type=int, default=400)
    make_demo.add_argument("--seed", type=int, default=42)

    prepare = sub.add_parser("prepare", help="validate CSV, clean it and write Parquet")
    _add_common(prepare)
    prepare.add_argument("--data", required=True, help="local CSV path or hdfs:// URI")

    analyze = sub.add_parser("analyze", help="run Spark SQL analysis and generate charts")
    _add_common(analyze)

    train = sub.add_parser("train", help="train, validate, evaluate and save sentiment models")
    _add_common(train)
    train.add_argument("--sample-fraction", type=float, default=0.10)
    train.add_argument("--seed", type=int, default=42)
    train.add_argument("--num-features", type=int, default=32768)
    train.add_argument("--max-iter", type=int, default=30)
    train.add_argument("--skip-naive-bayes", action="store_true")

    predict = sub.add_parser("predict", help="load the saved LR model and predict new English text")
    _add_common(predict)
    predict.add_argument("--text", action="append", required=True, help="repeat this option for multiple texts")

    benchmark = sub.add_parser("benchmark", help="measure daily aggregation with and without cache")
    _add_common(benchmark)
    benchmark.add_argument("--sizes", nargs="+", type=int, default=[100_000, 500_000])
    benchmark.add_argument("--repetitions", type=int, default=3)
    benchmark.add_argument("--seed", type=int, default=42)

    run_all = sub.add_parser("run-all", help="run the complete pipeline on a Sentiment140 CSV")
    _add_common(run_all)
    run_all.add_argument("--data", required=True, help="local CSV path or hdfs:// URI")
    run_all.add_argument("--sample-fraction", type=float, default=0.10)
    run_all.add_argument("--seed", type=int, default=42)
    run_all.add_argument("--num-features", type=int, default=32768)
    run_all.add_argument("--max-iter", type=int, default=30)
    run_all.add_argument("--skip-naive-bayes", action="store_true")
    run_all.add_argument("--skip-benchmark", action="store_true")
    run_all.add_argument("--repetitions", type=int, default=3)

    demo = sub.add_parser("demo", help="generate synthetic data and run the complete fast demo")
    _add_common(demo)
    demo.add_argument("--rows", type=int, default=400)
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--num-features", type=int, default=4096)
    demo.add_argument("--max-iter", type=int, default=15)
    demo.add_argument("--repetitions", type=int, default=3)
    demo.add_argument("--skip-naive-bayes", action="store_true")
    demo.add_argument("--skip-benchmark", action="store_true", help="skip benchmark step in demo")
    pop_report = sub.add_parser("populate-report", help="fill report template with experimental outputs")
    pop_report.add_argument("--template", type=Path, default=Path("report/bao_cao_cuoi_ky_template.md"))
    pop_report.add_argument("--output", type=Path, default=Path("report/bao_cao_cuoi_ky.md"))
    pop_report.add_argument("--outputs-dir", type=Path, default=Path("outputs"))

    storage_cmp = sub.add_parser("storage-compare", help="compare disk size and reading between CSV and Parquet")
    _add_common(storage_cmp)
    storage_cmp.add_argument("--data", default="data/raw/training.1600000.processed.noemoticon.csv")

    gui_parser = sub.add_parser("gui", help="launch desktop Tkinter dashboard interface")
    gui_parser.add_argument("--check", action="store_true", help="check dependencies without opening a window")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    effective_args = sys.argv[1:] if argv is None else argv
    if not effective_args:
        parser.print_help()
        print("\n" + "=" * 60)
        print("[HUONG DAN CHAY NHANH / QUICK START]")
        print("  1. Chay demo nhanh (400 mau):")
        print("     python main.py demo")
        print("  2. Chay toan bo du lieu that (1.6 trieu dong):")
        print("     python main.py run-all --data data/raw/training.1600000.processed.noemoticon.csv")
        print("  3. So sanh dung luong CSV vs Parquet:")
        print("     python main.py storage-compare")
        print("  4. Khoi chay giao dien GUI:")
        print("     python main.py gui")
        print("=" * 60)
        return 0

    args = parser.parse_args(effective_args)
    if args.command == "gui":
        from .gui import main as gui_main
        return gui_main(["--check"] if getattr(args, "check", False) else [])

    if args.command == "make-demo-data":
        count = generate_demo_csv(args.output, args.rows, args.seed)
        print(f"Created {count} synthetic rows at {args.output}")
        print("Do not use synthetic metrics as final report results.")
        return 0

    if args.command == "populate-report":
        filled, missing = populate_report(args.template, args.output, args.outputs_dir)
        print(f"Successfully populated {filled} metrics into {args.output}")
        if missing:
            print(f"Warning: {len(missing)} placeholders were not found in outputs: {missing}")
        return 0

    demo_path = Path("data/demo/sentiment140_demo.csv")
    config = _config(args, data_path=demo_path if args.command == "demo" else None, demo=args.command == "demo")
    config.ensure_directories()
    if args.command == "demo":
        count = generate_demo_csv(demo_path, args.rows, args.seed)
        print(f"Created {count} synthetic rows for the smoke-test demo.")

    spark = None
    try:
        spark = _spark_for(config)
        if args.command == "storage-compare":
            res = run_storage_comparison(spark, config.data_path, config.processed_path, config.outputs_dir)
            print(json.dumps(res, indent=2))
        if args.command == "prepare":
            print(json.dumps(prepare_data(spark, config.data_path, config.processed_path, config.outputs_dir), indent=2, default=str))
        elif args.command == "analyze":
            print(json.dumps(run_analysis(read_prepared(spark, config.processed_path), config.outputs_dir), indent=2, default=str))
        elif args.command == "train":
            report = train_and_evaluate(
                read_prepared(spark, config.processed_path), config.outputs_dir, config.model_dir,
                config.sample_fraction, config.seed, config.num_features, config.max_iter,
                include_naive_bayes=not args.skip_naive_bayes,
            )
            print(json.dumps(report["test_results"], indent=2, default=str))
        elif args.command == "predict":
            print(json.dumps(predict_texts(spark, config.model_dir, args.text), indent=2, ensure_ascii=False))
        elif args.command == "benchmark":
            sizes = list(args.sizes) + [None]
            print(json.dumps(run_benchmark(read_prepared(spark, config.processed_path), config.outputs_dir, sizes, config.benchmark_repetitions, config.seed), indent=2))
        elif args.command in {"run-all", "demo"}:
            report = _run_all(
                spark, config, include_nb=not args.skip_naive_bayes,
                skip_benchmark=getattr(args, "skip_benchmark", False),
            )
            predictions = predict_texts(spark, config.model_dir, DEMO_TEXTS)
            print("\nDemo predictions:")
            print(json.dumps(predictions, indent=2, ensure_ascii=False))
            print(f"\nDone. Open {config.outputs_dir / 'run_manifest.json'} and {config.outputs_dir / 'charts'}")
            if args.command == "demo":
                print("WARNING: these metrics come from synthetic smoke-test data, not Sentiment140.")
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if spark is not None:
            spark.stop()
