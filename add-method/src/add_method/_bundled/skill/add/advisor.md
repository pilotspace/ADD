# Advisor — spawning one subagent to follow your plan

The **advisor** strategy: spawn a *single* subagent for one piece of your plan, then merge its
verdict back — the single-subagent companion to `streams.md` (which pipelines *many*). The engine
never spawns; this is your call per step.

## When to spawn — and when not

Spawn when the piece is **separable and worth the round-trip** — a broad sweep, an independent adversarial review (the `6-verify` refute-read, fresh context not graded by the author), a well-scoped batch. Not for narrow, cheap work; when in doubt, do it in-context.

## The 3-lens sequential checklist at verify

At Verify, sweep security → concurrency → architecture in order. **Security HARD-STOP ends the checklist** (leave the rest blank). Each lens returns: **CLEAR** · **HARD-STOP** (security only) · **RESIDUE** (concurrency/architecture).

Record in §6 `### Advisor 3-lens verdict`: **Verdict** (PASS/HARD-STOP) · **Residue** (none/brief) · **Binding** (`yes` for `sensitivity: mechanical` — engine reads it for `advisor-gate-relax`; else `advisory`).

**Persona for the refute-read** — select a **Code-Reviewer** persona (🔴 blocker · 🟡 concern · 💭 note); advisory, never lowers a gate (security still HARD-STOPs).

## The plan-following prompt template

Give the subagent the *piece it owns* and a fixed return shape — `streams.md`'s worker-contract
tags, identical on any runner; only the spawn adapter changes. The `<strategy>` block mirrors §5 as
the PREFERRED path — it self-improves on that plan and reports the strategy it actually used.

```xml
<objective>
Execute THIS piece of the orchestrator's plan: {{PIECE}}. You own only this piece — not the
surrounding decisions. Return a verdict; do not record state.
</objective>

<persona>
SELECT the best-fit project persona for this piece and load `.add/personas/{{PERSONA_SLUG}}.md` —
Identity→your stance · Critical Rules→constraints · Success Metrics→done-bar (streams.md's worker
contract). No match → a {{DOMAIN}} engineer, correctness over speed; never blocks.
Work step by step: load the context + persona and confirm the piece you own; do the work in small
steps honoring the plan and constraints; self-score with confidence.md, refining if any dimension < 0.9.
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
{ piece, persona, result, evidence, confidence: {per-dimension 0–1}, open_questions }.
`persona` names the slug you adopted (or `generic`) — the orchestrator records which persona did the work.
Do NOT run add.py or write any shared state — you propose, the orchestrator records.
</return>
```

## The phase-specialist roster

As a Claude Code plugin, ADD ships `agents/` — one registered subagent per phase, each its
phase-guide role wrapped in the contract above: `add-setup · add-ground · add-specify ·
add-scenarios · add-contract · add-tests · add-build · add-verify · add-observe`. Spawn the
phase's own (plugin `Task(subagent_type="add:add-<phase>")`; a `.claude/agents/` copy → bare
`add-<phase>`); no roster → `Task(prompt=<rendered PROMPT.persona.md>)` still works on any runner.
Other runners reuse the same contract via the portable body + adapters (`streams.md`).

## Choosing the model — vendor-neutral tiers

Pick the tier from `streams.md`: **mid** for an ordinary piece, **top** for a complex one. The
mapping + spawn adapter live there; a stronger model never buys back a gate — high-risk scope still escalates.

## The hard rule — delegate, don't abdicate

<constraints>
The engine never spawns — it's the orchestrating agent's choice. And:
- the subagent PROPOSES; the orchestrator RECORDS — a worker never runs add.py or writes shared state;
- delegation never lowers a gate — a SECURITY finding still HARD-STOPs, high-risk scope still escalates;
- the subagent returns its confidence.md self-score; low → refine or re-spawn, never a pass.
</constraints>

> Used per step: each phase guide's Advisor hook points here (the per-step hooks).
