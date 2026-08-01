# Desktop-Cat

A free, open-source pixel-cat desktop companion, built with PySide6.
See [desktop_cat_plan.md](desktop_cat_plan.md) for the full build plan.

Currently implemented: **Phase 0** (transparent always-on-top window, click-through
mask, procedural drawing, eye-follow, drag, keyboard stub), **Phase 1**
(mouse-hunt, pet-to-purr, eased eye-follow, idle blink), **Phase 2**
(mochi drag squash/stretch/wobble, gravity to rest on the screen bottom),
**Phase 3** (kneading paw animation on keypress, overheat red tint + steam
particles on sustained fast typing), and **Phase 4** (paper scroll that
unspools while scrolling and re-rolls once you stop).

## Code style note

No custom classes are used in the Python files. The one exception is
`CatWindow` in `Python/desktopcat/window.py`, which PySide6 requires to be a
`QWidget` subclass in order to override `paintEvent`/mouse events -- it holds
no logic of its own and immediately delegates to plain functions. All other
state and behavior live in module-level dicts and functions.

## Setup

Dependencies are listed in `requirements.txt`. Install them into your own
environment (conda/venv/etc), e.g.:

```
pip install -r requirements.txt
```

## Run

From the repo root:

```
python -m desktopcat.main
```

with `Python/` on your `PYTHONPATH` (e.g. `PYTHONPATH=Python python -m desktopcat.main`),
or `cd Python && python -m desktopcat.main`.

## Running natively on Windows (not WSL)

The app is plain PySide6 + pynput with no Linux-specific code (the one
platform check, in `window.py`, safely no-ops on Windows), so it should run
unmodified with a native Windows Python install. This is also the better
way to test cursor/keyboard reactions: **if you're running this inside
WSL/WSLg, global cursor tracking only works while the pointer is directly
over the cat's own window** -- WSLg forwards windows individually over RDP
rather than exposing the real Windows desktop, so `QCursor.pos()` never
sees the cursor anywhere else and reactions like mouse-hunt/pet-to-purr
won't trigger from elsewhere on screen. A native Windows install doesn't
have that restriction; `pynput` also skips the Linux-only `evdev`
dependency there entirely (native Win32 hooks instead), so there's no
compiler/kernel-headers setup needed either.

Verified working end-to-end on real Windows: PySide6/pynput install and
import cleanly, the app launches, and `QCursor.pos()` genuinely tracks the
mouse across the whole desktop (unlike the WSLg restriction above).

**Install** (from a regular, non-WSL PowerShell, in the repo root):

```
.\install.ps1
```

**Run:**

```
.\run.ps1
```

If PowerShell blocks the scripts (`running scripts is disabled on this
system`), run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`,
or invoke directly with `powershell -ExecutionPolicy Bypass -File .\install.ps1`.

Equivalent by hand, without the scripts:

```
pip install -r requirements.txt
$env:PYTHONPATH = "Python"
python -m desktopcat.main
```

No network access is required or requested by the app.

## Linux: AppImage

Prebuilt `Desktop-Cat-x86_64.AppImage` releases are on the
[Releases page](https://github.com/gavvahar/Desktop-Cat/releases) -- download,
`chmod +x`, and run it, no install step needed.

To build it yourself from source:

```
bash packaging/appimage/build.sh
```

This installs PyInstaller, bundles the app and all its dependencies (PySide6,
pynput, etc.) into `packaging/appimage/dist/`, downloads `appimagetool` on
first run (cached in `packaging/appimage/.tools/`), and produces
`packaging/appimage/Desktop-Cat-x86_64.AppImage`. Only the source files
(`build.sh`, `AppRun`, `desktop-cat.desktop`, `desktop-cat.png`) are tracked
in git -- everything else the script generates is gitignored.
