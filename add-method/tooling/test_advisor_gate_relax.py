#!/usr/bin/env python3
"""Red/green tests for the advisor-gate-relax feature (milestone advisor-gated-autonomy).

Contract (frozen § 3):
  A risk:high task whose sensitivity is "mechanical" and whose §6 Advisor 3-lens
  verdict shows `Verdict: PASS` + `Residue: none` may auto-complete (gate PASS)
  WITHOUT a lowered autonomy dial (conservative/manual) at SITE 1 (cmd_gate).
  The audit (SITE 2) likewise does NOT flag unguarded_high_risk_auto for such a task.

  Security invariants that must hold:
    INV-1: sensitivity:security → guard ALWAYS fires (non-mechanical never relax)
    INV-2: sensitivity:data / architecture → guard ALWAYS fires
    INV-3: Residue ≠ "none" → guard fires even for mechanical
    INV-4: Verdict not PASS (HARD-STOP) → guard fires
    INV-5: advisor block absent → fail-safe False → guard fires
    INV-6: SITE 3 (autonomy set auto) → STILL strict; relaxation does NOT affect it
    INV-7: helpers scope to the Advisor sub-section; refute-read Verdict is never read

Run:
    python3 -m unittest test_advisor_gate_relax -v
"""
import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add

TOOLING = Path(add.__file__).resolve().parent

WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2026-07-01"]

# A minimal §6 §3 freeze stamp for audit tests
GOOD3 = "Status: FROZEN @ v1 — approved by Tin, 2026-06-05"


# ──────────────────────────────────────────────────────────────────────────────
# Shared board harness
# ──────────────────────────────────────────────────────────────────────────────
class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-agr-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def tearDown(self):
        os.chdir(self._cwd)

    # ── low-level CLI helpers ──────────────────────────────────────────────

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue()

    # ── TASK.md helpers ────────────────────────────────────────────────────

    def _task_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _mk_verify_task(self, slug: str, *, risk: str = "high",
                        sensitivity: str | None = None, autonomy: str | None = None):
        """Create a fresh task at verify, with optional header tokens on the slug line."""
        self._silent("new-task", slug, "--title", slug)
        self._silent("phase", "verify", slug)
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        extra = ""
        if risk:
            extra += f" · risk: {risk}"
        if sensitivity:
            extra += f" · sensitivity: {sensitivity}"
        if autonomy:
            extra += f" · autonomy: {autonomy}"
        if extra:
            t = re.sub(rf"(?m)^(slug: {slug}.*)$", rf"\1{extra}", t, count=1)
            p.write_text(t, encoding="utf-8")

    def _fill_advisor(self, slug: str, *, verdict: str = "PASS", residue: str = "none"):
        """Replace §6 advisor block placeholders with real values."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = t.replace("Advisor: <agent-id | self>", "Advisor: test-agent")
        t = t.replace("1. Security: <CLEAR | HARD-STOP: finding>", "1. Security: CLEAR")
        t = t.replace("2. Concurrency: <CLEAR | RESIDUE: finding>", "2. Concurrency: CLEAR")
        t = t.replace("3. Architecture: <CLEAR | RESIDUE: finding>", "3. Architecture: CLEAR")
        t = t.replace("Verdict: <PASS | HARD-STOP>", f"Verdict: {verdict}")
        t = t.replace("Residue: <none | summary>", f"Residue: {residue}")
        t = re.sub(r"Binding: <[^>\n]+(?:<[^>\n]+>)?[^>\n]*>", "Binding: yes — mechanical", t)
        p.write_text(t, encoding="utf-8")

    def _drop_advisor(self, slug: str):
        """Remove the entire advisor block from §6 (simulates a legacy TASK.md)."""
        p = self._task_md(slug)
        t = re.sub(
            r"### Advisor 3-lens verdict.*?(?=\n### GATE RECORD)",
            "",
            p.read_text(encoding="utf-8"),
            flags=re.DOTALL,
        )
        p.write_text(t, encoding="utf-8")

    def _gate(self, *argv):
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                add.main(["gate", *list(argv)])
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue()

    def _audit_findings_codes(self):
        code, out = self._run("audit", "--json")
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            return []
        return [x["code"] for x in d.get("findings", [])]


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (a): RELAXED PASS
#   risk:high + autonomy NOT lowered + sensitivity:mechanical + advisor PASS +
#   Residue: none  →  gate PASS succeeds + audit does NOT flag unguarded_high_risk_auto
# ──────────────────────────────────────────────────────────────────────────────
class RelaxedPassGateTest(_Board):
    def test_relaxed_pass_gate_succeeds(self):
        """mechanical + risk:high + no autonomy token + advisor PASS + Residue:none → PASS."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="PASS", residue="none")
        code, out = self._gate("PASS", "t")
        self.assertEqual(code, 0,
                         f"relaxed gate must succeed (exit 0):\n{out}")
        st = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(st["tasks"]["t"]["phase"], "done",
                         "relaxed gate must advance phase to done")

    def test_relaxed_risk_accepted_gate_succeeds(self):
        """mechanical + risk:high + RISK-ACCEPTED with advisor PASS + Residue:none → PASS."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="PASS", residue="none")
        code, out = self._gate("RISK-ACCEPTED", "t", *WAIVER)
        self.assertEqual(code, 0,
                         f"relaxed RISK-ACCEPTED gate must succeed:\n{out}")

    def test_audit_does_not_flag_relaxed_task(self):
        """After a relaxed gate, audit must NOT emit unguarded_high_risk_auto."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="PASS", residue="none")
        g_code, g_out = self._gate("PASS", "t")
        self.assertEqual(g_code, 0, f"gate must succeed before audit test:\n{g_out}")
        # Now write a proper §3 freeze stamp so audit doesn't bail on other findings
        p = self._task_md("t")
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^(## 3 · CONTRACT.*?)(\n## 4)",
                      lambda m_: m_.group(1) + f"\n{GOOD3}" + m_.group(2),
                      text, flags=re.DOTALL)
        p.write_text(text, encoding="utf-8")
        codes = self._audit_findings_codes()
        self.assertNotIn("unguarded_high_risk_auto", codes,
                         f"relaxed task must not produce unguarded_high_risk_auto finding")

    def test_hard_stop_still_allowed_without_advisor(self):
        """HARD-STOP is never blocked — even without advisor block."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        code, out = self._gate("HARD-STOP", "t")
        self.assertEqual(code, 0, f"HARD-STOP must always be allowed:\n{out}")


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (b): still-fires — advisor HARD-STOP verdict
# ──────────────────────────────────────────────────────────────────────────────
class StillFiresHardStopVerdictTest(_Board):
    def test_blocks_when_advisor_verdict_is_hard_stop(self):
        """mechanical + risk:high + advisor Verdict:HARD-STOP → gate blocked."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="HARD-STOP", residue="none")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0, "advisor HARD-STOP verdict must block the gate")
        self.assertIn("unguarded_high_risk_auto", out,
                      f"must emit the guard error code:\n{out}")

    def test_blocks_when_advisor_verdict_is_flag(self):
        """mechanical + risk:high + advisor Verdict:FLAG (not PASS-prefixed) → blocked."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="FLAG", residue="none")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("unguarded_high_risk_auto", out)


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (c): still-fires — Residue non-none
# ──────────────────────────────────────────────────────────────────────────────
class StillFiresResidueTest(_Board):
    def test_blocks_when_residue_is_non_none(self):
        """mechanical + risk:high + advisor PASS + Residue:leftover → gate blocked."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="PASS", residue="leftover concern")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0, "non-none Residue must block the gate")
        self.assertIn("unguarded_high_risk_auto", out)

    def test_blocks_when_residue_is_present_summary(self):
        """mechanical + risk:high + advisor PASS + Residue:minor latency risk → blocked."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._fill_advisor("t", verdict="PASS", residue="minor latency risk")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0)


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (d): non-mechanical sensitivities never relax (INV-1, INV-2)
# ──────────────────────────────────────────────────────────────────────────────
class NonMechanicalNeverRelaxTest(_Board):
    def _assert_blocked(self, sensitivity: str):
        self._mk_verify_task("t", risk="high", sensitivity=sensitivity)
        self._fill_advisor("t", verdict="PASS", residue="none")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0,
                             f"sensitivity:{sensitivity} must never relax the guard")
        self.assertIn("unguarded_high_risk_auto", out)

    def test_security_never_relaxes(self):
        """sensitivity:security + advisor PASS + Residue:none → STILL blocked (INV-1)."""
        self._assert_blocked("security")

    def test_data_never_relaxes(self):
        """sensitivity:data + advisor PASS + Residue:none → STILL blocked (INV-2)."""
        self._assert_blocked("data")

    def test_architecture_never_relaxes(self):
        """sensitivity:architecture + advisor PASS + Residue:none → STILL blocked (INV-2)."""
        self._assert_blocked("architecture")

    def test_no_sensitivity_declared_never_relaxes(self):
        """No sensitivity token at all → STILL blocked (None != 'mechanical')."""
        # task with no sensitivity token
        self._mk_verify_task("t", risk="high", sensitivity=None)
        self._fill_advisor("t", verdict="PASS", residue="none")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0,
                             "absent sensitivity must not relax the guard")
        self.assertIn("unguarded_high_risk_auto", out)


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (e): fail-safe — advisor block absent → guard fires (INV-5)
# ──────────────────────────────────────────────────────────────────────────────
class FailSafeNoAdvisorBlockTest(_Board):
    def test_blocks_when_advisor_block_absent(self):
        """mechanical + risk:high + NO advisor block → guard fires (fail-safe)."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        self._drop_advisor("t")
        code, out = self._gate("PASS", "t")
        self.assertNotEqual(code, 0, "absent advisor block must trigger guard (fail-safe)")
        self.assertIn("unguarded_high_risk_auto", out)


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (f): SITE 3 — autonomy set auto still strict (INV-6)
# ──────────────────────────────────────────────────────────────────────────────
class Site3StrictTest(_Board):
    def test_autonomy_set_auto_still_blocked_for_high_risk(self):
        """autonomy set auto on risk:high task → STILL dies (SITE 3 is unchanged)."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical",
                             autonomy="conservative")
        # fill advisor so relaxation would apply IF this were SITE 1
        self._fill_advisor("t", verdict="PASS", residue="none")
        code, out = self._run("autonomy", "set", "auto", "t")
        self.assertNotEqual(code, 0,
                             "autonomy set auto must be refused for risk:high (SITE 3 unchanged)")
        self.assertIn("unguarded_high_risk_auto", out,
                      f"SITE 3 guard must fire regardless of advisor:\n{out}")

    def test_autonomy_set_conservative_still_allowed(self):
        """autonomy set conservative on risk:high task → always allowed (non-raising direction)."""
        self._mk_verify_task("t", risk="high", sensitivity="mechanical")
        code, out = self._run("autonomy", "set", "conservative", "t")
        self.assertEqual(code, 0, f"lowering autonomy must always be allowed:\n{out}")


# ──────────────────────────────────────────────────────────────────────────────
# Scenario (g): unit tests for the two pure helpers (INV-7)
# ──────────────────────────────────────────────────────────────────────────────
class AdvisorHelperUnitTest(unittest.TestCase):
    """Test _advisor_verdict_is_pass and _advisor_no_residue in isolation."""

    # A minimal §6 body with a filled advisor block
    _BODY6_ADVISOR_PASS = "\n".join([
        "### Refute-read verdict — the earned-green check",
        "Verdict: EARNED",
        "By: self · adversarially checked: the full diff",
        "",
        "### Advisor 3-lens verdict — sequential",
        "Advisor: test-agent",
        "1. Security: CLEAR",
        "2. Concurrency: CLEAR",
        "3. Architecture: CLEAR",
        "Verdict: PASS",
        "Residue: none",
        "Binding: yes — mechanical",
        "",
        "### GATE RECORD",
        "Outcome: PASS",
        "Reviewed by: auto-gate · date: 2026-06-29",
    ])

    _BODY6_ADVISOR_HARD_STOP = "\n".join([
        "### Refute-read verdict — the earned-green check",
        "Verdict: EARNED",
        "By: self · adversarially checked: the full diff",
        "",
        "### Advisor 3-lens verdict — sequential",
        "Advisor: test-agent",
        "1. Security: HARD-STOP: found credentials in env",
        "Verdict: HARD-STOP",
        "Residue: critical security defect",
        "Binding: yes — mechanical",
        "",
        "### GATE RECORD",
        "Outcome: HARD-STOP",
        "Reviewed by: auto-gate · date: 2026-06-29",
    ])

    _BODY6_NO_ADVISOR_BLOCK = "\n".join([
        "### Refute-read verdict — the earned-green check",
        "Verdict: EARNED",
        "By: self · adversarially checked: the full diff",
        "",
        "### GATE RECORD",
        "Outcome: PASS",
        "Reviewed by: auto-gate · date: 2026-06-29",
    ])

    _BODY6_ADVISOR_RESIDUE = "\n".join([
        "### Advisor 3-lens verdict — sequential",
        "Advisor: test-agent",
        "1. Security: CLEAR",
        "2. Concurrency: RESIDUE: minor race on cold start",
        "Verdict: PASS",
        "Residue: minor race condition on cold start",
        "Binding: advisory — architecture",
        "",
        "### GATE RECORD",
        "Outcome: PASS",
        "Reviewed by: Tin · date: 2026-06-29",
    ])

    # ── _advisor_verdict_is_pass ───────────────────────────────────────────

    def test_verdict_pass_in_advisor_block(self):
        """Verdict: PASS in the advisor block → True."""
        self.assertTrue(add._advisor_verdict_is_pass(self._BODY6_ADVISOR_PASS))

    def test_verdict_hard_stop_in_advisor_block(self):
        """Verdict: HARD-STOP in the advisor block → False."""
        self.assertFalse(add._advisor_verdict_is_pass(self._BODY6_ADVISOR_HARD_STOP))

    def test_verdict_absent_advisor_block_false(self):
        """No advisor block → _advisor_verdict_is_pass returns False (fail-safe, INV-5)."""
        self.assertFalse(add._advisor_verdict_is_pass(self._BODY6_NO_ADVISOR_BLOCK))

    def test_verdict_not_fooled_by_refute_read_earned(self):
        """The refute-read's Verdict: EARNED must NOT satisfy _advisor_verdict_is_pass (INV-7).
        Body has no advisor block but DOES have refute-read Verdict: EARNED."""
        self.assertFalse(add._advisor_verdict_is_pass(self._BODY6_NO_ADVISOR_BLOCK))

    def test_verdict_pass_prefix_recognized(self):
        """Verdict: PASS-qualified → True (startswith 'PASS' is the rule)."""
        body = "\n".join([
            "### Advisor 3-lens verdict",
            "Verdict: PASS-with-notes",
            "Residue: none",
            "### GATE RECORD",
        ])
        self.assertTrue(add._advisor_verdict_is_pass(body))

    def test_refute_read_verdict_earned_not_pass(self):
        """Refute-read Verdict: EARNED does NOT start with PASS → stays False even with advisor block absent."""
        body = "### Refute-read verdict\nVerdict: EARNED\nBy: self\n\n### GATE RECORD\nOutcome: PASS\n"
        self.assertFalse(add._advisor_verdict_is_pass(body))

    def test_verdict_case_insensitive(self):
        """Verdict: pass (lowercase) → True (upper() check)."""
        body = "\n".join([
            "### Advisor 3-lens verdict",
            "Verdict: pass",
            "Residue: none",
            "### GATE RECORD",
        ])
        self.assertTrue(add._advisor_verdict_is_pass(body))

    # ── _advisor_no_residue ────────────────────────────────────────────────

    def test_residue_none(self):
        """Residue: none in advisor block → True."""
        self.assertTrue(add._advisor_no_residue(self._BODY6_ADVISOR_PASS))

    def test_residue_non_none(self):
        """Residue: non-none string → False."""
        self.assertFalse(add._advisor_no_residue(self._BODY6_ADVISOR_RESIDUE))

    def test_residue_absent_advisor_block_false(self):
        """No advisor block → _advisor_no_residue returns False (fail-safe, INV-5)."""
        self.assertFalse(add._advisor_no_residue(self._BODY6_NO_ADVISOR_BLOCK))

    def test_residue_scoped_to_advisor_block(self):
        """Residue line in a section OTHER than the advisor block does not satisfy
        _advisor_no_residue when the advisor block itself is absent."""
        body = "\n".join([
            "### Some other section",
            "Residue: none",
            "",
            "### GATE RECORD",
            "Outcome: PASS",
        ])
        # No "### Advisor 3-lens verdict" heading → fail-safe False
        self.assertFalse(add._advisor_no_residue(body))

    def test_residue_critical_defect_false(self):
        """Residue: critical defect → False."""
        self.assertFalse(add._advisor_no_residue(self._BODY6_ADVISOR_HARD_STOP))

    def test_residue_none_case_insensitive(self):
        """Residue: None (capital N) → True (strip().lower() check)."""
        body = "\n".join([
            "### Advisor 3-lens verdict",
            "Verdict: PASS",
            "Residue: None",
            "### GATE RECORD",
        ])
        self.assertTrue(add._advisor_no_residue(body))

    # ── combined: refute-read Verdict line never fools the helpers ────────

    def test_refute_read_verdict_pass_does_not_satisfy_advisor_verdict(self):
        """Body where refute-read says Verdict: PASS but advisor block is absent → False (INV-7).
        This is the critical anti-false-positive invariant."""
        body = "\n".join([
            "### Refute-read verdict",
            "Verdict: PASS",
            "By: self",
            "",
            "### GATE RECORD",
            "Outcome: PASS",
        ])
        self.assertFalse(add._advisor_verdict_is_pass(body),
                         "refute-read Verdict: PASS must NOT satisfy _advisor_verdict_is_pass "
                         "when the advisor block is absent")
        self.assertFalse(add._advisor_no_residue(body),
                         "absent advisor block must return False for _advisor_no_residue")


if __name__ == "__main__":
    unittest.main(verbosity=2)
