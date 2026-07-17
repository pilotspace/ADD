#!/usr/bin/env python3
"""Red/green tests for ux-stale-followups (next-step-seams 3/3) — retire the two stale v20/v21 UX follow-ups.

CONTRACT (frozen @ v1, template-soften / option A):
  (#2) A fresh `init` with no human goal shows the friendly sentinel GOAL_UNSET on `status`/`guide`,
       never the raw template placeholder. Fix locus: the PROJECT.md.tmpl goal line renders an EMPTY value
       (+ an inline comment prompt), so `_project_goal`'s EXISTING `… .strip() or GOAL_UNSET` surfaces the
       sentinel. `add.py` is UNTOUCHED; the three template mirrors stay byte-identical.
  (#1) `milestone-done`'s success output carries NO "confirm the boxes" prose (next-footer-engine already
       converged that tail to the footer) — a regression guard pins the absence.
  (cleanup) the two stale "Two UX follow-ups for v21" notes are retired from the live .add/PROJECT.md.

Render-blind: every assertion reads printed stdout or file bytes, never a private state key.
Run: python3 -m unittest test_ux_stale_followups -v
"""
import io
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent                       # add-method/tooling
_ADD_METHOD = _TOOLING.parent                                    # add-method
_REPO = _ADD_METHOD.parent                                       # repo root (AIDD-Book)

CANON_TMPL = _ADD_METHOD / "tooling" / "templates" / "PROJECT.md.tmpl"
BUNDLE_TMPL = _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PROJECT.md.tmpl"
DOGFOOD_TMPL = _REPO / ".add" / "tooling" / "templates" / "PROJECT.md.tmpl"
LIVE_PROJECT_MD = _REPO / ".add" / "PROJECT.md"

# The verbose placeholder chunk that today's template renders into the goal VALUE. The fix removes it
# from the goal value (it must not survive in the softened comment either, or the byte test stays red).
PLACEHOLDER = "the one durable outcome"


class _Base(unittest.TestCase):
    """A live board arranged through the real CLI (the test_project_goal idiom)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ux-stale-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")                   # grandfathered-locked
        self.add_dir = self.tmp / ".add"
        self.project_md = self.add_dir / "PROJECT.md"

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- CLI helpers ------------------------------------------------------
    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _status(self, *flags) -> str:
        return self._run("status", *flags)[0]

    def _guide(self, *a) -> str:
        return self._run("guide", *a)[0]

    # ---- goal arrangement (from test_project_goal) ------------------------
    def _set_goal(self, value: str) -> None:
        lines = [l for l in self.project_md.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("goal:")]
        out, inserted = [], False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("slug:"):
                out.append(f"goal: {value}")
                inserted = True
        if not inserted:
            out.insert(0, f"goal: {value}")
        self.project_md.write_text("\n".join(out) + "\n", encoding="utf-8")

    def _strip_goal(self) -> None:
        lines = [l for l in self.project_md.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("goal:")]
        self.project_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- milestone-close arrangement (the gate-owner-marker _arm idiom) ----
    @staticmethod
    def _section(n, name, *body):
        return [f"## {n} · {name}", *body, ""]

    def _write_task(self, slug):
        lines = [
            f"# TASK: {slug}", f"slug: {slug} · created: 2026-06-12 · stage: mvp",
            "phase: ground", "",
            *self._section(0, "GROUND", "Anchors the contract cites: cmd_gate"),
            *self._section(1, "SPECIFY", "Feature: f"),
            *self._section(2, "SCENARIOS", "(none)"),
            *self._section(3, "CONTRACT", "```", "shape: x { a }", "```",
                           "Status: FROZEN @ v1 — approved by Tester 2026-06-12.",
                           "Least-sure flag surfaced at freeze: [contract] none material."),
            *self._section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *self._section(5, "BUILD", "Strategy (ordered batches): 1. build",
                           "Safety rule (feature-specific): none", "Code lives in: `./src/`"),
            *self._section(6, "VERIFY", "checks"),
            *self._section(7, "OBSERVE", "watch"),
        ]
        (self.add_dir / "tasks" / slug / "TASK.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug):
        d = self.add_dir / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text("def test_one():\n    assert 2 + 2 == 4\n", encoding="utf-8")

    def _check_all_criteria(self, ms):
        p = self.add_dir / "milestones" / ms / "MILESTONE.md"
        p.write_text(p.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")

    def _milestone_with_one_done_task(self, ms="v1", slug="alpha"):
        self._silent("new-milestone", ms, "--title", "T", "--goal", "g")
        self._silent("new-task", slug, "--milestone", ms)
        self._write_task(slug)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build
        self._silent("advance", slug)            # build -> verify
        self._silent("gate", "PASS", slug)       # -> done
        self._check_all_criteria(ms)             # satisfy the goal-gate


# ── #2: a fresh init shows the sentinel, never the raw placeholder ───────────
class FreshInitGoalTest(_Base):

    def test_fresh_init_status_shows_sentinel(self):
        self._silent("new-task", "feat-a", "--title", "A")
        out = self._status("--all")   # goal sentinel on the --all goal line (status-lean-default)
        self.assertIn(add.GOAL_UNSET, out)
        self.assertNotIn(PLACEHOLDER, out)

    def test_fresh_init_guide_shows_sentinel(self):
        self._silent("new-task", "feat-a", "--title", "A")
        out = self._guide()
        self.assertIn(add.GOAL_UNSET, out)
        self.assertNotIn(PLACEHOLDER, out)

    def test_human_goal_renders_verbatim(self):       # regression pin (green throughout)
        self._set_goal("ship the thing")
        self._silent("new-task", "feat-a")
        out = self._status("--all")   # goal prose: --all
        self.assertIn("ship the thing", out)
        self.assertNotIn(add.GOAL_UNSET, out)

    def test_stripped_goal_shows_sentinel(self):      # regression pin (existing degrade)
        self._strip_goal()
        self._silent("new-task", "feat-a")
        out, _, code = self._run("status", "--all")   # goal sentinel: --all
        self.assertEqual(code, 0)
        self.assertIn(add.GOAL_UNSET, out)


# ── the template still carries a goal line + the 3 mirrors are byte-identical ─
class TemplateTest(_Base):

    def test_template_carries_goal_line_and_sections(self):   # regression pin
        text = self.project_md.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?im)^goal:")
        self.assertIn("Domain (DDD)", text)
        self.assertIn("UDD", text)

    def test_template_goal_softened(self):
        canon = CANON_TMPL.read_text(encoding="utf-8")
        self.assertNotIn(PLACEHOLDER, canon, "the goal value must be softened (no raw placeholder)")
        self.assertRegex(canon, r"(?im)^goal:")


# ── #1: milestone-done success output carries no stale confirm-the-boxes prose ─
class MilestoneDoneTest(_Base):

    def test_milestone_done_no_confirm_prose(self):           # regression pin
        self._milestone_with_one_done_task("v1", "alpha")
        out, _, code = self._run("milestone-done", "v1")
        self.assertEqual(code, 0, f"milestone-done should close cleanly:\n{out}")
        low = out.lower()
        self.assertNotIn("confirm the box", low)
        self.assertIn("next:", out)                           # the engine-sourced footer


# ── cleanup: the stale follow-up notes are retired from the live foundation ───
class StaleNotesTest(unittest.TestCase):

    def test_stale_notes_retired(self):
        if not LIVE_PROJECT_MD.exists():
            self.skipTest("live .add/PROJECT.md absent (runs only in the dev repo)")
        # whitespace-normalize: the note is line-wrapped ("…for\nv21:"), so a literal
        # search must collapse newlines or it matches nothing (red-for-the-wrong-reason).
        text = " ".join(LIVE_PROJECT_MD.read_text(encoding="utf-8").split())
        self.assertNotIn("Two UX follow-ups for v21", text,
                         "the stale v21 UX-follow-up note must be retired from the foundation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
