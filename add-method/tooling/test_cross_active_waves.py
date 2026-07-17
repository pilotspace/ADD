#!/usr/bin/env python3
"""Red/green tests for cross-active-waves (multi-active-UX 3/3): `add.py waves` (no --milestone)
spans EVERY active milestone, not just the primary; `ready` annotates each task with its
milestone. Single-active / --milestone / N<=1 output stays byte-identical; read-only. Run:
  python3 -m unittest test_cross_active_waves -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-xwaves-")).resolve()
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
                "depends_on": list(deps or []), "created": "2026-06-22", "updated": "2026-06-22"}

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


class WavesCrossActiveTest(_Sched):
    def test_waves_spans_active_milestones(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2")},
                   active_milestones=["m1", "m2"], primary="m1")
        before = self._md5()
        code, out, err = self._run("waves")
        self.assertEqual(code, 0, err)
        self.assertIn("m1", out)
        self.assertIn("m2", out)
        self.assertIn("active streams:", out)
        self.assertIn("alpha", out)
        self.assertIn("beta", out)
        self.assertIn("\n\nmilestone: m2", out)            # a blank line fences the second block
        self.assertEqual(self._md5(), before)              # read-only

    def test_single_active_byte_identical(self):
        # one active milestone, diamond — no cross-active header, today's format
        self._load({"a": self._task("m1"), "b": self._task("m1"),
                    "c": self._task("m1", deps=["a"]), "d": self._task("m1", deps=["b", "c"])},
                   active_milestones=["m1"], primary="m1")
        code, out, err = self._run("waves")
        self.assertEqual(code, 0, err)
        self.assertNotIn("active streams:", out)
        self.assertTrue(any(l.strip().startswith("wave 1:") for l in out.splitlines()))
        self.assertIn("critical path:", out)

    def test_explicit_milestone_single(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2")},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--milestone", "m2")
        self.assertEqual(code, 0, err)
        self.assertNotIn("active streams:", out)
        self.assertIn("beta", out)
        self.assertNotIn("alpha", out)                     # only m2's stream


class WavesJsonTest(_Sched):
    def test_waves_json_streams_multi(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2")},
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("waves", "--json")
        self.assertEqual(code, 0, err)
        obj = json.loads(out.strip().splitlines()[-1])
        self.assertIn("streams", obj)
        self.assertEqual([s["milestone"] for s in obj["streams"]], ["m1", "m2"])
        for s in obj["streams"]:
            self.assertIn("waves", s)


class WavesRejectTest(_Sched):
    def test_no_active_milestone_still_rejected(self):
        # primary scalar None, even though the SET has a leftover entry -> still rejects
        self._load({"alpha": self._task("m1")}, active_milestones=["m1"], primary=None)
        code, out, err = self._run("waves")
        self.assertNotEqual(code, 0)
        self.assertIn("no_active_milestone", out + err)


class ReadyAnnotateTest(_Sched):
    def test_ready_annotates_milestone(self):
        self._load({"alpha": self._task("m1"), "beta": self._task("m2"),
                    "loose": self._task(None)},          # milestone-less -> no annotation
                   active_milestones=["m1", "m2"], primary="m1")
        code, out, err = self._run("ready")
        self.assertEqual(code, 0, err)
        self.assertIn("[m1]", out)
        self.assertIn("[m2]", out)
        loose_line = next(l for l in out.splitlines() if "loose" in l)
        self.assertNotIn("[", loose_line)                  # milestone-less line carries no bracket


if __name__ == "__main__":
    unittest.main(verbosity=2)
