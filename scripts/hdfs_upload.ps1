param(
    [string]$DataPath = "data\raw\training.1600000.processed.noemoticon.csv"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    if (-not (Test-Path -LiteralPath $DataPath -PathType Leaf)) {
        throw "Sentiment140 CSV not found: $DataPath"
    }
    $ResolvedData = (Resolve-Path -LiteralPath $DataPath).Path
    $ContainerSource = "/tmp/sentiment140.csv"
    $HdfsTarget = "/twitter/raw/sentiment140.csv"

    docker exec twitter-hdfs-datanode hdfs dfsadmin -report *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "HDFS is not ready. Run scripts\hdfs_start.ps1 first."
    }

    docker cp $ResolvedData "twitter-hdfs-datanode:$ContainerSource"
    if ($LASTEXITCODE -ne 0) { throw "Copying the CSV into the DataNode container failed." }

    docker exec twitter-hdfs-datanode hdfs dfs -mkdir -p /twitter/raw
    if ($LASTEXITCODE -ne 0) { throw "Creating /twitter/raw in HDFS failed." }
    docker exec twitter-hdfs-datanode hdfs dfs -put -f $ContainerSource $HdfsTarget
    if ($LASTEXITCODE -ne 0) { throw "Uploading the CSV to HDFS failed." }

    docker exec twitter-hdfs-datanode hdfs dfs -ls -h $HdfsTarget
    if ($LASTEXITCODE -ne 0) { throw "The uploaded HDFS file could not be verified." }
    Write-Host "Uploaded to hdfs://localhost:8020$HdfsTarget"
}
finally {
    Pop-Location
}

