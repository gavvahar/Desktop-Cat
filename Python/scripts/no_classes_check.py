#!/usr/bin/env python3
"""Pre-commit check that rejects Python class definitions in the codebase."""

import os, sys, ast

EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    "env",
    # Django migration files always require `class Migration(migrations.Migration):`
    # -- there's no functional-programming equivalent in Django's migration framework.
    "migrations",
}

# window.py: PySide6 requires subclassing QWidget to override paintEvent /
# mouse events -- there's no classless way to do that.
# models.py: Django's ORM requires subclassing models.Model, with fields as
# class attributes the metaclass turns into the DB table/manager -- there's
# no classless way to do that either.
EXCLUDE_FILES = {"test.py", "jc_api.py", "window.py", "models.py"}


def iter_py_files():
    """Yield paths to all Python files, skipping excluded directories and files."""
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".py") and f not in EXCLUDE_FILES:
                yield os.path.join(root, f)


def main():
    """Report class definitions found in the codebase and exit non-zero if any exist."""
    violations = []
    for path in iter_py_files():
        try:
            with open(path, "rb") as fh:
                tree = ast.parse(fh.read(), filename=path)
        except SyntaxError:
            # Skip files with syntax errors; flake8 will catch these anyway
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef):
                violations.append(f"{path}:{n.lineno}:{n.col_offset + 1}: class {n.name}")
    if violations:
        print("❌ Error: Class definitions found in the codebase!")
        print("\n".join(violations))
        sys.exit(1)
    print("✅ No classes found. All good!")


if __name__ == "__main__":
    main()
