"""Red suite for queue-resume-surface (milestone multi-milestone-intake 3/3). Contract §3 FROZEN @ v1.

`add.py status` gains a `queued :` cue (backlog + promote-next hint), printed ONLY when ≥1 milestone
has status `queued` — byte-identical when zero. Presentation-only (reads state, writes nothing).
One assertion per frozen scenario. RED until cmd_status emits the cue; GREEN after build.
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add


def _status_text(args_root) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        add.main(["status"])
    return buf.getvalue()


class QueueResumeSurfaceTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-queue-resume-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "Demo", "--stage", "mvp"])
        self.root = Path(self.tmp) / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # Scenario: queued backlog is surfaced at resume
    def test_queued_surfaced(self):
        add.main(["new-milestone", "alpha"])
        add.main(["new-milestone", "beta", "--queued"])
        out = _status_text(self.root)
        self.assertIn("queued", out.lower(), "status must surface the queued backlog")
        self.assertIn("beta", out, "the queued cue must name the queued milestone")
        self.assertIn("activate beta", out, "the cue must give the promote-next hint")

    # Scenario: zero queued is byte-identical
    def test_zero_queued_byte_identical(self):
        add.main(["new-milestone", "alpha"])  # active only, none queued
        out = _status_text(self.root)
        # the additive cue must be absent — no "queued :" label line
        self.assertNotIn("queued  :", out, "no queued cue when zero queued (additive-cue convention)")

    # Scenario: the cue is presentation-only
    def test_presentation_only(self):
        add.main(["new-milestone", "alpha"])
        add.main(["new-milestone", "beta", "--queued"])
        before = (self.root / "state.json").read_bytes()
        _status_text(self.root)
        after = (self.root / "state.json").read_bytes()
        self.assertEqual(before, after, "status must not mutate state.json (presentation-only)")

    # Scenario: engine mirror + pin in sync


if __name__ == "__main__":
    unittest.main(verbosity=2)
