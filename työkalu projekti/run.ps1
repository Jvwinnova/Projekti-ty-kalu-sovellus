$ErrorActionPreference = "Stop"

$venvPython = Join-Path $PSScriptRoot ".venv312\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Python venv not found at .venv312. Please run:" -ForegroundColor Yellow
    Write-Host "  C:\Python312\python.exe -m venv .venv312" -ForegroundColor Yellow
    exit 1
}

& $venvPython "bin\run.py"
