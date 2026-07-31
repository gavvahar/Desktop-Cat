# Desktop-Cat

A free, open-source pixel-cat desktop companion, built with PySide6.
See [desktop_cat_plan.md](desktop_cat_plan.md) for the full build plan.

Currently implemented: **Phase 0** (transparent always-on-top window, click-through
mask, procedural drawing, eye-follow, drag, keyboard stub) and **Phase 1**
(mouse-hunt, pet-to-purr, eased eye-follow, idle blink).

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
