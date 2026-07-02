# Advisor — spawning one subagent to follow your plan

The **advisor** strategy: spawn a *single* subagent to execute one piece of your plan, then merge
its verdict back. It is the single-subagent companion to `streams.md` (which pipelines *many* tasks
in parallel worktrees) — you delegate *one* well-scoped piece and stay in the loop. The engine never
spawns; this is your call per step.

## When to spawn — and when not

Spawn when the piece is **separable and worth the round-trip**: a broad sweep; an independent adversarial review (the `6-verify` refute-read — fresh context, not graded by the author); a well-scoped batch; or context-offload to a small verdict.

Do **not** spawn for narrow, cheap work — pay the round-trip only when the piece is big or independent enough. When in doubt, do it in-context.

## The 3-lens sequential checklist at verify

At Verify, sweep security → concurrency → architecture in order. **Security HARD-STOP ends the checklist** (leave the rest blank). Each lens returns: **CLEAR** · **HARD-STOP** (security only) · **RESIDUE** (concurrency/architecture).

Record it in §6 `### Advisor 3-lens verdict`: **Verdict** (PASS/HARD-STOP) · **Residue** (none or brief) · **Binding** (`yes` for `sensitivity: mechanical` — the engine reads it for `advisor-gate-relax`; `advisory` otherwise).

**Persona for the refute-read.** When the piece is the earned-green refute-read, select a **Code-Reviewer** persona; its findings carry severity markers — 🔴 blocker · 🟡 concern · 💭 note. A persona is advisory: it never lowers a gate (a security finding still HARD-STOPs).

## The plan-following prompt template

Give the subagent the *piece it owns* and a fixed return shape. This reuses `streams.md`'s
worker-contract tags — identical on any runner; only the spawn adapter (see `streams.md`) changes.
The `<strategy>` block mirrors the task's §5 as the subagent's PREFERRED path — it self-improves on that plan and reports the strategy it actually used.

```xml
<objective>
Execute THIS piece of the orchestrator's plan: {{PIECE}}. You own only this piece — not the
surrounding decisions. Return a verdict; do not record state.
</objective>

<persona>
SELECT the best-fit project persona for this piece and load `.add/personas/{{PERSONA_SLUG}}.md` —
Identity→your stance · Critical Rules→constraints · Success Metrics→done-bar (streams.md's worker
contract). No match → a {{DOMAIN}} engineer, correctness over speed; never blocks.
Work step by step, following the plan:
1. Load the context files + the persona; confirm you understand the piece you own.
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
{ piece, persona, result, evidence, confidence: {per-dimension 0–1}, open_questions }.
`persona` names the slug you adopted (or `generic`) — the orchestrator records which persona did the work.
Do NOT run add.py or write any shared state — you propose, the orchestrator records.
</return>
```

## Choosing the model — vendor-neutral tiers

Pick the tier from `streams.md`: **mid** for an ordinary piece; **top** for a complex/ambiguous/
cross-cutting one. The tier→model-id mapping + spawn adapter live there. A stronger model never buys
back a gate: high-risk scope still escalates.

## The hard rule — delegate, don't abdicate

<constraints>
The engine never spawns — it's the orchestrating agent's choice. And:
- the subagent PROPOSES; the orchestrator RECORDS — a worker never runs add.py or writes shared state;
- delegation never lowers a gate — a SECURITY finding still HARD-STOPs and high-risk scope still escalates, whoever did the work;
- the subagent returns its confidence.md self-score; a low score means refine or re-spawn, never a pass.
</constraints>

> Used per step: each phase guide's Advisor hook points here (the per-step hooks).
