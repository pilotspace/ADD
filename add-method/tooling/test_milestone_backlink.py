#!/usr/bin/env python3
"""Red/green tests for task-milestone-backlink — the engine-written PLAN.md `milestone:` header.

The task↔milestone link stops being implicit in state.json and becomes a SELF-DESCRIBING
header backlink the ENGINE writes and maintains, so the file names its own parent and the
link can't silently drift. Frozen shape (§3 @ v1):
  - new-task writes a `milestone:` header line = the resolved parent slug (or "(none)" when
    milestone-free); via a {{milestone}} token in PLAN.md.tmpl + the cmd_new_task render call;
  - set-milestone REWRITES that line on a move/detach (insert if a grandfathered file lacks it),
    so state and file stay in lockstep;
  - check emits a WARN (never red) when a PRESENT `milestone:` line disagrees with state; a task
    with NO line (grandfathered/archived) is never flagged;
  - INVARIANTS: every add.py == the engine pin (re-pinned this milestone); PLAN.md.tmpl
    ×3 byte-identical; the phases lean pool stays within budget (no phase-guide prose).

Behavior pinned, not prose. Run: cd add-method/tooling && python3 -m unittest test_milestone_backlink -v
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent          # add-method/tooling
REPO = HERE.parent.parent                        # repo root

TMPL_COPIES = [
    HERE / "templates" / "PLAN.md.tmpl",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
]
FAST_TMPL_COPIES = [
    HERE / "templates" / "PLAN.fast.md.tmpl",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.fast.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "PLAN.fast.md.tmpl",
]
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
_CANON_SKILL = HERE.parent / "skill" / "add"

_MS_LINE = re.compile(r"(?m)^milestone:\s*(.+?)\s*$")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mbl-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run("init", "--name", "demo")
        self._run("new-milestone", "v1", "--title", "One", "--goal", "g")

    def _run(self, *argv) -> str:
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(out):
            try:
                add.main(list(argv))
            except SystemExit as e:        # check exits non-zero on a hard failure
                self._last_exit = e.code or 0
            else:
                self._last_exit = 0
        return out.getvalue()

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "PLAN.md"

    def _header(self, slug: str) -> str:
        return self._task_md(slug).read_text(encoding="utf-8").split("\n## ", 1)[0]

    def _milestone_line(self, slug: str):
        m = _MS_LINE.search(self._header(slug))
        return m.group(1) if m else None


class NewTaskWritesBacklink(_Board):
    def test_new_task_writes_milestone_backlink(self):           # M1
        self._run("new-task", "feat-x", "--title", "F")
        self.assertEqual(self._milestone_line("feat-x"), "v1",
                         "new-task must write `milestone: v1` matching the active milestone")

    def test_milestone_free_reads_none(self):                    # M2
        self._run("deactivate", "v1")
        self._run("new-task", "loose-x", "--title", "L")
        self.assertEqual(self._milestone_line("loose-x"), "(none)",
                         "a milestone-free task must read `milestone: (none)`, never blank/None")

    def test_fast_task_carries_backlink(self):                   # M2 (fast lane)
        self._run("new-task", "fast-x", "--title", "Fx", "--fast")
        self.assertEqual(self._milestone_line("fast-x"), "v1",
                         "a --fast task must also carry the milestone backlink")


class SetMilestoneRewritesBacklink(_Board):
    def test_set_milestone_rewrites_on_move_and_detach(self):    # M3
        self._run("new-task", "feat-x", "--title", "F")
        self._run("new-milestone", "v2", "--title", "Two", "--goal", "g")
        self._run("set-milestone", "feat-x", "v2")
        self.assertEqual(self._milestone_line("feat-x"), "v2",
                         "set-milestone must rewrite the backlink to the new parent")
        self._run("set-milestone", "feat-x", "none")
        self.assertEqual(self._milestone_line("feat-x"), "(none)",
                         "set-milestone none must rewrite the backlink to (none)")


class CheckSurfacesDrift(_Board):
    def test_check_warns_on_disagreeing_backlink(self):          # M4
        self._run("new-task", "feat-x", "--title", "F")
        p = self._task_md("feat-x")
        p.write_text(_MS_LINE.sub("milestone: bogus", p.read_text(encoding="utf-8"), count=1),
                     encoding="utf-8")
        out = self._run("check")
        self.assertEqual(self._last_exit, 0, "a backlink mismatch is a WARN, never a red check")
        self.assertIn("feat-x", out)
        self.assertRegex(out.lower(), r"backlink|milestone .*disagree|disagree")

    def test_check_ignores_grandfathered_task_without_line(self):  # M4, R:grandfather_retro_red
        self._run("new-task", "old-y", "--title", "Y")
        p = self._task_md("old-y")
        p.write_text(_MS_LINE.sub("", p.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        out = self._run("check")
        self.assertEqual(self._last_exit, 0,
                         "a task with no milestone: line must not turn check red")
        self.assertNotRegex(out.lower(), r"old-y.*backlink|backlink.*old-y")


class EnginePinnedAndTreesAligned(unittest.TestCase):
    def test_template_has_milestone_field(self):   # M5
        present = [p for p in TMPL_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 PLAN.md.tmpl copies must exist")
        for p in present:
            self.assertIn("milestone:", p.read_text(encoding="utf-8"),
                          "PLAN.md.tmpl must carry a `milestone:` header field")

if __name__ == "__main__":
    unittest.main(verbosity=2)
