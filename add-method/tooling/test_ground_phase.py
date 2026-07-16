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
        """Drive a fresh task direction -> verify -> done (PASS). TWO advances now
        (phase-collapse-3: the front collapsed into ONE `direction` phase, so
        direction -> build -> verify is 2 hops), then `gate PASS` finalizes to done."""
        self._run("new-task", slug, "--title", slug)
        self._freeze(slug)  # freeze-gate-universal: §3 must be FROZEN before direction->build crossing
        for _ in range(2):
            self._run("advance", slug)
        self._run("gate", "PASS", slug)
        assert self._task(slug)["phase"] == "done", "fixture: task did not reach done"

    # ---- the ladder shape -------------------------------------------------
    def test_phases_has_direction_first_len_4(self):
        # new truth (phase-collapse-3): specify+plan+tests collapsed into `direction`,
        # observe folded into verify. 3 work phases + done.
        self.assertEqual(add.PHASES[0], "direction", "direction must be the first phase")
        self.assertEqual(add.PHASES[-1], "done", "done stays the terminal phase")
        self.assertEqual(len(add.PHASES), 4, "the collapsed lifecycle: 3 work phases + done")

    def test_every_phase_is_owned_direction_is_seam(self):
        # PHASE_OWNER is fail-closed (unmapped_phase) -> every phase MUST be mapped;
        # "ground"/"contract"/"specify"/"plan"/"scenarios"/"tests"/"observe" are all gone,
        # "direction" carries the one human approval seam.
        for p in add.PHASES:
            self.assertIn(p, add.PHASE_OWNER, f"phase {p} must have an owner")
        self.assertEqual(add.PHASE_OWNER["direction"], "seam",
                         "the one human approval sits at the direction freeze")
        for retired in ("ground", "contract", "specify", "plan", "scenarios", "tests", "observe"):
            self.assertNotIn(retired, add.PHASE_OWNER, f"{retired} is no longer a phase")

    # test_new_task_starts_at_specify DELETED: identical premise (a fresh task is
    # born at the direction span, verified against the marker + state) is already
    # pinned, unduplicated, by
    # test_phase_collapse.py::DirectionIsTheBirthPhase.test_default_lane_starts_at_direction.

    # test_new_task_renders_section_0 DELETED: its entire premise (a standalone
    # "## 0 · GROUND" section in the rendered TASK.md) is gone — grounding now
    # renders inside "## 3 · PLAN" as the "### Grounding" sub-block, alongside
    # "### Contract"/"### Build-strategy". That exact behavior (no "## 0 · GROUND",
    # "## 3 · PLAN" present, all three sub-blocks present) is already pinned,
    # stronger and unduplicated, by
    # test_plan_phase_flow.py::_CLI.test_template_renders_plan_subblocks — re-adding
    # an equivalent-but-weaker check here would be a vacuous duplicate, not new signal.

    # test_first_task_of_project_starts_at_specify DELETED: same premise as
    # test_new_task_starts_at_specify above — a fresh milestone's first task starts
    # at direction, no distinct code path from any other new-task call; duplicate of
    # test_phase_collapse.py::DirectionIsTheBirthPhase.test_default_lane_starts_at_direction.

    # test_advance_specify_to_plan DELETED: its premise (advancing WITHIN the front
    # span, before any freeze) no longer exists — the front collapsed into ONE
    # `direction` phase, so a bare `advance` from a fresh, unfrozen task now attempts
    # the direction->build crossing and is REFUSED (contract_not_drafted), never a
    # same-span hop. That refusal floor is already pinned by
    # test_phase_collapse.py::TheFloorsAreUnchanged.test_freeze_floors_unchanged; the
    # legitimate crossing is pinned by
    # test_phase_collapse.py::OneFreezeCrossesTheFront.test_freeze_cross_universal_from_direction.

    # ---- guide at direction (grounding cue lives inside the merged action) --
    def test_guide_at_direction_cues_grounding(self):
        self._run("new-task", "feat", "--title", "Feat")
        out, err, code = self._run("guide")
        low = out.lower()
        self.assertIn("direction", low, "guide must name the direction phase")
        self.assertIn("ground", low,
                      f"guide at direction must still cue grounding the real code; got {out!r}")
        self.assertIn("real code", low,
                      f"guide at direction must cue the real-code grounding activity; got {out!r}")

    # ---- the decision digest seam -----------------------------------------
    def test_direction_task_has_front_seam(self):
        # new truth: direction (the whole front span now) IS the front-bundle seam —
        # there is no longer a phase-0-specific seam label distinct from front/gate;
        # the un-premature-approval invariant still holds.
        self._run("new-task", "feat", "--title", "Feat")
        st = add.load_state(self._root())
        d = add.decide_data(self._root(), st, "mvp", "feat")
        self.assertEqual(d["seam"], "front",
                         "a fresh task opens at direction, a DIRECTION/front-bundle seam")
        blob = (d["unlocks"] + " " + d["decide"]).lower()
        self.assertNotIn("approve the contract", blob,
                         "a fresh direction task has no contract to approve yet")

    def test_render_decide_handles_direction_seam(self):
        # render_decide's seam_label map must carry the front seam (else KeyError);
        # a legacy "plan" phase token maps to "direction" at the `phase` command.
        self._run("new-task", "feat", "--title", "Feat")
        _, err, code = self._run("phase", "plan", "feat")
        self.assertEqual(code, 0, f"phase plan must be settable; err={err!r}")
        self.assertEqual(self._task("feat")["phase"], "direction",
                         "the legacy 'plan' token maps to 'direction'")
        st = add.load_state(self._root())
        txt = add.render_decide(self._root(), st, "mvp", "feat", ascii=True)
        self.assertIn("feat", txt, "render_decide must not crash on the direction seam")

    # ---- reopen includes direction -----------------------------------------
    def test_reopen_to_direction_allowed(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "plan",
                                   "--reason", "codebase moved under the task")
        self.assertEqual(code, 0, f"reopen --to plan (legacy, maps to direction) must be "
                         f"allowed; err={err!r}")
        self.assertEqual(self._task("t")["phase"], "direction")

    def test_reopen_to_done_refused(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "done", "--reason", "x")
        self.assertNotEqual(code, 0, "reopen --to done must be refused")
        self.assertIn("reopen_target_invalid", err)
        self.assertEqual(self._task("t")["phase"], "done")

    # ---- phase-detail renders direction..verify ----------------------------
    def test_task_phases_render_direction_first(self):
        self._run("new-task", "feat", "--title", "Feat")
        phases = add.task_phases(self._root(), "feat")
        names = [p["phase"] for p in phases]
        self.assertEqual(names[0], "direction", "the drill-down renders direction first")
        self.assertEqual(names[-1], "verify", "the drill-down ends at verify (owns §6+§7)")
        self.assertEqual(len(phases), 3,
                         "direction..verify is 3 phase blocks now (direction owns §1-§4)")

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
