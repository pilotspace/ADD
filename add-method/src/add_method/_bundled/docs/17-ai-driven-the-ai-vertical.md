# 17 · The AI Vertical — Evaluation-Driven Development inside ADD

[← 16 Releasing](./16-releasing.md) · [Contents](./README.md) · Next: [18 The Eval Contract and Its Validators →](./18-ai-eval-contract-and-validators.md)

> **Purpose:** add a domain vertical for the one kind of work the red/green unit test cannot govern — a component whose output is generated, probabilistic, and only *statistically* correct.
> **Produces:** a frozen eval contract — the AI analog of the red suite — and a task-kind `ai` whose verify gate reads a score, not a green light.
> **Mirrors:** UDD (the design vertical) exactly. Silent when absent; additive when present.

---

## Why a generative component breaks the green/red unit test

Every step before this chapter rests on a binary: a test is red or green, against *one* input, *deterministically*. `transfer(a, b, 30)` either returns `200` and moves the money or it does not. Run it twice, get the same answer twice. That determinism is the whole reason a frozen red suite can be an independent standard the build must rise to meet ([Step 4](./06-step-4-tests.md)).

An open-ended generative component — a summarizer, a classifier over natural language, a RAG answerer, an agent — has none of that. Ask it the same question twice and the wording differs. There is no single golden string to assert against; "correct" is not a property of one output but a *statistical property of the model's behavior over a held-out distribution of inputs*. A unit test pinned to one input/one output is either too brittle (it fails on a paraphrase that is perfectly correct) or vacuous (it asserts the one canned case the build memorized). Neither is evidence.

So the AI vertical does not abandon ADD's discipline — it relocates it. The thing you freeze before the build is no longer a list of `assert` lines; it is an **eval set + a rubric + a threshold**. "Red" stops meaning *the suite throws* and starts meaning *the measured score is below the frozen threshold*. The rule is identical to TDD's: you never edit the frozen eval set to make a build pass, and you never lower the threshold to clear the gate. That is **evaluation-driven development (EDD)** — red→green TDD's analog for work whose correctness is a measured distribution, not a boolean. Everything in this chapter is that one substitution worked through.

A green unit suite is still *necessary* for an `ai` task — the plumbing around the model must work — but it is no longer *sufficient*. The verify gate ([Chapter 19](./19-ai-verify-and-observe.md)) reads the eval score.

## `AI-SPEC.md` — the human-owned binding entry doc

The vertical has one prose binding entry doc, and it is human-owned. `AI-SPEC.md` is to an AI feature exactly what `DESIGN.md` is to a UI feature: a short binding document that states intent the engine must never invent for you. The engine measures recorded scores; it never decides what "good" means or where the bar sits. That decision is the human's, and it lives here.

`AI-SPEC.md` carries five required sections:

- **Success metric.** The top-line quality metric tied to a real business impact — not "accuracy" in the abstract but the one number whose movement would change a decision. This is the thing the eval gate ultimately defends.
- **Criteria — the four buckets.** Every AI feature is scored across four kinds of quality, and each must be named with the rubric criterion that scores it:
  - *capability* — can it do the task at all (correctness, coverage)?
  - *generation faithfulness* — is the output grounded and non-hallucinated (especially for RAG)?
  - *instruction following* — does it obey the format, constraints, and refusals it was told to?
  - *cost + latency* — is it affordable and fast enough to ship? These are quality dimensions, not afterthoughts.
- **Method ladder.** The chosen rung of prompt → RAG → finetune, with the cheaper rungs shown exhausted (below).
- **Budget.** The latency envelope (p50/p90/p99) and the cost-per-request ceiling, stated as *acceptance constraints* — a build that is accurate but over budget fails verify.
- **Safety floor.** The guardrail classes the feature must hold: prompt-injection (including indirect injection through retrieved content), PII, toxicity, jailbreak. A finding in any of these is a `HARD-STOP`, never a waiver — it merges into ADD's existing security-is-always-a-`HARD-STOP` rule ([Step 6](./08-step-6-verify.md)).

Like every entry in `SETUP_FILES`, `AI-SPEC.md` is scaffolded at init *skip-not-clobber* — created if absent, never overwritten — and it is frozen as part of the one specification bundle at the contract phase, under the single human approval ([the flow](./02-the-flow.md)). It points downward at the named set the validators lint.

## The `.add/ai/` named set at a glance

Under `.add/ai/` sits a fixed, named set of artifacts — the EDD analog of UDD's `.add/design/` set. Each has one job:

| File | What it is |
|------|------------|
| `eval-set.jsonl` | The frozen, held-out evaluation set — the AI analog of the red suite. One case per line, with a disjoint train/val/test split. |
| `rubric.json` | The scored acceptance rubric — how each of the four buckets is measured, with a pass threshold per criterion. |
| `eval-spec.json` | The reproducible run config and the pre-registered gate: primary metric + threshold + baseline-to-beat + the pinned, bias-mitigated judge + the eval-set content hash. |
| `io-contract.json` | The pinned I/O boundary: model id(s), request/response schema, guardrails, idempotency/retry, the latency+cost envelope. |
| `fallback.md` | The required per-failure-mode safe state — what the system does on timeout, error, low confidence, schema-invalid output, or a tripped guardrail. |
| `monitor.json` | The Observe-phase online-eval + drift artifact: the live signals to watch against the frozen offline score. |

The next chapter takes each of these apart in detail; here the point is only their shape and their *collective* role: together they pin what "good" means tightly enough that a build can run autonomously against them and a gate can read a single outcome off them.

## Silent when absent, additive when present

The single most important property of this vertical is the one it inherits from UDD: it is **silent when absent**. A project with no `AI-SPEC.md` and no `.add/ai/` directory sees *zero* new behavior — not a warning, not a skipped check, nothing. Every AI validator returns an empty list the moment it finds no `.add/ai/` set to lint, exactly as the UDD checks return empty without `.add/design/`. The composer is pure, read-only, and fail-closed: a malformed JSON file yields a single named code (`malformed_eval_set` and its siblings), never a crash and never a silent pass.

This is what makes the vertical safe to ship into every project at once. A backend service with no model in it is unaffected. The day someone adds an AI feature — writes `AI-SPEC.md`, drops in `.add/ai/eval-set.jsonl` — the vertical wakes up and the checks begin to bite. Nothing is opt-in by flag; presence of the artifacts *is* the opt-in. Deleting them turns the whole vertical inert again. Additive, not invasive — the same contract UDD already keeps.

## Freeze the eval before the build

[Step 4](./06-step-4-tests.md) has one non-negotiable: never start the build until the tests are red. EDD keeps that rule verbatim, with the eval contract standing in for the red suite. A task-kind `ai` **cannot enter build** until four things are present and frozen inside the specification bundle:

1. `AI-SPEC.md` with all required sections,
2. a non-empty, parseable `eval-set.jsonl` (the freeze precondition — the analog of "the suite is red"),
3. `rubric.json` covering all four buckets with thresholds, and
4. `eval-spec.json` with a primary metric, a pass threshold, a baseline-to-beat, and a disjoint split.

No frozen eval set and rubric means the build is *refused* — the validator goes red with `missing_eval_set`. This is the same logic as the must-fail principle: an eval contract written *after* the model is built is unconsciously shaped to whatever the model happens to do, including its mistakes. Written first, from intent, it is an independent standard the model must rise to meet.

And because it is frozen, it is protected. The frozen test-partition rows and the declared thresholds are content-hashed into ADD's existing tamper tripwire at the tests→build snapshot — the same md5 mechanism that catches an edited unit test or an edited contract ([Step 6](./08-step-6-verify.md)). Lowering a threshold after the freeze, mutating a frozen test-split row, or swapping in a more lenient judge trips `build_tampered` as a `HARD-STOP`. Like a weakened test or an edited frozen contract, it is **never launderable through `RISK-ACCEPTED`** — it is a change request back to Specify, not a build fix. Weakening the eval to clear the gate is, definitionally, no longer measuring the thing you froze.

## The prompt → RAG → finetune ladder

EDD has a default architecture rule the way ADD has a default flow: **reach for the cheapest adaptation that works, and earn every escalation.** The ladder has three rungs, cheapest first:

- **prompt** — instructions, examples, and structure on a base model. Fastest to build, cheapest to run, easiest to change.
- **RAG** — retrieval-augmented generation: ground the model in retrieved context so it answers from your data, not its memory.
- **finetune** — train the model's weights on your task. Most expensive to build, slowest to change, hardest to roll back.

`AI-SPEC.md` records the chosen rung *with the cheaper rungs shown exhausted*. A finetune chosen without first proving prompting and RAG insufficient is a flagged decision — the single human bundle-approval must explicitly sign it, exactly as it signs any other escalation in the spec. The point is not that finetuning is wrong; it is that an unearned escalation buys cost, latency, and lock-in you did not have to pay, and the spec is where that trade is made visible and approved rather than slipped in during the build.

## Task-kind `ai` — what changes and what stays the same

You opt a task into the vertical at creation: `add.py new-task <slug> --kind ai`. From there, most of ADD is unchanged. The seven phases keep their names, their order, and their owners — Specify and Scenarios stay human-led, the contract freeze stays the one approval, Build stays AI-led. The `ai` kind changes exactly two things and adds the artifacts above:

- **Verify gates on the eval score, not a green unit suite.** Under the eval-gated verify ([Chapter 19](./19-ai-verify-and-observe.md)), a `PASS` requires *measured-score ≥ frozen threshold* **and** *> baseline* **and** *lineage recorded* (eval-set hash + model/data version). A below-threshold score returns to Build — never lower the threshold, never trim the eval set. A green unit suite is necessary but not sufficient.
- **Observe adds an online-eval / drift beat.** The Observe phase re-runs a sample of the eval set against production, classifies drift, and records the offline-vs-online delta — so a silent regression in a probabilistic system is forbidden the way it always has been for deterministic ones.

Everything else — the grounding map, the backward-correction rule, the never-skip-forward rule, the one frozen approval, security as `HARD-STOP` — applies to an `ai` task exactly as written. The vertical does not fork the method; it teaches the method to measure a distribution where it used to read a boolean.

## Exit check

- [ ] The feature is created as `--kind ai`, and `AI-SPEC.md` exists with all five required sections (success metric · four-bucket criteria · method ladder · budget · safety floor).
- [ ] The chosen ladder rung is recorded with the cheaper rungs shown exhausted; any finetune escalation is flagged for the bundle approval.
- [ ] The `.add/ai/` named set is present: a non-empty, parseable `eval-set.jsonl`, a four-bucket `rubric.json` with thresholds, an `eval-spec.json` with metric + threshold + baseline + disjoint split.
- [ ] The eval contract is frozen inside the one specification bundle, and its frozen test rows + thresholds are hashed into the tamper tripwire.
- [ ] In a non-AI project, none of the above exists and no AI validator fires.

## If the check fails

A missing or empty `eval-set.jsonl` on a build-bound `ai` task is the AI analog of a green suite before the build — the build is refused (`missing_eval_set` / `empty_eval_set`) until a real held-out distribution exists to score against. A threshold lowered or a frozen row mutated after the freeze is not a fix; it is `build_tampered`, a `HARD-STOP` that routes back to Specify. The next chapter is the validator-by-validator account of how each of these is caught.
