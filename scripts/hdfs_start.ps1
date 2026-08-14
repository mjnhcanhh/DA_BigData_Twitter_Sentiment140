$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker\hdfs\docker-compose.yml"
Push-Location $ProjectRoot

try {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine is not running. Open Docker Desktop and wait until it is ready."
    }

    docker compose -p twitter-hdfs -f $ComposeFile up -d --quiet-pull
    if ($LASTEXITCODE -ne 0) { throw "Starting the HDFS containers failed." }

    $Ready = $false
    for ($Attempt = 1; $Attempt -le 45; $Attempt++) {
        try {
            $null = docker exec twitter-hdfs-datanode hdfs dfsadmin -report 2>&1
            if ($LASTEXITCODE -eq 0) {
                $Ready = $true
                break
            }
        }
        catch {
            # Container still initializing
        }
        Start-Sleep -Seconds 2
    }
    if (-not $Ready) {
        throw "HDFS did not become ready within 90 seconds. Run scripts\hdfs_status.ps1."
    }

    docker compose -p twitter-hdfs -f $ComposeFile ps
    Write-Host "HDFS is ready: hdfs://localhost:8020"
    Write-Host "NameNode UI: http://localhost:9870"
    Write-Host "DataNode UI: http://localhost:9864"
}
finally {
    Pop-Location
}
