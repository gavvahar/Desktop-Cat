#!/usr/bin/env bash
# Builds "Desktop Cat.app" from source on macOS.
# Run from anywhere: bash packaging/macos/build.sh
#
# Must be run ON macOS -- PyInstaller can't cross-compile. Produces
# packaging/macos/dist/Desktop Cat.app, zipped as Desktop-Cat-macos.zip for
# distribution (Finder mangles the .app's own space when zipped for you, so
# this script does it explicitly with a space-free archive name instead).
#
# The app is unsigned (no Apple Developer account involved in this project),
# so Gatekeeper will block a plain double-click on first run. See the
# README's macOS section for the right-click-Open workaround.

set -euo pipefail

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$PKG_DIR/../.." && pwd)"

pip install --quiet pyinstaller -r "$REPO_ROOT/requirements.txt"

rm -rf "$PKG_DIR/build" "$PKG_DIR/dist" "$PKG_DIR/Desktop Cat.spec"

pyinstaller \
    --name "Desktop Cat" \
    --paths "$REPO_ROOT/Python" \
    --windowed \
    --icon "$PKG_DIR/desktop-cat.icns" \
    --distpath "$PKG_DIR/dist" \
    --workpath "$PKG_DIR/build" \
    --specpath "$PKG_DIR" \
    "$REPO_ROOT/Python/desktopcat/main.py"

(cd "$PKG_DIR/dist" && zip -qr "Desktop-Cat-macos.zip" "Desktop Cat.app")

echo "Built: $PKG_DIR/dist/Desktop Cat.app (zipped: $PKG_DIR/dist/Desktop-Cat-macos.zip)"
