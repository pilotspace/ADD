#!/usr/bin/env python3
"""Red/green tests for gate-record write-back (milestone flow-enforcement, task 3).

`add.py gate <outcome>` stamps the resolved outcome + reviewer + date into the TASK.md §6
`### GATE RECORD`, so the file and state.json never silently diverge (closes Finding C).
ALL tasks (NO opt-in — the write is additive, it never refuses, so it cannot break the
census the way the two refusal seams could). GRANDFATHER is the safety: only a line still
holding a `<…>` placeholder is rewritten; a resolved (hand-filled) line is byte-untouched.

Run: python3 -m unittest test_gate_record_writeback -v
"""
import contextlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from datetime import date
from pathlib import Path

import add


class GateRecordWritebackTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-grw-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])     # build-boundary: a verdict needs a locked setup

    def tearDown(self):
        os.chdir(self._cwd)

    # ── helpers ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(argv)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _task(self, slug="t"):
        return self._state()["tasks"][slug]

    def _task_path(self, slug="t"):
        return Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"

    def _gate_record(self, slug="t"):
        """The §6 `### GATE RECORD` block text (up to the next header / hr / EOF)."""
        t = self._task_path(slug).read_text()
        m = re.search(r"### GATE RECORD.*?(?=\n##\s|\n---|\Z)", t, re.S)
        return m.group(0) if m else ""

    def _record_line(self, prefix, slug="t"):
        for ln in self._gate_record(slug).splitlines():
            if ln.startswith(prefix):
                return ln
        return ""

    def _task_at_verify(self, slug="t"):
        self._quiet(["new-task", slug])              # no active milestone -> milestone-less
        self._quiet(["phase", "verify", slug])       # deliberate jump (test_audit_ci pattern)

    # ── any task: PASS stamps the record (no opt-in) ─────────────────────────────────────
    def test_pass_stamps_record(self):
        self._task_at_verify()
        self._quiet(["gate", "PASS"])
        self.assertEqual(self._record_line("Outcome:"), "Outcome: PASS")
        rev = self._record_line("Reviewed by:")
        self.assertNotIn("<", rev, "Reviewed-by placeholder is resolved")
        self.assertIn(date.today().isoformat(), rev, "Reviewed-by carries today's date")
        self.assertEqual(self._task().get("gate"), "PASS", "state still records the verdict")

    # ── RISK-ACCEPTED also fills the waiver line ─────────────────────────────────────────
    def test_risk_accepted_fills_waiver_line(self):
        self._task_at_verify()
        self._quiet(["gate", "RISK-ACCEPTED", "--owner", "alice",
                     "--ticket", "JIRA-9", "--expires", "2099-01-01"])
        self.assertEqual(self._record_line("Outcome:"), "Outcome: RISK-ACCEPTED")
        waiver = self._record_line("If RISK-ACCEPTED")
        self.assertNotIn("<", waiver, "waiver placeholder is resolved")
        for token in ("alice", "JIRA-9", "2099-01-01"):
            self.assertIn(token, waiver, f"{token} stamped from the state waiver")

    # ── fires regardless of milestone (no await_confirm shield) ──────────────────────────
    def test_fires_regardless_of_milestone(self):
        self._quiet(["new-milestone", "plain", "--goal", "g", "--stage", "mvp"])  # no --await-confirm
        self._task_at_verify("u")
        self._quiet(["gate", "PASS", "u"])
        self.assertEqual(self._record_line("Outcome:", "u"), "Outcome: PASS",
                         "write-back is not gated on await_confirm")

    # ── a hand-resolved record is never overwritten (grandfather) ────────────────────────
    def test_grandfather_resolved_not_overwritten(self):
        self._task_at_verify()
        p = self._task_path()
        p.write_text(p.read_text().replace(
            "Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>", "Outcome: HARD-STOP"), encoding="utf-8")
        self._quiet(["gate", "PASS"])
        self.assertEqual(self._record_line("Outcome:"), "Outcome: HARD-STOP",
                         "a resolved Outcome line is byte-untouched")
        self.assertEqual(self._task().get("gate"), "PASS", "only state.json changed")

    # ── no §6 GATE RECORD block -> silent no-op (no crash, file unchanged) ────────────────
    def test_no_gate_record_block_is_noop(self):
        self._task_at_verify()
        p = self._task_path()
        stripped = re.sub(r"### GATE RECORD.*?(?=\n##\s|\n---|\Z)", "", p.read_text(), flags=re.S)
        p.write_text(stripped, encoding="utf-8")
        # `gate PASS` syncs the `phase:` marker (verify->done) AND, on a full template, harvests the
        # §7 Decisions (ADR) block (adr-at-observe) — both orthogonal to THIS write-back; normalize
        # them out so this still asserts the GATE-RECORD write-back fabricated nothing.
        def norm(s):
            s = re.sub(r"(?m)^phase:.*$", "phase:", s)
            # strip-scaffold-at-done: a completing gate now ALSO removes the live-phase `<!-- -->`
            # instruction comments (and collapses the blank runs they leave) — orthogonal to THIS
            # write-back. Apply the engine's own normalizer to BOTH sides so this still asserts the
            # GATE-RECORD write-back fabricated nothing.
            s = add._strip_live_scaffold(s)
            return re.sub(r"### Decisions \(ADR\).*?(?=\n##\s|\n---|\Z)", "### Decisions (ADR)\n", s, flags=re.S)
        before = norm(p.read_text())
        self._quiet(["gate", "PASS"])            # must not raise
        self.assertEqual(norm(p.read_text()), before, "no GATE RECORD block -> write-back adds nothing")
        self.assertNotIn("### GATE RECORD", p.read_text(), "no GATE RECORD block was fabricated")
        self.assertEqual(self._task().get("gate"), "PASS")

    # ── write-back closes the audit divergence ───────────────────────────────────────────
    def test_writeback_closes_audit_divergence(self):
        self._task_at_verify()
        self._quiet(["gate", "PASS"])
        _checked, findings = add._audit_findings(
            Path(self.tmp) / ".add", self._state())
        # scope to the divergence THIS task closes (the scaffold's unstamped §3 is a separate concern)
        diverge = [f for f in findings if f["task"] == "t"
                   and f["code"] in ("malformed_gate_record", "gate_record_mismatch")]
        self.assertEqual(diverge, [], f"write-back closes the §6↔state divergence; got {diverge}")
        self.assertEqual(self._record_line("Outcome:"), "Outcome: PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
