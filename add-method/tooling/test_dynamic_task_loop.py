#!/usr/bin/env python3
"""Red/green tests for dynamic-task-loop (v20) - the goal-gated milestone loop.

A milestone self-drives toward its GOAL. Two engine changes + a guide tie the loop:
  - `milestone-done <slug>` REFUSES to close while the milestone has exit criteria
    that are not all met -> "milestone_goal_unmet" (the goal-gate that HOLDS the loop
    open); the existing all-tasks-done precondition is unchanged (tasks before goal).
  - the status rollup's decide-next line, when every task is done but the goal is
    unmet, STOPS saying "archive-milestone" and names the feed-forward inventory.
  - a guide (skill loop.md) + the book loop chapter (09-the-loop.md) document the
    AI-proposes -> human-confirms loop and the goal-gated close.

The exit-criteria checkbox IS the human's goal-met affirmation: the engine reads the
`- [x]`/`- [ ]` tally (_exit_criteria), it never judges whether the goal is met.

Arrange-through-CLI-contracts: the board is built with real `add.main` calls.
ASCII-safe asserts (house rule).
Run: python3 -m unittest test_dynamic_task_loop -v
"""
from __future__ import annotations

import hashlib
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

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

# The loop guide (skill) the running skill loads — the canonical of three copies
# (.claude/skills/add ; add-method/skill/add ; _bundled/skill/add — tree/bundle
# parity guards keep them byte-identical).
SKILL_LOOP = _REPO / ".claude" / "skills" / "add" / "loop.md"

# The book loop chapter the goal-gate statement must reach (3 tracked + 1 gitignored
# runtime copy under .add/docs/). Byte-identity across copies is owned by the parity
# guards; here we assert the CONTENT reached every copy.
BOOK_LOOP_COPIES = [                       # book-stops-shipping (2.0 M6b): canonical + root mirror only
    _REPO / "09-the-loop.md",
    _ADD_METHOD / "docs" / "09-the-loop.md",
]

# add.py copies the shared pin guards (must stay byte-identical and == the engine pin).
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class LoopBoard(unittest.TestCase):
    """A live board arranged through the real CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-loop-")).resolve()
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

    def _milestone(self, slug: str = "mvp") -> dict:
        return self._state()["milestones"][slug]

    def _retro(self) -> Path:
        return self._root() / "milestones" / "mvp" / "RETRO.md"

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
        p = self._root() / "tasks" / slug / "PLAN.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _mk_done(self, slug: str = "t"):
        """Drive a fresh task ground -> verify -> done (PASS)."""
        self._run("new-task", slug, "--title", slug)
        self._freeze(slug)
        for _ in range(6):                      # ground -> ... -> verify
            self._run("advance", slug)
        self._run("gate", "PASS", slug)
        assert self._milestone()["status"] != "done", "fixture: milestone not pre-closed"
        assert add._task_done(self._state()["tasks"][slug]), "fixture: task did not reach done"

    def _set_criteria(self, kind: str):
        """Rewrite mvp's '## Exit criteria' section.
        kind: 'unmet' (one '- [ ]'), 'met' (one '- [x]'), 'none' (no checkbox lines)."""
        f = self._root() / "milestones" / "mvp" / add.MILESTONE_FILE
        text = f.read_text(encoding="utf-8")
        if kind == "met":
            body = "## Exit criteria\n- [x] goal reached        (<- t)\n"
        elif kind == "unmet":
            body = "## Exit criteria\n- [ ] goal reached        (<- t)\n"
        elif kind == "none":
            body = "## Exit criteria\n(no checkbox criteria yet)\n"
        else:                                   # pragma: no cover - test typo guard
            raise ValueError(kind)
        new = re.sub(r"## Exit criteria.*?(?=\n## |\Z)", body.rstrip() + "\n",
                     text, flags=re.S)
        f.write_text(new, encoding="utf-8")
        met, total = add._exit_criteria(self._root(), "mvp")
        expect = {"met": (1, 1), "unmet": (0, 1), "none": (0, 0)}[kind]
        assert (met, total) == expect, f"fixture: criteria {kind} -> {(met, total)} != {expect}"

    def _decide_line(self) -> str:
        """The DECIDE NEXT footer of `report mvp` (lowercased)."""
        out, _, code = self._run("report", "mvp")
        assert code == 0, "report mvp should succeed"
        i = out.find("DECIDE NEXT")
        assert i != -1, "report must carry a DECIDE NEXT footer"
        return out[i:].lower()

    # ---- the goal-gate (the hold) -----------------------------------------
    def test_holds_while_criteria_unmet(self):
        self._mk_done("t")
        self._set_criteria("unmet")
        out, err, code = self._run("milestone-done", "mvp")
        self.assertNotEqual(code, 0, "milestone-done must refuse on unmet criteria")
        self.assertIn("milestone_goal_unmet", err)
        self.assertEqual(self._milestone()["status"], "active", "status must stay active")
        self.assertFalse(self._retro().exists(), "no RETRO.md may be written on refusal")

    def test_checked_criteria_releases_gate(self):
        self._mk_done("t")
        self._set_criteria("met")
        out, err, code = self._run("milestone-done", "mvp")
        self.assertEqual(code, 0, f"checked criteria must release the gate; err={err!r}")
        self.assertEqual(self._milestone()["status"], "done")
        self.assertTrue(self._retro().exists(), "RETRO.md is written on a real close")

    def test_no_criteria_closes_as_before(self):
        self._mk_done("t")
        self._set_criteria("none")                         # total == 0
        out, err, code = self._run("milestone-done", "mvp")
        self.assertEqual(code, 0, f"no-criteria milestone must close as before; err={err!r}")
        self.assertEqual(self._milestone()["status"], "done")

    def test_unfinished_tasks_still_block(self):
        self._run("new-task", "t", "--title", "t")         # left at specify (not done)
        self._set_criteria("met")                          # criteria met, but a task is open
        out, err, code = self._run("milestone-done", "mvp")
        self.assertNotEqual(code, 0)
        self.assertIn("milestone_incomplete", err, "tasks-first precedence is unchanged")
        self.assertEqual(self._milestone()["status"], "active")

    # ---- decide-next points at the inventory while held -------------------
    def test_decide_next_names_inventory(self):
        self._mk_done("t")
        self._set_criteria("unmet")
        line = self._decide_line()
        self.assertNotIn("archive-milestone", line,
                         "held milestone must not be told to archive")
        self.assertTrue("exit criteri" in line or "deltas" in line,
                        f"decide-next must name the inventory; got: {line!r}")

    def test_decide_next_archive_when_met(self):
        self._mk_done("t")
        self._set_criteria("met")
        line = self._decide_line()
        self.assertIn("archive-milestone", line,
                      "a goal-met milestone returns to the archive prompt")

    # ---- the hold is self-explaining --------------------------------------
    def test_goal_unmet_message_names_criteria(self):
        self._mk_done("t")
        self._set_criteria("unmet")
        _, err, _ = self._run("milestone-done", "mvp")
        low = err.lower()
        self.assertIn("exit criteri", low, "the message must name exit criteria")
        self.assertIn("1", err, "the message must show the met/total count")

    # ---- the loop is documented (guide + book) ----------------------------
    def test_loop_guide_documents_cycle(self):
        self.assertTrue(SKILL_LOOP.exists(), f"missing loop guide: {SKILL_LOOP}")
        g = SKILL_LOOP.read_text(encoding="utf-8").lower()
        for token in ("propose", "confirm", "exit criteri", "milestone-done"):
            self.assertIn(token, g, f"loop.md must document '{token}'")
        self.assertTrue("defer" in g or "reactivat" in g,
                        "loop.md must record the milestone-reactivation residual as deferred")

    def test_book_loop_chapter_names_gate(self):
        present = [p for p in BOOK_LOOP_COPIES if p.exists()]
        self.assertGreaterEqual(len(present), 2, "the 2 tracked book copies must exist")
        for p in present:
            t = p.read_text(encoding="utf-8").lower()
            self.assertIn("exit criteri", t, f"{p.name} must name the goal-gate")
            self.assertTrue("goal-gate" in t or "holds until" in t,
                            f"{p.name} must state the milestone holds until criteria met")

    # ---- engine re-anchor -------------------------------------------------


if __name__ == "__main__":
    unittest.main(verbosity=2)
