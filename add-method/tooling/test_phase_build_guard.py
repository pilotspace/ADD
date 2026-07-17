#!/usr/bin/env python3
"""Red/green tests for the phase-build build-entry guard (task `phase-build-guard`, milestone
audit-hardening — deep-audit finding F4).

`add.py phase build <slug>` is the human admin override; today it sets phase=build with NONE of
the guards `cmd_advance` runs at the direction->build crossing, so a task can reach build with a
DRAFT §3 and NO tamper-tripwire — and verify's `_tamper_guard` then returns silently (a gamed
green can record PASS). The fix extracts cmd_advance's `nxt == "build"` block into a shared
`_build_entry` helper that BOTH commands call: `phase build` becomes equivalent to advancing into
build — the freeze gate, the unflagged-freeze check + flag stamp, the tamper-tripwire snapshot,
and the §5 scope snapshot all run.

A plain / no-milestone task is NOT freeze-gated for build-expectations (that gate is opt-in only),
but DOES get the same freeze gate + tripwire baseline as an opted-in task. The heal loop is exempt
by construction (`_heal_or_escalate` sets phase=build directly, never via cmd_phase).

phase-collapse-3: the front (specify · plan · tests) collapsed into ONE phase `direction`, so a
DRAFT §3 task simply SITS at `direction` — there is no longer a separate "reach tests" bookkeeping
hop to force before exercising `phase build`; the admin override is tried directly from a fresh
task at `direction`.

Run: python3 -m unittest test_phase_build_guard -v
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add

PLACEHOLDER_BE = "- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>"
FILLED_BE = "- [x] the command prints the expected line — confirmed by the green test"


class PhaseBuildGuardTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-pbg-")
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── helpers (mirror test_freeze_before_build_gate) ───────────────────────────────────
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
        return Path(self.tmp) / ".add" / "tasks" / slug / "PLAN.md"

    def _fill_contracts(self, ms):
        p = self._ms_path(ms)
        p.write_text(p.read_text().replace(
            "- <contract name> -> owning task <slug>",
            "- real contract -> owning task t"), encoding="utf-8")

    def _freeze(self, slug="t"):
        """FROZEN + a well-formed least-sure flag (clears the unflagged_freeze gate)."""
        p = self._task_path(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-25.\n"
            "Least-sure flag surfaced at freeze: [contract] the renamed field may "
            "break a caller — cost: a follow-up migration"), encoding="utf-8")

    def _freeze_unflagged(self, slug="t"):
        """FROZEN but WITHOUT a least-sure flag — must trip unflagged_freeze."""
        p = self._task_path(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-25."), encoding="utf-8")

    def _fill_build_expectations(self, slug="t"):
        p = self._task_path(slug)
        t = p.read_text()
        t = t.replace(PLACEHOLDER_BE, FILLED_BE)
        t = t.replace("- [ ] <another observable outcome> — confirmed by <evidence seen>",
                      "- [x] the gate passes through a frozen contract — confirmed by the green test")
        p.write_text(t, encoding="utf-8")

    # phase-collapse-3: a fresh task is BORN at `direction` — no bookkeeping hop is needed to
    # reach the freeze seam, so these helpers just arrange the task AT direction.
    def _optedin_task_at_direction(self, slug="t", ms="mvp"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp", "--await-confirm"])
        self._fill_contracts(ms)
        self._quiet(["milestone-confirm", ms])
        self._quiet(["new-task", slug])

    def _plain_task_at_direction(self, slug="t", ms="plain"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])
        self._quiet(["new-task", slug])

    def _fast_task_at_direction(self, slug="t"):
        self._quiet(["new-task", slug, "--fast"])

    # ── scenarios ────────────────────────────────────────────────────────────────────────
    def test_optedin_unfrozen_blocks_phase_build(self):
        self._optedin_task_at_direction()
        code, err = self._die_stderr(["phase", "build", "t"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task().get("phase"), "direction",
                         "a refused `phase build` leaves phase=direction (validate-then-write)")
        self.assertNotIn("tripwire", self._task(), "no tripwire written on a refusal")

    def test_optedin_frozen_phase_build_arms_tripwire(self):
        self._optedin_task_at_direction()
        self._freeze()
        self._fill_build_expectations()
        self._quiet(["phase", "build", "t"])
        t = self._task()
        self.assertEqual(t.get("phase"), "build")
        self.assertIn("tripwire", t, "phase build must arm the tamper tripwire")
        self.assertTrue(t.get("flag_verified"), "flag_verified stamped on a flagged freeze")

    def test_unflagged_freeze_blocks_phase_build(self):
        self._optedin_task_at_direction()
        self._freeze_unflagged()
        self._fill_build_expectations()
        code, err = self._die_stderr(["phase", "build", "t"])
        self.assertEqual(code, 1)
        self.assertIn("unflagged_freeze", err)
        self.assertEqual(self._task().get("phase"), "direction")

    # freeze-gate-universal (flow-honesty): a plain task is now freeze-gated even via the `phase
    # build` admin override, so reaching build (and arming the tripwire) requires a FROZEN §3.
    def test_plain_milestone_frozen_arms_tripwire(self):
        self._plain_task_at_direction()
        self._freeze()                            # universal freeze gate: §3 must be frozen
        self._quiet(["phase", "build", "t"])      # frozen §3 -> the override runs the full gate stack
        t = self._task()
        self.assertEqual(t.get("phase"), "build")
        self.assertIn("tripwire", t, "the override arms the same tripwire baseline as advance")

    # the override is NOT a backdoor: a plain UNFROZEN task is blocked at `phase build` too
    # (the universal gate, matching test_fast_unfrozen_blocks_phase_build for the fast case).
    def test_plain_milestone_unfrozen_blocks_phase_build(self):
        self._plain_task_at_direction()
        code, err = self._die_stderr(["phase", "build", "t"])   # DRAFT §3 -> universal gate refuses
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task().get("phase"), "direction")

    def test_fast_unfrozen_blocks_phase_build(self):
        self._fast_task_at_direction()
        code, err = self._die_stderr(["phase", "build", "t"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task().get("phase"), "direction")

    def test_non_build_target_never_gated(self):
        # a non-build target (e.g. `verify`) is a bare admin phase-set with NO guard — even a
        # DRAFT §3, never-frozen task can be pointed there, and it takes no tripwire snapshot.
        # Only `build` is gated (the direction->build crossing is the one seam that matters).
        self._optedin_task_at_direction()
        self._quiet(["phase", "verify", "t"])
        t = self._task()
        self.assertEqual(t.get("phase"), "verify")
        self.assertNotIn("tripwire", t, "a non-build target takes no tripwire snapshot")

    def test_advance_into_build_unchanged(self):
        # parity guard: the extraction must leave `advance` into build behaving exactly as before
        self._optedin_task_at_direction()
        self._freeze()
        self._fill_build_expectations()
        self._quiet(["advance", "t"])
        t = self._task()
        self.assertEqual(t.get("phase"), "build")
        self.assertIn("tripwire", t)
        self.assertTrue(t.get("flag_verified"))


if __name__ == "__main__":
    unittest.main()
