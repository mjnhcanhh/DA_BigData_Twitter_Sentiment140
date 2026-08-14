$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker\hdfs\docker-compose.yml"
Push-Location $ProjectRoot

try {
    docker compose -p twitter-hdfs -f $ComposeFile ps
    docker exec twitter-hdfs-datanode hdfs dfsadmin -report
    docker exec twitter-hdfs-datanode hdfs dfs -ls -R -h /twitter
    Write-Host "NameNode UI: http://localhost:9870"
}
finally {
    Pop-Location
}

