"""
Sinh biểu đồ Gantt Chart trực quan hóa tiến độ thực hiện đồ án Big Data Nhóm 09
Sử dụng matplotlib để tạo hình ảnh biểu đồ Gantt chất lượng cao phục vụ chèn báo cáo.
"""

from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PNG_CHARTS = PROJECT_ROOT / "outputs" / "charts" / "gantt_chart.png"
OUT_PNG_FIGURES = PROJECT_ROOT / "report" / "figures" / "gantt_chart.png"
OUT_PNG_FIGURES.parent.mkdir(parents=True, exist_ok=True)
OUT_PNG_CHARTS.parent.mkdir(parents=True, exist_ok=True)

# Danh sách công việc, mốc thời gian và người phụ trách
tasks = [
    {"task": "1. Khảo sát đề tài & Bộ dữ liệu Sentiment140", "start": "2026-08-01", "end": "2026-08-07", "owner": "Cả hai", "phase": "Giai đoạn 1", "color": "#1E40AF"},
    {"task": "2. Thiết lập cụm Hadoop HDFS Docker", "start": "2026-08-08", "end": "2026-08-14", "owner": "Võ Minh Cảnh", "phase": "Giai đoạn 1", "color": "#1E40AF"},
    {"task": "3. Tiền xử lý dữ liệu Spark, lọc trùng, lưu Parquet", "start": "2026-08-15", "end": "2026-08-21", "owner": "Võ Minh Cảnh", "phase": "Giai đoạn 2", "color": "#0284C7"},
    {"task": "4. Spark SQL EDA, tổng hợp hành vi & xuất biểu đồ", "start": "2026-08-22", "end": "2026-08-28", "owner": "Cả hai", "phase": "Giai đoạn 2", "color": "#0284C7"},
    {"task": "5. Xây dựng MLlib Pipeline & Anti-Leakage Hash", "start": "2026-08-29", "end": "2026-09-07", "owner": "Hồ Thị Thanh Nhã", "phase": "Giai đoạn 3", "color": "#0D9488"},
    {"task": "6. Lập trình Desktop Dashboard GUI (Tkinter)", "start": "2026-09-08", "end": "2026-09-20", "owner": "Hồ Thị Thanh Nhã", "phase": "Giai đoạn 3", "color": "#0D9488"},
    {"task": "7. Xây dựng DAG Apache Airflow điều phối 9 tasks", "start": "2026-09-16", "end": "2026-09-28", "owner": "Võ Minh Cảnh", "phase": "Giai đoạn 4", "color": "#4F46E5"},
    {"task": "8. Đo lường Benchmark & Chạy Unit Tests 13/13", "start": "2026-09-25", "end": "2026-10-05", "owner": "Cả hai", "phase": "Giai đoạn 4", "color": "#4F46E5"},
    {"task": "9. Hoàn thiện Báo cáo cuối kỳ, Slide & Nghiệm thu", "start": "2026-10-04", "end": "2026-10-15", "owner": "Cả hai", "phase": "Nghiệm thu", "color": "#16A34A"},
]

def main():
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]

    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=200)

    y_ticks = []
    y_labels = []

    for idx, item in enumerate(tasks):
        y_pos = len(tasks) - 1 - idx
        start_dt = datetime.strptime(item["start"], "%Y-%m-%d")
        end_dt = datetime.strptime(item["end"], "%Y-%m-%d")
        duration = (end_dt - start_dt).days + 1

        # Vẽ thanh tiến độ
        bar = ax.barh(
            y=y_pos,
            width=duration,
            left=mdates.date2num(start_dt),
            height=0.55,
            align="center",
            color=item["color"],
            edgecolor="#FFFFFF",
            linewidth=1.2,
            zorder=3,
        )

        # Ghi chú người phụ trách
        owner_text = f" [{item['owner']}]"
        ax.text(
            mdates.date2num(end_dt) + 1.2,
            y_pos,
            owner_text,
            va="center",
            ha="left",
            fontsize=9.5,
            fontweight="bold",
            color=item["color"],
            zorder=4,
        )

        y_ticks.append(y_pos)
        y_labels.append(item["task"])

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=10.5, color="#1E293B", fontweight="medium")

    # Cấu hình trục thời gian
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.set_xlim(mdates.date2num(datetime(2026, 7, 28)), mdates.date2num(datetime(2026, 10, 25)))

    # Lưới và định dạng nền
    ax.grid(True, axis="x", linestyle="--", alpha=0.5, color="#CBD5E1", zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#94A3B8")
    ax.spines["bottom"].set_color("#94A3B8")

    # Mốc đánh giá tiến độ (Milestone giữa kỳ)
    mid_date = mdates.date2num(datetime(2026, 9, 15))
    ax.axvline(x=mid_date, color="#DC2626", linestyle=":", linewidth=1.5, zorder=2)
    ax.text(mid_date - 1, 8.3, "Mốc Báo cáo tiến độ (15/09)", color="#DC2626", fontsize=9, fontweight="bold", ha="right")

    # Tiêu đề
    plt.title(
        "SƠ ĐỒ GANTT CHART TIẾN ĐỘ THỰC HIỆN ĐỒ ÁN BIG DATA — NHÓM 09\n"
        "(Võ Minh Cảnh & Hồ Thị Thanh Nhã — Học kỳ I / 2026-2027)",
        fontsize=12.5,
        fontweight="bold",
        color="#0F172A",
        pad=16,
    )
    plt.xlabel("Dòng thời gian (Tuần / Tháng)", fontsize=10.5, color="#475569", labelpad=8)

    plt.tight_layout()
    plt.savefig(str(OUT_PNG_CHARTS), dpi=200, bbox_inches="tight")
    plt.savefig(str(OUT_PNG_FIGURES), dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Gantt chart image generated successfully: {OUT_PNG_CHARTS.resolve()}")

if __name__ == "__main__":
    main()
