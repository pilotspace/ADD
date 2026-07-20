"""loop-aware-orient — the orient surfaces (status, guide) must STEER into the loop.

Today the goal-gate HOLDS the loop open, but at the loop juncture (all member tasks
done while exit criteria are unmet) only `report <ms>` carries the cue — `status` says
"start the next feature" and `guide` routes to 02-the-flow.md. These tests pin the fix:

  - `_done_resume(root, state, slug)` classifies a done task's next move from the
    milestone's exit-criteria tally: LOOP-JUNCTURE / GOAL-MET / PLAIN.
  - status + guide (human AND --json) render it: loop juncture -> name the unmet goal
    and route to 09-the-loop.md; goal met -> milestone-done; no criteria -> byte-identical.
  - loop.md's quoted `status` cue is actually a substring the engine prints (doc-accord).
"""
from __future__ import annotations

import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
SKILL_LOOP = _REPO / ".claude" / "skills" / "add" / "loop.md"


class LoopAwareOrient(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-orient-")).resolve()
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
    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _freeze(self, slug: str):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = self._root() / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _mk_done(self, slug: str = "t"):
        self._run("new-task", slug, "--title", slug)
        self._freeze(slug)
        for _ in range(6):
            self._run("advance", slug)
        self._run("gate", "PASS", slug)

    def _set_criteria(self, kind: str):
        """kind: 'unmet' (0/1) | 'met' (1/1) | 'none' (no checkbox lines)."""
        f = self._root() / "milestones" / "mvp" / add.MILESTONE_FILE
        text = f.read_text(encoding="utf-8")
        body = {
            "met": "## Exit criteria\n- [x] goal reached\n",
            "unmet": "## Exit criteria\n- [ ] goal reached\n",
            "none": "## Exit criteria\n(no checkbox criteria yet)\n",
        }[kind]
        f.write_text(re.sub(r"## Exit criteria.*?(?=\n## |\Z)", body.rstrip() + "\n",
                            text, flags=re.S), encoding="utf-8")

    # ---- the helper (pure) ------------------------------------------------
    def test_done_resume_three_cases(self):
        self._mk_done("t")
        st = self._state()
        self._set_criteria("unmet")
        hl, nxt, chap = add._done_resume(self._root(), st, "t")
        self.assertIn("goal not met", hl.lower())
        self.assertEqual(chap, "09-the-loop.md")
        self._set_criteria("met")
        hl, nxt, chap = add._done_resume(self._root(), st, "t")
        self.assertIn("goal met", hl.lower())
        self.assertIn("milestone-done", nxt)
        self.assertEqual(chap, "09-the-loop.md")
        self._set_criteria("none")
        hl, nxt, chap = add._done_resume(self._root(), st, "t")
        self.assertEqual(chap, "02-the-flow.md")
        self.assertIn("new-task", nxt)

    def test_done_resume_fallback_on_unreadable_milestone(self):
        self._mk_done("t")
        st = self._state()
        # garble the milestone doc -> must fall back to PLAIN, never raise
        (self._root() / "milestones" / "mvp" / add.MILESTONE_FILE).write_text(
            "\x00 not a real doc", encoding="utf-8")
        hl, nxt, chap = add._done_resume(self._root(), st, "t")
        self.assertEqual(chap, "02-the-flow.md")

    # ---- status -----------------------------------------------------------
    def test_status_loop_juncture_names_goal_and_loop(self):
        self._mk_done("t")
        self._set_criteria("unmet")
        out, _, _ = self._run("status")
        low = out.lower()
        self.assertIn("goal not met", low)
        self.assertIn("09-the-loop/", out)
        self.assertNotIn("start the next feature", out)

    def test_status_goal_met_points_to_milestone_done(self):
        self._mk_done("t")
        self._set_criteria("met")
        out, _, _ = self._run("status")
        self.assertIn("milestone-done", out)

    def test_status_no_criteria_keeps_plain_resume(self):
        self._mk_done("t")
        self._set_criteria("none")
        out, _, _ = self._run("status")
        self.assertIn("start the next feature", out)

    # ---- guide ------------------------------------------------------------
    def test_guide_loop_juncture_routes_to_loop_chapter(self):
        self._mk_done("t")
        self._set_criteria("unmet")
        out, _, _ = self._run("guide")
        self.assertIn("09-the-loop/", out)
        self.assertNotIn("02-the-flow", out)

    def test_guide_json_loop_juncture_chapter(self):
        self._mk_done("t")
        self._set_criteria("unmet")
        out, _, _ = self._run("guide", "--json")
        obj = json.loads(out)
        self.assertTrue(obj["chapter"].endswith("/09-the-loop/"), obj["chapter"])

    def test_guide_no_criteria_keeps_flow_chapter(self):
        self._mk_done("t")
        self._set_criteria("none")
        out, _, _ = self._run("guide")
        self.assertIn("02-the-flow/", out)

    # ---- doc accord -------------------------------------------------------
    def test_loop_md_cue_matches_engine(self):
        """loop.md's quoted status cue ('goal not met ... exit criteria') must be a
        substring the engine actually prints at the loop juncture — no misattribution."""
        self._mk_done("t")
        self._set_criteria("unmet")
        out, _, _ = self._run("status")
        self.assertIn("goal not met", out.lower())
        self.assertIn("exit criteria", out.lower())
        guide = SKILL_LOOP.read_text(encoding="utf-8").lower()
        # loop.md still attributes the cue to `status` — and now that is TRUE.
        self.assertIn("goal not met", guide)
        self.assertIn("status", guide)


if __name__ == "__main__":
    unittest.main()
