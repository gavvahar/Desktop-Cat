#!/usr/bin/env bash
# Builds and bundles Desktop Cat as a .flatpak from source.
# Run from anywhere: bash packaging/flatpak/build.sh
#
# Requires flatpak + flatpak-builder installed, plus the
# org.freedesktop.Platform//23.08 and org.freedesktop.Sdk//23.08 runtimes:
#   flatpak install flathub org.freedesktop.Platform//23.08 org.freedesktop.Sdk//23.08
#
# Unlike the other packaging/*/build.sh scripts, this one has NOT been run
# successfully end-to-end locally -- flatpak-builder isn't available in the
# environment this was written in (sudo/network-heavy install, not
# feasible there). See .github/workflows/release.yml's build-flatpak job
# for the actual (CI-based) verification of this manifest.

set -euo pipefail

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

flatpak-builder --force-clean --repo="$PKG_DIR/repo" "$PKG_DIR/build-dir" \
    "$PKG_DIR/io.github.gavvahar.DesktopCat.yml"

flatpak build-bundle "$PKG_DIR/repo" "$PKG_DIR/Desktop-Cat.flatpak" \
    io.github.gavvahar.DesktopCat

echo "Built: $PKG_DIR/Desktop-Cat.flatpak"
