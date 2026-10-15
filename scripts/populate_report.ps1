$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        throw "Missing .venv. Run .\scripts\setup.ps1 first."
    }

    & .\.venv\Scripts\python.exe main.py populate-report
    if ($LASTEXITCODE -ne 0) { throw "Populate report failed." }
}
finally {
    Pop-Location
}

