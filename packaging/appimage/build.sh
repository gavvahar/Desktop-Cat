#!/usr/bin/env bash
# Builds Desktop-Cat-x86_64.AppImage from source.
# Run from anywhere: bash packaging/appimage/build.sh
#
# Requires: python3 + pip (network access to install pyinstaller and to
# download appimagetool on first run). Downloaded tools are cached in
# packaging/appimage/.tools/ so re-runs don't re-fetch them.

set -euo pipefail

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$PKG_DIR/../.." && pwd)"
TOOLS_DIR="$PKG_DIR/.tools"
APPIMAGETOOL="$TOOLS_DIR/appimagetool"

mkdir -p "$TOOLS_DIR"
if [ ! -x "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    curl -sL -o "$APPIMAGETOOL" \
        https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$APPIMAGETOOL"
fi

pip install --quiet pyinstaller -r "$REPO_ROOT/requirements.txt"

rm -rf "$PKG_DIR/build" "$PKG_DIR/dist" "$PKG_DIR/AppDir" "$PKG_DIR/desktop-cat.spec"

pyinstaller \
    --name desktop-cat \
    --paths "$REPO_ROOT/Python" \
    --windowed \
    --distpath "$PKG_DIR/dist" \
    --workpath "$PKG_DIR/build" \
    --specpath "$PKG_DIR" \
    "$REPO_ROOT/Python/desktopcat/main.py"

mkdir -p "$PKG_DIR/AppDir/usr/bin"
cp -a "$PKG_DIR/dist/desktop-cat/." "$PKG_DIR/AppDir/usr/bin/"

cp "$PKG_DIR/AppRun" "$PKG_DIR/AppDir/AppRun"
chmod +x "$PKG_DIR/AppDir/AppRun"
cp "$PKG_DIR/desktop-cat.desktop" "$PKG_DIR/AppDir/desktop-cat.desktop"
cp "$PKG_DIR/desktop-cat.png" "$PKG_DIR/AppDir/desktop-cat.png"

mkdir -p "$PKG_DIR/AppDir/usr/share/applications" "$PKG_DIR/AppDir/usr/share/icons/hicolor/512x512/apps"
cp "$PKG_DIR/desktop-cat.desktop" "$PKG_DIR/AppDir/usr/share/applications/desktop-cat.desktop"
cp "$PKG_DIR/desktop-cat.png" "$PKG_DIR/AppDir/usr/share/icons/hicolor/512x512/apps/desktop-cat.png"

ARCH=x86_64 "$APPIMAGETOOL" "$PKG_DIR/AppDir" "$PKG_DIR/Desktop-Cat-x86_64.AppImage"

echo "Built: $PKG_DIR/Desktop-Cat-x86_64.AppImage"
