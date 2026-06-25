#!/usr/bin/env python3
"""Red/green tests for the cross-milestone foundation layer (PROJECT.md survivor doc).

Realizes the AIDD diagram's foundation (Domain/DDD · Spec/SDD · Users/UDD) that
"provides context" across every milestone. Run: python3 -m unittest test_foundation -v
"""
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add


class FoundationTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-found-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _project_md(self) -> Path:
        return Path(self.tmp) / ".add" / "PROJECT.md"

    def _run_capture(self, *argv) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def test_init_scaffolds_project_md(self):
        pj = self._project_md()
        self.assertTrue(pj.exists(), "init must scaffold .add/PROJECT.md")
        text = pj.read_text(encoding="utf-8")
        for marker in ("Domain (DDD)", "Spec / Living Document (SDD)",
                       "Users (UDD)", "Key Decisions"):
            self.assertIn(marker, text, f"PROJECT.md must contain '{marker}'")

    def test_project_md_is_survivor_no_clobber(self):
        pj = self._project_md()
        pj.write_text("SENTINEL — hand edited foundation\n", encoding="utf-8")
        add.main(["init", "--force"])          # resets state, must NOT touch survivors
        self.assertIn("SENTINEL", pj.read_text(encoding="utf-8"),
                      "init --force must not clobber a hand-edited PROJECT.md (survivor)")

    def test_status_points_to_project(self):
        out = self._run_capture("status")
        self.assertIn("PROJECT.md", out,
                      "status must point a fresh session at the foundation doc")

    def test_init_never_writes_blank_survivor(self):
        # Simulate a stale/missing template that renders to whitespace.
        orig = add._render_template

        def fake(name, **subs):
            if name == "PROJECT.md":
                return "   \n  \n"           # blank render
            return orig(name, **subs)

        add._render_template = fake
        try:
            d = tempfile.mkdtemp(prefix="add-blank-")
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
            self.addCleanup(os.chdir, os.getcwd())
            os.chdir(d)
            add.main(["init", "--name", "blank"])
            pj = Path(d) / ".add" / "PROJECT.md"
            self.assertFalse(
                pj.exists() and pj.read_text(encoding="utf-8").strip() == "",
                "init must never create a 0-content survivor file")
        finally:
            add._render_template = orig
            os.chdir(self.tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
