# task-kind `ai` — the eval-gated overlay (EDD)

Goal: when a task has an **AI component** — an open-ended generative model, a RAG
pipeline, an agent — its correctness is not a green unit test on one input. It is a
**statistical property over a held-out distribution**. This guide is the overlay that
re-aims five phases for that reality. It does not replace the phase guides; it **adds
beats** to specify · contract · tests · verify · observe and re-points their gates.

Created with `python3 .add/tooling/add.py new-task <slug> --kind ai`. Ownership does
not change (`PHASE_OWNER` is the same) — only the **verify auto-PASS condition** (an
eval threshold, not a green suite) and the **observe step** (online-eval/drift) move.

The whole `.add/ai/` vertical is **silent-when-absent**: a non-AI task triggers zero
AI validators and zero new behavior — exactly as UDD is inert without `.add/design/`.
Load this guide only when the task is `kind: ai`.

## The named set (read-only foundation the validators lint)

The AI analog of the red suite is a frozen **eval contract** under `.add/ai/`. Like
UDD's `tokens.json` / `catalog.json`, these are bound read-only by the build and linted
by `add.py check`:

| Artifact | Role |
|----------|------|
| `AI-SPEC.md` | Human-owned binding prose entry doc (the `DESIGN.md` analog) — the success metric tied to business impact, the four criteria buckets, the prompt→RAG→finetune ladder, the budget, the safety floor. |
| `eval-set.jsonl` | The frozen, held-out evaluation set — the AI analog of the red suite. Disjoint train/val/test split. The test split is **sacred**. |
| `rubric.json` | The scored acceptance rubric — the four buckets (capability · generation · instruction · cost_latency), each with a numeric threshold. |
| `eval-spec.json` | The reproducible run config + the pre-registered gate: primary metric + threshold + baseline-to-beat + the pinned judge + the eval-set content hash. |
| `io-contract.json` | The pinned, frozen I/O boundary — model id+version, response schema, guardrails, idempotency/retry, latency+cost envelope, train-only transforms. |
| `fallback.md` | The required per-failure-mode safe state — a probabilistic system with no declared fallback is unsafe by construction. |
| `monitor.json` | The Observe-phase online-eval + drift artifact (live signals, drift baseline, alert policy). |

## How each phase changes

### specify (kind `ai`) — run the AI-definition loop
When an AI feature reaches specify, run the **AI-definition loop in `ai.md`** (EDD)
— the `design.md` analog at `skill/add/ai.md`, loaded on demand. Write `AI-SPEC.md`: the human-owned success
metric tied to business impact, the four-bucket criteria, the prompt→RAG→finetune ladder
decision (with the cheaper rungs shown exhausted), the cost+latency budget, the safety
floor. The engine never drafts the metric or invents the bar — intent is human-owned.

### contract + tests (kind `ai`) — Freeze the eval contract
This is the AI analog of "tests are red". Inside the **one specification-bundle approval**
at the frozen §3, author and freeze the eval contract: a non-empty, disjoint-split
`eval-set.jsonl`; a four-bucket, thresholded `rubric.json`; an `eval-spec.json` with
metric + threshold + baseline + pinned judge + eval-set hash; an `io-contract.json` with
pinned model + response schema + guardrails + budget. The tests phase produces/freezes the
**eval pipeline** — the runner that scores the build against `eval-set.jsonl` by
`rubric.json` under `eval-spec.json` — in place of (or alongside) a unit suite. **The
frozen eval set is the red suite.** Its test rows + thresholds are md5-snapshotted into the
**existing tamper-tripwire** — no new tamper machinery is invented.

`_ai_named_set_checks` goes red on any missing/malformed/leaky/unthresholded artifact:
`missing_eval_set` · `empty_eval_set` · `malformed_eval_set` · `split_undeclared` ·
`split_overlap` · `rubric_missing_bucket` · `rubric_missing_threshold` · `baseline_missing`
· `threshold_undeclared` · `judge_unpinned` · `judge_self_preference` ·
`judge_bias_unmitigated` · `io_contract_unbound`. No clean freeze → no build.

Leakage codes are **HARD-STOP-class** from this freeze onward: `split_overlap` ·
`group_leakage` · `duplicate_leakage` · `selection_on_test`; preprocessing leakage and
eval/train contamination are not engine reds — the eval runner enforces them, since the
engine cannot see preprocessing or training code. A leaked eval is non-evidence, like a
weakened test — never RISK-ACCEPTED.

### build (kind `ai`) — bound by the frozen contract
AI-led implementation against the frozen `io-contract.json` and the `AI-SPEC.md` ladder
rung. The build may **not** touch the frozen test split, lower a threshold, peek at the
test partition, or weaken the rubric — the never-weaken-the-eval discipline, enforced by
the tamper tripwire — a mutated eval set trips `build_tampered`. Every model output is validated
against the response schema at the boundary before use; a schema-invalid output takes the
`fallback.md` path and never propagates.

### verify (kind `ai`) — Eval-gated, not green-tested
The verify auto-PASS condition from `6-verify.md` is **rerouted**. A green unit suite is
necessary-but-not-sufficient for an `ai` task. The gate reads `eval-spec.json` and **passes
only if**:

- measured-score **≥ frozen threshold**, AND
- measured-score **> baseline** (the declared majority/random/heuristic/human/prior-model bar), AND
- **lineage recorded** — the eval-set hash + the model/data version (`MODEL_REGISTRY.md`'s
  `## AI evals` row), so the score is reproducible and rollback-able.

The judge runs **≥2 samples and variance is reported, not a single sample** — one sample is
non-evidence because the same input scores differently across runs. **Cost + latency are
first-class**: the eval run measures the p50/p90/p99 + cost-per-request envelope, and an
over-budget build **fails even when quality passes**.

A below-threshold score (`below_threshold`) or a no-baseline-gain result **returns to Build**
— never lower the threshold, never trim the eval set (the never-weaken discipline). A
**safety/guardrail finding is a HARD-STOP** — prompt-injection (including indirect injection
via retrieved content), PII leak to an external API, jailbreak, missing toxicity guardrail,
or an unsafe action — merging into ADD's existing security-is-always-HARD-STOP rule; never
auto-passed, never RISK-ACCEPTED. A mutated eval set, an unpinned metric, or a weakened
threshold is frozen into the tamper tripwire; a post-freeze edit trips `build_tampered`
(HARD-STOP, never launderable through RISK-ACCEPTED).

Record **exactly one** outcome, as in `6-verify.md`:

| Outcome | When (kind `ai`) |
|---------|------------------|
| `PASS` | score ≥ threshold AND > baseline AND within budget AND lineage recorded — no safety/leakage finding. |
| `RISK-ACCEPTED` | a **non-safety** quality gap, with signed owner + ticket + expiry (a quality-bar shortfall the human knowingly ships). |
| `HARD-STOP` | a safety/guardrail finding, a leakage finding, or a tamper/weakened-eval (`build_tampered`). Returns to Build. |

### observe (kind `ai`) — Online-eval / drift
The §7 Observe step gains an **online-eval/drift beat**, extending the scenarios-as-monitors
line to the eval-score drift baseline. Per `monitor.json`: re-run a **sample of
`eval-set.jsonl` against production traffic / fresh data**, classify drift (covariate / label
/ concept), and record the **offline-vs-online delta** alongside the latency p50/p90/p99,
cost/request, and ≥1 implicit-feedback signal. A drift **below the frozen threshold** is
emitted as a **spec delta / reopen back at Specify** — an integrity-class escalation, never a
silent regression. The loop is not closed until production feedback re-enters as a delta.

`add.py check` raises a never-red `missing_monitor` WARN (the `missing_capture` analog) when a
shipped/observe `ai` task has no `monitor.json`, and `monitor_no_drift_baseline` WARN when a
monitor declares no drift baseline — nudges, never blockers.

## The hard rules

<constraints>
- **Freeze the eval before build.** `AI-SPEC.md` + a non-empty parseable `eval-set.jsonl` +
  `rubric.json` (four buckets + thresholds) + `eval-spec.json` (metric + threshold + baseline
  + disjoint split) present and frozen in the bundle — or build is refused.
- **Never tune on the held-out test split.** The test partition informs no preprocessing, no
  feature/prompt choice, no model selection, no stopping point. Leakage is HARD-STOP.
- **Never weaken the frozen eval.** Lowering a threshold, mutating a frozen test row, swapping
  in a lenient judge, or weakening the rubric is a change request back to Specify — caught by
  the tamper-tripwire, never RISK-ACCEPTED.
- **Verify gates on the score, not a green suite.** PASS = score ≥ threshold AND > baseline
  AND lineage recorded. Below-threshold returns to Build.
- **A safety/guardrail finding is always HARD-STOP** — merges into ADD's security rule.
- **Pin model + version + temperature(=0 for judges) + seed; report variance, not one sample.**
  The judge is independent of the model-under-test and carries bias mitigations.
- **Cost + latency are first-class acceptance constraints** — over-budget fails at verify even
  when quality passes.
- **The prompt → RAG → finetune ladder is the default; an escalation must be earned** and shown
  in `AI-SPEC.md` with the cheaper rungs exhausted.
- **Silent-when-absent and additive.** No `.add/ai/` → zero AI validators, zero new behavior.
</constraints>

## Exit gate / Next

<exit_gate>
- [ ] The eval contract was frozen in the bundle before build; the frozen test rows are
  unchanged since the tests→build snapshot.
- [ ] Verify recorded exactly one outcome on the **eval threshold** (PASS / RISK-ACCEPTED for a
  non-safety quality gap / HARD-STOP) — with score ≥ threshold AND > baseline AND lineage
  recorded, within the cost+latency budget, no safety or leakage finding.
- [ ] At observe: an online-eval/drift delta is recorded; any below-threshold drift re-entered
  Specify as a spec delta.
</exit_gate>

> This overlay rides on the base phase guides — read `phases/6-verify.md` for the
> evidence/outcome machinery this re-aims, and `ai.md` (the on-demand AI-definition loop, the
> `design.md` analog) for the specify-phase loop.

```bash
python3 .add/tooling/add.py gate PASS          # at verify: PASS only if score ≥ threshold AND > baseline AND lineage recorded
# or: add.py gate RISK-ACCEPTED (non-safety quality gap)   |   add.py gate HARD-STOP (return to Build)
```
Then read `phases/7-observe.md` for the online-eval/drift beat. Book:
`docs/19-ai-verify-and-observe.md`.
