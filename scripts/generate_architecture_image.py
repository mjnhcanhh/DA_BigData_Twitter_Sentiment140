"""
Script tạo sơ đồ kiến trúc tổng thể hệ thống Big Data (Hình 3.1)
Phân tích hành vi đăng bài và cảm xúc Twitter bằng Apache Spark, HDFS và Airflow
Lưu vào:
- outputs/charts/architecture_diagram.png
- report/figures/architecture_diagram.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR_1 = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_DIR_2 = PROJECT_ROOT / "report" / "figures"
OUTPUT_DIR_1.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR_2.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=220)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Background Window
bg_rect = patches.FancyBboxPatch(
    (0, 0), 100, 100, boxstyle="square,pad=0",
    facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5
)
ax.add_patch(bg_rect)

# Top Header
header_rect = patches.Rectangle((0, 89), 100, 11, facecolor="#0F172A")
ax.add_patch(header_rect)

ax.text(
    3, 95.5,
    "HỆ THỐNG BIG DATA PHÂN TÍCH HÀNH VI & CẢM XÚC TWITTER",
    fontsize=14.5, fontweight="bold", color="#FFFFFF", va="center"
)
ax.text(
    3, 91.8,
    "Kiến trúc phân tầng kết hợp: Ingestion (HDFS) — Processing (Spark) — MLlib & SQL — Airflow DAG & Desktop GUI",
    fontsize=9.5, color="#94A3B8", va="center"
)

# Top Right Badges
ax.text(97, 95.5, "Apache Spark 3.5.7 • Hadoop HDFS 3.3.6 • Airflow 2.8+", fontsize=9, fontweight="bold", color="#38BDF8", ha="right", va="center")
ax.text(97, 91.8, "Nhóm 09: Võ Minh Cảnh (Trưởng nhóm) • Hồ Thị Thanh Nhã", fontsize=8.5, color="#E2E8F0", ha="right", va="center")

# Layer 1: Data Ingestion & Storage (x: 2.5 to 22.5, y: 16 to 86)
p1 = patches.FancyBboxPatch((2.5, 16), 20, 70, boxstyle="round,pad=0.5,rounding_size=1.0", facecolor="#F0FDF4", edgecolor="#86EFAC", linewidth=1.4)
ax.add_patch(p1)
ax.text(12.5, 83.5, "TẦNG DỮ LIỆU & LƯU TRỮ", fontsize=10.5, fontweight="bold", color="#166534", ha="center")
ax.text(12.5, 81.0, "(Ingestion & Storage Layer)", fontsize=8, color="#15803D", ha="center", style="italic")

# Box 1.1: Raw Dataset
box_raw = patches.FancyBboxPatch((4, 60), 17, 18, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#BBF7D0", linewidth=1.2)
ax.add_patch(box_raw)
ax.text(12.5, 75, "Sentiment140 CSV", fontsize=9.5, fontweight="bold", color="#0F172A", ha="center")
ax.text(12.5, 71.5, "• 1,600,000 tweets thô\n• Mã hóa: ISO-8859-1\n• Dung lượng: ~238 MB\n• Schema 6 cột cố định", fontsize=7.8, color="#334155", ha="center")

# Box 1.2: HDFS Cluster
box_hdfs = patches.FancyBboxPatch((4, 20), 17, 36, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#86EFAC", linewidth=1.2)
ax.add_patch(box_hdfs)
ax.text(12.5, 52.5, "HADOOP HDFS (Docker)", fontsize=9.5, fontweight="bold", color="#047857", ha="center")
ax.text(12.5, 49.5, "hdfs://localhost:8020", fontsize=8, color="#059669", ha="center", family="monospace")
ax.text(12.5, 41, "• NameNode IPC (:8020)\n• NameNode WebUI (:9870)\n• DataNode (:9864/:9866)\n• Block Size: 128 MiB\n• Thư mục nạp thô:\n  /twitter/raw/ (227.7 MB)\n• Thư mục Parquet sạch:\n  /twitter/processed/tweets", fontsize=7.6, color="#334155", ha="center")
ax.text(12.5, 24, "Lý giải Batch: Không dùng Kafka\ndo tập tĩnh, tối ưu I/O đĩa & RAM", fontsize=7.2, color="#047857", ha="center", style="italic")

# Layer 2: Core Processing (x: 25.5 to 49.5, y: 16 to 86)
p2 = patches.FancyBboxPatch((25.5, 16), 24, 70, boxstyle="round,pad=0.5,rounding_size=1.0", facecolor="#EFF6FF", edgecolor="#93C5FD", linewidth=1.4)
ax.add_patch(p2)
ax.text(37.5, 83.5, "TẦNG XỬ LÝ PHÂN TÁN", fontsize=10.5, fontweight="bold", color="#1E40AF", ha="center")
ax.text(37.5, 81.0, "(Apache Spark Engine)", fontsize=8, color="#2563EB", ha="center", style="italic")

box_spark_core = patches.FancyBboxPatch((27, 49), 21, 29, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#BFDBFE", linewidth=1.2)
ax.add_patch(box_spark_core)
ax.text(37.5, 74.5, "TIỀN XỬ LÝ & LÀM SẠCH", fontsize=9.5, fontweight="bold", color="#1D4ED8", ha="center")
ax.text(37.5, 64, "• Spark Master: local[2]\n• RAM: 32 GB | Partition: 8\n• Đọc CSV theo schema chuẩn\n• clean_text_expr():\n  Lọc URL, @mention, ký tự lạ\n• with_parsed_date():\n  Đổi PDT/PST -> UTC Timestamp\n• Loại trùng lặp & mâu thuẫn", fontsize=7.8, color="#334155", ha="center")
ax.text(37.5, 52.5, "Kết quả: 1,595,145 dòng sạch (99.7%)", fontsize=7.6, fontweight="bold", color="#1E40AF", ha="center")

box_parquet = patches.FancyBboxPatch((27, 20), 21, 25, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#BFDBFE", linewidth=1.2)
ax.add_patch(box_parquet)
ax.text(37.5, 41.5, "PARQUET COLUMNAR", fontsize=9.5, fontweight="bold", color="#1D4ED8", ha="center")
ax.text(37.5, 32, "• Lưu dạng cột Snappy nén\n• 8 Part-files song song\n• Dung lượng: ~202 MB\n• Tốc độ đọc: 0.30s (gấp 37.8x CSV)\n• Đăng ký TemporaryView 'tweets'", fontsize=7.8, color="#334155", ha="center")
ax.text(37.5, 23, "Lưu song song Local & HDFS", fontsize=7.5, color="#2563EB", ha="center", style="italic")

# Layer 3: Analytics & MLlib (x: 52.5 to 76.5, y: 16 to 86)
p3 = patches.FancyBboxPatch((52.5, 16), 24, 70, boxstyle="round,pad=0.5,rounding_size=1.0", facecolor="#FAF5FF", edgecolor="#D8B4FE", linewidth=1.4)
ax.add_patch(p3)
ax.text(64.5, 83.5, "TẦNG PHÂN TÍCH & ML", fontsize=10.5, fontweight="bold", color="#6B21A8", ha="center")
ax.text(64.5, 81.0, "(Spark SQL & Spark MLlib)", fontsize=8, color="#7E22CE", ha="center", style="italic")

box_sql = patches.FancyBboxPatch((54, 52), 21, 26, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#E9D5FF", linewidth=1.2)
ax.add_patch(box_sql)
ax.text(64.5, 74.5, "SPARK SQL & EDA", fontsize=9.5, fontweight="bold", color="#7E22CE", ha="center")
ax.text(64.5, 63.5, "• 5 Câu hỏi nghiên cứu (RQ1 - RQ5)\n• Phân bố theo ngày, giờ UTC\n• Phân bố 658,917 người dùng\n• Top từ ngữ theo 2 nhãn cảm xúc\n• 10 Bảng thống kê CSV\n• 7 Biểu đồ trực quan PNG", fontsize=7.8, color="#334155", ha="center")
ax.text(64.5, 54.5, "Xuất ra outputs/tables & charts", fontsize=7.5, color="#6B21A8", ha="center", style="italic")

box_ml = patches.FancyBboxPatch((54, 20), 21, 29, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#E9D5FF", linewidth=1.2)
ax.add_patch(box_ml)
ax.text(64.5, 45.5, "SPARK MLLIB PIPELINE", fontsize=9.5, fontweight="bold", color="#7E22CE", ha="center")
ax.text(64.5, 34, "• Lấy mẫu 10% phân tầng (151k dòng)\n• Chia hash: 70% Train, 15% Val, 15% Test\n• RegexTokenizer -> HashingTF (32k dims)\n• IDF (Inverse Document Frequency)\n• Logistic Regression & Naive Bayes\n• Accuracy: 74.75% | Macro-F1: 0.7475", fontsize=7.8, color="#334155", ha="center")
ax.text(64.5, 23, "Lưu Pipeline tại models/sentiment_lr", fontsize=7.5, fontweight="bold", color="#7E22CE", ha="center")

# Layer 4: Orchestration & Application (x: 79.5 to 97.5, y: 16 to 86)
p4 = patches.FancyBboxPatch((79.5, 16), 18, 70, boxstyle="round,pad=0.5,rounding_size=1.0", facecolor="#FFFBEB", edgecolor="#FCD34D", linewidth=1.4)
ax.add_patch(p4)
ax.text(88.5, 83.5, "ĐIỀU PHỐI & GIAO DIỆN", fontsize=10.5, fontweight="bold", color="#B45309", ha="center")
ax.text(88.5, 81.0, "(Airflow & Desktop GUI)", fontsize=8, color="#D97706", ha="center", style="italic")

box_airflow = patches.FancyBboxPatch((81, 52), 15, 26, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#FDE68A", linewidth=1.2)
ax.add_patch(box_airflow)
ax.text(88.5, 74.5, "APACHE AIRFLOW", fontsize=9.5, fontweight="bold", color="#B45309", ha="center")
ax.text(88.5, 63.5, "• DAG: 9 Tác vụ tự động\n• Dependency tuần tự/song song\n• Empty / Python / Bash Operator\n• Kiểm tra HDFS NameNode\n• Tự động retry và ghi log\n• Thời gian chạy DAG: 2.72s", fontsize=7.8, color="#334155", ha="center")
ax.text(88.5, 54.5, "outputs/logs/airflow_dag_run.log", fontsize=7.2, color="#B45309", ha="center", family="monospace")

box_gui = patches.FancyBboxPatch((81, 20), 15, 29, boxstyle="round,pad=0.4,rounding_size=0.6", facecolor="#FFFFFF", edgecolor="#FDE68A", linewidth=1.2)
ax.add_patch(box_gui)
ax.text(88.5, 45.5, "DESKTOP DASHBOARD", fontsize=9.5, fontweight="bold", color="#B45309", ha="center")
ax.text(88.5, 34, "• Lập trình Tkinter GUI thuần\n• Điều khiển Spark, HDFS, Airflow\n• Theo dõi Log thời gian thực\n• Thẻ hiển thị KPI trực quan\n• Dự đoán cảm xúc trực tiếp:\n  (Interactive Sentiment Predictor)\n• Mở nhanh bảng CSV & đồ thị", fontsize=7.8, color="#334155", ha="center")
ax.text(88.5, 23, "python main.py gui", fontsize=7.5, fontweight="bold", color="#B45309", ha="center", family="monospace")

# Connective Arrows between Layers
arrow_props = dict(facecolor="#475569", edgecolor="#334155", width=1.5, headwidth=6, headlength=6)

# Raw CSV -> HDFS
ax.annotate("", xy=(12.5, 56.5), xytext=(12.5, 60), arrowprops=arrow_props)
# HDFS -> Spark Ingestion
ax.annotate("", xy=(27, 65), xytext=(21, 65), arrowprops=arrow_props)
# Clean Spark -> Parquet
ax.annotate("", xy=(37.5, 45.5), xytext=(37.5, 49), arrowprops=arrow_props)
# Parquet -> SQL
ax.annotate("", xy=(54, 65), xytext=(48, 65), arrowprops=arrow_props)
# Parquet -> ML
ax.annotate("", xy=(54, 35), xytext=(48, 35), arrowprops=arrow_props)
# Airflow orchestrating Spark & HDFS (Top arrow)
ax.annotate("", xy=(49.5, 80), xytext=(79.5, 80), arrowprops=dict(facecolor="#B45309", edgecolor="#B45309", width=1.5, headwidth=6, headlength=6, linestyle="dashed"))
# ML & SQL outputs -> GUI
ax.annotate("", xy=(81, 35), xytext=(75, 35), arrowprops=arrow_props)

# Bottom Status Footer
footer_rect = patches.Rectangle((0, 0), 100, 12, facecolor="#F1F5F9", edgecolor="#CBD5E1")
ax.add_patch(footer_rect)
ax.text(
    5, 6,
    "Ghi chú: Toàn bộ đường ống đã được thực thi và kiểm chứng trên dữ liệu thật Sentiment140 (1.6M dòng) • Đạt 13/13 Unit Tests (100% OK)",
    fontsize=8.5, fontweight="bold", color="#0F172A", va="center"
)
ax.text(
    95, 6,
    "Hình 3.1: Sơ đồ Kiến trúc tổng thể hệ thống Big Data",
    fontsize=9.5, fontweight="bold", color="#1E293B", ha="right", va="center"
)

out_file_1 = OUTPUT_DIR_1 / "architecture_diagram.png"
out_file_2 = OUTPUT_DIR_2 / "architecture_diagram.png"
plt.tight_layout()
fig.savefig(out_file_1, dpi=220, bbox_inches="tight")
fig.savefig(out_file_2, dpi=220, bbox_inches="tight")
plt.close(fig)

print(f"Generated architecture diagram successfully:")
print(f"-> {out_file_1.resolve()} ({out_file_1.stat().st_size / 1024:.1f} KB)")
print(f"-> {out_file_2.resolve()} ({out_file_2.stat().st_size / 1024:.1f} KB)")
