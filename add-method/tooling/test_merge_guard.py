#!/usr/bin/env python3
"""Red/green tests for the merge-aware state load guard (git-merge-safety 1/2):
git conflict markers in .add/state.json make every state-load path fail with a
merge-specific `state_conflicted` message (not the generic state_invalid/no_state),
without touching the file. A healthy state loads unchanged. Run:
  python3 -m unittest test_merge_guard -v
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

CONFLICTED = """\
{
<<<<<<< HEAD
  "project": "ours",
=======
  "project": "theirs",
>>>>>>> branch
  "stage": "mvp"
}
"""


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mergeguard-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
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


class ConflictGuardTest(_Harness):
    def test_conflicted_load_state_dies_conflicted(self):
        self.state.write_text(CONFLICTED, encoding="utf-8")
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("status")
        self.assertNotEqual(code, 0)
        self.assertIn("state_conflicted", err)
        self.assertIn("state.json", err)
        self.assertIn("doctor", err)          # actionable reconciliation hint
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only

    def test_conflicted_json_path_dies_conflicted(self):
        self.state.write_text(CONFLICTED, encoding="utf-8")
        code, out, err = self._run("status", "--json")
        self.assertNotEqual(code, 0)
        self.assertIn("state_conflicted", err)
        self.assertEqual(out.strip(), "")     # no parseable JSON object on stdout

    def test_conflicted_check_reports_conflicted(self):
        self.state.write_text(CONFLICTED, encoding="utf-8")
        code, out, err = self._run("check")
        self.assertNotEqual(code, 0)
        self.assertIn("state_conflicted", out + err)


class NonConflictTest(_Harness):
    def test_nonconflict_corrupt_still_state_invalid(self):
        self.state.write_text("{bad json no markers", encoding="utf-8")
        code, out, err = self._run("status")
        self.assertNotEqual(code, 0)
        self.assertIn("state_invalid", err)
        self.assertNotIn("state_conflicted", err)

    def test_healthy_state_loads_unchanged(self):
        code, out, err = self._run("status")
        self.assertEqual(code, 0, err)

    def test_marker_regex_no_false_positive_on_content(self):
        # a value CONTAINING marker-like text sits on an INDENTED JSON line (`  "title": "==…"`),
        # so no line STARTS with the marker — build a COMPLETE record via the CLI, then confirm
        # the serialized state still loads (the regex does not false-trip on the content).
        self._silent("new-milestone", "m", "--goal", "=======ish goal", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "=======ish header")
        self.assertIn("=======ish", self.state.read_text(encoding="utf-8"))  # marker text is present
        code, out, err = self._run("status")
        self.assertEqual(code, 0, err)


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
