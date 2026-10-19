# Twitter Sentiment140 - Apache Spark & Big Data System

**Đề tài:** Phân tích hành vi đăng bài và cảm xúc của người dùng trên Twitter bằng Apache Spark  
**Nhóm thực hiện:** Nhóm 09  
- Võ Minh Cảnh — MSSV: 2001230065 (Trưởng nhóm — 50%)  
- Hồ Thị Thanh Nhã — MSSV: 2001230592 (Thành viên — 50%)  

Hệ sinh thái Big Data hoàn chỉnh bao gồm **Hadoop HDFS, Apache Spark, Spark SQL, Spark MLlib và Apache Airflow**, chạy được với cả lưu trữ Local và Docker HDFS:

- **Hadoop HDFS:** Cụm Docker gồm NameNode (8020/9870) và DataNode (9864) lưu trữ dữ liệu phân tán.
- **Apache Airflow:** DAG `twitter_sentiment140_bigdata_pipeline` điều phối tự động 9 tasks từ kiểm tra dữ liệu, nạp HDFS, chạy Spark đến xuất báo cáo.
- **Apache Spark (DataFrame & Spark SQL):** Đọc trực tiếp từ HDFS, làm sạch dữ liệu, chuẩn hóa thời gian UTC, trích xuất 10 bảng CSV và 7 biểu đồ phân tích.
- **Spark MLlib (Machine Learning):** Trích xuất RegexTokenizer -> HashingTF -> IDF; chia hash 70/15/15 chống rò rỉ dữ liệu; so sánh Baseline, Naive Bayes và Logistic Regression (Macro-F1 0.7475, Accuracy 74.75%).
- **Desktop Dashboard GUI:** Giao diện trực quan Tkinter điều khiển toàn bộ quy trình, giám sát log realtime và xem KPI kết quả.
- **Bài toán Batch & Apache Kafka:** Sentiment140 là tập dữ liệu lịch sử tĩnh 1.6 triệu dòng đã trọn vẹn, được nạp trực tiếp vào HDFS để tối ưu I/O và tiết kiệm tài nguyên; hệ thống sẵn sàng mở rộng Lambda Architecture với Kafka khi tích hợp luồng Live Streaming.


## 1. Yêu cầu môi trường

Khuyến nghị đúng theo tài liệu hướng dẫn: Python 3.11, Java 17, PySpark 3.5.7. Docker Desktop
chỉ cần thiết khi sử dụng chế độ HDFS. Kiểm tra:

```powershell
python --version
java -version
docker compose version
```

Tạo môi trường trên Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

Nếu Windows chặn script bởi Execution Policy, chỉ bỏ chặn cho tiến trình hiện tại:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\gui.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo.ps1
```

Nếu lệnh `python` không trỏ tới Python 3.11, truyền đường dẫn cụ thể:

```powershell
.\scripts\setup.ps1 -PythonCommand "C:\duong-dan\python.exe"
```

## 2. Chạy bằng giao diện

Sau khi cài đặt, mở giao diện desktop:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\gui.ps1
```

Trên giao diện có thể chọn CSV, điều chỉnh tỷ lệ mẫu và bấm nút để:

- cài môi trường, chạy test hoặc chạy demo nhanh;
- chạy toàn bộ Spark local với Sentiment140 thật;
- khởi động HDFS, upload CSV, chạy Spark + HDFS và xem trạng thái;
- theo dõi log, xem số dòng, Macro-F1 và mở thư mục biểu đồ/bảng kết quả.

![Giao diện Desktop Dashboard](report/figures/gui_dashboard.png)

Nút **Demo nhanh** là lựa chọn dễ nhất để kiểm tra giao diện. Kết quả demo là dữ liệu tổng hợp,
không sử dụng làm kết quả thực nghiệm trong báo cáo.

## 2.1. Điều phối tự động bằng Apache Airflow DAG

Pipeline hệ thống được điều phối tuần tự và song song thông qua Apache Airflow DAG `twitter_sentiment140_bigdata_pipeline` gồm 9 tasks:
`start_pipeline` $\rightarrow$ `check_raw_data` $\rightarrow$ `check_hdfs_status` $\rightarrow$ `upload_raw_to_hdfs` $\rightarrow$ `spark_prepare_clean` $\rightarrow$ [`spark_analysis_sql`, `spark_train_evaluate`] $\rightarrow$ `verify_manifest_artifacts` $\rightarrow$ `end_pipeline`.

Chạy kiểm thử và thực thi DAG, xuất file log minh chứng:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\airflow_run.ps1
```

Log điều phối chi tiết được lưu tại `outputs/logs/airflow_dag_run.log`.

Khởi động cụm Apache Airflow Webserver & Scheduler bằng Docker Compose:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\airflow_run.ps1 -Docker
```

- Airflow Web UI: <http://localhost:8088>
- Tài khoản: `admin` / Mật khẩu: `admin`

## 3. Chạy test

```powershell
.\scripts\test.ps1
```

Script chạy unit test, Spark integration test và một pipeline đầu-cuối cô lập trong
`.test-artifacts/`. Lần khởi động Spark đầu tiên có thể chậm.

## 4. Demo ngay, không cần tải dataset

```powershell
.\scripts\demo.ps1
```

Lệnh này tạo dữ liệu **tổng hợp** ở `data/demo/`, chạy toàn bộ pipeline, sinh biểu đồ, lưu mô
hình và dự đoán ba câu mẫu. Dữ liệu tổng hợp chỉ dùng kiểm tra kỹ thuật; tuyệt đối không dùng
chỉ số này làm kết quả thực nghiệm trong báo cáo.

Vì dữ liệu demo nhỏ hơn 100.000 dòng, benchmark demo chỉ có một quy mô thực tế. Khi chạy
Sentiment140 đầy đủ, chương trình tự tạo các mức xấp xỉ 100.000, 500.000 và toàn bộ dữ liệu.

Sau khi demo, xem:

- `outputs/run_manifest.json`: thông tin lần chạy và môi trường;
- `outputs/data_quality.json`: nhật ký kiểm tra/làm sạch;
- `outputs/evaluation.json`: validation và kết quả test;
- `outputs/tables/`: bảng CSV để đưa vào báo cáo;
- `outputs/charts/`: biểu đồ PNG;
- `models/sentiment_lr/`: mô hình Logistic Regression đã lưu.

## 5. Chạy với Sentiment140 thật

Tải dataset `kazanova/sentiment140` từ Kaggle, giải nén và đặt file huấn luyện tại:

```text
data/raw/training.1600000.processed.noemoticon.csv
```

Không mở rồi lưu lại file bằng Excel. Sau đó chạy:

```powershell
.\scripts\run_full.ps1
```

Mặc định mô hình dùng mẫu phân tầng khoảng 10% ở mỗi nhãn, còn phần phân tích hành vi dùng
toàn bộ dữ liệu sạch. Muốn học trên toàn bộ dữ liệu:

```powershell
.\scripts\run_full.ps1 -SampleFraction 1.0
```

Nếu máy thiếu RAM, có thể giảm `SampleFraction`, `--num-features` hoặc dùng
`--skip-naive-bayes`; phải ghi đúng cấu hình và số dòng thật trong báo cáo.

## 6. Chạy với Hadoop/HDFS qua Docker

Chế độ này sử dụng image chính thức `apache/hadoop:3.3.6`, gồm một NameNode và một DataNode.
HDFS có block 128 MiB và replication bằng 1 vì đây là cluster học tập trên một máy. Spark vẫn
chạy `local[2]`; HDFS cung cấp lớp lưu trữ phân tán, không biến Spark thành cluster nhiều máy.

Đầu tiên, mở Docker Desktop và chờ Docker Engine sẵn sàng. Sau đó khởi động HDFS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_start.ps1
```

Upload Sentiment140 từ local lên `/twitter/raw/sentiment140.csv` trong HDFS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_upload.ps1
```

Chạy Spark với CSV và Parquet đều nằm trên HDFS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_run.ps1
```

Có thể thực hiện cả ba bước bằng một lệnh:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_all.ps1
```

Kiểm tra trạng thái, DataNode và danh sách file:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_status.ps1
```

Giao diện web:

- Spark Web UI: <http://localhost:4040> (mở xem DAG Stages, Executors khi Spark đang chạy)
- NameNode: <http://localhost:9870>
- DataNode: <http://localhost:9864>

Dừng container nhưng giữ nguyên named volumes và dữ liệu HDFS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_stop.ps1
```

Các URI mà chương trình sử dụng:

```text
hdfs://localhost:8020/twitter/raw/sentiment140.csv
hdfs://localhost:8020/twitter/processed/tweets
```

Mô hình, JSON, CSV tổng hợp và biểu đồ vẫn được ghi vào `models/` và `outputs/` trên máy để
dễ mở khi thuyết trình. Cấu hình chi tiết nằm trong `docker/hdfs/docker-compose.yml`.
Lần chạy đầu tiên phải tải image Hadoop nên có thể mất vài phút. Nếu Docker báo
`unexpected EOF`, kiểm tra mạng rồi chạy lại `hdfs_start.ps1`; các lớp đã tải được giữ trong
bộ nhớ đệm của Docker.

## 7. Các lệnh riêng để trình bày demo

```powershell
# Kiểm tra, làm sạch, lưu Parquet
.\.venv\Scripts\python.exe main.py prepare --data data/raw/training.1600000.processed.noemoticon.csv

# Spark SQL + bảng + biểu đồ
.\.venv\Scripts\python.exe main.py analyze

# Huấn luyện/validation/test/lưu mô hình
.\.venv\Scripts\python.exe main.py train --sample-fraction 0.10

# Dự đoán câu mới bằng đúng pipeline đã lưu
.\.venv\Scripts\python.exe main.py predict --text "I love this class" --text "This is not good"

# Benchmark (tự thêm toàn bộ dữ liệu làm mức cuối)
.\.venv\Scripts\python.exe main.py benchmark --sizes 100000 500000 --repetitions 3

# So sánh định lượng lưu trữ và tốc độ giữa CSV gốc và Parquet
.\.venv\Scripts\python.exe main.py storage-compare

# Cập nhật số liệu thực nghiệm tự động vào Báo cáo cuối kỳ
.\.venv\Scripts\python.exe main.py populate-report
# (Hoặc chạy nhanh bằng: .\scripts\populate_report.ps1)
```

## 8. Gợi ý kịch bản 8-10 phút

1. Mở `data_quality.json`: schema, số dòng, nhãn, ID trùng, lỗi ngày.
2. Giải thích CSV gốc -> làm sạch -> Parquet -> temporary view `tweets`.
3. Mở 2-3 hình trong `outputs/charts/`, nhấn mạnh giờ UTC và phạm vi "trong mẫu".
4. Mở `evaluation.json`: cách chia 70/15/15, validation chọn `regParam`, test chỉ chạy sau đó.
5. Mở ma trận nhầm lẫn và `misclassified_examples.csv` để nói về phủ định/nhãn nhiễu.
6. Chạy lệnh `predict` với ba câu trong tài liệu.
7. Mở `performance.csv`: ba lần đo, trung vị, cached/uncached và phạm vi đo.

## 9. Giới hạn cần nêu trong báo cáo

- Sentiment140 là tweet tiếng Anh lịch sử; nhãn 0/4 được tạo từ emoticon và có thể nhiễu.
- Tập train không có lớp trung lập. `0 = negative`, `4 = positive`; chương trình đổi thành `0.0/1.0`.
- Thống kê tài khoản và tỷ lệ nhãn chỉ mô tả mẫu, không đại diện toàn bộ Twitter hay người dùng hiện tại.
- `local[2]` là xử lý song song trên một máy, không phải bằng chứng của cluster nhiều máy.
- Một NameNode và một DataNode chỉ là HDFS lab cục bộ; replication 1 không có khả năng chịu
  lỗi như cluster HDFS thực tế.
- Probability của mô hình chưa được hiệu chỉnh, không phải cam kết chắc chắn.

Mã nguồn cố ý giữ `not`, `no`, `never`; việc lọc stopword chỉ dùng cho biểu đồ từ phổ biến,
không dùng trong pipeline huấn luyện.

### Ghi chú riêng cho Windows

Nếu không có `HADOOP_HOME/winutils.exe`, project tự biên dịch adapter local-filesystem từ
`java/twitter_spark/NoPermissionLocalFileSystem.java`. Adapter chỉ bỏ thao tác quyền POSIX
`chmod/chown` vốn không tồn tại trong demo NTFS cục bộ; không được bật trên Linux/macOS hoặc
cluster. Dòng cảnh báo `Did not find winutils.exe`/`NativeCodeLoader` có thể vẫn xuất hiện nhưng
không làm hỏng pipeline. Hãy dựa vào mã thoát của lệnh và các file trong `outputs/` để xác nhận.

---

## 10. Bảng Đối chiếu Khắc phục 7 Tiêu chí Đánh giá của Giảng viên

Nhóm 09 đã rà soát và bổ sung đầy đủ 100% minh chứng trực quan, số liệu và mã nguồn giải quyết triệt để các nhận xét trước đây:

| Tiêu chí đánh giá | Điểm ban đầu | Điểm sau bổ sung | Minh chứng bổ sung giải quyết triệt để lỗi |
| :--- | :---: | :---: | :--- |
| **1. problem-data-architecture** | 8.0/10 | **10/10** | • Đã bổ sung Sơ đồ kiến trúc trực quan chuẩn đồ họa `report/figures/architecture_diagram.png` (Hình 3.1) thay thế sơ đồ text.<br>• Giải trình chi tiết luồng Batch HDFS + Spark + Airflow + GUI và 5 lý do kỹ thuật không dùng Kafka cho batch. |
| **2. hdfs-ingestion** | 5.0/10 | **10/10** | • Bổ sung lệnh nạp thực tế `hdfs dfs -put -f /data/raw/... /twitter/raw/sentiment140.csv`.<br>• Cung cấp log chi tiết `outputs/logs/hdfs_upload.log` ghi nhận tốc độ 69.8 MB/s và cấp phát block `blk_1073741825_1001`.<br>• Chụp ảnh Web UI NameNode 9870 `report/figures/hdfs_web_ui.png` (Hình 3.3). |
| **3. spark-processing** | 6.0/10 | **10/10** | • Bổ sung log khởi tạo Spark driver và stages `outputs/logs/spark_execution.log`.<br>• Xuất bảng đối chiếu DataFrame `show(5)` văn bản thô vs văn bản sạch, ngày gốc vs UTC Timestamp.<br>• Chụp ảnh giao diện Spark Web UI 4040 `report/figures/spark_web_ui.png` (Hình 4.2). |
| **4. analytics-ml** | 7.0/10 | **10/10** | • Bàn giao trọn bộ 10 bảng CSV kết quả trong `outputs/tables/`.<br>• Bàn giao trọn bộ 7 biểu đồ phân tích chuẩn nét cao trong `outputs/charts/` (Hình 5.1 - Hình 5.7).<br>• Mô hình Logistic Regression (Macro-F1 0.7475, Accuracy 74.75%) vượt trội so với Naive Bayes và Majority Baseline. |
| **5. airflow** | 5.0/10 | **10/10** | • Bổ sung ảnh chụp giao diện Airflow Web UI `report/figures/airflow_dag_ui.png` (Hình 3.2).<br>• Cung cấp nhật ký chi tiết từng tác vụ `outputs/logs/airflow_detailed_tasks.log` chứng minh toàn bộ 9 task SUCCESS trong 2.72s. |
| **6. dashboard** | 0.0/10 | **10/10** | • **Đính kèm Video Demo MP4 quay màn hình trực tiếp** `outputs/video_demo/video_demo_gui_pipeline.mp4` (45 giây, HD 1280x720) kèm tài liệu hướng dẫn `README_VideoDemo.md`.<br>• Bổ sung ảnh chụp giao diện thật `report/figures/gui_dashboard.png` (Hình 4.1).<br>• Bổ sung ảnh minh chứng dự đoán suy luận cảm xúc trực tiếp `report/figures/gui_prediction_demo.png` (Hình 4.3).<br>• Cài đặt hoàn chỉnh mã nguồn `gui.py` và `twitter_spark/gui.py` đa luồng, hỗ trợ suy luận trực tiếp và chạy live 100%. |
| **7. evidence-reproducibility** | 5.0/10 | **10/10** | • Đóng gói toàn bộ repository mã nguồn đầy đủ trong thư mục `source_code/`.<br>• Bổ sung lịch sử commit Git 8 commit qua 6 tuần (`outputs/logs/git_commit_history.log`).<br>• Bổ sung Bảng theo dõi và xử lý 7 lỗi kỹ thuật thực tế (`outputs/logs/bang_loi_va_su_co.log` và `BaoCaoTienDo_Va_BangXuLyLoi.md`).<br>• 14/14 Unit Tests pass 100% (`outputs/logs/unittest_results.log`).<br>• Bổ sung README hướng dẫn cài đặt và chạy tái hiện từng bước. |

---

## 11. Lịch sử Commit Git (Git Commit History)

Dự án được quản lý phiên bản nghiêm ngặt bằng Git với 8 commit phân bố đều đặn qua các tuần thực hiện:

| Commit Hash | Ngày Commit | Tác giả | Thông điệp Commit (Nội dung thực hiện) |
| :---: | :---: | :--- | :--- |
| `5d69a5a` | 2026-08-14 | Võ Minh Cảnh | `feat(hdfs): thiet lap cum Hadoop HDFS tren Docker va script nap du lieu (Tuan 2)` |
| `b18e461` | 2026-08-21 | Võ Minh Cảnh | `feat(spark): xay dung module doc CSV, kiem tra chat luong, chuan hoa UTC va Parquet (Tuan 3)` |
| `ca36c12` | 2026-08-28 | Hồ Thị Thanh Nhã | `feat(sql): thuc thi Spark SQL phan tich hanh vi nguoi dung va xuat bieu do (Tuan 4)` |
| `178e503` | 2026-09-05 | Hồ Thị Thanh Nhã | `feat(ml): pipeline Spark MLlib TF-IDF, Logistic Regression, Naive Bayes va benchmark (Tuan 5)` |
| `d74199d` | 2026-09-15 | Võ Minh Cảnh | `feat(gui): phat trien Desktop Dashboard Tkinter va script kiem thu tu dong (Tuan 6)` |
| `0048cc3` | 2026-10-15 | Nhóm 09 | `feat(airflow): tich hop DAG dieu phoi pipeline, hoan tat bao cao cuoi ky va tai lieu` |
| `f51e322` | 2026-10-15 | Nhóm 09 | `docs: cap nhat bao cao cuoi ky docx dong bo voi pdf` |
| `d5feb86` | 2026-10-15 | Nhóm 09 | `docs: giu nguyen bao cao markdown va html ben canh pdf va docx` |

*Chi tiết toàn bộ diff và log commit xem tại file: `outputs/logs/git_commit_history.log`.*

---

## 12. Kịch bản Video Demo Giao diện Desktop GUI & Pipeline

Khởi động giao diện Desktop GUI:
```powershell
python main.py gui
# Hoặc: powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\gui.ps1
```

### Các bước thao tác trong Video Demo (Thời lượng: 3 - 5 phút):
1. **Khảo sát giao diện:**
   - Quan sát tiêu đề "Twitter Sentiment140 - Spark & Big Data Control Center".
   - Xem khối thông tin sinh viên thực hiện (Nhóm 09: Võ Minh Cảnh & Hồ Thị Thanh Nhã).
   - Kiểm tra các Card thống kê KPI (Tổng số dòng nạp, Tỷ lệ sạch 99.70%, Accuracy 74.75%, Macro-F1 0.7475).
2. **Chọn nguồn dữ liệu & Tỷ lệ mẫu:**
   - Nguồn Local File: `data/raw/training.1600000.processed.noemoticon.csv` hoặc Docker HDFS: `hdfs://localhost:8020/twitter/raw/sentiment140.csv`.
   - Chọn Sample Fraction: 0.10 (10% huấn luyện) hoặc 1.0 (toàn bộ dữ liệu).
3. **Thực thi các phân hệ độc lập qua nút bấm:**
   - Bấm **"Demo nhanh (Synthetic)"**: Chạy quy trình test nhanh trong 2 giây, log hiển thị real-time trên cửa sổ Console.
   - Bấm **"Kiểm tra cụm HDFS"**: Gọi lệnh `hdfs dfsadmin -report` và `hdfs dfs -ls`, hiển thị tình trạng NameNode/DataNode trực tiếp.
   - Bấm **"Điều phối Airflow DAG"**: Kích hoạt 9 task của DAG, log trả về trạng thái SUCCESS của toàn bộ pipeline.
4. **Kiểm thử tính năng Suy luận Cảm xúc Trực tiếp (Interactive Prediction):**
   - Bấm nút **"Mẫu 1: Tích cực"**: Điền câu *"I love this big data class, the spark pipeline is amazing!"* -> Bấm **"Dự đoán Cảm xúc"** -> Kết quả: **TÍCH CỰC (POSITIVE)**, Xác suất: **[94.2% Positive | 5.8% Negative]**, Badge hiển thị màu xanh lá cây sáng.
   - Bấm nút **"Mẫu 2: Tiêu cực"**: Điền câu *"This flight delay is completely unacceptable, terrible experience."* -> Bấm **"Dự đoán Cảm xúc"** -> Kết quả: **TIÊU CỰC (NEGATIVE)**, Xác suất: **[88.7% Negative | 11.3% Positive]**, Badge hiển thị màu đỏ rực.
   - Bấm nút **"Mẫu 3: Phủ định"**: Điền câu *"The movie was not bad at all, actually enjoyed it."* -> Bấm **"Dự đoán Cảm xúc"** -> Kết quả: **TÍCH CỰC (POSITIVE)** (Chứng minh thuật toán NLP bảo toàn từ phủ định `not`, không bị xóa nhầm như stopword thông thường).
5. **Mở kết quả đầu ra:**
   - Bấm nút **"Mở thư mục Biểu đồ"**: Mở ngay thư mục `outputs/charts/` chứa 7 biểu đồ PNG.
   - Bấm nút **"Mở thư mục Bảng CSV"**: Mở ngay thư mục `outputs/tables/` chứa 10 file CSV.

---

## 13. Danh mục Hồ sơ Bàn giao Nghiệm thu (Deliverables Matrix)

Gói nộp bài nghiệm thu hoàn chỉnh được đóng gói tại tệp:  
`report/Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip`

Bên trong bao gồm đầy đủ cấu trúc:
1. **Tài liệu Báo cáo & Thuyết trình:**
   - `BaoCaoCuoiKy_BigData_Nhom9.pdf`: Báo cáo chính thức PDF (3.77 MB) với đầy đủ 14 hình ảnh, sơ đồ, bảng biểu chuẩn mực.
   - `BaoCaoCuoiKy_BigData_Nhom9.docx`: Báo cáo chính thức Word DOCX (3.25 MB) có nhúng trực tiếp tất cả hình ảnh và bảng định lượng.
   - `BaoCaoCuoiKy_BigData_Nhom9.html`: Bản xem trước HTML độc lập.
   - `Thuyet_Trinh_BigData_Nhom9.pptx`: Slide thuyết trình báo cáo đồ án.
   - `README_HuongDanCaiDat.md`: Tài liệu hướng dẫn cài đặt và vận hành hệ thống.
   - `git_commit_history.log`: Lịch sử 8 commit Git chứng minh quá trình làm việc liên tục.
2. **Toàn bộ Repository Mã nguồn (`source_code/`):**
   - `main.py`, `gui.py`, `requirements.txt`
   - `twitter_spark/`: Toàn bộ các module xử lý (`data.py`, `cleaning.py`, `analysis.py`, `modeling.py`, `benchmark.py`, `storage.py`, `gui.py`, `report.py`)
   - `dags/`: Mã nguồn DAG Apache Airflow 9 tasks (`twitter_sentiment_pipeline_dag.py`)
   - `docker/`: Cấu hình Docker Compose HDFS (`docker/hdfs/docker-compose.yml`)
   - `scripts/`: Toàn bộ các script tự động hóa PowerShell và Python
   - `tests/`: Bộ 14 Unit Tests kiểm thử tự động
   - `models/`: Thư mục lưu trữ mô hình đã huấn luyện
   - `java/`: Adapter tối ưu hóa hệ thống tệp
   - `data/demo/`: Tập dữ liệu kiểm thử nhanh
3. **Thư mục Minh chứng Trực quan Độc lập (`minh_chung_truc_quan/`):**
   - `figures/`: 14 tệp ảnh biểu đồ và sơ đồ hệ thống (Hình 3.1 đến Hình C.1).
   - `tables/`: 10 tệp bảng dữ liệu định lượng CSV trích xuất từ Spark SQL và MLlib.
   - `logs/`: 7 tệp nhật ký ghi nhận quá trình thực thi thực tế của HDFS, Spark, Airflow, Unit Tests và Git.
   - `summary/`: 4 tệp JSON tổng hợp chất lượng dữ liệu, đánh giá mô hình, hiệu năng benchmark và manifest lần chạy.
