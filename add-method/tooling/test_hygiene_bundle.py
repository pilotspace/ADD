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


class SnapshotHashTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-snaphash-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_good_file_returns_hash(self):
        p = self.tmp / "good.json"
        p.write_text(json.dumps({"id": "x", "hash": "abc123"}), encoding="utf-8")
        self.assertEqual(add._snapshot_hash(p), "abc123")

    def test_all_malformed_return_none_never_raise(self):
        missing = self.tmp / "nope.json"
        nonjson = self.tmp / "nonjson.json"; nonjson.write_text("}{not json", encoding="utf-8")
        nondict = self.tmp / "nondict.json"; nondict.write_text("[1, 2, 3]", encoding="utf-8")
        nohash = self.tmp / "nohash.json"; nohash.write_text(json.dumps({"id": "x"}), encoding="utf-8")
        for p in (missing, nonjson, nondict, nohash):
            self.assertIsNone(add._snapshot_hash(p), f"{p.name} must degrade to None, never raise")


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


class CmdCheckComponentsOncePerInvocationTest(unittest.TestCase):
    """#1b: cmd_check reads components.toml O(1) per invocation, not O(bound-tasks).
    Proven by comparing the _components() call count across a 2-bound-task and a
    4-bound-task project — a hoisted read is INDEPENDENT of task count."""

    def _silent(self, *argv):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            try:
                add.main(list(argv))
            except SystemExit:
                pass

    def _project(self, n_tasks: int) -> Path:
        d = Path(tempfile.mkdtemp(prefix="add-comp-")).resolve()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        prev = Path.cwd()
        os.chdir(d)
        try:
            self._silent("init", "--name", "demo")
            # a real component so a bound task's _tc != "?" (exercises the per-task read)
            (d / ".add" / "components.toml").write_text(
                '[component.api]\nroot = "api"\ngreen_bar = "tests pass"\n', encoding="utf-8")
            for i in range(n_tasks):
                slug = f"t{i}"
                self._silent("new-task", slug)
                p = d / ".add" / "tasks" / slug / "TASK.md"
                txt = p.read_text(encoding="utf-8").replace(
                    "autonomy: auto", "autonomy: auto\ncomponent: api", 1)
                p.write_text(txt, encoding="utf-8")
        finally:
            os.chdir(prev)
        return d

    def _count_components_calls(self, project: Path) -> int:
        real = add._components
        n = {"c": 0}
        def spy(root):
            n["c"] += 1
            return real(root)
        prev = Path.cwd()
        os.chdir(project)
        add._components = spy
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                try:
                    add.main(["check"])
                except SystemExit:
                    pass
        finally:
            add._components = real
            os.chdir(prev)
        return n["c"]

    def test_components_read_is_independent_of_task_count(self):
        c2 = self._count_components_calls(self._project(2))
        c4 = self._count_components_calls(self._project(4))
        self.assertEqual(c2, c4,
                         f"cmd_check must read components.toml O(1), not O(bound-tasks): "
                         f"2-task={c2} vs 4-task={c4} — a hoisted read is task-count-independent")


class EnginePinTest(unittest.TestCase):
    def test_addpy_trio_matches_engine_md5(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "engine_pin.ENGINE_MD5 must track the live engine")

    def test_pkg_digest_matches(self):
        self.assertEqual(engine_manifest.package_digest(HERE),
                         engine_pin.ENGINE_PKG_MD5,
                         "engine_pin.ENGINE_PKG_MD5 must track the engine package modules")


if __name__ == "__main__":
    unittest.main(verbosity=2)
