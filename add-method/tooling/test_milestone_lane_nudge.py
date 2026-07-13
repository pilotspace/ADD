#!/usr/bin/env python3
"""Red/green tests for the milestone lane nudge (task milestone-lane-nudge, frozen v1):
WM1 rep r1 lost 9-10 calls to milestone ceremony on single-task work despite the
wrapper prescribing the oneshot lane. Upstream prose doesn't land; a nudge at the
command point does (kickoff-truth precedent) — new-milestone now names the lane.

Run: python3 -m unittest test_milestone_lane_nudge -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mln-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _ok(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        text = out.getvalue() + err.getvalue()
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text


class LaneNudgeTest(_Harness):
    def _create(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        return self._ok("new-milestone", "m", "--title", "M", "--goal", "g")

    def test_nudge_prints(self):                                   # M1
        out = self._create()
        self.assertIn("oneshot lane is cheaper", out)
        self.assertIn("--oneshot", out)

    def test_footer_stays_last(self):                              # M2
        out = self._create()
        last = [ln for ln in out.splitlines() if ln.strip()][-1]
        self.assertTrue(last.startswith("next:"),
                        f"the next-footer must stay the last line, got: {last!r}")


if __name__ == "__main__":
    unittest.main()
