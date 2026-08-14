param(
    [string]$DataPath = "data\raw\training.1600000.processed.noemoticon.csv",
    [double]$SampleFraction = 0.10
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

& (Join-Path $PSScriptRoot "hdfs_start.ps1")
& (Join-Path $PSScriptRoot "hdfs_upload.ps1") -DataPath $DataPath
& (Join-Path $PSScriptRoot "hdfs_run.ps1") -SampleFraction $SampleFraction

Write-Host "Spark + HDFS workflow completed."
Write-Host "Project root: $ProjectRoot"

