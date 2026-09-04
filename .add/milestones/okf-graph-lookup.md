---
type: Milestone
title: Reading the bundle as a graph — one node in full, its neighbourhood to three levels, and a filter that answers by field
status: direction
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:1" }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:2" }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:3" }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:4" }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:7" }
advised_by: method-steward
---
## CARD
goal: any milestone or task in the bundle can be read whole by slug, with its relationships walked to three levels across both edge families and both directions, and any set of nodes can be selected by field rather than by substring — all of it emittable as JSON an agent consumes without re-parsing a table.
why: `okf-graph-time` made every lesson addressable, dated and typed, and gave one verb that FINDS a concept. Nothing READS one. `add search` returns an address and a 96-character snippet; `brief` returns a phase-scoped prompt, not the node; so an agent that wants a task's contract still `cat`s the file — outside the engine, unbounded, and with no relationships attached. And the relationships are worse than absent, they are misleading: measured on this bundle at 220 nodes, `edges()` yields 129 edges of which 120 are Run/Interview→Task receipt backlinks, 9 are Task→Task (`needs` 5, `depends_on` 4), and **`milestone:` is declared on 45 nodes and traversable from none** — every value is a bare slug and `edges()` skips any ref without `.md`, so the single most load-bearing structural link in the bundle is invisible to the graph. `todo` and `wave` only find it by string-comparing `_wave_slug()`. A three-level walk from a Milestone returns NOTHING today, and a walk from a Task returns its receipts and nothing about the milestone that owns it.
next: add new task <slug>

## SCOPE
In:  a bounded `neighborhood()` BFS primitive over BOTH edge families (`EDGE_KEYS` untyped node edges + `relations:` typed concept edges) in BOTH directions · milestone membership resolved into a real, traversable edge · `add show <ref>` as the 26th verb, read-only, full node content + `--expand N` · `add search` gaining structured field filters beside its free-text grammar · one `--json` payload schema serving both verbs · the X4 fold so `deltas` and `search` cite one concept at one address · the SKILL.md/intake routing that teaches the loop to read the graph before it plans
Out: any WRITE path — this milestone adds no verb that stamps, gates, closes or overrides, and touches no authority floor · widening `RELATION_VOCAB` beyond `refines` (the bar is a live instance in the same change) · `graph.json` becoming readable by the engine (law 1 stands; the primitive reads `scan()`) · a query LANGUAGE — filters are equality over declared fields, never expressions · exploding the `--expand` walk past a hard cap

## GROUND
touches: add-method/tooling/add.py · add-method/tooling/cli.py · add-method/tooling/engine_pin.py · add-method/FORMAT.md · add-method/README.md · README.md · add-method/docs/13-command-reference.md · add-method/skill/add · add-method/src/add_method/_bundled · .claude/skills/add · add-method/tests/engine · add-method/tests/skill · .add/specs
risks:
  - making `milestone:` traversable changes what `edges()` returns for 45 nodes at once, and `cycles()`, `doctor` and `wave` all read that function — a membership edge that joins the dependency adjacency would invent 45 false cycles (Milestone→Task→Milestone), so the new edge must be a distinct family or explicitly excluded from `cycles()`, proven by a check that reds when it is not
  - `add show` is a new verb, and a new verb is never one edit — M19/M28/S5 measured the ripple at five-plus registries (the CLI WIRED set, both README verb counts, the book command reference, the SKILL.md budget pins, and a phantom-verb fixture that uses a name precisely because it does not exist) and S5 proved a verb-count pin names no verb, so it is invisible to every grep. Find them by running the full suite, never by grepping
  - `--json` is the engine's first JSON on stdout — `json` is imported today solely to WRITE `graph.json`. An unpinned payload shape is a contract nobody can depend on and nobody can break loudly; it needs a schema in FORMAT.md and a determinism check, or it becomes a de-facto API that drifts silently
  - `add search`'s positional is REQUIRED today and an empty query is a recorded refusal (`R:EMPTYQUERY`); making it optional for filter-only mode re-opens that hole unless "no query AND no filter" still refuses — the exact "an unknown reads as clean" class this bundle has filed M22, M24 and S2 about
  - a read that silently degrades into a search answers a different question than the one asked and reads as success; `show` must refuse a ref that does not resolve to exactly one node, never fall back
  - both engine pins re-aim, not one: `ENGINE_MD5` pins `add.py` and `ENGINE_PKG_MD5` pins `cli.py` (S4) — every task here touches at least one and most touch both

## EXIT
- [x] milestone membership is a real edge the graph can walk in both directions, without inventing a cycle in `cycles()` and without breaking `todo`/`wave`'s slug matching   (← milestone-membership-is-an-edge)
- [x] `add.neighborhood(graph, cid, expand)` walks both edge families in both directions to a bounded depth, is cycle-safe, and emits a total order so two runs over an unchanged bundle are byte-identical   (← graph-neighborhood)
- [x] `add show REF` returns a node's full content plus its neighbourhood, defaults to 3 levels, refuses above the cap rather than clamping, refuses a ref that is not exactly one node, and every verb registry knows the 26th verb   (← show-verb)
- [x] `add search` selects by `--type`, `--status` and `--milestone` beside its free-text grammar, with the positional optional and "no query and no filter" still a refusal   (← search-structured-filters)
- [ ] one `--json` payload schema, pinned in FORMAT.md, serves both `show` and `search`, and is proven byte-stable across runs   (← json-emission)
- [x] `add deltas` cites a lesson at the same address `add search` does, so a reader who found it through either door can cite it (X4)   (← one-address-per-concept)
- [x] the loop reads the graph before it plans — SKILL.md and intake name the read step, byte-identical across all three shipped skill trees, funded by compression inside the existing budget pins   (← skill-reads-the-graph)

## CLOSE
evidence: <one row per task>
