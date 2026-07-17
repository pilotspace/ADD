#!/usr/bin/env python3
"""v11 — parallel-streams safety: the ENGINE behavior the concurrency rubric leans on.

streams.md is the opt-in concurrency rubric; it changes NO add.py code. The one safety
guarantee that IS engine-enforced — and thus tested here — is slug routing: advance/gate/
phase act on the EXPLICIT <slug>, and omitting it falls back to the single active_task.
streams.md tells the orchestrator to name the task every time precisely because that
fallback races once more than one stream is live. If the precedence ever flipped, every
parallel orchestration would corrupt the wrong task while the rubric still read as safe.

(The rubric's prose clauses — design-for-failure rules, the human floor — are no longer
word-pinned here: doc wording is free to evolve; only the engine contract is guarded.)

Run: python3 -m unittest test_streams -v
"""
import contextlib
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
SKILL = _ADD_METHOD / "skill" / "add"

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class SlugRoutingPrecedenceTest(unittest.TestCase):
    """advance/gate/phase act on the EXPLICIT slug; omitting it uses active_task.

    This is the engine contract streams.md §'Who writes what' depends on. Two tasks
    exist; 'b' is active (created last). Naming 'a' must mutate ONLY 'a' and must
    leave active_task untouched — proving the orchestrator can drive any stream
    without first switching focus."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-streams-route-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
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

    def _freeze(self, slug):
        """Stamp §3 FROZEN + a well-formed flag so `advance` (no admin override) can
        actually cross the slug's direction->build gate. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def test_active_task_is_b_after_setup(self):
        # premise check: the LAST-created task is active, so naming 'a' is the non-trivial path
        self.assertEqual(self._state()["active_task"], "b")

    def test_phase_routes_to_explicit_slug_not_active(self):
        code, _, _ = _run(["phase", "verify", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "verify", "the NAMED task must change")
        self.assertEqual(st["tasks"]["b"]["phase"], "direction", "the active task must NOT change")
        self.assertEqual(st["active_task"], "b", "phase <slug> must not steal focus from active_task")

    def test_advance_routes_to_explicit_slug_not_active(self):
        self._freeze("a")                        # a bare advance now needs a frozen §3 to cross
        code, _, _ = _run(["advance", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "build", "advance must step the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "direction", "the active task must NOT step")
        self.assertEqual(st["active_task"], "b")

    def test_gate_routes_to_explicit_slug_not_active(self):
        _run(["phase", "verify", "a"])          # bring 'a' to verify so PASS is legal
        code, _, _ = _run(["gate", "PASS", "a"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["a"]["phase"], "done")
        self.assertEqual(st["tasks"]["a"]["gate"], "PASS", "gate must record on the NAMED task")
        self.assertEqual(st["tasks"]["b"]["phase"], "direction", "the active task must be untouched")
        self.assertEqual(st["tasks"]["b"].get("gate", "none"), "none", "no gate may land on 'b'")
        self.assertEqual(st["active_task"], "b")

    def test_omitted_slug_falls_back_to_active_task(self):
        # the documented fallback (and the race premise): no slug => act on active_task ('b')
        self._freeze("b")                        # a bare advance now needs a frozen §3 to cross
        code, _, _ = _run(["advance"])
        self.assertEqual(code, 0)
        st = self._state()
        self.assertEqual(st["tasks"]["b"]["phase"], "build", "omitted slug must step the active task")
        self.assertEqual(st["tasks"]["a"]["phase"], "direction", "the non-active task must be untouched")


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


class WorkerStrategyPullTest(unittest.TestCase):
    """streams-strategy-pull: streams.md's worker-contract fence carries a <strategy> block that
    points the worker at the task's §5 (mirroring advisor.md). It must stay INSIDE the fence."""

    @classmethod
    def setUpClass(cls):
        cls.text = (SKILL / "streams.md").read_text(encoding="utf-8")

    def test_strategy_block_present_and_names_section5(self):
        block = re.search(r"<strategy>(.*?)</strategy>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "streams.md worker contract missing the <strategy> block")
        self.assertIn("§5", block.group(1), "the <strategy> block must point at the task's §5")
        # placed inside the worker contract: between </persona> and <touch_boundary>
        self.assertLess(self.text.index("</persona>"), self.text.index("<strategy>"))
        self.assertLess(self.text.index("</strategy>"), self.text.index("<touch_boundary>"))

    def test_strategy_stays_fenced(self):
        stripped = _FENCE_RE.sub("", self.text)
        self.assertNotIn("<strategy>", stripped,
                         "<strategy> leaked OUTSIDE the worker-contract code fence")

    def test_strategy_block_is_preferred_not_hard(self):
        # strategy-soft-not-hard: §5 is the worker's PREFERRED plan it self-improves on and
        # reports for audit — NOT a hard "do not invent your own" directive.
        block = re.search(r"\n<strategy>\n(.*?)\n</strategy>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "no line-anchored <strategy> block")
        body = block.group(1)
        self.assertIn("not a hard rule", body, "block must frame §5 as preferred, not a hard rule")
        self.assertIn("Improve on it", body, "block must invite the worker to self-improve the plan")
        self.assertIn("report the strategy", body, "block must ask the worker to report the strategy used")
        self.assertIn("audit", body, "the report must feed the §5 audit trail")
        self.assertNotIn("do not invent your own", self.text,
                         "the rigid 'do not invent your own' phrasing must be gone")

    def test_block_byte_identical_to_advisor(self):
        # the two spawn homes must carry the SAME <strategy> block (no drift -> block_drift)
        adv = (SKILL / "advisor.md").read_text(encoding="utf-8")
        pat = r"\n<strategy>\n.*?\n</strategy>"
        s_block = re.search(pat, self.text, re.DOTALL)
        a_block = re.search(pat, adv, re.DOTALL)
        self.assertIsNotNone(s_block, "streams.md <strategy> block not found")
        self.assertIsNotNone(a_block, "advisor.md <strategy> block not found")
        self.assertEqual(s_block.group(0), a_block.group(0),
                         "advisor.md and streams.md <strategy> blocks have drifted")


if __name__ == "__main__":
    unittest.main(verbosity=2)
