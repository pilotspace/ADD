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
        r = _run(cls.root, "new-task", "hint-probe", "--fast", "--title", "probe")
        assert r.returncode == 0, r.stderr + r.stdout

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _footer(self):
        r = _run(self.root, "status", "--brief")
        return (r.stdout + r.stderr)

    def test_walk_phases_fill_then_bare(self):
        # ONE ordered walk (no cross-test ordering dependency). advance-chain-collapse:
        # the front drafting phases {ground,specify,scenarios} teach the COLLAPSED
        # `advance --to contract` while keeping the per-section `--fill` alt; `contract`
        # points at the freeze gate (not another advance); `tests` keeps the bare --fill.
        for expect_phase in ("ground", "specify", "scenarios", "contract", "tests"):
            out = self._footer()
            if expect_phase in ("ground", "specify", "scenarios"):
                self.assertIn("add.py advance --to contract", out,
                              f"{expect_phase} footer must teach the collapse:\n{out}")
                self.assertIn("add.py advance --fill <draft>", out,
                              f"{expect_phase} footer must keep the --fill alt:\n{out}")
            elif expect_phase == "contract":
                self.assertIn("add.py freeze", out,
                              f"contract footer must point at the freeze gate:\n{out}")
                self.assertNotIn("--to", out,
                                 f"contract footer must not name a --to:\n{out}")
            else:  # tests
                self.assertIn("add.py advance --fill <draft>", out,
                              f"{expect_phase} footer must teach the batch form:\n{out}")
            _run(self.root, "advance")
        # tests->build is guarded (red suite / expectations) — the walk cannot cheaply
        # reach build, so the bare-branch is pinned in the composer source instead:
        src = ADD_PY.read_text()
        branch = src.split('elif phase == "tests"', 1)[1]
        self.assertIn('command = "add.py advance --fill <draft>"', branch,
                      "the tests phase keeps the per-section --fill hint")


if __name__ == "__main__":
    unittest.main(verbosity=2)
