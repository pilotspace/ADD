# ADD-AI evals — the .add/ai named set

The evaluation foundation an **AI feature** drives from — the AI analog of the red
test suite. Six artifacts under `.add/ai/`, a fail-closed lint rule, and a freeze
that makes the eval contract tamper-evident. The named set is **silent when absent**:
a non-AI project has no `.add/ai/` and triggers zero AI validators — exactly as UDD
is silent without `.add/design/`. The shipped samples
(`ai/eval-set.sample.jsonl`, `ai/rubric.sample.json`, `ai/eval-spec.sample.json`,
`ai/io-contract.sample.json`, `ai/fallback.sample.md`, `ai/monitor.sample.json`)
are a worked **RAG docs-Q&A** example that validates clean against itself.

## Success metric and the bar are human-owned — set at specify

The named set checks an eval's **shape and integrity**; the *metric*, the *threshold*,
and the *baseline-to-beat* are product **direction**, not an AI default. During
**specify** the human writes `AI-SPEC.md` and sets the bar; the engine never invents
the metric or the threshold. Shape is verifiable; the bar is a human decision — and
once frozen, it is **never weakened** to make a build pass.

## The named set (silent-when-absent)

```
.add/ai/eval-set.jsonl    the frozen held-out cases — the AI analog of the red suite
.add/ai/rubric.json       the four-bucket scored acceptance rubric + thresholds
.add/ai/eval-spec.json    the reproducible run config + the pre-registered gate
.add/ai/io-contract.json  the pinned, frozen I/O boundary + guardrails + budget
.add/ai/fallback.md       the per-failure-mode safe state (graceful degradation)
.add/ai/monitor.json      the Observe-phase online-eval + drift artifact
```

Each file lints independently and **fail-closed**: a non-parseable JSON/JSONL emits a
named code (never a crash), mirroring `malformed_tokens_json`. The cross-file checks
(a judge resolving to a pinned judge, a guardrail wiring to a fallback line, a
within-file split disjoint of `eval-set.jsonl`) are the **composer's** job —
`_ai_named_set_checks(root)` wires them inside `add.py check`, beside
`_udd_named_set_checks`. It returns `[]` when no `.add/ai/` exists.

## eval-set.jsonl — the frozen held-out set

Line-delimited JSON, **one case per line**, `>= 1` case (`>= 10` recommended). It is
**sacred**: never tuned on, never peeked at during build (leakage is a HARD-STOP).

```
{ "id": str,                         unique across the file
  "input": str | object,             the case input (for RAG: a question + retrieval knobs)
  "expected": str | object,          the reference/golden answer
                                      (RAG: include "relevant_chunk_ids": [str])
  "split": "train" | "val" | "test", the disjoint partition this row belongs to
  "tags": [str],                     slice keys: tier:/topic:/length:/failure-mode:
  "group_key"?: str }                entity/session/doc for group-leakage detection
```

A non-parsing line is `malformed_eval_set` — **one named code, never a crash**.

## rubric.json — the four-bucket scored rubric

```
{ "criteria": [
    { "name": str,
      "bucket": "capability" | "generation" | "instruction" | "cost_latency",
      "method": "exact" | "llm_judge" | "metric" | "human",
      "threshold": number,
      "weight": number } ],
  "overall_threshold": number }
```

All **four bucket values must appear at least once** (`rubric_missing_bucket` if not),
every criterion **and** the overall rubric carry a numeric threshold
(`rubric_missing_threshold`), and every `llm_judge` criterion must resolve to a
**pinned** judge in `eval-spec.json`.

## eval-spec.json — the reproducible run config + the gate

```
{ "primary_metric": str,
  "threshold": number,                          the pass bar the verify gate reads
  "baseline": { "kind": "majority"|"random"|"heuristic"|"human"|"prior_model",
                "score": number },              the baseline-to-beat
  "split": { "train": int, "val": int, "test": int,
             "key": str, "stratify": str|null },
  "selection_partition": "train" | "val",       model-selection/early-stop split — NEVER "test"
  "eval_set_hash": str,                          md5 of the frozen test rows (the freeze fingerprint)
  "judge": { "model": str, "version": str, "temperature": 0, "seed": int,
             "samples": int>=2,
             "bias_mitigations": [ "randomized_order", "length_normalized",
                                   "judge_ne_model_under_test" ] } | null,
  "rag":   { "retrieval_metrics": [str], "generation_metrics": [str] } | null,
  "agent": { "max_steps": int, "max_cost": number,
             "max_latency_ms": int, "trajectory_metric": str } | null }
```

`eval_set_hash` is the **md5 of the byte-exact `split:"test"` rows** of
`eval-set.jsonl`. It is the freeze fingerprint the tamper-tripwire snapshots — the
sample's value `19d183e9994c258463f954aa2841fcd8` is the md5 of its five test rows. A
judge must pin `model+version+temperature(=0)+seed` and score over `>= 2` samples;
the judge must **differ** from the model-under-test in `io-contract.json`.

## io-contract.json — the pinned, frozen I/O boundary

```
{ "model": [ { "id": str, "version": str } ],
  "request_schema": <json-schema>,
  "response_schema": <json-schema>,
  "reader_policy": "lenient",                    unknown fields tolerated + preserved
  "guardrails": [ "toxicity"|"pii"|"injection"|"jailbreak"|"refusal"| ... ],
  "idempotency": { "key_field": str } | { "no_side_effect": true },
  "retry": { "max": int, "backoff": str, "jitter": bool },
  "budget": { "latency_ms": { "p50": int, "p90": int, "p99": int },
              "cost_per_req": number },
  "train_only_transforms": [str] }               leakage guard: fit on train only
```

Every model output is validated against `response_schema` **at the boundary** before
use; a schema-invalid output takes the fallback path and never propagates. A
strict-reject reader policy with no documented reason is `io_contract_strict_reject`.

## fallback.md — the per-failure-mode safe state

Markdown with **one H2 per failure mode** — `## Timeout`, `## Error`,
`## Low-confidence`, `## Schema-invalid output`, `## Guardrail trip`, plus
`## Empty retrieval` (RAG) / `## Tool failure` (agent) — each naming a concrete safe
path (cached · default · cheaper-model · human-in-loop · hard-deny), **never** "crash"
or "hang". A `## Limits` section declares `timeout_ms` + a bounded retry /
circuit-breaker. **Every guardrail** declared in `io-contract.json` must have a wired
fallback line, or `guardrail_without_fallback` goes red.

## monitor.json — the Observe-phase online-eval + drift artifact

```
{ "signals": [ { "name": str,
                 "kind": "quality"|"safety"|"latency"|"cost"|"feedback"
                        |"input_dist"|"prediction_dist",
                 "threshold": number|null, "baseline": number|null } ],
  "drift": { "baseline_metric": str, "baseline_score": number,
             "alert_threshold": number },
  "audit_log": { "fields": [str], "retention": str, "stamp_contract_version": bool },
  "alert": { "policy": str, "channel": str, "runbook": str } }
```

Must include `>= 1` **feedback-kind** signal and a **drift baseline**. Its absence on a
shipped/observe `ai` task is a **never-red** `missing_monitor` WARN — the exact analog
of UDD's `missing_capture`; a declared-but-baselineless monitor is `monitor_no_drift_baseline`.

## Validation — the named codes

`_ai_named_set_checks(root)` returns `[]` for a clean named set, else one
`(ok, desc, reason)` per finding; the reds feed `failed`, the WARNs ride the warnings
list and **never** feed `failed`. Pure, read-only, stdlib, fail-closed.

### Reds (FAIL — feed `failed`)

| code | when |
|------|------|
| `missing_eval_set` | a kind:`ai` task reached the tests/contract freeze with no `eval-set.jsonl` |
| `empty_eval_set` | `eval-set.jsonl` exists but holds zero parseable cases |
| `malformed_eval_set` | a non-parseable JSONL line (fail-closed, never a crash) |
| `split_undeclared` | `eval-spec.json` declares no train/val/test partition with counts + key |
| `split_overlap` | an example id appears in more than one partition (the split is not disjoint) |
| `empty_test_split` | the test partition has zero rows — nothing held out to gate on |
| `group_leakage` | a `group_key` straddles train and test (identity memorization) |
| `duplicate_leakage` | an identical/near-duplicate input hash appears in train **and** test |
| `selection_on_test` | `eval-spec.json` names `test` as the selection/early-stop partition |
| `rubric_missing_bucket` | `rubric.json` omits one of capability/generation/instruction/cost_latency |
| `rubric_missing_threshold` | a criterion (or the overall rubric) declares no numeric threshold |
| `baseline_missing` | `eval-spec.json` declares no baseline-to-beat (kind + score) |
| `threshold_undeclared` | `eval-spec.json` declares no primary metric or no pass threshold |
| `judge_unpinned` | a judge-scored dimension's judge lacks pinned model/version/temperature(=0)/seed |
| `judge_self_preference` | the pinned judge equals the model-under-test in `io-contract.json` |
| `judge_bias_unmitigated` | a judge lacks `randomized_order`/`length_normalized`, or `samples < 2` |
| `io_contract_unbound` | `io-contract.json` absent, no `response_schema`, or a case/fallback can't be validated |
| `model_unpinned` | `io-contract.json` declares no model id + version |
| `budget_undeclared` | no latency (p50/p90/p99) or cost-per-request envelope is declared |
| `io_contract_strict_reject` | a strict-reject reader policy with no documented reason |
| `io_no_idempotency_key` | a side-effecting/retried op declares no idempotency key nor a no-side-effect assertion |
| `fallback_missing` | no `fallback.md`, or a required failure mode is left undefined |
| `fallback_no_timeout` | `fallback.md` declares no timeout and no bounded retry/circuit-breaker |
| `guardrail_without_fallback` | an `io-contract.json` guardrail has no wired fallback line |
| `rag_retrieval_uneval` | a RAG task's `eval-spec` declares no retrieval metric |
| `rag_faithfulness_unchecked` | a RAG task declares no faithfulness/grounding generation metric |
| `agent_unbounded` | an agent task declares no step/cost/latency bound or no trajectory metric |
| `build_tampered` | a frozen test row, threshold, or rubric changed after the tests→build snapshot (the tamper tripwire) |

### WARNs (never feed `failed`)

| code | when |
|------|------|
| `eval_set_too_small` | fewer cases than the recommended floor (default `>= 10`) — too thin to be evidence |
| `metric_mismatch` | bare accuracy as the sole metric on an imbalanced set (a majority predictor would win) |
| `missing_monitor` | a shipped/observe kind:`ai` task has no `monitor.json` (the `missing_capture` analog) |
| `monitor_no_drift_baseline` | `monitor.json` declares no drift baseline (metric + score + alert_threshold) |

### Runner-enforced disciplines (the engine does not lint these)

The engine lints the named set's shape and integrity only; the following are the eval
**runner's** responsibility and emit no `check` code:

- **Preprocess leakage.** The runner fits train-only transforms on the train split
  alone — never on test rows. (The engine lints leakage only *within* `eval-set.jsonl`,
  via `duplicate_leakage` / `group_leakage`.)
- **Finetune contamination.** For the finetune rung the runner keeps the external
  finetune training set disjoint from the eval set; the engine has no view of that
  external set and lints only within `eval-set.jsonl`.
- **I/O compatibility breaks.** A breaking response-schema change across releases is
  caught at **release review**, not by `check`.
- **Overfit gap.** The verify beat reports the val-vs-test gap; it is not an engine WARN.

## The freeze rules — never weaken the eval

The eval contract (`eval-set.jsonl` test rows + `rubric.json` thresholds +
`eval-spec.json` metric/threshold/baseline) is **frozen at the contract/tests gate**
as the AI analog of the red suite, with **one human approval** in the specification
bundle. The frozen test rows + thresholds are **md5-snapshotted** into the existing
tamper-tripwire (`eval_set_hash`). After the freeze:

- **No leakage, ever.** `split_overlap`, `group_leakage`, `duplicate_leakage`,
  `selection_on_test` are **HARD-STOP class** — never `RISK-ACCEPTED`. A leaked eval is
  non-evidence, like a weakened test.
- **Never weaken the frozen eval.** `eval-set.jsonl` test rows + `eval-spec.json`
  threshold + `rubric.json` are frozen into the tamper tripwire at tests→build. Lowering
  the threshold, mutating a frozen test row, swapping in a lenient judge, or weakening
  `rubric.json` trips `build_tampered` — a change request back to **Specify**, never
  launderable through `RISK-ACCEPTED`.
- **The verify gate reads the SCORE, not green tests.** A kind:`ai` task PASSES only
  when measured-score `>= threshold` **AND** `> baseline` **AND** lineage (eval-set
  hash + model/data version) is recorded; the judge runs `>= 2` samples and reports
  variance, not one sample. Below-threshold returns to **Build**.
- **A safety/guardrail finding is always a HARD-STOP** — prompt-injection (incl.
  indirect injection via retrieved content), PII leak to an external API, jailbreak,
  missing toxicity guardrail, or unsafe action merges into ADD's
  security-is-always-HARD-STOP rule.
- **Cost and latency are first-class gates.** The budget in `AI-SPEC.md` +
  `io-contract.json` is measured by the verify eval run; an over-budget build fails at
  verify even when quality passes.

Lineage lives in `MODEL_REGISTRY.md`'s additive `## AI evals` section: the
model-under-test (id + version), the judge (model + version + temperature=0 + seed +
samples), the `eval_set_hash` (the same md5 `eval-spec.json` carries), the prompt/data
version. A model/version/temperature/seed change is a **change request, not a silent
edit** — re-run the frozen eval-set against the new pin before changing it.

The validator lints **shape + integrity only** — stdlib, tool-agnostic, no model
calls. The engine never runs the eval; it only **measures** the recorded scores. To
score a build, point your own runner at `eval-set.jsonl` by `rubric.json` under
`eval-spec.json`, pin the run in `MODEL_REGISTRY.md`, and record the result the verify
gate reads.
