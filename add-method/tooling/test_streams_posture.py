#!/usr/bin/env python3
"""Red/green tests for the persisted streams posture + combined run-mode surfacing (task persist-run-mode).

CONTRACT (frozen @ v1, persist-run-mode):
  add.py streams [show | set <parallel|sequential>]
     show (default) -> READ-ONLY: prints the resolved posture; mutates nothing
     set <parallel|sequential> -> rewrites the SINGLE `streams:` line in PROJECT.md, idempotently
                                   (replace in place, never append; trailing comment kept)
     set <other>    -> "streams_posture_invalid" (exit != 0; PROJECT.md byte-unchanged)
  _project_streams(root) -> "parallel"|"sequential"  (PURE; anchored read; fail-safe:
     absent -> parallel · unrecognized -> sequential · unreadable -> parallel)
  _streams_decl_line(text, posture) -> str           (PURE; idempotent in-place rewrite/insert)
  cmd_status -> adds one line "run mode: <streams> + <autonomy>"
  Schema: PROJECT.md gains ONE `streams:` line (mirrors autonomy). state.json UNCHANGED.

Render-blind: assertions read printed lines / the public file surface, never a private state key.
Run: python3 -m unittest test_streams_posture -v
"""
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent           # add-method/tooling


class _Board(unittest.TestCase):
    """A live .add board arranged through the real CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-streams-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- CLI helpers ------------------------------------------------------
    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass
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

    # ---- paths ------------------------------------------------------------
    def _root(self):
        return self.tmp / ".add"

    def _project_md(self):
        return self._root() / "PROJECT.md"

    def _state_json(self):
        return self._root() / "state.json"

    # ---- arrangement (direct edits — never via the command under test) -----
    def _streams_lines(self, path):
        return re.findall(r"(?m)^streams:.*$", path.read_text(encoding="utf-8"))

    def _streams_value(self, path):
        """The declared posture token only (before any trailing comment) — so an assertion can never be
        fooled by a comment whose prose may contain 'parallel'/'sequential'."""
        m = re.search(r"(?m)^streams:[ \t]*([^\s<#|]+)", path.read_text(encoding="utf-8"))
        return m.group(1) if m else None

    def _write_streams_line(self, line):
        """Prepend a raw streams: line to PROJECT.md (arrange a posture WITHOUT the command under test)."""
        p = self._project_md()
        p.write_text(f"# project\n{line}\n\n{p.read_text(encoding='utf-8')}", encoding="utf-8")
class StatusRunModeTest(_Board):

    def test_status_shows_combined_run_mode(self):
        self._write_streams_line("streams: parallel")          # project autonomy defaults to auto
        out, err, code = self._run("status")
        self.assertEqual(code, 0, err)
        self.assertIn("run mode: parallel + auto", out,
                      "status surfaces the combined streams + autonomy posture")


# ── the resolver: fail-safe, read-only ───────────────────────────────────────
class ProjectStreamsResolverTest(_Board):

    def test_project_streams_absent_defaults_parallel(self):
        before = self._project_md().read_bytes()
        self.assertEqual(add._project_streams(self._root()), "parallel",
                         "absent streams: line resolves to the documented default")
        self.assertEqual(self._project_md().read_bytes(), before,
                         "resolving the posture must not write (no silent write on read)")

    def test_project_streams_garbled_failsafe_sequential(self):
        self._write_streams_line("streams: turbo")
        self.assertEqual(add._project_streams(self._root()), "sequential",
                         "an unrecognized token fails safe to sequential")

    def test_project_streams_reader_anchor(self):
        # a title/prose substring is NEVER a declaration (mirror the autonomy reader anchor)
        p = self._project_md()
        p.write_text("# my streams: parallel project\nSome prose about streams: parallel here.\n"
                     + p.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(add._project_streams(self._root()), "parallel",
                         "no real declaration line -> default parallel, not the prose substring")
if __name__ == "__main__":
    unittest.main()
