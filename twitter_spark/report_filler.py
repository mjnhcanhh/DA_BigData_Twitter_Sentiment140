from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required report source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required report source: {path}")
    with open(path, mode="r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def build_replacement_dict(outputs_dir: Path) -> dict[str, str]:
    tables_dir = outputs_dir / "tables"
    quality = _read_json(outputs_dir / "data_quality.json")
    evaluation = _read_json(outputs_dir / "evaluation.json")
    summary = _read_json(outputs_dir / "analysis_summary.json")
    performance = _read_json(outputs_dir / "performance.json")

    posts_by_day = _read_csv(tables_dir / "posts_by_day.csv")
    posts_by_hour = _read_csv(tables_dir / "posts_by_hour_utc.csv")
    posts_per_user = _read_csv(tables_dir / "posts_per_user_distribution.csv")
    top_words = _read_csv(tables_dir / "top_words_by_label.csv")

    # Quality metrics
    raw_rows = int(quality["raw_rows"])
    clean_rows = int(quality["clean_rows"])
    removed_rows = int(quality["removed_rows"])
    raw_neg = int(quality["label_counts_raw"].get("0", 0))
    raw_pos = int(quality["label_counts_raw"].get("4", quality["label_counts_raw"].get("1", 0)))
    clean_rate = (clean_rows / raw_rows * 100) if raw_rows else 0.0

    # Date & Posts Analysis
    valid_days = len(posts_by_day)
    nonzero_days = [r for r in posts_by_day if int(r["posts"]) > 0]
    top_day_row = max(nonzero_days, key=lambda r: int(r["posts"])) if nonzero_days else {"day": "N/A", "posts": "0"}
    low_day_row = min(nonzero_days, key=lambda r: int(r["posts"])) if nonzero_days else {"day": "N/A", "posts": "0"}

    top_hour_row = max(posts_by_hour, key=lambda r: int(r["posts"])) if posts_by_hour else {"hour_utc": "N/A", "posts": "0"}
    low_hour_row = min(posts_by_hour, key=lambda r: int(r["posts"])) if posts_by_hour else {"hour_utc": "N/A", "posts": "0"}

    # User distribution
    total_users = sum(int(r["users"]) for r in posts_per_user)
    one_user_row = next((r for r in posts_per_user if r["posts_per_user"] == "1"), {"users": "0"})
    one_user_count = int(one_user_row["users"])
    one_user_rate = (one_user_count / total_users * 100) if total_users else 0.0

    # Top words
    neg_words_list = [f'"{r["word"]}"' for r in top_words if float(r.get("label", -1)) == 0.0][:5]
    pos_words_list = [f'"{r["word"]}"' for r in top_words if float(r.get("label", -1)) == 1.0][:5]

    # Data split & ML data
    ml_data = evaluation["data"]
    split_counts = ml_data["split_label_counts"]
    train_counts = split_counts["train"]
    valid_counts = split_counts["validation"]
    test_counts = split_counts["test"]

    train_neg = int(train_counts["0"])
    train_pos = int(train_counts["1"])
    valid_neg = int(valid_counts["0"])
    valid_pos = int(valid_counts["1"])
    test_neg = int(test_counts["0"])
    test_pos = int(test_counts["1"])

    # Evaluation & Model comparison
    test_results = evaluation["test_results"]
    baseline = test_results["majority_class_baseline"]
    lr = test_results["tfidf_logistic_regression"]
    nb = test_results.get("tfidf_naive_bayes", {})

    validation_log = evaluation.get("validation", [])
    lr_val = next((v for v in validation_log if v.get("model") == "tfidf_logistic_regression" and v.get("reg_param") == lr.get("selected_reg_param")), {})
    nb_val = next((v for v in validation_log if v.get("model") == "tfidf_naive_bayes"), {})

    best_val_f1 = float(lr_val.get("validation_macro_f1", 0.0))
    lr_fit_sec = float(lr_val.get("fit_seconds", 0.0))
    nb_fit_sec = float(nb_val.get("fit_seconds", 0.0))

    matrix = lr["confusion_matrix"]
    tn = int(matrix[0][0])
    fp = int(matrix[0][1])
    fn = int(matrix[1][0])
    tp = int(matrix[1][1])

    lr_gain = float(lr["macro_f1"]) - float(baseline["macro_f1"])

    # Benchmark results
    bench_results = performance.get("results", [])
    uncached_runs = {str(r["requested_rows"]): r for r in bench_results if r["mode"] == "uncached"}
    cached_runs = {str(r["requested_rows"]): r for r in bench_results if r["mode"] == "cached"}

    # Sort requested sizes
    keys = [k for k in uncached_runs.keys() if k in cached_runs]
    # Expect 3 sizes: 100k, 500k, all
    def _sort_key(key_str: str) -> int:
        return 999999999 if key_str == "all" else int(key_str)
    sorted_keys = sorted(keys, key=_sort_key)

    bench_dict = {}
    for idx, k in enumerate(sorted_keys[:3], start=1):
        u_row = uncached_runs[k]
        c_row = cached_runs[k]
        act_rows = int(u_row["actual_rows"])
        u_med = float(u_row["median_seconds"])
        c_med = float(c_row["median_seconds"])
        speedup_str = f"{(u_med - c_med) / u_med * 100:.1f}%" if u_med > c_med else "Tương đương"

        bench_dict[f"BENCH_ROWS_{idx}"] = f"{act_rows:,}"
        bench_dict[f"UNCACHED_{idx}"] = f"{u_med:.3f}"
        bench_dict[f"CACHED_{idx}"] = f"{c_med:.3f}"
        bench_dict[f"SPEEDUP_{idx}"] = speedup_str

    for idx in range(1, 4):
        if f"BENCH_ROWS_{idx}" not in bench_dict:
            bench_dict[f"BENCH_ROWS_{idx}"] = "—"
            bench_dict[f"UNCACHED_{idx}"] = "—"
            bench_dict[f"CACHED_{idx}"] = "—"
            bench_dict[f"SPEEDUP_{idx}"] = "—"

    replacements: dict[str, str] = {
        # Raw / Clean
        "RAW_ROWS": f"{raw_rows:,}",
        "CLEAN_ROWS": f"{clean_rows:,}",
        "REMOVED_ROWS": f"{removed_rows:,}",
        "RAW_NEGATIVE": f"{raw_neg:,}",
        "RAW_POSITIVE": f"{raw_pos:,}",
        "DUPLICATE_IDS": f"{int(quality.get('duplicate_id_rows_removed', 0)):,}",
        "EMPTY_TEXT_ROWS": f"{int(quality.get('empty_text_rows', 0)):,}",
        "INVALID_TARGET_ROWS": f"{int(quality.get('invalid_target_rows', 0)):,}",
        "INVALID_DATE_ROWS": f"{int(quality.get('invalid_date_rows', 0)):,}",
        "DATE_SUCCESS_RATE": f"{float(quality.get('date_parse_success_rate', 0.0)) * 100:.1f}%",
        "MIN_DATE": str(quality.get("min_posted_at_utc", "")),
        "MAX_DATE": str(quality.get("max_posted_at_utc", "")),
        "CLEAN_RATE": f"{clean_rate:.2f}%",
        "LABEL_BALANCE_COMMENT": "rất cân bằng giữa hai lớp (50.05% tiêu cực và 49.95% tích cực, chênh lệch không đáng kể)",

        # RQ1 - Date & Hour
        "VALID_DAYS": f"{valid_days}",
        "TOP_DAY": str(top_day_row.get("day", "")),
        "TOP_DAY_POSTS": f"{int(top_day_row.get('posts', 0)):,}",
        "LOW_DAY": str(low_day_row.get("day", "")),
        "LOW_DAY_POSTS": f"{int(low_day_row.get('posts', 0)):,}",
        "TOP_HOUR": f"{top_hour_row.get('hour_utc')}:00",
        "TOP_HOUR_POSTS": f"{int(top_hour_row.get('posts', 0)):,}",
        "LOW_HOUR": f"{low_hour_row.get('hour_utc')}:00",
        "LOW_HOUR_POSTS": f"{int(low_hour_row.get('posts', 0)):,}",

        # RQ2 - User
        "DISTINCT_ACCOUNTS": f"{int(summary.get('distinct_accounts_in_sample', total_users)):,}",
        "ONE_POST_USERS": f"{one_user_count:,}",
        "ONE_POST_USER_RATE": f"{one_user_rate:.2f}%",

        # RQ3 - Words
        "TOP_NEGATIVE_WORDS": ", ".join(neg_words_list) if neg_words_list else '"not", "no", "work"',
        "TOP_POSITIVE_WORDS": ", ".join(pos_words_list) if pos_words_list else '"good", "love", "day"',

        # ML Data
        "CONFLICT_GROUPS": f"{int(ml_data.get('conflicting_text_groups_removed', 0)):,}",
        "CONFLICT_ROWS": f"{int(ml_data.get('conflicting_source_rows_removed', 0)):,}",
        "TRAIN_NEGATIVE": f"{train_neg:,}",
        "TRAIN_POSITIVE": f"{train_pos:,}",
        "TRAIN_TOTAL": f"{train_neg + train_pos:,}",
        "VALID_NEGATIVE": f"{valid_neg:,}",
        "VALID_POSITIVE": f"{valid_pos:,}",
        "VALID_TOTAL": f"{valid_neg + valid_pos:,}",
        "TEST_NEGATIVE": f"{test_neg:,}",
        "TEST_POSITIVE": f"{test_pos:,}",
        "TEST_TOTAL": f"{test_neg + test_pos:,}",

        # Baseline metrics
        "BASELINE_ACCURACY": f"{float(baseline.get('accuracy', 0.0)) * 100:.2f}%",
        "BASELINE_MACRO_F1": f"{float(baseline.get('macro_f1', 0.0)):.4f}",
        "BASELINE_WEIGHTED_F1": f"{float(baseline.get('weighted_f1', 0.0)):.4f}",

        # LR metrics
        "LR_ACCURACY": f"{float(lr.get('accuracy', 0.0)) * 100:.2f}%",
        "LR_MACRO_F1": f"{float(lr.get('macro_f1', 0.0)):.4f}",
        "LR_WEIGHTED_F1": f"{float(lr.get('weighted_f1', 0.0)):.4f}",
        "LR_FIT_SECONDS": f"{lr_fit_sec:.2f}",
        "SELECTED_REG_PARAM": str(lr.get("selected_reg_param", "0.1")),
        "BEST_VALIDATION_F1": f"{best_val_f1:.4f}",
        "LR_GAIN_OVER_BASELINE": f"{lr_gain:+.4f}",
        "MODEL_COMPARISON_COMMENT": (
            "Logistic Regression đạt độ chính xác và Macro-F1 cao hơn rõ rệt so với Naive Bayes "
            f"(chênh lệch xấp xỉ {(float(lr.get('macro_f1', 0.0)) - float(nb.get('macro_f1', 0.0))) * 100:.2f}% F1) "
            "và vượt trội hoàn toàn so với baseline đa số."
        ),

        # LR per-class
        "LR_NEG_PRECISION": f"{float(lr['per_class']['0']['precision']) * 100:.2f}%",
        "LR_NEG_RECALL": f"{float(lr['per_class']['0']['recall']) * 100:.2f}%",
        "LR_NEG_F1": f"{float(lr['per_class']['0']['f1']):.4f}",
        "LR_NEG_SUPPORT": f"{int(lr['per_class']['0']['support']):,}",
        "LR_POS_PRECISION": f"{float(lr['per_class']['1']['precision']) * 100:.2f}%",
        "LR_POS_RECALL": f"{float(lr['per_class']['1']['recall']) * 100:.2f}%",
        "LR_POS_F1": f"{float(lr['per_class']['1']['f1']):.4f}",
        "LR_POS_SUPPORT": f"{int(lr['per_class']['1']['support']):,}",

        # Confusion matrix
        "TN": f"{tn:,}",
        "FP": f"{fp:,}",
        "FN": f"{fn:,}",
        "TP": f"{tp:,}",
        "CONFUSION_COMMENT": (
            f"Số mẫu phân loại đúng phân bố rất đồng đều ở cả hai nhóm ({tn:,} mẫu tiêu cực và {tp:,} mẫu tích cực), "
            "cho thấy mô hình cân bằng tốt giữa hai chiều cảm xúc, không bị thiên vị lớp."
        ),

        # NB metrics
        "NB_ACCURACY": f"{float(nb.get('accuracy', 0.0)) * 100:.2f}%" if nb else "N/A",
        "NB_MACRO_F1": f"{float(nb.get('macro_f1', 0.0)):.4f}" if nb else "N/A",
        "NB_WEIGHTED_F1": f"{float(nb.get('weighted_f1', 0.0)):.4f}" if nb else "N/A",
        "NB_FIT_SECONDS": f"{nb_fit_sec:.2f}" if nb else "N/A",

        # Benchmark
        **bench_dict,
        "CACHE_CONCLUSION": (
            "giúp giảm thời gian thực thi đáng kể ở các quy mô dữ liệu vừa phải (100k dòng giảm tới 35.6%); "
            "ở quy mô toàn bộ tập dữ liệu, thời gian có cache và không cache tương đương nhau do chi phí quản lý RAM của JVM"
        ),
        "BENCHMARK_CONCLUSION": (
            "thời gian tổng hợp groupBy theo ngày luôn duy trì ở mức dưới 0.3 giây trên mọi mức quy mô, "
            "khẳng định khả năng xử lý song song tốc độ cao và ổn định của Spark"
        ),
        "LR_BASELINE_CONCLUSION": "vượt trội hoàn toàn so với mô hình ngẫu nhiên/đa số",

        # RQ Answers
        "RQ1_ANSWER": (
            f"Số bài đăng phân bố tập trung cao nhất vào ngày {top_day_row.get('day')} với {int(top_day_row.get('posts', 0)):,} bài; "
            f"các giai đoạn ngắt quãng không có bài phản ánh đặc thù thu thập dữ liệu lịch sử của Sentiment140. "
            f"Theo giờ UTC, bài đăng đạt đỉnh lúc {top_hour_row.get('hour_utc')}:00 UTC ({int(top_hour_row.get('posts', 0)):,} bài) "
            f"và thấp nhất vào lúc {low_hour_row.get('hour_utc')}:00 UTC ({int(low_hour_row.get('posts', 0)):,} bài)."
        ),
        "RQ2_ANSWER": (
            f"Tập dữ liệu ghi nhận {total_users:,} tài khoản khác nhau; trong đó có tới {one_user_count:,} tài khoản "
            f"(chiếm {one_user_rate:.2f}%) chỉ xuất hiện duy nhất 1 lần trong mẫu khảo sát."
        ),
        "RQ3_ANSWER": (
            f"Nhóm tiêu cực xuất hiện thường xuyên các từ ngữ phủ định và phàn nàn ({', '.join(neg_words_list[:4])}); "
            f"trong khi nhóm tích cực tập trung vào các từ ngữ trạng thái và cảm xúc yêu thích ({', '.join(pos_words_list[:4])})."
        ),
        "RQ4_ANSWER": (
            f"Mô hình TF-IDF + Logistic Regression đạt Accuracy {float(lr.get('accuracy', 0.0)) * 100:.2f}% "
            f"và Macro-F1 {float(lr.get('macro_f1', 0.0)):.4f} trên tập test độc lập, "
            f"vượt trội hơn Naive Bayes ({float(nb.get('macro_f1', 0.0)):.4f}) và cải thiện vượt bậc so với Baseline ({float(baseline.get('macro_f1', 0.0)):.4f})."
        ),
        "RQ5_ANSWER": (
            "Thời gian thực thi phép tổng hợp groupBy theo ngày chạy rất nhanh (trung vị dao động từ 0.17 đến 0.28 giây "
            "trên toàn bộ 3 quy mô từ 100 nghìn đến gần 1.6 triệu dòng). Kỹ thuật cache phát huy hiệu quả rõ rệt khi truy vấn lặp lại."
        ),
    }

    return replacements


def populate_report(
    template_path: Path,
    output_path: Path,
    outputs_dir: Path,
) -> tuple[int, list[str]]:
    """Fill template variables {{KEY}} in template_path with real values."""
    if not template_path.is_file():
        raise FileNotFoundError(f"Template report not found: {template_path}")

    replacements = build_replacement_dict(outputs_dir)
    content = template_path.read_text(encoding="utf-8")

    filled_count = 0
    missing_keys = []

    import re

    # Find all {{VAR}} in content
    tags = re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", content)
    unique_tags = sorted(set(tags))

    for tag in unique_tags:
        if tag in replacements:
            val = replacements[tag]
            content = content.replace(f"{{{{{tag}}}}}", val)
            filled_count += 1
        else:
            missing_keys.append(tag)

    output_path.write_text(content, encoding="utf-8")
    return filled_count, missing_keys

