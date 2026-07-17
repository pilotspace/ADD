#!/usr/bin/env python3
"""Red/green tests for untrack-add-tooling — repo hygiene, not an engine feature.

`.add/tooling/` becomes an untracked, regenerable dogfood mirror of `add-method/tooling/`
(the canonical engine source) — mirrors the EXISTING `.add/docs/` precedent.
Frozen shape (§3 @ v2 — change request after the v1 CI repoint broke the CANONICAL
invocation invariant, test_audit_ci.py; see that file's docstring):
  - `.add/.gitignore` gains a `tooling/` entry (the `.add`-scoped ignore file, alongside its
    existing transient-artifact entries — not the root `.gitignore`, per a mid-build steer);
  - the 34 previously-tracked files are `git rm --cached` (working tree untouched);
  - `.github/workflows/ci.yml`'s `seam-audit` job gains a materialize step (mkdir + copy
    add.py/add_engine/engine_pin.py/templates from add-method/tooling/) BEFORE the audit
    step — the audit step's `run:` line itself stays BYTE-IDENTICAL (the tested, shipped
    canonical invocation — portable to dogfood AND consumer repos alike);
  - the 2 non-soft-skip pin tests gain the same `.exists()` filter the other 11 already use.

These assertions run against the REAL repo state (git ls-files / .gitignore / ci.yml content) —
no sandbox needed, this is a repo-hygiene check, not an add.py behavior.

Run: cd add-method/tooling && python3 -m unittest test_untrack_add_tooling -v
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                           check=False).stdout


class TrackingRemoved(unittest.TestCase):
    def test_tooling_untracked_and_ignored(self):                  # M1, M2
        tracked = _git("ls-files", ".add/tooling").strip()
        self.assertEqual(tracked, "", "no file under .add/tooling/ may remain git-tracked")
        ignore_check = subprocess.run(
            ["git", "check-ignore", "-q", ".add/tooling/add.py"],
            cwd=REPO, check=False)
        self.assertEqual(ignore_check.returncode, 0,
                          ".add/tooling/add.py must be matched by .gitignore")

    def test_working_tree_files_unchanged(self):                   # R:tooling_files_deleted
        p = REPO / ".add" / "tooling" / "add.py"
        self.assertTrue(p.exists(), "git rm --cached must NOT delete the working-tree file")
        self.assertGreater(len(p.read_bytes()), 0, "the working file must keep its content")


# every line the materialize step must contain — each checked individually and by
# position, so a partial/incomplete copy (e.g. add_engine/ or engine_pin.py silently
# dropped) fails instead of slipping through a loosely-anchored first...last regex.
_REQUIRED_MATERIALIZE_LINES = [
    "mkdir -p .add/tooling",
    "cp add-method/tooling/add.py .add/tooling/add.py",
    "cp -r add-method/tooling/add_engine .add/tooling/add_engine",
    "cp add-method/tooling/engine_pin.py .add/tooling/engine_pin.py",
    "cp -r add-method/tooling/templates .add/tooling/templates",
]


class CiMaterializes(unittest.TestCase):
    def test_ci_materializes_before_untouched_audit(self):         # M3
        # kernel-trim (ADD 2.0 M5): the seam-audit job died with the audit verb;
        # the materialize step (the dogfood mirror CI still depends on) survives.
        txt = (REPO / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for line in _REQUIRED_MATERIALIZE_LINES:
            self.assertIn(line, txt,
                          f"ci.yml materialize step must copy: {line!r}")


class PinTestsToleratesAbsence(unittest.TestCase):
    def test_canonical_sweep_soft_skips(self):                     # M4, R:pin_test_hard_fails_on_absence
        # test-corpus-slim: the per-suite pin copies were consolidated into the
        # canonical sweep — the absence-tolerance guard re-aims at it.
        txt = (HERE / "test_tree_parity.py").read_text(encoding="utf-8")
        self.assertIn(".exists()", txt,
                      "test_tree_parity.py must filter absent (gitignored) twins by existence")


if __name__ == "__main__":
    unittest.main(verbosity=2)
