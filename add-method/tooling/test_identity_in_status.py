#!/usr/bin/env python3
"""Red/green tests for SURFACING the git-native actor (user-identity 3/3):
the current actor in `status` (human + --json) and the RECORDED actors (task-2's
gate_actor/done_actor) in `report`. Read-only; an unstamped record renders no actor.
Run: python3 -m unittest test_identity_in_status -v
"""
import hashlib
import io
import json
import os
import re
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-idstatus-")).resolve()
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
        p = self.tmp / ".add" / "milestones" / ms / add.MILESTONE_FILE
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                      lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
        p.write_text(text, encoding="utf-8")

    def _closed_milestone_with_gated_task(self, ms="m", t="t"):
        self._silent("lock", "--force")
        self._silent("new-milestone", ms, "--goal", "g", "--stage", "mvp")
        self._silent("new-task", t, "--title", "Feature")
        self._silent("phase", "verify", t)
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("gate", "PASS", t)
            self._meet_exit_criteria(ms)
            self._silent("milestone-done", ms)


class StatusActorTest(_Harness):
    def test_status_human_shows_actor(self):
        self._silent("whoami", "--name", "Bob", "--email", "bob@y.io")
        out = self._silent("status")
        # status aligns its colons (project :/stage   :/active  :) -> actor   :
        self.assertIn("actor   : Bob <bob@y.io> (source: override)", out)
        self.assertIn("project :", out)        # existing lines untouched

    def test_status_json_has_actor(self):
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            out = self._silent("status", "--json")
        obj = json.loads(out)
        self.assertEqual(obj["actor"], KNOWN)
        for base in ("project", "stage", "active_task", "milestones", "tasks"):
            self.assertIn(base, obj)           # base surface intact


class ReportActorTest(_Harness):
    def test_report_surfaces_recorded_actor(self):
        self._closed_milestone_with_gated_task()
        root = add.find_root()
        d = add.report_data(root, add.load_state(root), "m")
        row = next(r for r in d["tasks"] if r["slug"] == "t")
        self.assertEqual(row["gate_actor"], KNOWN)
        self.assertEqual(d["milestone"]["done_actor"], KNOWN)
        out = self._silent("report", "m")
        self.assertIn("Ada", out)              # the recorded actor is visible in the human render

    def test_unstamped_record_renders_no_actor(self):
        self._closed_milestone_with_gated_task()
        st = self._state()
        st["tasks"]["t"].pop("gate_actor", None)         # a pre-stamping record
        st["milestones"]["m"].pop("done_actor", None)
        (self.tmp / ".add" / "state.json").write_text(json.dumps(st), encoding="utf-8")
        _, code = self._run("report", "m")
        self.assertEqual(code, 0)
        _, code = self._run("status")
        self.assertEqual(code, 0)
        # report_data tolerates the absent stamp (None, not a crash/placeholder)
        root = add.find_root()
        d = add.report_data(root, add.load_state(root), "m")
        row = next(r for r in d["tasks"] if r["slug"] == "t")
        self.assertIsNone(row["gate_actor"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
