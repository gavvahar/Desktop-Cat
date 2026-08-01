# Builds Desktop-Cat.exe from source on native Windows.
# Run from the repo root in PowerShell: .\packaging\windows\build.ps1
#
# Requires a native Windows Python (not WSL) with pip. Produces a single
# portable .exe (PyInstaller --onefile) -- the Windows equivalent of the
# Linux AppImage in packaging/appimage/.

$ErrorActionPreference = "Stop"

$PkgDir = $PSScriptRoot
$RepoRoot = Join-Path $PkgDir "..\.."

pip install --quiet pyinstaller -r (Join-Path $RepoRoot "requirements.txt")

Remove-Item -Recurse -Force (Join-Path $PkgDir "build"), (Join-Path $PkgDir "dist"), (Join-Path $PkgDir "desktop-cat.spec") -ErrorAction SilentlyContinue

python -m PyInstaller `
    --name desktop-cat `
    --paths (Join-Path $RepoRoot "Python") `
    --windowed `
    --onefile `
    --icon (Join-Path $PkgDir "desktop-cat.ico") `
    --distpath (Join-Path $PkgDir "dist") `
    --workpath (Join-Path $PkgDir "build") `
    --specpath $PkgDir `
    (Join-Path $RepoRoot "Python\desktopcat\main.py")

Write-Host "Built: $(Join-Path $PkgDir 'dist\desktop-cat.exe')"
