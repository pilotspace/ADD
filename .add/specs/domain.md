---
type: Spec
title: Domain
lens: domain
project: AIDD-Book
description: what ADD itself must be true about — the bundle, the node, and the vocabulary a conforming engine speaks
tags: [bundle, node, vocabulary]
sources: []
generated: { by: add/3.0.0, at: 2026-08-08 }
delta_seq: 1
open_deltas: 0
---
## Now
The bundle IS the database. A conforming engine reads `.add/` — markdown files with YAML
frontmatter — and `graph.json` is a rebuildable cache of what those files already say, never a
second copy of it. One task is one atomic node with one lifecycle: direction → build → verify,
and exactly one human approval, at the freeze. The engine RECORDS and REFUSES; it never runs the
method, spawns an agent, or judges what a stamp attests.

## Decisions that bind
- The beat is DERIVED from a node's stamps, never read from a stored field. `status:` stays `direction` until close, so any surface that reports progress computes it — a stored beat drifts from the node it describes.
- A node's `covers:` binds EVERY referent it names — Musts, Rejects, filled edges, probed assumptions. There is ONE definition of an obligation, computed in one place and read by both the freeze rung and the gate. (from: /specs/method.md#M46, /tasks/uncovered-widens-to-rules.md)
- The authority floor is computed from `sensitivity:`, never from depth: `security → human`, `data|architecture → plan`, else `process`. Depth tunes ceremony; it never moves the floor. Security is a HARD-STOP no persona, depth or verdict buys back.
- A scaffold is a node that exists and has not been authored. It is not a beat but a STATE, and what it means depends on the plan that claims it — `queued`, `abandoned` or `adrift`. Derived from the milestone, never stored.
- The teacher corpus is REFERENCED, never vendored into a node. A persona reaches a brief as frontmatter; its body stays a file the agent may read and the bundle never copies.

## Deltas
- <what changed, and the evidence that changed it>
- [DDD · D1 · rejected · 2026-09-04→2026-09-08] The five specs' '## Decisions that bind' hold only the scaffold placeholder, and bind_sections() feeds that placeholder into EVERY brief. One of the two spec sections the method leans on has never been authored in this bundle — a search facet over it was cut for exactly that reason. (evidence: bind_sections add.py · all five .add/specs/*.md)
