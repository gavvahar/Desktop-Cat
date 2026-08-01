# Desktop-Cat installer for native Windows (not WSL).
# Run from the repo root in PowerShell: .\install.ps1

$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python was not found on PATH. Install Python 3 from python.org (check 'Add python.exe to PATH' during setup), then re-run this script."
    exit 1
}

Write-Host "Installing Desktop-Cat dependencies with $($python.Source)..."
pip install -r (Join-Path $PSScriptRoot "requirements.txt")

Write-Host ""
Write-Host "Done. Start the cat with:  .\run.ps1"
