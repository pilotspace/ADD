#!/usr/bin/env python3
"""Red/green tests for the UNIVERSAL freeze gate (milestone flow-honesty, task `freeze-gate-universal`).

Makes the freeze gate UNIVERSAL: `contract_not_frozen` fires for EVERY task at the tests->build
crossing — not just `--await-confirm` / `--fast` ones — closing audit finding H1 (the decision point
was engine-enforced for only a subset of tasks). An explicit, RECORDED `--skip-freeze` escape lets a
DRAFT-§3 task cross while writing a `freeze_skipped` marker the `audit` can surface (no silent skip).
Grandfather: the gate is evaluated only at the live `nxt == "build"` crossing, so a task already at /
after build is never retro-redded.

Run: python3 -m unittest test_freeze_gate_universal -v
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


class UniversalFreezeGateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ufg-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])     # grandfathered lock so build-entry is allowed

    def tearDown(self):
        os.chdir(self._cwd)

    # ── harness ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(argv)

    @staticmethod
    def _capture(argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            add.main(argv)
        return out.getvalue()

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

    def _write_state(self, state):
        (Path(self.tmp) / ".add" / "state.json").write_text(json.dumps(state), encoding="utf-8")

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
        p = self._task_path(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] the field may "
            "break a caller — cost: a follow-up migration"), encoding="utf-8")

    def _fill_build_expectations(self, slug="t"):
        p = self._task_path(slug)
        t = p.read_text()
        t = t.replace(PLACEHOLDER_BE, FILLED_BE)
        t = t.replace("- [ ] <another observable outcome> — confirmed by <evidence seen>",
                      "- [x] the gate passes through a frozen contract — confirmed by the green test")
        p.write_text(t, encoding="utf-8")

    def _to_tests(self, slug="t"):
        for _ in range(4):   # ground -> specify -> scenarios -> contract -> tests
            self._quiet(["advance", slug])

    def _plain_task_at_tests(self, slug="t", ms="plain"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])   # NO --await-confirm
        self._quiet(["new-task", slug])
        self._to_tests(slug)

    def _no_milestone_task_at_tests(self, slug="loose"):
        self._quiet(["new-task", slug])      # no active milestone -> milestone-less
        self._to_tests(slug)

    def _optedin_task_at_tests(self, slug="t", ms="mvp"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp", "--await-confirm"])
        self._fill_contracts(ms)
        self._quiet(["milestone-confirm", ms])
        self._quiet(["new-task", slug])
        self._to_tests(slug)

    def _fast_task_at_tests(self, slug="f"):
        self._quiet(["new-task", slug, "--fast"])
        self._to_tests(slug)

    # ── universal gate: PLAIN-milestone DRAFT §3 is now BLOCKED (inverts old behavior) ────
    def test_plain_milestone_unfrozen_blocks(self):
        self._plain_task_at_tests()
        code, err = self._die_stderr(["advance", "t"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task().get("phase"), "tests", "a refused advance leaves phase=tests")
        self.assertFalse((Path(self.tmp) / ".add" / "tasks" / "t" / "scope-snapshot.json").exists(),
                         "validate-before-write: no snapshot on a refused advance")

    # ── universal gate: NO-milestone DRAFT §3 is now BLOCKED (inverts old behavior) ───────
    def test_no_milestone_unfrozen_blocks(self):
        self._no_milestone_task_at_tests()
        self.assertIsNone(self._task("loose").get("milestone"))
        code, err = self._die_stderr(["advance", "loose"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task("loose").get("phase"), "tests")

    # ── happy path unchanged: FROZEN §3 advances, no skip marker ─────────────────────────
    def test_frozen_advances_without_marker(self):
        self._plain_task_at_tests()
        self._freeze()
        self._fill_build_expectations()
        self._quiet(["advance", "t"])
        self.assertEqual(self._task().get("phase"), "build")
        self.assertNotIn("freeze_skipped", self._task(), "a clean freeze records no skip marker")

    # ── escape: --skip-freeze crosses a DRAFT §3 AND records the marker ───────────────────
    def test_skip_freeze_allows_and_records(self):
        self._plain_task_at_tests()
        self._fill_build_expectations()      # clear the sibling gate; freeze is what we're skipping
        self._quiet(["advance", "t", "--skip-freeze"])
        self.assertEqual(self._task().get("phase"), "build")
        mark = self._task().get("freeze_skipped")
        self.assertIsInstance(mark, dict, "skip is RECORDED, not silent")
        self.assertIn("by", mark)
        self.assertIn("at", mark)
        self.assertEqual(mark.get("from_phase"), "tests")

    # ── escape never auto-freezes §3 (never pre-stamp a human freeze) ─────────────────────
    def test_skip_freeze_does_not_auto_freeze(self):
        self._plain_task_at_tests()
        self._fill_build_expectations()
        self._quiet(["advance", "t", "--skip-freeze"])
        self.assertIn("Status: DRAFT", self._task_path().read_text(),
                      "the escape crosses but leaves §3 DRAFT — it never freezes on the human's behalf")

    # ── a skipped freeze is auditable ────────────────────────────────────────────────────
    def test_skip_freeze_audited(self):
        self._plain_task_at_tests()
        self._fill_build_expectations()
        self._quiet(["advance", "t", "--skip-freeze"])
        out = self._capture(["audit"])
        self.assertIn("freeze_skipped", out)
        self.assertIn("t", out)

    # ── grandfather: a task already AT build is never retro-redded ───────────────────────
    def test_grandfather_past_build_not_retro_redded(self):
        # simulate a pre-existing task that crossed into build before this feature existed:
        # DRAFT §3, phase already == build. Advancing build->verify must NOT hit the gate.
        self._plain_task_at_tests()
        self._fill_build_expectations()
        st = self._state()
        st["tasks"]["t"]["phase"] = "build"     # pre-existing record, DRAFT §3
        self._write_state(st)
        # also mirror the marker the tests->build snapshot would have left, so the build-exit
        # checks that read it do not fault; then advance build -> verify.
        self._quiet(["advance", "t"])
        self.assertEqual(self._task().get("phase"), "verify",
                         "a task already past build advances without a freeze check")

    # ── regression: --await-confirm task still blocked (universal subsumes the old condition)
    def test_optedin_still_blocks(self):
        self._optedin_task_at_tests()
        code, err = self._die_stderr(["advance", "t"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)

    # ── regression: --fast task still blocked ────────────────────────────────────────────
    def test_fast_still_blocks(self):
        self._fast_task_at_tests()
        code, err = self._die_stderr(["advance", "f"])
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)


if __name__ == "__main__":
    unittest.main()
