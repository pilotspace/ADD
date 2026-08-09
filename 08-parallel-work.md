# 08 · Parallel work — waves and worktrees

[← 07 Setup and the three lanes](./07-setup-and-lanes.md) · [Contents](./README.md) · Next: [09 Governance →](./09-governance.md)

---

## Parallel streams (opt-in)

The default is one task at a time. But when a milestone's frontier is **several tasks that do not depend on each other**, you can build them **concurrently** — one builder per ready task, each behind its own frozen contract, each isolated in its own git worktree. This is opt-in and additive: a milestone that never fans out behaves exactly as the three-beat loop already does.

The engine stays a **NO-EXEC notary**. It does not spawn builders and it does not run the method. It does exactly two things for a wave — it **plans** the wave (and proves the plan is safe) and it **joins** the results (losslessly). You create the worktrees and spawn the builders; the engine records.

**Be honest about the gain.** With one human reviewer you cannot beat `review_time × N_tasks`; the human-led decision points are serial. So the win is **not N× throughput** — it is that the reviewer is *never blocked waiting on a build*. While a person reviews task A's frozen contract, the builds for B, C, and D run behind *their* frozen contracts. You hide build latency under human-review latency; do not promise more.

## Plan the wave — the engine proves it is safe

```bash
add wave <milestone>                    # derive the DAG schedule: topological levels,
                                        #   each a set of mutually-independent tasks
add wave <milestone> --streams a,b,c    # record ONE level as the active wave
```

A level is a set the engine has **proven** safe to run at once. It refuses an unsafe wave, so you never fan out into a race:

- **R:CYCLE** — a dependency cycle among the tasks; no parallel plan exists on a cyclic graph.
- **R:INTRADEP** — two streams with a dependency path between them; they must sequence *across* waves, not within one.
- **R:OVERLAP** — two streams whose `scope:` shares a file; disjoint scope is the write-safety invariant, so a shared file is refused.

Recording a wave writes the active level down — the engine tracks which tasks are building together, so a stale plan cannot be joined by accident.

**Streams can be persona-assigned.** A wave pick may carry a lens as `slug:persona`, assigning that stream to a seeded [persona](./10-personas.md):

```bash
add wave <milestone> --streams payments:backend-systems,checkout-ui:frontend-ux
```

The engine checks the lens is a real Persona node in the bundle (else `R:BADPERSONA` — seed it first). A persona is a lens on the work, never a lowered floor: it never buys back a gate, and **security stays HARD-STOP** whatever persona wears the stream.

## Isolate and build — one worktree per stream

Give each stream its own `git worktree` on its own branch, forked from the join point, each carrying its own `.add/`. Because the wave *guaranteed* disjoint scope, the streams only ever touch different files — so the build phase **cannot race**; the only reconciliation is the join.

Inside its worktree, each stream runs its **own full three-beat loop**: direction is already frozen, so it builds to green and records its own verdict — `add gate <slug>` **in its worktree**. A stream that hits a security finding or an unmet Must gates **HARD-STOP** there, and does not merge.

## Join — fold the worktrees back, PASS-only

```bash
add join <stream-1>/.add <stream-2>/.add …    # one bundle path per worktree
```

`join` reconciles by the bundle format's own invariants:

- **PASS-only** — a HARD-STOP stream is structurally un-mergeable; no union or flag softens it.
- **Task nodes copied byte-for-byte** — disjoint scope made this lossless.
- **Spec deltas union-merged** — every stream's lessons land; a same-lesson / different-disposition divergence is **FLAGGED** for you, never silently double-kept.
- **The graph is regenerated**, never copied — it is a rebuildable cache, so the joined bundle recomputes it.

**Rollback is just dropping a worktree.** Join leaves every other stream byte-intact, so a bad stream is discarded without touching its siblings.

## Design for failure (required)

Concurrency multiplies the ways a run can go wrong, so the wave is built to fail safely:

- **Worktree isolation** — a builder owns only its own worktree and its own `.add/`; two concurrent builds physically cannot collide, because the wave proved their scopes disjoint.
- **Lease + timeout** — lease each stream to its builder with a timeout; if a builder dies, release the claim rather than trusting partial work. A builder that stops-and-escalates blocks only its own stream; siblings keep running.
- **Serial join + integration verify** — bring worktrees back **one at a time** and run an integration verify for the concurrency and architecture conflicts that two-green-in-isolation tasks can still produce. The notary never auto-passes that step.
- **Circuit-break to sequential** — if several streams fail in one wave, trip the breaker and fall back to one task at a time. Repeated failure means the scope was wrong, not that you need more parallelism.

## The floors hold for N builders exactly as for one

- **No stream owns a gate.** Each stream gates its own task in its worktree; join only **records** the outcome — it never manufactures a PASS. You (or the human) still own the milestone-level decision.
- **security = HARD-STOP** — per stream and at the join. A HARD-STOP stream can never be merged.
- **High-risk still escalates** to the human — a wave is a scheduling tool, not a lowered floor.
- **Each stream stays inside its `scope:`** and never edits a frozen `gives:`; the wave's disjoint-scope refusal is what makes that mechanical rather than merely asked-for.

The full builder contract and the per-runner spawn adapter live in the skill's `streams.md`; this chapter is the *why* and the safety frame, not the operational recipe. The engine plans and joins; you build; the floors never move.
