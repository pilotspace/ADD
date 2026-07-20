#!/usr/bin/env python3
"""Behavioral proof of `add.py migrate` — the one-shot 1.x -> 2.0 board conversion
(ADD 2.0 M6, task migrate-verb).

CONTRACT:
  - renames every task doc TASK.md -> PLAN.md: live (.add/tasks/<slug>/) AND
    archived (.add/archive/<ms>/tasks/<slug>/), byte-preserving the content;
  - seeds any missing living 5-DD spec under .add/specs/ (never clobbers one);
  - idempotent: a second run is a loud no-op ("already 2.0"), exit 0;
  - a slug carrying BOTH TASK.md and PLAN.md refuses (migrate_conflict) BEFORE
    any rename — validate-all-then-write, tree byte-unchanged.
One test per scenario. Run: python3 -m unittest test_migrate_verb -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class MigrateVerbTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-migrate-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = self.tmp / ".add"

    def tearDown(self):
        os.chdir(self._cwd)

    def _age_to_1x(self, slug):
        """Shape a task dir like a 1.x board: doc named TASK.md."""
        d = self.root / "tasks" / slug
        (d / "PLAN.md").rename(d / "TASK.md")
        return d

    def test_renames_live_and_archived_docs(self):
        add.main(["new-task", "t", "--title", "F"])
        d = self._age_to_1x("t")
        body = (d / "TASK.md").read_bytes()
        arch = self.root / "archive" / "v0" / "tasks" / "old"
        arch.mkdir(parents=True)
        (arch / "TASK.md").write_text("# PLAN: old\n", encoding="utf-8")
        code, out, err = _run(["migrate"])
        self.assertEqual(code, 0, err)
        self.assertFalse((d / "TASK.md").exists())
        self.assertEqual((d / "PLAN.md").read_bytes(), body, "content byte-preserved")
        self.assertTrue((arch / "PLAN.md").exists(), "archived docs migrate too")
        self.assertIn("2 task doc(s)", out)

    def test_seeds_missing_specs_never_clobbers(self):
        marker = "## Deltas (newest first)\n- [open · 2026-01-01] keep me\n"
        (self.root / "specs" / "domain.md").write_text(marker, encoding="utf-8")
        (self.root / "specs" / "system.md").unlink()
        code, out, _ = _run(["migrate"])
        self.assertEqual(code, 0)
        self.assertIn("seeded 1 living spec(s): system.md", out)
        self.assertEqual((self.root / "specs" / "domain.md").read_text(encoding="utf-8"),
                         marker, "an existing spec is never clobbered")

    def test_idempotent_second_run_noop(self):
        code, out, _ = _run(["migrate"])
        self.assertEqual(code, 0)
        self.assertIn("already 2.0", out)
        before = sorted(p.name for p in (self.root / "tasks").rglob("*"))
        code2, out2, _ = _run(["migrate"])
        self.assertEqual(code2, 0)
        self.assertIn("already 2.0", out2)
        self.assertEqual(sorted(p.name for p in (self.root / "tasks").rglob("*")), before)

    def test_conflict_refuses_before_any_rename(self):
        add.main(["new-task", "a", "--title", "A"])
        add.main(["new-task", "b", "--title", "B"])
        self._age_to_1x("a")                                  # a: TASK.md (renameable)
        db = self.root / "tasks" / "b"
        (db / "TASK.md").write_text("stray twin", encoding="utf-8")  # b: BOTH docs
        code, out, err = _run(["migrate"])
        self.assertNotEqual(code, 0)
        self.assertIn("migrate_conflict", out + err)
        self.assertIn("b", out + err, "the refusal names the conflicted slug")
        self.assertTrue((self.root / "tasks" / "a" / "TASK.md").exists(),
                        "validate-all-then-write: the renameable doc was NOT renamed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
