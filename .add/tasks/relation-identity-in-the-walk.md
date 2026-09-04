---
type: Task
title: A relation is identified by the lesson that declared it, in the walk and in the payload
status: direction
depth: standard
sensitivity: architecture
milestone: walk-truth
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/FORMAT.md
  - add-method/tests/engine

gives:
  - S1 add.neighborhood(graph, cid, expand) rows — each row carries the address of the concept that DECLARED the edge, and the dedup key distinguishes two relations that agree on rel and ref
  - S2 FORMAT.md section 11's edges[] schema and the payload that fills it — the declaring address is a key a consumer can read
  - S3 add.show(...)'s prose render — a relation row names the lesson it came from, so the human view loses nothing the machine view gained
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:walk-truth", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:e0f509ea55d95f57", binding: "sha256:9feb3826b419be57" }
---
## CARD
goal: two lessons refining one target emit two rows, and every row names the concept that declared it.
why: `relations()` returns the declaring delta id and `neighborhood()` throws it away, dedupping on `(family, label, src, ref, target)`. Two lessons refining the same target collapse into one row. It is live: `.add/specs/method.md` declares `M8 refines #M4` and `M31 refines #M4`, and the walk emits one — 4 relations in the bundle, 3 rows. FORMAT section 3.4 promises one EDGE emitted once; two edges are not one edge. And the `edges[]` schema pinned in section 11 has no key that could carry the id, so a consumer cannot recover the loss even in principle.
beat: direction · next: add freeze relation-identity-in-the-walk

## RULES
<must>
- M1 two relations that agree on rel and ref but were declared by different lessons emit TWO rows
- M2 every row carries `origin` — the address of the concept that declared the edge: a lesson address for a relation, the node's own cid for a node edge
- M3 the dedup key includes `origin`, so one edge is still emitted once at its shallowest depth
- M4 FORMAT section 11 pins `origin` beside the other edge keys, and section 3.4 states identity in terms of the declaring concept
- M5 the prose render names the declaring lesson for a relation, so the human view is not the lossy one
- M6 the walk's relation-row count over the live bundle equals what `relations()` reports for those nodes
</must>
<reject>
- R:COLLAPSE two distinct declared edges must never become one row -> "COLLAPSE"
- R:DOUBLEVISIT the fix must not reopen double-emission — one edge seen outbound from one node and inbound at the other is still ONE fact -> "DOUBLEVISIT"
- R:PINNEDNUMBER the count check must compare two computed values, never assert a literal that goes stale the moment a lesson is filed -> "PINNEDNUMBER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · a read-only traversal and its two renders; no stamp, no floor, no write path, no new capability
- A2 [which] covers: S1 S2 · the request does not say HOW identity is carried; taking a new `origin` key rather than redefining `src`, because a consumer joining `src` to a node cid must keep working and `results[]` already pairs a full `address` with a bare `cid` for exactly this reason -> if wrong, every consumer that joined on `src` breaks on the release that was supposed to fix a loss
- A3 [which] covers: S3 · the request does not say what the prose shows; taking the delta ID alone, not the full address — the row already prints the target address, and repeating the file twice per line spends width on a fact the reader has -> if wrong, the human render is wider for no added information
- A4 [when] covers: S1 · the request does not say when `origin` differs from `src`; taking ONLY the relation family — a node edge is declared by the node itself, so `origin == src` there and no consumer needs a special case · probe: `edges()` yields `(cid, key, ref, target)` with no sub-node identity, so a node edge has no other declarer -> if wrong, a node edge invents an origin nothing produced
- A5 [absent] covers: S1 · the request does not say what a relation with no parseable delta id is; I took it as a legacy head degrading to the file address, and the probe REFUTED that · found: `parse_relation('refines /x.md#M1')` returns `(None, None, raw)` — the id is MANDATORY in the relation grammar, so an id-less entry is malformed, `rel is None`, and the walk already skips it. `origin` therefore always carries an id, and the degrade branch would be code for a state no producer can create -> the cost of having been wrong: a defensive branch and a reject code that name nothing, which is this repo's documented defect class
- A6 [absent] covers: S2 S3 · the request does not say what `origin` is when it equals `src`; taking it as PRESENT anyway, never omitted — a key that appears only sometimes forces every consumer to branch, which is the shape section 11 already refused for `edges` -> if wrong, the schema has an optional key and is no longer one schema
- A7 [order] covers: S1 · the request does not say where `origin` sits in the sort; taking it into the existing total order after `label` and before `ref`, so two rows that differ only by declarer order deterministically · probe: the sort key already coerces a None target, and adding a field keeps it total -> if wrong, two runs order the two new rows differently and byte-stability fails intermittently
- A8 [order] covers: S2 S3 · the request does not say whether row ORDER changes; taking it as unchanged except for the newly-distinguished rows — this task adds rows that were being lost, it does not re-rank the ones that survived -> if wrong, a rendering fix silently re-sorts the whole walk
- A9 [experience] covers: S3 · the receiver is a human reading `add show` on a spec; what would make it hard is two identical-looking rows, so the declaring id is what tells them apart -> if wrong, the fix emits the second row and the reader cannot see why it is not a duplicate
- A10 [experience] covers: S1 S2 · the receiver is a consumer that pinned section 11 one release ago and unpublished; taking an ADDED key over a changed one, so a reader written against the old shape keeps working -> if wrong, an unreleased schema still breaks somebody
- A11 [when] covers: S2 S3 · the request does not say when the two renders must move; taking WITH the row — a payload or a prose line that lags the row shape describes a walk the engine stopped emitting, and section 11 is believed precisely because it is pinned -> if wrong, the document and the two renders disagree about what an edge is

## PLAN
contract: `neighborhood()` keeps `relations()`'s `src_id` and emits an 8-field row `(depth, direction, family, label, origin, src, ref, target)`. `origin` is `delta_address(stem, src_id)` for a relation and `src` for a node edge. The dedup key becomes `(family, label, origin, ref, target)`. `show_payload` adds `"origin"`; FORMAT section 11 pins it and section 3.4 restates identity. `show()`'s render appends the delta id to a relation row.
strategy: write the two-relations-one-target check FIRST against the LIVE bundle shape, and prove it red by the collapse that exists today. Then the count reconciliation, which must compare two computed values so it cannot go stale.

## EDGES
- E1 two lessons in one file refining one target — the live case
- E2 the same edge seen outbound from one node and inbound at the other is still one row
- E3 a relation with no id is MALFORMED, not degraded: it yields no walk row at all, so `origin` never carries a bare file address
- E4 a node edge's `origin` equals its `src`, and the key is present

## CHECKS
- test_two_lessons_one_target_emit_two_rows · covers: M1, R:COLLAPSE, E1 · the live shape, built in a fixture: two relations agreeing on rel and ref, two rows out
- test_every_row_names_its_declaring_concept · covers: M2, A6, E4 · `origin` is present on every row, is a lesson address for a relation, and equals `src` for a node edge
- test_one_edge_is_still_emitted_once · covers: M3, R:DOUBLEVISIT, E2 · an edge reachable both directions emits one row, at its shallowest depth
- test_walk_reconciles_with_relations · covers: M6, R:PINNEDNUMBER · the walk's relation rows are compared against `relations()` over the same nodes — two computed values, no literal
- test_format_pins_the_declaring_key · covers: M4 · section 11 names `origin` and section 3.4 states identity in terms of the declaring concept
- test_prose_render_names_the_lesson · covers: M5, A3, A9 · two otherwise-identical relation rows are distinguishable in `show`'s human output
- test_an_idless_relation_is_malformed_not_degraded · covers: A5, E3 · the grammar rejects an id-less entry and the walk emits no row for it, so the degrade branch is unreachable
- test_row_order_is_total_and_stable · covers: A7, A8 · two walks over an unchanged bundle emit identical rows, and the newly-split rows order deterministically
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
