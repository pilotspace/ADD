#!/usr/bin/env python3
"""Red/green tests for the parallel-status view (state-model-reshape 4/5):
`status` renders the active SET as parallel streams (per-milestone active task + phase),
additive at N>=2 and byte-identical at N<=1.
Run: python3 -m unittest test_parallel_status_view -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
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


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-psv-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "m1", "--stage", "mvp")
        self._silent("new-milestone", "m2", "--stage", "mvp")   # m2 = replace-focus primary

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def _status(self, *extra):
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["status", *extra])
        return buf.getvalue()

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _set_state(self, st):
        (self.tmp / ".add" / "state.json").write_text(json.dumps(st))

    def _craft(self, active_milestones, active_tasks, primary, phases=None):
        """Write a precise multi-active state: tasks created + phased, the SET/map set directly."""
        st = self._state()
        for t in set(active_tasks.values()):
            st["tasks"][t] = {"phase": (phases or {}).get(t, "build"), "gate": "none",
                              "milestone": next(m for m, tk in active_tasks.items() if tk == t)}
        st["active_milestones"] = list(active_milestones)
        st["active_tasks"] = dict(active_tasks)
        st["active_milestone"] = primary
        st["active_task"] = active_tasks.get(primary)
        self._set_state(st)


class StreamsRenderTest(_Board):
    def test_two_active_render_as_streams(self):
        self._craft(["m1", "m2"], {"m1": "t1", "m2": "t2"}, "m2",
                    phases={"t1": "verify", "t2": "build"})
        out = self._status()
        self.assertIn("streams : 2 active milestones", out)
        lines = out.splitlines()
        m2_line = next(l for l in lines if l.lstrip().startswith("▸") and " m2 " in l)
        self.assertIn("task=t2", m2_line)
        self.assertIn("phase=build", m2_line)
        self.assertIn("(primary)", m2_line)
        m1_line = next(l for l in lines if " m1 " in l and "task=t1" in l)
        self.assertIn("phase=verify", m1_line)
        self.assertNotIn("(primary)", m1_line)

    def test_primary_listed_first(self):
        self._craft(["m1", "m2"], {"m1": "t1", "m2": "t2"}, "m2")
        body = self._status().split("streams :", 1)[1]
        self.assertLess(body.index(" m2 "), body.index(" m1 "),
                        "the primary stream is listed before the others")

    def test_single_active_no_streams_block(self):
        # collapse to one active milestone (the migrated single-active shape)
        self._craft(["m1"], {"m1": "t1"}, "m1")
        out = self._status()
        self.assertIn("active  :", out)
        self.assertNotIn("streams :", out)
        # N=1 rollup-mark byte-identity: the new `mslug in active_milestones` predicate must
        # still mark the single active milestone `*` and leave the non-active one unmarked —
        # locks the regression the rollup-mark change could silently introduce (review NIT).
        rollup = out.split("milestones:", 1)[1].split("active  :", 1)[0]
        m1_roll = next(l for l in rollup.splitlines() if " m1 " in l and l.strip().endswith("status=active"))
        self.assertTrue(m1_roll.lstrip().startswith("*"), "N=1: the single active milestone keeps its * mark")
        m2_roll = next(l for l in rollup.splitlines() if " m2 " in l and l.strip().endswith("status=active"))
        self.assertFalse(m2_roll.lstrip().startswith("*"), "N=1: a non-active milestone stays unmarked")

    def test_no_active_no_streams_block(self):
        st = self._state()
        st["active_milestones"] = []
        st["active_milestone"] = None
        st["active_task"] = None
        st["active_tasks"] = {}
        self._set_state(st)
        out = self._status()
        self.assertIn("active  : (none)", out)
        self.assertNotIn("streams :", out)

    def test_stream_without_active_task_shows_none(self):
        self._craft(["m1", "m2"], {"m2": "t2"}, "m2")   # m1 has no active task
        out = self._status()
        m1_line = next(l for l in out.splitlines() if " m1 " in l and "task=" in l)
        self.assertIn("task=(none)", m1_line)
        self.assertIn("phase=-", m1_line)

    def test_rollup_marks_every_active_member(self):
        self._craft(["m1", "m2"], {"m1": "t1", "m2": "t2"}, "m2")
        out = self._status()
        rollup = out.split("milestones:", 1)[1].split("active  :", 1)[0]
        m1_roll = next(l for l in rollup.splitlines() if l.strip().endswith("status=active") and " m1 " in l)
        m2_roll = next(l for l in rollup.splitlines() if l.strip().endswith("status=active") and " m2 " in l)
        self.assertTrue(m1_roll.lstrip().startswith("*"), m1_roll)
        self.assertTrue(m2_roll.lstrip().startswith("*"), m2_roll)


class StreamsJsonTest(_Board):
    def test_json_exposes_set_and_map(self):
        self._craft(["m1", "m2"], {"m1": "t1", "m2": "t2"}, "m2")
        out = self._status("--json")
        d = json.loads(out)
        self.assertEqual(d["active_milestones"], ["m1", "m2"])
        self.assertEqual(d["active_tasks"], {"m1": "t1", "m2": "t2"})
        self.assertEqual(d["active_task"], "t2")   # existing key unchanged

    def test_json_single_active_preserves_active_task(self):
        # N=1 JSON byte-identity: the existing active_task key is unchanged and the new
        # additive keys carry the single-member shape (review NIT — the N<=1 json was untested).
        self._craft(["m1"], {"m1": "t1"}, "m1")
        d = json.loads(self._status("--json"))
        self.assertEqual(d["active_task"], "t1")
        self.assertEqual(d["active_milestones"], ["m1"])
        self.assertEqual(d["active_tasks"], {"m1": "t1"})


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
