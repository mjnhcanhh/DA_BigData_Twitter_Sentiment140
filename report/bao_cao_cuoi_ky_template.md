# BÁO CÁO ĐỒ ÁN MÔN NHẬP MÔN BIG DATA

## PHÂN TÍCH HÀNH VI ĐĂNG BÀI VÀ CẢM XÚC CỦA NGƯỜI DÙNG TRÊN TWITTER BẰNG APACHE SPARK

**Trường:** [Điền tên trường]  
**Khoa/Bộ môn:** [Điền khoa hoặc bộ môn]  
**Học phần:** Nhập môn Big Data  
**Giảng viên:** [Điền họ tên giảng viên]  
**Lớp học phần:** [Điền lớp học phần]  
**Nhóm:** [Điền tên/số nhóm]  

| Thành viên | Mã sinh viên | Nhiệm vụ chính |
|---|---|---|
| [Thành viên 1] | [MSSV 1] | Dữ liệu, Hadoop/HDFS, kiểm tra chất lượng, Spark SQL |
| [Thành viên 2] | [MSSV 2] | Xử lý văn bản, mô hình, đánh giá, benchmark, giao diện |

**Ngày hoàn thành:** 17/09/2026  
**Địa điểm:** [Điền địa điểm]

---

## TÓM TẮT

Đồ án xây dựng một quy trình Big Data để phân tích dữ liệu Twitter lịch sử và phân loại cảm
xúc bằng Apache Spark. Dữ liệu đầu vào là Sentiment140, gồm các tweet tiếng Anh được gán
nhãn tự động dựa trên emoticon. Hệ thống đọc CSV theo schema cố định, kiểm tra chất lượng,
làm sạch văn bản, chuẩn hóa thời gian UTC và lưu dữ liệu ở định dạng Parquet. Spark SQL và
DataFrame được sử dụng để thống kê số bài theo ngày, giờ, tài khoản và nhóm cảm xúc. Phần
học máy sử dụng RegexTokenizer, HashingTF, IDF và Logistic Regression; Naive Bayes và mô
hình dự đoán lớp phổ biến được dùng làm đối chứng.

Quy trình được triển khai ở chế độ `local[2]` và hỗ trợ lưu trữ HDFS bằng Docker với một
NameNode, một DataNode. Chương trình có giao diện desktop để chọn dữ liệu, chạy local/HDFS,
theo dõi nhật ký và mở kết quả. Trên lần chạy Sentiment140 thật, hệ thống xử lý
**{{RAW_ROWS}}** dòng đầu vào, giữ lại **{{CLEAN_ROWS}}** dòng hợp lệ. Logistic Regression
đạt Accuracy **{{LR_ACCURACY}}** và Macro-F1 **{{LR_MACRO_F1}}** trên tập test. Kết quả
chỉ mô tả tập dữ liệu lịch sử được phân tích, không đại diện cho toàn bộ người dùng Twitter
hoặc cảm xúc hiện tại.

**Từ khóa:** Big Data, Apache Spark, Spark SQL, MLlib, Sentiment140, phân tích cảm xúc,
TF-IDF, Logistic Regression, HDFS.

---

## MỤC LỤC

1. [Tổng quan đề tài](#chương-1-tổng-quan-đề-tài)
2. [Cơ sở lý thuyết](#chương-2-cơ-sở-lý-thuyết)
3. [Dữ liệu và thiết kế hệ thống](#chương-3-dữ-liệu-và-thiết-kế-hệ-thống)
4. [Cài đặt và thiết kế thực nghiệm](#chương-4-cài-đặt-và-thiết-kế-thực-nghiệm)
5. [Kết quả và đánh giá](#chương-5-kết-quả-và-đánh-giá)
6. [Kết luận và hướng phát triển](#chương-6-kết-luận-và-hướng-phát-triển)
7. [Tài liệu tham khảo](#tài-liệu-tham-khảo)
8. [Phụ lục](#phụ-lục)

## DANH MỤC HÌNH

- Hình 3.1. Kiến trúc tổng thể của hệ thống.
- Hình 5.1. Số bài đăng theo ngày.
- Hình 5.2. Số bài đăng theo giờ UTC.
- Hình 5.3. Phân bố số bài trên mỗi tài khoản.
- Hình 5.4. Từ xuất hiện phổ biến theo nhãn.
- Hình 5.5. Nhãn dữ liệu theo ngày.
- Hình 5.6. Ma trận nhầm lẫn của Logistic Regression.
- Hình 5.7. Thời gian tổng hợp theo quy mô dữ liệu.

## DANH MỤC BẢNG

- Bảng 1.1. Câu hỏi nghiên cứu và đầu ra.
- Bảng 3.1. Từ điển dữ liệu Sentiment140.
- Bảng 3.2. Quy tắc kiểm tra và làm sạch.
- Bảng 4.1. Cấu hình môi trường thực nghiệm.
- Bảng 4.2. Cấu hình mô hình và phép chia dữ liệu.
- Bảng 5.1. Kết quả kiểm tra chất lượng dữ liệu.
- Bảng 5.2. Phân bố train/validation/test.
- Bảng 5.3. Kết quả so sánh mô hình.
- Bảng 5.4. Kết quả benchmark.

---

# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

## 1.1. Lý do chọn đề tài

Twitter là nền tảng tạo ra lượng lớn dữ liệu văn bản cùng với thông tin thời gian và tài khoản.
Khi số bản ghi tăng lên hàng triệu dòng, quy trình đọc, làm sạch, tổng hợp và huấn luyện mô
hình cần một công cụ có khả năng xử lý song song. Apache Spark phù hợp với bài toán vì cung
cấp chung một hệ sinh thái cho DataFrame, Spark SQL, xử lý dữ liệu phân tán và học máy.

Phân tích cảm xúc từ tweet là bài toán có tính ứng dụng trong theo dõi phản hồi, khảo sát xu
hướng nội dung và hỗ trợ phân loại văn bản. Tuy nhiên, nhãn của Sentiment140 được tạo tự
động từ emoticon nên có thể nhiễu. Vì vậy, đồ án không chỉ xây dựng mô hình mà còn chú trọng
kiểm tra chất lượng dữ liệu, tránh rò rỉ giữa các tập và diễn giải giới hạn của kết quả.

## 1.2. Phát biểu bài toán

Đồ án xây dựng một hệ thống sử dụng Apache Spark để:

1. Tiếp nhận và kiểm tra dữ liệu Sentiment140.
2. Làm sạch tweet, chuẩn hóa thời gian và lưu Parquet.
3. Phân tích hành vi đăng bài trong phạm vi tập dữ liệu.
4. Huấn luyện mô hình phân loại cảm xúc tiêu cực hoặc tích cực.
5. Đánh giá mô hình và khảo sát thời gian xử lý ở nhiều quy mô.
6. Cung cấp giao diện để chạy demo local hoặc HDFS.

Trong đề tài, “hành vi” chỉ gồm số bài đăng, phân bố theo thời gian và số bài trên mỗi tài
khoản xuất hiện trong mẫu. “Cảm xúc” là sắc thái của nội dung văn bản theo hai nhãn có sẵn,
không đồng nghĩa với tâm trạng hoặc đặc điểm tâm lý của người viết.

## 1.3. Mục tiêu

- Xây dựng pipeline có thể tái lập từ CSV đến bảng, biểu đồ và mô hình.
- Sử dụng DataFrame và Spark SQL thay cho xử lý toàn bộ dữ liệu bằng Python thuần.
- Lưu dữ liệu sạch bằng Parquet và hỗ trợ đường dẫn HDFS.
- Xây dựng pipeline TF-IDF kết hợp Logistic Regression.
- So sánh với baseline lớp phổ biến và Naive Bayes.
- Đánh giá bằng Accuracy, Precision, Recall, F1 từng lớp, Macro-F1 và ma trận nhầm lẫn.
- Xây dựng giao diện desktop phục vụ demo và theo dõi log.

## 1.4. Câu hỏi nghiên cứu

**Bảng 1.1. Câu hỏi nghiên cứu và đầu ra**

| Mã | Câu hỏi | Đầu ra dùng để trả lời |
|---|---|---|
| RQ1 | Số bài đăng trong mẫu thay đổi như thế nào theo ngày và giờ UTC? | Bảng và biểu đồ ngày/giờ |
| RQ2 | Mức độ xuất hiện của các tài khoản trong mẫu ra sao? | Số tài khoản và phân bố bài/tài khoản |
| RQ3 | Nội dung thường gặp của hai nhóm cảm xúc khác nhau như thế nào? | Top từ theo nhãn |
| RQ4 | Mô hình phân loại đạt chất lượng bao nhiêu? | Accuracy, Precision, Recall, F1, Macro-F1, ma trận nhầm lẫn |
| RQ5 | Thời gian xử lý thay đổi như thế nào khi quy mô dữ liệu tăng? | Benchmark 100 nghìn, 500 nghìn và toàn bộ dữ liệu |

## 1.5. Phạm vi và giới hạn

Đối tượng nghiên cứu là các tweet tiếng Anh và tài khoản xuất hiện trong tập Sentiment140.
Đồ án không có dữ liệu để kết luận về tuổi, giới tính, quốc gia, lượt thích, chia sẻ hoặc quan
hệ giữa người dùng. Tập huấn luyện chỉ có hai lớp tiêu cực và tích cực, không có lớp trung lập.

Dữ liệu được xử lý theo lô. Spark chạy `local[2]`, nghĩa là dùng hai luồng trên một máy chứ
không phải cluster Spark nhiều máy. HDFS Docker chỉ gồm một NameNode và một DataNode với
hệ số sao chép 1, phù hợp minh họa kiến trúc nhưng chưa có khả năng chịu lỗi như hệ thống
phân tán thực tế.

## 1.6. Đóng góp của đồ án

- Mã nguồn hoàn chỉnh từ chuẩn bị dữ liệu đến dự đoán câu mới.
- Nhật ký chất lượng dữ liệu dưới dạng JSON.
- Sáu bảng phân tích, bảy biểu đồ và truy vấn Spark SQL.
- Pipeline học máy có chia train/validation/test ổn định theo hash của văn bản.
- So sánh ba phương án dự đoán trên cùng tập test.
- Benchmark có ba lần đo và báo cáo trung vị cho trường hợp cache/không cache.
- Hỗ trợ local, HDFS và giao diện desktop.

---

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

## 2.1. Big Data và các đặc trưng

Dữ liệu lớn thường được mô tả qua các đặc trưng Volume, Velocity, Variety, Veracity và Value.
Trong đồ án:

- **Volume:** tập dữ liệu có khoảng 1,6 triệu tweet.
- **Velocity:** Twitter tạo nội dung liên tục, nhưng dữ liệu trong đồ án là dữ liệu lịch sử xử
  lý theo lô.
- **Variety:** mỗi bản ghi kết hợp số, chuỗi văn bản, thời gian và tài khoản.
- **Veracity:** nhãn tự động, văn bản nhiễu, ID trùng và thời gian lỗi làm giảm độ tin cậy.
- **Value:** dữ liệu được chuyển thành thống kê hành vi và mô hình phân loại cảm xúc.

## 2.2. Apache Spark

Apache Spark là nền tảng xử lý dữ liệu hỗ trợ chạy local hoặc trên cluster. Spark 3.5.7 hỗ trợ
Java 17 và Python 3.8 trở lên [4]. Đồ án sử dụng PySpark để điều khiển Spark từ Python.

### 2.2.1. DataFrame và Spark SQL

DataFrame là tập dữ liệu có các cột được đặt tên, tương tự bảng quan hệ nhưng được Spark tối
ưu hóa kế hoạch thực thi [5]. Đồ án đọc CSV thành DataFrame theo schema cố định, thực hiện
`filter`, `groupBy`, `join`, window function và đăng ký temporary view `tweets` để truy vấn
SQL.

### 2.2.2. Partition và xử lý song song

Partition là đơn vị chia dữ liệu để Spark phân phối cho các task. Ở chế độ `local[2]`, tối đa
hai task có thể chạy đồng thời trên hai luồng của máy local. Khi `groupBy`, Spark có thể cần
shuffle dữ liệu giữa các partition, làm tăng chi phí I/O và thời gian.

### 2.2.3. Lazy evaluation và cache

Các transformation như `select`, `filter` và `groupBy` chủ yếu tạo kế hoạch xử lý. Công việc
chỉ thực sự chạy khi gặp action như `count`, `collect` hoặc `write`. `cache()` giữ dữ liệu đã
tính trong bộ nhớ/đĩa để giảm việc tính lại. Benchmark của đồ án tách riêng trường hợp cache
và không cache, đồng thời đặt bước làm nóng cache ngoài khoảng đo.

## 2.3. HDFS

HDFS là hệ thống tệp phân tán của Hadoop, thiết kế cho dữ liệu lớn và truy cập thông lượng
cao. NameNode quản lý namespace và ánh xạ block; DataNode lưu block và phục vụ yêu cầu
đọc/ghi [8]. DataNode định kỳ gửi Heartbeat và Block Report cho NameNode.

Cấu hình demo dùng block 128 MiB, một NameNode, một DataNode và replication 1. HDFS chạy
trong Docker, còn Spark driver chạy trên Windows. CSV và Parquet có thể được truy cập qua URI
`hdfs://localhost:8020/...`. Do chỉ có một DataNode, cấu hình này minh họa luồng lưu trữ chứ
không chứng minh khả năng chịu lỗi.

## 2.4. CSV và Parquet

CSV phù hợp trao đổi dữ liệu nhưng không lưu schema và phải parse lại khi đọc. Parquet là định
dạng lưu trữ theo cột, giữ kiểu dữ liệu và hỗ trợ đọc chọn cột. Vì các phép phân tích thường
chỉ sử dụng một số cột, Parquet phù hợp làm tầng dữ liệu sạch để tái sử dụng.

## 2.5. Tiền xử lý văn bản

Chương trình thực hiện các bước:

1. Chuyển văn bản thành chữ thường.
2. Loại URL và tên tài khoản được nhắc đến.
3. Loại ký tự không phải chữ, số, dấu nháy đơn hoặc khoảng trắng.
4. Chuẩn hóa khoảng trắng.
5. Giữ các từ phủ định như `not`, `no`, `never` vì chúng ảnh hưởng đến cảm xúc.

Văn bản sạch được tách từ bằng RegexTokenizer. Quy tắc làm sạch của dữ liệu huấn luyện và
câu dự đoán mới là giống nhau để tránh sai lệch pipeline.

## 2.6. TF-IDF

Term Frequency (TF) biểu diễn số lần một từ xuất hiện trong văn bản. Inverse Document
Frequency (IDF) giảm trọng số của từ xuất hiện ở nhiều văn bản. Spark MLlib định nghĩa:

\[
IDF(t,D)=\log\frac{|D|+1}{DF(t,D)+1}
\]

\[
TFIDF(t,d,D)=TF(t,d)\times IDF(t,D)
\]

HashingTF ánh xạ từ vào vector có kích thước cố định mà không cần xây dựng từ điển toàn cục,
nhưng có khả năng va chạm hash [6]. Đồ án dùng 32.768 chiều, là lũy thừa của hai.

## 2.7. Mô hình phân loại

### 2.7.1. Logistic Regression

Logistic Regression ước lượng xác suất một mẫu thuộc lớp tích cực dựa trên tổ hợp tuyến tính
của các đặc trưng. Mô hình phù hợp với bài toán nhị phân và vector văn bản thưa. Hai giá trị
`regParam` 0,01 và 0,1 được thử trên tập validation; cấu hình có Macro-F1 cao hơn được chọn
trước khi đánh giá test.

### 2.7.2. Naive Bayes

Naive Bayes giả định các đặc trưng độc lập có điều kiện theo lớp. Tuy giả định đơn giản, mô
hình thường là đối chứng hữu ích cho dữ liệu đếm từ hoặc TF-IDF không âm.

### 2.7.3. Baseline lớp phổ biến

Baseline luôn dự đoán lớp xuất hiện nhiều nhất trong tập train. Mô hình học máy chỉ có ý nghĩa
khi cải thiện rõ ràng so với baseline này.

## 2.8. Chỉ số đánh giá

Với mỗi lớp, Precision, Recall và F1 được tính như sau:

\[
Precision=\frac{TP}{TP+FP},\quad
Recall=\frac{TP}{TP+FN},\quad
F1=\frac{2\times Precision\times Recall}{Precision+Recall}
\]

Accuracy là tỷ lệ dự đoán đúng trên toàn bộ mẫu. Macro-F1 là trung bình F1 của hai lớp và cho
hai lớp trọng số bằng nhau. Weighted-F1 lấy trung bình có trọng số theo số mẫu mỗi lớp, vì vậy
không được gọi nhầm là Macro-F1. Ma trận nhầm lẫn trong báo cáo có hàng là nhãn thật, cột là
nhãn dự đoán theo thứ tự `[negative, positive]`.

---

# CHƯƠNG 3. DỮ LIỆU VÀ THIẾT KẾ HỆ THỐNG

## 3.1. Nguồn dữ liệu

Đồ án sử dụng file huấn luyện Sentiment140 được phân phối trên Kaggle [3]. Công trình gốc của
Go, Bhayani và Huang sử dụng emoticon để gán nhãn từ xa cho tweet [2]. File CSV không có
header, sử dụng mã hóa ISO-8859-1 và có khoảng 1,6 triệu dòng. Tập huấn luyện không có lớp
trung lập; nhãn 0 biểu thị tiêu cực và nhãn 4 biểu thị tích cực.

## 3.2. Từ điển dữ liệu

**Bảng 3.1. Từ điển dữ liệu Sentiment140**

| Trường | Kiểu đọc | Ý nghĩa | Cách sử dụng |
|---|---|---|---|
| `target` | Integer | Nhãn gốc 0/4 | Đổi thành 0.0/1.0 |
| `id` | String | Mã tweet | Kiểm tra và loại ID trùng |
| `date` | String | Thời gian có múi giờ | Chuyển sang timestamp UTC |
| `flag` | String | Trường truy vấn | Giữ để đối chiếu, không dùng làm đặc trưng |
| `user` | String | Tên tài khoản | Thống kê trong phạm vi mẫu |
| `text` | String | Nội dung tweet | Làm sạch và tạo đặc trưng |

ID được đọc dưới dạng chuỗi để tránh mất chính xác. Chương trình giữ cả `text` gốc và
`clean_text` để có thể kiểm tra, giải thích hoặc truy vết bản ghi.

## 3.3. Kiến trúc tổng thể

**Hình 3.1. Kiến trúc tổng thể của hệ thống**

```text
Sentiment140 CSV trên máy
          |
          +-------------------+
          |                   |
          v                   v
     Đọc trực tiếp      HDFS qua Docker
                         NameNode + DataNode
          |                   |
          +---------+---------+
                    v
          Spark DataFrame local[2]
                    |
       kiểm tra -> làm sạch -> Parquet
                    |
          +---------+----------+
          |                    |
          v                    v
 Spark SQL + biểu đồ    TF-IDF + mô hình ML
          |                    |
          +---------+----------+
                    v
         JSON + CSV + PNG + mô hình
                    |
                    v
             Giao diện desktop
```

## 3.4. Kiểm tra và làm sạch dữ liệu

**Bảng 3.2. Quy tắc kiểm tra và làm sạch**

| Hạng mục | Cách xử lý |
|---|---|
| Schema | Khai báo đúng sáu cột thay vì suy luận tự động |
| Nhãn | Chỉ giữ `target` bằng 0 hoặc 4 |
| Giá trị thiếu | Đếm null theo từng cột; loại dòng thiếu ID/text cần thiết |
| ID trùng | Giữ một bản ghi trên mỗi ID trong dữ liệu phân tích |
| Văn bản rỗng | Loại sau khi tạo `clean_text` |
| Thời gian | Thay PDT/PST bằng offset, parse và lưu UTC |
| Ngày không hợp lệ | Đếm và loại khỏi thống kê thời gian; vẫn có thể dùng cho ML |
| Nhãn ML | Chuyển 0 thành 0.0, 4 thành 1.0 |

Toàn bộ số dòng bị loại được ghi vào `outputs/data_quality.json`, tránh việc âm thầm loại dữ
liệu mà không thể giải thích.

## 3.5. Tách dữ liệu phân tích và học máy

Dữ liệu phân tích loại ID trùng nhưng vẫn giữ các tweet khác ID dù nội dung giống nhau, vì
chúng có thể là các lần đăng khác nhau. Dữ liệu học máy được xử lý nghiêm ngặt hơn:

- Gom nhóm theo `clean_text`.
- Loại toàn bộ nhóm có cùng văn bản nhưng nhãn mâu thuẫn.
- Với nhóm chỉ có một nhãn, giữ một bản ghi đại diện.
- Lấy mẫu phân tầng 10% ở từng nhãn cho huấn luyện thực nghiệm.

Sau đó, `xxhash64(clean_text)` được chuyển thành bucket ổn định để chia 70% train, 15%
validation và 15% test. Cùng một `clean_text` không thể xuất hiện ở nhiều tập, nhờ đó giảm
nguy cơ rò rỉ dữ liệu.

## 3.6. Lưu trữ dữ liệu

CSV gốc được giữ nguyên trong `data/raw/`. Dữ liệu sạch được ghi vào
`data/processed/tweets/` dưới dạng nhiều part-file Parquet. Khi dùng HDFS, chương trình đọc
`hdfs://localhost:8020/twitter/raw/sentiment140.csv` và ghi
`hdfs://localhost:8020/twitter/processed/tweets`.

Temporary view `tweets` chỉ tồn tại trong một phiên Spark. Khi mở phiên mới, chương trình đọc
Parquet và đăng ký lại view trước khi chạy SQL.

---

# CHƯƠNG 4. CÀI ĐẶT VÀ THIẾT KẾ THỰC NGHIỆM

## 4.1. Cấu hình môi trường

**Bảng 4.1. Cấu hình môi trường thực nghiệm**

| Thành phần | Cấu hình thực tế |
|---|---|
| Hệ điều hành | Microsoft Windows 11 Home, 64-bit |
| CPU | AMD Ryzen 5 5500U, 6 nhân/12 luồng |
| RAM | 31,3 GB |
| Python | 3.10.0rc2, 64-bit |
| Java | Eclipse Temurin OpenJDK 17.0.19, 64-bit |
| PySpark | 3.5.7 |
| matplotlib | 3.10.9 |
| Spark master | `local[2]` |
| Shuffle partitions | 8 |
| HDFS Docker | Apache Hadoop 3.3.6; 1 NameNode + 1 DataNode |
| HDFS block/replication | 128 MiB / 1 |

Mặc dù tài liệu hướng dẫn khuyến nghị Python 3.11, lần thực nghiệm thực tế dùng Python
3.10.0rc2. Spark 3.5.7 hỗ trợ Python 3.8 trở lên [4]. Báo cáo ghi đúng môi trường đã chạy thay
vì thay thế bằng cấu hình dự kiến.

## 4.2. Tổ chức mã nguồn

| Tệp/thư mục | Vai trò |
|---|---|
| `main.py` | Điểm vào CLI |
| `twitter_spark/data.py` | Đọc, kiểm tra và làm sạch dữ liệu |
| `twitter_spark/analysis.py` | Spark SQL và các phép tổng hợp |
| `twitter_spark/modeling.py` | Lấy mẫu, chia tập, huấn luyện và dự đoán |
| `twitter_spark/evaluation.py` | Chỉ số và ma trận nhầm lẫn |
| `twitter_spark/benchmark.py` | Đo thời gian cache/không cache |
| `twitter_spark/charts.py` | Sinh biểu đồ PNG |
| `twitter_spark/gui.py` | Giao diện desktop và log tác vụ |
| `docker/hdfs/` | Docker Compose và cấu hình Hadoop |
| `scripts/` | Cài đặt, test, local, GUI và HDFS |
| `tests/` | Unit test và Spark integration test |

## 4.3. Giao diện chương trình

Giao diện được xây dựng bằng Tkinter và không cần cài thêm web framework. Người dùng có thể:

- Chọn file CSV và tỷ lệ mẫu.
- Cài môi trường, chạy test hoặc demo.
- Chạy toàn bộ pipeline local.
- Khởi động HDFS, upload CSV và chạy Spark với HDFS.
- Xem log theo thời gian thực và dừng tác vụ.
- Xem số dòng, Macro-F1 và mở thư mục bảng/biểu đồ.

Giao diện gọi lại các PowerShell script có sẵn nên CLI và GUI dùng cùng một pipeline, tránh
sai khác giữa thao tác demo và quy trình kiểm thử.

## 4.4. Cấu hình thí nghiệm mô hình

**Bảng 4.2. Cấu hình mô hình và phép chia dữ liệu**

| Hạng mục | Giá trị |
|---|---|
| Tỷ lệ mẫu ML | 0,10 ở từng lớp |
| Seed | 42 |
| Chia tập | 70% train, 15% validation, 15% test theo hash |
| Đặc trưng | RegexTokenizer -> HashingTF -> IDF |
| Số chiều HashingTF | 32.768 |
| Logistic Regression | `maxIter=30`; `regParam` thuộc {0,01; 0,1} |
| Mô hình so sánh | Naive Bayes |
| Baseline | Luôn dự đoán lớp phổ biến của train |
| Chỉ số chọn mô hình | Macro-F1 trên validation |
| Chỉ số test | Accuracy, Precision, Recall, F1, Macro-F1, Weighted-F1 |

IDF và classifier chỉ được fit trên train. Validation dùng để chọn `regParam`; test chỉ được
sử dụng sau khi khóa cấu hình.

## 4.5. Thiết kế benchmark

Benchmark sử dụng cùng phép tổng hợp số bài theo ngày ở ba mức dữ liệu: khoảng 100.000,
500.000 và toàn bộ dữ liệu sạch. Mỗi mức chạy ba lần cho hai chế độ:

- **Uncached:** phép tổng hợp được tính từ lineage chưa cache.
- **Cached:** DataFrame được cache và làm nóng trước khi bắt đầu đo.

Khoảng đo bắt đầu ngay trước action tổng hợp và kết thúc khi action hoàn thành. Việc đọc dữ
liệu và tạo mẫu không nằm trong thời gian báo cáo. Trung vị được dùng để giảm ảnh hưởng của
nhiễu giữa các lần chạy.

## 4.6. Kiểm thử

Bộ kiểm thử gồm kiểm tra dữ liệu demo, công thức chỉ số, làm sạch Spark, nhận diện URI HDFS,
xử lý đường dẫn Windows và helper của giao diện. Script `test.ps1` còn chạy một pipeline đầu
cuối cô lập trong `.test-artifacts/`. Kết quả kiểm thử gần nhất: **11/11 test đạt** và smoke
test Spark hoàn thành với mã thoát 0.

---

# CHƯƠNG 5. KẾT QUẢ VÀ ĐÁNH GIÁ

> Các giá trị `{{...}}` trong chương này được thay tự động bằng kết quả của lần chạy
> Sentiment140 thật. Không sử dụng số liệu demo tổng hợp để kết luận.

## 5.1. Chất lượng dữ liệu

**Bảng 5.1. Kết quả kiểm tra chất lượng dữ liệu**

| Chỉ tiêu | Kết quả |
|---|---:|
| Số dòng CSV đầu vào | {{RAW_ROWS}} |
| Số dòng sau làm sạch | {{CLEAN_ROWS}} |
| Số dòng bị loại | {{REMOVED_ROWS}} |
| Nhãn 0 trong dữ liệu gốc | {{RAW_NEGATIVE}} |
| Nhãn 4 trong dữ liệu gốc | {{RAW_POSITIVE}} |
| ID trùng bị loại | {{DUPLICATE_IDS}} |
| Văn bản rỗng | {{EMPTY_TEXT_ROWS}} |
| Nhãn không hợp lệ | {{INVALID_TARGET_ROWS}} |
| Thời gian không parse được | {{INVALID_DATE_ROWS}} |
| Tỷ lệ parse thời gian thành công | {{DATE_SUCCESS_RATE}} |
| Thời gian nhỏ nhất UTC | {{MIN_DATE}} |
| Thời gian lớn nhất UTC | {{MAX_DATE}} |

Dữ liệu sau làm sạch chiếm **{{CLEAN_RATE}}** số dòng đầu vào. Phân bố hai nhãn
**{{LABEL_BALANCE_COMMENT}}**. Các dòng thời gian lỗi không được dùng trong phân tích ngày
và giờ, nhưng vẫn có thể tham gia mô hình nếu văn bản và nhãn hợp lệ.

## 5.2. Kết quả phân tích hành vi đăng bài

### 5.2.1. RQ1 - Số bài theo ngày và giờ UTC

![Hình 5.1. Số bài đăng theo ngày](../outputs/charts/posts_by_day.png)

**Hình 5.1. Số bài đăng theo ngày trong tập dữ liệu đã xử lý.**

Dữ liệu có timestamp hợp lệ trải từ **{{MIN_DATE}}** đến **{{MAX_DATE}}**, tương ứng
**{{VALID_DAYS}}** ngày trong bảng biểu diễn. Ngày có nhiều bài nhất là **{{TOP_DAY}}** với
**{{TOP_DAY_POSTS}}** bài; ngày có ít bài nhất là **{{LOW_DAY}}** với
**{{LOW_DAY_POSTS}}** bài. Các khoảng bằng 0 được giữ trên trục ngày để tránh nối liền sai các
giai đoạn không có dữ liệu.

![Hình 5.2. Số bài đăng theo giờ UTC](../outputs/charts/posts_by_hour_utc.png)

**Hình 5.2. Phân bố số bài theo giờ UTC.**

Khung giờ xuất hiện nhiều bài nhất là **{{TOP_HOUR}} UTC** với **{{TOP_HOUR_POSTS}}** bài.
Khung giờ ít nhất là **{{LOW_HOUR}} UTC** với **{{LOW_HOUR_POSTS}}** bài. Đây là giờ UTC
được chuẩn hóa từ chuỗi thời gian của dataset, không phải giờ địa phương của người viết.

### 5.2.2. RQ2 - Mức độ xuất hiện của tài khoản

![Hình 5.3. Phân bố số bài trên mỗi tài khoản](../outputs/charts/posts_per_user.png)

**Hình 5.3. Phân bố số bài trên mỗi tài khoản trong mẫu.**

Tập dữ liệu sạch có **{{DISTINCT_ACCOUNTS}}** tài khoản phân biệt. Có
**{{ONE_POST_USERS}}** tài khoản chỉ xuất hiện một lần, chiếm **{{ONE_POST_USER_RATE}}** số
tài khoản. Nhóm từ 20 bài trở lên được gộp ở mốc 20 để biểu đồ không bị kéo dài bởi số ít tài
khoản xuất hiện nhiều lần. Kết quả phản ánh cấu trúc tập Sentiment140, không phải thống kê về
toàn bộ tài khoản Twitter.

### 5.2.3. RQ3 - Nội dung phổ biến theo nhãn

![Hình 5.4. Từ phổ biến theo nhãn](../outputs/charts/top_words_by_label.png)

**Hình 5.4. Top từ theo lượt xuất hiện trong hai nhóm nhãn.**

Các từ đứng đầu nhóm tiêu cực gồm **{{TOP_NEGATIVE_WORDS}}**; nhóm tích cực gồm
**{{TOP_POSITIVE_WORDS}}**. Một số từ có thể xuất hiện ở cả hai nhóm vì mô hình cảm xúc cần
xét ngữ cảnh và tổ hợp từ, không chỉ một token riêng lẻ. Danh sách này đếm lượt xuất hiện sau
khi lọc stopword chỉ dành cho biểu đồ; pipeline mô hình không áp dụng danh sách stopword đó.

![Hình 5.5. Nhãn dữ liệu theo ngày](../outputs/charts/label_by_day.png)

**Hình 5.5. Số bài của từng nhãn theo ngày.**

Hình 5.5 mô tả sự phân bố nhãn có sẵn của dataset theo thời gian. Tỷ lệ tích cực/tiêu cực ở
đây chịu ảnh hưởng trực tiếp từ cách xây dựng Sentiment140 và không được diễn giải thành mức
độ hài lòng của cộng đồng Twitter.

## 5.3. Dữ liệu học máy

Trước khi lấy mẫu, chương trình loại **{{CONFLICT_GROUPS}}** nhóm `clean_text` có nhãn mâu
thuẫn, tương ứng **{{CONFLICT_ROWS}}** dòng nguồn.

**Bảng 5.2. Phân bố train/validation/test**

| Tập | Tiêu cực | Tích cực | Tổng |
|---|---:|---:|---:|
| Train | {{TRAIN_NEGATIVE}} | {{TRAIN_POSITIVE}} | {{TRAIN_TOTAL}} |
| Validation | {{VALID_NEGATIVE}} | {{VALID_POSITIVE}} | {{VALID_TOTAL}} |
| Test | {{TEST_NEGATIVE}} | {{TEST_POSITIVE}} | {{TEST_TOTAL}} |

Cả ba tập đều có đủ hai lớp. Phép chia theo hash giúp kết quả ổn định giữa các lần chạy và
đảm bảo một nội dung chuẩn hóa không xuất hiện ở nhiều tập.

## 5.4. RQ4 - Kết quả mô hình

**Bảng 5.3. So sánh kết quả trên tập test**

| Phương pháp | Accuracy | Macro-F1 | Weighted-F1 | Thời gian fit (giây) |
|---|---:|---:|---:|---:|
| Baseline lớp phổ biến | {{BASELINE_ACCURACY}} | {{BASELINE_MACRO_F1}} | {{BASELINE_WEIGHTED_F1}} | - |
| TF-IDF + Logistic Regression | {{LR_ACCURACY}} | {{LR_MACRO_F1}} | {{LR_WEIGHTED_F1}} | {{LR_FIT_SECONDS}} |
| TF-IDF + Naive Bayes | {{NB_ACCURACY}} | {{NB_MACRO_F1}} | {{NB_WEIGHTED_F1}} | {{NB_FIT_SECONDS}} |

Trên validation, `regParam={{SELECTED_REG_PARAM}}` được chọn cho Logistic Regression với
Macro-F1 **{{BEST_VALIDATION_F1}}**. Trên test, Logistic Regression cải thiện
**{{LR_GAIN_OVER_BASELINE}}** điểm Macro-F1 so với baseline. **{{MODEL_COMPARISON_COMMENT}}**

### 5.4.1. Chỉ số từng lớp của Logistic Regression

| Lớp | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Tiêu cực (0) | {{LR_NEG_PRECISION}} | {{LR_NEG_RECALL}} | {{LR_NEG_F1}} | {{LR_NEG_SUPPORT}} |
| Tích cực (1) | {{LR_POS_PRECISION}} | {{LR_POS_RECALL}} | {{LR_POS_F1}} | {{LR_POS_SUPPORT}} |

![Hình 5.6. Ma trận nhầm lẫn](../outputs/charts/confusion_matrix.png)

**Hình 5.6. Ma trận nhầm lẫn của Logistic Regression; hàng là nhãn thật, cột là dự đoán.**

Ma trận gồm **{{TN}}** mẫu tiêu cực dự đoán đúng, **{{FP}}** mẫu tiêu cực bị dự đoán thành
tích cực, **{{FN}}** mẫu tích cực bị dự đoán thành tiêu cực và **{{TP}}** mẫu tích cực dự
đoán đúng. **{{CONFUSION_COMMENT}}**

### 5.4.2. Phân tích lỗi

Các ví dụ sai được lưu ở `outputs/tables/misclassified_examples.csv`. Lỗi thường có thể đến
từ câu quá ngắn, phủ định, tiếng lóng, mỉa mai hoặc nhãn tự động không phản ánh đúng nội dung.
Ba câu demo tự tạo cho thấy mô hình xử lý tốt các từ cảm xúc rõ ràng, nhưng câu “The movie was
not good.” có thể khó đối với mô hình bag-of-words vì TF-IDF không biểu diễn đầy đủ thứ tự và
quan hệ phủ định.

## 5.5. RQ5 - Kết quả benchmark

**Bảng 5.4. Thời gian tổng hợp theo ngày; mỗi ô là trung vị của ba lần chạy**

| Quy mô thực tế | Không cache (giây) | Có cache (giây) | Mức giảm |
|---:|---:|---:|---:|
| {{BENCH_ROWS_1}} | {{UNCACHED_1}} | {{CACHED_1}} | {{SPEEDUP_1}} |
| {{BENCH_ROWS_2}} | {{UNCACHED_2}} | {{CACHED_2}} | {{SPEEDUP_2}} |
| {{BENCH_ROWS_3}} | {{UNCACHED_3}} | {{CACHED_3}} | {{SPEEDUP_3}} |

![Hình 5.7. Benchmark](../outputs/charts/performance.png)

**Hình 5.7. Thời gian phép tổng hợp theo ngày ở các quy mô dữ liệu.**

Khi quy mô tăng từ **{{BENCH_ROWS_1}}** lên **{{BENCH_ROWS_3}}** dòng, trung vị không cache
thay đổi từ **{{UNCACHED_1}}** lên **{{UNCACHED_3}}** giây. Cache
**{{CACHE_CONCLUSION}}** trong phép đo này. Kết quả phụ thuộc cấu hình máy, trạng thái JVM,
I/O và dữ liệu; không được xem là benchmark chung cho mọi cụm Spark.

## 5.6. Trả lời câu hỏi nghiên cứu

- **RQ1:** {{RQ1_ANSWER}}
- **RQ2:** {{RQ2_ANSWER}}
- **RQ3:** {{RQ3_ANSWER}}
- **RQ4:** {{RQ4_ANSWER}}
- **RQ5:** {{RQ5_ANSWER}}

## 5.7. Đánh giá hệ thống

Hệ thống đã bao phủ toàn bộ vòng đời của một bài toán Big Data theo lô: tiếp nhận, kiểm tra,
làm sạch, lưu trữ, truy vấn, trực quan hóa, huấn luyện, đánh giá và demo. Việc dùng JSON/CSV
cho số liệu giúp các hình và nhận xét có thể truy vết. Mô hình được lưu cùng toàn bộ pipeline
tiền xử lý đặc trưng, nên câu mới không cần xây dựng vector thủ công.

Điểm hạn chế là Spark chỉ chạy trên một máy, mẫu ML mặc định là 10%, HDFS có một DataNode
và mô hình TF-IDF không hiểu đầy đủ trật tự từ. Ngoài ra, kết quả HDFS là phần minh họa lưu
trữ; các số liệu đo trong chương này được thực hiện ở chế độ local để bảo đảm điều kiện so sánh
nhất quán.

---

# CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 6.1. Kết luận

Đồ án đã xây dựng được pipeline phân tích Twitter bằng Apache Spark, từ CSV gốc đến dữ liệu
Parquet, bảng tổng hợp, biểu đồ và mô hình phân loại cảm xúc. Kết quả cho phép trả lời năm câu
hỏi nghiên cứu trong phạm vi Sentiment140. Logistic Regression đạt Macro-F1
**{{LR_MACRO_F1}}**, **{{LR_BASELINE_CONCLUSION}}** so với baseline lớp phổ biến. Benchmark
cho thấy **{{BENCHMARK_CONCLUSION}}**.

Quan trọng hơn, đồ án phân biệt rõ nhãn có sẵn và dự đoán của mô hình, loại nguy cơ rò rỉ theo
văn bản, dùng validation để chọn cấu hình và chỉ đánh giá test sau khi khóa mô hình. Đây là các
yếu tố cần thiết để kết quả có thể kiểm tra và tái lập.

## 6.2. Hạn chế

- Nhãn Sentiment140 được suy ra từ emoticon và có thể chứa nhiễu.
- Dataset là dữ liệu tiếng Anh lịch sử, không đại diện Twitter hiện tại.
- Tập train không có lớp trung lập.
- TF-IDF bỏ qua phần lớn thứ tự từ, ngữ cảnh, mỉa mai và nghĩa đa từ.
- Probability của Logistic Regression chưa được hiệu chỉnh.
- Spark `local[2]` chưa đánh giá khả năng scale-out trên nhiều máy.
- HDFS một DataNode với replication 1 không có khả năng chịu lỗi.
- Thời gian benchmark chịu ảnh hưởng của máy cá nhân và các tiến trình nền.

## 6.3. Hướng phát triển

1. Chạy Spark Standalone, YARN hoặc Kubernetes trên nhiều máy để đánh giá scale-out.
2. Mở rộng HDFS lên ít nhất ba DataNode và replication 3.
3. So sánh CountVectorizer, n-gram hoặc embedding với HashingTF.
4. Thử mô hình có khả năng nắm bắt ngữ cảnh như Transformer, với thiết kế tài nguyên phù hợp.
5. Bổ sung lớp trung lập bằng dataset được gán nhãn tương ứng.
6. Thêm hiệu chỉnh xác suất và phân tích fairness/bias của dữ liệu.
7. Chuyển pipeline batch thành Structured Streaming khi có nguồn dữ liệu hợp pháp.
8. Đóng gói ứng dụng thành dịch vụ có xác thực, giám sát và quản lý phiên bản mô hình.

---

# TÀI LIỆU THAM KHẢO

[1] *Hướng dẫn thực hiện đồ án - Nhập môn Big Data: Phân tích hành vi đăng bài và cảm xúc
của người dùng trên Twitter bằng Apache Spark*, tài liệu môn học do người học cung cấp,
15/09/2026.

[2] A. Go, R. Bhayani, L. Huang, “Twitter Sentiment Classification using Distant
Supervision,” Stanford University, 2009. https://www-cs.stanford.edu/people/alecmgo/papers/TwitterDistantSupervision09.pdf

[3] Kaggle, “Sentiment140 dataset with 1.6 million tweets.”
https://www.kaggle.com/datasets/kazanova/sentiment140. Truy cập ngày 17/09/2026.

[4] Apache Spark, “Spark 3.5.7 Documentation - Overview.”
https://spark.apache.org/docs/3.5.7/. Truy cập ngày 17/09/2026.

[5] Apache Spark, “Spark SQL, DataFrames and Datasets Guide.”
https://spark.apache.org/docs/3.5.7/sql-programming-guide.html. Truy cập ngày 17/09/2026.

[6] Apache Spark, “Extracting, transforming and selecting features.”
https://spark.apache.org/docs/3.5.7/ml-features.html. Truy cập ngày 17/09/2026.

[7] Apache Spark, “Classification and Regression - Spark MLlib.”
https://spark.apache.org/docs/3.5.7/ml-classification-regression.html. Truy cập ngày
17/09/2026.

[8] Apache Hadoop, “HDFS Architecture.”
https://hadoop.apache.org/docs/current3/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html.
Truy cập ngày 17/09/2026.

[9] Apache Parquet, “Overview.” https://parquet.apache.org/docs/overview/. Truy cập ngày
17/09/2026.

[10] Apache Hadoop, “Official Hadoop Docker Image.” https://hub.docker.com/r/apache/hadoop.
Truy cập ngày 17/09/2026.

---

# PHỤ LỤC

## Phụ lục A. Cài đặt và chạy chương trình

### A.1. Cài môi trường

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### A.2. Mở giao diện

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\gui.ps1
```

### A.3. Chạy kiểm thử

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

### A.4. Chạy dữ liệu thật ở local

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_full.ps1 `
    -SampleFraction 0.10
```

### A.5. Chạy HDFS

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\hdfs_all.ps1 `
    -SampleFraction 0.10
```

NameNode UI: `http://localhost:9870`; DataNode UI: `http://localhost:9864`.

## Phụ lục B. Sản phẩm đầu ra

| Đường dẫn | Nội dung |
|---|---|
| `outputs/data_quality.json` | Chất lượng dữ liệu và số dòng bị loại |
| `outputs/analysis_summary.json` | Tóm tắt phân tích hành vi |
| `outputs/evaluation.json` | Validation, test và ma trận nhầm lẫn |
| `outputs/performance.json` | Các lần đo và trung vị benchmark |
| `outputs/tables/` | Bảng CSV dùng trong báo cáo |
| `outputs/charts/` | Biểu đồ PNG |
| `outputs/run_manifest.json` | Cấu hình và phiên bản môi trường |
| `models/sentiment_lr/` | Pipeline Logistic Regression đã lưu |

## Phụ lục C. Phân công nhóm hai thành viên

| Công việc | Thành viên 1 | Thành viên 2 | Kiểm tra chéo |
|---|:---:|:---:|---|
| Tìm hiểu bài toán và dataset | Chính | Hỗ trợ | Cả hai |
| Schema, chất lượng và làm sạch | Chính | Hỗ trợ | Thành viên 2 |
| Docker, NameNode, DataNode, HDFS | Chính | Hỗ trợ | Thành viên 2 |
| Spark SQL và bảng thống kê | Chính | Hỗ trợ | Thành viên 2 |
| Xử lý văn bản và đặc trưng | Hỗ trợ | Chính | Thành viên 1 |
| Huấn luyện và đánh giá | Hỗ trợ | Chính | Thành viên 1 |
| Benchmark và giao diện | Hỗ trợ | Chính | Thành viên 1 |
| Báo cáo, kiểm thử và demo | Cùng thực hiện | Cùng thực hiện | Cả hai |

## Phụ lục D. Kịch bản demo 8-10 phút

| Thời gian | Thao tác | Nội dung giải thích |
|---|---|---|
| 0-1 phút | Giới thiệu đề tài | Phạm vi hành vi và cảm xúc hai lớp |
| 1-2 phút | Mở giao diện, chọn CSV | Schema, nguồn và quy mô dữ liệu |
| 2-3 phút | Mở nhật ký chất lượng | Dòng bị loại và Parquet |
| 3-5 phút | Mở Spark SQL và 2-3 biểu đồ | Kết quả trong mẫu, giờ UTC |
| 5-7 phút | Mở đánh giá và ma trận | Train/validation/test và chỉ số |
| 7-9 phút | Dự đoán ba câu mới | Cùng pipeline tiền xử lý, giới hạn phủ định |
| 9-10 phút | Mở benchmark và kết luận | Vai trò Spark, giới hạn local/HDFS lab |

## Phụ lục E. Danh sách kiểm tra trước khi nộp

- [ ] Điền trường, khoa, giảng viên, lớp, nhóm, tên và MSSV của hai thành viên.
- [ ] Bảo đảm không còn placeholder dạng `{{...}}` trong báo cáo.
- [ ] Kiểm tra bảng số liệu khớp JSON/CSV trong `outputs/`.
- [ ] Kiểm tra tất cả hình mở được và có nhận xét.
- [ ] Ghi rõ kết quả chạy local; không gọi `local[2]` là cluster nhiều máy.
- [ ] Không dùng chỉ số của dữ liệu demo tổng hợp làm kết quả cuối kỳ.
- [ ] Thử giao diện và lệnh dự đoán trước buổi trình bày.
- [ ] Nộp kèm mã nguồn, README và bảng phân công theo yêu cầu giảng viên.
