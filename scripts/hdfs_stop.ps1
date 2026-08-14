$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker\hdfs\docker-compose.yml"
Push-Location $ProjectRoot

try {
    docker compose -p twitter-hdfs -f $ComposeFile down
    if ($LASTEXITCODE -ne 0) { throw "Stopping the HDFS containers failed." }
    Write-Host "HDFS containers stopped. Named volumes and data were retained."
}
finally {
    Pop-Location
}

