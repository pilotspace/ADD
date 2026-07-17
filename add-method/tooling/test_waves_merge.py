#!/usr/bin/env python3
"""Red/green tests for `waves --merge` (multi-active-polish: waves-merge): fold the active SET
into ONE unified DAG so a cross-milestone dependency orders into a single critical path instead
of showing `blocked`. Merge is opt-in; no-flag (separate streams) + single `--milestone` output
stays byte-identical (the existing test_cross_active_waves is that oracle). Read-only. Run:
  python3 -m unittest test_waves_merge -v
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class _Sched(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mwaves-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self.state = self.tmp / ".add" / "state.json"

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
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

    def _md5(self):
        return hashlib.md5(self.state.read_bytes()).hexdigest()

    @staticmethod
    def _task(milestone, deps=None):
        return {"title": "t", "phase": "ground", "gate": "none", "milestone": milestone,
                "depends_on": list(deps or []), "created": "2026-06-26", "updated": "2026-06-26"}

    def _load(self, tasks, active_milestones, primary):
        st = json.loads(self.state.read_text(encoding="utf-8"))
        st["tasks"] = tasks
        st["active_task"] = None
        st["active_milestone"] = primary
        st["active_milestones"] = list(active_milestones)
        ms = st.setdefault("milestones", {})
        for m in set(list(active_milestones) + [t["milestone"] for t in tasks.values() if t.get("milestone")]):
            if m and m not in ms:
                ms[m] = {"status": "active"}
        self.state.write_text(json.dumps(st), encoding="utf-8")
        return st


class MergeScheduleTest(_Sched):
    def test_merge_schedules_cross_milestone_dep(self):
        # beta (m2) depends on alpha (m1): without merge beta would be blocked; with merge it waves
        self._load({"alpha": self._task("m1"), "beta": self._task("m2", deps=["alpha"])},
                   active_milestones=["m1", "m2"], primary="m1")
        before = self._md5()
        code, out, err = self._run("waves", "--merge")
        self.assertEqual(code, 0, err)
        lines = [l.strip() for l in out.splitlines()]
        wave1 = next(l for l in lines if l.startswith("wave 1:"))
        wave2 = next(l for l in lines if l.startswith("wave 2:"))
        self.assertIn("alpha", wave1)
        self.assertIn("beta", wave2)
        self.assertIn("critical path: alpha → beta", out)
        self.assertNotIn("blocked: beta", out)            # the dep is satisfied across milestones
        self.assertEqual(self._md5(), before)             # read-only

    def test_merge_render_header_and_milestone_labels(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2", deps=["alpha"])},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--merge")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "merged: m1 + m2 (2 milestones)")
        self.assertIn("alpha [m1]", out)
        self.assertIn("beta [m2] (deps: alpha)", out)

    def test_merge_external_dep_still_blocks(self):
        self._load({"alpha": self._task("m1", deps=["ghost"])},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--merge")
        self.assertEqual(code, 0, err)
        self.assertIn("blocked: alpha (waiting on ghost)", out)

    def test_merge_single_active_milestone_degrades(self):
        self._load({"a": self._task("m1"), "b": self._task("m1", deps=["a"])},
                   active_milestones=["m1"], primary="m1")
        code, out, err = self._run("waves", "--merge")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "merged: m1 (1 milestone)")
        self.assertIn("a [m1]", out)


class MergeDegradeRejectTest(_Sched):
    def test_merge_explicit_milestone_degrades(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2")},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--merge", "--milestone", "m1")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "merged: m1 (1 milestone)")
        self.assertIn("alpha", out)
        self.assertNotIn("beta", out)

    def test_merge_unknown_milestone_dies(self):
        self._load({"alpha": self._task("m1")}, active_milestones=["m1"], primary="m1")
        code, out, err = self._run("waves", "--merge", "--milestone", "ghost")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_milestone", out + err)

    def test_merge_no_active_milestone_dies(self):
        self._load({"alpha": self._task("m1")}, active_milestones=["m1"], primary=None)
        code, out, err = self._run("waves", "--merge")
        self.assertNotEqual(code, 0)
        self.assertIn("no_active_milestone", out + err)

    def test_merge_cross_milestone_cycle_dies(self):
        self._load({"a": self._task("m1", deps=["b"]), "b": self._task("m2", deps=["a"])},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--merge")
        self.assertNotEqual(code, 0)
        self.assertIn("dependency_cycle", out + err)


class MergeJsonTest(_Sched):
    def test_merge_json_shape(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2", deps=["alpha"])},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--merge", "--json")
        self.assertEqual(code, 0, err)
        obj = json.loads(out.strip().splitlines()[-1])
        self.assertEqual(obj["merged"], ["m1", "m2"])
        for key in ("waves", "critical_path", "critical_path_len", "tiers", "blocked"):
            self.assertIn(key, obj)
        self.assertNotIn("streams", obj)


class WrapperIdentityTest(_Sched):
    def test_wave_schedule_is_merged_over_one(self):
        # _wave_schedule(state, m) must equal _wave_schedule_merged(state, [m]) for several shapes
        st = self._load({"a": self._task("m1"), "b": self._task("m1", deps=["a"]),
                         "c": self._task("m1", deps=["a", "b"]), "x": self._task("m2")},
                        active_milestones=["m1", "m2"], primary="m1")
        for m in ("m1", "m2"):
            self.assertEqual(add._wave_schedule(st, m),
                             add._wave_schedule_merged(st, [m]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
