# BÁO CÁO ĐỒ ÁN GIAI ĐOẠN 1

## Phân tích hành vi đăng bài và cảm xúc của người dùng trên Twitter bằng Apache Spark

**Học phần:** Nhập môn Big Data  
**Giảng viên:** ........................................................  
**Nhóm thực hiện:** ....................................................  
**Lớp:** ...............................................................  

---

## 1. Giới thiệu đề tài

Twitter tạo ra lượng lớn dữ liệu văn bản trong thời gian ngắn. Việc xử lý các bài đăng bằng
công cụ truyền thống có thể gặp khó khăn khi dữ liệu tăng về số lượng và cần thực hiện nhiều
phép tổng hợp. Vì vậy, nhóm lựa chọn Apache Spark để xây dựng quy trình đọc, làm sạch, lưu
trữ, phân tích và huấn luyện mô hình phân loại cảm xúc trên dữ liệu Twitter.

Mục tiêu của đề tài là:

1. Sử dụng Apache Spark để xử lý dữ liệu Twitter theo phương pháp xử lý theo lô.
2. Thống kê số bài đăng theo ngày, giờ UTC và số bài trên mỗi tài khoản trong mẫu.
3. So sánh nội dung thường xuất hiện trong hai nhóm cảm xúc.
4. Xây dựng mô hình phân loại cảm xúc tích cực hoặc tiêu cực từ văn bản tiếng Anh.
5. Đánh giá mô hình và khảo sát thời gian xử lý khi quy mô dữ liệu thay đổi.

Các câu hỏi nghiên cứu chính gồm:

- Số bài đăng trong mẫu thay đổi như thế nào theo ngày và giờ?
- Mức độ xuất hiện của các tài khoản trong mẫu ra sao?
- Từ ngữ phổ biến của hai nhóm cảm xúc khác nhau như thế nào?
- Mô hình phân loại đạt chất lượng bao nhiêu theo Accuracy, Precision, Recall và Macro-F1?
- Thời gian xử lý thay đổi như thế nào khi tăng số dòng dữ liệu?

Đề tài chỉ nghiên cứu các tweet tiếng Anh có trong tập Sentiment140. Kết quả thống kê phản ánh
tập dữ liệu được phân tích, không đại diện cho toàn bộ người dùng Twitter và không được dùng
để suy luận tuổi, giới tính, quốc gia hay trạng thái tâm lý của người viết.

## 2. Cơ sở lý thuyết

### 2.1. Dữ liệu lớn và Apache Spark

Dữ liệu của đề tài thể hiện một số đặc trưng của Big Data: **Volume** là số lượng lớn bài
đăng; **Variety** là sự kết hợp giữa văn bản và các thuộc tính như thời gian, tài khoản;
**Veracity** là vấn đề nhiễu, trùng lặp và nhãn tự động; **Value** là thông tin thu được từ
phân tích và dự đoán. Velocity là đặc trưng của nền tảng Twitter, nhưng chương trình trong đề
tài xử lý dữ liệu lịch sử theo lô.

Apache Spark hỗ trợ xử lý dữ liệu song song thông qua DataFrame, Spark SQL và MLlib. Trong
phạm vi đồ án, chương trình chạy bằng chế độ `local[2]`, tức sử dụng hai luồng trên một máy;
đây không phải là một cluster xử lý nhiều máy. Nhóm bổ sung HDFS chạy bằng Docker gồm một
NameNode và một DataNode để minh họa lưu trữ phân tán. Spark sử dụng cơ chế đánh giá lười:
các phép biến đổi chỉ tạo kế hoạch, còn thao tác như `count`, `collect` hoặc ghi Parquet mới
kích hoạt xử lý.

### 2.2. Lưu trữ và xử lý văn bản

CSV được sử dụng làm dữ liệu đầu vào vì dễ trao đổi, nhưng không lưu kiểu dữ liệu và đọc kém
hiệu quả hơn khi cần truy vấn nhiều lần. CSV gốc có thể được đọc từ ổ đĩa local hoặc HDFS.
Sau khi làm sạch, dữ liệu được lưu dưới dạng Parquet trên cùng lớp lưu trữ đã chọn. Parquet là
định dạng lưu trữ theo cột, giữ được schema và phù hợp với DataFrame/Spark SQL.

Văn bản được chuyển thành chữ thường, loại URL, tên tài khoản được nhắc đến và chuẩn hóa
khoảng trắng. Các từ phủ định như `not`, `no`, `never` được giữ lại vì có ý nghĩa đối với cảm
xúc. Sau đó, văn bản được tách từ và biểu diễn thành vector bằng HashingTF kết hợp IDF.

### 2.3. Mô hình và chỉ số đánh giá

Mô hình chính là Logistic Regression; Naive Bayes được dùng để so sánh. Dữ liệu được chia
thành 70% train, 15% validation và 15% test theo hash của văn bản đã làm sạch. Train dùng để
học mô hình, validation dùng để chọn cấu hình và test chỉ dùng cho đánh giá cuối cùng.

Các chỉ số dự kiến gồm Accuracy, Precision, Recall, F1 của từng lớp, Macro-F1 và ma trận nhầm
lẫn. Macro-F1 được tính bằng trung bình F1 của hai lớp, không đồng nhất với Weighted-F1 của
Spark. Ngoài ra, nhóm sử dụng mô hình luôn dự đoán lớp phổ biến làm baseline để so sánh.

## 3. Dữ liệu và phương pháp đề xuất

### 3.1. Tập dữ liệu

Đề tài sử dụng tập Sentiment140, gồm khoảng 1,6 triệu tweet tiếng Anh. Tập huấn luyện không
có dòng tiêu đề và gồm sáu trường:

| Trường | Ý nghĩa |
|---|---|
| `target` | Nhãn gốc: 0 là tiêu cực, 4 là tích cực |
| `id` | Mã tweet |
| `date` | Thời gian đăng |
| `flag` | Trường truy vấn của dữ liệu |
| `user` | Tên tài khoản |
| `text` | Nội dung tweet |

Nhãn của Sentiment140 được tạo tự động dựa trên emoticon nên có thể chứa nhiễu. Tập huấn
luyện không có lớp trung lập. Khi huấn luyện, chương trình chuyển nhãn 0 thành 0.0 và nhãn 4
thành 1.0.

### 3.2. Quy trình thực hiện

Quy trình đề xuất gồm các bước:

1. Đọc CSV từ local hoặc HDFS theo schema cố định và mã hóa ISO-8859-1.
2. Kiểm tra số dòng, phân bố nhãn, giá trị thiếu, ID trùng, văn bản rỗng và lỗi thời gian.
3. Loại ID trùng cho dữ liệu phân tích; tạo `clean_text` và chuyển thời gian về UTC.
4. Lưu dữ liệu sạch dưới dạng Parquet trên local/HDFS và đăng ký temporary view `tweets`.
5. Dùng DataFrame/Spark SQL để tổng hợp theo ngày, giờ, tài khoản, nhãn và từ phổ biến.
6. Với dữ liệu học máy, loại các nhóm `clean_text` có nhãn mâu thuẫn và chỉ giữ một bản ghi
   cho mỗi văn bản chuẩn hóa để tránh rò rỉ.
7. Chia train/validation/test, huấn luyện mô hình và đánh giá trên tập test.
8. Đo một phép tổng hợp tại các quy mô khoảng 100.000, 500.000 và toàn bộ dữ liệu; mỗi mức
   chạy ba lần và báo cáo trung vị cho trường hợp có cache và không cache.

Kiến trúc xử lý có thể mô tả ngắn gọn như sau:

```text
Sentiment140 CSV trên máy
       |
       +----> Spark đọc trực tiếp
       |
       +----> HDFS (NameNode + DataNode)
                         |
                         v
Spark DataFrame -> kiểm tra/làm sạch -> Parquet local/HDFS
                                             |
                          +------------------+------------------+
                          v                                     v
                 Spark SQL + biểu đồ            TF-IDF -> mô hình -> đánh giá
```

## 4. Kế hoạch triển khai

Môi trường dự kiến gồm Python 3.11, Java 17, PySpark 3.5.7, matplotlib và Docker Desktop.
Docker Compose dùng để khởi tạo một NameNode và một DataNode. Chương trình được tổ chức
thành mã nguồn xử lý dữ liệu, phân tích, mô hình, đánh giá, benchmark và các script
PowerShell để cài đặt, kiểm thử, chạy HDFS và demo.

| Thời gian | Công việc | Sản phẩm |
|---|---|---|
| Tuần 1 | Tìm hiểu lý thuyết, tải và kiểm tra dữ liệu | Báo cáo giai đoạn 1, schema dữ liệu |
| Tuần 2 | Làm sạch, lưu Parquet, Spark SQL | Nhật ký chất lượng, bảng và biểu đồ |
| Tuần 3 | Huấn luyện, đánh giá, benchmark | Mô hình, chỉ số, ma trận nhầm lẫn |
| Tuần 4 | Hoàn thiện báo cáo và demo | Báo cáo cuối kỳ, slide, mã nguồn |

Nhóm gồm hai thành viên, phân công đề xuất như sau:

- Thành viên 1: chuẩn bị dữ liệu, Hadoop/HDFS, schema, kiểm tra chất lượng và Spark SQL.
- Thành viên 2: xử lý văn bản, xây dựng mô hình học máy, đánh giá và benchmark hiệu năng.
- Cả hai thành viên: trực quan hóa, tổng hợp báo cáo, kiểm thử chương trình và chuẩn bị demo.

Các rủi ro chính là thiếu RAM, lỗi tương thích Java/Python, Docker chưa khởi động, cổng HDFS
bị chiếm, dữ liệu bị sắp theo nhãn và thời gian không parse được. Biện pháp xử lý là kiểm tra
môi trường trước khi chạy, dùng mẫu có đủ hai lớp, giảm tỷ lệ mẫu hoặc số chiều đặc trưng khi
cần, cố định phiên bản môi trường và lưu nhật ký số dòng bị loại.

## 5. Yêu cầu môi trường, cài đặt và chạy chương trình

### 5.1. Yêu cầu môi trường

Chương trình có thể chạy cục bộ trên Windows 10/11, Linux hoặc macOS. Cấu hình khuyến nghị
cho máy Windows như sau:

| Thành phần | Yêu cầu |
|---|---|
| CPU | Tối thiểu 2 nhân; khuyến nghị 4 nhân trở lên |
| RAM | Tối thiểu 8 GB; khuyến nghị 16 GB khi xử lý toàn bộ dữ liệu |
| Ổ đĩa | Còn trống ít nhất 8 GB nếu chạy thêm HDFS bằng Docker |
| Python | Khuyến nghị Python 3.11, bản 64-bit |
| Java | JDK 17, bản 64-bit; cần có lệnh `java`, `javac` và `jar` |
| Apache Spark | PySpark 3.5.7 |
| Thư viện khác | matplotlib 3.7 trở lên và nhỏ hơn 4.0 |
| Docker | Docker Desktop có Docker Compose; chỉ bắt buộc khi demo HDFS |
| Terminal | PowerShell trên Windows hoặc terminal tương đương |

Chương trình mặc định chạy Spark ở chế độ `local[2]`, sử dụng hai luồng xử lý trên một máy.
Khi bật HDFS, Spark vẫn xử lý trên máy local nhưng đọc và ghi dữ liệu qua HDFS. Cụm HDFS
demo gồm một NameNode, một DataNode, hệ số sao chép 1 và block 128 MiB. Có thể kiểm tra môi
trường bằng các lệnh:

```powershell
python --version
java -version
javac -version
docker compose version
```

### 5.2. Chuẩn bị mã nguồn và môi trường Python

Mở PowerShell tại thư mục gốc của project, nơi có file `main.py`, sau đó chạy script cài đặt:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Script trên thực hiện các công việc sau:

1. Tạo môi trường Python riêng tại `.venv`.
2. Nâng cấp công cụ cài gói `pip`.
3. Cài PySpark 3.5.7, matplotlib và các thư viện phụ thuộc từ `requirements-dev.txt`.

Nếu máy có nhiều phiên bản Python và lệnh `python` không trỏ đến Python 3.11, chỉ định đường
dẫn Python khi chạy script:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 `
    -PythonCommand "C:\duong-dan\Python311\python.exe"
```

Sau khi cài đặt, có thể kiểm tra phiên bản PySpark bằng lệnh:

```powershell
.\.venv\Scripts\python.exe -c "import pyspark; print(pyspark.__version__)"
```

Chương trình có giao diện desktop để nhóm dễ thao tác khi demo. Khởi động bằng lệnh:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\gui.ps1
```

Giao diện cho phép chọn CSV, điều chỉnh tỷ lệ mẫu, chạy Spark local hoặc HDFS, theo dõi log
và mở các bảng, biểu đồ đầu ra. Các lệnh terminal vẫn được giữ để kiểm thử và xử lý sự cố.

### 5.3. Chuẩn bị dữ liệu Sentiment140

Tải dataset `kazanova/sentiment140` từ Kaggle và giải nén. Đặt file huấn luyện không có
header vào đúng đường dẫn:

```text
data/raw/training.1600000.processed.noemoticon.csv
```

Không mở rồi lưu lại file bằng Excel vì Excel có thể thay đổi mã tweet, mã hóa hoặc cấu trúc
CSV. Chương trình đọc file bằng mã hóa ISO-8859-1 và tự khai báo sáu cột `target`, `id`,
`date`, `flag`, `user`, `text`.

### 5.4. Chạy kiểm thử

Chạy toàn bộ unit test, Spark integration test và một smoke test đầu-cuối bằng lệnh:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Smoke test dùng dữ liệu tổng hợp và ghi kết quả riêng vào `.test-artifacts/`. Kết quả này chỉ
xác nhận chương trình hoạt động, không được sử dụng làm kết quả thực nghiệm trong báo cáo.

### 5.5. Chạy demo nhanh

Khi chưa tải Sentiment140, có thể chạy toàn bộ luồng bằng dữ liệu tổng hợp:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo.ps1
```

Lệnh demo thực hiện lần lượt: tạo dữ liệu mẫu, làm sạch, lưu Parquet, chạy Spark SQL, sinh
biểu đồ, huấn luyện Logistic Regression và Naive Bayes, đánh giá mô hình, lưu mô hình, đo
thời gian và dự đoán ba câu tiếng Anh. Nhóm có thể bấm **Demo nhanh** trên giao diện desktop
hoặc dùng lệnh PowerShell; biểu đồ và các bảng kết quả được mở từ thư mục `outputs/`.

### 5.6. Chạy với dữ liệu Sentiment140 thật

Sau khi đặt CSV đúng vị trí, chạy toàn bộ quy trình với mẫu phân tầng khoảng 10% cho phần học
máy bằng lệnh:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_full.ps1
```

Phần phân tích hành vi vẫn sử dụng toàn bộ dữ liệu sạch. Muốn huấn luyện mô hình trên toàn bộ
dữ liệu, truyền `SampleFraction` bằng 1.0:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_full.ps1 `
    -SampleFraction 1.0
```

Nếu muốn trình bày từng bước trong buổi demo, có thể chạy riêng các lệnh sau:

```powershell
# Kiểm tra, làm sạch và lưu Parquet
.\.venv\Scripts\python.exe main.py prepare `
    --data data/raw/training.1600000.processed.noemoticon.csv

# Truy vấn Spark SQL và tạo biểu đồ
.\.venv\Scripts\python.exe main.py analyze

# Huấn luyện, validation, đánh giá test và lưu mô hình
.\.venv\Scripts\python.exe main.py train --sample-fraction 0.10

# Dự đoán các câu tiếng Anh mới bằng mô hình đã lưu
.\.venv\Scripts\python.exe main.py predict `
    --text "I really enjoyed this day." `
    --text "This experience was awful." `
    --text "The movie was not good."

# Đo phép tổng hợp ở ba quy mô, mỗi mức chạy ba lần
.\.venv\Scripts\python.exe main.py benchmark `
    --sizes 100000 500000 --repetitions 3
```

### 5.7. Chạy với Hadoop/HDFS qua Docker

Khởi động NameNode và DataNode, sau đó chép file Sentiment140 từ máy lên HDFS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_start.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_upload.ps1
```

Chạy toàn bộ pipeline với CSV đầu vào và Parquet đầu ra đều nằm trên HDFS:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_run.ps1
```

Có thể thực hiện cả ba bước trên bằng một lệnh:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_all.ps1
```

Các đường dẫn sử dụng trong HDFS là:

- CSV: `hdfs://localhost:8020/twitter/raw/sentiment140.csv`.
- Parquet: `hdfs://localhost:8020/twitter/processed/tweets`.
- Giao diện NameNode: `http://localhost:9870`.
- Giao diện DataNode: `http://localhost:9864`.

Kiểm tra trạng thái hoặc dừng HDFS bằng các lệnh:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_status.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_stop.ps1
```

Lệnh dừng không xóa hai Docker volume nên dữ liệu HDFS vẫn được giữ lại.

### 5.8. Kết quả đầu ra

Sau khi chạy thành công, các sản phẩm chính gồm:

| Đường dẫn | Nội dung |
|---|---|
| `data/processed/tweets/` | Dữ liệu Parquet khi chạy chế độ local |
| `hdfs://localhost:8020/twitter/processed/tweets` | Dữ liệu Parquet khi chạy chế độ HDFS |
| `models/sentiment_lr/` | Pipeline Logistic Regression đã huấn luyện |
| `outputs/data_quality.json` | Số dòng, nhãn, null, ID trùng và lỗi thời gian |
| `outputs/evaluation.json` | Validation, chỉ số test và ma trận nhầm lẫn |
| `outputs/performance.json` | Thời gian các lần chạy và trung vị |
| `outputs/tables/` | Các bảng tổng hợp ở định dạng CSV |
| `outputs/charts/` | Biểu đồ PNG dùng cho báo cáo và demo |
| `outputs/run_manifest.json` | Phiên bản Python, Java, Spark và cấu hình lần chạy |

### 5.9. Một số lỗi thường gặp

- **Không tìm thấy CSV:** kiểm tra tên và đường dẫn file trong `data/raw/`.
- **Java gateway lỗi:** kiểm tra `java -version`, `javac -version` và bảo đảm đang dùng JDK 17.
- **PowerShell chặn script:** chạy bằng `-ExecutionPolicy Bypass` như các lệnh phía trên.
- **Không kết nối được Docker:** mở Docker Desktop và chờ Docker Engine khởi động xong.
- **Không mở được HDFS:** kiểm tra các cổng `8020`, `9870`, `9864`, `9866` có bị chiếm và
  chạy `hdfs_status.ps1` để xem báo cáo NameNode/DataNode.
- **Docker báo `unexpected EOF` khi tải image:** kiểm tra kết nối mạng rồi chạy lại
  `hdfs_start.ps1`; Docker sẽ tiếp tục dùng các lớp đã lưu trong bộ nhớ đệm.
- **Chỉ có một nhãn trong tập chia:** tăng `SampleFraction` hoặc kiểm tra lại file dữ liệu.
- **Thiếu bộ nhớ:** giảm `SampleFraction`, giảm số chiều HashingTF hoặc đóng ứng dụng khác.
- **Cảnh báo thiếu `winutils.exe`:** khi chạy cục bộ trên Windows, project tự biên dịch adapter
  local-filesystem để bỏ thao tác quyền POSIX không có trên NTFS. Cảnh báo này không làm hỏng
  pipeline nếu lệnh kết thúc thành công và các file đầu ra đã được tạo.

## 6. Kết luận giai đoạn 1

Giai đoạn 1 đã xác định được mục tiêu, phạm vi, dữ liệu, cơ sở lý thuyết và quy trình triển khai
đề tài. Giai đoạn tiếp theo sẽ chạy chương trình trên Sentiment140 thật, thu thập số liệu, biểu
đồ và chỉ số mô hình để trả lời các câu hỏi nghiên cứu. Mọi kết quả trong báo cáo cuối kỳ phải
lấy từ lần chạy thực tế; dữ liệu tổng hợp chỉ được sử dụng để kiểm tra kỹ thuật và demo luồng
chương trình. Cấu hình HDFS một DataNode và hệ số sao chép 1 chỉ phù hợp cho học tập, không có
khả năng chịu lỗi như cụm Hadoop nhiều máy trong thực tế.

## Tài liệu tham khảo

1. Đề cương học phần *Nhập môn Big Data*, mã học phần 0101101971.
2. Kaggle, *Sentiment140 dataset with 1.6 million tweets*: https://www.kaggle.com/datasets/kazanova/sentiment140
3. Stanford NLP, *Sentiment140 Dataset Card*: https://huggingface.co/datasets/stanfordnlp/sentiment140
4. Apache Spark, *Spark 3.5.7 Documentation*: https://spark.apache.org/docs/3.5.7/
5. Apache Spark, *ML Feature Extractors, Transformers and Selectors*: https://spark.apache.org/docs/3.5.7/ml-features.html
6. Apache Hadoop, *Official Hadoop Docker Image*: https://hub.docker.com/r/apache/hadoop
