# Phase 7 — Observe (feed the next loop)

Goal: release deliberately, watch reality, turn what you learn into the next spec. Fill **§7** in TASK.md.

## Do

1. **Release behind a scope-of-impact limit** — a flag and/or gradual rollout
2. **Reuse scenarios as monitors** — the §2 scenarios that defined "correct" now
   define what you alert on: overall error rate, each rejection's rate (a spike is a
   signal), latency of the risky op.
3. **Draft the next spec delta** — every defect, surprise, or new need becomes a
   change that re-enters the flow at Specify (a new task).
4. **Propose a voice delta** — note where your voice diverged from the human's (wordings +
   flow); propose a confirmable **voice delta** tuning `SOUL.md`, emitted `open`. The human
   confirms, then you rewrite the routed section. Read `soul.md` (grammar, routing,
   human-is-only-writer).

> **Decisions (ADR)** — at the gate the engine harvests §7's ADR block (§1/§3/§5/§6); `add.py audit` flags one never harvested.

## AI prompt

<prompt>
Role: a reliability analyst feeding the next cycle.
Read first: telemetry · objectives · incidents.
Steps: 1. report error-budget burn · 2. cluster errors, surface the top real failures ·
  3. draft a SPEC delta with evidence links.
Never: auto-roll-back — recommend; a human owns the production decision.
</prompt>

## Exit gate

<exit_gate>
- [ ] Released behind a flag/rollout.
- [ ] Scenario-based monitors live.
- [ ] A reviewed spec delta captured (becomes the next `new-task`).
</exit_gate>

> **Persona** — tag `· persona:<slug> · critical-rule|success-metric|anti-pattern|ability`;
> `fold` grows that section — a HOW-an-agent-behaves lesson belongs in a persona, not the shared pile.
> **Advisor · Confidence** — spawn a reviewer to mine the run for lessons (advisor.md); score Self-evaluation — did this loop teach the foundation? (confidence.md).

## Next

Loop — the artifacts are living docs the next cycle refines.
Map: `self-improve.md` · book: `docs/09-the-loop.md`
