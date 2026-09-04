---
type: Task
title: A relation connects two concepts, and the walk can start at either
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - .add/tooling/engine_pin.py
  - add-method/.add/tooling/add.py
  - add-method/.add/tooling/engine_pin.py
  - add-method/FORMAT.md
  - add-method/tests/engine
gives:
  - S1 the walk's relation rows — a relation's `target` is the CONCEPT address it names, never the file that contains it
  - S2 add.neighborhood(...) — accepts a concept address as its start node and walks the concept graph both ways
  - S3 add.show(...)'s `related:` for a concept — inbound and outbound, each with its direction
  - S4 FORMAT.md §11 — what `src` and `target` mean on a relation row
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "Tin Dang", at: 2026-09-04, act: freeze, authority: human, direction: "sha256:404054c2d6dbc6a3", binding: "sha256:8fd57a8108a35a7f" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ccc7cfc11558d03e" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/concepts-are-endpoints.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/concepts-are-endpoints.d/runs/1.md, brief: "sha256:1fb0dfa2bd208226" }
---
## CARD
goal: a relation joins the two concepts it was written between, so a walk that starts at either end finds it.
why: demonstrated live on this bundle. `.add/specs/method.md` declares `M8 refines /specs/method.md#M4` and `M31 refines /specs/method.md#M4`. `add show /specs/method.md#M4` answers "related: none within 3 level(s)" — the two lessons that refine it are invisible from the concept they refine — while `add show /specs/method.md` renders both as `refines /specs/method.md`, a row that reads as a self-loop and names a file where the author wrote a concept. walk-truth repaired the ORIGIN end (which lesson declared the edge); the TARGET end still runs through `_norm`, which strips the fragment by design because a node edge like `needs: /specs/x.md#gives` must resolve to the file. The result is a concept graph that is declarable and citable but not traversable: `show <address>`'s `related:` is structurally always empty, and no check says otherwise. §11 is one release old and unpublished, so the window to correct what a relation row MEANS closes when 3.5.0 ships.
beat: done · next: add status

## RULES
<must>
- M1 a relation whose ref names a concept emits that concept address as the row's `target`
- M2 `neighborhood` accepts a concept address as its start node and refuses an unknown one the way it refuses an unknown cid
- M3 a walk from a concept reaches the concepts related to it, in BOTH directions
- M4 a walk from a FILE still reaches every relation declared in it or targeting it
- M5 the containment decision for a relation's target is UNCHANGED — `doctor` and the standalone validator report the same code at the same severity as before
- M6 §11 states what `src` and `target` are on a relation row
</must>
<reject>
- R:FILEASCONCEPT a relation row must never name a file where the author wrote a concept -> "FILEASCONCEPT"
- R:NODEEDGEDRIFT a NODE edge's target resolution must not change; only the typed relation family gains the fragment -> "NODEEDGEDRIFT"
- R:PHANTOMTARGET a concept address is only emitted as a target when the lesson it names exists; an unresolvable one stays unresolved, never invented -> "PHANTOMTARGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 S4 · n/a · a read-path change; no stamp, no write, no authority. The floor is `architecture` because it moves what a published schema row MEANS
- A2 [which] covers: S1 · the request does not say which refs gain the fragment; taking ONLY `relations:` — `_norm` stays untouched, so `needs:`/`depends_on:` resolve to the file exactly as today (R:NODEEDGEDRIFT) · probe: brief's ref resolution reads `needs: …#gives` through `resolve`, which must keep returning the file -> if wrong, every brief loses its refs
- A3 [which] covers: S1 · the request does not say which fragments count; taking one that names an EXISTING lesson in the target file; an id that names nothing leaves the target unresolved (R:PHANTOMTARGET) -> if wrong, the walk emits edges to concepts that do not exist
- A4 [which] covers: S2 S3 · the request does not say which end may start a walk; taking BOTH — inbound and outbound are one fact seen from two sides, and a reader at M4 wants its refiners as much as a reader at M8 wants its target -> if wrong, half the graph stays unreachable
- A5 [when] covers: S2 · the request does not say when a file's concepts join the walk; taking the SAME depth as the file — containment is not a hop, so `show <spec> --expand 1` still costs one level (M4) -> if wrong, every file walk silently costs a level more than it says
- A6 [when] covers: S1 · the request does not say when the address is computed; taking WALK time from the ref as written, never a cached or stored address -> if wrong, a lesson renamed after the cache still resolves to its old id
- A7 [absent] covers: S1 S3 · the request does not say what an id-less or fragment-less relation does; taking the file cid, exactly as `delta_address` degrades today -> if wrong, a legacy relation stops resolving at all
- A8 [absent] covers: S2 · the request does not say what an unknown concept address does; taking the SAME refusal shape `neighborhood` already gives an unknown cid, so one verb has one grammar (M2) -> if wrong, two refusals mean the same thing in two voices
- A9 [order] covers: S1 S2 S3 · the request does not say what order survives; taking the existing total order unchanged — two reads of an unchanged bundle stay byte-identical -> if wrong, a walk stops being diffable
- A10 [order] covers: S4 · the request does not say where §11 changes; taking the `edges` row description in place, no renumbering -> if wrong, a citation into §11 breaks
- A11 [experience] covers: S3 · the receiver is a reader standing on one lesson; what would make it hard is a `related:` that is empty because the walk cannot represent the thing, while the file it lives in shows the edge — the state demonstrated above -> if wrong, the read keeps lying by omission
- A13 [which] covers: S4 · the request does not say which part of §11 changes; taking the `edges` row's field table, which is the only place a consumer learns what `target` holds -> if wrong, the correction is written where nobody reads it
- A14 [when] covers: S3 S4 · the request does not say when the doc changes; taking THE SAME COMMIT as the behaviour, because a schema note that lags its schema by one commit is how the last wrong docstring happened -> if wrong, the prose and the engine disagree again
- A15 [absent] covers: S4 · the request does not say what §11 says when a relation has no concept target; taking an explicit sentence — the file cid, and why -> if wrong, a reader treats a file target as a bug
- A16 [experience] covers: S2 · the receiver is the next caller of `neighborhood`; what would make it hard is a function that takes two kinds of start value with no word about it, so the docstring names both -> if wrong, the next caller passes a cid and never learns an address works
- A12 [experience] covers: S1 S4 · the receiver is a consumer of the JSON envelope; what would make it hard is a `target` whose meaning changed with no word in the schema that describes it (M6) -> if wrong, a consumer joins on a value that quietly changed shape

## PLAN
contract: relations join concept addresses; `neighborhood` starts at either a cid or a concept address; a file expands into the concepts it hosts at its own depth; `_norm` and the containment path are untouched; §11 says so.
strategy: write the two-sided walk check FIRST against the live bundle's M4/M8/M31 triangle — it is the demonstrated defect, and it must go red before anything moves. Then the containment parity check, so `doctor` and the validator are pinned BEFORE the target end is touched.

## EDGES
- E1 a relation whose ref carries no fragment still resolves to the file
- E2 a relation whose fragment names no lesson leaves the target unresolved
- E3 two lessons refining one concept stay two rows, seen from either end
- E4 a walk from a concept does not spill into every relation its file declares

## CHECKS
- test_a_concept_finds_what_refines_it · covers: M3, A4, E3, A11 · from M4 the walk reaches M8 and M31, both of them
- test_a_relation_targets_the_concept_it_names · covers: M1, R:FILEASCONCEPT, A3 · the row's target is the address, not the file
- test_a_file_still_reaches_all_its_relations · covers: M4, A5, E4 · a file walk is unchanged in content and costs no extra level
- test_a_concept_address_starts_a_walk · covers: M2, A8 · an unknown concept address refuses in the same grammar as an unknown cid
- test_node_edges_did_not_move · covers: M5, R:NODEEDGEDRIFT, A2, E1 · `_norm`, `resolve`, brief refs and the containment codes are unchanged
- test_an_unresolvable_concept_is_not_invented · covers: R:PHANTOMTARGET, E2, A7 · a bad fragment leaves the target unresolved
- test_the_walk_is_still_totally_ordered · covers: A9 · two walks over an unchanged bundle are byte-identical
- test_format_says_what_a_relation_row_means · covers: M6, A10, A12 · §11 describes `src` and `target` for a relation
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
