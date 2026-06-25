#!/usr/bin/env python3
"""Behavioral proof of loose-task release attribution (task: loose-task-release).

A "loose task" = a milestone-free task that is done (gate PASS / RISK-ACCEPTED) and not
yet named in any RELEASES.md `loose tasks:` row. It is a first-class releasable item,
peer to a closed milestone: `release` sweeps it into a `loose tasks:` row, the status
cue counts it, and once attributed it drops out — all without weakening the security
floor. Mirrors the milestone track (_released_milestones / _releasable).

Run: python3 -m unittest test_loose_task_release -v
"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-loose-")).resolve()
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        buf = io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _loose_done(self, slug="loose1"):
        """A milestone-free task carried to a clean PASS — a loose task."""
        self._silent("new-task", slug, "--title", "Standalone")
        self._silent("phase", "verify", slug)
        self._silent("gate", "PASS", slug)

    def _release_data(self):
        root = add.find_root()
        return add.release_data(root, add.load_state(root))

    def _releases_text(self):
        p = self.tmp / "RELEASES.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""


class LooseAttributionTest(_Harness):
    def test_loose_task_attributed(self):
        # no releasable milestone, just one done milestone-free task
        self._loose_done("loose1")
        self._silent("release", "0.1.0")
        rel = self._releases_text()
        self.assertIn("loose tasks: loose1", rel,
                      "the cut row must attribute the loose task in a `loose tasks:` line")

    def test_attributed_loose_drops_out(self):
        self._loose_done("loose1")
        self._silent("release", "0.1.0")
        # gathered again, the attributed slug is gone from the loose record-set
        slugs = [m["slug"] for m in self._release_data()["loose"]]
        self.assertNotIn("loose1", slugs, "an attributed loose task is no longer releasable")
        # re-running release is now a no-op (nothing left to bundle)
        _, code = self._run("release", "0.2.0")
        self.assertNotEqual(code, 0, "a second cut with nothing left must refuse as a no-op")

    def test_status_loose_cue(self):
        self._loose_done("loose1")
        out, _ = self._run("status")
        self.assertRegex(out, r"releasable: \d+ loose task",
                         "status must print a separate loose-task cue")
        # the milestone cue constant is byte-unchanged
        self.assertIn("milestone(s) closed since last release", add.RELEASABLE_CUE)


class NotLooseTest(_Harness):
    def test_milestone_attached_and_in_build_are_not_loose(self):
        # a done task UNDER a milestone is not loose
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "attached", "--title", "Attached", "--milestone", "m")
        self._silent("phase", "verify", "attached")
        self._silent("gate", "PASS", "attached")
        # a milestone-free task still mid-flight (not done) is not loose
        self._silent("new-task", "wip", "--title", "WIP")
        slugs = [m["slug"] for m in self._release_data()["loose"]]
        self.assertNotIn("attached", slugs, "a milestone-attached done task is not loose")
        self.assertNotIn("wip", slugs, "a not-done milestone-free task is not loose")


class SecurityFloorTest(_Harness):
    def test_security_blocks_loose_only_cut(self):
        self._loose_done("loose1")
        # an open HARD-STOP anywhere is the un-forceable stop
        self._silent("new-task", "danger", "--title", "Danger")
        self._silent("phase", "verify", "danger")
        self._silent("gate", "HARD-STOP", "danger")
        before_rel = self._releases_text()
        cl = self.tmp / "CHANGELOG.md"
        before_cl = cl.read_text(encoding="utf-8") if cl.exists() else None
        _, code = self._run("release", "0.1.0", "--force")
        self.assertNotEqual(code, 0, "an open HARD-STOP blocks the cut even with --force")
        self.assertEqual(self._releases_text(), before_rel, "RELEASES.md must be byte-unchanged")
        after_cl = cl.read_text(encoding="utf-8") if cl.exists() else None
        self.assertEqual(after_cl, before_cl, "CHANGELOG.md must be byte-unchanged")


if __name__ == "__main__":
    unittest.main(verbosity=2)
