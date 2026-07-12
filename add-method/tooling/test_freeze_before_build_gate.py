#!/usr/bin/env python3
"""Red/green tests for the freeze-before-build gate (milestone fast-lane, task `freeze-before-build-gate`).

Makes the "collapse-never-skip" floor REAL: a task may NOT cross tests->build while its §3 contract
is unfrozen. The guard sits at the `nxt == "build"` crossing in `_build_entry`, BEFORE the existing
build-expectations gate. As of `freeze-gate-universal` (flow-honesty) the gate is UNIVERSAL — it
fires for EVERY task, not just `--await-confirm` / `--fast` ones; the recorded `--skip-freeze` escape
is the only bypass (see test_freeze_gate_universal). Scenarios 3 & 4 below were INVERTED accordingly.

Run: python3 -m unittest test_freeze_before_build_gate -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

PLACEHOLDER_BE = "- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>"
FILLED_BE = "- [x] the command prints the expected line — confirmed by the green test"


class FreezeBeforeBuildGateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-fbg-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])     # grandfathered lock so build-entry is allowed

    def tearDown(self):
        os.chdir(self._cwd)

    # ── helpers ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(argv)

    @staticmethod
    def _die_stderr(argv):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    add.main(argv)
            except SystemExit as e:
                return e.code, err.getvalue()
        raise AssertionError(f"expected SystemExit from {argv}")

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _task(self, slug="t"):
        return self._state()["tasks"][slug]

    def _ms_path(self, slug):
        return Path(self.tmp) / ".add" / "milestones" / slug / "MILESTONE.md"

    def _task_path(self, slug="t"):
        return Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"

    def _fill_contracts(self, ms):
        p = self._ms_path(ms)
        p.write_text(p.read_text().replace(
            "- <contract name> -> owning task <slug>",
            "- real contract -> owning task t"), encoding="utf-8")

    def _freeze(self, slug="t"):
        """Stamp §3 FROZEN — the artifact-observable freeze signal `_contract_frozen` reads.
        Also surfaces a well-formed least-sure flag so the EXISTING `unflagged_freeze` build-entry
        gate passes through (a frozen §3 must name its lowest-confidence part)."""
        p = self._task_path(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-23.\n"
            "Least-sure flag surfaced at freeze: [contract] the renamed field may "
            "break a caller — cost: a follow-up migration"), encoding="utf-8")

    def _fill_build_expectations(self, slug="t"):
        p = self._task_path(slug)
        t = p.read_text()
        t = t.replace(PLACEHOLDER_BE, FILLED_BE)
        t = t.replace("- [ ] <another observable outcome> — confirmed by <evidence seen>",
                      "- [x] the gate passes through a frozen contract — confirmed by the green test")
        p.write_text(t, encoding="utf-8")

    def _to_plan(self, slug="t"):
        for _ in range(2):   # specify -> scenarios -> plan
            self._quiet(["advance", slug])

    def _optedin_task_at_plan(self, slug="t", ms="mvp"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp", "--await-confirm"])
        self._fill_contracts(ms)
        self._quiet(["milestone-confirm", ms])
        self._quiet(["new-task", slug])
        self._to_plan(slug)

    def _plain_task_at_plan(self, slug="t", ms="plain"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])   # no --await-confirm
        self._quiet(["new-task", slug])
        self._to_plan(slug)

    def _force_to_tests(self, slug="t"):
        """Admin override: force phase=tests directly, WITHOUT crossing the (plan-phase-core)
        plan->tests freeze gate — `phase <n>` for a non-build/-plan target runs no guard.
        Arranges the grandfather scenario this file's OWN target crossing (tests->build, inside
        `_build_entry`) must still catch: a pre-plan-phase-core record, or a lost/never-granted
        skip marker, sitting at `tests` with a DRAFT §3. The plan->tests front door itself is
        covered in test_freeze_gate_universal."""
        self._quiet(["phase", "tests", slug])

    # ── scenario 1: opted-in + DRAFT §3 -> refused, stays at tests ───────────────────────
    def test_optedin_unfrozen_blocks_build(self):
        self._optedin_task_at_plan()
        self._force_to_tests()
        code, err = self._die_stderr(["advance", "t"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task().get("phase"), "tests", "a refused advance leaves phase=tests")
        self.assertFalse((Path(self.tmp) / ".add" / "tasks" / "t" / "scope-snapshot.json").exists(),
                         "validate-then-write: no scope snapshot on a refused advance")

    # ── scenario 2: opted-in + FROZEN §3 -> advances to build ────────────────────────────
    def test_optedin_frozen_advances(self):
        self._optedin_task_at_plan()
        self._freeze()
        self._fill_build_expectations()   # clear the sibling build-expectations gate too
        self._quiet(["advance", "t"])     # plan -> tests (frozen, passes)
        self._quiet(["advance", "t"])     # tests -> build
        self.assertEqual(self._task().get("phase"), "build")

    # ── scenario 3: plain (no-key) milestone + DRAFT §3 -> now BLOCKED (universal gate) ───
    # INVERTED by `freeze-gate-universal` (flow-honesty): the gate is no longer opt-in, so a
    # plain-milestone DRAFT §3 is refused at tests->build (full coverage in test_freeze_gate_universal,
    # which also covers the plan-phase-core FRONT-door refusal at plan->tests).
    def test_plain_milestone_unfrozen_blocks(self):
        self._plain_task_at_plan()
        self._force_to_tests()
        code, err = self._die_stderr(["advance", "t"])   # DRAFT §3 — universal gate refuses
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task().get("phase"), "tests")

    # ── scenario 4: no milestone + DRAFT §3 -> now BLOCKED (universal gate) ───────────────
    def test_no_milestone_unfrozen_blocks(self):
        self._quiet(["new-task", "loose"])   # no active milestone -> milestone-less
        self.assertIsNone(self._task("loose").get("milestone"))
        self._to_plan("loose")
        self._force_to_tests("loose")
        code, err = self._die_stderr(["advance", "loose"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task("loose").get("phase"), "tests")

    # ── scenario 5: freeze precedes build-expectations (DRAFT §3 + empty §6) ──────────────
    def test_freeze_precedes_build_expectations(self):
        self._optedin_task_at_plan()
        self._force_to_tests()             # DRAFT §3 AND placeholder §6
        code, err = self._die_stderr(["advance", "t"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertNotIn("build_expectations_unfilled", err,
                         "the freeze gate fires FIRST — build-expectations is never reached")

    # ── precedence proof in reverse: frozen §3 + empty §6 -> build-expectations now fires ─
    def test_frozen_then_build_expectations_gate_takes_over(self):
        self._optedin_task_at_plan()
        self._freeze()                     # §3 frozen, but §6 left as placeholder
        self._quiet(["advance", "t"])      # plan -> tests (frozen, passes)
        code, err = self._die_stderr(["advance", "t"])
        self.assertEqual(code, 1)
        self.assertIn("build_expectations_unfilled", err,
                      "once §3 is frozen the NEXT gate (build-expectations) takes over")


if __name__ == "__main__":
    unittest.main()
