#!/usr/bin/env python3
"""Red/green tests for `add.py waves` — the DAG wave scheduler (task dag-scheduler,
v13-onboarding-polish 1/6).

`waves` is READ-ONLY: from the active milestone's not-done tasks + their depends_on it
computes topological waves, the critical path (longest chain), an advisory per-task tier
hint (top on the critical path, mid elsewhere), and a `blocked` set for tasks whose deps
can never be satisfied within the milestone. It writes nothing and emits no `next:` footer.

Render-blind: --json assertions parse the JSON; text assertions read printed lines. The
dep graph is injected via _set_state (the test_next_footer_engine idiom), never internals.
Run: python3 -m unittest test_dag_scheduler -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class _Sched(unittest.TestCase):
    """A live project arranged through the real CLI, with a dep graph injected into state."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-waves-")).resolve()
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
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
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

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _set_state(self, st: dict):
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")

    def _state_md5(self) -> str:
        return hashlib.md5((self._root() / "state.json").read_bytes()).hexdigest()

    # ---- graph injection --------------------------------------------------
    @staticmethod
    def _task(milestone="v1", phase="ground", gate="none", deps=None):
        return {
            "title": "t", "phase": phase, "gate": gate, "milestone": milestone,
            "depends_on": list(deps or []), "created": "2026-06-15", "updated": "2026-06-15",
        }

    def _load(self, tasks: dict, active="v1"):
        """Inject a task graph; preserve every other state key the engine expects."""
        st = self._state()
        st["tasks"] = tasks
        st["active_task"] = None
        st["active_milestone"] = active
        # ensure referenced milestones exist in state (status active) so unknown_milestone is precise
        ms = st.setdefault("milestones", {})
        for t in tasks.values():
            m = t.get("milestone")
            if m and m not in ms:
                ms[m] = {"status": "active"}
        if active and active not in ms:
            ms[active] = {"status": "active"}
        self._set_state(st)

    def _diamond(self):
        """a,b roots · c deps a · d deps b,c — the canonical diamond."""
        self._load({
            "a": self._task(deps=[]),
            "b": self._task(deps=[]),
            "c": self._task(deps=["a"]),
            "d": self._task(deps=["b", "c"]),
        })

    def _json(self, *argv):
        out, err, code = self._run(*argv, "--json")
        self.assertEqual(code, 0, f"expected exit 0, got {code}; err={err}; out={out}")
        return json.loads(out.strip().splitlines()[-1])

    # ── waves / ordering ──────────────────────────────────────────────────
    def test_diamond_schedules_into_waves(self):
        self._diamond()
        before = self._state_md5()
        data = self._json("waves")
        self.assertEqual(data["waves"], [["a", "b"], ["c"], ["d"]])
        self.assertEqual(self._state_md5(), before, "waves must not mutate state")

    def test_critical_path_and_tiers(self):
        self._diamond()
        data = self._json("waves")
        self.assertEqual(data["critical_path"], ["a", "c", "d"])
        self.assertEqual(data["critical_path_len"], 3)
        self.assertEqual(data["tiers"]["a"], "top")
        self.assertEqual(data["tiers"]["c"], "top")
        self.assertEqual(data["tiers"]["d"], "top")
        self.assertEqual(data["tiers"]["b"], "mid")

    def test_satisfied_dep_not_delayed(self):
        self._load({
            "a": self._task(phase="done", gate="PASS"),
            "c": self._task(deps=["a"]),
        })
        before = self._state_md5()
        data = self._json("waves")
        self.assertIn("c", data["waves"][0], "a dep already PASS must not delay c")
        self.assertEqual(self._state_md5(), before)

    def test_incomplete_nonmember_dep_blocks(self):
        self._load({
            "z": self._task(milestone="v1", deps=["ext"]),
            "ext": self._task(milestone="v2", phase="ground"),  # not-done, different milestone
        })
        data = self._json("waves")
        flat = [s for wave in data["waves"] for s in wave]
        self.assertNotIn("z", flat, "z's external dep is unsatisfiable here")
        self.assertEqual(data["blocked"].get("z"), ["ext"])

    def test_all_done_milestone_no_error(self):
        self._load({
            "a": self._task(phase="done", gate="PASS"),
            "b": self._task(phase="done", gate="PASS"),
        })
        before = self._state_md5()
        out, err, code = self._run("waves")
        self.assertEqual(code, 0, f"all-done is not an error; err={err}")
        self.assertIn("nothing to schedule", out)
        self.assertEqual(self._state_md5(), before)

    def test_text_output_render_blind(self):
        self._diamond()
        out, err, code = self._run("waves")
        self.assertEqual(code, 0, f"err={err}")
        wave1 = [ln for ln in out.splitlines() if ln.strip().startswith("wave 1:")]
        self.assertTrue(wave1, f"expected a 'wave 1:' line, got:\n{out}")
        self.assertIn("a", wave1[0])
        self.assertIn("b", wave1[0])
        self.assertTrue(any("critical path:" in ln for ln in out.splitlines()))
        self.assertFalse(
            any(ln.strip().startswith("next:") for ln in out.splitlines()),
            "waves is read-only — it must print no `next:` footer",
        )

    # ── rejections ─────────────────────────────────────────────────────────
    def test_no_active_milestone_rejected(self):
        self._load({"a": self._task()}, active=None)
        out, err, code = self._run("waves")
        self.assertNotEqual(code, 0)
        self.assertIn("no_active_milestone", out + err)

    def test_unknown_milestone_rejected(self):
        self._diamond()
        out, err, code = self._run("waves", "--milestone", "ghost")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_milestone", out + err)

    def test_dependency_cycle_rejected(self):
        self._load({
            "p": self._task(deps=["q"]),
            "q": self._task(deps=["p"]),
        })
        out, err, code = self._run("waves")
        self.assertNotEqual(code, 0)
        msg = out + err
        self.assertIn("dependency_cycle", msg)
        self.assertIn("p", msg)
        self.assertIn("q", msg)

    def test_transitive_blocked_dep_is_not_scheduled(self):
        # a depends on b; b depends on ext (a not-done task in another milestone).
        # b is blocked, so a (whose only dep is the blocked b) must ALSO be blocked,
        # never placed in a wave as if it were ready — blocking propagates transitively.
        self._load({
            "a": self._task(milestone="v1", deps=["b"]),
            "b": self._task(milestone="v1", deps=["ext"]),
            "ext": self._task(milestone="v2", phase="ground"),
        })
        data = self._json("waves")
        flat = [s for wave in data["waves"] for s in wave]
        self.assertNotIn("a", flat, "a's only dep (b) is blocked — a must not be scheduled")
        self.assertNotIn("b", flat)
        self.assertEqual(data["blocked"].get("b"), ["ext"])
        self.assertEqual(data["blocked"].get("a"), ["b"], "a is waiting on the blocked b")

    def test_empty_milestone_schedules_nothing(self):
        self._load({}, active="v1")
        before = self._state_md5()
        out, err, code = self._run("waves")
        self.assertEqual(code, 0, f"an empty milestone is not an error; err={err}")
        self.assertIn("nothing to schedule", out)
        self.assertEqual(self._state_md5(), before)

    def test_self_dependency_is_a_cycle(self):
        self._load({"a": self._task(deps=["a"])})
        out, err, code = self._run("waves")
        self.assertNotEqual(code, 0)
        self.assertIn("dependency_cycle", out + err)

    def test_linear_chain_critical_path(self):
        self._load({
            "a": self._task(),
            "b": self._task(deps=["a"]),
            "c": self._task(deps=["b"]),
            "d": self._task(deps=["c"]),
            "e": self._task(deps=["d"]),
        })
        data = self._json("waves")
        self.assertEqual(data["critical_path"], ["a", "b", "c", "d", "e"])
        self.assertEqual(data["critical_path_len"], 5)
        self.assertEqual(data["waves"], [["a"], ["b"], ["c"], ["d"], ["e"]])

    def test_waves_is_read_only_across_invocations(self):
        # the §4 read-only guard: state is byte-unchanged across a success AND a rejection.
        self._diamond()
        before = self._state_md5()
        self._run("waves")
        self._run("waves", "--json")
        self._run("waves", "--milestone", "ghost")   # a rejection path
        self.assertEqual(self._state_md5(), before, "no waves invocation may mutate state")


if __name__ == "__main__":
    unittest.main()
