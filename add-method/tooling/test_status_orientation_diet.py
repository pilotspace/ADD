#!/usr/bin/env python3
"""Red/green tests for status-orientation-diet (call-residuals, frozen §3 v1):
the WM1 anatomy measured 3-4 status re-reads/rep. The resume info already exists in
the plain `status` view — but at line ~67 of a 69-line dump, so agents re-read to
find it. This leads the plain view with a compact "now     :" glance card (active
slug · phase · next verb · resume file) placed BEFORE the "project :" line, reusing
the existing `_next_footer` composer. Additive: every existing line stays; --brief /
--json / --section and the no-active-task path are byte-unchanged.

Run: python3 -m unittest test_status_orientation_diet -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sod-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-task", "orient", "--fast", "--title", "x")

    def _silent(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass

    def _run(self, *argv):
        out = io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(io.StringIO()):
                add.main(list(argv))
        except SystemExit:
            pass
        return out.getvalue()


class GlanceCardTest(_Harness):
    def test_plain_status_leads_with_now_card(self):
        out = self._run("status")
        self.assertIn("now     :", out, "plain status must emit a 'now' glance card")
        self.assertIn("orient", out, "the card must name the active task")
        self.assertRegex(out, r"now     :.*phase=", "the card must carry phase=")
        self.assertIn(".add/tasks/orient/PLAN.md", out, "the card must name the resume file")

    def test_card_appears_before_project_line(self):
        out = self._run("status")
        self.assertIn("now     :", out)
        self.assertIn("project :", out)
        self.assertLess(out.index("now     :"), out.index("project :"),
                        "the glance card must lead the view — before 'project :'")

    def test_card_carries_the_next_verb(self):
        # reuses _next_footer, whose line starts with "next:"
        out = self._run("status")
        card = next((ln for ln in out.splitlines() if ln.startswith("now     :")), "")
        self.assertIn("next:", card, "the card line must carry the next-verb (from _next_footer)")

    def test_brief_view_unchanged_two_lines(self):
        out = self._run("status", "--brief").strip()
        self.assertNotIn("now     :", out, "--brief must not grow the glance card")
        self.assertEqual(len(out.splitlines()), 2, "--brief stays the 2-line resume essentials")

    def test_no_card_when_no_active_task(self):
        # a fresh project with the task removed from active — the no-active path stays clean.
        # simulate by asserting the card is guarded on an active task: after a project with
        # no tasks, 'now     :' must be absent.
        fresh = Path(tempfile.mkdtemp(prefix="add-sod2-")).resolve()
        self.addCleanup(shutil.rmtree, fresh, ignore_errors=True)
        os.chdir(fresh)
        self._silent("init", "--name", "empty", "--stage", "mvp")
        out = self._run("status")
        self.assertNotIn("now     :", out, "no active task → no glance card")


class ResumeBlockDedupTest(_Harness):
    """resume-card-dedup (advance-fold follow-through): the diet added the top 'now'
    card but left the bottom 'resume :' block RESTATING the same slug·phase·next·
    re-orient. That byte-doubling re-enters cache on every later turn. The bottom
    block must keep ONLY the context ops it uniquely teaches (--section / --brief);
    the next-verb lives once, in the card."""

    def test_next_command_stated_once_not_twice(self):
        out = self._run("status")
        # phase-collapse-3: the direction-phase next verb is `freeze --by <name> --cross`;
        # the card carries it via _next_footer, so the resume block must not restate it.
        n = out.count("add.py freeze --by <name> --cross")
        self.assertEqual(n, 1, f"next-command must appear once (card only), got {n}:\n{out}")

    def test_resume_keeps_unique_context_ops_drops_restated_prose(self):
        out = self._run("status")
        # unique ops survive (the context-tax drivers engine-hint-context-ops added)
        self.assertIn("status --section direction", out, "per-section read op must survive")
        self.assertIn("status --brief", out, "cheap re-orient op must survive")
        # restated prose is gone — the card already carries phase= and the next verb
        self.assertNotIn("is at phase", out, "resume must not restate phase (card has phase=)")

    def test_done_branch_still_present(self):
        # the done-task resume branch carries UNIQUE loop-steering (not in the card) — keep it.
        src = (Path(add.__file__)).read_text()
        self.assertIn("resume  : task '{active}' is done", src,
                      "done-task resume branch must stay (unique loop-steering)")


if __name__ == "__main__":
    unittest.main()
