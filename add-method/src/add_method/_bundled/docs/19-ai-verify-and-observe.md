# 19 · Guardrails, Reliability & Observability — Eval-Gated Verify and the Online-Eval / Drift Loop

[← 18 The eval contract and its validators](./18-ai-eval-contract-and-validators.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)

---

[Chapter 17](./17-ai-driven-the-ai-vertical.md) introduced the AI vertical and why an open-ended
generative component breaks the green/red unit test. [Chapter 18](./18-ai-eval-contract-and-validators.md)
froze what *good* means — the held-out eval set, the four-bucket rubric, the pinned judge, the I/O
contract — and lit the validators that keep that contract honest. This chapter is where the frozen
contract finally pays out: the **verify gate** that reads a measured score instead of a green suite,
the **guardrails** that merge into ADD's security rule as `HARD-STOP`s, the **cost and latency budget**
that fails an over-budget build even when its quality passes, the **graceful-degradation** path that
gives a probabilistic system a safe state, and the **Observe step** that re-runs the eval against
production and turns drift into the next spec.

The same shape governs all of it. [Chapter 08 · Verify](./08-step-6-verify.md) established that trust
is built *through evidence, not inspection*, and that a security finding is always a `HARD-STOP` that is
never auto-passed. The AI vertical does not invent a second philosophy; it specializes the one already
there. For a `kind: ai` task the evidence is a *score over a held-out distribution* rather than a count
of passing assertions — but the rule that the evidence must be sufficient, recorded, and signed is
unchanged, and the rule that security is un-waivable is unchanged.

## 19.1 · The eval-gated verify — a score, not a green suite

For an ordinary task, [Step 6](./08-step-6-verify.md) confirms the evidence (tests green, coverage not
decreased, nothing weakened) and then checks what tests miss. For a `kind: ai` task the *evidence
itself* changes shape. A green unit suite is **necessary but not sufficient** — the runner can be green
while the model is worse than a coin flip, because the suite proves the pipeline executes, not that the
output is *good*. So the verify auto-PASS condition is rerouted: it reads `eval-spec.json` and passes
only when **all three** hold:

- **Score ≥ the frozen threshold.** The measured score on the held-out test split clears the bar
  `eval-spec.json` declared at the contract freeze — the AI analog of "all tests pass."
- **Score > the baseline.** The model beats the declared baseline-to-beat (majority / random /
  heuristic / human / prior model). A threshold a majority-class predictor already clears is not
  evidence of skill; the gate refuses to mistake a high absolute number for a real gain.
- **Lineage recorded.** The eval-set content hash plus the model and data versions are written down
  (`MODEL_REGISTRY.md`, the `## AI evals` section), so the recorded score is *rebuildable* — anyone can
  re-run the same pinned judge against the same frozen rows and reproduce the number.

This mirrors the auto-PASS evidence rule of [Step 6](./08-step-6-verify.md) exactly. There, an `auto`
run signs `PASS` only when every test is green, coverage holds, nothing was weakened, and there is no
residue. Here, an `auto` run signs `PASS` only when the score clears the threshold, beats the baseline,
and the lineage is written — *and* the ordinary non-functional review (concurrency, security,
architecture, the deep check, the earned-green refute-read) still runs underneath. The AI gate is an
**overlay**, not a replacement: it adds the score condition on top of the verify checks every task
carries.

> **Do:** read the score off `eval-spec.json` and require threshold ∧ baseline-gain ∧ lineage.
> **Don't:** sign `PASS` because the eval *runner* exited zero. A green runner against an unmeasured or
> below-baseline score is the AI form of shipping on plausibility.

And the variance rule from [Chapter 18](./18-ai-eval-contract-and-validators.md) is load-bearing right
here: a judge-scored dimension runs over **≥ 2 samples** at `temperature: 0` with a fixed seed, and the
gate reads the reported variance, not a single sample. The same input scores differently across runs;
a one-sample score is non-evidence, the way a test that passes only on Tuesdays is non-evidence.

## 19.2 · Below threshold returns to Build — never weaken the eval

A below-threshold score does exactly what a failing test does: it **returns the task to Build**. The
`below_threshold` outcome is the AI analog of a red suite — the build is not done, because the bar it
was given is not met.

The tempting cheat is the one the whole method exists to refuse. Faced with a score one point under the
bar, the path of least resistance is to *lower the bar*, trim the awkward rows out of the test split, or
swap the strict judge for a lenient one. Each of those is the AI form of weakening a test or editing a
frozen contract, and each is caught mechanically. The frozen test rows and thresholds were md5-snapshotted
into the **same tamper tripwire** that guards the red suite and the frozen §3 contract ([Step 6](./08-step-6-verify.md)'s
floor). The frozen test rows, rubric, and thresholds are frozen into the tamper tripwire; mutating a
frozen test row, or changing the metric or threshold after the freeze, is a post-freeze edit that trips
`build_tampered` as a `HARD-STOP` — and that stop is **never launderable through `RISK-ACCEPTED`**,
exactly as the contract-tamper stop never is.

This is the never-weaken-the-eval discipline, and it is the AI vertical's single most important
inheritance. In ADD you do not move the goalposts to score; you return to Build and earn the score
honestly, or you take the gap back to Specify as a change request and let a human re-decide the bar in
the open. There is no third door.

| Situation at verify | Outcome | Where it goes |
|---|---|---|
| Score ≥ threshold ∧ > baseline ∧ lineage recorded | `PASS` | forward to Observe |
| Score < threshold, or no baseline gain | `below_threshold` | back to **Build** (earn it honestly) |
| Threshold lowered / test row mutated / judge swapped lenient | `build_tampered` (`HARD-STOP`) | un-waivable; back to Specify as a change request |
| A non-safety quality shortfall the human accepts knowingly | `RISK-ACCEPTED` | ship with a signed, expiring waiver |
| Any safety / guardrail finding | `HARD-STOP` | never auto-passed, never waived |

## 19.3 · Guardrails are HARD-STOPs — the AI security classes

[Chapter 08](./08-step-6-verify.md) made one rule absolute: a security finding is always a `HARD-STOP`,
never auto-passed, never waved through with a waiver. The AI vertical adds the security classes that are
specific to a probabilistic, prompt-driven system, and **merges them into that same rule** rather than
inventing a softer one. A safety or guardrail finding at the AI verify gate is a `HARD-STOP` of exactly
the same un-waivable kind as a hardcoded secret or an injection opening.

The guardrail classes the gate must escalate:

- **Prompt injection.** A user input that overrides the system instruction — "ignore your rules and …".
  A model that can be talked out of its constraints by its own input is a security defect, not a quality
  one.
- **Indirect (retrieved-content) injection.** The RAG-specific form: the malicious instruction arrives
  inside a *retrieved chunk*, not the user's message. The system trusted a document it fetched and let
  it steer behavior. This is the injection class that catches teams off guard, because the attack
  surface is the corpus, not the prompt.
- **PII leakage to an external boundary.** The model emits — or forwards to an external API or judge —
  personal data that must not cross that boundary. A PII leak to a third party is a `HARD-STOP`; the
  eval set must include cases that *try* to make it happen, and the I/O-boundary guardrail must catch
  them before they propagate.
- **Jailbreak.** A crafted input that defeats the safety layer and elicits a response the policy forbids.
- **Toxicity / unsafe action.** Output that is harmful, or — for an agent — a *tool call* that takes an
  unsafe real-world action (a destructive command, an unauthorized spend, an irreversible write).

Two properties make these un-cheatable. First, the guardrail classes named in `AI-SPEC.md`'s **safety
floor** and `io-contract.json`'s **`guardrails`** list are not decorative — a guardrail declared in the
contract with *no wired fallback path* in `fallback.md` is itself a red `guardrail_without_fallback`
finding (see §19.5), so a guardrail cannot be claimed and then left unhandled. Second, a safety eval
finding is **never auto-passed and never `RISK-ACCEPTED`** — the same line the method draws for every
security finding. A model can score brilliantly on capability and still fail here, and the safety failure
governs: an over-the-bar quality score does not buy its way past a jailbreak.

> **Do:** put adversarial cases — injection, indirect injection, PII-bait, jailbreak prompts — *in the
> frozen eval set*, so the gate measures safety, not just capability.
> **Don't:** treat a safety finding as a quality gap a waiver can cover. It is a `HARD-STOP`, the same
> as a leaked credential.

## 19.4 · Cost and latency are first-class gates

Quality is not the only acceptance constraint. A correct answer that costs ten cents and arrives in
twelve seconds can be a *product failure* even though every quality criterion passed. So cost and latency
are **first-class gates**, not afterthoughts — declared as acceptance constraints in `AI-SPEC.md`'s
**Budget** section and pinned in `io-contract.json`, and *measured* by the same verify eval run that
scores quality.

The budget is an envelope, not a single number, because tail behavior is where probabilistic systems
hurt users:

- **Latency p50 / p90 / p99.** The median is the headline; the tail is the truth. A p50 inside budget
  with a p99 ten times over it means one user in a hundred has a broken experience — and for a streamed
  response, TTFT (time to first token) and TPOT (time per output token) are the envelope users actually
  feel.
- **Cost per request.** The per-call ceiling. An eval run that is over budget on cost fails the same way
  an over-latency run does.

The rule is sharp and worth stating on its own line: **an over-budget build fails at verify even when its
quality passes.** A model that clears the threshold, beats the baseline, and records clean lineage but
blows the p99 latency envelope or the cost-per-request ceiling does not pass — `budget_undeclared`
guarded the existence of the envelope at the freeze, and the verify run enforces it. This is the AI
analog of the architecture-conformance check in [Step 6](./08-step-6-verify.md): speed and spend are
non-functional properties tests do not catch, so the gate checks them by measurement, every time.

## 19.5 · Graceful degradation — a probabilistic system needs a safe state

A deterministic function either returns or raises, and the caller knows which. A probabilistic dependency
has a third state — *plausible and wrong* — and several more besides: it times out, it returns schema-invalid
output, it answers below its own confidence floor, it trips a guardrail. **A probabilistic system without
a declared fallback is unsafe by construction**, so the absence of `fallback.md` on a `kind: ai` task is
red (`fallback_missing`), and a fallback that leaves a required failure mode undefined is red too.

`fallback.md` declares a concrete, named safe state for **every** failure mode — never `crash`, never
`hang`:

- **Timeout** — bounded wait, then a degraded path (a cached answer, a default, a cheaper model).
- **Error / exception** — a safe response, not an unhandled stack trace reaching the user.
- **Low-confidence / below-threshold** — when the model is unsure, hand off (human-in-the-loop) or
  refuse safely rather than guess confidently.
- **Schema-invalid output** — and this is the load-bearing one: **every AI output is validated against
  `io-contract.json`'s response schema at the boundary before use, and a schema-invalid output takes the
  fallback path and never propagates.** A model that returns malformed JSON does not crash the caller and
  does not get parsed leniently into a wrong shape — it is caught at the boundary and degraded. This is the
  format-validation half of the output guardrails, and it is the anti-train/serve-skew artifact: the same
  contract validates both sides.
- **Guardrail trip** — when a safety guardrail fires, the declared safe path (hard-deny, sanitized
  response, escalation) runs. A guardrail named in `io-contract.json` with no matching wired line here is
  the `guardrail_without_fallback` red from §19.3.
- **Empty retrieval (RAG)** — when nothing relevant is retrieved, the system says so rather than
  hallucinating over an empty context.
- **Tool failure (agent)** — when a tool errors, the agent degrades rather than looping or fabricating
  the tool's result.

And one structural requirement underneath all of them: a **`## Limits` section** declaring a `timeout_ms`
and a bounded retry / circuit-breaker. An unbounded wait on a probabilistic dependency is `fallback_no_timeout`
— red. Retries must be bounded and, for any operation with side effects, idempotent (`io-contract.json`
carries the idempotency key or the explicit no-side-effect assertion); a retried non-idempotent write is
a double-spend waiting to happen. Design-for-failure here is the same discipline [16 · Releasing](./16-releasing.md)
asks of the deploy pipeline — timeouts, retries, a tested fallback — pushed down to the model boundary.

> **Do:** name a concrete safe path per failure mode, and validate every output against the response
> schema at the boundary before it is used.
> **Don't:** let a schema-invalid or low-confidence output propagate, and never leave a failure mode's
> behavior as "crash" or "hang."

## 19.6 · RAG and agent specializations

The verify gate sharpens for the two task shapes that fail in their own ways.

**RAG** has two systems that can each rot independently — retrieval and generation — so it needs two
classes of metric, and `eval-spec.json` must declare both:

- **Retrieval metrics** — context precision / recall, hit-rate, MRR. Without them retrieval rot is
  invisible: the corpus drifts, the right chunk stops being fetched, and the generator quietly answers
  from worse context. A RAG task with no retrieval metric is `rag_retrieval_uneval` — red.
- **Faithfulness / grounding** — does the generated answer stay *grounded in the retrieved context*, or
  does it confabulate beyond it? This is the anti-hallucination gate, and its absence is
  `rag_faithfulness_unchecked` — red. High answer quality with low faithfulness is a system that sounds
  right while inventing — exactly the failure RAG was supposed to prevent.

**Agents** add unbounded action, so they must be bounded and trajectory-scored. `eval-spec.json`'s
`agent` block declares `max_steps`, `max_cost`, and `max_latency_ms`, plus a tool-use / trajectory
success metric — did the agent reach the goal *and* did it take a sane path to get there? An agent with
no bounds or no trajectory metric is `agent_unbounded` — red. An agent that reaches the right answer after
forty tool calls and three dollars has not passed; the bound is part of the acceptance criterion, the
same way the latency envelope is.

## 19.7 · Observe — online eval and drift classification

A passing offline score is a snapshot of one day's distribution. Production is a moving distribution, and
the gap between the two is where models silently decay. So the **Observe step** for a `kind: ai` task
extends [09 · The loop](./09-the-loop.md)'s "scenarios become monitors" line with an **online-eval / drift**
beat: re-run a *sample of the frozen eval set against production traffic and fresh data*, per
`monitor.json`, and record the **offline-vs-online delta**.

`monitor.json` is the Observe-phase artifact. It declares the live signals to watch — and the set is not
optional shape, it is the closing of the loop:

- **Quality and safety drift** versus the frozen offline score — has the production score fallen below
  the bar the verify gate cleared?
- **Latency p50 / p90 / p99** (TTFT / TPOT) and **cost per request** — the §19.4 budget, now watched live
  rather than measured once.
- **At least one implicit user-feedback signal** — a thumbs-down, a retry, an edit of the model's
  output, an abandonment. Implicit feedback is the cheapest, highest-volume drift sensor a shipped AI
  system has, and `monitor.json` must declare ≥ 1.
- **Input-distribution and prediction-distribution** signals — so a *covariate* shift (the inputs moved)
  is distinguishable from a *concept* shift (the right answer for the same input moved).

When the online sample runs, classify what you see:

- **Covariate drift** — the input distribution moved; the model still maps correctly, but it is now
  seeing inputs the eval set under-represents. The fix is usually new eval rows.
- **Label / prior drift** — the distribution of correct answers moved.
- **Concept drift** — the *relationship* between input and correct output changed; yesterday's right
  answer is today's wrong one. This is the dangerous one, because the model can look unchanged while
  becoming wrong.

`monitor.json` also carries a **drift baseline** — `baseline_metric`, `baseline_score`, `alert_threshold`
— so there is a concrete frozen-score line to detect production drift *below*. A monitor with signals but
no drift baseline has nothing to alert against; it is `monitor_no_drift_baseline` — a WARN, a nudge to
fill the bar, not a red.

## 19.8 · The never-red nudge and closing the loop

The Observe artifact follows the UDD precedent exactly. Just as a shipped UI prototype without a capture
file raises a **never-red** `missing_capture` WARN — a nudge that rides the warnings list and never feeds
`failed` — a shipped or observe-phase `kind: ai` task with no `monitor.json` raises a never-red
**`missing_monitor`** WARN. It is the same mechanism, the same place in `add.py check`, the same
philosophy: monitoring is the right thing to do and the engine *reminds* you, but a non-AI project and an
un-monitored AI task both keep shipping — the nudge informs, it does not block. An `ai` task with no AI
vertical at all triggers zero of this; the whole thing is silent-when-absent.

And then the loop closes the way ADD's loops always close. A drift below the frozen threshold is **not**
swallowed as noise and **not** silently re-tuned. It is emitted as a **spec delta / reopen back at
Specify** — a security/integrity-class escalation, because a model that has decayed below the bar it was
accepted at is shipping a quality it never earned. **A silent regression is forbidden.** The same rule
that says you never lower the threshold at verify (§19.2) says you never let production quietly fall below
it either; both routes return through Specify — where a human re-decides in the open.

This is the data flywheel without the silent regression: production traffic flows back as fresh eval rows
and spec deltas, the eval set grows toward the real distribution, the next cycle is gated against a harder
and truer bar — and every move of that bar is a recorded, human-confirmed decision, never a quiet edit.
The Observe exit is not satisfied until a recorded online-eval / drift delta exists; the loop is not
closed until production feedback has re-entered the flow as a delta a person can read.

> **Do:** re-run a sample of the eval set against production, classify the drift, and turn a below-bar
> delta into a spec change at Specify.
> **Don't:** treat a passing offline score as permanent, or absorb production decay by quietly editing the
> bar. The most reliable evidence about an AI feature — like every feature — arrives *after* it ships.

## 19.9 · The AI verify-and-observe arc, in one line

**measure the score → gate on threshold ∧ baseline ∧ lineage → escalate any safety / budget failure →
degrade safely on every failure mode → watch production → reopen on drift.**

The eval-gated verify reads a measured score, not a green suite; below-threshold returns to Build and the
bar is never lowered; a safety or guardrail finding merges into ADD's un-waivable security `HARD-STOP`; the
cost and latency budget fails an over-budget build even when quality passes; `fallback.md` gives the
probabilistic system a safe state at every failure mode with the output validated at the boundary; and the
Observe step re-runs the eval against production, classifies drift, and reopens at Specify when the live
score falls below the bar it was accepted at. The reasoning is here; the procedure — the `ai.md` skill
loop, the `add.py check` codes, the eval-runner mechanics — lives in the skill guides
([Chapter 18](./18-ai-eval-contract-and-validators.md) maps the validators). This chapter is the *why*:
an AI feature is held to the same standard as every other — trust through evidence, security un-waivable,
the loop never silent — with the evidence taking the shape its probabilistic nature demands.

---

[← 18 The eval contract and its validators](./18-ai-eval-contract-and-validators.md) · [Contents](./README.md) · Next: [Appendix A Templates →](./appendix-a-templates.md)
