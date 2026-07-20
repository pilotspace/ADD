#!/usr/bin/env python3
"""Red/green for hygiene-bundle (engine-hygiene, frozen §3 v1).

Four behavior-preserving engine cleanups, pinned structurally (the ~3600-test
fence guards behavior; these pin that each change actually landed):
  #2  _snapshot_hash(path) -> str | None      — one reader, unified exception tuple
  #5  _resolve_milestone(state, slug) -> str   — one resolver (twin of _resolve_task)
  #3  taskdoc._HEADING_RE                        — static heading regex hoisted to module
  #1  cmd_check reads components.toml O(1), not O(tasks) (+ no dead _arch recompute)

Run: python3 -m unittest test_hygiene_bundle -v
"""
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin
import engine_manifest
from add_engine import taskdoc

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")
class ResolveMilestoneTest(unittest.TestCase):
    def test_present_returns_slug(self):
        state = {"milestones": {"v1": {}}}
        self.assertEqual(add._resolve_milestone(state, "v1"), "v1")

    def test_absent_dies_unknown_milestone(self):
        state = {"milestones": {"v1": {}}}
        with self.assertRaises(SystemExit) as cm:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                add._resolve_milestone(state, "ghost")
        self.assertNotEqual(cm.exception.code, 0)


class TaskdocHeadingReTest(unittest.TestCase):
    def test_module_constant_exists_and_matches(self):
        self.assertTrue(hasattr(taskdoc, "_HEADING_RE"),
                        "the static heading regex must be a module-level constant (hoisted)")
        m = taskdoc._HEADING_RE.match("## 3 · PLAN")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "3")
class EnginePinTest(unittest.TestCase):

    def test_pkg_digest_matches(self):
        self.assertEqual(engine_manifest.package_digest(HERE),
                         engine_pin.ENGINE_PKG_MD5,
                         "engine_pin.ENGINE_PKG_MD5 must track the engine package modules")


if __name__ == "__main__":
    unittest.main(verbosity=2)
