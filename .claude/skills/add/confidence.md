# Confidence — the self-score that aims attention

The **confidence self-score** is an *advisory* check an agent runs on its own drafted artifact — a spec, a contract, a build, or a subagent verdict — *before* presenting it. It sharpens the draft and aims the reader's eye at the soft spots; it is never a gate.

## The six dimensions

Score each 0–1 honestly on the artifact you are about to hand over:

- **Completeness** — did it cover every rule, scenario, and rejection the task asked for?
- **Clarity** — would the next reader understand it without you in the room?
- **Practicality** — is it feasible and implementable as written, against the real code?
- **Optimization** — does it balance correctness, simplicity, and cost — no gold-plating, no corner cut?
- **Edge cases** — did it name the failure modes, the concurrency, the empty/oversized inputs?
- **Self-evaluation** — does it carry its own refine step — a way to catch its own mistakes?

If **any** dimension scores **< 0.9**, refine the artifact before presenting, then re-score.

## Where it plugs in

- It **feeds the lowest-confidence flag** (run.md · 1-specify.md): the lowest-scoring dimension is what you surface ⚠-first at the contract freeze.
- A persistently low score on a risky scope is a signal to **recommend** lowering the autonomy level (auto → conservative / manual; run.md). Recommend it — the autonomy level stays the human's call.

## The hard rule — advisory, never a gate

<constraints>
The confidence self-score is advisory only — never a gate. It never:
- auto-pass a verify or block a run — the verify outcome rests on evidence (passing tests, the non-functional review), not a self-assigned number;
- substitutes for evidence or for the human decision point;
- is recorded as a score the human "agreed to" — a self-asserted score that gated would only move an unread approval one level up (run.md).

What it MAY do: aim the lowest-confidence flag, trigger a refine pass, and recommend an autonomy adjustment. The gate itself stays evidence-based and human-owned.
</constraints>
