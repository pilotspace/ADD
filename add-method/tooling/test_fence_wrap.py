#!/usr/bin/env python3
"""Red/green tests for fence-safe wrap in the phase drill-down (task fence-safe-wrap,
milestone v13).

A line whose lstrip() starts with ``` toggles fence state; delimiter lines and every
line inside an open fence render VERBATIM (indent + raw bytes — no word-wrap, no
whitespace collapse, even past the render width). Prose outside fences keeps today's
soft-wrap byte-for-byte. Unclosed fences fail open (verbatim to §body end). The
drill-down stays PURE. Asserts rendered output lines — never _detail_body internals. Run:
    python3 -m unittest test_fence_wrap -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

IND = "   "
# both deliberately LONGER than the default render width (72) so today's soft-wrap
# would split/collapse them — the red condition
LONG_FENCED = "POST /charges   body: {amount_minor_units, currency, idempotency_key}   201_or_409"
SPACED = "col_amount:      int64        col_currency:   char(3)        col_state:  enum"


def _task_md_text(sec3):
    return "\n".join([
        "# TASK: t", "",
        "## 1 · SPECIFY", "Feature: f", "",
        "## 2 · SCENARIOS", "(none)", "",
        "## 3 · CONTRACT", sec3, "",
        "## 4 · TESTS", "plan", "",
        "## 5 · BUILD", "code", "",
        "## 6 · VERIFY", "  - [x] all tests pass", "",
        "## 7 · OBSERVE", "watch", "",
    ])


class FenceWrapTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fence-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "v13", "--title", "Decide", "--goal", "decide fast"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _hash_state(self) -> str:
        return hashlib.sha256((self._root() / "state.json").read_bytes()).hexdigest()

    def _file_set(self):
        return sorted(str(p) for p in self.tmp.rglob("*") if p.is_file())

    def _run(self, *args):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["report", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _mk_task(self, slug, sec3):
        add.main(["new-task", slug, "--title", slug])
        (self._root() / "tasks" / slug / "TASK.md").write_text(
            _task_md_text(sec3), encoding="utf-8")

    # ---- scenarios ---------------------------------------------------------
    def test_fenced_long_line_never_wraps(self):
        self._mk_task("alpha", "```\n" + LONG_FENCED + "\n```")
        out, _, code = self._run("v13", "alpha")
        self.assertEqual(code, 0)
        self.assertIn(IND + LONG_FENCED, out.splitlines())   # ONE line, bytes intact

    def test_fenced_space_runs_survive(self):
        self._mk_task("alpha", "```\n" + SPACED + "\n```")
        out, _, code = self._run("v13", "alpha")
        self.assertEqual(code, 0)
        self.assertIn(IND + SPACED, out.splitlines())        # internal runs preserved

    def test_prose_still_soft_wraps(self):
        prose = ("this long prose sentence sits outside any fence and therefore keeps "
                 "the soft wrap treatment it has today across multiple rendered lines")
        self._mk_task("alpha", prose + "\n\n```\n" + LONG_FENCED + "\n```")
        out, _, code = self._run("v13", "alpha")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertNotIn(IND + prose, lines)                 # still wrapped (regression)
        self.assertTrue(any(ln.startswith(IND + "this long prose") for ln in lines))
        self.assertIn(IND + LONG_FENCED, lines)              # same body, fence untouched

    def test_delimiters_verbatim(self):
        self._mk_task("alpha", "```gherkin\nGiven g\n```")
        out, _, code = self._run("v13", "alpha")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertIn(IND + "```gherkin", lines)
        self.assertIn(IND + "```", lines)

    def test_unclosed_fence_fails_open(self):
        self._mk_task("alpha", "```\n" + LONG_FENCED)        # opener, never closed
        out, _, code = self._run("v13", "alpha")
        self.assertEqual(code, 0)
        self.assertIn(IND + LONG_FENCED, out.splitlines())   # verbatim to §body end

    def test_blank_inside_fence(self):
        self._mk_task("alpha", "```\nfirst_fenced_line\n\nsecond_fenced_line\n```")
        out, _, code = self._run("v13", "alpha")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        i = lines.index(IND + "first_fenced_line")
        self.assertEqual(lines[i + 1], "")                   # blank survives in place
        self.assertEqual(lines[i + 2], IND + "second_fenced_line")

    def test_drilldown_pure(self):
        self._mk_task("alpha", "```\n" + LONG_FENCED + "\n```")
        before_state, before_files = self._hash_state(), self._file_set()
        for argv in (("v13", "alpha"), ("v13", "alpha", "--json")):
            out, _, code = self._run(*argv)
            self.assertEqual(code, 0, f"exit != 0 for {argv}")
        json.loads(out)                                      # --json twin stays valid JSON
        self.assertEqual(self._hash_state(), before_state)
        self.assertEqual(self._file_set(), before_files)


if __name__ == "__main__":
    unittest.main()
