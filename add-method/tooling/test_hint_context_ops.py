#!/usr/bin/env python3
"""engine-hint-context-ops: the full-`status` resume block teaches the cheap
context ops (`status --section <phase>` · `status --brief`) at the moment of
use, instead of instructing a whole-PLAN.md read every re-orient.

Post-hint wm1 census: advance --fill ×12 adopted, --brief/--section still 0 —
nothing in the engine's own output named them. Same fix shape as
engine-hint-batch-ops (validated −29%).

Run:
    python3 -m unittest test_hint_context_ops -v
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"


def _run(cwd, *args):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120)


class ResumeTeachesContextOps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = cls._tmp.name
        r = _run(cls.root, "init", "--name", "ctx", "--stage", "mvp")
        assert r.returncode == 0, r.stderr + r.stdout
        r = _run(cls.root, "new-task", "ctx-probe", "--fast", "--title", "probe")
        assert r.returncode == 0, r.stderr + r.stdout

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_resume_names_section_and_brief(self):
        out = _run(self.root, "status").stdout
        resume = out.split("resume", 1)[1]
        self.assertIn("status --section direction", resume,
                      f"resume must teach the per-section read:\n{out}")
        self.assertIn("status --brief", resume,
                      f"resume must teach the cheap re-orient:\n{out}")

    def test_whole_file_read_is_no_longer_the_first_action(self):
        out = _run(self.root, "status").stdout
        resume = out.split("resume", 1)[1]
        self.assertNotIn("read .add/tasks/ctx-probe/PLAN.md and continue", resume,
                         "the old whole-file instruction must be replaced")

    def test_done_branch_unchanged_shape(self):
        src = ADD_PY.read_text()
        self.assertIn('print(f"\\nresume  : task \'{active}\' is done', src,
                      "done-task resume branch must keep its existing rendering")


if __name__ == "__main__":
    unittest.main(verbosity=2)
