# Apache Airflow Cho Twitter Sentiment140 Pipeline

Thư mục này chứa cấu hình Docker Compose để khởi chạy Apache Airflow Standalone nhằm điều phối DAG quy trình Big Data.

## 1. Khởi chạy Airflow bằng Docker

```powershell
docker compose -f docker/airflow/docker-compose.yml up -d
```

Sau khi container khởi động, truy cập giao diện Airflow Web UI:
- Địa chỉ: <http://localhost:8088>
- Tài khoản: `admin`
- Mật khẩu: `admin`

## 2. Kiểm tra DAG

Trong danh sách DAGs, tìm DAG `twitter_sentiment140_bigdata_pipeline` và bật nút kích hoạt (Unpause) hoặc nhấn nút **Trigger DAG** để bắt đầu quy trình điều phối.

## 3. Dừng container

```powershell
docker compose -f docker/airflow/docker-compose.yml down
```
