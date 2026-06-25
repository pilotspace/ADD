#!/usr/bin/env python3
"""Red/green tests for ground-phase-engine - insert `ground` as phase-0.

The engine ladder gains a per-task `ground` phase BEFORE specify: every new task
starts by grounding in the real codebase (a `## 0 · GROUND` map) before it
specifies. `ground` is AI-owned - no new human gate; the one approval stays at the
contract freeze. Behavior pinned, not words:
  - new-task seeds phase "ground"; the rendered TASK.md carries "## 0 · GROUND";
  - advance ground -> specify (index-derived); PHASES len 9, ground at index 0;
  - PHASE_OWNER["ground"] == "ai"; contract owner stays "seam" (one gate);
  - the decision digest gives a ground task its own seam (never "approve the contract");
  - render_decide does not crash on the new seam;
  - reopen targets are ground..observe (ground IS reopenable); done is refused;
  - the heading scan captures "## 0 ·" (header-parsed; sec 1..7 keep their numbers);
  - the phase-detail drill-down renders ground..observe;
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

    def _mk_done(self, slug: str):
        """Drive a fresh task ground -> verify -> done (PASS). SIX advances now
        (ground -> specify -> scenarios -> contract -> tests -> build -> verify)."""
        self._run("new-task", slug, "--title", slug)
        for _ in range(6):
            self._run("advance", slug)
        self._run("gate", "PASS", slug)
        assert self._task(slug)["phase"] == "done", "fixture: task did not reach done"

    # ---- the ladder shape -------------------------------------------------
    def test_phases_has_ground_first_len_9(self):
        self.assertEqual(add.PHASES[0], "ground", "ground must be the first phase")
        self.assertEqual(add.PHASES[-1], "done", "done stays the terminal phase")
        self.assertEqual(len(add.PHASES), 9, "ground brings PHASES to 9")

    def test_every_phase_is_owned_ground_is_ai(self):
        # PHASE_OWNER is fail-closed (unmapped_phase) -> ground MUST be mapped.
        for p in add.PHASES:
            self.assertIn(p, add.PHASE_OWNER, f"phase {p} must have an owner")
        self.assertEqual(add.PHASE_OWNER["ground"], "ai", "ground is AI-owned")
        self.assertEqual(add.PHASE_OWNER["contract"], "seam",
                         "the one human approval stays at the contract freeze")

    # ---- new-task starts at ground ----------------------------------------
    def test_new_task_starts_at_ground(self):
        self._run("new-task", "feat", "--title", "Feat")
        self.assertEqual(self._task("feat")["phase"], "ground",
                         "a new task starts by grounding, not specifying")

    def test_new_task_renders_section_0(self):
        self._run("new-task", "feat", "--title", "Feat")
        md = self._task_md("feat")
        self.assertIn("## 0 ", md, "the rendered TASK.md must carry a section 0")
        self.assertIn("GROUND", md, "section 0 is the GROUND map")

    def test_first_task_of_project_starts_at_ground(self):
        # setUp just locked + made a milestone; this IS the first task.
        out, err, code = self._run("new-task", "first", "--title", "First")
        self.assertEqual(code, 0, f"first task should create; err={err!r}")
        self.assertEqual(self._task("first")["phase"], "ground")

    # ---- advance ground -> specify ----------------------------------------
    def test_advance_ground_to_specify(self):
        self._run("new-task", "feat", "--title", "Feat")
        self._run("advance", "feat")
        self.assertEqual(self._task("feat")["phase"], "specify",
                         "advancing from ground lands at specify")

    # ---- guide at ground --------------------------------------------------
    def test_guide_at_ground_cues_gathering(self):
        self._run("new-task", "feat", "--title", "Feat")
        out, err, code = self._run("guide")
        low = out.lower()
        self.assertIn("ground", low, "guide must name the ground phase")
        self.assertTrue("gather" in low or "codebase" in low,
                        f"guide at ground must cue gathering the codebase; got {out!r}")

    # ---- the decision digest seam -----------------------------------------
    def test_ground_task_has_its_own_seam(self):
        self._run("new-task", "feat", "--title", "Feat")
        st = add.load_state(self._root())
        d = add.decide_data(self._root(), st, "mvp", "feat")
        self.assertEqual(d["seam"], "ground",
                         "a ground task is neither a front nor a gate seam")
        blob = (d["unlocks"] + " " + d["decide"]).lower()
        self.assertNotIn("approve the contract", blob,
                         "a ground task has no contract to approve yet")

    def test_render_decide_handles_ground_seam(self):
        # render_decide's seam_label map must carry "ground" (else KeyError).
        self._run("new-task", "feat", "--title", "Feat")
        _, err, code = self._run("phase", "ground", "feat")
        self.assertEqual(code, 0, f"phase ground must be settable; err={err!r}")
        self.assertEqual(self._task("feat")["phase"], "ground")
        st = add.load_state(self._root())
        txt = add.render_decide(self._root(), st, "mvp", "feat", ascii=True)
        self.assertIn("feat", txt, "render_decide must not crash on the ground seam")

    # ---- reopen includes ground -------------------------------------------
    def test_reopen_to_ground_allowed(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "ground",
                                   "--reason", "codebase moved under the task")
        self.assertEqual(code, 0, f"reopen --to ground must be allowed; err={err!r}")
        self.assertEqual(self._task("t")["phase"], "ground")

    def test_reopen_to_done_refused(self):
        self._mk_done("t")
        out, err, code = self._run("reopen", "t", "--to", "done", "--reason", "x")
        self.assertNotEqual(code, 0, "reopen --to done must be refused")
        self.assertIn("reopen_target_invalid", err)
        self.assertEqual(self._task("t")["phase"], "done")

    # ---- phase-detail renders ground --------------------------------------
    def test_task_phases_render_ground_first(self):
        self._run("new-task", "feat", "--title", "Feat")
        phases = add.task_phases(self._root(), "feat")
        names = [p["phase"] for p in phases]
        self.assertEqual(names[0], "ground", "the drill-down renders ground first")
        self.assertEqual(names[-1], "observe", "the drill-down ends at observe")
        self.assertEqual(len(phases), 8, "ground..observe is 8 sections")

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
