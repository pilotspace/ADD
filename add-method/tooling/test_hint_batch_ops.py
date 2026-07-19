#!/usr/bin/env python3
"""engine-hint-batch-ops: the `next:` footer teaches `advance --fill` at the
moment of use. Enforced-rerun census: 208 engine calls, ZERO uses of the batch
ops — they exist but are undiscoverable. The footer is the one line every turn
reads, so the drafting phases advertise the batch form there.

Run:
    python3 -m unittest test_hint_batch_ops -v
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


class FooterTeachesBatchForm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = cls._tmp.name
        r = _run(cls.root, "init", "--name", "hint", "--stage", "mvp")
        assert r.returncode == 0, r.stderr + r.stdout
        r = _run(cls.root, "new-task", "hint-probe", "--title", "probe")
        assert r.returncode == 0, r.stderr + r.stdout

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _footer(self):
        r = _run(self.root, "status", "--brief")
        return (r.stdout + r.stderr)

    def test_walk_phases_fill_then_bare(self):
        # phase-collapse-3: the front is ONE direction span — the footer teaches the
        # 3-call walk's one approval (`freeze --by <name> --cross`), never a `--to`
        # bundle step, and the frozen/unfrozen fork is pinned in the ONE
        # _next_command composer source (status-guide-fold) all three surfaces reuse.
        out = self._footer()
        self.assertIn("add.py freeze --by <name> --cross", out,
                      f"direction footer must teach the one-approval crossing:\n{out}")
        self.assertNotIn("--to", out,
                         f"direction footer must not name a --to:\n{out}")
        src = ADD_PY.read_text()
        composer = src.split("def _next_command", 1)[1].split("def _next_footer", 1)[0]
        self.assertIn('if phase == "direction":', composer)
        self.assertIn('return ("add.py advance" if contract_frozen', composer,
                      "the direction branch distinguishes a frozen §3 from an unfrozen one")


if __name__ == "__main__":
    unittest.main(verbosity=2)
