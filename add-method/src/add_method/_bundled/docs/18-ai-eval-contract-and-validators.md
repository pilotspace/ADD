# 18 · The Eval Contract and Its Validators — Freezing What "Good" Means

[← 17 The AI vertical](./17-ai-driven-the-ai-vertical.md) · [Contents](./README.md) · Next: [19 Eval-Gated Verify and the Online-Eval / Drift Loop →](./19-ai-verify-and-observe.md)

---

[Chapter 17](./17-ai-driven-the-ai-vertical.md) made the case that an open-ended
generative component breaks the green/red unit test, and that the AI vertical answers by
relocating ADD's discipline rather than abandoning it: the thing you freeze before the
build stops being a list of `assert` lines and becomes an **eval set + a rubric + a
threshold**. This chapter is that promise cashed out file by file. It takes the six
artifacts of the `.add/ai/` named set apart, shows exactly what each one pins, and then
lights the validators that keep the whole contract honest once it is frozen.

The frame is the one [Chapter 17](./17-ai-driven-the-ai-vertical.md) established and worth
restating once, plainly, because everything below is a specialization of it. The eval
contract is the **AI analog of ADD's frozen §3 contract plus its red test suite**
([Step 3](./05-step-3-contract.md), [Step 4](./06-step-4-tests.md)). It is what one human
approves, once, inside the specification bundle at the contract freeze ([the
flow](./02-the-flow.md)) — and after that single approval it is *frozen*. The validators
in this chapter are how the engine enforces that it stays frozen, stays leakage-free, and
is never quietly weakened to clear a gate. They are pure, read-only, fail-closed, and —
the property that makes the vertical safe to ship everywhere — **silent when absent**. A
project with no `.add/ai/` set triggers zero of them.

A note on division of labor before we begin. The named set checks an eval's **shape and
integrity** — that a split is disjoint, that a judge is pinned, that a guardrail has a
wired fallback. It never checks whether the *bar is right*. The metric, the threshold, and
the baseline-to-beat are product **direction**, written by the human in `AI-SPEC.md` at
Specify; the engine never invents them. Shape is verifiable by a machine; the bar is a
human decision. That line — *the engine measures, the human decides* — runs through every
section here.

## 18.1 · `eval-set.jsonl` — the frozen held-out set, and why the test split is sacred

`eval-set.jsonl` is the AI analog of the red suite: the body of cases the model must rise
to meet, written from intent *before* the build, so it is an independent standard rather
than a flattering description of whatever the model happens to do. It is line-delimited
JSON, **one case per line**, at least one case (ten or more recommended), and each row
carries the same fixed shape:

```
{ "id":       str,                          unique across the file
  "input":    str | object,                 the case input (RAG: a question + retrieval knobs)
  "expected": str | object,                 the reference/golden answer
  "split":    "train" | "val" | "test",     the disjoint partition this row belongs to
  "tags":     [str],                         slice keys: tier:/topic:/length:/failure-mode:
  "group_key"?: str }                        entity/session/doc, for group-leakage detection
```

The load-bearing field is `split`, and the rule behind it is the oldest in machine
learning, imported here verbatim: **you train on one partition, you select and tune on a
second, and you gate on a third that you never touch until the gate fires.** *train* is
where the system is fit. *val* (validation) is where you choose between candidates —
prompts, retrieval knobs, model versions, early-stop points. *test* is the held-out
partition that exists for exactly one purpose: to produce the number the verify gate reads
([Chapter 19](./19-ai-verify-and-observe.md)). The three must be **disjoint** — no case may
appear in two of them, and nothing about a test case may have informed how the system was
built.

The test split is **sacred**, and the word is chosen deliberately. The moment you look at
a test case while building — to debug a failure, to tune a prompt against it, to pick the
checkpoint that happens to score well on it — that case stops being held out. It has leaked
into the build, and the score it later produces is no longer evidence; it is the model
grading its own homework. This is the precise analog of [Step 4](./06-step-4-tests.md)'s
rule that you never edit a red test to make a build pass. There you protect a frozen
assertion; here you protect a frozen *distribution*. A glimpse is a tamper.

So the test split is the freeze precondition. A `kind: ai` task **cannot enter build**
without a non-empty, parseable `eval-set.jsonl` with a populated test partition — the AI
analog of "the suite is red." No held-out set, no build: the validator goes red with
`missing_eval_set` (the file is absent on a build-bound task), `empty_eval_set` (it exists
but holds zero parseable cases), or `empty_test_split` (a split is declared but nothing is
held out to gate on). And because the parse is fail-closed, a single non-parseable line is
one named code — `malformed_eval_set`, with the offending line number — never a crash and
never a silent pass.

> **Do:** write the held-out set from intent before the build, and treat its test rows as
> write-once until the gate fires.
> **Don't:** peek at a test case to debug a build. The glimpse spends the evidence.

## 18.2 · Leakage is a HARD-STOP — the six named codes

A leaked eval is non-evidence the way a weakened test is non-evidence, so leakage is not a
quality gap a waiver can cover. The six leakage codes are **HARD-STOP class** — they merge
into the same un-waivable rule that governs a hardcoded secret ([Step 6](./08-step-6-verify.md))
and are **never launderable through `RISK-ACCEPTED`**. Each names a distinct way the held-out
set can be contaminated, and each is caught mechanically by reading shape alone:

- **`split_overlap`** — the same example `id` appears in more than one partition. The most
  basic failure: the split is simply not disjoint, so a test row was also a train row and
  the model has seen the answer.
- **`group_leakage`** — a `group_key` straddles train and test. Even when no individual row
  repeats, a *related* row can leak. If three questions about one document sit in train and
  a fourth sits in test, the model has effectively memorized the entity, not learned the
  task. `group_key` (a doc id, a session, a customer) lets the validator catch this
  family-resemblance leak that a per-row id check misses.
- **`duplicate_leakage`** — an identical or near-identical input hash appears in both train
  and test. The same question phrased once in each partition is a test the model already
  trained on, even though the ids differ. The validator hashes each normalized input and
  flags a hash that lives on both sides.
- **`selection_on_test`** — `eval-spec.json` names `test` as the model-selection or
  early-stop partition. This is using the held-out set to *choose*, which silently tunes the
  build toward the very rows that are supposed to judge it. Selection happens on *val*,
  never on *test* — the sacred split is read once, at the gate, and never as a tuning
  signal.

All four are caught from shape — ids, group keys, input hashes, the declared partitions —
without the engine ever running a model. And all four route the same way a contract tamper
routes: back to **Specify** as a change request, in the open, where a human re-decides. There
is no quiet fix for a leaked eval, because a quietly-fixed leak is just a leak nobody admitted
to.

> **Runner-enforced disciplines (the engine does not lint these).** Two related leakage
> guards live with the *runner*, not with `add.py check`, because the engine cannot see
> preprocessing code or an external training corpus:
> - **Train-only transforms.** A transform fit on test rows (a chunk-embedding index, a BM25
>   IDF table whose *statistics* are computed over the held-out set) leaks the test
>   distribution into the pipeline before inference. The eval runner must fit `train_only_transforms`
>   on the train split alone; the engine cannot inspect the fit, so this is a runner-enforced
>   discipline, not an `add.py check` red.
> - **Finetune-set disjointness.** For the finetune rung the runner keeps the finetune
>   training set disjoint from the eval set. The engine lints only *within* `eval-set.jsonl`
>   (`duplicate_leakage` / `group_leakage` cover train/test dupes there); contamination of an
>   external training set is not an engine red.

## 18.3 · `rubric.json` — the four-bucket scored rubric

One number rarely captures "good." A summarizer can be accurate and verbose; a RAG answerer
can be fluent and ungrounded; an instruction-follower can be correct and over budget. So the
rubric scores every AI feature across **four buckets**, each a distinct kind of quality, and
each criterion declares its own pass threshold:

```
{ "criteria": [
    { "name": str,
      "bucket": "capability" | "generation" | "instruction" | "cost_latency",
      "method": "exact" | "llm_judge" | "metric" | "human",
      "threshold": number,
      "weight": number } ],
  "overall_threshold": number }
```

The four buckets are the same four `AI-SPEC.md` names as criteria, now made measurable:

- **capability** — can it do the task at all? Correctness, coverage, the headline "is the
  answer right" question.
- **generation** — is the output grounded and non-hallucinated? The faithfulness bucket,
  load-bearing for RAG, where an answer can sound right while inventing.
- **instruction** — does it obey the format, the constraints, the refusals it was told to?
  An answer that is correct but ignores the required JSON shape or answers a question it was
  told to refuse fails here.
- **cost_latency** — is it affordable and fast enough to ship? Speed and spend are *quality
  dimensions*, not afterthoughts; a correct answer that costs too much or arrives too late is
  a product failure.

Two rules give the rubric teeth, and both are checked by `_rubric_violations` from shape
alone. **All four bucket values must appear at least once** — a rubric that scores
capability and generation but never instruction or cost_latency is `rubric_missing_bucket`,
because a whole class of quality is going unmeasured. And **every criterion, plus the overall
rubric, must carry a numeric threshold** — a criterion with no number to clear is
`rubric_missing_threshold`, because a bucket you score but never gate on is decoration. The
sample rubric clears both: four criteria spanning the four buckets, each with a threshold
and a weight, under an `overall_threshold` of `0.85`.

The validator also carries one WARN. If *every* criterion is a bare-accuracy criterion, it
raises `metric_mismatch` — on an imbalanced set a majority-class predictor already scores
high, so accuracy alone is a foot-gun that mistakes the base rate for skill. It is a nudge,
not a red: it rides the warnings list and never feeds `failed`. The engine reminds; the human
decides whether the metric mix is honest.

## 18.4 · `eval-spec.json` — the metric, the threshold, the baseline, and the pinned judge

If `rubric.json` is the scorecard, `eval-spec.json` is the **pre-registered gate** — the
config that says, before any score is measured, exactly what number will count as passing and
how that number will be produced. Pre-registration is the point: declaring the bar *before*
the result is what stops the bar from drifting to wherever the result lands.

```
{ "primary_metric": str,
  "threshold": number,                          the pass bar the verify gate reads
  "baseline": { "kind": "majority"|"random"|"heuristic"|"human"|"prior_model",
                "score": number },              the baseline-to-beat
  "split": { "train": int, "val": int, "test": int, "key": str, "stratify": str|null },
  "selection_partition": "train" | "val",       NEVER "test" (§18.2)
  "eval_set_hash": str,                          md5 of the frozen test rows (the freeze fingerprint)
  "judge": { "model": str, "version": str, "temperature": 0, "seed": int,
             "samples": int >= 2,
             "bias_mitigations": [ "randomized_order", "length_normalized",
                                   "judge_ne_model_under_test" ] } | null,
  "rag":   { "retrieval_metrics": [str], "generation_metrics": [str] } | null,
  "agent": { "max_steps": int, "max_cost": number,
             "max_latency_ms": int, "trajectory_metric": str } | null }
```

Three of these together *are* the gate, and the absence of any one is a red:

- **The metric and threshold.** `primary_metric` is the one number the verify gate reads;
  `threshold` is the bar it must clear. Neither present is `threshold_undeclared` — without
  them there is nothing to gate on at all.
- **The baseline-to-beat.** `baseline` declares what the model must *beat*, with a kind
  (majority class, random, a heuristic, a human, the prior model) and a score. No baseline is
  `baseline_missing`. The reason this is mandatory, not optional, is sharp: a threshold a
  majority-class predictor already clears is not evidence of skill. An accuracy of 0.85 looks
  impressive until you learn the majority class is 0.84. The baseline is what stops a high
  absolute number from masquerading as a real gain.

Then there is the **judge** — the mechanism that scores the dimensions a string-compare
can't, like faithfulness or answer correctness over paraphrases. An LLM judge is itself a
probabilistic component, so it must be pinned and de-biased or its scores are as unreliable
as the thing it grades. Three codes guard it:

- **`judge_unpinned`** — the judge lacks a pinned `model`, `version`, `temperature` (which
  must be `0`), or `seed`. An unpinned judge scores the same answer differently across runs,
  so its number is not rebuildable — and a number nobody can reproduce is an impression
  wearing a decimal point.
- **`judge_self_preference`** — the judge model equals the model-under-test in
  `io-contract.json`. A model grading its own output prefers its own style; self-preference
  bias inflates the score. The validator compares the judge's model id against the
  io-contract model ids and reds if they match. (This is why the io-contract is loaded first:
  the eval-spec check needs the model-under-test to make the comparison without reading disk
  itself.)
- **`judge_bias_unmitigated`** — the judge declares fewer than two `samples`, or omits the
  required `randomized_order` / `length_normalized` mitigations. Position bias (the judge
  favors whichever answer it sees first) and verbosity bias (it favors the longer answer) are
  the two best-documented judge pathologies; the mitigations neutralize them, and the
  two-sample floor exists because a one-sample judge score is non-evidence the way a test that
  passes only on Tuesdays is non-evidence (§18.5).

The metric and threshold are not only declared here — once the contract freezes they are
*frozen into the tamper tripwire*. Changing the metric to one the build happens to clear, or
sliding the threshold down a point, is the AI form of editing a frozen contract: a post-freeze
edit trips `build_tampered`, exactly as an edited §3 contract does (§18.7).

## 18.5 · Pin the run, report the variance — and `MODEL_REGISTRY.md` as the lineage record

A deterministic test gives the same answer twice; a generative model does not. Ask it the same
question with the same prompt and the wording — and often the score — differs run to run. That
single fact forces two disciplines the eval contract makes non-negotiable.

**Pin the run.** Every recorded score names the exact conditions that produced it: the
model and version under test, the temperature (`0` for a scored run, to remove sampling
noise), the seed, and — for a judged dimension — the judge's full pin. A score produced by
an unnamed model at an unknown temperature, judged by an unpinned grader over a single
sample, is not reproducible, and verification in ADD is *trust through evidence*
([Step 6](./08-step-6-verify.md)) — evidence nobody can rebuild is not evidence.

**Report the variance, not one sample.** Because the same input scores differently across
runs, a judged dimension runs over **at least two samples** and the gate reads the reported
spread, not a lucky single number. This is why `samples >= 2` is enforced in
`eval-spec.json` and why a one-sample judge is `judge_bias_unmitigated`. One sample of a
probabilistic process is an anecdote; the verify gate ([Chapter 19](./19-ai-verify-and-observe.md))
needs the distribution.

The lineage lives in **`MODEL_REGISTRY.md`**, in an additive `## AI evals` section — the
registry is to an AI feature what a build manifest is to a release. It records the
model-under-test (id + version), the judge (model + version + temperature `0` + seed +
samples), the `eval_set_hash` (the same md5 `eval-spec.json` carries), and the prompt/data
version. With that written down, anyone can re-point a runner at the frozen `eval-set.jsonl`,
by `rubric.json`, under `eval-spec.json`, and reproduce the number the gate read. And because
the pin is recorded, **changing it is a change request, not a silent edit** — bumping the
model version or the temperature means re-running the frozen eval against the new pin and
recording the result in the open, never quietly swapping the lineage under a passing score.

## 18.6 · `io-contract.json` + `fallback.md` — the deterministic boundary and the safe state

A contract in ADD is the frozen boundary between a producer and a consumer
([Step 3](./05-step-3-contract.md)). For an AI component the boundary matters *more*, not less,
because the producer is fluent and frequently wrong in *shape* as well as content.
`io-contract.json` pins that boundary:

```
{ "model":          [ { "id": str, "version": str } ],     which model(s), pinned
  "request_schema":  <json-schema>,                         what goes in
  "response_schema": <json-schema>,                         what must come out
  "reader_policy":   "lenient",                             tolerate + preserve unknown fields
  "guardrails":      [ "toxicity"|"pii"|"injection"|"jailbreak"|"refusal" ... ],
  "idempotency":     { "key_field": str } | { "no_side_effect": true },
  "retry":           { "max": int, "backoff": str, "jitter": bool },
  "budget":          { "latency_ms": { "p50": int, "p90": int, "p99": int }, "cost_per_req": number },
  "train_only_transforms": [str] }                          the leakage guard (§18.2)
```

The load-bearing rule is one sentence: **every AI output is validated against
`response_schema` at the boundary, before it is used; a schema-invalid output takes the
fallback path and never propagates.** This is the format-validation half of output
guardrails. The model may say anything; the boundary only lets through something the system
already agreed to read. A generation that does not parse is not an error to surface to a
user — it is a failure mode with a defined safe state. The validator `_io_contract_violations`
holds the boundary up:

- **`io_contract_unbound`** — `io-contract.json` is absent, or carries no `response_schema`.
  An output that cannot be format-validated is an unenforceable boundary; this is the named
  red that says so.
- **`model_unpinned`** — no model id + version. The same lineage discipline as §18.5, at the
  serving boundary: an un-pinned production model means the boundary cannot say which model's
  output it is validating.
- **`io_contract_strict_reject`** — a strict-reject reader policy with no documented reason.
  The boundary tolerates and *preserves* unknown fields (`reader_policy: "lenient"`) so the
  contract can evolve forward-compatibly; a strict policy turns every additive model-side
  change into a break, so one without a stated reason is flagged. (A genuinely breaking schema
  change across releases — a removed required field, a narrowed type — is caught at release
  review, not by `check`; it is a change request back to Specify, exactly as editing a frozen
  contract is elsewhere.)
- **`io_no_idempotency_key`** — a side-effecting or retried operation declares neither an
  idempotency key nor an explicit no-side-effect assertion. AI calls are retried — for
  timeouts, for low-confidence reruns — so any operation that *writes* must be safe to retry
  or it is a double-spend waiting to happen.
- **`budget_undeclared`** — no latency p50/p90/p99 envelope or cost-per-request ceiling. Cost
  and latency are first-class acceptance constraints (the verify run measures them,
  [Chapter 19](./19-ai-verify-and-observe.md)); a boundary with no declared budget has nothing
  to measure against.

Where `io-contract.json` declares *what* a valid output is, **`fallback.md`** declares what
happens when one isn't produced — because a probabilistic dependency has more than the
return/raise of a deterministic one. It times out, it returns schema-invalid output, it
answers below its own confidence floor, it trips a guardrail. **A probabilistic system
without a declared fallback is unsafe by construction**, so `fallback.md` is markdown with
one `H2` per failure mode, each naming a concrete safe path — `cached`, `default`,
`cheaper-model`, `human-in-loop`, `hard-deny` — **never `crash`, never `hang`**:

- `## Timeout`, `## Error`, `## Low-confidence`, `## Schema-invalid output`,
  `## Guardrail trip` — the base modes every AI task must define.
- `## Empty retrieval` (RAG) and `## Tool failure` (agent) — the specializations the task
  shape requires.
- `## Limits` — a declared `timeout_ms` and a bounded retry / circuit-breaker, because an
  unbounded wait on a probabilistic dependency is itself a failure mode.

`_fallback_violations` enforces three things from the document's shape. A missing file or an
undefined base mode is **`fallback_missing`**. A document with no timeout and no bounded
retry/circuit-breaker is **`fallback_no_timeout`** — design-for-failure pushed down to the
model boundary, the same discipline [16 · Releasing](./16-releasing.md) asks of the deploy
pipeline. And the cross-file check that ties the two artifacts together: **every guardrail
declared in `io-contract.json` must have a wired fallback line in `fallback.md`**, or
`guardrail_without_fallback` goes red. A guardrail you name but never handle is a guardrail in
name only — you cannot claim `pii` protection in the contract and leave no line that says what
happens when the PII guardrail fires. This pairing is what makes the safety floor un-cheatable,
and [Chapter 19](./19-ai-verify-and-observe.md) carries it forward into the verify gate, where a
tripped guardrail is a `HARD-STOP`.

## 18.7 · `_ai_named_set_checks` wired into `add.py check` — the validator and its code table

Everything above is enforced by one composer, **`_ai_named_set_checks(root)`**, wired into
`add.py check` beside the UDD vertical's `_udd_named_set_checks`. It mirrors that idiom
verbatim, and the mirror is the point — the AI vertical does not invent a second engine
philosophy, it reuses the proven one:

- **Pure and read-only.** Each per-artifact validator is a total function over already-parsed
  content: it returns a list of findings in deterministic document order, never mutates its
  input, never touches disk. Only the composer reads files.
- **Fail-closed on malformed JSON.** The composer loads each file through a local loader that
  catches a decode error and emits a named `malformed_*` code rather than crashing. A
  syntactically broken `eval-set.jsonl`, `rubric.json`, `eval-spec.json`, or
  `io-contract.json` is a finding, never a stack trace — bad content can never wave a build
  through by breaking the checker.
- **Silent when absent.** It discovers the named set under `.add/ai/` and returns `[]` the
  moment none of it exists. A non-AI project sees zero new behavior — the exact UDD guarantee.

The findings split by severity. The **reds feed `failed`** and block; the **WARNs ride the
warnings list and never feed `failed`** — they are nudges, the way [Step 4](./06-step-4-tests.md)
records a coverage target without making its absence fatal. Here is the full code table.

### Reds (FAIL — feed `failed`)

| code | when |
|------|------|
| `missing_eval_set` | a `kind: ai` task reached the contract/tests freeze with no `eval-set.jsonl` |
| `empty_eval_set` | `eval-set.jsonl` exists but holds zero parseable cases |
| `malformed_eval_set` | a non-parseable JSONL line (fail-closed, never a crash) |
| `split_undeclared` | no train/val/test partition with counts + key is declared |
| `split_overlap` | an example id appears in more than one partition — the split is not disjoint |
| `empty_test_split` | the test partition has zero rows — nothing held out to gate on |
| `group_leakage` | a `group_key` straddles train and test (identity memorization) |
| `duplicate_leakage` | an identical/near-duplicate input appears in train **and** test |
| `selection_on_test` | `eval-spec.json` names `test` as the selection/early-stop partition |
| `rubric_missing_bucket` | `rubric.json` omits one of capability/generation/instruction/cost_latency |
| `rubric_missing_threshold` | a criterion (or the overall rubric) declares no numeric threshold |
| `threshold_undeclared` | `eval-spec.json` declares no primary metric or no pass threshold |
| `baseline_missing` | `eval-spec.json` declares no baseline-to-beat (kind + score) |
| `judge_unpinned` | a judge lacks pinned model/version/temperature(=0)/seed |
| `judge_self_preference` | the pinned judge equals the model-under-test in `io-contract.json` |
| `judge_bias_unmitigated` | a judge lacks `randomized_order`/`length_normalized`, or `samples < 2` |
| `io_contract_unbound` | `io-contract.json` absent, no `response_schema`, or an output can't be validated |
| `model_unpinned` | `io-contract.json` declares no model id + version |
| `budget_undeclared` | no latency p50/p90/p99 or cost-per-request envelope is declared |
| `io_contract_strict_reject` | a strict-reject reader policy with no documented reason |
| `io_no_idempotency_key` | a side-effecting/retried op declares no idempotency key nor a no-side-effect assertion |
| `fallback_missing` | no `fallback.md`, or a required failure mode is left undefined |
| `fallback_no_timeout` | `fallback.md` declares no timeout and no bounded retry/circuit-breaker |
| `guardrail_without_fallback` | an `io-contract.json` guardrail has no wired fallback line |
| `rag_retrieval_uneval` | a RAG task's `eval-spec` declares no retrieval metric |
| `rag_faithfulness_unchecked` | a RAG task declares no faithfulness/grounding metric |
| `agent_unbounded` | an agent task declares no step/cost/latency bound or no trajectory metric |

### WARNs (never feed `failed`)

| code | when |
|------|------|
| `eval_set_too_small` | fewer cases than the recommended floor (default `>= 10`) — too thin to be evidence |
| `metric_mismatch` | bare accuracy as the sole metric on an imbalanced set (a majority predictor would win) |
| `missing_monitor` | a shipped/observe `kind: ai` task has no `monitor.json` (the `missing_capture` analog) |
| `monitor_no_drift_baseline` | `monitor.json` declares no drift baseline (metric + score + alert_threshold) |

> **Runner-enforced discipline (the engine does not lint this).** The val-vs-test score gap
> is *reported* by the verify beat ([Chapter 19](./19-ai-verify-and-observe.md)) as a
> leakage-suspect signal for a human to read; it is not an engine WARN.

### The never-weaken tamper-tripwire

One code — **`build_tampered`** — is not a lint of shape. It is the **tamper-tripwire**, and
it is the single most important inheritance the AI vertical takes from the rest of ADD. When
the specification bundle freezes, the byte-exact `split: "test"` rows of `eval-set.jsonl`, the
`rubric.json`, and the `eval-spec.json` thresholds are **frozen into the tamper tripwire** —
the same md5 mechanism that already catches an edited red test or an edited §3 contract
([Step 6](./08-step-6-verify.md)). `eval-spec.json` carries that md5 as `eval_set_hash` — in
the sample, `19d183e9994c258463f954aa2841fcd8`, the md5 of its five test rows.

After the freeze, the tripwire is absolute. Mutating a frozen test row, lowering a threshold,
swapping in a lenient judge, or weakening the rubric is a **post-freeze edit that trips
`build_tampered`** (against `.add/ai/<file>`) as a **`HARD-STOP`** — and that stop is **never
launderable through `RISK-ACCEPTED`**, exactly as the contract-tamper stop never is. The point is not pedantry; it
is the one cheat the whole vertical exists to refuse. Faced with a score a point under the bar,
the path of least resistance is to *move the bar* — trim the awkward test rows, soften the
judge, slide the threshold down. Each of those is, definitionally, no longer measuring the
thing you froze. In ADD you do not move the goalposts to score: you return to Build and earn
it honestly, or you take the gap back to Specify as a change request and let a human re-decide
the bar in the open. There is no third door — and the tripwire is what makes sure of it.

## 18.8 · The eval contract, in one line

**Freeze the held-out set before the build; keep the test split sacred and the splits
disjoint; score the four buckets against declared thresholds; pre-register the metric,
threshold, baseline, and a pinned bias-mitigated judge; pin the run and report variance;
validate every output against the boundary schema with a safe state per failure mode — and
let the validators hold all of it frozen and leakage-free.**

That is the AI analog of ADD's frozen contract plus its red suite: one human approval at the
freeze, then a named set the engine keeps honest. The leakage codes and the tamper-tripwire are
`HARD-STOP` class, never `RISK-ACCEPTED`; the shape checks are reds that block; the thin-evidence
and monitoring codes are WARNs that nudge; and a project with no `.add/ai/` set fires none of it.
With the contract frozen and the validators lit, the next chapter is where the contract finally
pays out — the **eval-gated verify** that reads the measured score instead of a green suite, and
the **online-eval / drift loop** that re-runs the frozen set against production and reopens at
Specify when the live score falls below the bar it was accepted at.

---

[← 17 The AI vertical](./17-ai-driven-the-ai-vertical.md) · [Contents](./README.md) · Next: [19 Eval-Gated Verify and the Online-Eval / Drift Loop →](./19-ai-verify-and-observe.md)
