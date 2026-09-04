---
type: Task
title: A bounded, cycle-safe walk over both edge families in both directions
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-lookup
depends_on:
  - /tasks/milestone-membership-is-an-edge.md
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/FORMAT.md
  - add-method/tests/engine
gives:
  - S1 add.neighborhood(graph, cid, expand) — (rows, note); rows is None ONLY when cid names no node in the graph. Each row is (depth, direction, family, label, src, ref, target) under one total order
  - S2 add.NEIGHBORHOOD_MAX — the one home for the depth cap, cited by the verb that enforces it and by FORMAT, so the number is never spelled twice
  - S3 FORMAT.md — the documented walk contract: which families, which directions, what a repeat visit emits, and what orders the rows
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:805877f7ef2f02cd", binding: "sha256:0a1f598d0ebde73a" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:43d864c0fa6750bd" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/graph-neighborhood.d/runs/1.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/graph-neighborhood.d/runs/1.md, brief: "sha256:8e314a4e3da39be6" }
---
## CARD
goal: one bounded, cycle-safe, deterministic walk outward from any node, over both edge families and both directions.
why: `edges()` and `relations()` are flat lists and `cycles()` walks one direction of one family. Nothing in the engine can answer "what is near this node", so the read verb has nothing to call. The walk has to be bounded and totally ordered before a verb prints it, or two runs over an unchanged bundle differ and no reader can diff them.
beat: done · next: add status

## RULES
<must>
- M1 the walk covers BOTH families — the `EDGE_KEYS` untyped node edges and the `relations:` typed concept edges — and both are distinguishable in the row by a `family` field
- M2 the walk covers BOTH directions: a row where the start node is the source, and a row where it is the target, each labelled, so "what depends on this" is answerable
- M3 the walk is bounded by `expand` and never emits a row deeper than it; `NEIGHBORHOOD_MAX` is the one home for the ceiling and the primitive names it, so no caller spells the number itself
- M4 the walk is cycle-safe: a node already reached at an equal or shallower depth is never expanded again, and the walk terminates on a graph that is a single cycle
- M5 the rows carry a TOTAL order, so two calls over an unchanged bundle return byte-identical rows
- M6 a `cid` that names no node in the graph returns `rows is None` — a refusal, never an empty list
</must>
<reject>
- R:EMPTYISUNKNOWN an empty row list must never be returned for a node that does not exist; "no neighbours" and "no such node" are different answers and a caller must be able to tell them apart -> "EMPTYISUNKNOWN"
- R:UNBOUNDED no input may make the walk visit a node twice or run past `expand`, on any graph shape including a self-edge -> "UNBOUNDED"
- R:CACHEREAD the walk reads the scanned graph it is handed and never `graph.json`; law 1 stands -> "CACHEREAD"
- R:SILENTORDER the order must not depend on dict or set iteration; every tie is broken by a field in the row -> "SILENTORDER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · the walk is a pure read over a graph the caller already holds; it grants no capability, records no stamp, and touches no authority floor
- A2 [which] covers: S1 · the request does not say which edges belong to a neighbourhood; taking BOTH families and BOTH directions, because an outbound-only walk cannot answer "what depends on this", which is most of what a reader wants from a task node · probe: a Task's neighbourhood at depth 1 contains its Run receipts, which reach it only on the INBOUND `task:` edge -> if wrong, the walk answers half the question and reads as complete
- A3 [which] covers: S2 S3 · n/a · the cap and the documented contract are single values with no membership question — there is no subset of them to choose
- A4 [when] covers: S1 · the request does not say whether a node reached twice appears twice; taking the EDGE as the unit — every distinct edge is emitted once, at the shallowest depth it is reached, and the node behind it is expanded only the first time · probe: a bundle with two paths to one node emits both edges and expands that node once -> if wrong, either a real link is hidden or the walk doubles rows on every diamond
- A5 [when] covers: S2 · the request does not say whether the cap is inclusive; taking `expand` as the DEEPEST depth emitted, so `--expand 1` means immediate neighbours -> if wrong, every caller is off by one and the verb prints a level nobody asked for
- A6 [when] covers: S3 · n/a · a documented contract has no runtime boundary of its own; the boundaries it describes are S1's and S2's and are swept there
- A7 [absent] covers: S1 · the request does not say what an unresolved edge contributes; taking it as a row with `target` None that is EMITTED but never expanded, because a dangling `depends_on` is information about this node -> if wrong, a broken link silently disappears from the one view built to show links
- A8 [absent] covers: S2 S3 · the request does not say what an absent `expand` means; taking the verb's default of 3 as the primitive's default too, so one number governs and a caller that omits it gets the documented walk · found: the ratified direction fixes the default at 3 and the cap at 5 -> if wrong, the primitive and the verb disagree about what "the default walk" is
- A9 [order] covers: S1 S3 · the request does not say what orders the rows; taking (depth, direction, family, label, src, ref, target) — every field in the row participates, so no tie can fall through to dict order · probe: two calls over one unchanged bundle return identical row lists -> if wrong, output is undiffable and every downstream pin churns
- A10 [order] covers: S2 · n/a · a scalar ceiling has no ordering
- A11 [experience] covers: S1 S2 · the receiver is the read verb and, through it, an agent spending context on the result; what would make it hard is unbounded volume, so the row is a flat tuple rather than a nested tree and the caller shapes the display -> if wrong, the primitive dictates one rendering and the JSON payload has to un-nest it again
- A12 [experience] covers: S3 · the reader is the next author adding an edge family; taking a FORMAT contract that states the walk in terms of FAMILIES rather than of the two that exist today, so a third family joins by satisfying the contract -> if wrong, the contract names today's families and the next one is bolted on beside it

## PLAN
contract: `neighborhood(graph, cid, expand=3)` returns `(rows, note)`. `rows is None` only when `cid` is not a key of `graph`. Otherwise `rows` is a list of `(depth, direction, family, label, src, ref, target)` where `direction` is `"out"` or `"in"`, `family` is `"edge"` or `"relation"`, and `label` is the edge key or the rel word. The walk is breadth-first from `cid`; an edge is emitted at the shallowest depth it is reached and a node is expanded at most once. `NEIGHBORHOOD_MAX` is a module constant; the primitive does not enforce it (the verb refuses above it) but names it so there is one home for the number.
strategy: build the two adjacency maps once from `edges()` and `relations()` — forward and reverse — then walk levels with a visited set. Write the checks first, including a self-edge fixture and a two-path diamond, and prove termination before proving content.

## EDGES
- E1 a self-edge (`depends_on` naming its own node) terminates and is emitted once
- E2 a two-node cycle terminates at any `expand`
- E3 a diamond — two distinct paths to one node — emits both edges and expands the node once
- E4 an unresolved edge (`target` None) is emitted and never expanded
- E5 `expand=0` returns an empty list and a note, never a refusal — the node exists, its neighbourhood was simply not asked for
- E6 a node with no edges at all returns an empty list and a note, distinguishable from a refusal by `rows == []` rather than `rows is None`

## CHECKS
- test_walk_covers_both_families · covers: M1 · a bundle carrying a `depends_on` and a `relations:` entry yields rows of family `edge` and family `relation`
- test_walk_covers_both_directions · covers: M2, A2 · a Task's depth-1 rows include its Run receipt, reachable only inbound, and its milestone, reachable only outbound
- test_expand_bounds_the_depth · covers: M3, A5 · no row exceeds `expand`, and `expand=1` returns only immediate neighbours
- test_cap_has_one_home · covers: M3 · `add.NEIGHBORHOOD_MAX` exists and is the only literal for the ceiling in the engine
- test_a_cycle_terminates_and_visits_once · covers: M4, E1, E2, R:UNBOUNDED · a self-edge and a two-node cycle both terminate, and no node is expanded twice
- test_a_diamond_emits_both_edges_once · covers: E3, A4 · two paths to one node yield two edge rows and one expansion
- test_rows_are_totally_ordered · covers: M5, A9, R:SILENTORDER · two calls over an unchanged bundle return identical rows, and the sort key names every field
- test_absent_node_refuses_rather_than_empties · covers: M6, R:EMPTYISUNKNOWN, E6 · a cid not in the graph returns None; a real node with no edges returns []
- test_unresolved_edge_is_emitted_not_expanded · covers: A7, E4 · a dangling `depends_on` appears as a row with target None
- test_expand_zero_is_an_answer_not_a_refusal · covers: E5 · `expand=0` returns [] and a note
- test_walk_never_reads_the_cache · covers: R:CACHEREAD · the walk returns identical rows with `graph.json` deleted
- test_format_states_the_walk_contract · covers: A12 · FORMAT states the walk in terms of families and directions, not of the two families that exist today
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
