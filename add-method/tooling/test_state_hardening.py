#!/usr/bin/env python3
"""Design-for-failure proofs for the state engine (task: v11 state-engine hardening).

The brief's CRITICAL RULE demands every IO path design for failure. These pin:
  - load_state fails CLOSED — a corrupt/unreadable state.json dies with a clean
    'state_invalid' message, never a raw Python traceback (affects every command).
  - cmd_status survives a schema-shifted state (missing key) and a stale active_task
    slug without a KeyError traceback.
  - `add.py use <slug>` switches the active task without hand-editing state.json.
  - _write_retro is atomic (temp + os.replace) per the module's own contract — a
    crash mid-write leaves no half-written RETRO.md and the milestone still active.
  - archive-milestone writes a recoverable pre-archive snapshot before its destructive
    deletes (the archived record keeps only a slug-list).
Run: python3 -m unittest test_state_hardening -v
"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import add


def _run(argv):
    """Run add.main, capturing (code, out, err). Non-SystemExit exceptions propagate
    (so a bare traceback shows up as a test ERROR — exactly what we are guarding against)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class StateHardeningTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-state-harden-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.state_path = Path(self.tmp) / ".add" / "state.json"

    def tearDown(self):
        os.chdir(self._cwd)

    def _poke_state(self, mutate):
        st = json.loads(self.state_path.read_text(encoding="utf-8"))
        mutate(st)
        self.state_path.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")

    def _complete_task_in_milestone(self, ms, slug):
        add.main(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", slug])
        add.main(["phase", "verify", slug])
        add.main(["gate", "PASS", slug])

    # --- load_state fails closed --------------------------------------------
    def test_corrupt_state_dies_clean_not_traceback(self):
        self.state_path.write_text("{ this is not valid json", encoding="utf-8")
        code, out, err = _run(["status"])
        self.assertEqual(code, 1, "a corrupt state.json must exit 1, not raise a traceback")
        self.assertIn("state_invalid", err)
        self.assertNotIn("Traceback", out + err)

    # --- cmd_status survives schema drift -----------------------------------
    def test_status_survives_missing_project_key(self):
        add.main(["new-task", "a"])
        self._poke_state(lambda st: st.pop("project", None))
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0, "status must not KeyError on a missing 'project' key")
        self.assertIn("project", out)  # the labelled line still prints (with a fallback)

    def test_status_survives_stale_active_task(self):
        add.main(["new-task", "a"])
        self._poke_state(lambda st: st.__setitem__("active_task", "ghost"))
        code, _, err = _run(["status"])
        self.assertEqual(code, 0, "a stale active_task slug must not crash status")
        self.assertNotIn("Traceback", err)

    # --- add.py use <slug> ---------------------------------------------------
    def test_use_switches_active_task(self):
        add.main(["new-task", "a"])
        add.main(["new-task", "b"])  # active_task is now 'b'
        code, out, _ = _run(["use", "a"])
        self.assertEqual(code, 0)
        st = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(st["active_task"], "a", "use must set active_task to the named task")

    def test_use_rejects_unknown_task(self):
        add.main(["new-task", "a"])
        code, _, err = _run(["use", "ghost"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_task", err)
        st = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(st["active_task"], "a", "a rejected use must not change active_task")

    # --- _write_retro is atomic ---------------------------------------------
    def test_retro_write_is_atomic(self):
        self._complete_task_in_milestone("mvp", "t")
        retro = Path(self.tmp) / ".add" / "milestones" / "mvp" / "RETRO.md"
        self.assertFalse(retro.exists())
        # A crash at the os.replace step must leave NO half-written RETRO.md, and the
        # milestone must remain active (the close aborts before the status flip).
        with mock.patch("add.os.replace", side_effect=OSError("disk full")):
            code, _, err = _run(["milestone-done", "mvp"])
        self.assertEqual(code, 1)
        self.assertIn("retro_write_failed", err)
        self.assertFalse(retro.exists(), "a failed atomic write must leave no partial RETRO.md")
        st = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(st["milestones"]["mvp"]["status"], "active",
                         "milestone must stay active when the retro write fails")

    # --- archive writes a recoverable snapshot ------------------------------
    def test_archive_writes_pre_archive_snapshot(self):
        self._complete_task_in_milestone("mvp", "t")
        add.main(["milestone-done", "mvp"])
        code, _, _ = _run(["archive-milestone", "mvp"])
        self.assertEqual(code, 0)
        snap = Path(self.tmp) / ".add" / "milestones" / "mvp" / "pre-archive-state.bak.json"
        self.assertTrue(snap.exists(), "archive must write a pre-archive snapshot")
        data = json.loads(snap.read_text(encoding="utf-8"))
        self.assertIn("t", data["tasks"], "snapshot must capture member task records")
        self.assertEqual(data["tasks"]["t"]["phase"], "done")
        self.assertEqual(data["tasks"]["t"]["gate"], "PASS",
                         "snapshot must preserve gate data the archived record drops")


if __name__ == "__main__":
    unittest.main(verbosity=2)
