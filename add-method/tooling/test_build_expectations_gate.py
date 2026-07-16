#!/usr/bin/env python3
"""Red/green tests for the build-expectations gate (milestone flow-enforcement, task 2).

Opted-in per milestone: `advance` tests->build refuses `build_expectations_unfilled` when the
task's §6 `### Build expectations` block is a `<…>` placeholder/empty — but ONLY when the task's
PARENT milestone opted into `--await-confirm` (the same switch task-1 uses, one level out). A task
under a plain/no milestone is never gated, so the 33 existing advance-to-build suites stay green.
The shared `_section_unfilled` is extended (break on any header + skip `>` guidance) to read the
sub-section; task-1's `## Shared / risky contracts` truth table is preserved.

Run: python3 -m unittest test_build_expectations_gate -v
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

BE_HEADER = "### Build expectations"
PLACEHOLDER_BE = "- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>"
FILLED_BE = "- [x] the command prints the expected line — confirmed by the green test"


class BuildExpectationsGateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-be-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])     # plain-init grandfathered lock so build-entry is allowed

    def tearDown(self):
        os.chdir(self._cwd)

    # ── helpers ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(argv)

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
        """Stamp §3 FROZEN + a well-formed least-sure flag so an opted-in task clears the
        freeze-before-build gate (fast-lane) and reaches THIS build-expectations gate."""
        p = self._task_path(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-23.\n"
            "Least-sure flag surfaced at freeze: [contract] the §6 outcomes may under-specify "
            "— cost: a follow-up gate"), encoding="utf-8")

    def _fill_build_expectations(self, slug="t"):
        p = self._task_path(slug)
        t = p.read_text()
        t = t.replace(PLACEHOLDER_BE, FILLED_BE)
        # the scaffold ships TWO placeholder bullets — clear the second too (any leftover <…> keeps it unfilled)
        t = t.replace("- [ ] <another observable outcome> — confirmed by <evidence seen>",
                      "- [x] the gate is skipped for plain milestones — confirmed by the green test")
        p.write_text(t, encoding="utf-8")

    # phase-collapse-3: a fresh task is BORN at `direction` — freeze §3 there, straight into
    # the ONE direction->build crossing (which runs the freeze gate THEN this build-expectations
    # gate, in that order — no separate "reach tests" hop left).
    def _optedin_task_at_direction(self, slug="t", ms="mvp"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp", "--await-confirm"])
        self._fill_contracts(ms)
        self._quiet(["milestone-confirm", ms])
        self._quiet(["new-task", slug])
        self._freeze(slug)   # §3 must freeze BEFORE the direction->build crossing

    def _plain_task_at_direction(self, slug="t", ms="plain"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])   # no --await-confirm
        self._quiet(["new-task", slug])
        self._freeze(slug)  # freeze-gate-universal: §3 must be FROZEN before the crossing

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

    # ── opted-in + unfilled §6 -> blocked ────────────────────────────────────────────────
    def test_optedin_unfilled_blocks_build(self):
        self._optedin_task_at_direction()
        code, err = self._die_stderr(["advance", "t"])
        self.assertEqual(code, 1)
        self.assertIn("build_expectations_unfilled", err)
        self.assertEqual(self._task().get("phase"), "direction", "a refused advance leaves phase=direction")
        self.assertFalse((Path(self.tmp) / ".add" / "tasks" / "t" / "scope-snapshot.json").exists(),
                         "validate-then-write: no scope snapshot on a refused advance")

    # ── opted-in + filled §6 -> advances ─────────────────────────────────────────────────
    def test_optedin_filled_advances(self):
        self._optedin_task_at_direction()
        self._fill_build_expectations()
        self._quiet(["advance", "t"])
        self.assertEqual(self._task().get("phase"), "build")

    # ── plain (no-key) milestone -> never gated ──────────────────────────────────────────
    def test_plain_milestone_task_not_gated(self):
        self._plain_task_at_direction()
        self._quiet(["advance", "t"])   # §6 placeholder, but milestone not opted-in
        self.assertEqual(self._task().get("phase"), "build")

    # ── no milestone -> never gated ──────────────────────────────────────────────────────
    def test_no_milestone_task_not_gated(self):
        self._quiet(["new-task", "loose"])   # no active milestone -> milestone-less
        self.assertIsNone(self._task("loose").get("milestone"))
        self._freeze("loose")  # freeze-gate-universal: §3 must be FROZEN before the crossing
        self._quiet(["advance", "loose"])    # direction -> build (the ONE crossing)
        self.assertEqual(self._task("loose").get("phase"), "build")

    # ── the extended predicate over a ### sub-section ─────────────────────────────────────
    def test_section_unfilled_subsection(self):
        ph = f"{BE_HEADER} x\n> guidance line\n- [ ] <outcome> — confirmed by <where>\n\n### Deep checks\n"
        fl = f"{BE_HEADER} x\n> guidance line\n- [x] real outcome — confirmed by the test\n\n### Deep checks\n"
        em = f"{BE_HEADER} x\n> guidance line only\n\n### Deep checks\n"
        self.assertTrue(add._section_unfilled(ph, BE_HEADER), "placeholder -> unfilled")
        self.assertFalse(add._section_unfilled(fl, BE_HEADER), "filled -> filled")
        self.assertTrue(add._section_unfilled(em, BE_HEADER), "only > guidance -> unfilled")

    # ── task-1's contracts truth table is preserved by the extension ─────────────────────
    def test_section_unfilled_contracts_unchanged(self):
        H = "## Shared / risky contracts"
        placeholder = f"{H}\n- <contract name> -> owning task <slug>\n\n## Tasks\n"
        filled = f"{H}\n- a real contract -> owning task alpha\n\n## Tasks\n"
        absent = "## Scope\n- in\n\n## Tasks\n"
        self.assertTrue(add._section_unfilled(placeholder, H))
        self.assertFalse(add._section_unfilled(filled, H))
        self.assertFalse(add._section_unfilled(absent, H))


if __name__ == "__main__":
    unittest.main(verbosity=2)
