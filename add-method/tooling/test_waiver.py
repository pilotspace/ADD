#!/usr/bin/env python3
"""Proof that a signed RISK-ACCEPTED waiver completes a task (task: risk-accepted-gate,
milestone v2). Closes the Known gap T2's Matrix 4 surfaced: Matrix 3 says a task is
done when Verify reads "PASS (or a signed RISK-ACCEPTED)", but the engine advanced
only PASS. These tests pin the RISK-ACCEPTED half of that promise.
Run: python3 -m unittest test_waiver -v
"""
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")

WAIVER = ["--owner", "alice", "--ticket", "T-1", "--expires", "2026-12-31"]


class WaiverGateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-waiver-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-task", "t", "--title", "Feature"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _task(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())["tasks"]["t"]

    # --- verify-phase guard, symmetric with PASS -----------------------------
    def test_risk_accepted_refused_before_verify(self):
        with self.assertRaises(SystemExit) as cm:
            add.main(["gate", "RISK-ACCEPTED", "t", *WAIVER])  # phase is "direction" (phase-collapse-3 seed)
        self.assertEqual(cm.exception.code, 1)
        t = self._task()
        self.assertEqual(t["phase"], "direction", "refused gate must NOT advance phase")
        self.assertEqual(t["gate"], "none", "refused gate must NOT record an outcome")

    # --- a waiver must be signed: all three fields ---------------------------
    def test_risk_accepted_requires_waiver(self):
        add.main(["phase", "verify", "t"])
        with self.assertRaises(SystemExit) as cm:
            add.main(["gate", "RISK-ACCEPTED", "t"])           # no waiver flags
        self.assertEqual(cm.exception.code, 1)
        t = self._task()
        self.assertEqual(t["phase"], "verify", "incomplete waiver must NOT complete the task")
        self.assertEqual(t["gate"], "none")
        self.assertNotIn("waiver", t, "no partial waiver may be recorded")

    def test_risk_accepted_partial_waiver_refused(self):
        add.main(["phase", "verify", "t"])
        with self.assertRaises(SystemExit) as cm:
            add.main(["gate", "RISK-ACCEPTED", "t", "--owner", "alice", "--ticket", "T-1"])
        self.assertEqual(cm.exception.code, 1)                 # --expires missing
        self.assertEqual(self._task()["phase"], "verify")

    # --- the happy path: a signed waiver at verify completes the task --------
    def test_risk_accepted_complete_reaches_done(self):
        add.main(["phase", "verify", "t"])
        add.main(["gate", "RISK-ACCEPTED", "t", *WAIVER])
        t = self._task()
        self.assertEqual(t["phase"], "done")
        self.assertEqual(t["gate"], "RISK-ACCEPTED")
        self.assertEqual(t["waiver"],
                         {"owner": "alice", "ticket": "T-1", "expires": "2026-12-31"})


class WaiverCompletesMilestoneTest(unittest.TestCase):
    """The HEADLINE promise: a waived task can complete its milestone. `gate
    RISK-ACCEPTED` reaching `done` is necessary but not sufficient — the
    completeness predicate (_task_done) behind `milestone-done`, `ready`,
    `check`, `archive` and `status` must also count a signed RISK-ACCEPTED as
    done, or the waived task silently blocks its milestone. Matrix 3 says done is
    "PASS (or a signed RISK-ACCEPTED)"; this pins the second half end-to-end."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-waiver-ms-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        add.main(["new-task", "t", "--title", "Feature"])   # auto-linked to mvp
        add.main(["phase", "verify", "t"])
        add.main(["gate", "RISK-ACCEPTED", "t", *WAIVER])    # t is done via a signed waiver
        _meet_exit_criteria("mvp")   # v20 goal-gate: meet criteria before close

    def tearDown(self):
        os.chdir(self._cwd)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def test_milestone_done_accepts_a_waived_task(self):
        add.main(["milestone-done", "mvp"])
        self.assertEqual(self._state()["milestones"]["mvp"]["status"], "done",
                         "a signed RISK-ACCEPTED member must NOT block its milestone")

    def test_check_tolerates_a_recorded_waiver(self):
        # `check` must run clean over a state that actually carries a waiver key
        # (the dogfood completed risk-accepted-gate with PASS, so no real state
        # ever exercised this until now). It must also see the milestone as
        # complete-able, not flag the waived task as unfinished.
        add.main(["milestone-done", "mvp"])
        add.main(["check"])   # raises SystemExit(1) if any check fails


class WaiverExpiryCheckTest(unittest.TestCase):
    """FINDING-B (minimalism-audit): Matrix 4 promises waiver fields are stored
    "for a later `check` to expire" — `cmd_check` must FAIL a RISK-ACCEPTED task
    whose `expires` has passed. A waiver valid when signed but lapsed now is the
    real case: the gate stored it; `check` is the standing monitor that catches it.
    Fail-closed: an unparseable `expires` is also a FAIL (never a silent pass)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-waiver-exp-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _waive(self, slug, expires):
        add.main(["new-task", slug, "--title", slug])
        add.main(["phase", "verify", slug])
        add.main(["gate", "RISK-ACCEPTED", slug,
                  "--owner", "alice", "--ticket", "T-1", "--expires", expires])

    def _run_check(self):
        """Run check; return (exit_code, combined_output). exit_code 0 == clean."""
        import contextlib, io
        buf = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                add.main(["check"])
            except SystemExit as e:
                code = e.code or 0
        return code, buf.getvalue()

    def test_check_flags_expired_waiver(self):
        self._waive("lapsed", "2000-01-01")          # signed once, long expired
        before = (Path(self.tmp) / ".add" / "state.json").read_text()
        code, out = self._run_check()
        self.assertEqual(code, 1, "an expired waiver must fail check")
        self.assertIn("waiver_expired", out, "the failing reason must name the code")
        after = (Path(self.tmp) / ".add" / "state.json").read_text()
        self.assertEqual(before, after, "check must not mutate state")

    def test_check_passes_unexpired_waiver(self):
        self._waive("valid", "2999-12-31")           # far future
        code, out = self._run_check()
        self.assertEqual(code, 0, f"a still-valid waiver must pass check; got:\n{out}")
        self.assertNotIn("waiver_expired", out)

    def test_check_failclosed_on_unparseable_expires(self):
        # The gate stores --expires verbatim; a malformed one must not slip past.
        self._waive("garbled", "not-a-date")
        code, out = self._run_check()
        self.assertEqual(code, 1, "an unparseable expires must fail closed")
        self.assertIn("waiver_expired", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
