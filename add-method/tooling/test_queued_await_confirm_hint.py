"""Red suite for queued-await-confirm-hint (standalone fast lane). Contract §3 FROZEN @ v1.

`new-milestone --queued --await-confirm <slug>` must surface the `milestone-confirm` reminder
(the confirm gate is already recorded — make it visible). Additive-only: `--queued` alone is
byte-identical (no reminder). RED until the queued output branch prints the reminder.
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


class QueuedAwaitConfirmHintTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-qac-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "Demo", "--stage", "mvp"])
        self.root = Path(self.tmp) / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _new_ms_out(self, *flags) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["new-milestone", *flags])
        return buf.getvalue()

    # Accept: queued + await-confirm surfaces the milestone-confirm reminder
    def test_queued_await_confirm_shows_reminder(self):
        out = self._new_ms_out("beta", "--queued", "--await-confirm")
        self.assertIn("activate beta", out, "still shows the promote hint")
        self.assertIn("milestone-confirm beta", out,
                      "queued + await-confirm must surface the milestone-confirm reminder")

    # Additive-only: --queued alone is byte-identical (no reminder)
    def test_queued_alone_no_reminder(self):
        out = self._new_ms_out("gamma", "--queued")
        self.assertNotIn("milestone-confirm", out,
                         "queued without --await-confirm must NOT print the reminder (byte-identical)")

    # The confirm gate state is recorded (the reminder is purely presentational)
    def test_gate_state_recorded(self):
        self._new_ms_out("beta", "--queued", "--await-confirm")
        st = add.load_state(self.root)
        rec = st["milestones"]["beta"]
        self.assertEqual(rec.get("status"), "queued")
        self.assertEqual(rec.get("await_confirm"), True)
        self.assertEqual(rec.get("confirmed"), False)

    # Engine mirror + pin in sync (this is an engine change)


if __name__ == "__main__":
    unittest.main(verbosity=2)
