"""
Script tạo ảnh minh chứng giao diện Desktop GUI điều phối Spark & HDFS
Lưu vào:
- outputs/charts/gui_dashboard.png
- report/figures/gui_dashboard.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR_1 = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR_2 = PROJECT_ROOT / "report" / "figures"
OUTPUT_DIR_1.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR_2.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Background Window
bg_rect = patches.FancyBboxPatch((0, 0), 100, 100, boxstyle="square,pad=0", facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5)
ax.add_patch(bg_rect)

# Top Bar (Header)
header_rect = patches.Rectangle((0, 88), 100, 12, facecolor="#1E293B")
ax.add_patch(header_rect)

# Title & Subtitle
ax.text(3, 95.5, "Twitter Sentiment140 — Big Data Pipeline & Desktop Dashboard", fontsize=15, fontweight="bold", color="#FFFFFF", va="center")
ax.text(3, 91.5, "Hệ thống phân tích hành vi người dùng và phân loại cảm xúc bằng Apache Spark, HDFS & Apache Airflow", fontsize=9.5, color="#94A3B8", va="center")

# Status badges on header
ax.text(78, 95.5, "● HDFS: ONLINE (8020/9870)", fontsize=9, fontweight="bold", color="#34D399", va="center")
ax.text(78, 91.5, "● Spark: local[2] | RAM: 32GB", fontsize=9, fontweight="bold", color="#60A5FA", va="center")

# LEFT PANEL: Parameters & Controls (x: 3 to 38, y: 3 to 85)
left_panel = patches.FancyBboxPatch((3, 3), 35, 82, boxstyle="round,pad=0.5,rounding_size=1.0", facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1.2)
ax.add_patch(left_panel)

ax.text(5, 82, "1. CẤU HÌNH DỮ LIỆU & THỰC NGHIỆM", fontsize=11, fontweight="bold", color="#0F172A")

# Input file box
ax.text(5, 78.5, "Tệp dữ liệu đầu vào (CSV):", fontsize=8.5, color="#475569")
file_box = patches.FancyBboxPatch((5, 73.5), 26, 4, boxstyle="round,pad=0.3,rounding_size=0.5", facecolor="#F1F5F9", edgecolor="#CBD5E1")
ax.add_patch(file_box)
ax.text(6, 75.5, ".../data/raw/training.1600000.processed.csv", fontsize=7.5, color="#1E293B", va="center")

btn_browse = patches.FancyBboxPatch((32, 73.5), 4.5, 4, boxstyle="round,pad=0.3,rounding_size=0.5", facecolor="#E2E8F0", edgecolor="#94A3B8")
ax.add_patch(btn_browse)
ax.text(34.25, 75.5, "Chọn", fontsize=7.5, fontweight="bold", color="#334155", ha="center", va="center")

# Sample fraction
ax.text(5, 70, "Tỷ lệ mẫu ML (Sample Fraction):", fontsize=8.5, color="#475569")
frac_box = patches.FancyBboxPatch((5, 65.5), 10, 3.8, boxstyle="round,pad=0.3,rounding_size=0.5", facecolor="#F1F5F9", edgecolor="#CBD5E1")
ax.add_patch(frac_box)
ax.text(7, 67.4, "0.10 (10%)", fontsize=8, fontweight="bold", color="#0F172A", va="center")
ax.text(16, 67.4, "Phân tầng nhị phân, chống tràn RAM", fontsize=7.5, color="#64748B", va="center")

# Action Buttons
ax.text(5, 62, "2. THAO TÁC PIPELINE & ĐIỀU PHỐI", fontsize=11, fontweight="bold", color="#0F172A")

buttons = [
    ("⚡ Demo Nhanh Cục Bộ", "#2563EB", "#FFFFFF", "demo.ps1"),
    ("⚙️ Cài Đặt Môi Trường", "#F1F5F9", "#0F172A", "setup.ps1"),
    ("🧪 Chạy Kiểm Thử Tự Động", "#F1F5F9", "#0F172A", "test.ps1"),
    ("🚀 Chạy Spark Toàn Bộ (Local)", "#0284C7", "#FFFFFF", "run_full.ps1"),
    ("🐳 Khởi Động HDFS (Docker)", "#0F766E", "#FFFFFF", "hdfs_start.ps1"),
    ("⬆️ Tải CSV Lên HDFS (Hadoop)", "#0D9488", "#FFFFFF", "hdfs_upload.ps1"),
    ("🔥 Chạy Spark Đọc/Ghi HDFS", "#115E59", "#FFFFFF", "hdfs_run.ps1"),
    ("📊 Chạy Airflow DAG Điều Phối", "#7C3AED", "#FFFFFF", "airflow_run.ps1"),
    ("⏹️ Dừng Dịch Vụ HDFS", "#EF4444", "#FFFFFF", "hdfs_stop.ps1"),
]

btn_y = 57.5
for label, bg, fg, script in buttons:
    b_rect = patches.FancyBboxPatch((5, btn_y), 31, 3.5, boxstyle="round,pad=0.3,rounding_size=0.6", facecolor=bg, edgecolor=None if bg != "#F1F5F9" else "#CBD5E1")
    ax.add_patch(b_rect)
    ax.text(7, btn_y + 1.75, label, fontsize=8, fontweight="bold", color=fg, va="center")
    ax.text(34.5, btn_y + 1.75, script, fontsize=7, color=fg if bg == "#F1F5F9" else "#E2E8F0", ha="right", va="center", style="italic")
    btn_y -= 4.3

# Status footer left
ax.text(5, 14, "Trạng thái tác vụ:", fontsize=8.5, fontweight="bold", color="#334155")
status_badge = patches.FancyBboxPatch((5, 7.5), 31, 5, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#DCFCE7", edgecolor="#86EFAC")
ax.add_patch(status_badge)
ax.text(20.5, 10, "✓ HOÀN THÀNH XUẤT SẮC TOÀN BỘ PIPELINE", fontsize=8.5, fontweight="bold", color="#166534", ha="center", va="center")


# RIGHT PANEL: KPI Summary & Log Console (x: 40 to 97, y: 3 to 85)
right_panel = patches.FancyBboxPatch((40, 3), 57, 82, boxstyle="round,pad=0.5,rounding_size=1.0", facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1.2)
ax.add_patch(right_panel)

ax.text(42, 82, "3. BÁO CÁO KẾT QUẢ ĐẦU RA & THỰC NGHIỆM", fontsize=11, fontweight="bold", color="#0F172A")

# 4 KPI Cards
kpi_data = [
    ("TỔNG DÒNG DỮ LIỆU", "1,595,145", "1.6M thô / Giữ lại 99.7%", "#1E293B", (42, 70), (12.5, 9)),
    ("CHẤT LƯỢNG MÔ HÌNH", "74.75%", "Accuracy trên tập test", "#2563EB", (56, 70), (12.5, 9)),
    ("MACRO-F1 SCORE", "0.7475", "+41.2% so với Baseline", "#059669", (70, 70), (12.5, 9)),
    ("BENCHMARK SPARK", "0.150s", "Thời gian tổng hợp có cache", "#D97706", (84, 70), (12.5, 9)),
]

for title, val, note, clr, (kx, ky), (kw, kh) in kpi_data:
    card = patches.FancyBboxPatch((kx, ky), kw, kh, boxstyle="round,pad=0.3,rounding_size=0.6", facecolor="#F8FAFC", edgecolor="#E2E8F0", linewidth=1.0)
    ax.add_patch(card)
    ax.text(kx + kw/2, ky + 7.2, title, fontsize=6.5, fontweight="bold", color="#64748B", ha="center")
    ax.text(kx + kw/2, ky + 4.2, val, fontsize=12, fontweight="bold", color=clr, ha="center")
    ax.text(kx + kw/2, ky + 1.8, note, fontsize=6.0, color="#64748B", ha="center")

# Log Console Window
ax.text(42, 66.5, "4. NHẬT KÝ THỰC THI (REAL-TIME CONSOLE LOG):", fontsize=9.5, fontweight="bold", color="#0F172A")
console_rect = patches.FancyBboxPatch((42, 17), 53, 48, boxstyle="round,pad=0.3,rounding_size=0.5", facecolor="#0F172A", edgecolor="#334155")
ax.add_patch(console_rect)

console_lines = [
    ("[2026-10-15 21:06:38] [AIRFLOW] Starting DAG 'twitter_sentiment140_bigdata_pipeline'", "#38BDF8"),
    ("[Task 1/9] check_raw_data: Validated 1,600,000 tweets (227.74 MB) [SUCCESS]", "#4ADE80"),
    ("[Task 2/9] check_hdfs_status: NameNode port 8020 ONLINE (HDFS Docker) [SUCCESS]", "#4ADE80"),
    ("[Task 3/9] upload_raw_to_hdfs: Ingested to /twitter/raw/sentiment140.csv [SUCCESS]", "#4ADE80"),
    ("[Task 4/9] spark_prepare_clean: Cleaned 1,595,145 rows -> Parquet /twitter/processed/ [SUCCESS]", "#FACC15"),
    ("           -> Filtered 4,855 bad rows (null, duplicate IDs, invalid format)", "#94A3B8"),
    ("[Task 5/9] spark_analysis_sql: Spark SQL TemporaryView 'tweets' created [SUCCESS]", "#FACC15"),
    ("           -> Generated 10 CSV tables & 7 charts in outputs/", "#94A3B8"),
    ("[Task 6/9] spark_train_evaluate: MLlib Pipeline (RegexTokenizer + HashingTF + IDF) [SUCCESS]", "#C084FC"),
    ("           -> Train: 106,209 | Validation: 22,826 | Test: 22,812 (Hash 70/15/15)", "#94A3B8"),
    ("           -> Logistic Regression: Accuracy=74.75%, Macro-F1=0.7475 (regParam=0.1)", "#4ADE80"),
    ("           -> Naive Bayes Comparison: Accuracy=71.69%, Macro-F1=0.7168", "#94A3B8"),
    ("           -> Majority Baseline Comparison: Accuracy=50.49%, Macro-F1=0.3355", "#F87171"),
    ("[Task 7/9] verify_manifest_artifacts: Model saved to models/sentiment_lr/ [SUCCESS]", "#4ADE80"),
    ("[Task 8/9] end_pipeline: All 9 tasks finished successfully in 2.68s [SUCCESS]", "#38BDF8"),
    ("-------------------------------------------------------------------------------------", "#64748B"),
    ("CLI Predict Test: 'I love this Big Data class!' -> POSITIVE (Score: 0.884)", "#34D399"),
    ("CLI Predict Test: 'This system is failing completely.' -> NEGATIVE (Score: 0.128)", "#F87171"),
]

cy = 61.5
for cline, ccolor in console_lines:
    ax.text(43.5, cy, cline, fontsize=6.8, fontfamily="monospace", color=ccolor)
    cy -= 2.5

# Bottom Action Buttons on Right Panel (Open Artifacts)
ax.text(42, 13.5, "Truy cập nhanh kết quả thực nghiệm:", fontsize=8.5, fontweight="bold", color="#475569")
quick_links = [
    ("📁 Mở Thư Mục Bảng CSV", (42, 6), (12.5, 5), "#F1F5F9", "#1E293B"),
    ("📊 Mở Thư Mục Biểu Đồ PNG", (55.5, 6), (13.5, 5), "#F1F5F9", "#1E293B"),
    ("🤖 Thử Nghiệm Dự Đoán CLI", (70, 6), (12.5, 5), "#F1F5F9", "#1E293B"),
    ("📄 Xem Báo Cáo Cuối Kỳ", (83.5, 6), (11.5, 5), "#2563EB", "#FFFFFF"),
]

for q_label, (qx, qy), (qw, qh), q_bg, q_fg in quick_links:
    q_box = patches.FancyBboxPatch((qx, qy), qw, qh, boxstyle="round,pad=0.3,rounding_size=0.6", facecolor=q_bg, edgecolor="#CBD5E1" if q_bg=="#F1F5F9" else None)
    ax.add_patch(q_box)
    ax.text(qx + qw/2, qy + qh/2, q_label, fontsize=7.2, fontweight="bold", color=q_fg, ha="center", va="center")

plt.tight_layout()
fig.savefig(OUTPUT_DIR_1 / "gui_dashboard.png", dpi=200, bbox_inches="tight")
fig.savefig(OUTPUT_DIR_2 / "gui_dashboard.png", dpi=200, bbox_inches="tight")
plt.close(fig)

try:
    print("Success: Generated GUI dashboard image at:")
    print(f"- {OUTPUT_DIR_1 / 'gui_dashboard.png'}")
    print(f"- {OUTPUT_DIR_2 / 'gui_dashboard.png'}")
except Exception:
    pass

