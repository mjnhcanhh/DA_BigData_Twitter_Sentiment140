param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    & $PythonCommand -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Creating .venv failed." }
    & .\.venv\Scripts\python.exe -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "Upgrading pip failed." }
    & .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Installing dependencies failed." }

    Write-Host "Environment ready. Run: .\scripts\test.ps1"
}
finally {
    Pop-Location
}
