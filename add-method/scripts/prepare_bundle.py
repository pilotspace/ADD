#!/usr/bin/env python3
"""prepare_bundle.py — regenerate src/add_method/_bundled/ from the canonical trees.

This script is the single source of truth for what ships in the Python package.
Run it whenever skill/, tooling/add.py, tooling/templates/, or docs/ change:

    python3 scripts/prepare_bundle.py

The output directory (src/add_method/_bundled/) is COMMITTED to the repo so that
`python -m build` needs no network or special tooling — it just zips what is there.
The parity guard (tooling/test_bundle_parity.py) ensures it never drifts.

What is copied:
  skill/add/              -> _bundled/skill/add/
  tooling/add.py          -> _bundled/tooling/add.py
  tooling/templates/      -> _bundled/tooling/templates/
  docs/                   -> _bundled/docs/

What is explicitly EXCLUDED (mirrors cli.js post-copy scrub):
  tooling/test_*.py       (dev-only; never ship to end users)
  **/__pycache__/, *.pyc  (bytecode; never ship)
  **/.DS_Store            (OS noise)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE_ROOT = REPO_ROOT / "src" / "add_method" / "_bundled"

SKILL_SRC = REPO_ROOT / "skill" / "add"
TOOLING_SRC = REPO_ROOT / "tooling"
DOCS_SRC = REPO_ROOT / "docs"


def _rm(p: Path) -> None:
    if p.exists():
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


def _copy_tree(src: Path, dest: Path, *, exclude_test_py: bool = False) -> None:
    """Copy src -> dest, excluding OS junk, bytecode, and optionally test sources."""
    if not src.exists():
        print(f"error: source does not exist: {src}", file=sys.stderr)
        sys.exit(1)

    def ignore(directory: str, contents: list[str]) -> set[str]:
        excluded: set[str] = set()
        for name in contents:
            if name in ("__pycache__", ".DS_Store"):
                excluded.add(name)
            elif name.endswith((".pyc", ".pyo")):
                excluded.add(name)
            elif exclude_test_py and name.startswith("test_") and name.endswith(".py"):
                excluded.add(name)
        return excluded

    _rm(dest)
    shutil.copytree(str(src), str(dest), ignore=ignore)


def main() -> None:
    print(f"Regenerating bundle at {BUNDLE_ROOT}")

    # 1. skill
    skill_dest = BUNDLE_ROOT / "skill" / "add"
    _copy_tree(SKILL_SRC, skill_dest)
    print(f"  copied skill/add  ({len(list(skill_dest.rglob('*')))} items)")

    # 2. tooling/add.py  +  tooling/templates/  (runtime only — no tests)
    tooling_dest = BUNDLE_ROOT / "tooling"
    _rm(tooling_dest)
    tooling_dest.mkdir(parents=True, exist_ok=True)
    add_py_src = TOOLING_SRC / "add.py"
    if not add_py_src.exists():
        print(f"error: {add_py_src} does not exist", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(str(add_py_src), str(tooling_dest / "add.py"))
    # the engine is a package now: ship tooling/add_engine/ (runtime modules; no tests)
    engine_pkg_src = TOOLING_SRC / "add_engine"
    if engine_pkg_src.is_dir():
        _copy_tree(engine_pkg_src, tooling_dest / "add_engine", exclude_test_py=True)
    _copy_tree(TOOLING_SRC / "templates", tooling_dest / "templates")
    print("  copied tooling/add.py + add_engine/ + templates/")

    # 3. docs/
    docs_dest = BUNDLE_ROOT / "docs"
    _copy_tree(DOCS_SRC, docs_dest)
    print(f"  copied docs/  ({len(list(docs_dest.rglob('*')))} items)")

    print("Bundle ready. Run `python3 -m unittest tooling.test_bundle_parity -v` to verify.")


if __name__ == "__main__":
    main()
