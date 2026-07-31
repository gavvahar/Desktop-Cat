# Desktop-Cat

A free, open-source pixel-cat desktop companion, built with PySide6.
See [desktop_cat_plan.md](desktop_cat_plan.md) for the full build plan.

Currently implemented: **Phase 0** (transparent always-on-top window, click-through
mask, procedural drawing, eye-follow, drag, keyboard stub), **Phase 1**
(mouse-hunt, pet-to-purr, eased eye-follow, idle blink), and **Phase 2**
(mochi drag squash/stretch/wobble, gravity to rest on the screen bottom).

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
