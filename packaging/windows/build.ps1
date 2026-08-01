# Builds Desktop Cat for Windows from source on native Windows.
# Run from the repo root in PowerShell: .\packaging\windows\build.ps1
#
# Requires a native Windows Python (not WSL) with pip. Produces a folder
# (PyInstaller's default --onedir mode) zipped as Desktop-Cat-windows.zip --
# the Windows equivalent of the Linux AppImage in packaging/appimage/.
#
# Deliberately NOT --onefile: onefile mode self-extracts to a temp folder
# and runs from there on every launch, which is exactly the behavioral
# pattern antivirus heuristics (Windows Defender especially) associate with
# malware droppers. Unsigned PyInstaller onefile .exe's get flagged as
# "virus detected" constantly, even when completely benign. onedir mode
# doesn't have that unpack-and-run-from-temp behavior at runtime, so it's
# far less likely to trip heuristic/cloud-reputation detection. See the
# README's Windows section for the full explanation.

$ErrorActionPreference = "Stop"

$PkgDir = $PSScriptRoot
$RepoRoot = Join-Path $PkgDir "..\.."

pip install --quiet pyinstaller -r (Join-Path $RepoRoot "requirements.txt")

Remove-Item -Recurse -Force (Join-Path $PkgDir "build"), (Join-Path $PkgDir "dist"), (Join-Path $PkgDir "desktop-cat.spec") -ErrorAction SilentlyContinue

python -m PyInstaller `
    --name desktop-cat `
    --paths (Join-Path $RepoRoot "Python") `
    --windowed `
    --icon (Join-Path $PkgDir "desktop-cat.ico") `
    --distpath (Join-Path $PkgDir "dist") `
    --workpath (Join-Path $PkgDir "build") `
    --specpath $PkgDir `
    (Join-Path $RepoRoot "Python\desktopcat\main.py")

$zipPath = Join-Path $PkgDir "dist\Desktop-Cat-windows.zip"
Remove-Item $zipPath -ErrorAction SilentlyContinue
Compress-Archive -Path (Join-Path $PkgDir "dist\desktop-cat") -DestinationPath $zipPath

Write-Host "Built: $(Join-Path $PkgDir 'dist\desktop-cat\desktop-cat.exe') (zipped: $zipPath)"
