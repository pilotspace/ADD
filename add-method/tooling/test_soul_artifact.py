#!/usr/bin/env python3
"""Red/green guard for the SOUL.md living voice doc (task soul-artifact,
v13-onboarding-polish 5/6).

SOUL.md ("Trusting") joins the survivor layer: `cmd_init` scaffolds it from
`templates/SOUL.md.tmpl`, `cmd_status` points at it each session, and SKILL.md
"Always start here" tells the agent to read it. The voice prose is HUMAN-OWNED —
these tests assert the SCHEMA + mechanism ONLY, never the specific tone words, so
the human can rewrite the voice without breaking the build.

Run: python3 -m unittest test_soul_artifact -v
"""
from __future__ import annotations

import hashlib
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

ADD_METHOD = Path(__file__).resolve().parent.parent
REPO = ADD_METHOD.parent
CANON_TMPL = ADD_METHOD / "tooling" / "templates" / "SOUL.md.tmpl"
DOG_TMPL = REPO / ".add" / "tooling" / "templates" / "SOUL.md.tmpl"
BUNDLE_TMPL = ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "SOUL.md.tmpl"
CANON_SKILL = ADD_METHOD / "skill" / "add" / "SKILL.md"
SECTIONS = ("Tone", "Communication style", "Trust", "Learns from", "Voice deltas")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class SoulArtifact(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-soul-")
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
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _soul(self) -> Path:
        return Path(self.tmp) / ".add" / "SOUL.md"

    # --- SETUP_FILES membership + scaffold ---
    def test_soul_in_setup_files(self):
        self.assertIn("SOUL.md", add.SETUP_FILES)

    def test_init_scaffolds_soul(self):
        self._run("init", "--name", "demo", "--stage", "mvp")
        soul = self._soul()
        self.assertTrue(soul.exists(), "init did not scaffold .add/SOUL.md")
        body = soul.read_text(encoding="utf-8")
        self.assertTrue(body.strip(), "SOUL.md scaffolded blank")
        self.assertIn("Trusting", body, "the voice is named 'Trusting'")
        for sec in SECTIONS:
            self.assertIn(sec, body, f"SOUL.md missing schema section '{sec}'")

    def test_soul_never_clobbered(self):
        # a customised SOUL.md must survive a re-init (survivor-layer never-clobber)
        self._run("init", "--name", "demo", "--stage", "mvp")
        soul = self._soul()
        soul.write_text("# SOUL — my own voice\nMINE\n", encoding="utf-8")
        self._run("init", "--name", "demo", "--stage", "mvp", "--force")
        self.assertIn("MINE", soul.read_text(encoding="utf-8"),
                      "init --force clobbered a customised SOUL.md")

    def test_soul_marked_human_owned(self):
        body = CANON_TMPL.read_text(encoding="utf-8")
        low = body.lower()
        self.assertIn("human-owned", low, "the voice must be marked human-owned")
        self.assertTrue("overridable" in low or "starter" in low,
                        "the voice must be marked a starter / overridable")
        self.assertIn("soul-self-improve", low,
                      "SOUL.md must point at the self-improve loop as the voice-delta writer")

    # --- read each session: status pointer + skill instruction ---
    def test_status_points_at_soul(self):
        self._run("init", "--name", "demo", "--stage", "mvp")
        out, _, _ = self._run("status")
        soul_lines = [ln for ln in out.splitlines() if "SOUL.md" in ln]
        self.assertTrue(soul_lines, "status prints no SOUL.md pointer")
        self.assertTrue(any("voice" in ln.lower() for ln in soul_lines),
                        "the SOUL.md pointer must name it the 'voice'")
        self.assertIn("PROJECT.md", out, "the PROJECT.md context pointer must still print")

    def test_skill_reads_soul_each_session(self):
        body = CANON_SKILL.read_text(encoding="utf-8")
        i = body.index("Always start here")
        region = body[i: i + 1200]
        self.assertIn("SOUL.md", region,
                      "SKILL.md 'Always start here' must tell the agent to read .add/SOUL.md")

    # --- installer ships it: 3-tree parity ---

    # --- reject: a SETUP_FILES member with no template scaffolds nothing ---
    def test_dangling_member_scaffolds_nothing(self):
        # skip-if-blank guard: if a member's template is absent, cmd_init creates no file
        # rather than a 0-content survivor. Point _templates_dir at an empty dir to prove it.
        empty = Path(self.tmp) / "no-templates"
        empty.mkdir()
        orig = add._templates_dir
        add._templates_dir = lambda: empty  # type: ignore[assignment]
        try:
            self._run("init", "--name", "demo", "--stage", "mvp")
        finally:
            add._templates_dir = orig  # type: ignore[assignment]
        self.assertFalse(self._soul().exists(),
                         "a SETUP_FILES member with no template must scaffold nothing (skip-if-blank)")


if __name__ == "__main__":
    unittest.main()
