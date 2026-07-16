#!/usr/bin/env python3
"""Red/green tests for `new-task --fast` + the fast-lane trust floor (task fast-new-task-flag,
milestone fast-lane).

`--fast` opts a task into the fast lane: it scaffolds the minimal TASK.fast.md template, records a
durable `state["tasks"][slug]["fast"] = True` marker, and — the v2 contract — WIRES the task into
the freeze-before-build gate so a fast task is held to the freeze floor under ANY milestone (the gate
firing gains a fast arm: `_optin OR task.fast is True`). Without `--fast`, new-task is byte-identical
to today. `cmd_status` marks an active fast task; `--fast` composes with `--from-delta`.

Run: python3 -m unittest test_fast_new_task_flag -v
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

FULL = {1, 2, 3, 4, 5, 6, 7}
KEPT = {1, 2, 3, 4, 5, 6}   # template-unify: fast = full minus §7 (+§6 deep-check blocks)


class FastNewTaskFlagTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-fnt-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ── helpers ──────────────────────────────────────────────────────────────────────────
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

    def _task(self, slug):
        return self._state()["tasks"][slug]

    def _task_path(self, slug):
        return Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"

    def _sections(self, slug):
        return set(add._phase_spans(self._task_path(slug).read_text()))

    def _plain_milestone(self, ms="mvp"):
        self._quiet(["new-milestone", ms, "--goal", "g", "--stage", "mvp"])   # no --await-confirm

    def _freeze(self, slug):
        """Freeze the fast task's §3 with a well-formed least-sure flag."""
        p = self._task_path(slug)
        t = p.read_text()
        t = t.replace("Status: DRAFT",
                      "Status: FROZEN @ v1 — approved by Tester 2026-06-23.\n"
                      "Least-sure flag surfaced at freeze: [contract] the field rename may "
                      "break a caller — cost: a follow-up migration")
        p.write_text(t, encoding="utf-8")

    # ── scenario 1: --fast scaffolds the minimal template + records the marker ────────────
    def test_fast_scaffolds_minimal_and_marks_state(self):
        self._plain_milestone()
        self._quiet(["new-task", "quick", "--fast"])
        self.assertEqual(self._sections("quick"), KEPT, "fast scaffold keeps only {0,1,3,4,5,6}")
        self.assertIn("fast: true", self._task_path("quick").read_text())
        self.assertIs(self._task("quick").get("fast"), True)

    # ── scenario 2: without --fast, new-task is unchanged (full template, no marker) ──────
    def test_plain_new_task_unchanged(self):
        self._plain_milestone()
        self._quiet(["new-task", "normal"])
        self.assertEqual(self._sections("normal"), FULL, "plain scaffold keeps the full {0..7}")
        self.assertNotIn("fast", self._task("normal"), "no fast key on a normal task")

    # ── scenario 3: the floor holds — a fast task under a PLAIN milestone is freeze-gated ─
    def test_fast_floor_holds_under_plain_milestone(self):
        self._plain_milestone()
        self._quiet(["new-task", "quick", "--fast"])     # DRAFT §3, born at direction
        code, err = self._die_stderr(["advance", "quick"])   # direction -> build: freeze gate fires here
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err,
                      "fast ⇒ freeze-gated even though the milestone did not opt in")
        self.assertEqual(self._task("quick").get("phase"), "direction", "refused advance stays at direction")

    # ── a NON-fast task under a plain milestone is NOW freeze-gated too ───────────────────
    # INVERTED by freeze-gate-universal (flow-honesty): the freeze gate is no longer fast/opt-in
    # only — it fires for EVERY task. So `--fast` no longer DISTINGUISHES freeze-gating (it now
    # only selects the lighter template); a plain DRAFT-§3 task is refused at tests->build too.
    def test_plain_task_now_freeze_gated(self):
        self._plain_milestone()
        self._quiet(["new-task", "normal"])              # DRAFT §3, not fast
        code, err = self._die_stderr(["advance", "normal"])   # universal gate refuses at direction -> build
        self.assertEqual(code, 1)
        self.assertIn("contract_not_frozen", err)
        self.assertEqual(self._task("normal").get("phase"), "direction")

    # ── scenario 4: a fast task completes through the same gates ──────────────────────────
    def test_fast_task_completes_through_gates(self):
        self._plain_milestone()
        self._quiet(["new-task", "quick", "--fast"])
        self._freeze("quick")                            # freeze BEFORE the direction->build crossing
        self._quiet(["advance", "quick"])                # direction -> build (freeze satisfied)
        self.assertEqual(self._task("quick").get("phase"), "build")
        self._quiet(["advance", "quick"])                # build -> verify
        self._quiet(["gate", "PASS"])
        self.assertEqual(self._task("quick").get("gate"), "PASS")
        body = self._task_path("quick").read_text()
        self.assertRegex(body, r"Outcome:\s*PASS", "§6 GATE RECORD Outcome stamped PASS")

    # ── scenario 5: status marks the active fast task ─────────────────────────────────────
    def test_status_marks_active_fast_task(self):
        self._plain_milestone()
        self._quiet(["new-task", "quick", "--fast"])     # becomes the active task
        out = self._capture(["status"])
        active_line = next(ln for ln in out.splitlines() if ln.startswith("active  :"))
        self.assertIn("fast", active_line, "an active fast task is marked on the active line")

    def test_status_no_marker_for_plain_active_task(self):
        self._plain_milestone()
        self._quiet(["new-task", "normal"])
        out = self._capture(["status"])
        active_line = next(ln for ln in out.splitlines() if ln.startswith("active  :"))
        self.assertNotIn("fast", active_line, "a plain active task carries no fast marker")

    # ── scenario 6: --fast composes with --from-delta ────────────────────────────────────
    def test_fast_composes_with_from_delta(self):
        self._plain_milestone()
        self._quiet(["new-task", "prior"])
        p = self._task_path("prior")
        p.write_text(p.read_text().replace(
            "### Spec delta",
            "### Spec delta\n- [SPEC · open] rate-limit the retry path (evidence: prod herd spikes)",
            1), encoding="utf-8")
        self._quiet(["new-task", "next", "--fast", "--from-delta", "prior"])
        self.assertEqual(self._sections("next"), KEPT, "seeded fast task is still the minimal template")
        self.assertIs(self._task("next").get("fast"), True)
        nxt = self._task_path("next").read_text()
        self.assertRegex(nxt, r"Feature:.*rate-limit the retry path", "§1 Feature pre-filled from the delta")


if __name__ == "__main__":
    unittest.main()
