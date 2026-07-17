#!/usr/bin/env python3
"""Red/green tests for doctor VALUE-DOMAIN checks (multi-active-polish: doctor-value-checks):
`add.py doctor` widens from referential-only to also flag a bad/missing gate-or-phase enum, a
malformed owner/assignee stamp, and an inconsistent archived entry. Detect-only (never mutates);
a healthy state still PASSes. Run:
  python3 -m unittest test_doctor_value_checks -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _clean_task(milestone="m", **extra):
    t = {"title": "x", "phase": "ground", "gate": "none", "milestone": milestone,
         "depends_on": [], "created": "2026-06-26", "updated": "2026-06-26"}
    t.update(extra)
    return t


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-docval-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "Feature")
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

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return code, out.getvalue(), err.getvalue()

    def _poke(self, mutate):
        st = json.loads(self.state.read_text(encoding="utf-8"))
        mutate(st)
        self.state.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")


class GatePhaseTest(_Harness):
    def test_healthy_state_still_passes(self):
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("doctor")
        self.assertEqual(code, 0, out + err)
        self.assertIn("PASS", out)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only

    def test_invalid_gate_flagged(self):
        self._poke(lambda st: st["tasks"]["t"].__setitem__("gate", "DONE"))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("invalid gate", out)
        self.assertIn("'t'", out)

    def test_invalid_phase_flagged(self):
        self._poke(lambda st: st["tasks"]["t"].__setitem__("phase", "shipping"))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("invalid phase", out)

    def test_missing_gate_phase_flagged(self):
        def mut(st):
            st["tasks"]["t"].pop("gate", None)
            st["tasks"]["u"] = _clean_task()
            st["tasks"]["u"].pop("phase", None)
        self._poke(mut)
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("missing its gate", out)
        self.assertIn("'t'", out)
        self.assertIn("missing its phase", out)
        self.assertIn("'u'", out)

    def test_none_gate_string_is_valid(self):
        # the STRING "none" is a legal gate (ungated task) — must NOT be flagged
        self._poke(lambda st: st["tasks"]["t"].__setitem__("gate", "none"))
        code, out, err = self._run("doctor")
        self.assertEqual(code, 0, out + err)
        self.assertIn("PASS", out)


class OwnerAssigneeTest(_Harness):
    def test_malformed_owner_flagged_wellformed_and_absent_not(self):
        def mut(st):
            st["tasks"]["t"]["owner"] = "Tin"                                   # malformed (bare string)
            st["tasks"]["b"] = _clean_task(owner={"name": "Tin", "email": None, "source": "assigned"})
            st["tasks"]["c"] = _clean_task()                                    # no owner
        self._poke(mut)
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("malformed owner", out)
        self.assertIn("'t'", out)
        self.assertEqual(out.count("malformed"), 1)                            # only t — b/c not flagged

    def test_malformed_assignee_flagged(self):
        self._poke(lambda st: st["tasks"]["t"].__setitem__("assignee", 123))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("malformed assignee", out)


class ArchivedConsistencyTest(_Harness):
    def test_archived_slug_also_live_flagged(self):
        self._poke(lambda st: st.setdefault("archived", []).append(
            {"slug": "m", "title": "dup", "tasks": 0, "task_slugs": [],
             "archived": "2026-06-26", "compacted": "2026-06-26"}))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("also a live milestone", out)
        self.assertIn("'m'", out)

    def test_archived_count_mismatch_flagged(self):
        self._poke(lambda st: st.setdefault("archived", []).append(
            {"slug": "arch1", "title": "old", "tasks": 3, "task_slugs": ["a", "b"],
             "archived": "2026-06-26", "compacted": "2026-06-26"}))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("task count 3", out)
        self.assertIn("2 listed", out)


class PurityTest(_Harness):
    def test_doctor_pure_total_on_malformed(self):
        # a non-dict task value must be skipped, not crashed on (no Traceback)
        self._poke(lambda st: st["tasks"].__setitem__("junk", "not a dict"))
        code, out, err = self._run("doctor")
        self.assertNotIn("Traceback", out + err)
        self.assertEqual(code, 0, out + err)   # junk skipped; otherwise clean → PASS


if __name__ == "__main__":
    unittest.main(verbosity=2)
