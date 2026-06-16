# AI — the eval-definition loop (EDD)

When an **AI feature** reaches specify (a task created with `new-task <slug> --kind ai`),
define what *good* means before you build it. An open-ended generative component — a prompt, a
RAG pipeline, an agent — has no green/red unit test: correctness is a **statistical property over
a held-out set**, not a binary on one input. This loop takes the feature from its **success
metric** to a **frozen eval contract** — the AI analog of the red suite — that a human approves
**once**, *before* any build. It is loaded on demand (like `design.md` / `advisor.md`); the
engine never runs the eval for you — it only **measures** the scores you record.

Eval-before-build is the EDD half of the method. The named set a task draws from lives under
`.add/ai/` (`eval-set.jsonl` · `rubric.json` · `eval-spec.json` · `io-contract.json` ·
`fallback.md` · `monitor.json`); the dialect is in `ai-eval.md`. This loop is how you *fill*
that set for a feature and earn the human's sign-off on the bar before build. It is
silent-when-absent: a task without `--kind ai` and no `.add/ai/` set sees none of this.

## The loop — four beats

```
spec  →  ladder  →  eval-set  →  freeze-the-contract
```

Run the beats in order. Each feeds the next; the last ends at the one human approval at the
contract gate, with `add.py check` green over `.add/ai/`.

### 1 · spec
Write `AI-SPEC.md` (scaffolded at setup, the binding entry doc — the `DESIGN.md` analog). Start
from the **success metric tied to business impact**, not a model choice. Name the four criteria
buckets the feature must hold — **capability**, **generation faithfulness**, **instruction
following**, **cost and latency** — and the **safety floor** (the guardrail classes: prompt
injection incl. indirect, PII, jailbreak, toxicity). The metric, the buckets, and the budget are
this beat's output; they bound everything below.

### 2 · ladder (the cheapest rung that works)
Choose the adaptation rung on the **prompt → RAG → finetune** ladder, cheapest first. Record the
chosen rung in `AI-SPEC.md` with the cheaper rungs shown **exhausted**, not skipped — an
escalation is earned and flagged, and a jump to finetune is human-approved. Most features stop at
prompt or RAG; finetune is the justified exception, never the reflex.

### 3 · eval-set
Assemble `eval-set.jsonl` — the **frozen, held-out** set of real cases (≥1, ten or more
preferred). Declare a **disjoint** train / val / test split in `eval-spec.json`. The **test split
is sacred**: it informs no prompt, no retrieval tuning, no preprocessing, and no model selection.
A `group_key` (user / session / entity) must sit on one side of the split, never straddle it. The
held-out set is the bar the build is measured against, not material to tune on.

### 4 · freeze-the-contract
Complete the named set and freeze it as one bundle at the contract gate: `rubric.json` (the four
buckets, each with a pass threshold) · `eval-spec.json` (primary metric + threshold +
**baseline-to-beat** + the **pinned, bias-mitigated judge** — model+version+temperature 0+seed,
order randomized, judge ≠ model-under-test) · `io-contract.json` (the response schema validated
at the boundary, the guardrail set, idempotency/retry) · `fallback.md` (a declared safe state per
failure mode — timeout, error, low-confidence, schema-invalid, guardrail trip, empty retrieval,
tool failure — never *crash* or *hang*). `add.py check` lints the set in place and goes red on any
missing, malformed, leaky, un-thresholded, or unpinned-judge gap. The human approves the frozen
contract once; from here the `phases/ai.md` overlay re-aims the run.

## Tool-agnostic eval

How you run the eval is **your** choice, not the engine's: a notebook, an eval harness
(promptfoo / DeepEval / a bespoke script), an LLM-judge call, a retrieval-metrics pass — whatever
the agent has. You record the result (score, the frozen `eval-set` hash, model + data version)
where the verify reads it; the engine **measures** that recorded run against the frozen
`threshold` + `baseline`, and never executes a model itself. This keeps the loop framework-free
and the method portable across stacks.

The loop **binds** the named set under one human approval and leaves it frozen: after the contract
gate, lowering a threshold, trimming a test row, or swapping in a lenient judge is a tamper
(`build_tampered`, a `HARD-STOP`), never a quiet edit — a real change is a change request back to
Specify. Identity-of-the-judge and the held-out split stay fixed for the life of the contract.

## The hard rules

<constraints>
- **Freeze before build.** No build until `AI-SPEC.md` + a non-empty `eval-set.jsonl` + a
  thresholded `rubric.json` / `eval-spec.json` exist and `add.py check` is green over `.add/ai/`.
- **The test split is sacred.** It is never tuned on; a split overlap, a straddling `group_key`,
  a duplicate across partitions, or selection on the test set is a leakage `HARD-STOP`.
- **Never weaken the frozen eval.** A lowered threshold, a mutated frozen row, or a lenient judge
  swap trips `build_tampered` — the eval-contract analog of *never weaken a test*.
- **Judge independence + variance.** The judge is pinned (model+version+temperature 0+seed),
  bias-mitigated, and is not the model-under-test; report variance over ≥2 samples, not one run.
- **The engine measures, never runs.** The eval is a tool-agnostic recipe the agent runs; the
  engine reads the recorded scores and gates on them. A safety or guardrail finding is a
  `HARD-STOP` — part of the security rule, never waived.
</constraints>

> Used at specify for an AI feature: `phases/0-setup.md` scaffolds `AI-SPEC.md`, and
> `phases/1-specify.md` points here when the task is `--kind ai` — run the four beats, then
> carry the frozen eval contract into the run via `phases/ai.md`.
