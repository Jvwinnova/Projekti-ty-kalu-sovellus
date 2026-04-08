$ErrorActionPreference = "Stop"

$venvCandidates = @(
    (Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"),
    (Join-Path $PSScriptRoot ".venv312\Scripts\python.exe")
)

$venvPython = $null
foreach ($candidate in $venvCandidates) {
    if (Test-Path $candidate) {
        $venvPython = $candidate
        break
    }
}

if (-not $venvPython) {
    Write-Host "Python venv not found. Looked for:" -ForegroundColor Yellow
    Write-Host "  ..\\.venv\\Scripts\\python.exe" -ForegroundColor Yellow
    Write-Host "  .venv312\\Scripts\\python.exe" -ForegroundColor Yellow
    exit 1
}

& $venvPython "bin\run.py"
