#!/usr/bin/env python3
"""Red/green tests for `add.py mine --all` (multi-active-polish: mine-all-lens): widen the
ownership lens past the active SET — list every not-done task owned/assigned to the actor across
ALL milestones (+ loose). Plain `mine` (active-only) stays byte-identical. Read-only. Run:
  python3 -m unittest test_mine_all_lens -v
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
ME = "Ada <ada@x.io>"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mineall-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("whoami", "--name", "Ada", "--email", "ada@x.io")
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

    def _milestone(self, slug):
        self._silent("new-milestone", slug, "--goal", "g", "--stage", "mvp")

    def _task(self, slug, milestone, *, owner=None, assignee=None):
        if milestone is None:
            # new-task auto-links to the active milestone; force a truly LOOSE task
            self._silent("new-task", slug, "--title", slug)
            self._poke(lambda st: st["tasks"][slug].__setitem__("milestone", None))
        else:
            self._silent("new-task", slug, "--title", slug, "--milestone", milestone)
        if owner is not None:
            self._silent("assign", slug, "--owner", owner)
        if assignee is not None:
            self._silent("assign", slug, "--assignee", assignee)

    def _activate(self, *slugs):
        self._poke(lambda st: st.__setitem__("active_milestones", list(slugs)))


class AllScopeTest(_Harness):
    def test_all_surfaces_nonactive(self):
        self._milestone("m1")
        self._milestone("paused")
        self._task("t1", "m1", owner=ME)
        self._task("t2", "paused", owner=ME)
        self._activate("m1")                       # paused NOT active
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("mine", "--all")
        self.assertEqual(code, 0, out + err)
        self.assertIn("t1", out)
        self.assertIn("t2", out)
        self.assertIn("across all milestones", out)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only

    def test_plain_mine_still_excludes_nonactive(self):
        self._milestone("m1")
        self._milestone("paused")
        self._task("t1", "m1", owner=ME)
        self._task("t2", "paused", owner=ME)
        self._activate("m1")
        code, out, err = self._run("mine")
        self.assertEqual(code, 0, out + err)
        self.assertIn("t1", out)
        self.assertNotIn("t2", out)
        self.assertIn("across active milestones", out)

    def test_all_includes_loose_renders_loose(self):
        self._milestone("m1")
        self._task("t3", None, owner=ME)           # loose (milestone-less)
        self._activate("m1")
        code, out, err = self._run("mine", "--all")
        self.assertEqual(code, 0, out + err)
        self.assertIn("t3", out)
        self.assertIn("[loose]", out)
        self.assertNotIn("[None]", out)

    def test_all_excludes_done_and_unowned(self):
        self._milestone("paused")
        self._task("done_mine", "paused", owner=ME)
        self._poke(lambda st: st["tasks"]["done_mine"].update({"phase": "done", "gate": "PASS"}))
        self._task("unowned", "paused")            # no owner/assignee
        self._activate()                           # nothing active
        code, out, err = self._run("mine", "--all")
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("done_mine", out)
        self.assertNotIn("unowned", out)


class AllJsonTest(_Harness):
    def test_all_json_includes_nonactive(self):
        self._milestone("m1")
        self._milestone("paused")
        self._task("t1", "m1", owner=ME)
        self._task("t2", "paused", assignee=ME)
        self._activate("m1")
        code, out, err = self._run("mine", "--all", "--json")
        self.assertEqual(code, 0, out + err)
        obj = json.loads(out.strip().splitlines()[-1])
        slugs = {r["slug"] for r in obj["tasks"]}
        self.assertEqual(slugs, {"t1", "t2"})
        for r in obj["tasks"]:
            self.assertEqual(set(r), {"slug", "milestone", "phase", "role"})


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
