#!/usr/bin/env python3
"""Red/green tests for scope-first-draft (call-residuals, frozen §3 v1):
the WM1 re-measure's post-freeze re-cross repairs come from a too-narrow §5 Scope
that resolves [ok] yet misses a §3 Touches path. The freeze scope-echo already
prints a per-token "note: … outside the declared scope"; this task escalates that
to ONE paste-ready "Scope (may touch): …" line merging the declared tokens with
the uncovered Touches paths, so the agent fixes scope AT freeze (copy-paste),
never at the gate (return-to-build + re-cross). Propose-not-impose: printed, never
written.

Run: python3 -m unittest test_scope_first_draft -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sfd-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-task", "t", "--fast", "--title", "x")
        self.root = self.tmp / ".add"
        self.task_md = self.root / "tasks" / "t" / "TASK.md"

    def _silent(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass

    def _mkfile(self, rel: str):
        # Touches path-heads must EXIST under the project root to be considered.
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n")

    def _write_plan(self, touches: str, scope: str):
        # Replace the §3 Touches + §5 Scope lines with the fixture's.
        text = self.task_md.read_text()
        lines = []
        for ln in text.splitlines():
            if ln.lstrip().startswith("Touches (files"):
                lines.append(f"Touches (files · symbols): {touches}")
            elif ln.lstrip().startswith("Scope (may touch):"):
                lines.append(f"Scope (may touch): {scope}")
            else:
                lines.append(ln)
        self.task_md.write_text("\n".join(lines) + "\n")

    def _echo(self):
        out = io.StringIO()
        with redirect_stdout(out):
            add._scope_echo(self.root, "t")
        return out.getvalue()


class PasteReadyLineTest(_Harness):
    def test_paste_ready_line_when_touches_uncovered(self):
        # §5 declares only pkg/a.py (resolves [ok]); §3 Touches also names pkg/b.py.
        self._mkfile("pkg/a.py")
        self._mkfile("pkg/b.py")
        self._write_plan(
            touches="`pkg/a.py:foo` · `pkg/b.py:bar`",
            scope="`pkg/a.py`",
        )
        out = self._echo()
        self.assertIn("Scope (may touch):", out,
                      "a paste-ready Scope line must be emitted when Touches is uncovered")
        self.assertIn("paste-ready", out, "the escalation must be labelled paste-ready")
        self.assertIn("pkg/a.py", out, "declared token stays in the merged line")
        self.assertIn("pkg/b.py", out,
                      "the uncovered §3 Touches path joins the merged line")

    def test_no_paste_ready_line_when_fully_covered(self):
        # §5 already covers the §3 Touches path — no escalation.
        self._mkfile("pkg/a.py")
        self._write_plan(
            touches="`pkg/a.py:foo`",
            scope="`pkg/a.py`",
        )
        out = self._echo()
        self.assertNotIn("paste-ready", out,
                         "no paste-ready line when the declared scope already covers Touches")

    def test_paste_ready_never_writes_task_md(self):
        self._mkfile("pkg/a.py")
        self._mkfile("pkg/b.py")
        self._write_plan(
            touches="`pkg/a.py:foo` · `pkg/b.py:bar`",
            scope="`pkg/a.py`",
        )
        before = self.task_md.read_bytes()
        self._echo()
        self.assertEqual(before, self.task_md.read_bytes(),
                         "propose-not-impose: the echo must never write TASK.md")


if __name__ == "__main__":
    unittest.main()
