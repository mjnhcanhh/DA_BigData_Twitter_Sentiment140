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

### Ghi chú riêng cho Windows (Winutils & Hadoop)
Nếu không có `HADOOP_HOME/winutils.exe`, project đã tích hợp sẵn nhị phân Hadoop 3.3.6 tại `.spark-support/winutils/` và adapter local-filesystem từ `java/twitter_spark/NoPermissionLocalFileSystem.java`. Script `.\scripts\setup.ps1` sẽ tự động cấu hình đường dẫn và biến môi trường.

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

---

## 8. Lịch sử Commit Git (Git Commit History)

Dự án được quản lý phiên bản nghiêm ngặt bằng Git với các commit phân bố đều đặn qua các tuần thực hiện:

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
| `572cfb0` | 2026-10-19 | Nhóm 09 | `feat: hoan thien toan dien ho so nghiem thu, bao cao pdf 35 trang, video demo va minh chung thuc nghiem` |

*Chi tiết toàn bộ diff và log commit xem tại file: `outputs/logs/git_commit_history.log`.*

---

## 9. Danh mục Hồ sơ Bàn giao Nghiệm thu (Deliverables Matrix)

Gói nộp bài nghiệm thu hoàn chỉnh được đóng gói tại tệp:  
`report/Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip`

Bên trong bao gồm đầy đủ cấu trúc:
1. **Tài liệu Báo cáo & Thuyết trình:**
   - `BaoCaoCuoiKy_BigData_Nhom9.pdf`: Báo cáo chính thức PDF (4.14 MB) với đầy đủ 14 hình ảnh, sơ đồ, 10 bảng số liệu và 8 log thực tế chuẩn mực.
   - `BaoCaoCuoiKy_BigData_Nhom9.docx`: Báo cáo chính thức Word DOCX (3.25 MB) có nhúng trực tiếp tất cả hình ảnh và bảng định lượng.
   - `BaoCaoCuoiKy_BigData_Nhom9.html`: Bản xem trước HTML độc lập.
   - `ThuyetTrinh_BigData_Nhom9.pptx`: Slide thuyết trình báo cáo đồ án.
   - `README_HuongDanCaiDat.md`: Tài liệu hướng dẫn cài đặt và vận hành hệ thống.
   - `git_commit_history.log`: Lịch sử commit Git chứng minh quá trình làm việc liên tục.
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
3. **Thư mục Minh chứng Trực quan & Video Demo (`outputs/`):**
   - `video_demo/`: Tệp video MP4 demo vận hành (`video_demo_gui_pipeline.mp4`) kèm kịch bản chi tiết (`README_VideoDemo.md`).
   - `figures/`: 14 tệp ảnh biểu đồ và sơ đồ hệ thống (Hình 3.1 đến Hình C.1).
   - `tables/`: 10 tệp bảng dữ liệu định lượng CSV trích xuất từ Spark SQL và MLlib.
   - `logs/`: 8 tệp nhật ký ghi nhận quá trình thực thi thực tế của HDFS, Spark, Airflow, Unit Tests, Git và Bảng theo dõi lỗi (`bang_loi_va_su_co.log`).
   - `summary/`: 4 tệp JSON tổng hợp chất lượng dữ liệu, đánh giá mô hình, hiệu năng benchmark và manifest lần chạy.
