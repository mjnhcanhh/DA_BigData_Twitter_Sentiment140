$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VirtualPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Push-Location $ProjectRoot
try {
    if (Test-Path -LiteralPath $VirtualPython -PathType Leaf) {
        & $VirtualPython gui.py
    }
    else {
        Write-Host "The .venv environment is missing. Opening the GUI with system Python."
        Write-Host "Use the 'Cai moi truong' button before running Spark."
        & python gui.py
    }
    if ($LASTEXITCODE -ne 0) { throw "Opening the desktop interface failed." }
}
finally {
    Pop-Location
}
