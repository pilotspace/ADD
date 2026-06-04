#!/usr/bin/env python3
"""v11 — parallel-streams safety: the rubric's clauses + the engine behavior it leans on.

streams.md is the opt-in concurrency rubric. It changes NO add.py code, so its safety
guarantees live in two places that must not drift apart:

  1. The PROSE clauses a human/orchestrator reads — the design-for-failure rules
     (slug-routing, fresh worktree base, lease+timeout, circuit-breaker, failure
     isolation, serial integration-merge, the irreducible human floor, "a worker
     never writes shared state"). Words-exist guards so a refactor cannot quietly
     drop a safety rule from the rubric.
  2. The ENGINE behavior clause #1 depends on — advance/gate/phase route to the
     EXPLICIT <slug> and act on it; omitting the slug falls back to the single
     active_task. streams.md tells the orchestrator to "name the task every time"
     precisely because the fallback races once more than one stream is live. If
     that precedence ever flipped, every parallel orchestration would corrupt the
     wrong task while the rubric still told you it was safe.

Run: python3 -m unittest test_streams -v
"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
SKILL = _ADD_METHOD / "skill" / "add"


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class StreamsSafetyClausesTest(unittest.TestCase):
    """Each design-for-failure clause in streams.md must survive a refactor.

    Pins the SAFETY CONCEPT (distinctive lowercased substrings), not whole sentences,
    so wording can evolve but a deleted guarantee fails loudly."""

    @classmethod
    def setUpClass(cls):
        cls.low = (SKILL / "streams.md").read_text(encoding="utf-8").lower()

    def test_slug_routing_names_the_task_every_time(self):
        self.assertIn("explicit", self.low)
        self.assertIn("name the task every time", self.low,
                      "the rubric must keep the always-pass-the-slug rule")
        self.assertIn("race", self.low,
                      "the rubric must keep the WHY: the active_task fallback races across streams")

    def test_fresh_worktree_base_clause(self):
        self.assertIn("fresh worktree base", self.low,
                      "the worktree-base safety step must remain")
        self.assertIn("base == head", self.low,
                      "must keep the concrete check: worker base == orchestrator HEAD")

    def test_lease_and_timeout_clause(self):
        self.assertIn("lease", self.low)
        self.assertIn("timeout", self.low,
                      "a dead worker's claim must be releasable — lease + timeout")

    def test_circuit_breaker_clause(self):
        self.assertIn("circuit-breaker", self.low,
                      "repeated worker failure must fall back to sequential, not keep fanning out")

    def test_failure_isolation_clause(self):
        self.assertIn("failure isolates", self.low,
                      "a STOP-and-escalate must block only its own task, not siblings")

    def test_serial_integration_merge_clause(self):
        self.assertIn("merge is serial", self.low)
        self.assertIn("integration", self.low,
                      "merged-green tasks can still conflict — the integration Verify must stay")

    def test_irreducible_human_floor_clause(self):
        self.assertIn("one human approval per task", self.low,
                      "the contract-seam floor must never be engineered away")
        self.assertIn("never drops to zero", self.low)

    def test_worker_never_writes_shared_state(self):
        self.assertIn("never write shared state", self.low,
                      "the worker/orchestrator write boundary is the core race guard")


class SlugRoutingPrecedenceTest(unittest.TestCase):
    """advance/gate/phase act on the EXPLICIT slug; omitting it uses active_task.

    This is the engine contract streams.md §'Who writes what' depends on. Two tasks
    exist; 'b' is active (created last). Naming 'a' must mutate ONLY 'a' and must
    leave active_task untouched — proving the orchestrator can drive any stream
    without first switching focus."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-streams-route-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "a"])   # auto-linked to mvp
        add.main(["new-task", "b"])   # active_task is now 'b'
        self.state_path = Path(self.tmp) / ".add" / "state.json"

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def test_active_task_is_b_after_setup(self):
        # premise check: the LAST-created task is active, so naming 'a' is the non-trivial path
        self.assertEqual(self._state()["active_task"], "b")

    def test_phase_routes_to_explicit_slug_not_active(self):
        code, _, _ = _run(["phase", "verify", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "verify", "the NAMED task must change")
        self.assertEqual(st["tasks"]["b"]["phase"], "specify", "the active task must NOT change")
        self.assertEqual(st["active_task"], "b", "phase <slug> must not steal focus from active_task")

    def test_advance_routes_to_explicit_slug_not_active(self):
        code, _, _ = _run(["advance", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "scenarios", "advance must step the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "specify", "the active task must NOT step")
        self.assertEqual(st["active_task"], "b")

    def test_gate_routes_to_explicit_slug_not_active(self):
        _run(["phase", "verify", "a"])          # bring 'a' to verify so PASS is legal
        code, _, _ = _run(["gate", "PASS", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "done")
        self.assertEqual(st["tasks"]["a"]["gate"], "PASS", "gate must record on the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "specify", "the active task must be untouched")
        self.assertEqual(st["tasks"]["b"].get("gate", "none"), "none", "no gate may land on 'b'")
        self.assertEqual(st["active_task"], "b")

    def test_omitted_slug_falls_back_to_active_task(self):
        # the documented fallback (and the race premise): no slug => act on active_task ('b')
        code, _, _ = _run(["advance"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["b"]["phase"], "scenarios", "omitted slug must step the active task")
        self.assertEqual(st["tasks"]["a"]["phase"], "specify", "the non-active task must be untouched")


if __name__ == "__main__":
    unittest.main(verbosity=2)
