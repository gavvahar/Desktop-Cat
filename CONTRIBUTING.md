# Contributing

## Setup

```
pip install -r requirements.txt
```

(or `conda env create -f enviroment.yml`, or use Docker/Podman -- see the
README's "Run with Docker / Podman" section). PySide6 apps need a real X11
display to run; see the README for details.

## Code style

- **No custom classes in Python files.** State lives in module-level dicts
  (`Python/desktopcat/state.py`); behavior is plain functions. The one
  exception is `Python/desktopcat/window.py`, which PySide6 requires to
  subclass `QWidget` in order to override `paintEvent`/mouse events -- it's
  allowlisted in `Python/scripts/no_classes_check.py`'s `EXCLUDE_FILES` and
  should stay pure Qt glue (no logic beyond one-line delegations into
  `input.py`/`render.py`).
- **One `import` line per file for bare `import x` statements** -- combine
  multiple into `import x, y, z`. `from x import y` is untouched. Enforced
  by `Python/scripts/combined_imports_check.py`; run it with `--fix` to
  auto-combine.
- Formatted/linted with `ruff` (line length 180, rules in `pyproject.toml`).
- Non-Python files (`.md`, `.json`, `.yml`, `.yaml`, `.css`, `.js`, `.html`)
  are formatted with `prettier`; `.toml` files with `taplo`.

## Running checks

Everything is wired through `tox` (env config lives in `pyproject.toml`
under `[tool.tox.*]`):

```
tox -e lint                    # ruff check
tox -e no-classes-check        # rejects any `class` definition outside EXCLUDE_FILES
tox -e combined-imports-check  # rejects multiple bare `import x` lines in one file
tox -e txt-lint                # textlint over *.txt (misspellings, weasel words)
tox -e prettier                # prettier --check
tox -e toml-lint                # taplo fmt --check + lint
tox -e format                  # auto-fixes everything above that can be auto-fixed
tox -e github                  # the full read-only chain CI runs
tox -e all                     # format, then the full github chain
```

Run `tox -e format` before pushing, then `tox -e github` to confirm
everything that CI checks is clean.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `perf:`, `chore:`, `lint:`),
optionally scoped (`feat(render): ...`). This isn't just a style
preference -- `pyproject.toml`'s `[tool.git-cliff.git]` commit_parsers use
these prefixes to group the changelog, and `.github/workflows/release.yml`
parses them to decide the next version bump on every push to `main`:

- `feat!:` / `BREAKING CHANGE:` footer -> major bump
- `feat:` -> minor bump
- anything else -> patch bump

A push to `main` that changes nothing release-worthy just won't tag; there's
no need to skip CI manually.

## CI

- `.github/workflows/tests.yml` ("Code Quality") runs `tox -e github` on
  every push and PR.
- `.github/workflows/release.yml` runs on push to `main`: computes the next
  semver tag from commit messages since the last release, generates release
  notes via `git-cliff` (falling back to `.github/scripts/gen_release_notes.py`
  for GitHub attribution lookups), and cuts a GitHub release.

## Testing GUI changes

There's no automated GUI test suite -- this is a PySide6 desktop overlay, so
after any change to `render.py`, `window.py`, or `input.py`, actually run it
against a real X11 display and check the behavior (mouse-hunt, pet-to-purr,
drag, click-through, etc.) before opening a PR.

## Pull requests

`CODEOWNERS` auto-requests review from `@gavvahar` on any change.
