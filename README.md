# Desktop-Cat

A free, open-source pixel-cat desktop companion, built with PySide6.
See [desktop_cat_plan.md](desktop_cat_plan.md) for the full build plan.

Currently implemented: **Phase 0** (transparent always-on-top window, click-through
mask, procedural drawing, eye-follow, drag, keyboard stub), **Phase 1**
(mouse-hunt, pet-to-purr, eased eye-follow, idle blink), **Phase 2**
(mochi drag squash/stretch/wobble, gravity to rest on the screen bottom), and
**Phase 3** (kneading paw animation on keypress, overheat red tint + steam
particles on sustained fast typing).

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

## Run with Docker / Podman

The cat is a GUI app, so the container needs access to your **host's X11
display** -- it doesn't bundle its own display server. This only works on
X11 (or XWayland); see the plan's "hard parts" note on Wayland restricting
global input. The commands below are identical for `docker` and `podman`
(swap the binary name); on some setups `docker` is itself provided by
`podman-docker`, in which case they're literally the same thing.

Build:

```
docker build -t desktop-cat .
```

Allow the container to connect to your X server, then run:

```
xhost +local:docker   # or +local:podman
docker run --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --ipc host \
  desktop-cat
xhost -local:docker   # revoke access when done
```

Or with Compose (`docker compose up --build` / `podman-compose up --build`),
using the included `compose.yml`.

**Notes**

- `xhost +local:docker` grants any local container access to your X server --
  narrower than `xhost +`, but still worth revoking (`xhost -local:docker`)
  when you're done. If that's too permissive for your taste, use an
  `XAUTHORITY`-cookie-based approach instead.
- Rootless Podman: if the X11 socket's permissions don't line up with the
  container's UID, add `--userns=keep-id`.
- The global keyboard "kneading" reaction needs the container to reach your
  X server the same way (already covered by the mounts above); it prints a
  warning and disables itself rather than crashing if it can't.
- No network access is required or requested by the app or image.
