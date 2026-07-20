#!/usr/bin/env python3
"""Red/green tests for the multi-active state schema + migration (state-model-reshape /
team-collaboration foundation). Run: python3 -m unittest test_multi_active_state -v

Contract (FROZEN @ v1): a PURE, idempotent, TOTAL `_migrate_state` upgrades any single-active
state on load — adds `active_milestones` (the SET, derived from the scalar) + `active_tasks`
(per-milestone active-task MAP); KEEPS the scalar `active_milestone`/`active_task` mirrors;
orphan active_task stays a top-level fallback; corrupt JSON still dies `state_invalid`.
"""
import copy
import hashlib
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent          # add-method/tooling
REPO = HERE.parent.parent                        # repo root
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class MigrateHelperTest(unittest.TestCase):
    """The pure _migrate_state helper — no I/O, total, idempotent."""

    def test_single_active_gains_set(self):
        st = {"active_milestone": "m1", "active_task": None, "tasks": {}, "milestones": {"m1": {}}}
        out = add._migrate_state(copy.deepcopy(st))
        self.assertEqual(out["active_milestones"], ["m1"])
        self.assertEqual(out["active_milestone"], "m1")   # scalar mirror kept

    def test_empty_state_to_empty_set(self):
        st = {"active_milestone": None, "active_task": None, "tasks": {}, "milestones": {}}
        out = add._migrate_state(copy.deepcopy(st))
        self.assertEqual(out["active_milestones"], [])
        self.assertEqual(out["active_tasks"], {})

    def test_active_task_lands_under_owner(self):
        st = {"active_milestone": "m1", "active_task": "t1",
              "tasks": {"t1": {"milestone": "m1"}}, "milestones": {"m1": {}}}
        out = add._migrate_state(copy.deepcopy(st))
        self.assertEqual(out["active_tasks"], {"m1": "t1"})

    def test_orphan_active_task_preserved(self):
        # active_task set but belongs to no active milestone -> stays a top-level fallback (decision a)
        st = {"active_milestone": None, "active_task": "t9",
              "tasks": {"t9": {"milestone": "mX"}}, "milestones": {}}
        out = add._migrate_state(copy.deepcopy(st))
        self.assertEqual(out["active_task"], "t9")        # retained, not dropped
        self.assertNotIn("t9", out["active_tasks"].values())
        self.assertEqual(out["active_milestones"], [])

    def test_migration_idempotent(self):
        st = {"active_milestone": "m1", "active_task": "t1",
              "active_milestones": ["m1", "m2"], "active_tasks": {"m1": "t1", "m2": "t2"},
              "tasks": {}, "milestones": {}}
        out = add._migrate_state(copy.deepcopy(st))
        self.assertEqual(out, st)                          # already-migrated -> unchanged

    def test_total_never_raises_on_partial(self):
        # a sparse/None-shaped state must migrate without an exception (fail-soft)
        for st in ({}, {"active_milestone": None}, {"active_task": "t1"}):
            out = add._migrate_state(copy.deepcopy(st))
            self.assertIn("active_milestones", out)


class LoadSeamTest(unittest.TestCase):
    """Both load seams apply the migration; corrupt state still fails closed."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mas-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        (self.tmp / ".add").mkdir()

    def tearDown(self):
        os.chdir(self._cwd)

    def _write_state(self, obj):
        (self.tmp / ".add" / "state.json").write_text(json.dumps(obj), encoding="utf-8")

    def test_load_state_migrates(self):
        self._write_state({"active_milestone": "m1", "active_task": None,
                           "tasks": {}, "milestones": {"m1": {}}})
        out = add.load_state(self.tmp / ".add")
        self.assertEqual(out["active_milestones"], ["m1"])

    def test_load_for_json_migrates(self):
        self._write_state({"project": "p", "stage": "mvp", "active_milestone": "m1",
                           "active_task": None, "tasks": {}, "milestones": {"m1": {}}})
        os.chdir(self.tmp)
        _root, out = add._load_state_for_json()
        self.assertEqual(out["active_milestones"], ["m1"])

    def test_corrupt_state_still_invalid(self):
        (self.tmp / ".add" / "state.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            add.load_state(self.tmp / ".add")


class InitBornMigratedTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mas-init-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    def test_init_writes_active_set_natively(self):
        add.main(["init", "--name", "demo", "--stage", "mvp"])
        st = json.loads((self.tmp / ".add" / "state.json").read_text())
        self.assertEqual(st["active_milestones"], [])
        self.assertEqual(st["active_tasks"], {})
        self.assertIsNone(st["active_task"])               # scalar mirror still present
        # a second load is a no-op (already conforms)
        out = add.load_state(self.tmp / ".add")
        self.assertEqual(out["active_milestones"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
