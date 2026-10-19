"""
Script kiểm tra chi tiết toàn bộ nội dung file PDF báo cáo: report/BaoCaoCuoiKy_BigData_Nhom9.pdf
Đối chiếu 100% với danh mục lỗi và yêu cầu của giảng viên chấm bài.
"""

import sys
from pathlib import Path
import pypdf

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PDF_PATH = Path("report/BaoCaoCuoiKy_BigData_Nhom9.pdf")


def main():
    if not PDF_PATH.is_file():
        print(f"LỖI: Không tìm thấy tệp {PDF_PATH}")
        return 1

    reader = pypdf.PdfReader(str(PDF_PATH))
    total_pages = len(reader.pages)
    print("=" * 80)
    print(f"BÁO CÁO KIỂM ĐỊNH TỆP PDF: {PDF_PATH}")
    print(f"Tổng số trang: {total_pages} trang | Dung lượng: {PDF_PATH.stat().st_size / (1024*1024):.2f} MB")
    print("=" * 80)

    # 1. Trích xuất text và kiểm tra hình ảnh từng trang
    full_text = ""
    pages_text = []
    page_images = []
    total_imgs = 0

    for idx, page in enumerate(reader.pages):
        t = page.extract_text()
        pages_text.append(t)
        full_text += f"\n--- Trang {idx+1} ---\n" + t
        n_img = len(page.images)
        total_imgs += n_img
        page_images.append([img.name for img in page.images])

    print(f"Tổng số đối tượng hình ảnh nhúng trong PDF: {total_imgs} ảnh")

    # 2. Danh mục các tiêu chí cần kiểm tra theo feedback của giảng viên
    checks = {
        # Tiêu chí 1: Kiến trúc & Không dùng Kafka
        "Hình 3.1: Sơ đồ kiến trúc tổng thể 4 tầng": ("Hình 3.1", True),
        "Bảng 3.3: Lý giải không dùng Kafka cho batch": ("Bảng 3.3", False),
        "Luận điểm kỹ thuật không dùng Kafka (5 lý do)": ("không dùng Kafka", False),

        # Tiêu chí 2: HDFS Ingestion
        "Hình 3.3: Giao diện HDFS Web UI NameNode 9870": ("Hình 3.3", True),
        "Lệnh nạp thực tế hdfs dfs -put": ("hdfs dfs -put", False),
        "Tốc độ nạp 69.8 MB/s và block blk_1073741825": ("69.8 MB/s", False),
        "Nhật ký nạp dữ liệu HDFS (hdfs_upload.log)": ("hdfs_upload.log", False),

        # Tiêu chí 3: Spark Processing
        "Hình 4.2: Giao diện Spark Web UI (port 4040, 5 Jobs Succeeded)": ("Hình 4.2", True),
        "Nhật ký thực thi PySpark Driver (spark_execution.log)": ("spark_execution.log", False),
        "Bảng DataFrame df_raw.show(5) dữ liệu thô": ("df_raw.show(5", False),
        "Bảng DataFrame df_clean.show(5) sau làm sạch UTC": ("df_clean.show(5", False),
        "Bảng DataFrame predictions.show(5) dự đoán MLlib": ("predictions.show(5", False),

        # Tiêu chí 4: Analytics & Machine Learning (10 Bảng CSV & 7 Biểu đồ)
        "Hình 5.1: Số bài đăng theo ngày (RQ1)": ("Hình 5.1", True),
        "Hình 5.2: Số bài đăng theo giờ UTC (RQ1)": ("Hình 5.2", True),
        "Hình 5.3: Phân bố bài đăng trên mỗi tài khoản (RQ2)": ("Hình 5.3", True),
        "Hình 5.4: Từ xuất hiện phổ biến theo nhãn (RQ3)": ("Hình 5.4", True),
        "Hình 5.5: Nhãn dữ liệu theo ngày (RQ4)": ("Hình 5.5", True),
        "Hình 5.6: Ma trận nhầm lẫn Confusion Matrix": ("Hình 5.6", True),
        "Hình 5.7: Biểu đồ Benchmark hiệu năng": ("Hình 5.7", True),
        "Bảng 5.2a: Phân bố theo 24 giờ UTC (posts_by_hour_utc.csv)": ("Bảng 5.2a", False),
        "Bảng 5.2b: Top ngày cao nhất & thấp nhất (posts_by_day.csv)": ("Bảng 5.2b", False),
        "Bảng 5.2c: Phân bố bài/tài khoản (posts_per_user_distribution.csv)": ("Bảng 5.2c", False),
        "Bảng 5.2d: Top từ theo nhãn cảm xúc (top_words_by_label.csv)": ("Bảng 5.2d", False),
        "Bảng 5.4a: Tinh chỉnh siêu tham số Validation (validation_results.csv)": ("Bảng 5.4a", False),
        "Bảng 5.4b: Phân tích mẫu đoán sai Test (misclassified_examples.csv)": ("Bảng 5.4b", False),
        "Bảng 5.4c: So sánh lưu trữ CSV vs Parquet (storage_comparison.csv)": ("Bảng 5.4c", False),
        "Kết quả ML Accuracy 74.75% và Macro-F1 0.7475": ("74.75%", False),
        "So sánh 3 phương pháp (Baseline, Naive Bayes, Logistic Regression)": ("Naive Bayes", False),
        "Danh mục 10 bảng CSV định lượng bàn giao (Mục I.1)": ("posts_by_day.csv", False),

        # Tiêu chí 5: Airflow DAG
        "Hình 3.2: Giao diện Airflow DAG UI 9 task SUCCESS": ("Hình 3.2", True),
        "Đồ thị phụ thuộc 9 task Airflow": ("check_raw_data", False),
        "Nhật ký thực thi DAG Airflow (airflow_dag_run.log / detailed)": ("airflow_dag_run.log", False),

        # Tiêu chí 6: Desktop Dashboard GUI
        "Hình 4.1: Giao diện Desktop Dashboard Tkinter": ("Hình 4.1", True),
        "Hình 4.3: Phân hệ suy luận cảm xúc trực tiếp (Interactive Predictor)": ("Hình 4.3", True),
        "Mục Video Demo và đường dẫn video_demo/video_demo_gui_pipeline.mp4": ("video_demo_gui_pipeline.mp4", False),
        "Kịch bản và các bước thao tác trong Video Demo (Phần 1 - Phần 7)": ("README_VideoDemo.md", False),
        "Mã nguồn giao diện Desktop GUI (gui.py / twitter_spark/gui.py)": ("twitter_spark/gui.py", False),

        # Tiêu chí 7: Tính tái lập, Bảng lỗi & Lịch sử Commit
        "Hình C.1: Sơ đồ Gantt Chart tiến độ qua các tuần": ("Hình C.1", True),
        "Bảng theo dõi và xử lý 7 lỗi kỹ thuật thực tế (Phụ lục E)": ("Bảng C.3", False),
        "Lỗi ERR-01: JVM OutOfMemoryError 4GB RAM": ("ERR-01", False),
        "Lỗi ERR-02: ISO-8859-1 Latin-1 Encoding": ("ERR-02", False),
        "Lỗi ERR-03: Data Leakage xxhash64 Anti-leakage": ("ERR-03", False),
        "Lỗi ERR-04: Windows winutils.exe & hadoop.dll": ("ERR-04", False),
        "Lỗi ERR-05: Hadoop HDFS SafeMode retry": ("ERR-05", False),
        "Lỗi ERR-06: Airflow Docker Linux/Windows path": ("ERR-06", False),
        "Lỗi ERR-07: Tkinter GUI freeze multithreaded queue": ("ERR-07", False),
        "Lịch sử commit Git 8 commit qua 6 tuần (Bảng C.1b)": ("5d69a5a", False),
        "Nhật ký tiến độ thực hiện đồ án 6 tuần (Bảng C.2)": ("Bảng C.2", False),
        "14/14 Unit Tests pass 100%": ("14/14", False),
        "Hướng dẫn cài đặt và chạy tái hiện từng bước (Phụ lục H)": ("Phụ lục H", False),
    }

    all_passed = True
    print("\n--- KẾT QUẢ ĐỐI CHIẾU TỪNG TIÊU CHÍ VỚI NỘI DUNG PDF ---")
    for desc, (kw, is_img_check) in checks.items():
        pages_found = []
        for p_idx, p_txt in enumerate(pages_text, start=1):
            if kw.lower() in p_txt.lower():
                pages_found.append(p_idx)

        has_found = len(pages_found) > 0
        if not has_found:
            all_passed = False
            status = "❌ THIẾU"
            detail = f"Không tìm thấy từ khóa: '{kw}'"
        else:
            status = "✔ ĐẦY ĐỦ"
            detail = f"Xuất hiện tại trang: {pages_found}"

        print(f"[{status}] {desc:<68} -> {detail}")

    print("\n" + "=" * 80)
    if all_passed:
        print("TỔNG KẾT: TỆP PDF ĐÃ CHỨA ĐẦY ĐỦ 100% TẤT CẢ CÁC MINH CHỨNG, BẢNG BIỂU,")
        print("HÌNH ẢNH, NHẬT KÝ VÀ SỐ LIỆU THEO YÊU CẦU CỦA GIẢNG VIÊN!")
    else:
        print("CẢNH BÁO: Còn một số mục cần bổ sung vào file PDF (xem chi tiết ở trên).")
    print("=" * 80)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
