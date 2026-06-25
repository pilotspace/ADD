#!/usr/bin/env python3
"""Red/green tests for `add.py doctor` (git-merge-safety 2/2): a read-only diagnostic
that validates state.json integrity + referential consistency and REPORTS each problem
(with a fix) or PASS — mutating nothing. Run:
  python3 -m unittest test_state_doctor -v
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
from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)
MARKERS = "{\n<<<<<<< HEAD\n  \"a\": 1\n=======\n  \"a\": 2\n>>>>>>> b\n}\n"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-doctor-")).resolve()
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


class DoctorHealthyTest(_Harness):
    def test_doctor_passes_healthy(self):
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("doctor")
        self.assertEqual(code, 0, out + err)
        self.assertIn("PASS", out)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only


class DoctorBlockingTest(_Harness):
    def test_doctor_reports_conflict(self):
        self.state.write_text(MARKERS, encoding="utf-8")
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("marker", (out + err).lower())
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)

    def test_doctor_reports_bad_json(self):
        self.state.write_text("{bad json no markers", encoding="utf-8")
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("JSON", out + err)


class DoctorReferentialTest(_Harness):
    def test_doctor_reports_dangling_active_milestone(self):
        self._poke(lambda st: st.setdefault("active_milestones", []).append("ghost"))
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("ghost", out)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only

    def test_doctor_reports_task_missing_milestone(self):
        self._poke(lambda st: st["tasks"]["t"].__setitem__("milestone", "gone"))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("gone", out)
        self.assertIn("'t'", out)                       # the culpable slug, quoted (not an incidental "t")

    def test_doctor_reports_active_task_no_record(self):
        self._poke(lambda st: st.setdefault("active_tasks", {}).__setitem__("m", "phantom"))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("phantom", out)

    def test_doctor_reports_mislabeled_active_task(self):
        # contract rule 3: active_tasks maps "m" -> "t", but t.milestone is some OTHER milestone
        self._poke(lambda st: (st.setdefault("milestones", {}).setdefault(
                                   "other", {"goal": "g", "stage": "mvp", "status": "active"}),
                               st.setdefault("active_tasks", {}).__setitem__("m", "t"),
                               st["tasks"]["t"].__setitem__("milestone", "other")))
        code, out, err = self._run("doctor")
        self.assertNotEqual(code, 0)
        self.assertIn("mislabeled", out)
        self.assertIn("'t'", out)

    def test_doctor_reports_not_aborts_on_type_corrupt_state(self):
        # design-for-failure: a parseable-but-type-corrupt state (active_tasks a list, a task a
        # string) must be REPORTED, never crash the diagnostic with an AttributeError.
        self._poke(lambda st: (st.__setitem__("active_tasks", ["bad"]),
                               st["tasks"].__setitem__("t", "not-a-dict")))
        code, out, err = self._run("doctor")
        self.assertEqual(code, 0, out + err)            # no referential violation in this shape
        self.assertNotIn("Traceback", err)              # never an uncaught crash


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
