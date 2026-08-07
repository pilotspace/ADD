# 08 · Parallel work — waves and worktrees

[← 07 Setup and the three lanes](./07-setup-and-lanes.md) · [Contents](./README.md) · Next: [09 Governance →](./09-governance.md)

---

## Parallel streams (opt-in)

The default is one task at a time. But when a milestone holds several tasks whose dependencies are already `PASS` and a reviewer is ready, you may run them **concurrently** — one worker per ready task, each building behind its own frozen contract.

**Be honest about the gain.** With one human reviewer you cannot beat `review_time × N_tasks`; the human-led decision points are serial. So the win is **not throughput** — it is that the reviewer is *never blocked waiting on a build*. While a person reviews task A's specification bundle, the builds for B, C, and D run behind *their* frozen contracts. You hide build latency under human latency; do not promise more.

**Two queues, no new state** — both read from `add.py status`:

- **READY-QUEUE** — tasks in the active milestone where the phase is not `done` and every dependency already reads `gate=PASS`. These are the only tasks a worker may pick up; a task finishing `PASS` unblocks its dependents on the next `status`.
- **REVIEW-QUEUE** — the irreducibly serial part: the **bundle approval** (contract freeze) and any **Verify escalation**. One human, one queue, presented one at a time — never a batch that invites approval without reading.

**The autonomy level is the throttle** — an explicit, overridable per-task token on an ordered ladder `manual < conservative < auto`. At `manual`, the human owns every gate and nothing auto-resolves (the strict floor). At `conservative`, both gates queue on the human (pure pipelining — builds overlap, nothing auto-resolves). At `auto` (the seeded default), only the bundle-approval decision point and residue escalations queue; Verify auto-PASSes on evidence, so real concurrency follows. The floor never drops below **one human approval per task, at the contract decision point**.

**Design for failure (required).** Lease each task to its worker with a timeout — if a worker dies, release the claim back to READY rather than trusting partial work. A worker that hits a stop-and-escalate blocks only its own task; siblings keep running. And if several workers fail in one wave, trip a circuit-breaker and fall back to sequential — repeated failure means the scope was wrong, not the parallelism.

**The hard boundary.** The orchestrator owns every shared write — `state.json`, `MILESTONE.md`, and each `add.py advance`/`gate` call (always with the explicit task slug). A worker owns only its own task directory and is isolated in a git worktree — ADD's default for any agent-spawned step, not only a wave — so concurrent builds cannot collide. Merge is **serial**: bring worktrees back one at a time and run an **integration Verify** for the concurrency and architecture conflicts that two-green-in-isolation tasks can still produce — automation never auto-passes that step.

The full, agent-agnostic worker contract (the prompt a worker runs) and the per-runner spawn adapter live in the skill's `streams.md`; this section is the *why* and the safety frame, not the operational recipe.
