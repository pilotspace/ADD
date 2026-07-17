#!/usr/bin/env python3
"""Red/green tests for structured-actor STAMPING (user-identity 2/3):
the 4 engine-WRITTEN human seams (lock · gate · milestone-done · release) each record
the `{name,email,source}` actor from `_whoami`, ALONGSIDE today's free-text. Descriptive
only — a legacy record without the field still loads + behaves identically.
Run: python3 -m unittest test_actor_stamping -v
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
from unittest import mock

import add
from add_engine import identity

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)
KNOWN = {"name": "Ada", "email": "ada@x.io", "source": "git"}


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-stamp-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

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

    def _run(self, *argv):
        buf = io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _meet_exit_criteria(self, ms):
        import re
        p = self.tmp / ".add" / "milestones" / ms / add.MILESTONE_FILE
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                      lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
        p.write_text(text, encoding="utf-8")

    def _task_to_verify(self, ms="m", t="t"):
        """Minimal path: lock, a milestone + task, jump straight to verify (the logged
        override). The task never crosses tests->build, so the tamper/scope guards are
        grandfathered-skipped — a completing gate records cleanly."""
        self._silent("lock", "--force")
        self._silent("new-milestone", ms, "--goal", "g", "--stage", "mvp")
        self._silent("new-task", t, "--title", "Feature")
        self._silent("phase", "verify", t)


class LockStampTest(_Harness):
    def test_lock_stamps_actor(self):
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("lock", "--force")
        setup = self._state()["setup"]
        self.assertEqual(setup["actor"], KNOWN)
        self.assertIn("locked_by", setup)          # the existing free-text survives

    def test_override_flows_into_stamp(self):
        # end-to-end (no mock): an override resolves source=override into the stamp
        self._silent("whoami", "--name", "Bob", "--email", "bob@y.io")
        self._silent("lock", "--force")
        self.assertEqual(self._state()["setup"]["actor"],
                         {"name": "Bob", "email": "bob@y.io", "source": "override"})


class GateStampTest(_Harness):
    def test_gate_stamps_gate_actor_on_pass(self):
        self._task_to_verify()
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("gate", "PASS", "t")
        rec = self._state()["tasks"]["t"]
        self.assertEqual(rec["gate_actor"], KNOWN)
        self.assertEqual(rec["gate"], "PASS")

    def test_gate_stamps_gate_actor_on_hard_stop(self):
        self._task_to_verify()
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("gate", "HARD-STOP", "t")
        rec = self._state()["tasks"]["t"]
        self.assertEqual(rec["gate_actor"], KNOWN)
        self.assertEqual(rec["gate"], "HARD-STOP")


class MilestoneDoneStampTest(_Harness):
    def test_milestone_done_stamps_done_actor(self):
        self._task_to_verify()
        self._silent("gate", "PASS", "t")
        self._meet_exit_criteria("m")
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("milestone-done", "m")
        rec = self._state()["milestones"]["m"]
        self.assertEqual(rec["done_actor"], KNOWN)
        self.assertEqual(rec["status"], "done")


class ReleaseStampTest(_Harness):
    def test_release_row_carries_actor_line(self):
        self._task_to_verify()
        self._silent("gate", "PASS", "t")
        self._meet_exit_criteria("m")
        self._silent("milestone-done", "m")
        before = self._state()
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("release", "0.1.0")
        releases = (self.tmp / "RELEASES.md").read_text(encoding="utf-8")
        self.assertIn("actor: Ada <ada@x.io> (git)", releases)
        # release records to the LEDGER only — state.json is byte-unchanged (no release actor in state)
        self.assertEqual(self._state(), before)


class DescriptiveOnlyTest(_Harness):
    def test_legacy_record_without_actor_unchanged(self):
        # a state whose gate record predates stamping (no gate_actor) must load + run clean
        self._task_to_verify()
        self._silent("gate", "PASS", "t")
        st = self._state()
        st["tasks"]["t"].pop("gate_actor", None)        # simulate a pre-stamping record
        (self.tmp / ".add" / "state.json").write_text(json.dumps(st), encoding="utf-8")
        _, code = self._run("status")
        self.assertEqual(code, 0)
        _, code = self._run("report")
        self.assertEqual(code, 0)

    def test_actor_stamp_is_whoami(self):
        # single-source: the stamp helper IS the resolver
        self.assertEqual(add._actor_stamp({}), add._whoami({}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
