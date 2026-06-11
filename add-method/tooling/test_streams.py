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
import hashlib
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
        self.assertEqual(st["tasks"]["b"]["phase"], "ground", "the active task must NOT change")
        self.assertEqual(st["active_task"], "b", "phase <slug> must not steal focus from active_task")

    def test_advance_routes_to_explicit_slug_not_active(self):
        code, _, _ = _run(["advance", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "specify", "advance must step the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "ground", "the active task must NOT step")
        self.assertEqual(st["active_task"], "b")

    def test_gate_routes_to_explicit_slug_not_active(self):
        _run(["phase", "verify", "a"])          # bring 'a' to verify so PASS is legal
        code, _, _ = _run(["gate", "PASS", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "done")
        self.assertEqual(st["tasks"]["a"]["gate"], "PASS", "gate must record on the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "ground", "the active task must be untouched")
        self.assertEqual(st["tasks"]["b"].get("gate", "none"), "none", "no gate may land on 'b'")
        self.assertEqual(st["active_task"], "b")

    def test_omitted_slug_falls_back_to_active_task(self):
        # the documented fallback (and the race premise): no slug => act on active_task ('b')
        code, _, _ = _run(["advance"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["b"]["phase"], "specify", "omitted slug must step the active task")
        self.assertEqual(st["tasks"]["a"]["phase"], "ground", "the non-active task must be untouched")


# ── wave-protocol-runtime: merge-time fork-base shift + worker commits its report ──
# v19 wave deltas #7 (merge-time fork-base) + #8 (worker commits SUMMARY.md). streams.md must
# MIRROR the folded CONVENTIONS runtime-exception: on a spawn-time-worktree runner the pre-spawn
# rev-parse cell is unsatisfiable, so the `unverified_fork_base` check SHIFTS to worker step-0
# (sync + re-echo) verified at MERGE-time; and the worker `<return>` contract must COMMIT its
# SUMMARY.md/deltas.md. Token-presence guards (phrasing free, behaviour locked) + ×3 parity.
_REPO = _ADD_METHOD.parent
_STREAMS_TREES = (
    SKILL / "streams.md",                                                              # canonical
    _REPO / ".claude" / "skills" / "add" / "streams.md",                               # dogfood
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "streams.md",  # bundle
)


class WaveProtocolRuntimeTest(unittest.TestCase):
    """streams.md states the merge-time fork-base shift for spawn-time runners and requires the
    worker to COMMIT its report — mirroring the folded CONVENTIONS runtime-exception — while the
    pre-spawn rule is PRESERVED and the ×3 copies stay byte-identical. RED until the build amends
    streams.md (the 2 new-behaviour tests); the 2 invariant tests stay green throughout."""

    @classmethod
    def setUpClass(cls):
        cls.low = (SKILL / "streams.md").read_text(encoding="utf-8").lower()

    def test_merge_time_fork_base_shift_stated(self):        # Scenario 1 / Must 1
        self.assertIn("merge-time", self.low,
                      "the fork-base check must SHIFT to merge-time on a spawn-time-worktree runner")
        self.assertIn("step-0", self.low,
                      "the shift names the worker step-0 (sync-to-base + re-echo)")
        self.assertIn("unverified_fork_base", self.low,
                      "the shifted check keeps its refusal code — it shifts, it never skips")

    def test_worker_commits_its_report(self):                # Scenario 2 / Must 2
        self.assertIn("commit summary.md", self.low,
                      "the worker <return> contract must require COMMITTING SUMMARY.md, not just writing it")
        self.assertIn("deltas.md", self.low,
                      "the worker commits deltas.md alongside SUMMARY.md")

    def test_pre_spawn_rule_preserved(self):                 # Scenario 4 / Must 4 · Reject 1
        self.assertIn("fresh worktree base", self.low,
                      "the pre-spawn rule stays the DEFAULT — deleting it is fork_base_rule_weakened")
        self.assertIn("base == head", self.low,
                      "the concrete pre-spawn check (worker base == orchestrator HEAD) must remain")

    def test_three_streams_copies_byte_identical(self):      # Scenario 3 / Must 3 · Reject 2
        present = [p for p in _STREAMS_TREES if p.exists()]
        self.assertEqual(len(present), 3,
                         f"all 3 streams.md copies must exist: {[str(p) for p in _STREAMS_TREES]}")
        hashes = {hashlib.md5(p.read_bytes()).hexdigest() for p in present}
        self.assertEqual(len(hashes), 1, f"streams.md mirror_drift across the 3 copies: {hashes}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
