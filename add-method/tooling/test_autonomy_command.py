#!/usr/bin/env python3
"""Red/green tests for the `autonomy` command + the de-command-shape fence (task autonomy-command).

CONTRACT (frozen @ v2, autonomy-command):
  add.py autonomy [show] [slug]          -> READ-ONLY: prints declared · effective · project · verify-gate
  add.py autonomy set <level> [slug] [--project] [--yes]
     - rewrites the SINGLE `autonomy:` declaration line, idempotently (replace, never append; comment kept)
     - --project rewrites PROJECT.md's default instead of a task header
     - LOWER freely; RAISE toward auto needs --yes  -> else "autonomy_raise_unconfirmed"
     - `set auto` on a risk:high task               -> "unguarded_high_risk_auto"  (reused guard)
     - bad/missing level                            -> "autonomy_level_invalid"
     - reused guards VERBATIM: _require_root ("no .add/ project found …") · _resolve_task ("unknown task '<slug>'")
  De-command-shape: add.py:480/:730/:1575 + PLAN.md.tmpl cite `add.py autonomy set`, never bare "set autonomy: X";
     WORDING_RUBRIC.md carries an [enforced] fence; engine_pin.py re-aims @ autonomy-command.

Render-blind: assertions read printed lines / the public file surface, never a private state key.
Run: python3 -m unittest test_autonomy_command -v
"""
import io
import os
import re
import subprocess
import sys
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent           # add-method/tooling


class _Board(unittest.TestCase):
    """A live .add board arranged through the real CLI."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-autonomy-cmd-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")               # plain init -> grandfathered-locked

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

    def _task_md(self, slug):
        return self._root() / "tasks" / slug / "PLAN.md"

    def _project_md(self):
        return self._root() / "PROJECT.md"

    # ---- arrangement (direct edits — never via the command under test) -----
    def _new_task(self, slug="t"):
        self._silent("new-task", slug, "--title", slug)

    def _autonomy_lines(self, path):
        return re.findall(r"(?m)^autonomy:.*$", path.read_text(encoding="utf-8"))

    def _autonomy_value(self, path):
        """The declared LEVEL token only (before any trailing comment) — so an assertion can never be
        fooled by the comment, whose '… manual < conservative < auto …' prose contains every level."""
        m = re.search(r"(?m)^autonomy:[ \t]*([^\s<#|]+)", path.read_text(encoding="utf-8"))
        return m.group(1) if m else None

    def _set_autonomy_line(self, slug, level):
        p = self._task_md(slug)
        txt = p.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^autonomy:.*$", f"autonomy: {level}", txt, count=1)
        if new == txt and not re.search(r"(?m)^autonomy:", txt):
            new = re.sub(r"(?m)^(slug:.*)$", r"\1\nautonomy: " + level, txt, count=1)
        p.write_text(new, encoding="utf-8")

    def _strip_autonomy_line(self, slug):
        p = self._task_md(slug)
        p.write_text(re.sub(r"(?m)^autonomy:.*\n", "", p.read_text(encoding="utf-8")),
                     encoding="utf-8")

    def _set_risk_high(self, slug):
        p = self._task_md(slug)
        txt = p.read_text(encoding="utf-8")
        # append `· risk: high` to the slug line (a DECLARATION position the guard reads)
        p.write_text(re.sub(r"(?m)^(slug:.*?)\s*$", r"\1 · risk: high", txt, count=1),
                     encoding="utf-8")

    def _set_project_autonomy(self, level):
        p = self._project_md()
        txt = re.sub(r"(?m)^autonomy:.*\n", "", p.read_text(encoding="utf-8"))
        p.write_text(f"# project\nautonomy: {level}\n\n{txt}", encoding="utf-8")

    # ---- show parsing (render-blind) --------------------------------------
    @staticmethod
    def _field(out, label):
        for ln in out.splitlines():
            s = ln.strip()
            if s.startswith(label) and ":" in s:
                return s.split(":", 1)[1].strip()
        return None


# ── show: read-only, four fields ────────────────────────────────────────────
class AutonomyShowTest(_Board):

    def test_show_reports_all_four_fields(self):
        self._new_task("t")
        self._set_autonomy_line("t", "conservative")           # project default stays auto
        before = self._task_md("t").read_bytes()
        out, _, code = self._run("autonomy")                   # active task = t
        self.assertEqual(code, 0, out)
        self.assertEqual(self._field(out, "declared"), "conservative", out)
        self.assertEqual(self._field(out, "effective"), "conservative", out)
        self.assertEqual(self._field(out, "project"), "auto", out)
        self.assertIn("human gate", self._field(out, "verify gate") or "", out)
        self.assertEqual(self._task_md("t").read_bytes(), before, "show mutates nothing")

    def test_show_unset_falls_back_to_project(self):
        self._new_task("t")
        self._strip_autonomy_line("t")                         # declared unset; project default auto
        out, _, code = self._run("autonomy", "show", "t")
        self.assertEqual(code, 0, out)
        self.assertIn("unset", (self._field(out, "declared") or "").lower(), out)
        self.assertEqual(self._field(out, "effective"), "auto", out)


# ── set: the idempotent single-line writer ───────────────────────────────────
class AutonomySetTest(_Board):

    def test_set_lowers_single_line(self):
        self._new_task("t")                                    # seeded auto
        out, err, code = self._run("autonomy", "set", "conservative", "t")
        self.assertEqual(code, 0, err)
        lines = self._autonomy_lines(self._task_md("t"))
        self.assertEqual(len(lines), 1, f"exactly one autonomy: line, got {lines}")
        self.assertEqual(self._autonomy_value(self._task_md("t")), "conservative")
        self.assertIn("<!--", lines[0], "trailing rationale comment preserved")

    def test_set_idempotent_no_duplicate(self):
        self._new_task("t")                                    # seeded auto (≠ the value we set)
        self._run("autonomy", "set", "conservative", "t")
        self._run("autonomy", "set", "conservative", "t")      # twice
        lines = self._autonomy_lines(self._task_md("t"))
        self.assertEqual(len(lines), 1, "re-running set never appends a second autonomy: line")
        self.assertEqual(self._autonomy_value(self._task_md("t")), "conservative",
                         "the value actually applied (proves the command ran)")

    def test_set_project_rewrites_default(self):
        out, err, code = self._run("autonomy", "set", "conservative", "--project")
        self.assertEqual(code, 0, err)
        proj = self._autonomy_lines(self._project_md())
        self.assertEqual(len(proj), 1, f"one project autonomy line, got {proj}")
        self.assertEqual(self._autonomy_value(self._project_md()), "conservative")
        self._new_task("t2")                                   # inherits the new default
        self.assertEqual(self._autonomy_value(self._task_md("t2")), "conservative")


# ── the raise guard (human-owned escalation) ─────────────────────────────────
class AutonomyRaiseGuardTest(_Board):

    def test_raise_refused_without_yes(self):
        self._new_task("t")
        self._set_autonomy_line("t", "conservative")
        out, err, code = self._run("autonomy", "set", "auto", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("autonomy_raise_unconfirmed", out + err)
        self.assertEqual(self._autonomy_value(self._task_md("t")), "conservative",
                         "a refused raise leaves the line unchanged")

    def test_raise_succeeds_with_yes(self):
        self._new_task("t")
        self._set_autonomy_line("t", "conservative")
        out, err, code = self._run("autonomy", "set", "auto", "t", "--yes")
        self.assertEqual(code, 0, err)
        self.assertEqual(self._autonomy_value(self._task_md("t")), "auto")

    def test_set_auto_on_risk_high_refused(self):
        self._new_task("t")
        self._set_autonomy_line("t", "conservative")
        self._set_risk_high("t")
        out, err, code = self._run("autonomy", "set", "auto", "t", "--yes")
        self.assertNotEqual(code, 0)
        self.assertIn("unguarded_high_risk_auto", out + err)
        self.assertEqual(self._autonomy_value(self._task_md("t")), "conservative",
                         "the risk:high guard runs BEFORE the write")


# ── the named rejects (own code + reused guards verbatim) ────────────────────
class AutonomyRejectTest(_Board):

    def test_invalid_level_rejected(self):
        self._new_task("t")
        before = self._task_md("t").read_bytes()
        out, err, code = self._run("autonomy", "set", "yolo", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("autonomy_level_invalid", out + err)
        self.assertEqual(self._task_md("t").read_bytes(), before, "a bad level writes nothing")

    def test_unknown_slug_rejected(self):
        self._new_task("t")
        out, err, code = self._run("autonomy", "show", "no-such-task")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown task 'no-such-task'", out + err)   # _resolve_task verbatim (v2)

    def test_no_add_project_rejected(self):
        outside = Path(tempfile.mkdtemp(prefix="add-no-project-")).resolve()
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(outside)
        try:
            out, err, code = self._run("autonomy")
            self.assertNotEqual(code, 0)
            self.assertIn("no .add/ project found", out + err)     # _require_root verbatim (v2)
        finally:
            os.chdir(self.tmp)


# ── the de-command-shape: source surface + the registered verb ───────────────
class DeCommandShapeTest(_Board):

    _OLD_COMMAND_SHAPED = (
        "set autonomy: manual|conservative|auto in PROJECT.md",   # the :480 form
        "set autonomy: manual or conservative",                    # the :730 form
        "set `autonomy: manual|conservative|auto` in the header",  # the :1575 form
    )

    def test_no_command_shaped_string(self):
        src = (HERE / "add.py").read_text(encoding="utf-8")
        for phrase in self._OLD_COMMAND_SHAPED:
            self.assertNotIn(phrase, src, f"command-shaped autonomy string still present: {phrase!r}")
        self.assertGreaterEqual(src.count("add.py autonomy set"), 3,
                                "each reworded site should point at the verb")
        tmpl = (HERE / "templates" / "PLAN.md.tmpl").read_text(encoding="utf-8")
        self.assertIn("add.py autonomy set", tmpl, "the PLAN.md template points at the verb")

    def test_autonomy_subcommand_is_registered(self):
        # the phantom resolves real — `autonomy` is no longer an invalid choice
        self._new_task("t")                                    # show defaults to the active task
        out, err, code = self._run("autonomy", "show")
        self.assertNotIn("invalid choice", out + err)
        self.assertEqual(code, 0, out + err)


# ── the wording-lint fence: the idiom can never regress ──────────────────────
class WordingFenceTest(unittest.TestCase):

    def test_rubric_carries_enforced_entry(self):
        rubric = (HERE / "WORDING_RUBRIC.md").read_text(encoding="utf-8")
        line = next((ln for ln in rubric.splitlines()
                     if "set autonomy" in ln.lower() and "[enforced]" in ln), None)
        self.assertIsNotNone(line, "WORDING_RUBRIC.md must ban the command-shaped 'set autonomy: <level>' idiom")

    def test_wording_lint_passes_clean_surface(self):
        r = subprocess.run([sys.executable, str(HERE / "wording_lint.py")],
                           capture_output=True, text=True, cwd=str(HERE))
        self.assertEqual(r.returncode, 0, f"wording_lint must stay green:\n{r.stdout}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main()
