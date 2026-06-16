"""Red suite for the ADD-AI vertical (add-ai-foundation).

Mirrors test_udd_check_lint.py: a pure-validator block over the named-set
linters and an integration block that drives `add.py check` over a real
`.add/ai/` named set in a tempdir. Wired against the DRAFT in
`_ai_validators_DRAFT.py` until the human pastes the functions into add.py;
the integration class imports `add` and exercises the wired `cmd_check`
(those tests stay RED until the AI section is wired in — exactly as the UDD
suite's integration reds did before its section landed).

What this suite pins:
  * clean named set -> check green, AI PASS lines, no writes (read-only);
  * each named FAIL fires its code (missing/empty eval set, leakage,
    rubric bucket/threshold, baseline/threshold, judge unpinned/self-pref/
    bias, io-contract unbound/model/budget, fallback missing/no-timeout,
    guardrail-without-fallback, rag/agent);
  * FAIL-CLOSED on malformed JSON / a non-parsing JSONL line
    (malformed_eval_set, malformed_*_json) — a named code, never a crash;
  * SILENT-WHEN-ABSENT — no .add/ai/ -> zero AI lines, check stays green;
  * the never-red missing_monitor WARN (never feeds `failed`).

The pure block imports the DRAFT module directly so it can run BEFORE the
wiring; the integration block imports `add`. When the human finishes wiring,
flip `_ai` to `import add as _ai` (or delete the DRAFT import) and the whole
suite runs against the real engine.
"""
import contextlib
import copy
import importlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add

# The pure validators live in the DRAFT until the human pastes them into add.py.
# Prefer the engine copy once wired (so the suite tracks the real functions);
# fall back to the DRAFT module so the suite is runnable pre-wiring.
if hasattr(add, "_ai_foundation_violations"):
    _ai = add
else:                                               # pre-wiring: read the DRAFT
    _ai = importlib.import_module("_ai_validators_DRAFT")


# ----------------------------------------------------------------------------
# fixtures — a clean, four-bucket, leakage-free named set
# ----------------------------------------------------------------------------
def _eval_rows(n_test=3, n_train=8):
    rows = []
    for i in range(n_train):
        rows.append({"id": f"tr{i}", "input": f"train-q-{i}", "expected": f"a{i}",
                     "split": "train", "tags": ["tier:a"]})
    for i in range(n_test):
        rows.append({"id": f"te{i}", "input": f"test-q-{i}", "expected": f"a{i}",
                     "split": "test", "tags": ["tier:a"]})
    return rows


def _rubric():
    return {
        "criteria": [
            {"name": "task_success", "bucket": "capability", "method": "exact",
             "threshold": 0.8, "weight": 0.4},
            {"name": "faithfulness", "bucket": "generation", "method": "llm_judge",
             "threshold": 0.9, "weight": 0.3},
            {"name": "format_adherence", "bucket": "instruction", "method": "exact",
             "threshold": 0.95, "weight": 0.2},
            {"name": "p90_latency", "bucket": "cost_latency", "method": "metric",
             "threshold": 800, "weight": 0.1},
        ],
        "overall_threshold": 0.85,
    }


def _spec(judge_model="judge-x", **over):
    s = {
        "primary_metric": "task_success",
        "threshold": 0.85,
        "baseline": {"kind": "majority", "score": 0.5},
        "split": {"train": 8, "val": 0, "test": 3, "key": "id", "stratify": None},
        "selection_partition": "val",
        "eval_set_hash": "deadbeef",
        "judge": {"model": judge_model, "version": "2026-01", "temperature": 0,
                  "seed": 7, "samples": 3,
                  "bias_mitigations": ["randomized_order", "length_normalized",
                                       "judge_ne_model_under_test"]},
        "rag": None, "agent": None,
    }
    s.update(over)
    return s


def _io():
    return {
        "model": [{"id": "model-under-test", "version": "1.4"}],
        "request_schema": {"type": "object"},
        "response_schema": {"type": "object", "required": ["answer"]},
        "reader_policy": "lenient",
        "guardrails": ["toxicity", "pii", "injection"],
        "idempotency": {"no_side_effect": True},
        "retry": {"max": 2, "backoff": "exponential", "jitter": True},
        "budget": {"latency_ms": {"p50": 200, "p90": 600, "p99": 1200},
                   "cost_per_req": 0.004},
        "train_only_transforms": [],
    }


def _fallback():
    return (
        "# Fallback\n"
        "## Timeout\nServe the cached answer; bound at timeout_ms 1500.\n"
        "## Error\nReturn the safe default, log the exception.\n"
        "## Low-confidence\nRoute to the cheaper deterministic path.\n"
        "## Schema-invalid output\nReject the output, take the human-in-loop path.\n"
        "## Guardrail trip\nHard-deny; toxicity / pii / injection all route here.\n"
        "## Limits\ntimeout_ms 1500, retry max 2 with backoff; circuit-breaker on 3 fails.\n"
    )


def _monitor():
    return {
        "signals": [
            {"name": "online_quality", "kind": "quality", "threshold": 0.8, "baseline": 0.85},
            {"name": "thumbs", "kind": "feedback", "threshold": 0.6, "baseline": 0.7},
        ],
        "drift": {"baseline_metric": "task_success", "baseline_score": 0.85,
                  "alert_threshold": 0.05},
        "audit_log": {"fields": ["req_id"], "retention": "30d", "stamp_contract_version": True},
        "alert": {"policy": "page", "channel": "#oncall", "runbook": "rb-7"},
    }


def _codes(v):
    return [x[0] for x in v]


# ----------------------------------------------------------------------------
# pure validators
# ----------------------------------------------------------------------------
class EvalSetValidatorTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertEqual(_ai._eval_set_violations(_eval_rows()), [])

    def test_empty(self):
        self.assertIn("empty_eval_set", _codes(_ai._eval_set_violations([])))

    def test_too_small_warn(self):
        v = _ai._eval_set_violations(_eval_rows(n_test=1, n_train=2))
        self.assertIn("eval_set_too_small", _codes(v))

    def test_split_undeclared(self):
        rows = [{"id": "a", "input": "x", "expected": "y"}]
        self.assertIn("split_undeclared", _codes(_ai._eval_set_violations(rows)))

    def test_split_overlap(self):
        rows = _eval_rows()
        rows.append({"id": "tr0", "input": "dup-id", "expected": "y", "split": "test"})
        self.assertIn("split_overlap", _codes(_ai._eval_set_violations(rows)))

    def test_empty_test_split(self):
        rows = _eval_rows(n_test=0, n_train=10)
        self.assertIn("empty_test_split", _codes(_ai._eval_set_violations(rows)))

    def test_group_leakage(self):
        rows = _eval_rows()
        rows[0]["group_key"] = "user-7"
        rows[-1]["group_key"] = "user-7"          # straddles train + test
        self.assertIn("group_leakage", _codes(_ai._eval_set_violations(rows)))

    def test_duplicate_leakage(self):
        rows = _eval_rows()
        rows.append({"id": "extra", "input": "train-q-0", "expected": "a0", "split": "test"})
        self.assertIn("duplicate_leakage", _codes(_ai._eval_set_violations(rows)))

    def test_pure(self):
        rows = _eval_rows()
        snap = copy.deepcopy(rows)
        _ai._eval_set_violations(rows)
        self.assertEqual(rows, snap)


class RubricValidatorTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertEqual(_ai._rubric_violations(_rubric()), [])

    def test_missing_bucket(self):
        r = _rubric()
        r["criteria"] = r["criteria"][:2]             # drops instruction + cost_latency
        codes = _codes(_ai._rubric_violations(r))
        self.assertIn("rubric_missing_bucket", codes)

    def test_missing_threshold(self):
        r = _rubric()
        del r["criteria"][0]["threshold"]
        self.assertIn("rubric_missing_threshold", _codes(_ai._rubric_violations(r)))

    def test_missing_overall_threshold(self):
        r = _rubric()
        del r["overall_threshold"]
        self.assertIn("rubric_missing_threshold", _codes(_ai._rubric_violations(r)))

    def test_metric_mismatch_warn(self):
        r = {"criteria": [
            {"name": "accuracy", "bucket": "capability", "method": "exact", "threshold": 0.9},
            {"name": "accuracy2", "bucket": "generation", "method": "exact", "threshold": 0.9},
            {"name": "accuracy3", "bucket": "instruction", "method": "exact", "threshold": 0.9},
            {"name": "accuracy4", "bucket": "cost_latency", "method": "exact", "threshold": 0.9},
        ], "overall_threshold": 0.9}
        self.assertIn("metric_mismatch", _codes(_ai._rubric_violations(r)))


class EvalSpecValidatorTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertEqual(
            _ai._eval_spec_violations(_spec(), model_under_test=_io()["model"]), [])

    def test_threshold_undeclared(self):
        s = _spec(); del s["threshold"]
        self.assertIn("threshold_undeclared", _codes(_ai._eval_spec_violations(s)))

    def test_baseline_missing(self):
        s = _spec(); del s["baseline"]
        self.assertIn("baseline_missing", _codes(_ai._eval_spec_violations(s)))

    def test_split_undeclared(self):
        s = _spec(); del s["split"]
        self.assertIn("split_undeclared", _codes(_ai._eval_spec_violations(s)))

    def test_selection_on_test(self):
        s = _spec(selection_partition="test")
        self.assertIn("selection_on_test", _codes(_ai._eval_spec_violations(s)))

    def test_judge_unpinned(self):
        s = _spec(); s["judge"]["temperature"] = 0.7; del s["judge"]["seed"]
        self.assertIn("judge_unpinned", _codes(_ai._eval_spec_violations(s)))

    def test_judge_self_preference(self):
        s = _spec(judge_model="model-under-test")
        v = _ai._eval_spec_violations(s, model_under_test=_io()["model"])
        self.assertIn("judge_self_preference", _codes(v))

    def test_judge_bias_unmitigated(self):
        s = _spec(); s["judge"]["bias_mitigations"] = []; s["judge"]["samples"] = 1
        self.assertIn("judge_bias_unmitigated", _codes(_ai._eval_spec_violations(s)))

    def test_rag_uneval(self):
        s = _spec(rag={"retrieval_metrics": [], "generation_metrics": []})
        codes = _codes(_ai._eval_spec_violations(s))
        self.assertIn("rag_retrieval_uneval", codes)
        self.assertIn("rag_faithfulness_unchecked", codes)

    def test_agent_unbounded(self):
        s = _spec(agent={"trajectory_metric": ""})
        self.assertIn("agent_unbounded", _codes(_ai._eval_spec_violations(s)))


class IoContractValidatorTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertEqual(_ai._io_contract_violations(_io()), [])

    def test_unbound_no_schema(self):
        c = _io(); del c["response_schema"]
        self.assertIn("io_contract_unbound", _codes(_ai._io_contract_violations(c)))

    def test_model_unpinned(self):
        c = _io(); c["model"] = [{"id": "x"}]            # no version
        self.assertIn("model_unpinned", _codes(_ai._io_contract_violations(c)))

    def test_budget_undeclared(self):
        c = _io(); del c["budget"]
        self.assertIn("budget_undeclared", _codes(_ai._io_contract_violations(c)))

    def test_strict_reject(self):
        c = _io(); c["reader_policy"] = "strict"          # no strict_reason
        self.assertIn("io_contract_strict_reject", _codes(_ai._io_contract_violations(c)))

    def test_no_idempotency_key_when_side_effect(self):
        c = _io(); c["idempotency"] = {}
        v = _ai._io_contract_violations(c, has_side_effect=True)
        self.assertIn("io_no_idempotency_key", _codes(v))


class FallbackValidatorTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertEqual(_ai._fallback_violations(_fallback(), _io()), [])

    def test_absent_is_missing(self):
        self.assertIn("fallback_missing", _codes(_ai._fallback_violations(None, _io())))

    def test_missing_mode(self):
        txt = _fallback().replace("## Timeout\nServe the cached answer; bound at timeout_ms 1500.\n", "")
        self.assertIn("fallback_missing", _codes(_ai._fallback_violations(txt, _io())))

    def test_no_timeout(self):
        txt = ("## Timeout\nserve cached\n## Error\ndefault\n## Low confidence\ncheaper\n"
               "## Schema invalid output\nreject\n## Guardrail trip\ndeny\n")  # no Limits/timeout
        self.assertIn("fallback_no_timeout", _codes(_ai._fallback_violations(txt, _io())))

    def test_guardrail_without_fallback(self):
        c = _io(); c["guardrails"] = ["toxicity", "jailbreak"]
        txt = _fallback()                                # mentions toxicity but not jailbreak
        codes = _codes(_ai._fallback_violations(txt, c))
        self.assertIn("guardrail_without_fallback", codes)


class MonitorValidatorTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertEqual(_ai._monitor_violations(_monitor()), [])

    def test_no_drift_baseline(self):
        m = _monitor(); del m["drift"]
        self.assertIn("monitor_no_drift_baseline", _codes(_ai._monitor_violations(m)))

    def test_no_feedback_signal(self):
        m = _monitor(); m["signals"] = [m["signals"][0]]   # drop the feedback signal
        self.assertIn("missing_monitor", _codes(_ai._monitor_violations(m)))


# ----------------------------------------------------------------------------
# integration: the cmd_check "AI foundation" section over .add/ai/
# (RED until the human wires _ai_foundation_violations into cmd_check)
# ----------------------------------------------------------------------------
class CheckAiSectionTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-ai-check-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo", "--stage", "mvp"])
        self.ai = Path(self.tmp) / ".add" / "ai"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, *, rows=None, rubric=None, spec=None, io_c=None,
               fallback=None, monitor=None, raw=None):
        self.ai.mkdir(parents=True, exist_ok=True)
        if rows is not None:
            (self.ai / "eval-set.jsonl").write_text(
                "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        if rubric is not None:
            (self.ai / "rubric.json").write_text(json.dumps(rubric), encoding="utf-8")
        if spec is not None:
            (self.ai / "eval-spec.json").write_text(json.dumps(spec), encoding="utf-8")
        if io_c is not None:
            (self.ai / "io-contract.json").write_text(json.dumps(io_c), encoding="utf-8")
        if fallback is not None:
            (self.ai / "fallback.md").write_text(fallback, encoding="utf-8")
        if monitor is not None:
            (self.ai / "monitor.json").write_text(json.dumps(monitor), encoding="utf-8")
        if raw:
            for rel, content in raw.items():
                p = self.ai / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")

    def _clean_set(self):
        self._write(rows=_eval_rows(), rubric=_rubric(), spec=_spec(),
                    io_c=_io(), fallback=_fallback())

    def _check(self):
        buf = io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(["check"])
        except SystemExit as e:
            code = e.code or 0
        return code, buf.getvalue()

    def test_clean_named_set_passes(self):
        self._clean_set()
        before = {p: p.read_bytes() for p in self.ai.rglob("*")}
        code, out = self._check()
        self.assertEqual(code, 0, out)
        self.assertIn("held-out-valid", out)
        self.assertIn("gate-valid", out)
        after = {p: p.read_bytes() for p in self.ai.rglob("*")}
        self.assertEqual(before, after, "cmd_check must be read-only")

    def test_split_overlap_red(self):
        rows = _eval_rows()
        rows.append({"id": "tr0", "input": "dup", "expected": "y", "split": "test"})
        self._write(rows=rows, rubric=_rubric(), spec=_spec(), io_c=_io(), fallback=_fallback())
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("split_overlap", out)

    def test_rubric_missing_bucket_red(self):
        r = _rubric(); r["criteria"] = r["criteria"][:2]
        self._write(rows=_eval_rows(), rubric=r, spec=_spec(), io_c=_io(), fallback=_fallback())
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("rubric_missing_bucket", out)

    def test_judge_self_preference_red(self):
        self._write(rows=_eval_rows(), rubric=_rubric(),
                    spec=_spec(judge_model="model-under-test"), io_c=_io(), fallback=_fallback())
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("judge_self_preference", out)

    def test_io_contract_unbound_red(self):
        c = _io(); del c["response_schema"]
        self._write(rows=_eval_rows(), rubric=_rubric(), spec=_spec(), io_c=c, fallback=_fallback())
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("io_contract_unbound", out)

    def test_fallback_missing_red(self):
        self._write(rows=_eval_rows(), rubric=_rubric(), spec=_spec(), io_c=_io())
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("fallback_missing", out)

    def test_malformed_eval_set_failclosed(self):
        self._write(rubric=_rubric(), spec=_spec(), io_c=_io(), fallback=_fallback(),
                    raw={"eval-set.jsonl": '{"id":"a","split":"test"}\n{ not json\n'})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("malformed_eval_set", out)
        self.assertIn("check:", out)              # tally still printed — did not crash

    def test_malformed_rubric_failclosed(self):
        self._write(rows=_eval_rows(), spec=_spec(), io_c=_io(), fallback=_fallback(),
                    raw={"rubric.json": "{ not valid json"})
        code, out = self._check()
        self.assertEqual(code, 1)
        self.assertIn("malformed_rubric_json", out)
        self.assertIn("check:", out)

    def test_eval_set_too_small_is_warn_not_fail(self):
        """eval_set_too_small must WARN, never feed `failed` — a thin-but-clean set stays green."""
        self._write(rows=_eval_rows(n_test=1, n_train=2), rubric=_rubric(), spec=_spec(),
                    io_c=_io(), fallback=_fallback())
        code, out = self._check()
        self.assertEqual(code, 0, out)
        self.assertIn("eval_set_too_small", out)
        self.assertIn("WARN", out)

    def test_no_named_set_is_silent(self):
        """A project with no .add/ai/ emits NO AI line and stays green (the non-AI dogfood case)."""
        code, out = self._check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("held-out-valid", out)
        self.assertNotIn("gate-valid", out)

    def test_missing_monitor_is_warn_only(self):
        """A shipped 'ai' task with no monitor.json -> a never-red missing_monitor WARN."""
        self._clean_set()
        # mark an 'ai' task in observe phase with no monitor.json present
        state_path = Path(self.tmp) / ".add" / "state.json"
        st = json.loads(state_path.read_text(encoding="utf-8"))
        st.setdefault("tasks", {})["feat"] = {"title": "feat", "phase": "observe",
                                              "gate": "PASS", "kind": "ai",
                                              "depends_on": []}
        state_path.write_text(json.dumps(st), encoding="utf-8")
        code, out = self._check()
        self.assertIn("missing_monitor", out)
        # the monitor absence is a never-red WARN, never a red FAIL line — it rides
        # `warnings`, so it never feeds `failed` on its own account.
        self.assertIn("WARN  missing_monitor", out)
        self.assertNotIn("FAIL  missing_monitor", out)


if __name__ == "__main__":
    unittest.main()
