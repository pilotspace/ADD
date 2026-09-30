#!/usr/bin/env python3
"""prepare_bundle.py — regenerate src/add_method/_bundled/ from the canonical trees.

This script is the single source of truth for what ships in the Python package.
Run it whenever skill/, personas/, personas-teacher/ or personas-index/ change:

    python3 scripts/prepare_bundle.py

The output directory (src/add_method/_bundled/) is COMMITTED to the repo so that
`python -m build` needs no network or special tooling — it just zips what is there.
The parity guard (tests/test_npm_pip_parity.py::test_the_pip_bundle_mirrors_the_npm_payload)
ensures it never drifts from what npm ships.

What is copied:
  skill/add/              -> _bundled/skill/add/        (the method, incl. persona-author)
  personas/               -> _bundled/personas/         (starter personas, seeded never-overwrite)
  personas-teacher/       -> _bundled/personas-teacher/   (vendored teacher snapshot)
  personas-index/         -> _bundled/personas-index/     (its generated routing sidecar)
  ../THIRD_PARTY_NOTICES.md -> ./THIRD_PARTY_NOTICES.md + _bundled/THIRD_PARTY_NOTICES.md

ADD 4.0 ships no engine: a leftover _bundled/tooling/ or _bundled/agents/ is removed.

What is explicitly EXCLUDED:
  **/__pycache__/, *.pyc  (bytecode; never ship)
  **/.DS_Store            (OS noise)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent       # add-method/ (the package root)
BUNDLE_ROOT = REPO_ROOT / "src" / "add_method" / "_bundled"

SKILL_SRC = REPO_ROOT / "skill" / "add"
PERSONAS_SRC = REPO_ROOT / "personas"                    # starter personas (ours)
TEACHER_SRC = REPO_ROOT / "personas-teacher"             # vendored teacher snapshot (verbatim)
INDEX_SRC = REPO_ROOT / "personas-index"                 # its routing sidecar tree (generated, ours)
# THIRD_PARTY_NOTICES.md is a repo-LEVEL legal doc; its canonical lives one level up,
# outside the package root, so it is propagated INTO both package roots as parity-guarded
# twins (test_bundle_teacher.AttributionShipsBothTest asserts byte-identity).
NOTICES_CANON = REPO_ROOT.parent / "THIRD_PARTY_NOTICES.md"
NOTICES_NPM = REPO_ROOT / "THIRD_PARTY_NOTICES.md"       # npm ships from the package root


def _rm(p: Path) -> None:
    if p.exists():
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


def _copy_tree(src: Path, dest: Path) -> None:
    """Copy src -> dest, excluding OS junk and bytecode."""
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
        return excluded

    _rm(dest)
    shutil.copytree(str(src), str(dest), ignore=ignore)


def main() -> None:
    print(f"Regenerating bundle at {BUNDLE_ROOT}")

    # 1. skill
    skill_dest = BUNDLE_ROOT / "skill" / "add"
    _copy_tree(SKILL_SRC, skill_dest)
    print(f"  copied skill/add  ({len(list(skill_dest.rglob('*')))} items)")

    # 2. personas/ — the starter personas the installer seeds into .add/personas/
    personas_dest = BUNDLE_ROOT / "personas"
    _copy_tree(PERSONAS_SRC, personas_dest)
    print(f"  copied personas/  ({len(list(personas_dest.rglob('*')))} items)")

    # 2b. 4.0 ships no engine and no agent roster — drop any 3.x leftovers from the bundle.
    for retired in ("tooling", "agents"):
        _rm(BUNDLE_ROOT / retired)

    # 3. personas-teacher/  (vendored teacher snapshot — verbatim, no test/junk strip needed
    #    since it carries none; ship it whole so the persona phase reads it off-build)
    teacher_dest = BUNDLE_ROOT / "personas-teacher"
    _copy_tree(TEACHER_SRC, teacher_dest)
    print(f"  copied personas-teacher/  ({len(list(teacher_dest.rglob('*')))} items)")

    # 3b. personas-index/ — the routing sidecar. It lives BESIDE the snapshot, never inside it:
    #     update_teacher.py replaces personas-teacher/ wholesale, so an in-tree index would be
    #     erased on the next refresh. The installer copies it into .add/personas-index/.
    if not INDEX_SRC.is_dir():
        print(f"error: missing {INDEX_SRC} — run scripts/build_persona_index.py", file=sys.stderr)
        sys.exit(1)
    index_dest = BUNDLE_ROOT / "personas-index"
    _copy_tree(INDEX_SRC, index_dest)
    print(f"  copied personas-index/  ({len(list(index_dest.rglob('*')))} items)")

    # 4. THIRD_PARTY_NOTICES.md — propagate the repo-level MIT attribution into BOTH
    #    package roots (npm root + the pip bundle) as byte-identical twins of the canonical.
    if not NOTICES_CANON.exists():
        print(f"error: missing {NOTICES_CANON}", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(str(NOTICES_CANON), str(NOTICES_NPM))
    shutil.copy2(str(NOTICES_CANON), str(BUNDLE_ROOT / "THIRD_PARTY_NOTICES.md"))
    print("  propagated THIRD_PARTY_NOTICES.md -> package root + bundle")

    print("Bundle ready. Run `python3 -m pytest -q tests/test_npm_pip_parity.py` to verify.")


if __name__ == "__main__":
    main()
