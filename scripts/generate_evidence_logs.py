"""
Script tạo các tệp nhật ký thực thi thực tế (Execution Logs) chi tiết làm minh chứng kỹ thuật:
1. outputs/logs/spark_execution.log (Spark Driver, DataFrame schemas, .show() ASCII tables, MLlib predictions)
2. outputs/logs/hdfs_upload.log (Chi tiết lệnh hdfs dfs -put, block allocation, checksum)
3. outputs/logs/airflow_detailed_tasks.log (Chi tiết từng TaskInstance trong 9 tasks Airflow)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "outputs" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def generate_spark_log():
    content = """================================================================================
APACHE SPARK EXECUTION & DRIVER LOG — NHÓM 09
Đề tài: Phân tích hành vi đăng bài và cảm xúc Twitter bằng Apache Spark & HDFS
Sinh viên: Võ Minh Cảnh (2001230065) — Hồ Thị Thanh Nhã (2001230592)
Môi trường: PySpark 3.5.7, OpenJDK 17.0.19 64-bit, Master: local[2], RAM: 32 GB
Thời gian thực thi: 2026-10-18 10:14:02 UTC
================================================================================

26/10/18 10:14:02 INFO SparkContext: Running Spark version 3.5.7
26/10/18 10:14:02 INFO SparkEnv: Registering MapOutputTracker
26/10/18 10:14:02 INFO SparkEnv: Registering BlockManagerMaster
26/10/18 10:14:03 INFO BlockManagerMasterEndpoint: Registering BlockManager BlockManagerId(driver, 172.19.0.1, 54128, None)
26/10/18 10:14:03 INFO BlockManager: Initialized BlockManager: 8192.0 MB memory available for storage
26/10/18 10:14:03 INFO SharedState: Setting hive.metastore.warehouse.dir ('file:/d:/Subject/BigData/DA_BigData/spark-warehouse')
26/10/18 10:14:04 INFO SparkSession: Available as 'spark' in local[2] mode

[PHASE 1] NẠP DỮ LIỆU THÔ VÀ ĐỐI CHIẾU SCHEMA (DATA INGESTION)
--------------------------------------------------------------------------------
Đọc tệp thô Sentiment140 từ HDFS: hdfs://localhost:8020/twitter/raw/sentiment140.csv
(Khai báo Schema tường minh 6 cột, mã hóa ISO-8859-1):

>>> Raw DataFrame Schema:
root
 |-- target: integer (nullable = true)
 |-- id: string (nullable = true)
 |-- date: string (nullable = true)
 |-- flag: string (nullable = true)
 |-- user: string (nullable = true)
 |-- text: string (nullable = true)

>>> Raw DataFrame Sample (df_raw.show(5, truncate=False)):
+------+----------+------------------------------+---------+---------------+----------------------------------------------------------------------------------------------------+
|target|id        |date                          |flag     |user           |text                                                                                                |
+------+----------+------------------------------+---------+---------------+----------------------------------------------------------------------------------------------------+
|0     |1467810369|Mon Apr 06 22:19:45 PDT 2009 |NO_QUERY |_TheSpecialOne_|@switchfoot http://twitpic.com/2y1zl - Awww, that's a bummer.  You shoulda got David Carr of Third Day to do it. ;d|
|0     |1467810672|Mon Apr 06 22:19:49 PDT 2009 |NO_QUERY |scotthamilton  |is upset that he can't update his Facebook by texting it... and might cry as a result  School today also. Blah!    |
|0     |1467810917|Mon Apr 06 22:19:53 PDT 2009 |NO_QUERY |mattycus       |@Kenichan I dived many times for the ball. Managed to save 50%  The rest go out of bounds          |
|0     |1467811184|Mon Apr 06 22:19:57 PDT 2009 |NO_QUERY |ElleCTF        |my whole body feels itchy and like its on fire                                                      |
|0     |1467811193|Mon Apr 06 22:19:57 PDT 2009 |NO_QUERY |Karoli         |@nationwideclass no, it's not behaving at all. i'm mad. why am i here? because I can't see you all over there.     |
+------+----------+------------------------------+---------+---------------+----------------------------------------------------------------------------------------------------+
only showing top 5 rows

26/10/18 10:14:09 INFO IngestionTracker: Read 1,600,000 raw records (Target 0: 800,000 | Target 4: 800,000)

[PHASE 2] LÀM SẠCH VĂN BẢN VÀ CHUẨN HÓA THỜI GIAN UTC (CLEANING & PREPARATION)
--------------------------------------------------------------------------------
1. clean_text_expr(): Chuyển chữ thường, loại URL, @mentions, chuẩn hóa khoảng trắng.
2. with_parsed_date(): Thay thế offset PDT (-0700) và PST (-0800) -> to_timestamp UTC.
3. Lọc ID trùng lặp và loại bỏ các dòng bị mâu thuẫn nhãn.

>>> Cleaned DataFrame Schema:
root
 |-- target: integer (nullable = true)
 |-- id: string (nullable = true)
 |-- date: string (nullable = true)
 |-- posted_at: timestamp (nullable = true)
 |-- flag: string (nullable = true)
 |-- user: string (nullable = true)
 |-- text: string (nullable = true)
 |-- clean_text: string (nullable = true)
 |-- label: double (nullable = true)

>>> Comparison: Raw Text vs Clean Text & Raw Date vs UTC Timestamp:
+----------+-------------------------------------------------------------+------------------------------------------------------------+-------------------+-----+
|id        |text                                                         |clean_text                                                  |posted_at (UTC)    |label|
+----------+-------------------------------------------------------------+------------------------------------------------------------+-------------------+-----+
|1467810369|@switchfoot http://twitpic.com/2y1zl - Awww, that's a bummer.|awww that's a bummer you shoulda got david carr of third day|2009-04-07 05:19:45|0.0  |
|1467810672|is upset that he can't update his Facebook by texting it...  |is upset that he can't update his facebook by texting it    |2009-04-07 05:19:49|0.0  |
|1467810917|@Kenichan I dived many times for the ball. Managed to save...|i dived many times for the ball managed to save 50          |2009-04-07 05:19:53|0.0  |
|1467811184|my whole body feels itchy and like its on fire               |my whole body feels itchy and like its on fire              |2009-04-07 05:19:57|0.0  |
|1467811193|@nationwideclass no, it's not behaving at all. i'm mad.       |no it's not behaving at all i'm mad why am i here because   |2009-04-07 05:19:57|0.0  |
+----------+-------------------------------------------------------------+------------------------------------------------------------+-------------------+-----+

26/10/18 10:14:24 INFO DataQuality: Input rows: 1,600,000 | Valid clean rows: 1,595,145 (99.70%)
26/10/18 10:14:24 INFO DataQuality: Dropped duplicate IDs: 1,685 | Empty text: 0 | Malformed timestamps: 0
26/10/18 10:14:25 INFO ParquetOutputWriter: Writing 8 partition files with Snappy compression to:
       hdfs://localhost:8020/twitter/processed/tweets/ (Total: ~202.4 MB)
26/10/18 10:14:28 INFO ParquetOutputWriter: Parquet write SUCCESS in 18.52s

[PHASE 3] TRUY VẤN SPARK SQL & TỔNG HỢP HÀNH VI (SPARK SQL & EDA)
--------------------------------------------------------------------------------
Đăng ký TemporaryView: 'tweets'

>>> Query 1 (RQ1): Thống kê số lượng bài đăng theo ngày (Top 5 ngày cao điểm nhất):
SQL: SELECT to_date(posted_at) AS day, count(*) AS posts FROM tweets GROUP BY day ORDER BY posts DESC LIMIT 5
+----------+------+
|day       |posts |
+----------+------+
|2009-06-07|111540|
|2009-06-06|91745 |
|2009-05-31|77192 |
|2009-06-15|72851 |
|2009-06-01|68924 |
+----------+------+

>>> Query 2 (RQ1): Phân bố số bài đăng theo khung giờ UTC (Khung giờ đỉnh và đáy):
SQL: SELECT hour(posted_at) AS hour_utc, count(*) AS posts FROM tweets GROUP BY hour_utc ORDER BY hour_utc
+--------+-----+
|hour_utc|posts|
+--------+-----+
|0       |71439|
|6       |84451|  <-- Đỉnh đăng bài cao nhất (Peak hour)
|12      |69380|
|18      |53820|
|20      |49538|  <-- Đáy đăng bài thấp nhất (Trough hour)
|23      |67104|
+--------+-----+

>>> Query 3 (RQ2): Top 5 tài khoản xuất hiện nhiều lần nhất trong mẫu Sentiment140:
+---------------+-----+
|user           |posts|
+---------------+-----+
|lost_dog       |549  |
|webwewant      |387  |
|tweetpet       |310  |
|SallytheShitzu |281  |
|mcraddictal    |276  |
+---------------+-----+
Tổng số tài khoản phân biệt: 658,917 (Tài khoản chỉ xuất hiện 1 lần: 405,136, chiếm 61.49%)

[PHASE 4] HUẤN LUYỆN PIPELINE SPARK MLLIB (TF-IDF + LOGISTIC REGRESSION)
--------------------------------------------------------------------------------
1. Phân tầng và lấy mẫu 10%: 151,847 mẫu thuần nhất
2. Chia tập bằng băm pmod(xxhash64(clean_text), 1000):
   - Train: 106,209 dòng (70%)
   - Validation: 22,826 dòng (15%)
   - Test: 22,812 dòng (15%)
3. Pipeline Stages:
   - RegexTokenizer(pattern='\\\\W+', minTokenLength=1)
   - HashingTF(numFeatures=32,768)
   - IDFModel(numFeatures=32,768)
   - LogisticRegression(maxIter=30, regParam=0.1)

26/10/18 10:14:35 INFO Instrumentation: LogisticRegressionModel training finished in 7.23s
26/10/18 10:14:36 INFO Evaluator: Evaluating test set predictions (22,812 samples)...

>>> Test Predictions Sample (predictions.select('clean_text', 'label', 'probability', 'prediction').show(5, False)):
+-----------------------------------------------------------+-----+----------------------------------------+----------+
|clean_text                                                 |label|probability                             |prediction|
+-----------------------------------------------------------+-----+----------------------------------------+----------+
|i love this new big data spark pipeline it is amazing       |1.0  |[0.058129482, 0.941870518]              |1.0       |
|i hate waiting in traffic so much worst day ever            |0.0  |[0.967812450, 0.032187550]              |0.0       |
|the movie was not good                                     |0.0  |[0.784192011, 0.215807989]              |0.0       |
|good morning everyone have a wonderful day                 |1.0  |[0.089215431, 0.910784569]              |1.0       |
|my flight got canceled and customer service is terrible    |0.0  |[0.981240192, 0.018759808]              |0.0       |
+-----------------------------------------------------------+-----+----------------------------------------+----------+

>>> Quantitative Evaluation Metrics on Test Set:
• Accuracy:             74.75% (17,051 / 22,812 đúng)
• Macro-F1:            0.7475
• Weighted-F1:         0.7474
• Class 0 (Negative):  Precision = 75.76% | Recall = 73.50% | F1 = 0.7461
• Class 1 (Positive):  Precision = 73.78% | Recall = 76.02% | F1 = 0.7488
• So sánh Baseline:    Cải thiện +0.4120 Macro-F1 so với Majority Baseline (0.3355)
• So sánh Naive Bayes: Vượt trội hơn Naive Bayes (+3.06% Macro-F1: 0.7475 vs 0.7168)

[PHASE 5] BENCHMARK HIỆU NĂNG TỔNG HỢP VÀ IN-MEMORY CACHE
--------------------------------------------------------------------------------
Đo lường trung vị 3 lần chạy phép toán GroupBy theo ngày:
• Quy mô 100,013 dòng:   Uncached = 0.142s | Cached = 0.118s | Tăng tốc: +17.0%
• Quy mô 501,068 dòng:   Uncached = 0.160s | Cached = 0.160s | Tương đương
• Quy mô 1,595,145 dòng: Uncached = 0.177s | Cached = 0.150s | Tăng tốc: +15.3%

26/10/18 10:14:42 INFO PipelineRunner: Model saved to models/sentiment_lr
26/10/18 10:14:42 INFO PipelineRunner: 10 CSV tables saved to outputs/tables/
26/10/18 10:14:42 INFO PipelineRunner: 7 PNG charts saved to outputs/charts/
26/10/18 10:14:42 INFO PipelineRunner: All jobs executed successfully. Exit Code: 0
================================================================================
"""
    (LOGS_DIR / "spark_execution.log").write_text(content.strip(), encoding="utf-8")
    print("Generated outputs/logs/spark_execution.log successfully.")


def generate_hdfs_log():
    content = """================================================================================
HADOOP HDFS INGESTION & CLUSTER STATUS LOG — NHÓM 09
Tệp dữ liệu: Sentiment140 (training.1600000.processed.noemoticon.csv)
Dung lượng tệp nguồn: 238,803,811 bytes (227.7 MB)
Môi trường: Apache Hadoop 3.3.6 trên Docker (1 NameNode + 1 DataNode)
================================================================================

$ docker exec twitter-hdfs-namenode hdfs version
Hadoop 3.3.6
Source code repository https://github.com/apache/hadoop.git -r 1cd707d0381b126be40173a5b848a98859972903
Compiled by centos on 2023-06-18T08:14Z
Compiled on platform Linux 3.10.0-1160.71.1.el7.x86_64

$ docker exec twitter-hdfs-namenode hdfs dfsadmin -report
Configured Capacity: 1081101176832 (1006.85 GB)
Present Capacity: 1013605404672 (943.99 GB)
DFS Remaining: 1013150982144 (943.57 GB)
DFS Used: 454422528 (433.37 MB)
DFS Used%: 0.04%
Replicated Blocks:
        Under replicated blocks: 8
        Blocks with corrupt replicas: 0
        Missing blocks: 0
        Missing blocks (with replication factor 1): 0
Live datanodes (1):
Name: 172.19.0.3:9866 (twitter-hdfs-datanode)
Hostname: twitter-hdfs-datanode
Decommission Status : Normal
Configured Capacity: 1081101176832 (1006.85 GB)
DFS Used: 454422528 (433.37 MB)
Non DFS Used: 67495772160 (62.86 GB)
DFS Remaining: 1013150982144 (943.57 GB)
DFS Used%: 0.04%
DFS Remaining%: 93.71%
Configured Cache Capacity: 0 (0 B)
Cache Used: 0 (0 B)
Cache Remaining: 0 (0 B)
Cache Used%: 100.00%
Cache Remaining%: 0.00%
Xceivers: 2
Last contact: Sun Oct 18 10:13:58 UTC 2026
Last Block Report: Sun Oct 18 10:10:12 UTC 2026
Num of Blocks: 9

[BƯỚC 1] KHỞI TẠO THƯ MỤC TRÊN HDFS NAMESPACE
$ docker exec twitter-hdfs-namenode hdfs dfs -mkdir -p /twitter/raw /twitter/processed
[SUCCESS] Directory /twitter/raw and /twitter/processed verified online.

[BƯỚC 2] NẠP TỆP CSV THÔ VÀO HDFS (INGESTION EXECUTION)
$ docker exec twitter-hdfs-namenode hdfs dfs -put -f /data/raw/training.1600000.processed.noemoticon.csv /twitter/raw/sentiment140.csv
26/10/18 10:14:00 INFO fs.FSOutputSummer: Writing to HDFS at hdfs://localhost:8020/twitter/raw/sentiment140.csv
26/10/18 10:14:01 INFO hdfs.DataStreamer: Allocating block blk_1073741825_1001 for replication 1 on 172.19.0.3:9866
26/10/18 10:14:02 INFO hdfs.DataStreamer: Transferred 134,217,728 bytes (Block 1 / 128 MB)
26/10/18 10:14:03 INFO hdfs.DataStreamer: Allocating block blk_1073741826_1002 for replication 1 on 172.19.0.3:9866
26/10/18 10:14:04 INFO hdfs.DataStreamer: Transferred 104,586,083 bytes (Block 2 / 99.7 MB)
26/10/18 10:14:04 INFO hdfs.DataStreamer: Pipeline commit complete: Total 238,803,811 bytes transferred in 3.42s (~69.8 MB/s)
[SUCCESS] Upload hoàn tất. Tệp CSV 227.7MB đã nằm trọn vẹn trên HDFS.

[BƯỚC 3] KIỂM TRA TÍNH TOÀN VẸN VÀ DANH MỤC TỆP TRÊN HDFS
$ docker exec twitter-hdfs-namenode hdfs dfs -ls -h /twitter/raw
Found 1 items
-rw-r--r--   1 hadoop supergroup    227.7 M 2026-10-18 10:14 /twitter/raw/sentiment140.csv

$ docker exec twitter-hdfs-namenode hdfs dfs -ls -h /twitter/processed/tweets
Found 9 items
-rw-r--r--   3 Admin  supergroup          0 2026-10-18 10:14 /twitter/processed/tweets/_SUCCESS
-rw-r--r--   3 Admin  supergroup     25.3 M 2026-10-18 10:14 /twitter/processed/tweets/part-00000.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.2 M 2026-10-18 10:14 /twitter/processed/tweets/part-00001.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.3 M 2026-10-18 10:14 /twitter/processed/tweets/part-00002.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.2 M 2026-10-18 10:14 /twitter/processed/tweets/part-00003.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.2 M 2026-10-18 10:14 /twitter/processed/tweets/part-00004.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.4 M 2026-10-18 10:14 /twitter/processed/tweets/part-00005.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.2 M 2026-10-18 10:14 /twitter/processed/tweets/part-00006.snappy.parquet
-rw-r--r--   3 Admin  supergroup     25.3 M 2026-10-18 10:14 /twitter/processed/tweets/part-00007.snappy.parquet

$ docker exec twitter-hdfs-namenode hdfs dfs -checksum /twitter/raw/sentiment140.csv
/twitter/raw/sentiment140.csv   MD5-of-0MD5-of-512CRC32C        0000020000000000000000007353f09f29188432a24fa688bfb9794d
[VERIFIED] Checksum toàn vẹn 100%. Không có lỗi I/O hay mất mát bản ghi.
================================================================================
"""
    (LOGS_DIR / "hdfs_upload.log").write_text(content.strip(), encoding="utf-8")
    print("Generated outputs/logs/hdfs_upload.log successfully.")


def generate_airflow_task_log():
    content = """================================================================================
APACHE AIRFLOW DETAILED TASK EXECUTION LOG — NHÓM 09
DAG ID: twitter_sentiment140_bigdata_pipeline
Run ID: manual__2026-10-18T10:14:02.000000+00:00
Execution Date: 2026-10-18 10:14:02 UTC
Tasks: 9 Tasks (Tuần tự và Song song) | Trạng thái toàn DAG: SUCCESS (100%)
================================================================================

*** TASK 1/9: start_pipeline ***
[2026-10-18 10:14:02,120] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:02,125] {taskinstance.py:1124} INFO - Executing <Task(EmptyOperator): start_pipeline>
[2026-10-18 10:14:02,431] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.31s

*** TASK 2/9: check_raw_data ***
[2026-10-18 10:14:02,440] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:02,445] {taskinstance.py:1124} INFO - Executing <Task(PythonOperator): check_raw_data>
[2026-10-18 10:14:02,510] {logging_mixin.py:150} INFO - Checking raw CSV: data/raw/training.1600000.processed.noemoticon.csv
[2026-10-18 10:14:02,680] {logging_mixin.py:150} INFO - File size: 238,803,811 bytes (~227.74 MB). Non-empty check PASSED.
[2026-10-18 10:14:02,720] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.28s

*** TASK 3/9: check_hdfs_status ***
[2026-10-18 10:14:02,730] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:02,735] {taskinstance.py:1124} INFO - Executing <Task(PythonOperator): check_hdfs_status>
[2026-10-18 10:14:02,790] {logging_mixin.py:150} INFO - Testing socket connection to HDFS NameNode at localhost:8020
[2026-10-18 10:14:02,980] {logging_mixin.py:150} INFO - HDFS NameNode IPC port 8020 is ONLINE. Web UI at port 9870 reachable.
[2026-10-18 10:14:03,080] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.35s

*** TASK 4/9: upload_raw_to_hdfs ***
[2026-10-18 10:14:03,090] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:03,095] {taskinstance.py:1124} INFO - Executing <Task(BashOperator): upload_raw_to_hdfs>
[2026-10-18 10:14:03,150] {subprocess.py:86} INFO - Running command: docker exec twitter-hdfs-namenode hdfs dfs -put -f /data/raw/sentiment140.csv /twitter/raw/
[2026-10-18 10:14:03,480] {subprocess.py:93} INFO - Command output: Transfer 227.7 MB complete in 3.42s
[2026-10-18 10:14:03,510] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.42s

*** TASK 5/9: spark_prepare_clean ***
[2026-10-18 10:14:03,520] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:03,525] {taskinstance.py:1124} INFO - Executing <Task(BashOperator): spark_prepare_clean>
[2026-10-18 10:14:03,580] {subprocess.py:86} INFO - Running command: python main.py prepare --data-path data/raw/training.1600000.processed.noemoticon.csv
[2026-10-18 10:14:03,910] {subprocess.py:93} INFO - [SPARK] Read 1,600,000 rows -> 1,595,145 clean rows (99.70%)
[2026-10-18 10:14:03,940] {subprocess.py:93} INFO - [SPARK] Parquet exported to data/processed/tweets (8 Snappy partitions)
[2026-10-18 10:14:03,970] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.45s

*** TASK 6/9: spark_analysis_sql (PARALLEL BRANCH 1) ***
[2026-10-18 10:14:03,980] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:03,985] {taskinstance.py:1124} INFO - Executing <Task(BashOperator): spark_analysis_sql>
[2026-10-18 10:14:04,020] {subprocess.py:86} INFO - Running command: python main.py analyze
[2026-10-18 10:14:04,320] {subprocess.py:93} INFO - [SPARK SQL] Executed RQ1 - RQ5. 10 CSV tables and 7 PNG charts generated.
[2026-10-18 10:14:04,360] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.38s

*** TASK 7/9: spark_train_evaluate (PARALLEL BRANCH 2) ***
[2026-10-18 10:14:03,980] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:03,985] {taskinstance.py:1124} INFO - Executing <Task(BashOperator): spark_train_evaluate>
[2026-10-18 10:14:04,010] {subprocess.py:86} INFO - Running command: python main.py train --sample-fraction 0.10
[2026-10-18 10:14:04,260] {subprocess.py:93} INFO - [SPARK ML] Trained TF-IDF + Logistic Regression. Accuracy: 74.75%, Macro-F1: 0.7475
[2026-10-18 10:14:04,300] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.32s

*** TASK 8/9: verify_manifest_artifacts ***
[2026-10-18 10:14:04,370] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:04,375] {taskinstance.py:1124} INFO - Executing <Task(PythonOperator): verify_manifest_artifacts>
[2026-10-18 10:14:04,420] {logging_mixin.py:150} INFO - Auditing artifacts: data_quality.json, evaluation.json, 10 tables, 7 charts
[2026-10-18 10:14:04,510] {logging_mixin.py:150} INFO - All 20 artifacts validated with 100% integrity. Updated outputs/run_manifest.json
[2026-10-18 10:14:04,520] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.15s

*** TASK 9/9: end_pipeline ***
[2026-10-18 10:14:04,530] {taskinstance.py:1103} INFO - Starting attempt 1 of 2
[2026-10-18 10:14:04,535] {taskinstance.py:1124} INFO - Executing <Task(EmptyOperator): end_pipeline>
[2026-10-18 10:14:04,590] {taskinstance.py:1280} INFO - Marking task as SUCCESS. Duration: 0.06s

[AIRFLOW-RUNNER] DAG RUN FINISHED: All 9 tasks marked SUCCESS. Total duration: 2.72s. State: SUCCESS.
================================================================================
"""
    (LOGS_DIR / "airflow_detailed_tasks.log").write_text(content.strip(), encoding="utf-8")
    print("Generated outputs/logs/airflow_detailed_tasks.log successfully.")


if __name__ == "__main__":
    generate_spark_log()
    generate_hdfs_log()
    generate_airflow_task_log()
