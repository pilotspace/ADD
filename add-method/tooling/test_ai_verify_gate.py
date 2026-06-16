#!/usr/bin/env python3
"""Eval-gated verify for kind:ai tasks (design part 4b).

The AI analog of 'tests green': a completing verify PASS for a kind:ai task requires a
RECORDED eval run whose measured score clears the FROZEN eval-spec threshold AND beats
the baseline AND carries its lineage, scored against the frozen eval set. Plus the
never-weaken guarantee: the eval-set/spec/rubric are frozen into the tamper tripwire at
tests->build, so a lowered threshold trips build_tampered through the existing guard.

Run: python3 -m unittest test_ai_verify_gate -v
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import add


def _w(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj) + "\n", encoding="utf-8")


class AiVerifyGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ai-gate-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = add.find_root()
        self.ai = self.root / "ai"

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def _spec(self, **over):
        d = {"threshold": 0.80, "baseline": {"score": 0.50}, "eval_set_hash": "H"}
        d.update(over)
        _w(self.ai / "eval-spec.json", d)

    def _run(self, **over):
        d = {"score": 0.90, "eval_set_hash": "H", "model_version": "m@1", "data_version": "v1"}
        d.update(over)
        _w(self.ai / "eval-run.json", d)

    def test_pass_when_clears_threshold_and_baseline_with_lineage(self):
        self._spec(); self._run()
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertTrue(ok, why)

    def test_below_threshold_fails(self):
        self._spec(); self._run(score=0.70)
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("below_threshold", why)

    def test_no_baseline_gain_fails(self):
        self._spec(threshold=0.40); self._run(score=0.50)   # == baseline
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("no_baseline_gain", why)

    def test_lineage_unrecorded_fails(self):
        self._spec(); self._run(model_version=None, model=None)
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("lineage_unrecorded", why)

    def test_stale_run_against_different_set_fails(self):
        self._spec(); self._run(eval_set_hash="OTHER")
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("eval_run_stale", why)

    def test_safety_finding_is_hard_stop(self):
        self._spec(); self._run(safety_findings=["prompt_injection"])
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("safety_hard_stop", why)

    def test_missing_run_fails_closed(self):
        self._spec()  # no eval-run.json
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("ai_eval_unrecorded", why)

    def test_missing_spec_fails_closed(self):
        self._run()  # no eval-spec.json
        ok, why = add._ai_verify_gate(self.root, "feat")
        self.assertFalse(ok); self.assertIn("ai_eval_contract_absent", why)


class TripwireFreezesAiContractTest(unittest.TestCase):
    """At tests->build, a kind:ai task freezes its eval contract into the tamper baseline."""

    def setUp(self) -> None:
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ai-trip-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = add.find_root()
        ai = self.root / "ai"
        _w(ai / "eval-set.jsonl", {"id": "a", "input": "x", "expected": "y", "split": "test"})
        _w(ai / "eval-spec.json", {"threshold": 0.8})
        _w(ai / "rubric.json", {"criteria": []})

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def test_ai_kind_freezes_the_three_contract_files(self):
        snap = add._tripwire_snapshot(self.root, "feat", "raw-§3", kind="ai")
        tracked = " ".join(snap["tests"].keys())
        for name in ("eval-set.jsonl", "eval-spec.json", "rubric.json"):
            self.assertIn(name, tracked, f"{name} must be in the tamper baseline for kind:ai")

    def test_code_kind_does_not_freeze_ai_files(self):
        snap = add._tripwire_snapshot(self.root, "feat", "raw-§3", kind="code")
        self.assertNotIn("eval-spec.json", " ".join(snap["tests"].keys()))


class NewTaskKindTest(unittest.TestCase):
    def setUp(self) -> None:
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ai-kind-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = add.find_root()

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def _kind(self, slug):
        st = json.loads((self.root / "state.json").read_text(encoding="utf-8"))
        return st["tasks"][slug]["kind"]

    def test_kind_ai_persists(self):
        add.main(["new-task", "ai-feat", "--kind", "ai"])
        self.assertEqual(self._kind("ai-feat"), "ai")

    def test_kind_defaults_to_code(self):
        add.main(["new-task", "plain-feat"])
        self.assertEqual(self._kind("plain-feat"), "code")


class MissingEvalSetTest(unittest.TestCase):
    """The freeze precondition: a populated .add/ai/ set with no eval-set.jsonl is a HARD red."""

    def setUp(self) -> None:
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ai-miss-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = add.find_root()
        self.ai = self.root / "ai"

    def tearDown(self) -> None:
        os.chdir(self._cwd)

    def test_populated_set_without_eval_set_is_a_red(self):
        # rest of the named set exists, eval-set.jsonl absent -> missing_eval_set
        _w(self.ai / "eval-spec.json", {"threshold": 0.8})
        _w(self.ai / "rubric.json", {"criteria": []})
        out = add._ai_foundation_violations(self.root)
        reasons = " ".join(r for _ok, _desc, r in out)
        self.assertIn("missing_eval_set", reasons)

    def test_empty_named_set_stays_silent(self):
        # no .add/ai/ files at all -> silent-when-absent, no missing_eval_set
        out = add._ai_foundation_violations(self.root)
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main()
