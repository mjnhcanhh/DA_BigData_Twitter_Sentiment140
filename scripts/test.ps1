$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot

try {
    if (-not (Test-Path .\.venv\Scripts\python.exe)) {
        throw "Missing .venv. Run .\scripts\setup.ps1 first."
    }

    $env:RUN_SPARK_TESTS = "1"
    & .\.venv\Scripts\python.exe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Unit or Spark integration tests failed." }
    & .\.venv\Scripts\python.exe main.py demo `
        --rows 240 `
        --processed .test-artifacts\processed `
        --outputs .test-artifacts\outputs `
        --model .test-artifacts\models\sentiment_lr `
        --skip-naive-bayes `
        --skip-benchmark
    if ($LASTEXITCODE -ne 0) { throw "End-to-end smoke test failed." }
}
finally {
    Pop-Location
}
