#!/usr/bin/env python3
"""persona-nudge-quiet: the unseeded persona hint fires at discovery seams
(init · new-milestone · idle status), never on every active-task status.

Benchmark evidence: the hint printed 20-30x per milestone run; agents
deliberated it 65-93x and wrote 0 persona files — pure context noise.

Run:
    python3 -m unittest test_persona_nudge_quiet -v
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"

NAG = "no project-fit persona"


def _run(cwd, *args):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120)


class PersonaNudgeSeams(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        r = _run(self.root, "init", "--name", "pq", "--stage", "mvp")
        assert r.returncode == 0, r.stderr + r.stdout

    def tearDown(self):
        self._tmp.cleanup()

    def test_idle_status_still_nudges(self):
        # the discovery nudge fires on an EMPTY roster; init now seeds the method
        # personas, so clear them to reach that state (behaviour under test unchanged).
        for _f in (Path(self.root) / '.add' / 'personas').glob('*.md'):
            _f.unlink()
        out = _run(self.root, "status").stdout
        self.assertIn(NAG, out, "idle (no active task) status keeps the discovery nudge")

    def test_active_task_status_is_quiet(self):
        _run(self.root, "new-task", "probe", "--title", "t")
        out = _run(self.root, "status").stdout
        self.assertNotIn(NAG, out,
                         "an active task's status must not re-advertise personas every turn")

    def test_new_milestone_nudge_unchanged(self):
        # the discovery nudge fires on an EMPTY roster; init now seeds the method
        # personas, so clear them to reach that state (behaviour under test unchanged).
        for _f in (Path(self.root) / '.add' / 'personas').glob('*.md'):
            _f.unlink()
        out = _run(self.root, "new-milestone", "mvp", "--goal", "g", "--stage", "mvp").stdout
        self.assertIn(NAG, out, "new-milestone keeps its discovery nudge")


if __name__ == "__main__":
    unittest.main(verbosity=2)
