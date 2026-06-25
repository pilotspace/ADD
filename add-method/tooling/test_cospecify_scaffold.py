#!/usr/bin/env python3
"""Regression guard: the new-task scaffold must emit the co-specification §1 shape.

This pins the surface that the docs-only reform could not reach on its own: a
real `add.py new-task` materializes `TASK.md` from `templates/TASK.md.tmpl` (or
the embedded `_FALLBACK_TASK` circuit breaker). Before co-specification this
section was a flat `Assumptions (confirm before building)` list — the very shape
that produced walls of pre-ticked `[x] confirmed` assumptions. These tests fail
if any future edit reverts the scaffold to that flat shape, so the reform cannot
silently regress to cosmetic-only.

Run: python3 -m unittest test_cospecify_scaffold -v
"""
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

OLD_FLAT_SHAPE = "Assumptions (confirm before building):"
OLD_EXIT = "zero open assumptions"
NEW_FRAMINGS = "Framings weighed:"
NEW_RANKED = "Assumptions — lowest-confidence first:"
FLAG_GLYPH = "⚠"


class CospecifyScaffoldTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-cospec-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    # --- the real end-to-end path that produced the smoking-gun TASK.md -------
    def test_new_task_scaffolds_cospecification_spec(self):
        add.main(["init"])
        add.main(["new-task", "demo", "--title", "Demo feature"])
        text = (Path(self.tmp) / ".add" / "tasks" / "demo" / "TASK.md").read_text(
            encoding="utf-8"
        )
        # new shape present
        self.assertIn(NEW_FRAMINGS, text, "scaffold must offer a Framings weighed: line")
        self.assertIn(NEW_RANKED, text, "scaffold must rank assumptions lowest-confidence first")
        self.assertIn(FLAG_GLYPH, text, "scaffold must carry the ⚠ lowest-confidence flag")
        # §3 freeze leads with the bundle-level flag (the one approval)
        self.assertIn("lowest-confidence flag", text, "freeze must lead with the bundle flag")
        # old shape gone — this is the assertion that was RED before the reform
        self.assertNotIn(OLD_FLAT_SHAPE, text, "flat confirm-list must not return")
        self.assertNotIn(OLD_EXIT, text, "the 'zero open assumptions' exit must not return")

    # --- the circuit-breaker fallback must not be a back-door to the old shape
    def test_fallback_task_carries_cospecification_shape(self):
        fb = add._FALLBACK_TASK
        self.assertIn(NEW_FRAMINGS, fb)
        self.assertIn(NEW_RANKED, fb)
        self.assertNotIn(OLD_FLAT_SHAPE, fb)

    # --- whole-class guard: no old-shape remnant survives in any method surface
    # Codifies the global grep that caught the scaffold/appendix/roles misses: the
    # docs-only reform must not leave the flat confirm-list model anywhere a reader
    # or agent would treat as current method. History (.add/tasks) and the gitignored
    # .add/docs mirror are excluded; test files may name the old strings to assert them.
    def test_no_old_shape_in_method_surfaces(self):
        root = Path(add.__file__).resolve().parents[2]  # .../AIDD-Book
        forbidden = (
            "Assumptions (confirm before building)",
            "zero open assumptions",
            "zero unconfirmed assumptions",
            "unconfirmed assumption",
            "all assumptions confirmed",
            "no open assumptions",
        )
        exts = {".md", ".py", ".tmpl"}
        exclude_frags = ("/.git/", "/node_modules/", "/.add/tasks/", "/.add/docs/", "/tmp/")
        scan_dirs = [root / "add-method", root / ".claude" / "skills" / "add"]
        files = []
        for d in scan_dirs:
            if d.exists():
                files += [p for p in d.rglob("*") if p.suffix in exts]
        files += list(root.glob("*.md"))  # the tracked book source also lives at repo root
        offenders = []
        for p in files:
            sp = str(p)
            if any(frag in sp for frag in exclude_frags):
                continue
            if p.name.startswith("test_") and p.suffix == ".py":
                continue  # tests may name the old strings to assert their absence
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for bad in forbidden:
                if bad in text:
                    offenders.append(f"{p.relative_to(root)} :: {bad!r}")
        self.assertEqual(
            offenders, [],
            "old-shape (flat confirm-list) remnants survive in method surfaces:\n  "
            + "\n  ".join(offenders),
        )

    # --- propagation discipline: the two tooling trees stay byte-identical ----
    def test_tooling_trees_byte_identical(self):
        root = Path(add.__file__).resolve().parents[2]  # .../AIDD-Book
        pairs = [
            ("add-method/tooling/templates/TASK.md.tmpl", ".add/tooling/templates/TASK.md.tmpl"),
            ("add-method/tooling/add.py", ".add/tooling/add.py"),
        ]
        for canon, dogfood in pairs:
            cb, db = (root / canon), (root / dogfood)
            if not db.exists():
                self.skipTest(f"dogfood mirror absent: {dogfood}")
            self.assertEqual(
                cb.read_bytes(), db.read_bytes(),
                f"tooling trees drifted: {canon} != {dogfood} — propagate with cp",
            )


if __name__ == "__main__":
    unittest.main()
