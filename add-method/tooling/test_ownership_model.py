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
from add_engine import identity

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
if __name__ == "__main__":
    unittest.main(verbosity=2)
