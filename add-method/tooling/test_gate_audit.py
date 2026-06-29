#!/usr/bin/env python3
"""Red/green tests for `add.py audit` (task gate-audit, milestone v14).

The audit verifies that human seams left WELL-FORMED records — judgment-free,
read-only, purely additive. Exit 0 clean, exit 1 with findings {task, code,
detail}; six frozen finding codes. Asserts CLI output + exit codes, never parser
internals. Run:
    python3 -m unittest test_gate_audit -v
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"

GOOD3 = "Status: FROZEN @ v1 — approved by Tin, 2026-06-05"
SEC_CLEAN = "  - [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only"
SEC_NOTE = ("  - [x] no exposed secrets, injection openings, or unexpected dependencies — NOTE\n"
            "        (security line): residual metadata touch outside the root")
REC_AUTO = ("### GATE RECORD\nOutcome: PASS (auto-resolved on complete evidence)\n"
            "Reviewed by: auto-gate under autonomy: auto · date: 2026-06-05")
REC_HUMAN = ("### GATE RECORD\nOutcome: PASS — human-confirmed\n"
             "Reviewed by: Tin (human gate) · date: 2026-06-05")

# the marker convention the guide must state (prose accord)
GUIDE_ANCHOR = "start it with `NOTE` or `⚠`"


def _sec6(item=SEC_CLEAN, record=REC_AUTO):
    return f"{item}\n\n{record}"


class GateAuditTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-audit-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _run(self, *args):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["audit", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _mk_done(self, slug, sec3=GOOD3, sec6=None, gate="PASS"):
        """A done task whose §3/§6 we control byte-exactly."""
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])   # becomes the active task
            add.main(["phase", "verify"])
            gate_args = ["gate", gate, slug]
            if gate == "RISK-ACCEPTED":                     # engine enforces the waiver fields
                gate_args += ["--owner", "Tin", "--ticket", "T-1",
                              "--expires", "2026-07-01"]
            add.main(gate_args)
        body = "\n".join([
            f"# TASK: {slug}", "",
            # a well-formed done task declares its risk + sensitivity level — keeps the board clean
            # of the presence-only `risk_unset`/`sensitivity_unset` notices (guarantee-audit-lints,
            # flow-honesty M3 + risk-sensitivity-taxonomy).
            f"slug: {slug} · risk: normal · sensitivity: mechanical", "",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · CONTRACT", "```\nshape\n```", "", sec3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", sec6 if sec6 is not None else _sec6(), "",
            "## 7 · OBSERVE", "watch", "",
        ])
        (self._root() / "tasks" / slug / "TASK.md").write_text(body, encoding="utf-8")

    def _mk_ungated(self, slug, sec6=None, phase="observe"):
        """A task pushed to done/observe via the admin `phase` override — NO engine
        gate, so state.gate stays 'none' — whose §6 we then control byte-exactly.
        This is the F13 shape: a §6 verdict the engine never recorded."""
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])   # active task; gate stays 'none'
            add.main(["phase", phase, slug])                # admin override — no gate recorded
        body = "\n".join([
            f"# TASK: {slug}", "",
            # a well-formed done task declares its risk + sensitivity level — keeps the board clean
            # of the presence-only `risk_unset`/`sensitivity_unset` notices (guarantee-audit-lints,
            # flow-honesty M3 + risk-sensitivity-taxonomy).
            f"slug: {slug} · risk: normal · sensitivity: mechanical", "",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · CONTRACT", "```\nshape\n```", "", GOOD3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", sec6 if sec6 is not None else _sec6(), "",
            "## 7 · OBSERVE", "watch", "",
        ])
        (self._root() / "tasks" / slug / "TASK.md").write_text(body, encoding="utf-8")

    def _codes(self, out):
        return [f["code"] for f in json.loads(out)["findings"]]

    # ---- clean board --------------------------------------------------------
    def test_clean_board_exit_zero(self):
        self._mk_done("alpha")
        out, _, code = self._run()
        self.assertEqual(code, 0, out)
        self.assertIn("audit: clean (1 tasks checked)", out)
        out, _, code = self._run("--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertEqual((d["checked"], d["findings"]), (1, []))

    # ---- F1 unstamped_freeze ------------------------------------------------
    def test_unstamped_freeze(self):
        self._mk_done("alpha", sec3="Status: FROZEN")          # no version, no name
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("unstamped_freeze", self._codes(out))
        text, _, _ = self._run()
        self.assertIn("audit: unstamped_freeze alpha", text)

    def test_missing_name_is_unstamped(self):
        self._mk_done("alpha", sec3="Status: FROZEN @ v1 — approved by")
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("unstamped_freeze", self._codes(out))

    # ---- F2 malformed_gate_record -------------------------------------------
    def test_zero_outcomes_malformed(self):
        self._mk_done("alpha", sec6=SEC_CLEAN + "\n\n### GATE RECORD\nReviewed by: Tin")
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("malformed_gate_record", self._codes(out))

    def test_two_outcomes_malformed(self):
        rec = "### GATE RECORD\nOutcome: PASS\nOutcome: HARD-STOP\nReviewed by: Tin"
        self._mk_done("alpha", sec6=SEC_CLEAN + "\n\n" + rec)
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("malformed_gate_record", self._codes(out))

    # ---- F3 gate_record_mismatch --------------------------------------------
    def test_prose_state_mismatch(self):
        rec = "### GATE RECORD\nOutcome: HARD-STOP\nReviewed by: Tin"
        self._mk_done("alpha", sec6=SEC_CLEAN + "\n\n" + rec, gate="PASS")
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("gate_record_mismatch", self._codes(out))

    # ---- F13 ungated_verdict (a §6 verdict the engine never gated) -----------
    def test_ungated_verdict_flagged(self):
        # done/observe + gate=="none" + exactly one §6 Outcome -> ungated_verdict
        self._mk_ungated("alpha")          # §6 carries Outcome: PASS, but no engine gate
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("ungated_verdict", self._codes(out))
        text, _, _ = self._run()
        self.assertIn("ungated_verdict alpha", text)

    def test_engine_gated_task_not_flagged(self):
        # a normally-gated PASS task stays clean — the new arm must not over-fire
        self._mk_done("alpha")
        out, _, code = self._run("--json")
        self.assertEqual(code, 0, out)
        self.assertNotIn("ungated_verdict", self._codes(out))

    def test_mismatch_takes_precedence_over_ungated(self):
        # gate!=none and §6!=state -> gate_record_mismatch, NOT ungated_verdict
        rec = "### GATE RECORD\nOutcome: HARD-STOP\nReviewed by: Tin"
        self._mk_done("alpha", sec6=SEC_CLEAN + "\n\n" + rec, gate="PASS")
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("gate_record_mismatch", self._codes(out))
        self.assertNotIn("ungated_verdict", self._codes(out))

    # ---- F4 three-way matrix -------------------------------------------------
    def test_security_note_autogate_flagged(self):
        self._mk_done("alpha", sec6=_sec6(SEC_NOTE, REC_AUTO))
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("unescalated_security_note", self._codes(out))

    def test_security_note_human_ok(self):
        self._mk_done("alpha", sec6=_sec6(SEC_NOTE, REC_HUMAN))
        out, _, code = self._run("--json")
        self.assertNotIn("unescalated_security_note", self._codes(out))

    def test_clean_security_autogate_ok(self):
        self._mk_done("alpha", sec6=_sec6(SEC_CLEAN, REC_AUTO))
        out, _, code = self._run("--json")
        self.assertNotIn("unescalated_security_note", self._codes(out))

    # ---- F5 / F6 risk-accepted ------------------------------------------------
    def test_risk_accepted_security(self):
        rec = ("### GATE RECORD\nOutcome: RISK-ACCEPTED\n"
               "owner: Tin · ticket: T-1 · expires: 2026-07-01\nReviewed by: Tin")
        self._mk_done("alpha", sec6=SEC_NOTE + "\n\n" + rec, gate="RISK-ACCEPTED")
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("risk_accepted_security", self._codes(out))

    def test_waiver_incomplete(self):
        rec = "### GATE RECORD\nOutcome: RISK-ACCEPTED\nReviewed by: Tin"
        self._mk_done("alpha", sec6=SEC_CLEAN + "\n\n" + rec, gate="RISK-ACCEPTED")
        out, _, code = self._run("--json")
        self.assertEqual(code, 1)
        self.assertIn("waiver_incomplete", self._codes(out))

    # ---- scope + purity --------------------------------------------------------
    def test_open_task_skipped(self):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", "open-one", "--title", "open"])   # stays at specify
        out, _, code = self._run("--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["checked"], 0)

    def test_audit_pure(self):
        self._mk_done("alpha", sec3="Status: FROZEN")               # has a finding
        state_p = self._root() / "state.json"
        before = hashlib.sha256(state_p.read_bytes()).hexdigest()
        files = sorted(str(p) for p in self.tmp.rglob("*") if p.is_file())
        for argv in ((), ("--json",)):
            self._run(*argv)
        self.assertEqual(hashlib.sha256(state_p.read_bytes()).hexdigest(), before)
        self.assertEqual(sorted(str(p) for p in self.tmp.rglob("*") if p.is_file()), files)

    # ---- prose accord ------------------------------------------------------------
    def test_guide_states_marker_convention(self):
        canon = HERE.parent / "skill" / "add" / "phases" / "6-verify.md"
        text = canon.read_text(encoding="utf-8")
        self.assertIn(GUIDE_ANCHOR, text)
        for twin in (REPO / ".claude" / "skills" / "add" / "phases" / "6-verify.md",
                     BUNDLE / "skill" / "add" / "phases" / "6-verify.md"):
            self.assertEqual(canon.read_bytes(), twin.read_bytes(), f"divergence: {twin}")


if __name__ == "__main__":
    unittest.main()
