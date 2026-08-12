# 17 · Components — monorepo and multi-repo

[← 16 Releasing](./16-releasing.md) · [Contents](./README.md) · Next: [18 Personas in practice — the project-fit loop →](./18-personas.md)

---

Most of this book treats a project as one codebase with one green bar. Real
systems are rarely that tidy: a backend and a frontend, a shared library and two
apps, or three services across three repos. ADD models all of these the same
way — through the **task graph** already in the `.add/` bundle. A task owns a
`scope:` (the source subtree it may touch), its own checks, and the frozen
contracts it produces (`gives:`) or consumes (`needs:`). With that, **one milestone
can ship a vertical slice across parts** — a backend endpoint and the frontend that
calls it — instead of splitting the slice across milestones.

This is **opt-in and additive**: a project whose tasks all share one scope behaves
exactly as the rest of the book describes. You reach for the multi-part machinery
only when a milestone genuinely spans more than one green bar.

## Scope is declared, never inferred

A task's parts of the tree are **declared on the node**, not guessed from the
directory layout. You name them in the task's `scope:` frontmatter (also the
freshness set the gate hashes a receipt against):

```yaml
---
type: Task
title: Reject overlapping bookings
scope:
  - apps/gateway/**
  - src/bookings/**
---
```

`add new Task <slug> --scope apps/gateway/**` writes that line; `add locate
apps/gateway/service.py` does the reverse lookup — *which node's scope owns this
path*. A task that names no cross-part scope is byte-identical to a
single-part project. There is no registry to keep in sync and nothing scans
`apps/*` to guess ownership: the scope is on the node that governs it.

## Verify each task against its own green bar

In a mixed milestone, a backend task and a frontend task pass on **different
toolchains**. The verify gate enforces this per task, through the **bound receipt**:
`add run <slug> --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- <the suite for this scope>` records the checks
that actually ran, and `add gate <slug> PASS` refuses unless every listed check
appears in that receipt with `outcome: pass`. The engine never *runs* the suite —
that invariant holds here too ([NO-EXEC](./01-principles.md)). The AI runs the
right suite for the task's scope; the gate checks that the **right checks were
observed** in a fresh, covers-bound receipt. Two tasks, one milestone, two green
bars — each held to its own.

## Freeze a contract between parts

When one part produces an interface another consumes, that boundary needs a
**frozen, machine-checkable contract**. It is not a separate file type — it is the
producer task's `gives:`, frozen at the freeze stamp, and the consumer task's
`needs:` citing it:

```yaml
# producer task
gives:
  - "POST /bookings -> 409 OVERLAP on user-overlap"

# consumer task
depends_on:
  - /tasks/add-booking-endpoint.md
needs:
  - /tasks/add-booking-endpoint.md#gives     # a frozen fragment of the producer
```

When the **producer** task freezes, its `gives:` becomes an immutable interface
(the frozen-interface rule of the [bundle format](./12-bundle-format.md), FORMAT.md
§3.5). The **consumer** task's `needs:` cites that frozen
fragment by reference — resolved from `graph.json` at brief time, so a spec edit
re-scopes the consumer with no edit here. If the producer later **refreezes a
changed shape**, every node whose `needs:` cite the old fragment is flagged
**stale** and must re-verify before its next gate — ATG's minimal repair made
mechanical: internals may change freely; an interface change propagates as explicit,
bounded re-verification of the dependents. A `needs:` pointing at a `gives:` that
was never frozen is an `edge_unresolved` finding the consumer can see before it
builds against a shape that does not exist.

## One milestone, a full-stack slice

The reason to put a producer and a consumer in the *same* milestone is to ship a
vertical slice — but the frontend must not commit to an endpoint the backend has
not frozen yet. The `depends_on` edge and the frozen `gives:` enforce that ordering:
the consumer's `needs:` cannot resolve until the producer's `gives:` is frozen, so
the slice is **ordered by the frozen contract**, all inside one milestone. The
frontend stays downstream of the backend endpoint, not split into a later milestone.
`add wave <milestone>` reads exactly this DAG: it plans the parallel wave by
**levels**, so producers land before the consumers that depend on them.

## Parallel across parts: waves and worktrees

When a milestone's parts are independent, they run in parallel. `add wave
<milestone>` plans the wave from the task DAG and records the streams; each stream
runs behind its own frozen contract in its **own git worktree**, under its own
persona lens. `add join <bundles…>` folds the finished stream bundles back —
**PASS-only**, unioning their deltas and regenerating the graph.

What makes this safe is that **`graph.json` is a compiled cache**, gitignored and
rebuildable from the node frontmatter at any time. Because every derivable fact is
rendered rather than hand-maintained, there is no shared mutable file for N agents in
N worktrees to conflict on — the compiled cache cannot go stale and has no concurrent
writers. That property, not a coordinator, is what lets a wave fan out.

## Across repositories: one bundle each

Parts in separate repositories work the same way, with one honest difference: an
edge may not escape its bundle (`edge_out_of_bundle` is the one fatal finding), so a
consumer in repo B cannot `needs:` a node in repo A directly. Each repo carries its
**own `.add/` bundle** — its own five specs, its own tasks, its own vendored engine
under `.add/tooling/` (`add init` vendors the flat engine there; `add doctor --sync`
re-vendors a stale copy).

The hand-off between repos is the **frozen interface itself**. The producing repo
freezes its `gives:` and commits it; the consuming repo carries a copy of that frozen
shape as its own contract of record and holds its consumer task against it. The
frozen shape is content-addressed, so a copy that drifts from the source is
detectable rather than silent. This is deliberately **not** an automatic transport:
the engine ships no cross-repo fetch verb, because a boundary between two teams'
repos is exactly where a human-carried, committed contract beats a background pull.
"Publishing" is committing the frozen shape in the producer repo; adopting it is
committing the copy in the consumer repo.

## What this pillar is not

- **Not auto-discovery.** Scope is declared on each task's `scope:`, not inferred
  from the directory tree.
- **Not a central server.** Each repo keeps its own `.add/` bundle; `graph.json` is
  a local, rebuildable cache, and cross-repo sharing is a committed frozen shape, not
  shared mutable state.
- **Not a new approval.** The cross-part machinery rides the existing three-beat flow
  and its single contract-freeze — it adds edges and stale-flags the engine tracks,
  not human checkpoints.

The whole pillar is structure, not policy: who *owns* a part and how strict its floor
is remains the governance story (chapters 09–10) — the sensitivity floor and the
personas — layered on top of this graph.

---

[← 16 Releasing](./16-releasing.md) · [Contents](./README.md) · Next: [18 Personas in practice →](./18-personas.md)
