#!/usr/bin/env python3
"""Red/green tests for kickoff truth (task kickoff-truth, frozen contract v1):
the engine's own stdout stops generating wasted calls (evidence: the 2026-07-13
transcript audit of loop2-lever rep0/1/2 — milestone-first kickoff bait, 6-11
orientation calls, 12-21% byte-identical duplicate failures).

  M1 — `init`'s kickoff block names the single-task lane (`--oneshot`) BEFORE
       the milestone lines.
  M2 — `new-task` stdout ends with the task's FULL remaining engine-call recipe
       (advance --to plan · freeze --by <name> · advance x3 · gate PASS) on
       every lane (milestone-bound · --fast · --oneshot).
  M3 — a byte-identical failing call repeated consecutively gets a short-circuit
       hint line; a DIFFERENT failure gets none; an intervening success clears it.
  R  — regression pin: `advance --to plan` on a fresh unfilled task succeeds
       (the old skip bait is dead and stays dead).

One test per §1 Must/Reject. Run: python3 -m unittest test_kickoff_truth -v
"""
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_HINT_MARK = "already failed with the same error"


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors the sibling suites'
    fixture conventions — test_first_call_ergonomics.py's _Harness — duplicated
    here per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-kt-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    # ---- CLI helpers -------------------------------------------------------
    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _ok(self, *argv):
        text, code = self._run(*argv)
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _init(self):
        return self._ok("init", "--name", "demo", "--stage", "mvp")

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))


class KickoffLaneTest(_Harness):
    """M1 — the kickoff block leads with the single-task lane."""

    def test_init_kickoff_names_single_task_lane_first(self):
        out = self._init()
        one = out.index("headless, single task:")
        ms = out.index("headless, multi-task:")
        self.assertLess(one, ms,
                        "the single-task kickoff must print BEFORE the milestone kickoff lines "
                        "(rep2 — the cheapest measured run — skipped the milestone)")


class RecipeTest(_Harness):
    """M2 — new-task hands the full remaining call recipe, every lane."""

    _MARKS = ("freeze --by", "--cross", "gate PASS")

    def _assert_recipe(self, out, lane):
        self.assertIn("recipe", out.lower(), f"{lane}: no recipe block in new-task stdout")
        for mark in self._MARKS:
            self.assertIn(mark, out, f"{lane}: recipe is missing `{mark}`")
        # phase-collapse-3: the front is ONE phase — freeze --cross absorbs the whole
        # direction->build crossing and a completing gate absorbs build->verify, so the
        # recipe is the two-call walk with no bookkeeping `advance` left to list.
        tail = out[out.lower().index("recipe"):]
        self.assertNotIn("add.py advance", tail,
                         f"{lane}: recipe must not list a bookkeeping advance (none remain)")

    def test_new_task_emits_full_recipe_milestone_lane(self):
        self._init()
        self._ok("lock", "--force")
        self._ok("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        out = self._ok("new-task", "t-norm", "--title", "T", "--milestone", "m")
        self._assert_recipe(out, "milestone lane")

    def test_new_task_emits_full_recipe_fast_and_oneshot_lanes(self):
        self._init()
        self._ok("lock", "--force")
        out = self._ok("new-task", "t-one", "--title", "T")
        self._assert_recipe(out, "--oneshot lane")
        self._ok("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        out = self._ok("new-task", "t-fast", "--title", "T", "--milestone", "m")
        self._assert_recipe(out, "--fast lane")

    def test_later_task_recipe_is_compact_not_re_annotated(self):
        # recipe-dedup (engine-output-trim): the FIRST task of a project teaches the
        # annotated flow; a LATER task in the same project names the SAME flow compactly
        # — the agent already read the per-step prose once. The flow floor still holds
        # (all marks + both advances, asserted by _assert_recipe on BOTH), so there is
        # no rediscovery/--help backfire — only the repeated annotation prose is dropped.
        self._init()
        self._ok("lock", "--force")
        first = self._ok("new-task", "t1", "--title", "T")
        second = self._ok("new-task", "t2", "--title", "T")
        self._assert_recipe(first, "first task")   # full flow named
        self._assert_recipe(second, "later task")  # full flow STILL named (no backfire)
        self.assertIn("[approval —", first,
                      "the first task must carry the teaching annotations")
        self.assertNotIn("[approval —", second,
                         "a later task must not repeat the per-step annotations")

        def _recipe_span(o):
            return len(o[o.lower().index("recipe"):])
        self.assertLess(_recipe_span(second), _recipe_span(first),
                        "the deduped later recipe must be shorter than the annotated first")


class DupFailureTest(_Harness):
    """M3 — consecutive byte-identical failures short-circuit; nothing else does."""

    def _fail(self, *argv):
        text, code = self._run(*argv)
        self.assertNotEqual(code, 0, f"{argv} unexpectedly succeeded: {text}")
        return text

    @staticmethod
    def _tree_snapshot(root: Path) -> dict:
        return {str(p.relative_to(root)): p.read_bytes()
                for p in root.rglob("*") if p.is_file()}

    def test_repeated_identical_failing_call_gets_hint(self):
        self._init()
        pre = self._tree_snapshot(self.tmp / ".add")
        first = self._fail("gate", "PASS")            # no active task -> error
        self.assertNotIn(_HINT_MARK, first, "hint must not fire on the FIRST failure")
        second = self._fail("gate", "PASS")           # byte-identical repeat
        self.assertIn(_HINT_MARK, second,
                      "an identical consecutive failure must say it already failed")
        # contract v2: the hint state lives OUTSIDE the tree — a rejected command
        # writes ZERO bytes to .add/ (the engine's reject-writes-nothing floor)
        self.assertEqual(pre, self._tree_snapshot(self.tmp / ".add"),
                         "a failing call must leave the .add tree byte-identical")

    def test_different_failure_gets_no_hint(self):
        self._init()
        self._fail("gate", "PASS")
        other = self._fail("freeze", "--by", "x")     # different argv, also fails
        self.assertNotIn(_HINT_MARK, other, "a DIFFERENT failure must not short-circuit")

    def test_success_clears_dup_state(self):
        self._init()
        self._fail("gate", "PASS")
        self._ok("status")                            # intervening success clears
        again = self._fail("gate", "PASS")
        self.assertNotIn(_HINT_MARK, again,
                         "a success between two identical failures must clear the state")


class BaitDeadRegressionTest(_Harness):
    """R — the measured skip bait stays dead: --to plan succeeds on a fresh task.
    phase-collapse-3: `plan` is now a legacy alias for `direction` (the sole front
    phase), so the call succeeds as a friendly no-op rather than landing a new phase."""

    def test_advance_to_plan_unfilled_succeeds(self):
        self._init()
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T")
        self._ok("advance", "--to", "plan")
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "direction")


if __name__ == "__main__":
    unittest.main()
