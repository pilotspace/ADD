#!/usr/bin/env python3
"""Red/green tests for new-milestone-add-focus (multi-active-polish): `new-milestone` (non-queued)
PRESERVES the active SET — it ADDS the new milestone and makes it primary, instead of REPLACING
the set and evicting the others. `--queued` and single-active stay byte-identical. Run:
  python3 -m unittest test_new_milestone_add_focus -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-nmaf-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self.state = self.tmp / ".add" / "state.json"

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _st(self):
        return json.loads(self.state.read_text(encoding="utf-8"))


class PreserveTest(_Harness):
    def test_create_while_active_preserves_set(self):
        self._silent("new-milestone", "P", "--stage", "mvp")
        self._silent("new-milestone", "X", "--stage", "mvp")
        st = self._st()
        self.assertEqual(set(st["active_milestones"]), {"P", "X"})   # P NOT evicted
        self.assertEqual(st["active_milestone"], "X")                # X primary

    def test_fresh_milestone_repoints_active_task(self):
        self._silent("new-milestone", "P", "--stage", "mvp")
        self._silent("new-task", "t1", "--milestone", "P")          # t1 becomes the scalar active_task
        self.assertEqual(self._st()["active_task"], "t1")
        self._silent("new-milestone", "X", "--stage", "mvp")
        # X is fresh/taskless -> the scalar re-points to X's (None) entry, not P's dangling t1
        self.assertIsNone(self._st()["active_task"])

    def test_single_active_unchanged(self):
        self._silent("new-milestone", "X", "--stage", "mvp")
        st = self._st()
        self.assertEqual(st["active_milestones"], ["X"])
        self.assertEqual(st["active_milestone"], "X")

    def test_queued_leaves_set_untouched(self):
        self._silent("new-milestone", "P", "--stage", "mvp")
        self._silent("new-milestone", "X", "--stage", "mvp", "--queued")
        st = self._st()
        self.assertEqual(st["active_milestones"], ["P"])            # X queued, not active
        self.assertEqual(st["milestones"]["X"]["status"], "queued")

    def test_force_recreate_single_membership(self):
        self._silent("new-milestone", "X", "--stage", "mvp")
        self._silent("new-milestone", "X", "--stage", "mvp", "--force")
        st = self._st()
        self.assertEqual(st["active_milestones"].count("X"), 1)     # idempotent, no duplicate
        self.assertEqual(st["active_milestone"], "X")


if __name__ == "__main__":
    unittest.main(verbosity=2)
