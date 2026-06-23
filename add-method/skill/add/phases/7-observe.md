# Phase 7 — Observe (feed the next loop)

Goal: release deliberately, watch reality, and turn what you learn into the next spec. Fill **§7** in TASK.md.

## Do

1. **Release behind a scope-of-impact limit** — feature flag and/or gradual rollout.
2. **Reuse scenarios as monitors** — the §2 scenarios that defined "correct" now
   define what you alert on: overall error rate, each rejection's rate (a spike in
   one is a signal), latency of the risky operation under load.
3. **Draft the next spec delta** — every defect, surprise, or new need becomes a
   concrete change that re-enters the flow at Specify (a new task).
4. **Propose a voice delta** — you just worked a whole task alongside the human, so
   notice where your voice diverged from theirs (their wordings + flow) and propose a
   confirmable **voice delta** that tunes `SOUL.md`. Emit it `open`; the human confirms;
   only then do you rewrite the routed SOUL.md section. Read `soul.md` for the grammar,
   the routing, and the human-is-only-writer rule.

## AI prompt

<prompt>
Role: a reliability analyst feeding the next cycle.
Read first: telemetry · objectives · incidents.
Objective: turn what production shows into the next SPEC delta.
Steps:
  1. Report error-budget burn.
  2. Cluster errors and surface the top real-world failures.
  3. Draft a SPEC delta with evidence links.
Never: auto-roll-back — recommend; a human owns the production decision.
</prompt>

## Exit gate

<exit_gate>
- [ ] Released behind a flag/rollout.
- [ ] Scenario-based monitors live.
- [ ] A reviewed spec delta captured (becomes the next `new-task`).
</exit_gate>

> **Advisor · Confidence** — spawn a reviewer to mine the run for lessons (advisor.md); score Self-evaluation — did this loop teach the foundation? (confidence.md).

## Next

Loop. The artifacts you built are living documents the next cycle refines.
Book: `docs/09-the-loop.md`.
