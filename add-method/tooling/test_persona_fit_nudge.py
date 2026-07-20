#!/usr/bin/env python3
"""Red/green tests for persona-fit-nudge — a second, mutually-exclusive `new-milestone` hint:
once ≥1 REAL project-fit persona already exists under `.add/personas/`, print a `persona-fit:`
line naming the existing persona slug(s) + the add-persona fix path, so the AI is nudged to
confirm domain fit (or draft a new persona) instead of silently assuming an existing one covers
a brand-new milestone's domain. Mutually exclusive with persona-seed-nudge's own
`note: {PERSONA_HINT}` line (that one fires only when ZERO real personas exist).

NO-EXEC: the engine only measures `_personas_unseeded(root)` (existence, not content) — domain-fit
judgment itself stays the AI's job via the add-persona agent. `check`/`status` are untouched in v1.
Run: python3 -m unittest test_persona_fit_nudge -v
"""
from __future__ import annotations

import io
import json
import os
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

FIT_MARKERS = ("add-persona", "docs/18-personas.md")

_CONFORMANT_PERSONA = (
    "---\nname: Frontend Engineer\nvibe: ships accessible, fast UI\n---\n"
    "## Identity\nA frontend specialist.\n\n"
    "## Critical Rules\n- accessibility first\n\n"
    "## Default Requirement\nWCAG AA in every screen.\n\n"
    "## Success Metrics\n- 4.5:1 contrast · 44px targets\n"
)


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="addfitnudgeboard-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return buf.getvalue(), err.getvalue(), code

    def _personas(self) -> Path:
        return self.tmp / ".add" / "personas"


class NewMilestoneFitHintTest(_Board):
    # scenario: new-milestone with real personas prints the fit-check line   # M1
    def test_new_milestone_prints_fit_line_when_real_persona_exists(self):
        self._run("init", "--name", "demo")
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        self.assertIn("persona-fit:", out)
        self.assertIn("frontend", out)
        self.assertTrue(any(m in out for m in FIT_MARKERS),
                         f"fit hint must name add-persona or docs/18-personas.md, got: {out!r}")
        self.assertIn("created milestone 'mvp'", out)

    # scenario: the two persona nudges never co-occur (zero-persona side)   # M2
    def test_new_milestone_note_only_when_personas_absent(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        self.assertIn("note:", out)
        self.assertNotIn("persona-fit:", out)

    # scenario: a queued milestone never gets the fit-check hint   # M4
    def test_queued_milestone_never_prints_fit_hint(self):
        self._run("init", "--name", "demo")
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--queued")
        self.assertEqual(code, 0)
        self.assertNotIn("persona-fit:", out)
        self.assertNotIn("note:", out)

    # scenario: exactly one nudge per new-milestone invocation   # R3
    def test_exactly_one_nudge_per_invocation(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        out_zero, _err, code = self._run("new-milestone", "zero", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        zero_hits = sum(marker in out_zero for marker in ("note:", "persona-fit:"))
        self.assertEqual(zero_hits, 1, out_zero)

        self._personas().mkdir(parents=True, exist_ok=True)
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        out_real, _err, code = self._run("new-milestone", "real", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        real_hits = sum(marker in out_real for marker in ("note:", "persona-fit:"))
        self.assertEqual(real_hits, 1, out_real)


class CheckStatusUntouchedTest(_Board):
    # scenario: check/status stay untouched in this v1   # R2
    def test_check_and_status_byte_identical_with_real_persona(self):
        self._run("init", "--name", "demo")
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        check_out, _err, code = self._run("check")
        self.assertEqual(code, 0)
        self.assertNotIn("persona-fit:", check_out)
        status_out, _err, code = self._run("status")
        self.assertEqual(code, 0)
        self.assertNotIn("persona-fit:", status_out)


class SourceInspectionTest(unittest.TestCase):
    # scenario: the fit-check wording is single-sourced   # M3
    def test_persona_fit_hint_is_single_sourced(self):
        const_text = (TOOLING / "add_engine" / "constants.py").read_text(encoding="utf-8")
        self.assertIn("PERSONA_FIT_HINT_TEMPLATE", const_text)
        add_text = (TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertIn("PERSONA_FIT_HINT_TEMPLATE", add_text,
                      "cmd_new_milestone must reference the single-sourced constant")

    # scenario: the engine never computes domain fit itself   # R1
    def test_no_content_heuristic_in_source(self):
        add_text = (TOOLING / "add.py").read_text(encoding="utf-8")
        start = add_text.index("def cmd_new_milestone(")
        end = add_text.index("\ndef ", start + 1)
        body = add_text[start:end].lower()
        for banned in ("similarity", "keyword_match", "token_match", "token overlap", "word overlap"):
            self.assertNotIn(banned, body,
                              f"no content-fit heuristic allowed in cmd_new_milestone, found {banned!r}")
        self.assertIn("_personas_unseeded(root)", body,
                      "the fit-hint branch must be gated ONLY by the existence predicate")

    # scenario: source parity across the 3 engine trees


if __name__ == "__main__":
    unittest.main(verbosity=2)
