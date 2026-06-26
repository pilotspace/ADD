#!/usr/bin/env python3
"""milestone-naming — new-milestone should NUDGE bare-version slugs toward a short
descriptive name (warn, never block) and stamp the MILESTONE.md `created:` with the
FULL `_now()` ISO timestamp (equal to the state record), not a date-only string.

Run: python3 -m unittest test_milestone_naming -v
"""
import contextlib
import io
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

import add


class MilestoneNamingTest(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.tmp = tempfile.mkdtemp(prefix="add-mname-")
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(["init", "--name", "demo"])

    def _new_milestone(self, slug):
        """Run new-milestone, return captured stdout."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            add.main(["new-milestone", slug, "--goal", "g", "--stage", "mvp"])
        return buf.getvalue()

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def test_version_slug_nudges(self):
        out = self._new_milestone("v9")
        self.assertIn("note:", out)
        self.assertIn("bare version", out)
        self.assertTrue((Path(self.tmp) / ".add" / "milestones" / "v9").is_dir(),
                        "the milestone must STILL be created (warn never blocks)")

    def test_descriptive_slug_silent(self):
        out = self._new_milestone("payment-retries")
        self.assertNotIn("bare version", out,
                         "a descriptive slug must not trip the version nudge")
        self.assertTrue((Path(self.tmp) / ".add" / "milestones" / "payment-retries").is_dir())

    def test_created_is_full_iso_and_matches_state(self):
        self._new_milestone("billing")
        mfile = Path(self.tmp) / ".add" / "milestones" / "billing" / "MILESTONE.md"
        created_line = next(l for l in mfile.read_text().splitlines() if "created:" in l)
        rendered = created_line.split("created:", 1)[1].strip()
        # full ISO datetime: has a 'T' separator and a UTC offset, not a bare date
        self.assertRegex(rendered, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                         f"created: must be a full ISO timestamp, got {rendered!r}")
        self.assertEqual(rendered, self._state()["milestones"]["billing"]["created"],
                         "the MILESTONE.md stamp must equal the state record's created instant")

    def test_bad_slug_still_rejected(self):
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                add.main(["new-milestone", "bad slug!", "--goal", "g", "--stage", "mvp"])
        self.assertFalse((Path(self.tmp) / ".add" / "milestones" / "bad slug!").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
