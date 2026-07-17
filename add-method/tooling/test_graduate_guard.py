#!/usr/bin/env python3
"""Behavioral proof of the stage-graduation guard + guide (task: graduate-guide, v22).

CONTRACT (frozen @ v1): `add.py stage production` is a GUARDED transition, not a bare flip.
  - refuses with `stage_no_roadmap` (non-zero exit, state byte-unchanged) when 0 milestones
    have stage=="production";
  - succeeds (exit 0) once ≥1 production-stage milestone exists — STATUS-AGNOSTIC: it counts
    existence, never judges done-ness (gather-not-judge at stage altitude);
  - `--force` overrides the floor and announces the bypass;
  - scoped to →production ONLY: prototype/poc/mvp flips are byte-unchanged (unguarded_by_design);
  - existing rejections preserved: bad_stage, no_project;
  - `cmd_init` is NOT guarded — `init --stage production` is the declared_at_init boundary
    (an at-creation declaration, not a transition); this task does not touch cmd_init.
Plus the prose orchestration deliverable: graduate.md documents the ordered flow
cue → graduation-report → interview → new-milestone --stage production (N≥1) → confirm →
stage production, with the "final step / never outside the confirmed path / no auto-flip"
invariant; SKILL.md routes to it on the cue and the Depth-by-stage production line points at it.

These prose checks are EXISTENCE/MARKER checks (the file names the seams) — NOT a proof the
orchestration "works"; the guard behavior below + a temp-project dogfood are that proof. (Matches
the test_competency_deltas marker pattern; honors the "pin structurally, not lexically" delta —
the real invariant is the guard, the markers only assert the guide mentions the seams.)

RED until the guard exists (today cmd_stage is a bare flip → production succeeds at 0 milestones;
the `stage` subparser has no --force) and graduate.md / the SKILL routing are written.
Run from repo root:
  PYTHONPATH=add-method/tooling python3 -m unittest test_graduate_guard -v
"""
import contextlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

# Resolve repo paths from THIS file, not cwd: tooling/ -> add-method/ -> repo root.
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
CANON_SKILL = _ADD_METHOD / "skill" / "add"          # canonical skill tree (source of truth)
GRADUATE_MD = CANON_SKILL / "graduate.md"
SKILL_MD = CANON_SKILL / "SKILL.md"


def _run(argv):
    """Run add.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class StageGuardTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-stage-guard-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        _run(["init", "--name", "demo"])   # defaults to stage prototype
        _run(["stage", "mvp"])             # non-production flip (unguarded) -> mvp baseline

    def tearDown(self):
        os.chdir(self._cwd)

    def _stage(self):
        return json.loads(Path(".add/state.json").read_text(encoding="utf-8"))["stage"]

    def _add_production_milestone(self, slug="hardening"):
        # active, NOT done — the status-agnostic floor must accept a fresh draft
        _run(["new-milestone", slug, "--goal", "SLOs+rollback", "--stage", "production"])

    # --- Must-1 / Reject stage_no_roadmap: refuse without a roadmap ---
    def test_production_refuses_without_roadmap(self):
        before = Path(".add/state.json").read_bytes()
        code, out, err = _run(["stage", "production"])
        self.assertNotEqual(code, 0, "stage production must refuse with no production milestone")
        self.assertIn("stage_no_roadmap", out + err, "the refusal must name the error code")
        self.assertEqual(self._stage(), "mvp", "stage must stay mvp on refusal")
        self.assertEqual(Path(".add/state.json").read_bytes(), before,
                         "state.json must be byte-unchanged on refusal (die precedes save)")

    # --- Must / After: succeed once a roadmap exists ---
    def test_production_succeeds_with_roadmap(self):
        self._add_production_milestone()
        code, out, err = _run(["stage", "production"])
        self.assertEqual(code, 0, f"stage production must succeed with a roadmap (err={err!r})")
        self.assertEqual(self._stage(), "production")

    # --- Must-2 / Reject would_be_judging: the guard counts a tally, not readiness ---
    def test_guard_is_status_agnostic(self):
        self._add_production_milestone()   # fresh, active, not done, no exit criteria met
        code, _, err = _run(["stage", "production"])
        self.assertEqual(code, 0, f"the guard must count existence, not done-ness (err={err!r})")
        self.assertEqual(self._stage(), "production")

    # --- Must-4: --force escape overrides the floor ---
    def test_force_overrides_floor(self):
        code, out, err = _run(["stage", "production", "--force"])
        self.assertEqual(code, 0, f"--force must override the roadmap floor (err={err!r})")
        self.assertEqual(self._stage(), "production")
        self.assertIn("bypass", (out + err).lower(),
                      "--force must announce it bypassed the roadmap check")

    # --- Must-3 / Reject unguarded_by_design: non-production flip stays a bare flip ---
    def test_nonproduction_flip_unguarded(self):
        code, out, err = _run(["stage", "poc"])   # 0 production milestones present
        self.assertEqual(code, 0)
        self.assertEqual(self._stage(), "poc")
        self.assertNotIn("stage_no_roadmap", out + err,
                         "a non-production target must never trigger the roadmap guard")

    # --- Reject bad_stage: existing rejection preserved (argparse `choices=STAGES`
    #     rejects an unknown stage at PARSE time — before cmd_stage runs — so the
    #     observable is argparse's "invalid choice", not cmd_stage's _die text). ---
    def test_bad_stage_still_dies(self):
        code, out, err = _run(["stage", "bogus"])
        self.assertNotEqual(code, 0, "an unknown stage must be rejected")
        self.assertIn("invalid choice", (out + err).lower(),
                      "argparse must reject the unknown stage by choice")
        self.assertEqual(self._stage(), "mvp", "an invalid stage must not change the stage")


class StageGuardNoProjectTest(unittest.TestCase):
    # Reject no_project — separate case: no init in setUp.
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-stage-noproj-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    def test_no_project_dies(self):
        code, out, err = _run(["stage", "production"])
        self.assertNotEqual(code, 0, "stage with no project must die")
        self.assertTrue((out + err).strip(), "a failure must explain itself")
        self.assertFalse(Path(".add").exists(), "nothing must be created on no_project")


def _depth_section(text: str) -> str:
    m = re.search(r"##+\s*Depth by stage.*?(?=\n##\s|\Z)", text, re.S)
    return m.group(0) if m else ""
if __name__ == "__main__":
    unittest.main(verbosity=2)
