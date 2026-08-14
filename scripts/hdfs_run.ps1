param(
    [double]$SampleFraction = 0.10
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        throw "Missing .venv. Run scripts\setup.ps1 first."
    }

    docker exec twitter-hdfs-datanode hdfs dfs -test -e /twitter/raw/sentiment140.csv
    if ($LASTEXITCODE -ne 0) {
        throw "HDFS input is missing. Run scripts\hdfs_upload.ps1 first."
    }

    & .\.venv\Scripts\python.exe main.py run-all `
        --data "hdfs://localhost:8020/twitter/raw/sentiment140.csv" `
        --processed "hdfs://localhost:8020/twitter/processed/tweets" `
        --sample-fraction $SampleFraction
    if ($LASTEXITCODE -ne 0) { throw "The Spark + HDFS pipeline failed." }
}
finally {
    Pop-Location
}

