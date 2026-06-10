#!/usr/bin/env python3
"""Behavioral proof of the independent-verifier auto-gate (Generator–Verifier split).

The problem this guards against: under `autonomy: auto`, the old "adversarial verify"
ran in the SAME context that wrote the code. In-context self-critique is unreliable —
a model favours its own output (self-enhancement bias) and repeats its own errors,
so the skeptic approves it uncritically. The fix makes the skeptic STRUCTURALLY independent:
the auto-gate decision is computed by the engine from recorded, structured verdicts
produced by fresh context-isolated verifier subagents (one per lens).

Three seams, each proven behaviorally:
  (A) Verdict SCHEMA — a verdict is well-formed data, not free-form prose; the engine
      validates shape (no shallow "looks good" passes).
  (B) CONSENSUS — the deterministic auto-gate decision over the recorded verdicts:
      any refutation or security finding blocks; residue escalates; an auto-PASS needs
      agreement across >= N independent lenses (self-consistency).
  (C) EVAL — the data-engineering harness: score the consensus logic against labeled
      fixtures so the gate's own judgment is measurable (recall = no seeded-bad build
      slips through).

Run: python3 -m unittest test_independent_verify -v
"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import add

SKILL = Path(__file__).resolve().parent.parent / "skill" / "add"


def _run(argv):
    """Invoke add.main, capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


# --- (A) verdict schema --------------------------------------------------------
class VerdictSchemaTest(unittest.TestCase):
    def test_well_formed_verdict_validates(self):
        errs = add._validate_verdict({
            "lens": "wiring", "verdict": "pass",
            "evidence": "every new symbol is referenced; no dead code",
            "refutation": "tried to find an unreachable export — none",
            "security": False,
        })
        self.assertEqual(errs, [])

    def test_missing_evidence_is_rejected(self):
        # the whole point: no shallow "looks good" — evidence is mandatory.
        errs = add._validate_verdict({"lens": "wiring", "verdict": "pass", "evidence": "  "})
        self.assertTrue(any("evidence" in e for e in errs), errs)

    def test_unknown_verdict_value_is_rejected(self):
        errs = add._validate_verdict({"lens": "wiring", "verdict": "lgtm", "evidence": "x"})
        self.assertTrue(any("verdict" in e for e in errs), errs)

    def test_empty_lens_is_rejected(self):
        errs = add._validate_verdict({"lens": "", "verdict": "pass", "evidence": "x"})
        self.assertTrue(any("lens" in e for e in errs), errs)

    def test_security_must_be_boolean(self):
        errs = add._validate_verdict(
            {"lens": "concurrency-security", "verdict": "pass", "evidence": "x", "security": "yes"})
        self.assertTrue(any("security" in e for e in errs), errs)


# --- (B) consensus decision ----------------------------------------------------
class ConsensusTest(unittest.TestCase):
    def _v(self, lens, verdict, security=False):
        return {"lens": lens, "verdict": verdict, "evidence": "e", "security": security}

    def test_three_independent_passes_auto_pass(self):
        outcome, _ = add._consensus([
            self._v("wiring", "pass"),
            self._v("concurrency-security", "pass"),
            self._v("contract-conformance", "pass"),
        ])
        self.assertEqual(outcome, "PASS")

    def test_any_refutation_hard_stops(self):
        outcome, reason = add._consensus([
            self._v("wiring", "pass"),
            self._v("contract-conformance", "fail"),
            self._v("concurrency-security", "pass"),
        ])
        self.assertEqual(outcome, "HARD-STOP")
        self.assertIn("contract-conformance", reason)

    def test_security_finding_is_always_hard_stop(self):
        # even a 'risk' (not 'fail') is a HARD-STOP when flagged security.
        outcome, reason = add._consensus([
            self._v("wiring", "pass"),
            self._v("concurrency-security", "risk", security=True),
            self._v("contract-conformance", "pass"),
        ])
        self.assertEqual(outcome, "HARD-STOP")
        self.assertIn("security", reason.lower())

    def test_non_security_risk_escalates_to_human(self):
        outcome, _ = add._consensus([
            self._v("wiring", "pass"),
            self._v("concurrency-security", "risk"),
            self._v("contract-conformance", "pass"),
        ])
        self.assertEqual(outcome, "ESCALATE")

    def test_thin_coverage_cannot_auto_pass(self):
        # two passing lenses is not enough independence for an auto-PASS.
        outcome, _ = add._consensus([
            self._v("wiring", "pass"),
            self._v("contract-conformance", "pass"),
        ])
        self.assertEqual(outcome, "ESCALATE")

    def test_duplicate_lens_does_not_count_twice(self):
        outcome, _ = add._consensus([
            self._v("wiring", "pass"),
            self._v("wiring", "pass"),
            self._v("wiring", "pass"),
        ])
        self.assertEqual(outcome, "ESCALATE")

    def test_no_verdicts_never_auto_passes(self):
        outcome, _ = add._consensus([])
        self.assertNotEqual(outcome, "PASS")


# --- command surface (verdict ledger + consensus) ------------------------------
class VerdictCommandTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-iv-")
        os.chdir(self.tmp)
        _run(["init", "--name", "demo"])
        self.root = add.find_root()
        _run(["new-task", "t"])

    def tearDown(self):
        os.chdir(self._cwd)

    def test_verdict_is_appended_to_ledger_and_consensus_reads_it(self):
        for lens in ("wiring", "concurrency-security", "contract-conformance"):
            code, _, err = _run(["verdict", "t", "--lens", lens, "--verdict", "pass",
                                 "--evidence", f"{lens}: checked"])
            self.assertEqual(code, 0, err)
        ledger = self.root / "tasks" / "t" / "verdicts.jsonl"
        self.assertTrue(ledger.exists(), "verdict ledger must be written")
        lines = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 3)

        code, out, _ = _run(["consensus", "t", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["outcome"], "PASS")
        self.assertEqual(data["verdicts"], 3)

    def test_invalid_verdict_is_refused_fail_closed(self):
        code, _, err = _run(["verdict", "t", "--lens", "wiring", "--verdict", "pass"])  # no evidence
        self.assertNotEqual(code, 0)
        self.assertIn("verdict", (err or "").lower())
        ledger = self.root / "tasks" / "t" / "verdicts.jsonl"
        self.assertFalse(ledger.exists(), "a refused verdict must not be written")

    def test_security_verdict_drives_hard_stop_consensus(self):
        _run(["verdict", "t", "--lens", "wiring", "--verdict", "pass", "--evidence", "ok"])
        _run(["verdict", "t", "--lens", "contract-conformance", "--verdict", "pass", "--evidence", "ok"])
        _run(["verdict", "t", "--lens", "concurrency-security", "--verdict", "fail",
              "--evidence", "hardcoded secret", "--security"])
        code, out, _ = _run(["consensus", "t", "--json"])
        self.assertEqual(json.loads(out)["outcome"], "HARD-STOP")


# --- (C) eval harness ----------------------------------------------------------
class EvalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="add-iv-eval-")
        self.fx = Path(self.tmp) / "eval"
        self.fx.mkdir()

    def _fixture(self, name, verdicts, label):
        (self.fx / name).write_text(json.dumps({"verdicts": verdicts, "label": label}))

    def test_eval_scores_consensus_against_labels(self):
        good = [{"lens": l, "verdict": "pass", "evidence": "e"}
                for l in ("wiring", "concurrency-security", "contract-conformance")]
        bad = [{"lens": "wiring", "verdict": "pass", "evidence": "e"},
               {"lens": "concurrency-security", "verdict": "fail", "evidence": "race"},
               {"lens": "contract-conformance", "verdict": "pass", "evidence": "e"}]
        self._fixture("good.json", good, "PASS")
        self._fixture("seeded-bad.json", bad, "HARD-STOP")

        code, out, err = _run(["eval", "--fixtures", str(self.fx), "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["fixtures"], 2)
        self.assertEqual(data["accuracy"], 1.0)
        # the safety metric: every seeded-bad build is caught (no false-negatives).
        self.assertEqual(data["fn"], 0)
        self.assertEqual(data["recall"], 1.0)


# --- skill wiring (the prompt surface that drives the subagents) ---------------
class SkillWiringTest(unittest.TestCase):
    def test_verify_critic_prompt_exists_and_demands_isolation(self):
        f = SKILL / "verify-critic.md"
        self.assertTrue(f.exists(), "skill/add/verify-critic.md must exist")
        text = f.read_text(encoding="utf-8").lower()
        for token in ("isolat", "fresh", "context", "refute", "consensus"):
            self.assertIn(token, text, f"verify-critic.md must mention {token!r}")

    def test_verify_phase_routes_to_independent_verification(self):
        text = (SKILL / "phases" / "6-verify.md").read_text(encoding="utf-8").lower()
        self.assertIn("verify-critic", text)
        self.assertIn("consensus", text)

    def test_run_autogate_requires_structural_independence(self):
        text = (SKILL / "run.md").read_text(encoding="utf-8").lower()
        self.assertIn("consensus", text)
        self.assertIn("context-isolated", text)


if __name__ == "__main__":
    unittest.main()
