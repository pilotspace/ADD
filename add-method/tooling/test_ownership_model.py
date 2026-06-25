#!/usr/bin/env python3
"""Red/green tests for the ownership DATA MODEL (ownership-assignment 1/2):
two mutable {name,email,source} fields — `owner` (accountable) and `assignee`
(working it) — written on a task OR milestone record via `add.py assign`/`unassign`.
Descriptive + additive; validate-before-mutate (a reject leaves state byte-identical).
Run: python3 -m unittest test_ownership_model -v
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
from unittest import mock

import add
from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)
SELF = {"name": "Ada", "email": "ada@x.io", "source": "git"}


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ownership-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "Feature")

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
        return code, out.getvalue() + err.getvalue()

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _raw(self):
        return (self.tmp / ".add" / "state.json").read_text()


class ParseTest(unittest.TestCase):
    def test_parse_actor_arg_total(self):
        self.assertEqual(add._parse_actor_arg("Ada <a@x.io>"),
                         {"name": "Ada", "email": "a@x.io", "source": "assigned"})
        self.assertEqual(add._parse_actor_arg("Ada"),
                         {"name": "Ada", "email": None, "source": "assigned"})
        # malformed (no close bracket) never raises — the whole string is the name
        got = add._parse_actor_arg("Ada <a@x.io")
        self.assertEqual(got["name"], "Ada <a@x.io")
        self.assertIsNone(got["email"])


class AssignTest(_Harness):
    def test_bare_assign_sets_both_to_self(self):
        with mock.patch.object(add, "_whoami", return_value=dict(SELF)):
            self._silent("assign", "t")
        rec = self._state()["tasks"]["t"]
        self.assertEqual(rec["owner"], SELF)
        self.assertEqual(rec["assignee"], SELF)

    def test_assign_owner_names_only_owner(self):
        self._silent("assign", "t", "--owner", "Bob <bob@y.io>")
        rec = self._state()["tasks"]["t"]
        self.assertEqual(rec["owner"], {"name": "Bob", "email": "bob@y.io", "source": "assigned"})
        self.assertNotIn("assignee", rec)

    def test_assign_both_flags_on_milestone(self):
        self._silent("assign", "m", "--owner", "Bob <bob@y.io>", "--assignee", "Cy")
        rec = self._state()["milestones"]["m"]
        self.assertEqual(rec["owner"], {"name": "Bob", "email": "bob@y.io", "source": "assigned"})
        self.assertEqual(rec["assignee"], {"name": "Cy", "email": None, "source": "assigned"})

    def test_assign_assignee_preserves_owner(self):
        self._silent("assign", "t", "--owner", "Bob <bob@y.io>")
        self._silent("assign", "t", "--assignee", "Cy")
        rec = self._state()["tasks"]["t"]
        self.assertEqual(rec["assignee"]["name"], "Cy")
        self.assertEqual(rec["owner"]["name"], "Bob")   # untouched


class UnassignTest(_Harness):
    def _both(self):
        self._silent("assign", "t", "--owner", "Bob <b@y.io>", "--assignee", "Cy")

    def test_unassign_clears_both(self):
        self._both()
        self._silent("unassign", "t")
        rec = self._state()["tasks"]["t"]
        self.assertNotIn("owner", rec)
        self.assertNotIn("assignee", rec)

    def test_unassign_owner_only(self):
        self._both()
        self._silent("unassign", "t", "--owner")
        rec = self._state()["tasks"]["t"]
        self.assertNotIn("owner", rec)
        self.assertEqual(rec["assignee"]["name"], "Cy")


class RejectTest(_Harness):
    def test_assign_unknown_slug_rejected(self):
        before = self._raw()
        code, out = self._run("assign", "ghost")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_slug", out)
        self.assertEqual(self._raw(), before)   # byte-identical

    def test_assign_blank_owner_rejected(self):
        code, out = self._run("assign", "t", "--owner", "   ")
        self.assertNotEqual(code, 0)
        self.assertIn("owner_name_blank", out)
        self.assertNotIn("owner", self._state()["tasks"]["t"])

    def test_assign_bracket_blank_owner_rejected(self):
        # a value whose NAME parses empty ("<>", " <a@x.io>") is blank too — validate the
        # parsed name, not just the raw string (adversarial-review finding).
        for val in ("<>", " <a@x.io>"):
            before = self._raw()
            code, out = self._run("assign", "t", "--owner", val)
            self.assertNotEqual(code, 0, f"{val!r} should reject")
            self.assertIn("owner_name_blank", out)
            self.assertEqual(self._raw(), before)   # byte-identical, no blank-name write

    def test_unassign_absent_rejected(self):
        code, out = self._run("unassign", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("not_assigned", out)
        self.assertNotIn("owner", self._state()["tasks"]["t"])


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
