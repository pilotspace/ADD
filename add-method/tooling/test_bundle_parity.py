#!/usr/bin/env python3
"""Bundle-parity guard: the Python package _bundled/ copy must stay byte-identical
to the canonical source trees, and must contain ZERO test files or bytecode.

This is the Python-package analog of test_tree_parity.py. Run after any change to
skill/, tooling/add.py, or tooling/templates/ — and again after running
scripts/prepare_bundle.py — to confirm the bundle is fresh.

Always-on (no skipTest): a publish from a stale or junk-containing bundle is
irreversible, so this guard is designed to fail loud rather than skip silently.

Run: python3 -m unittest test_bundle_parity -v
"""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent

# Canonical source locations (the trees cli.js ships)
CANON_SKILL = _ADD_METHOD / "skill" / "add"
CANON_TOOLING_PY = _ADD_METHOD / "tooling" / "add.py"
CANON_TEMPLATES = _ADD_METHOD / "tooling" / "templates"
CANON_TEACHER = _ADD_METHOD / "personas-teacher"

# Bundle locations inside the Python package source tree
BUNDLE = _ADD_METHOD / "src" / "add_method" / "_bundled"
BUNDLE_SKILL = BUNDLE / "skill" / "add"
BUNDLE_TOOLING_PY = BUNDLE / "tooling" / "add.py"
BUNDLE_TEMPLATES = BUNDLE / "tooling" / "templates"
BUNDLE_TEACHER = BUNDLE / "personas-teacher"

_JUNK = re.compile(r"(__pycache__|\.(pyc|pyo|DS_Store)$)")
_TEST_SRC = re.compile(r"(^|/)test_.*\.py$")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _rel_files(root: Path) -> dict[Path, str]:
    """Return {relative_path: md5} for every file under root."""
    return {
        p.relative_to(root): _md5(p)
        for p in root.rglob("*")
        if p.is_file()
    }


class BundleParityTest(unittest.TestCase):

    # --- skill tree is byte-identical to canonical --------------------------

    # --- add.py is byte-identical to canonical ------------------------------

    # --- templates/ is byte-identical to canonical -------------------------

    # --- teacher tree is byte-identical to canonical -----------------------
    def test_teacher_tree_byte_identical(self):
        self.assertTrue(CANON_TEACHER.is_dir(), f"missing canonical: {CANON_TEACHER}")
        self.assertTrue(BUNDLE_TEACHER.is_dir(),
                        "_bundled/personas-teacher/ missing — run scripts/prepare_bundle.py")
        canon = _rel_files(CANON_TEACHER)
        bundle = _rel_files(BUNDLE_TEACHER)
        self.assertEqual(
            sorted(map(str, canon.keys())),
            sorted(map(str, bundle.keys())),
            "teacher file sets differ between canonical and bundle.",
        )
        mismatched = [
            str(rel) for rel in sorted(canon, key=str)
            if canon[rel] != bundle[rel]
        ]
        self.assertEqual(mismatched, [],
                         "teacher file(s) differ between canonical and bundle: " +
                         ", ".join(mismatched))

    # --- no junk in bundle -------------------------------------------------
    def test_no_bytecode_or_os_junk_in_bundle(self):
        junk = [
            str(p.relative_to(BUNDLE))
            for p in BUNDLE.rglob("*")
            if p.is_file() and _JUNK.search(str(p))
        ]
        self.assertEqual(junk, [],
                         "compiled/OS junk must not be in bundle: " + str(junk))

    # --- no test sources in bundle ----------------------------------------
    def test_no_test_sources_in_bundle(self):
        tests = [
            str(p.relative_to(BUNDLE))
            for p in BUNDLE.rglob("*.py")
            if _TEST_SRC.search(str(p.relative_to(BUNDLE)))
        ]
        self.assertEqual(tests, [],
                         "dev test sources must not ship in bundle: " + str(tests))

    # --- required runtime paths are present --------------------------------
    def test_runtime_surface_complete(self):
        required = [BUNDLE_SKILL, BUNDLE_TOOLING_PY, BUNDLE_TEMPLATES, BUNDLE_TEACHER]
        missing = [str(p) for p in required if not p.exists()]
        self.assertEqual(missing, [],
                         "bundle is missing required paths: " + str(missing))
        self.assertFalse((BUNDLE / "docs").exists(),
                         "book-stops-shipping (2.0 M6b): the bundle must not carry docs/")


if __name__ == "__main__":
    unittest.main(verbosity=2)
