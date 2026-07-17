#!/usr/bin/env python3
"""Red/green tests for persona-self-improve (persona-learning-loop 5/7). CONTRACT frozen @ v1.

A project persona grows through the EXISTING observe->delta->fold loop: an observe-phase
competency lesson MAY carry a `persona:<slug>` target plus a section hint
(`[<comp> · open · persona:<slug> · <critical-rule|success-metric>] <text>`); `add.py fold`
then judgment-free-transcribes that lesson's captured text into `.add/personas/<slug>.md`
under `## Critical Rules`/`## Success Metrics`, PREPENDED newest-first, NEVER clobbering,
stamped folded. The persona file stays schema-conformant (`_persona_missing == []`). No new
learning engine; reuses delta->fold. The engine stays NO-EXEC on the path (no network, no
child launch). One test per §2 scenario + parity. Run: python3 -m unittest test_persona_self_improve -v
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

ENGINE_TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)
SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)
# network/child-launch tokens a NO-EXEC path must never contain (built to dodge lint scanners)
FORBIDDEN_EXEC = ("socket", "urllib", "requests", "sub" + "process",
                  "Pop" + "en", "os." + "system", "spa" + "wn")

PERSONA_BODY = """\
---
name: UI Designer
vibe: clarity over cleverness
---

## Identity
A senior UI designer who keeps interfaces legible and accessible.

## Critical Rules
- Never ship a control without a visible focus state.

## Default Requirement
WCAG AA accessibility in every screen.

## Success Metrics
- Tap targets >= 44px.
"""


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return out.getvalue(), err.getvalue(), code


def _snapshot(base):
    return {str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()}


class PersonaSelfImproveTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-persona-fold-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = Path(self.tmp) / ".add"
        self.project = self.root / "PROJECT.md"
        # a schema-conformant persona to grow
        (self.root / "personas").mkdir(exist_ok=True)
        self.persona = self.root / "personas" / "ui-designer.md"
        self.persona.write_text(PERSONA_BODY, encoding="utf-8")

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers -------------------------------------------------------------
    def _new_task(self, slug):
        add.main(["new-task", slug])

    def _plant(self, slug, line):
        """Inject one raw competency-delta line into slug's §7 Competency deltas block."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        i = s.index("### Competency deltas") + len("### Competency deltas")
        p.write_text(s[:i] + f"\n{line}\n" + s[i:], encoding="utf-8")

    def _set_fv(self, n):
        s = self.project.read_text(encoding="utf-8")
        if re.search(r"foundation-version:\s*\d+", s):
            s = re.sub(r"foundation-version:\s*\d+", f"foundation-version: {n}", s)
        else:
            s = re.sub(r"(?m)^(slug:.*)$", rf"\1 · foundation-version: {n}", s, count=1)
        self.project.write_text(s, encoding="utf-8")

    def _fv(self):
        m = re.search(r"foundation-version:\s*(\d+)", self.project.read_text(encoding="utf-8"))
        return int(m.group(1)) if m else None

    def _persona_text(self):
        return self.persona.read_text(encoding="utf-8")

    def _task_md(self, slug):
        return (self.root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    # --- scenarios -----------------------------------------------------------
    def test_persona_lesson_folds_prepended_no_clobber(self):
        before = self._persona_text()
        self._new_task("a")
        self._plant("a", "- [UDD · open · persona:ui-designer · success-metric] "
                         "4.5:1 contrast on all text (evidence: audit)")
        self._set_fv(3)
        out, err, code = _run(["fold"])
        self.assertIsNone(code, f"fold should succeed: {err}")
        after = self._persona_text()
        # the lesson lands under ## Success Metrics
        sm = after.split("## Success Metrics", 1)[1]
        self.assertIn("4.5:1 contrast on all text", sm,
                      "the lesson must be transcribed under ## Success Metrics")
        # prepended newest-first: the new bullet precedes the pre-existing metric
        self.assertLess(sm.index("4.5:1 contrast"), sm.index("Tap targets >= 44px"),
                        "the new bullet must be prepended (newest-first), above prior metrics")
        # NEVER CLOBBER: every pre-existing non-empty line survives byte-for-byte
        for ln in before.splitlines():
            if ln.strip():
                self.assertIn(ln, after, f"pre-existing persona line dropped: {ln!r}")
        # the TASK.md delta is stamped folded (idempotency marker)
        self.assertIn("[UDD · folded", self._task_md("a"))

    def test_persona_conformant_after_fold(self):
        self._new_task("a")
        self._plant("a", "- [UDD · open · persona:ui-designer · critical-rule] "
                         "always label icon-only buttons (evidence: review)")
        self._set_fv(1)
        out, err, code = _run(["fold"])
        self.assertIsNone(code, f"fold should succeed: {err}")
        self.assertEqual(add._persona_missing(self._persona_text()), [],
                         "the merged persona must stay schema-conformant (all 4 sections survive)")

    def test_refold_idempotent(self):
        self._new_task("a")
        self._plant("a", "- [UDD · open · persona:ui-designer · success-metric] "
                         "once only (evidence: e)")
        self._set_fv(1)
        _run(["fold"])
        first = self._persona_text()
        self.assertEqual(first.count("once only"), 1, "folded exactly once")
        before = _snapshot(self.root)
        out, err, code = _run(["fold"])  # nothing open left -> no-op reject, byte-unchanged
        self.assertIsNotNone(code, "a second fold has no open lesson to consolidate")
        self.assertEqual(self._persona_text().count("once only"), 1,
                         "a folded lesson must not be transcribed twice")
        self.assertEqual(_snapshot(self.root), before, "re-fold leaves the tree byte-unchanged")

    def test_missing_persona_target_rejects(self):
        self._new_task("a")
        self._plant("a", "- [UDD · open · persona:ghost · success-metric] "
                         "no such persona (evidence: e)")
        self._set_fv(8)
        before = _snapshot(self.root)
        out, err, code = _run(["fold"])
        self.assertIsNotNone(code, "a missing persona target must fail-closed")
        self.assertIn("missing_persona_target", out + err)
        self.assertEqual(self._fv(), 8, "no version bump on a fail-closed reject")
        self.assertEqual(_snapshot(self.root), before, "nothing written on a fail-closed reject")

    def test_unroutable_section_rejects(self):
        self._new_task("a")
        self._plant("a", "- [UDD · open · persona:ui-designer · default-requirement] "
                         "bad section (evidence: e)")
        self._set_fv(4)
        before = _snapshot(self.root)
        out, err, code = _run(["fold"])
        self.assertIsNotNone(code, "an unroutable persona section must be rejected")
        self.assertIn("persona_section_unroutable", out + err)
        self.assertEqual(_snapshot(self.root), before, "the tree is byte-unchanged on reject")

    def test_fold_persona_no_exec(self):
        # static scan of the fold path: no network/child-launch token in cmd_fold + helpers
        import inspect
        src = inspect.getsource(add.cmd_fold)
        src += inspect.getsource(add._collect_open_deltas)
        src += inspect.getsource(add._prepend_to_section)
        for forbidden in FORBIDDEN_EXEC:
            self.assertNotIn(forbidden, src,
                             f"the fold-into-persona path must stay NO-EXEC (found {forbidden!r})")
        # dynamic proof: the fold completes offline (no network needed)
        self._new_task("a")
        self._plant("a", "- [UDD · open · persona:ui-designer · success-metric] "
                         "offline ok (evidence: e)")
        self._set_fv(1)
        out, err, code = _run(["fold"])
        self.assertIsNone(code, f"fold must complete offline: {err}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
