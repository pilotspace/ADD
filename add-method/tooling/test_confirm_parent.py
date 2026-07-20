#!/usr/bin/env python3
"""Red/green tests for the confirm-parent gate (milestone flow-simplification).

OPT-IN (mirrors `--await-lock`): `new-milestone --await-confirm` seeds the milestone
`confirmed:false`; `new-task` HARD-BLOCKS on an unconfirmed parent until the human runs
`add.py milestone-confirm`. A milestone created WITHOUT the flag carries NO `confirmed`
key and is grandfathered-confirmed (never gated) — so the 342 existing engine tests stay
green untouched. Grandfather-by-missing-key mirrors `_setup_locked` exactly.

Run: python3 -m unittest test_confirm_parent -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


class ConfirmParentTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-confirm-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])   # init creates NO milestone

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _milestone(self, slug="mvp"):
        return self._state()["milestones"][slug]

    def _fill_contracts(self, slug="mvp"):
        """v2 contract-fill gate (flow-enforcement): an OPTED-IN milestone needs a filled
        '## Shared / risky contracts' section before milestone-confirm will record it."""
        p = Path(self.tmp) / ".add" / "milestones" / slug / "MILESTONE.md"
        p.write_text(p.read_text().replace(
            "- <contract name> -> owning task <slug>",
            "- real contract -> owning task alpha"), encoding="utf-8")

    @staticmethod
    def _die_stderr(argv):
        """Run add.main(argv) expecting SystemExit; return (code, stderr text)."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                add.main(argv)
            except SystemExit as e:
                return e.code, err.getvalue()
        raise AssertionError(f"expected SystemExit from {argv}")

    # ── opt-in: --await-confirm seeds an unconfirmed milestone ───────────────────────────
    def test_await_confirm_seeds_unconfirmed(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--await-confirm"])
        m = self._milestone()
        self.assertIs(m.get("confirmed"), False,
                      "--await-confirm must seed confirmed:false")
        self.assertIsNone(m.get("confirmed_at"))
        self.assertIsNone(m.get("confirmed_by"))

    def test_plain_new_milestone_writes_no_key(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        self.assertNotIn("confirmed", self._milestone(),
                         "a plain new-milestone (no flag) must write NO confirmed key")

    # ── the gate: an --await-confirm parent blocks new-task ──────────────────────────────
    def test_await_confirm_blocks_new_task(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--await-confirm"])
        code, err = self._die_stderr(["new-task", "t"])
        self.assertEqual(code, 1)
        self.assertIn("milestone_unconfirmed", err)
        # validate-then-write: nothing scaffolded for the blocked task
        self.assertNotIn("t", self._state().get("tasks", {}))
        self.assertFalse((Path(self.tmp) / ".add" / "tasks" / "t" / "PLAN.md").exists())

    def test_milestone_confirm_opens_gate(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--await-confirm"])
        self._fill_contracts()   # v2: opted-in confirm needs filled cross-task contracts
        add.main(["milestone-confirm", "mvp"])
        m = self._milestone()
        self.assertIs(m.get("confirmed"), True)
        self.assertTrue(m.get("confirmed_at"))
        self.assertTrue(m.get("confirmed_by"))
        add.main(["new-task", "t"])   # now allowed
        self.assertIn("t", self._state()["tasks"])

    # ── grandfather: a plain milestone (no key) is never gated ───────────────────────────
    def test_plain_milestone_never_gates(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "t"])   # no block — no key
        self.assertIn("t", self._state()["tasks"])
        self.assertNotIn("confirmed", self._milestone(),
                         "a grandfathered milestone must not gain a confirmed key")

    def test_grandfather_injected_key_absent(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--await-confirm"])
        # simulate a pre-existing milestone: strip the confirmed keys from state
        sp = Path(self.tmp) / ".add" / "state.json"
        st = json.loads(sp.read_text())
        for k in ("confirmed", "confirmed_at", "confirmed_by"):
            st["milestones"]["mvp"].pop(k, None)
        sp.write_text(json.dumps(st), encoding="utf-8")
        add.main(["new-task", "t"])   # no block — grandfathered
        self.assertIn("t", self._state()["tasks"])
        self.assertNotIn("confirmed", self._state()["milestones"]["mvp"],
                         "grandfathered milestone must not gain a confirmed key")

    # ── the unattached path is unchanged (warn-never-block) ──────────────────────────────
    def test_unattached_task_warn_never_block(self):
        add.main(["new-task", "loose"])   # no milestone at all
        self.assertIn("loose", self._state()["tasks"])

    # ── only the human command sets confirmed (no self-confirm) ──────────────────────────
    def test_no_self_confirm(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--await-confirm"])
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(["status"])
        self.assertIs(self._milestone().get("confirmed"), False,
                      "no command other than milestone-confirm may set confirmed:true")

    def test_unknown_milestone_confirm(self):
        code, err = self._die_stderr(["milestone-confirm", "ghost"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_milestone", err)

    def test_reconfirm_idempotent(self):
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp", "--await-confirm"])
        self._fill_contracts()   # v2: opted-in confirm needs filled cross-task contracts
        add.main(["milestone-confirm", "mvp"])
        first = self._milestone().get("confirmed_at")
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(["milestone-confirm", "mvp"])   # re-confirm: a note, not an error
        self.assertIs(self._milestone().get("confirmed"), True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
