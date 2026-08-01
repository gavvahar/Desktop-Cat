# Desktop-Cat

A free, open-source pixel-cat desktop companion, built with PySide6.
See [desktop_cat_plan.md](desktop_cat_plan.md) for the full build plan.

Currently implemented: **Phase 0** (transparent always-on-top window, click-through
mask, procedural drawing, eye-follow, drag, keyboard stub), **Phase 1**
(mouse-hunt, pet-to-purr, eased eye-follow, idle blink), **Phase 2**
(mochi drag squash/stretch/wobble, gravity to rest on the screen bottom),
**Phase 3** (kneading paw animation on keypress, overheat red tint + steam
particles on sustained fast typing), **Phase 4** (paper scroll that
unspools while scrolling and re-rolls once you stop), **Phase 5**
(stretch/water/Pomodoro/custom reminders and a pinned message, all shown in
a floating bubble above the cat), **Phase 6** (custom fur color +
optional tabby pattern, a name used in reminders, and a right-click
Settings window -- all persisted to `~/.config/desktopcat/config.json`), and
**Phase 7** (peek mode: slides to the screen edge and mutes reactions when
a fullscreen window is active, X11-only best-effort; and best-effort
"AI-agent" hooks -- a little thinking-along animation while a known AI
coding tool process is running, and a done-jump when it exits), and most
of **Phase 8** (autostart at login, toggled from Settings; MIT-licensed).
Original sprite art is the one thing left undone -- the app stays
asset-free procedural (QPainter) until someone draws or commissions it.

Right-click the cat for Settings / Quit.

**Just want to install it?** See [INSTALL.md](INSTALL.md) for
download-and-run instructions on every platform. Everything below this
point is about building from source.

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

## Windows: standalone build

If you'd rather not `pip install` anything, `packaging/windows/build.ps1`
builds a portable `desktop-cat` folder -- no Python setup needed. This is
the Windows equivalent of the Linux AppImage below; there's no
cross-platform way to build it, so it has to be built (or downloaded
prebuilt -- see [INSTALL.md](INSTALL.md)) on an actual Windows machine.

**Why a zip of a folder instead of a single .exe:** it used to be a single
PyInstaller `--onefile` executable, but that got flagged by Windows
Defender as "virus detected" -- a well-known, common false positive for
PyInstaller onefile builds specifically. Onefile mode works by
self-extracting to a temp folder and running from there on every launch,
which is exactly the behavioral pattern malware droppers have, so
heuristic/cloud-reputation antivirus engines flag it constantly, even
when it's completely benign. Combined with being unsigned (no Apple/
Microsoft developer certificate involved in this project) and a brand-new
file hash Windows has never seen before, that's a near-guaranteed flag.
Switching to PyInstaller's default `--onedir` mode (a plain folder, no
runtime self-extraction) avoids that specific behavioral trigger. If
Defender or SmartScreen still complains, right-click -> Properties ->
Unblock, or "More info" -> "Run anyway".

Build it yourself, from a native (non-WSL) PowerShell in the repo root:

```
.\packaging\windows\build.ps1
```

This installs PyInstaller, then produces
`packaging\windows\dist\desktop-cat\desktop-cat.exe`, zipped as
`packaging\windows\dist\Desktop-Cat-windows.zip`. Only the source files
(`build.ps1`, `desktop-cat.ico`) are tracked in git; `build/`, `dist/`, and
the generated `.spec` are gitignored.

## Linux: AppImage

See [INSTALL.md](INSTALL.md) for downloading and running a prebuilt one.
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

## Linux: Flatpak

`packaging/flatpak/io.github.gavvahar.DesktopCat.yml` is a full Flatpak
manifest. It's built by `.github/workflows/release.yml` on a real Linux CI
runner via the standard
[flatpak-github-actions](https://github.com/flatpak/flatpak-github-actions)
action (build succeeding there is how every release's `Desktop-Cat.flatpak`
gets made) -- it hasn't been built locally, since `flatpak-builder` needs a
`sudo` install plus multi-GB runtime downloads that weren't practical in
the environment this was originally written in. See
[INSTALL.md](INSTALL.md) for the `flatpak install` command.

A few things worth knowing:

- Runtime is `org.freedesktop.Platform`, not a KDE/Qt runtime -- PySide6's
  wheels bundle their own Qt, so a Qt-flavored runtime would just mean two
  copies of Qt on disk.
- Dependency wheels are pinned by URL + sha256 directly in the manifest,
  since Flatpak builds run offline and need every source pre-declared.
  `pynput` is installed with `--no-deps` plus explicit `python-xlib`/`six`,
  deliberately excluding its `evdev` dependency (the Wayland-fallback
  backend) -- this build only grants X11 access, not raw `/dev/input`
  access, so evdev couldn't do anything here even if it built, and its
  `pyproject.toml` doesn't build cleanly against modern setuptools anyway
  (an old-style `license = "BSD-3-Clause"` string fails PEP 621
  validation).
- Needs `--socket=x11` specifically (not just the more sandboxed
  `--socket=fallback-x11`) for `pynput`'s global keyboard/mouse capture to
  work at all; under pure Wayland without that, those reactions fail to
  start the same way they do everywhere else in this app -- see the plan's
  "hard parts" note on Wayland restricting global input.
- `--filesystem` grants match this app's actual file I/O:
  `~/.config/desktopcat/config.json` and `~/.config/autostart/desktopcat.desktop`
  (the latter is how `autostart.py` implements autostart on Linux --
  a stricter Flatpak citizen would use the Background portal instead).

To build it yourself once you have `flatpak` + `flatpak-builder` +
the `org.freedesktop.Platform`/`Sdk`//23.08 runtimes installed:

```
bash packaging/flatpak/build.sh
```

## macOS: .app bundle (unverified -- see caveats)

**Nothing about macOS has been tested on real hardware.** Everything below
is reasoned through and, where possible, built by CI on GitHub's hosted
`macos-latest` runner (so at least the _packaging step_ is verified to
succeed) -- but actually running/using the app on a Mac has not been
confirmed by anyone yet. Two known gaps:

- **Peek mode doesn't work on macOS.** It's implemented via X11 window
  properties (`python-xlib`), and there's no X server on macOS. It fails
  safely -- the feature just never triggers -- rather than crashing.
- `pynput`'s keyboard/scroll listeners need the app to be granted
  **Accessibility permission** (System Settings -> Privacy & Security ->
  Accessibility) before they'll receive any events. Without it, those
  reactions silently do nothing (same graceful-disable behavior as any
  other listener failure).

See [INSTALL.md](INSTALL.md) for downloading and running a prebuilt one
(including the Gatekeeper right-click-Open step). To build it yourself
(must be run **on** macOS -- PyInstaller can't cross-compile):

```
bash packaging/macos/build.sh
```

This produces `packaging/macos/dist/Desktop Cat.app`, zipped as
`packaging/macos/dist/Desktop-Cat-macos.zip`. Only the source files
(`build.sh`, `desktop-cat.icns`) are tracked in git.
