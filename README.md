# Desktop-Cat

A free, open-source pixel-cat desktop companion, built with PySide6.
See [desktop_cat_plan.md](desktop_cat_plan.md) for the full build plan.

Currently implemented: **Phase 0** (transparent always-on-top window, click-through
mask, procedural drawing, eye-follow, drag, keyboard stub), **Phase 1**
(mouse-hunt, pet-to-purr, eased eye-follow, idle blink), **Phase 2**
(mochi drag squash/stretch/wobble, gravity to rest on the screen bottom),
**Phase 3** (kneading paw animation on keypress, overheat red tint + steam
particles on sustained fast typing), **Phase 4** (paper scroll that
unspools while scrolling and re-rolls once you stop), and **Phase 5**
(stretch/water/Pomodoro/custom reminders and a pinned message, all shown in
a floating bubble above the cat; configured via
`~/.config/desktopcat/config.json`).

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

## Windows: standalone .exe

If you'd rather not `pip install` anything, `packaging/windows/build.ps1`
builds a single portable `desktop-cat.exe` (PyInstaller `--onefile`) --
download-and-run, no Python setup needed. This is the Windows equivalent of
the Linux AppImage below; there's no cross-platform way to build it, so it
has to be built (or downloaded prebuilt, once uploaded to a release) on an
actual Windows machine.

Build it yourself, from a native (non-WSL) PowerShell in the repo root:

```
.\packaging\windows\build.ps1
```

This installs PyInstaller, then produces
`packaging\windows\dist\desktop-cat.exe`. Only the source files
(`build.ps1`, `desktop-cat.ico`) are tracked in git; `build/`, `dist/`, and
the generated `.spec` are gitignored.

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
