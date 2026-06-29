#!/usr/bin/env python3
"""Red/green tests for `add.py dag-plan` — the persisted DAG-plan snapshot + freshness check
(task persist-dag-plan, advisor-gated-autonomy).

CONTRACT (frozen @ v2):
  add.py dag-plan [--milestone <slug>]   # record-only; default target = active milestone
    ok   -> writes .add/milestones/<mslug>/dag-plan.json (atomic, committed) + prints "… (fresh ✓)"
    4xx  -> "unknown_milestone" | "no_active_milestone" | "dependency_cycle"  (NO file on reject)
  dag-plan.json = { milestone, generated, edges_fingerprint, schedule{waves,critical_path,
                    critical_path_len,tiers,blocked} }   (indent=2, sort_keys, trailing newline)
  edges_fingerprint = md5(json.dumps({s: sorted(depends_on) for s in ALL members of mslug},
                          sort_keys=True))   # ALL members → completion is NOT drift; an edge change IS
  freshness -> none | unreadable | fresh | stale   (fail-safe reader)
  status (active milestone) -> one "dag-plan: fresh ✓ | stale (…) | none — … | unreadable — …" line
  idempotent: unchanged fingerprint → file byte-identical (stable generated date)
  waves UNCHANGED (read-only authority untouched); no state.json field added.

Render-blind: assertions read printed lines / the public snapshot file, never a private state key.
Run: python3 -m unittest test_persist_dag_plan -v
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


class _Plan(unittest.TestCase):
    """A live project arranged through the real CLI, with a dep graph injected into state."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-dagplan-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- CLI helpers ------------------------------------------------------
    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _snap_path(self, mslug="v1") -> Path:
        return self._root() / "milestones" / mslug / "dag-plan.json"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _set_state(self, st: dict):
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")

    @staticmethod
    def _task(milestone="v1", phase="ground", gate="none", deps=None):
        return {
            "title": "t", "phase": phase, "gate": gate, "milestone": milestone,
            "depends_on": list(deps or []), "created": "2026-06-15", "updated": "2026-06-15",
        }

    def _load(self, tasks: dict, active="v1"):
        st = self._state()
        st["tasks"] = tasks
        st["active_task"] = None
        st["active_milestone"] = active
        ms = st.setdefault("milestones", {})
        for t in tasks.values():
            m = t.get("milestone")
            if m and m not in ms:
                ms[m] = {"status": "active"}
        self._set_state(st)

    def _status(self) -> str:
        out, _err, _code = self._run("status")
        return out

    # ---- scenarios --------------------------------------------------------
    def test_write_creates_snapshot_and_status_fresh(self):
        self._load({"a": self._task(), "b": self._task(deps=["a"])})
        out, _err, code = self._run("dag-plan")
        self.assertEqual(code, 0, out)
        self.assertTrue(self._snap_path().exists(), "dag-plan.json must be written")
        snap = json.loads(self._snap_path().read_text(encoding="utf-8"))
        self.assertEqual(snap["milestone"], "v1")
        self.assertIn("generated", snap)
        self.assertIn("edges_fingerprint", snap)
        for k in ("waves", "critical_path", "critical_path_len", "tiers", "blocked"):
            self.assertIn(k, snap["schedule"], f"schedule must carry {k}")
        self.assertIn("dag-plan: fresh ✓", self._status())

    def test_committed_not_gitignored(self):
        self._load({"a": self._task()})
        self._run("dag-plan")
        gi = (self._root() / ".gitignore")
        if gi.exists():
            self.assertNotIn("dag-plan.json", gi.read_text(encoding="utf-8"),
                             "the snapshot is committed/auditable, not a transient artifact")

    def test_edge_change_marks_stale_without_rewrite(self):
        self._load({"a": self._task(), "b": self._task(deps=["a"])})
        self._run("dag-plan")
        before = self._snap_path().read_bytes()
        # redirect b's dependency away from a (a real edge change)
        st = self._state()
        st["tasks"]["b"]["depends_on"] = []
        self._set_state(st)
        self.assertIn("dag-plan: stale", self._status())
        self.assertEqual(self._snap_path().read_bytes(), before,
                         "status must not rewrite the snapshot")

    def test_completing_a_task_is_not_drift(self):
        self._load({"a": self._task(), "b": self._task(deps=["a"])})
        self._run("dag-plan")
        before = self._snap_path().read_bytes()
        # a completes — phase/gate change, NO edge change
        st = self._state()
        st["tasks"]["a"]["phase"] = "done"
        st["tasks"]["a"]["gate"] = "PASS"
        self._set_state(st)
        self.assertIn("dag-plan: fresh ✓", self._status(),
                      "completion must NOT mark the plan stale")
        self.assertEqual(self._snap_path().read_bytes(), before)

    def test_idempotent_rewrite(self):
        self._load({"a": self._task(), "b": self._task(deps=["a"])})
        self._run("dag-plan")
        first = self._snap_path().read_bytes()
        self._run("dag-plan")
        self.assertEqual(self._snap_path().read_bytes(), first,
                         "re-running with unchanged edges must be byte-identical")

    def test_none_before_write(self):
        self._load({"a": self._task()})
        self.assertIn("dag-plan: none", self._status())
        self.assertFalse(self._snap_path().exists(), "status must not create the snapshot")

    def test_corrupt_snapshot_reads_fail_safe(self):
        self._load({"a": self._task()})
        self._snap_path().parent.mkdir(parents=True, exist_ok=True)
        self._snap_path().write_text("{ not json", encoding="utf-8")
        out = self._status()
        self.assertIn("dag-plan: unreadable", out)
        self.assertEqual(self._snap_path().read_text(encoding="utf-8"), "{ not json")

    def test_unknown_milestone_rejected(self):
        self._load({"a": self._task()})
        _out, err, code = self._run("dag-plan", "--milestone", "nope")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_milestone", err)
        self.assertFalse((self._root() / "milestones" / "nope" / "dag-plan.json").exists())

    def test_no_active_milestone_rejected(self):
        self._load({"a": self._task()})
        st = self._state()
        st["active_milestone"] = None
        st["active_milestones"] = []
        self._set_state(st)
        _out, err, code = self._run("dag-plan")
        self.assertNotEqual(code, 0)
        self.assertIn("no_active_milestone", err)
        self.assertFalse(self._snap_path().exists())

    def test_dependency_cycle_not_persisted(self):
        self._load({"a": self._task(deps=["b"]), "b": self._task(deps=["a"])})
        _out, err, code = self._run("dag-plan")
        self.assertNotEqual(code, 0)
        self.assertIn("dependency_cycle", err)
        self.assertFalse(self._snap_path().exists())


if __name__ == "__main__":
    unittest.main()
