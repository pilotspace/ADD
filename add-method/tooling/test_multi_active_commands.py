#!/usr/bin/env python3
"""Red/green tests for the multi-active COMMANDS (state-model-reshape 3/5):
activate / deactivate a milestone in the working SET + a milestone-aware `use`.
Run: python3 -m unittest test_multi_active_commands -v
"""
import hashlib
import json
import os
import tempfile
import shutil
import unittest
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


class HelperTest(unittest.TestCase):
    def test_activate_appends_and_focuses(self):
        st = {"active_milestones": ["m1"], "active_milestone": "m1",
              "active_tasks": {"m1": "t1"}, "active_task": "t1"}
        add._activate_milestone(st, "m2")
        self.assertEqual(set(st["active_milestones"]), {"m1", "m2"})
        self.assertEqual(st["active_milestone"], "m2")

    def test_activate_idempotent(self):
        st = {"active_milestones": ["m1", "m2"], "active_milestone": "m2", "active_tasks": {}}
        add._activate_milestone(st, "m1")
        self.assertEqual(st["active_milestones"].count("m1"), 1)
        self.assertEqual(st["active_milestone"], "m1")

    def test_deactivate_removes_and_repoints(self):
        st = {"active_milestones": ["m1", "m2"], "active_milestone": "m2",
              "active_tasks": {"m1": "t1", "m2": "t2"}, "active_task": "t2"}
        add._deactivate_milestone(st, "m2")
        self.assertEqual(st["active_milestones"], ["m1"])
        self.assertNotIn("m2", st["active_tasks"])
        self.assertEqual(st["active_milestone"], "m1")

    def test_deactivate_last_empties_primary(self):
        st = {"active_milestones": ["m1"], "active_milestone": "m1",
              "active_tasks": {"m1": "t1"}, "active_task": "t1"}
        add._deactivate_milestone(st, "m1")
        self.assertEqual(st["active_milestones"], [])
        self.assertIsNone(st["active_milestone"])
        self.assertIsNone(st["active_task"])


class CommandTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mac-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo", "--stage", "mvp"])
        add.main(["new-milestone", "m1", "--stage", "mvp"])
        add.main(["new-milestone", "m2", "--stage", "mvp"])   # m2 now the (replace) focus

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _set_status(self, mslug, status):
        st = self._state()
        st["milestones"][mslug]["status"] = status
        (self.tmp / ".add" / "state.json").write_text(json.dumps(st))

    def test_activate_reaches_n2(self):
        add.main(["activate", "m1"])
        st = self._state()
        self.assertEqual(set(st["active_milestones"]), {"m1", "m2"})
        self.assertEqual(st["active_milestone"], "m1")

    def test_activate_unknown_rejected(self):
        before = self._state()["active_milestones"]
        with self.assertRaises(SystemExit):
            add.main(["activate", "mX"])
        self.assertEqual(self._state()["active_milestones"], before)

    def test_activate_done_rejected(self):
        self._set_status("m1", "done")
        with self.assertRaises(SystemExit):
            add.main(["activate", "m1"])

    def test_use_switches_task_in_milestone(self):
        add.main(["new-task", "t2", "--milestone", "m2"])
        add.main(["activate", "m1"])           # focus m1
        add.main(["use", "t2"])                # t2 belongs to m2 -> focus m2
        st = self._state()
        self.assertEqual(st["active_tasks"].get("m2"), "t2")
        self.assertEqual(st["active_milestone"], "m2")
        self.assertEqual(st["active_task"], "t2")

    def test_deactivate_removes_and_repoints(self):
        add.main(["activate", "m1"])           # {m2, m1}, primary m1
        add.main(["deactivate", "m1"])
        st = self._state()
        self.assertNotIn("m1", st["active_milestones"])
        self.assertIn("m2", st["active_milestones"])

    def test_deactivate_nonmember_rejected(self):
        # new-milestone PRESERVES the active SET (new-milestone-add-focus), so both m1+m2 are
        # active after setUp — make a GENUINE non-member with a queued milestone and reject that.
        add.main(["new-milestone", "m3", "--stage", "mvp", "--queued"])
        st = self._state()
        self.assertNotIn("m3", st["active_milestones"])
        with self.assertRaises(SystemExit):
            add.main(["deactivate", "m3"])

    def test_archive_deactivates_from_set(self):
        add.main(["activate", "m1"])
        self._set_status("m2", "done")
        add.main(["archive-milestone", "m2"])
        st = self._state()
        self.assertNotIn("m2", st["active_milestones"])
        self.assertNotIn("m2", st.get("active_tasks", {}))

    def test_archive_nonprimary_clears_stale_scalar_task(self):
        # N<=1 oracle regression guard: t1 belongs to m1 and is the scalar active_task, but the
        # primary focus is m2 (the new-milestone replace-to-focus quirk leaves the scalar stale).
        # Archiving the done m1 must CLEAR the scalar (old behavior), never leave it dangling at a
        # now-deleted member task — else `advance`/`gate` with no slug fail with a phantom unknown_task.
        add.main(["new-task", "t1", "--milestone", "m1"])
        st = self._state()
        st["tasks"]["t1"]["phase"] = "done"      # member must be complete or archive refuses (milestone_has_incomplete_tasks)
        st["tasks"]["t1"]["gate"] = "PASS"
        st["milestones"]["m1"]["status"] = "done"
        st["active_milestone"] = "m2"
        st["active_milestones"] = ["m2"]
        st["active_task"] = "t1"                 # stale scalar from m1 while primary is m2
        st["active_tasks"] = {"m1": "t1"}
        (self.tmp / ".add" / "state.json").write_text(json.dumps(st))
        add.main(["archive-milestone", "m1"])
        st2 = self._state()
        self.assertNotIn("t1", st2["tasks"])           # member task deleted
        self.assertIsNone(st2["active_task"])          # stale scalar cleared, not dangling
        self.assertNotIn("m1", st2.get("active_tasks", {}))
        self.assertEqual(st2["active_milestone"], "m2")  # primary untouched


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
