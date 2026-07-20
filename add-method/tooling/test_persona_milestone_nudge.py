#!/usr/bin/env python3
"""Red/green tests for persona-seed-nudge — a non-blocking `note:` at `add.py new-milestone`
(plus companion lines in `add.py check` and `add.py status`) when a project has no REAL
project-fit persona under `.add/personas/` yet (absent dir, empty dir, or only the seeded
`_template.md`).

Closes a gap surfaced from the field: a project can run many milestones without ever seeding
`.add/personas/`, with nothing pointing the AI at the `add-persona` agent / docs/18-personas.md.
The hint is purely additive stdout (docs/18-personas.md: "a project with no personas behaves
exactly as before") — never a gate, never a state.json field. One test per §2 scenario.

v2 amendment (project-wide, not milestone-scoped): the hint's wording no longer says "this
milestone's domain" — it is single-sourced as `add_engine.constants.PERSONA_HINT` and reused
verbatim by all three surfaces (new-milestone/check/status) so wording can't drift.
Run: python3 -m unittest test_persona_milestone_nudge -v
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

NOTE_MARKERS = ("add-persona", "docs/18-personas.md")

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
        self.tmp = Path(tempfile.mkdtemp(prefix="addpnudgeboard-")).resolve()
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

    def _state(self) -> dict:
        return json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))


class NewMilestoneNudgeTest(_Board):
    # scenario: nudge on a personas-less project (M1/M2)
    def test_new_milestone_nudges_when_personas_dir_absent(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)   # strip the seeded _template.md too
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        self.assertIn("note:", out)
        self.assertTrue(any(m in out for m in NOTE_MARKERS),
                         f"note must name the add-persona agent or docs/18-personas.md, got: {out!r}")
        # the milestone was still created and the footer still prints
        self.assertIn("created milestone 'mvp'", out)
        self.assertIn("next:", out)

    # scenario: nudge on a template-only project (M1/M2)
    def test_new_milestone_nudges_when_only_template_present(self):
        self._run("init", "--name", "demo")
        self.assertTrue((self._personas() / "_template.md").exists())
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        self.assertTrue(any(m in out for m in NOTE_MARKERS), out)

    # scenario: the unseeded nudge stays silent once a real persona exists (M3) — superseded by
    # persona-fit-nudge, which adds the MUTUALLY EXCLUSIVE opposite-branch `persona-fit:` hint
    # for this exact case (see test_persona_fit_nudge.py) rather than staying fully silent.
    def test_new_milestone_silent_when_real_persona_exists(self):
        self._run("init", "--name", "demo")
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        self.assertNotIn("no project-fit persona", out)   # the UNSEEDED hint specifically never fires
        self.assertNotIn("note:", out)                    # ...and neither does its `note:` line

    # scenario: unreadable persona file degrades fail-soft (R1)
    def test_new_milestone_unreadable_persona_dir_fails_soft(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        # a FILE where the engine expects a directory: is_dir() is False -> unseeded, and any
        # glob attempt against it would raise NotADirectoryError if mis-coded — this is the
        # fail-soft trap the predicate must not stumble into.
        self._personas().write_text("not a directory", encoding="utf-8")
        out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0, f"must not raise; stderr={_err!r}")
        self.assertTrue(any(m in out for m in NOTE_MARKERS), out)

    # scenario: the nudge never touches gate state (R2)
    def test_persona_hint_does_not_touch_gate_or_state(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        before_keys = set(json.loads((self.tmp / ".add" / "state.json")
                                      .read_text(encoding="utf-8")).keys())
        _out, _err, code = self._run("new-milestone", "mvp", "--goal", "g", "--stage", "mvp")
        self.assertEqual(code, 0)
        after = self._state()
        # every NEW top-level key introduced by this run is a normal new-milestone side
        # effect (milestones/tasks records, active-set pointer, …) — none is persona-shaped.
        new_keys = set(after.keys()) - before_keys
        self.assertFalse(any("persona" in k.lower() for k in new_keys), new_keys)
        # nothing persona-shaped landed in the milestone record either
        self.assertNotIn("persona", json.dumps(after["milestones"]["mvp"]).lower())
        self.assertEqual(after["milestones"]["mvp"]["status"], "active")


class CheckNudgeTest(_Board):
    # scenario: check surfaces the same gap (M4)
    def test_check_reports_personas_unseeded(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        out, _err, code = self._run("check")
        self.assertEqual(code, 0, "check must stay measure-not-block (exit 0)")
        self.assertIn("unseeded", out)
        self.assertIn("personas", out)

    def test_check_silent_when_real_persona_exists(self):
        self._run("init", "--name", "demo")
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        out, _err, code = self._run("check")
        self.assertEqual(code, 0)
        self.assertNotIn("unseeded", out)


class StatusNudgeTest(_Board):
    # scenario: status surfaces the same gap every session (v2 M7)
    def test_status_nudges_when_personas_unseeded(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        out, _err, code = self._run("status")
        self.assertEqual(code, 0)
        self.assertIn("persona ", out)
        self.assertTrue(any(m in out for m in NOTE_MARKERS), out)

    def test_status_silent_when_real_persona_exists(self):
        self._run("init", "--name", "demo")
        (self._personas() / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        out, _err, code = self._run("status")
        self.assertEqual(code, 0)
        for m in NOTE_MARKERS:
            self.assertNotIn(m, out)

    # scenario: the hint never leaks into the machine-readable --json branch (v2 R3)
    def test_status_json_unaffected_when_personas_unseeded(self):
        self._run("init", "--name", "demo")
        shutil.rmtree(self._personas(), ignore_errors=True)
        out, _err, code = self._run("status", "--json")
        self.assertEqual(code, 0)
        parsed = json.loads(out)
        self.assertNotIn("persona", json.dumps(parsed).lower())


class PredicateUnitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-persona-nudge-unit-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _root(self) -> Path:
        (self.tmp / ".add").mkdir(exist_ok=True)
        return self.tmp / ".add"

    def test_absent_dir_is_unseeded(self):
        self.assertTrue(add._personas_unseeded(self._root()))

    def test_template_only_dir_is_unseeded(self):
        root = self._root()
        (root / "personas").mkdir()
        (root / "personas" / "_template.md").write_text("x", encoding="utf-8")
        self.assertTrue(add._personas_unseeded(root))

    def test_real_persona_is_seeded(self):
        root = self._root()
        (root / "personas").mkdir()
        (root / "personas" / "frontend.md").write_text(_CONFORMANT_PERSONA, encoding="utf-8")
        self.assertFalse(add._personas_unseeded(root))

    def test_file_where_dir_expected_is_unseeded_not_raising(self):
        root = self._root()
        (root / "personas").write_text("not a directory", encoding="utf-8")
        self.assertTrue(add._personas_unseeded(root))


class ParityTest(unittest.TestCase):
    # scenario: the change is byte-identical across all engine trees (mirrors
    # test_persona_setup.py:test_persona_template_3tree_parity)

    # scenario: single-sourced wording (v2 M8) — all three call sites reference the ONE
    # PERSONA_HINT constant, never a duplicated literal that could drift out of sync.
    def test_persona_hint_is_single_sourced(self):
        const_text = (TOOLING / "add_engine" / "constants.py").read_text(encoding="utf-8")
        self.assertIn("PERSONA_HINT = (", const_text)
        add_text = (TOOLING / "add.py").read_text(encoding="utf-8")
        uses = add_text.count("PERSONA_HINT")
        # 1 in __all__-derived import (star-import, no explicit name needed) + 3 call sites
        self.assertGreaterEqual(uses, 3, "expected new-milestone/check/status to all reference PERSONA_HINT")
        self.assertNotIn("this milestone's domain", add_text,
                          "v1's milestone-scoped wording must not survive the v2 reword")


if __name__ == "__main__":
    unittest.main(verbosity=2)
