#!/usr/bin/env python3
"""Red/green tests for `add.py mine` (multi-active-UX 1/3): a read-only per-actor lens that,
across ALL active milestones, lists the not-done tasks owned-by/assigned-to the resolved actor
(`_whoami`, or `--actor "Name <email>"`). Text + `--json`; mutates nothing. Run:
  python3 -m unittest test_my_work_lens -v
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
ME_NAME = "Ada"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mine-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("whoami", "--name", "Ada", "--email", "ada@x.io")  # deterministic actor
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

    # fixture builders — milestone/task records through the REAL constructors; the active SET
    # (a plain list of real slugs) is set last, since `new-milestone` replaces the focus set.
    def _milestone(self, slug):
        self._silent("new-milestone", slug, "--goal", "g", "--stage", "mvp")

    def _task(self, slug, milestone, *, owner=None, assignee=None):
        self._silent("new-task", slug, "--title", slug, "--milestone", milestone)
        if owner is not None and assignee is not None and owner == assignee:
            self._silent("assign", slug, "--owner", owner, "--assignee", assignee)
        else:
            if owner is not None:
                self._silent("assign", slug, "--owner", owner)
            if assignee is not None:
                self._silent("assign", slug, "--assignee", assignee)

    def _activate(self, *slugs):
        self._poke(lambda st: st.__setitem__("active_milestones", list(slugs)))


class MineListTest(_Harness):
    def test_mine_lists_owned_and_assigned(self):
        self._milestone("m1")
        self._milestone("m2")
        self._task("t1", "m1", owner=ME)        # I own t1
        self._task("t2", "m2", assignee=ME)     # I'm assigned t2
        self._activate("m1", "m2")
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("mine")
        self.assertEqual(code, 0, out + err)
        self.assertIn("t1", out)
        self.assertIn("t2", out)
        self.assertIn("m1", out)
        self.assertIn("m2", out)
        self.assertIn("owner", out)
        self.assertIn("assignee", out)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only

    def test_mine_excludes_done_unowned_nonactive(self):
        self._milestone("m1")
        self._milestone("paused")
        self._task("done_mine", "m1", owner=ME)
        self._poke(lambda st: st["tasks"]["done_mine"].update({"phase": "done", "gate": "PASS"}))
        self._task("unowned", "m1")                        # no owner/assignee
        self._task("nonactive_mine", "paused", owner=ME)   # mine but milestone not active
        self._activate("m1")                               # paused stays OUT of the active set
        code, out, err = self._run("mine")
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("done_mine", out)
        self.assertNotIn("unowned", out)
        self.assertNotIn("nonactive_mine", out)


class MineEmptyTest(_Harness):
    def test_mine_empty_queue_exits_zero(self):
        self._milestone("m1")
        self._task("t1", "m1")                              # unowned -> not mine
        self._activate("m1")
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("mine")
        self.assertEqual(code, 0, out + err)
        self.assertIn("no open task", out.lower())
        self.assertNotIn("t1", out)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only on the empty path too


class MineRoleOrderTest(_Harness):
    def test_mine_role_both_and_milestone_order(self):
        self._milestone("m1")
        self._milestone("m2")
        self._task("a_both", "m1", owner=ME, assignee=ME)   # owner AND assignee -> role "both"
        self._task("z_owner", "m2", owner=ME)               # owner only -> role "owner"
        self._activate("m1", "m2")                          # active order m1, m2
        code, out, err = self._run("mine", "--json")
        self.assertEqual(code, 0, out + err)
        rows = json.loads(out)["tasks"]
        self.assertEqual([r["slug"] for r in rows], ["a_both", "z_owner"])  # m1 before m2 (active order)
        self.assertEqual(rows[0]["role"], "both")
        self.assertEqual(rows[1]["role"], "owner")


class MineActorOverrideTest(_Harness):
    def test_mine_actor_override(self):
        self._milestone("m1")
        self._task("bobs", "m1", assignee="Bob <bob@x.io>")
        self._activate("m1")
        # my own queue is empty; Bob's has the task
        code_self, out_self, _ = self._run("mine")
        self.assertNotIn("bobs", out_self)
        code, out, err = self._run("mine", "--actor", "Bob <bob@x.io>")
        self.assertEqual(code, 0, out + err)
        self.assertIn("bobs", out)


class MineJsonTest(_Harness):
    def test_mine_json_surface(self):
        self._milestone("m1")
        self._task("t1", "m1", owner=ME)
        self._activate("m1")
        code, out, err = self._run("mine", "--json")
        self.assertEqual(code, 0, out + err)
        obj = json.loads(out)                               # exactly one JSON object on stdout
        self.assertEqual(obj["actor"]["name"], ME_NAME)
        self.assertEqual(len(obj["tasks"]), 1)
        row = obj["tasks"][0]
        self.assertEqual(set(row), {"slug", "milestone", "phase", "role"})
        self.assertEqual(row["slug"], "t1")
        self.assertEqual(row["milestone"], "m1")
        self.assertEqual(row["role"], "owner")


class MineMatchTest(_Harness):
    def test_mine_match_email_first_name_fallback(self):
        self._milestone("m1")
        # name fallback: record carries NO email; my name matches -> mine
        self._task("byname", "m1", owner="Ada")             # bare name -> email None
        # both-email mismatch: same name, different email -> NOT mine (email-first)
        self._task("byemail", "m1", owner="Ada <other@x.io>")
        self._activate("m1")
        code, out, err = self._run("mine", "--json")
        self.assertEqual(code, 0, out + err)
        slugs = {r["slug"] for r in json.loads(out)["tasks"]}
        self.assertIn("byname", slugs)                      # name-equality fallback
        self.assertNotIn("byemail", slugs)                  # both have email, emails differ


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
