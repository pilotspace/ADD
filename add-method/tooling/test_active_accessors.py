#!/usr/bin/env python3
"""Red/green tests for the active milestone/task ACCESSOR SEAM (state-model-reshape 2/5).
Run: python3 -m unittest test_active_accessors -v

The four accessors are a behavior-preserving seam over the migrated multi-active shape:
reads return today's scalar (N≤1), writes keep scalar + structures in sync. The FULL suite
is the byte-for-decision-identity oracle; these tests pin the accessor branches directly.
"""
import ast
import hashlib
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class ReadAccessorTest(unittest.TestCase):
    def test_active_milestone_returns_primary(self):
        self.assertEqual(add._active_milestone({"active_milestone": "m1"}), "m1")
        self.assertIsNone(add._active_milestone({"active_milestone": None}))
        self.assertIsNone(add._active_milestone({}))

    def test_active_task_per_milestone_and_global(self):
        st = {"active_task": "g", "active_tasks": {"m1": "t1"}}
        self.assertEqual(add._active_task(st, "m1"), "t1")
        self.assertEqual(add._active_task(st), "g")            # no milestone -> global scalar

    def test_active_task_partial_state(self):
        st = {"active_milestones": ["m1"]}                     # no active_tasks key
        self.assertIsNone(add._active_task(st, "m1"))          # defaulted, no KeyError


class WriteAccessorTest(unittest.TestCase):
    def test_set_milestone_syncs_list(self):
        st = {}
        add._set_active_milestone(st, "m1")
        self.assertEqual(st["active_milestone"], "m1")
        self.assertEqual(st["active_milestones"], ["m1"])
        add._set_active_milestone(st, None)
        self.assertIsNone(st["active_milestone"])
        self.assertEqual(st["active_milestones"], [])

    def test_set_task_syncs_map(self):
        st = {"active_milestone": "m1", "active_milestones": ["m1"]}
        add._set_active_task(st, "t1", "m1")
        self.assertEqual(st["active_task"], "t1")
        self.assertEqual(st["active_tasks"], {"m1": "t1"})

    def test_set_task_clear_pops_entry(self):
        st = {"active_milestone": "m1", "active_milestones": ["m1"],
              "active_task": "t1", "active_tasks": {"m1": "t1"}}
        add._set_active_task(st, None, "m1")
        self.assertIsNone(st["active_task"])
        self.assertNotIn("m1", st["active_tasks"])

    def test_set_task_orphan_scalar_only(self):
        st = {"active_milestone": None, "active_milestones": []}
        add._set_active_task(st, "t9")            # no active milestone -> scalar only
        self.assertEqual(st["active_task"], "t9")
        self.assertEqual(st.get("active_tasks", {}), {})

    def test_set_task_default_milestone_is_primary(self):
        st = {"active_milestone": "m1", "active_milestones": ["m1"]}
        add._set_active_task(st, "t1")            # milestone omitted -> primary
        self.assertEqual(st["active_tasks"], {"m1": "t1"})


class RoutingTest(unittest.TestCase):
    def test_cmd_check_has_no_raw_active_task_read(self):
        # the cmd_check function body must route active-task access through the accessor
        src = (HERE / "add.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "cmd_check"), None)
        self.assertIsNotNone(fn, "cmd_check must exist")
        raw = [n for n in ast.walk(fn)
               if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
               and n.value.id == "state"
               and isinstance(n.slice, ast.Constant) and n.slice.value == "active_task"]
        # also catch state.get("active_task")
        gets = [n for n in ast.walk(fn)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get" and n.args
                and isinstance(n.args[0], ast.Constant) and n.args[0].value == "active_task"]
        self.assertEqual(raw + gets, [], "cmd_check must read active_task via _active_task, not raw")


if __name__ == "__main__":
    unittest.main(verbosity=2)
