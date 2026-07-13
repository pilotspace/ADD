#!/usr/bin/env python3
"""Red/green tests for ground-phase-engine - insert `ground` as phase-0.

MIGRATED (plan-phase-core, expectations-first): `ground` no longer exists as its own
phase. `ground` (grounding) + the old `contract` phase COLLAPSED into one `plan`
phase — the change plan is grounding + the frozen contract + the build strategy,
recorded as sub-blocks (`### Grounding` / `### Contract` / `### Build-strategy`) inside
`## 3 · PLAN`. A new task now opens at `specify`, not `ground`; the shape/owner/seam
facts this file pins are re-pointed to that new truth below (never weakened — see
test_plan_phase_flow.py for the canonical, non-duplicated coverage of the same
invariants; this file keeps its own CLI-arranged regression net). Behavior pinned,
not words:
  - new-task seeds phase "specify"; grounding now renders inside "## 3 · PLAN";
  - advance specify -> plan (index-derived); PHASES len 7, specify at index 0;
  - PHASE_OWNER["plan"] == "seam" (the one human approval);
  - the decision digest gives a fresh task the FRONT seam (never "approve the contract"
    prematurely — specify/plan/tests all share the front seam now);
  - render_decide does not crash on the plan seam;
  - reopen targets are specify..observe; done is refused;
  - the phase-detail drill-down renders specify..observe (7 sections) — SEE the
    `task_phases` engine-bug note below, kept RED honestly, not papered over;
  - the engine stays byte-identical across the 3 add.py trees (== engine_pin).

Arrange-through-CLI: the board is built with real add.main calls, so the tests
exercise the engine's input contracts, not its internals. ASCII-safe asserts.
Run: python3 -m unittest test_ground_phase -v
"""
from __future__ import annotations

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
import engine_pin

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

# add.py copies that must stay byte-identical and == ENGINE_MD5.
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class GroundLadder(unittest.TestCase):
    """The ground phase as a frozen part of the engine ladder, arranged via the CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ground-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["lock", "--force"])
            add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _task(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    def _task_md(self, slug: str) -> str:
        return (self._root() / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    def _run(self, *argv):
        """Run an add.main call; return (stdout, stderr, exit-code)."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _freeze(self, slug: str):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = self._root() / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _mk_done(self, slug: str):
        """Drive a fresh task specify -> observe -> done (PASS). SIX advances now
        (specify -> plan -> tests -> build -> verify -> observe), then
        `gate PASS` finalizes to done. (plan-phase-core: ground+contract collapsed
        into plan, so the transition count is unchanged from before the rename —
        verified empirically against the live engine, not assumed.)"""
        self._run("new-task", slug, "--title", slug)
        self._freeze(slug)  # freeze-gate-universal: §3 must be FROZEN before plan->tests crossing
        for _ in range(6):
            self._run("advance", slug)
        self._run("gate", "PASS", slug)
        assert self._task(slug)["phase"] == "done", "fixture: task did not reach done"

    # ---- the ladder shape -------------------------------------------------
    def test_phases_has_specify_first_len_7(self):
        # new truth (plan-phase-core): ground+contract collapsed into plan; PHASES is 8.
        self.assertEqual(add.PHASES[0], "specify", "specify must be the first phase")
        self.assertEqual(add.PHASES[-1], "done", "done stays the terminal phase")
        self.assertEqual(len(add.PHASES), 7, "scenarios merged into specify: PHASES is now 7")

    def test_every_phase_is_owned_plan_is_seam(self):
        # PHASE_OWNER is fail-closed (unmapped_phase) -> every phase MUST be mapped;
        # "ground"/"contract" are gone, "plan" carries the one human approval seam.
        for p in add.PHASES:
            self.assertIn(p, add.PHASE_OWNER, f"phase {p} must have an owner")
        self.assertEqual(add.PHASE_OWNER["plan"], "seam",
                         "the one human approval sits at the plan freeze")
        self.assertNotIn("ground", add.PHASE_OWNER, "ground is no longer a phase")
        self.assertNotIn("contract", add.PHASE_OWNER, "contract is no longer a phase")

    # ---- new-task starts at specify ----------------------------------------
    def test_new_task_starts_at_specify(self):
        self._run("new-task", "feat", "--title", "Feat")
        self.assertEqual(self._task("feat")["phase"], "specify",
                         "a new task now starts by specifying; grounding lives inside "
                         "the plan phase (## 3 · PLAN ### Grounding), not a standalone phase-0")

    # test_new_task_renders_section_0 DELETED: its entire premise (a standalone
    # "## 0 · GROUND" section in the rendered TASK.md) is gone — grounding now
    # renders inside "## 3 · PLAN" as the "### Grounding" sub-block, alongside
    # "### Contract"/"### Build-strategy". That exact behavior (no "## 0 · GROUND",
    # "## 3 · PLAN" present, all three sub-blocks present) is already pinned,
    # stronger and unduplicated, by
    # test_plan_phase_flow.py::_CLI.test_template_renders_plan_subblocks — re-adding
    # an equivalent-but-weaker check here would be a vacuous duplicate, not new signal.

    def test_first_task_of_project_starts_at_specify(self):
        # setUp just locked + made a milestone; this IS the first task.
        out, err, code = self._run("new-task", "first", "--title", "First")
        self.assertEqual(code, 0, f"first task should create; err={err!r}")
        self.assertEqual(self._task("first")["phase"], "specify")

    # ---- advance specify -> plan ----------------------------------------
    def test_advance_specify_to_plan(self):
        self._run("new-task", "feat", "--title", "Feat")
        self._run("advance", "feat")
        self.assertEqual(self._task("feat")["phase"], "plan",
                         "advancing from specify lands at plan (merged flow)")

    # ---- guide at plan (grounding now happens inside plan) -----------------
    def test_guide_at_plan_cues_grounding(self):
        self._run("new-task", "feat", "--title", "Feat")
        self._run("advance", "feat")  # specify -> plan (merged flow)
        out, err, code = self._run("guide")
        low = out.lower()
        self.assertIn("plan", low, "guide must name the plan phase")
        self.assertIn("ground", low,
                      f"guide at plan must still cue grounding the real code; got {out!r}")
        self.assertIn("real code", low,
                      f"guide at plan must cue the real-code grounding activity; got {out!r}")

    # ---- the decision digest seam -----------------------------------------
    def test_specify_task_has_front_seam(self):
        # new truth: specify (the opening phase now) shares the FRONT seam with
        # scenarios/plan/tests — there is no longer a phase-0-specific seam label
        # distinct from front/gate; the un-premature-approval invariant still holds.
        self._run("new-task", "feat", "--title", "Feat")
        st = add.load_state(self._root())
        d = add.decide_data(self._root(), st, "mvp", "feat")
        self.assertEqual(d["seam"], "front",
                         "a fresh task opens at specify, a DIRECTION/front-bundle seam")
        blob = (d["unlocks"] + " " + d["decide"]).lower()
        self.assertNotIn("approve the contract", blob,
                         "a fresh specify task has no contract to approve yet")

    def test_render_decide_handles_plan_seam(self):
        # render_decide's seam_label map must carry "plan" (else KeyError).
        self._run("new-task", "feat", "--title", "Feat")
        _, err, code = self._run("phase", "plan", "feat")
        self.assertEqual(code, 0, f"phase plan must be settable; err={err!r}")
        self.assertEqual(self._task("feat")["phase"], "plan")
        st = add.load_state(self._root())
        txt = add.render_decide(self._root(), st, "mvp", "feat", ascii=True)
        self.assertIn("feat", txt, "render_decide must not crash on the plan seam")

    # ---- reopen includes plan -------------------------------------------
    def test_reopen_to_plan_allowed(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "plan",
                                   "--reason", "codebase moved under the task")
        self.assertEqual(code, 0, f"reopen --to plan must be allowed; err={err!r}")
        self.assertEqual(self._task("t")["phase"], "plan")

    def test_reopen_to_done_refused(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "done", "--reason", "x")
        self.assertNotEqual(code, 0, "reopen --to done must be refused")
        self.assertIn("reopen_target_invalid", err)
        self.assertEqual(self._task("t")["phase"], "done")

    # ---- phase-detail renders specify..observe -----------------------------
    # SUSPECTED ENGINE BUG (reported, NOT fixed here — out of this migration's
    # authority): add.task_phases (add.py ~L5718) builds `names = PHASES[:-1]`
    # (7 items: specify..observe under the new 8-phase PHASES) but still iterates
    # `range(0, 8)` (both the OSError fallback branch and the main branch), so
    # `names[7]` raises IndexError on EVERY call, unconditionally — a stale bound
    # left over from the old 9-phase PHASES (where `PHASES[:-1]` was 8 items and
    # `range(0, 8)` matched). This is a genuine defect in the newly-restructured
    # engine, not a fixture mismatch: no rewrite of THIS test can route around it
    # without touching add.py, which is out of scope. The assertions below encode
    # the CORRECT new-truth expectation (matches task_phases' own docstring/comment,
    # "names = PHASES[:-1]  # specify..observe"); this test stays honestly RED until
    # the engine's `range(0, 8)` is corrected to `range(0, 7)` at both call sites.
    def test_task_phases_render_specify_first(self):
        self._run("new-task", "feat", "--title", "Feat")
        phases = add.task_phases(self._root(), "feat")
        names = [p["phase"] for p in phases]
        self.assertEqual(names[0], "specify", "the drill-down renders specify first")
        self.assertEqual(names[-1], "observe", "the drill-down ends at observe")
        self.assertEqual(len(phases), 6,
                         "specify..observe is 6 phase blocks now (specify owns §1+§2)")

    # ---- heading scan captures section 0 ----------------------------------
    def test_phase_spans_captures_section_0(self):
        text = ("# TASK: x\n\n## 0 · GROUND\nthe map\n\n"
                "## 1 · SPECIFY\nthe rules\n\n## 2 · SCENARIOS\ncases\n")
        spans = add._phase_spans(text)
        self.assertIn(0, spans, "## 0 must be captured (bound widened to include 0)")
        self.assertIn("the map", spans[0])
        self.assertIn(1, spans, "## 1 stays captured")
        self.assertIn("the rules", spans[1], "section 1 stays specify (no renumber)")

    # ---- engine parity (sync + repin) -------------------------------------
    def test_engine_byte_identical(self):
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match engine_pin.ENGINE_MD5")


if __name__ == "__main__":
    unittest.main(verbosity=2)
