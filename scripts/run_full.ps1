param(
    [string]$DataPath = "data/raw/training.1600000.processed.noemoticon.csv",
    [double]$SampleFraction = 0.10
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        throw "Missing .venv. Run .\scripts\setup.ps1 first."
    }

    if (-not (Test-Path -LiteralPath $DataPath)) {
        throw "Sentiment140 CSV not found: $DataPath"
    }

    & .\.venv\Scripts\python.exe main.py run-all --data $DataPath --sample-fraction $SampleFraction
    if ($LASTEXITCODE -ne 0) { throw "Full Sentiment140 pipeline failed." }
}
finally {
    Pop-Location
}
