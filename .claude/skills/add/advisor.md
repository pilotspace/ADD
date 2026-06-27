# Advisor — spawning one subagent to follow your plan

The **advisor** strategy is for the orchestrating agent: spawn a *single* subagent to execute
one piece of your plan, then merge its verdict back in. It is the single-subagent companion to
`streams.md` — streams pipelines *many* independent tasks in parallel worktrees; the advisor
delegates *one* well-scoped piece (a sweep, a review, a batch) while you stay in the loop. The
engine never spawns; this is your judgment to make per step.

## When to spawn — and when not

Spawn a subagent when the piece is **separable and worth the round-trip**:

- **Broad / expensive sweep** — gather a wide map cheaply, return a compact result.
- **Independent adversarial review** — a fresh context argues *against* your result (the
  `6-verify` earned-green refute-read), so the check is not graded by the author.
- **A well-scoped delegable batch** — a self-contained slice with a clear contract and return shape.
- **Context offload** — work that would bloat your context but compresses to a small verdict.

Do **not** spawn when the work is narrow and cheap enough to do in-context: a small sweep, a
two-file read, a quick edit. A spawn costs a round-trip — pay it only when the piece is big or
independent enough to earn it. When in doubt, do it in-context.

## The plan-following prompt template

Give the subagent the *piece of your plan it owns* and a fixed return shape. This reuses
`streams.md`'s worker-contract tags for a single advisory subagent — the contract is identical
on any runner; only the spawn adapter (see `streams.md`) changes. The `<strategy>` block mirrors the task's §5 (Strategy + Known-problem fixes) as the subagent's PREFERRED path — it self-improves on that plan and reports the strategy it actually used.

```xml
<objective>
Execute THIS piece of the orchestrator's plan: {{PIECE}}. You own only this piece — not the
surrounding decisions. Return a verdict; do not record state.
</objective>

<persona>
You are a {{DOMAIN}} engineer. Correctness over speed; a wrong-but-plausible result is expensive.
Work step by step, following the plan:
1. Load the context files; confirm you understand the piece you own.
2. Do the work in small steps, honoring the orchestrator's plan and constraints.
3. Self-score your result with confidence.md; if any dimension < 0.9, refine before returning.
</persona>

<strategy>
The task's §5 plan — the Strategy (ordered batches) order and the Known-problem fixes — is
your PREFERRED starting path, not a hard rule. Improve on it when a better strategy emerges
as you build; on done, report the strategy you ACTUALLY used so the orchestrator can update
§5 for the audit trail.
</strategy>

<context_files>
the plan / task files the piece needs (read-only unless the piece says otherwise)
</context_files>

<return>
End with a structured verdict the orchestrator parses and RECORDS:
{ piece, result, evidence, confidence: {per-dimension 0–1}, open_questions }.
Do NOT run add.py or write any shared state — you propose, the orchestrator records.
</return>
```

## Choosing the model — vendor-neutral tiers

Pick the tier from `streams.md`'s vocabulary: **mid** for an ordinary, well-scoped piece; **top**
for a complex, ambiguous, or cross-cutting one. The tier→model-id mapping and the spawn adapter
live there — one home, not repeated here. A stronger model never buys back a human gate: high-risk
scope still escalates.

## The hard rule — you delegate, you do not abdicate

<constraints>
The engine never spawns — spawning is the orchestrating agent's choice (tool-agnostic). And:
- the subagent PROPOSES; the orchestrator RECORDS — a worker never runs add.py or writes shared
  state (state.json, MILESTONE.md, a sibling's files): you read its verdict and record the outcome;
- delegation never lowers a gate — a SECURITY finding still HARD-STOPs, and high-risk scope still
  escalates to the human, whoever (or whatever tier) did the work;
- the spawned subagent returns its confidence.md self-score; a low score is a signal to refine or
  re-spawn, never a pass.
</constraints>

> Used per step: each phase guide's Advisor hook points here, so an agent spawns in the idiom of
> the phase it is in (see the per-step hooks).
