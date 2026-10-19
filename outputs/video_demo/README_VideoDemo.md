# HƯỚNG DẪN KIỂM CHỨNG VIDEO DEMO VẬN HÀNH HỆ THỐNG
## ĐỒ ÁN CÔNG NGHỆ DỮ LIỆU LỚN (BIG DATA) — NHÓM 09
**Đề tài:** Phân tích hành vi đăng bài và cảm xúc Twitter bằng Apache Spark, HDFS, Airflow DAG và MLlib  
**Tệp video minh chứng:** `video_demo/video_demo_gui_pipeline.mp4` (Chuẩn HD 1280x720, 20 FPS)  
**Nhóm sinh viên thực hiện:**  
- **Võ Minh Cảnh** — MSSV: 2001230065 (Trưởng nhóm)  
- **Hồ Thị Thanh Nhã** — MSSV: 2001230592 (Thành viên)  

---

## 1. MỤC TIÊU CỦA VIDEO DEMO
Video demo được xây dựng nhằm cung cấp bằng chứng trực quan trực tiếp, có thể phát trên mọi trình xem video chuẩn (Windows Media Player, VLC, QuickTime, Google Chrome, Microsoft Edge...) nhằm giải trình và minh chứng rõ ràng:
1. **Kiến trúc hệ thống 4 tầng:** Tầng nạp HDFS phân tán, Tầng xử lý PySpark 3.5.7, Tầng điều phối Apache Airflow DAG và Tầng giao diện Desktop Tkinter Control Center.
2. **Khởi động và điều phối giao diện:** Người dùng tương tác trực tiếp với giao diện Desktop GUI thông qua lệnh `python gui.py`.
3. **Thực thi luồng dữ liệu lớn (Big Data Pipeline):** Đọc tệp Sentiment140 CSV (1.600.000 dòng, 238.8 MB) qua HDFS, chuẩn hóa thời gian UTC, làm sạch văn bản, phân tích Spark SQL và huấn luyện Spark MLlib TF-IDF + Logistic Regression (Accuracy = 74.75%, Macro-F1 = 0.7475).
4. **Trực quan hóa bảng dữ liệu `DataFrame.show(5)`:** So sánh trực tiếp dữ liệu thô và dữ liệu sạch, UTC timestamp, schema 6 cột.
5. **Dự đoán cảm xúc trực tiếp (Interactive Predictor):** Nhập thử nghiệm câu tweet từ bàn phím, phân tích từ ngữ phủ định và suy luận xác suất cảm xúc tức thì.
6. **Kiểm chứng Web UI:** Truy cập trực tiếp Apache Spark Web UI (Port 4040), Hadoop HDFS Web UI (Port 9870) và Apache Airflow DAG Web UI (Port 8080).

---

## 2. PHÂN ĐOẠN NỘI DUNG VÀ MỐC THỜI GIAN TRONG VIDEO DEMO

| Phân đoạn | Mốc thời gian | Tiêu đề phân đoạn | Nội dung thao tác và Minh chứng trực quan |
|:---:|:---:|:---|:---|
| **Phần 1** | `00:00 – 00:04` | Giới thiệu Đề tài & Nhóm tác giả | Slide tiêu đề chuẩn đồ họa, giới thiệu thành viên, các công nghệ sử dụng (PySpark, HDFS, Airflow, MLlib, Tkinter). |
| **Phần 2** | `00:04 – 00:08` | Kiến trúc Tổng thể Hệ thống 4 Tầng | Hiển thị sơ đồ kiến trúc Hình 3.1, giải trình chi tiết luồng dữ liệu Batch HDFS phân tán và 5 lý do kỹ thuật không dùng Kafka. |
| **Phần 3** | `00:08 – 00:14` | Giao diện Desktop Control Center Dashboard | Trình diễn giao diện Desktop Tkinter (Hình 4.1), thao tác chọn file CSV `training.1600000.processed.noemoticon.csv`, cấu hình tỷ lệ mẫu 0.10, và bấm nút chạy pipeline. |
| **Phần 4** | `00:14 – 00:24` | Nhật ký Thực thi Spark & DataFrame.show(5) | Cửa sổ dòng lệnh Terminal cuộn thời gian thực: Khởi tạo SparkContext 4GB RAM, nạp HDFS 69.8 MB/s, bảng mẫu `df_raw.show(5)` và `df_clean.show(5)`, truy vấn SQL đỉnh ngày 111.540 bài, huấn luyện MLlib đạt 74.75%. |
| **Phần 5** | `00:24 – 00:34` | Dự đoán Cảm xúc Trực tiếp (Live Predictor) | Thao tác nhập và dự đoán 3 câu tweet thực tế:<br>1. Tweet tích cực: *"I love this new big data spark pipeline!..."* → Xanh: **TÍCH CỰC (94.2%)**<br>2. Tweet tiêu cực: *"I hate waiting in traffic so much..."* → Đỏ: **TIÊU CỰC (96.8%)**<br>3. Tweet phủ định: *"The movie was not good."* → Đỏ: **TIÊU CỰC (78.4%)** |
| **Phần 6** | `00:34 – 00:40` | Kiểm chứng Web UI HDFS, Spark, Airflow | Trình chiếu giao diện thực tế của:<br>• Apache Spark Web UI (Port 4040, 5 Jobs Succeeded)<br>• Hadoop HDFS Web UI (Port 9870, Browse Directory /twitter/raw/)<br>• Apache Airflow DAG Graph View (Port 8080, 9 Tasks SUCCESS) |
| **Phần 7** | `00:40 – 00:45` | Tổng kết Nghiệm thu Toàn diện | Bảng đối chiếu 100% tiêu chí đạt được, danh mục gói hồ sơ nghiệm thu đính kèm. |

---

## 3. CÁCH THỨC TÁI HIỆN VÀ CHẠY LIVE TRÊN MÁY CHẤM THI

Giảng viên hoặc người chấm có thể tái hiện toàn bộ giao diện và luồng thực thi trong video bằng các lệnh đơn giản sau:

### Bước 1: Khởi động Giao diện Desktop Dashboard
```bash
# Trong thư mục dự án:
python gui.py
# Hoặc sử dụng script PowerShell tiện ích:
.\scripts\gui.ps1
```

### Bước 2: Chạy Demo Nhanh Pipeline (Dữ liệu Demo)
- Nhấn trực tiếp nút **"Demo nhanh"** trên giao diện Desktop GUI.
- Hoặc chạy từ terminal:
```powershell
.\scripts\demo.ps1
```

### Bước 3: Thử nghiệm Dự đoán Cảm xúc Trực tiếp
- Tại phân hệ **"Dự đoán cảm xúc trực tiếp"** trên giao diện, nhập bất kỳ câu tweet tiếng Anh nào hoặc nhấn các nút mẫu có sẵn (**"Tích cực"**, **"Tiêu cực"**, **"Phủ định"**).
- Nhấn nút **"⚡ Dự đoán"** để xem nhãn cảm xúc, tỷ lệ tin cậy và thanh phân bố xác suất thay đổi theo thời gian thực.
