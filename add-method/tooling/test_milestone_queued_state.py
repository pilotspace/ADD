"""Red suite for milestone-queued-state (milestone multi-milestone-intake). Contract §3 FROZEN @ v1.

Adds a `queued` milestone status (enum: active · queued · done). `new-milestone --queued`
creates a milestone non-active (MILESTONE.md still written, active set unchanged); `activate`
promotes a queued milestone (status queued→active + joins the active set). Default path
(no --queued) is byte-identical. One assertion per frozen scenario.

RED until the --queued flag + cmd_activate promotion exist; GREEN after build.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add


class QueuedMilestoneTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-queued-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "Demo", "--stage", "mvp"])
        self.root = Path(self.tmp) / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _state(self):
        return add.load_state(self.root)

    # Scenario: create a queued milestone without focusing it
    def test_queued_create_does_not_focus(self):
        add.main(["new-milestone", "alpha"])              # active focus
        add.main(["new-milestone", "beta", "--queued"])   # queued, must not steal focus
        st = self._state()
        self.assertEqual(st["milestones"]["beta"]["status"], "queued")
        self.assertEqual(st.get("active_milestone"), "alpha", "queued must not change focus")
        self.assertNotIn("beta", st.get("active_milestones") or [])
        self.assertTrue((self.root / "milestones" / "beta" / add.MILESTONE_FILE).exists(),
                        "queued milestone must still write MILESTONE.md")

    # Scenario: default new-milestone is unchanged (byte-identical)
    def test_default_new_milestone_unchanged(self):
        add.main(["new-milestone", "gamma"])
        st = self._state()
        self.assertEqual(st["milestones"]["gamma"]["status"], "active")
        self.assertEqual(st.get("active_milestone"), "gamma", "default new-milestone focuses it")

    # Scenario: promote a queued milestone to active
    def test_activate_promotes_queued(self):
        add.main(["new-milestone", "beta", "--queued"])
        add.main(["activate", "beta"])
        st = self._state()
        self.assertEqual(st["milestones"]["beta"]["status"], "active", "activate must flip queued→active")
        self.assertIn("beta", st.get("active_milestones") or [])

    # Scenario: a queued milestone is neither done nor active
    def test_queued_not_done_not_active(self):
        add.main(["new-milestone", "beta", "--queued"])
        st = self._state()
        from add_engine.milestones import _all_milestones_done
        self.assertFalse(_all_milestones_done(st), "a queued milestone must block all-done/graduation")
        self.assertNotIn("beta", st.get("active_milestones") or [])

    # Scenario: queued on an existing slug is rejected
    def test_queued_existing_slug_rejected(self):
        add.main(["new-milestone", "beta", "--queued"])
        with self.assertRaises(SystemExit):
            add.main(["new-milestone", "beta", "--queued"])  # exists, no --force

    # Scenario: activating a done milestone is still rejected
    def test_activate_done_rejected(self):
        add.main(["new-milestone", "beta"])
        # close it: mark done in state directly via the engine path
        st = self._state()
        st["milestones"]["beta"]["status"] = "done"
        add.save_state(self.root, st)
        with self.assertRaises(SystemExit):
            add.main(["activate", "beta"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
