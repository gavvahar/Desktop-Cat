# Launch Desktop-Cat on native Windows (not WSL). Run from the repo root: .\run.ps1

$env:PYTHONPATH = Join-Path $PSScriptRoot "Python"
python -m desktopcat.main
