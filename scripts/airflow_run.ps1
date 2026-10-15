param(
    [switch]$Docker
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    $PythonPath = "python"
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [AIRFLOW] KIỂM THỬ VÀ ĐIỀU PHỐI DAG HỆ THỐNG BIG DATA" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ($Docker) {
    Write-Host "Khởi chạy Apache Airflow qua Docker Compose..." -ForegroundColor Yellow
    docker compose -f (Join-Path $ProjectRoot "docker\airflow\docker-compose.yml") up -d
    Write-Host "Airflow Web UI: http://localhost:8088 (User: admin / Pass: admin)" -ForegroundColor Green
} else {
    Write-Host "Thực thi kiểm tra DAG và xuất log điều phối pipeline..." -ForegroundColor Yellow
    & $PythonPath (Join-Path $ProjectRoot "scripts\test_airflow_dag.py")
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Hoàn thành kiểm thử Airflow DAG! Log đã được ghi vào outputs\logs\airflow_dag_run.log" -ForegroundColor Green
    } else {
        Write-Host "Có lỗi trong quá trình thực thi DAG." -ForegroundColor Red
    }
}
