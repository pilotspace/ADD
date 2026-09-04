---
type: Task
title: add deltas cites a lesson at the same address add search does (X4)
status: done
depth: quick
milestone: okf-graph-lookup
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/.add/tooling/cli.py
  - add-method/tests/engine
  - .add/specs
gives:
  - S1 add.delta_address(stem, delta_id) — the ONE place a lesson's citable address is built, called by both readers, so the two views cannot drift apart again
  - S2 add.deltas(...) note rows — every lesson is rendered at the address `add search` emits, degrading to the bare file when a legacy head carries no id
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:99d826a58907eb0a", binding: "sha256:8fd57a8108a35a7f" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:98eca265e0f57d00" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: FAIL, receipt: /tasks/one-address-per-concept.d/runs/1.md }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/one-address-per-concept.d/runs/2.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:2f89d520ae85a9fa", binding: "sha256:8fd57a8108a35a7f" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/one-address-per-concept.d/runs/3.md }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: gate, authority: process, outcome: PASS, receipt: /tasks/one-address-per-concept.d/runs/3.md, brief: "sha256:ef6f383b4b5bd2db" }
---
## CARD
goal: a lesson found through `add deltas` carries the same citable address it carries through `add search`.
why: X4, filed at the close of okf-graph-time and still open. `deltas` renders a lesson as `[TDD Q14] quality: ...` and `search` renders the same lesson as `/specs/quality.md#Q14`. The id is visible in both, but only one is pasteable into a `relations:` target — so a reader who found a lesson through the wrong door cannot cite it without reconstructing the path by hand.
beat: done · next: add status

## RULES
<must>
- M1 every `deltas` row carries the concept address `search` emits for the same lesson, character for character
- M2 the address form is built in ONE function that both readers call; neither composes it itself
- M3 a legacy head with no id degrades to the bare file address in BOTH readers, the same way
- M4 the X4 delta is folded once this holds, and not before
</must>
<reject>
- R:DRIFT the two views must not build the address separately — a second copy is how they diverged in the first place -> "DRIFT"
- R:LOSTID a row must never drop the lesson text to make room for the address; the address is added, the content is not traded away -> "LOSTID"
- R:HALFFOLD the delta must not be folded while any reader still prints the old form -> "HALFFOLD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · n/a · a rendering change in a read-only verb; no stamp, no floor, no capability
- A2 [which] covers: S1 · the request does not say which address form is canonical; taking SEARCH's, because it already ships, is already pasteable into a `relations:` target, and is already what §3.3 resolves · probe: the string `deltas` prints for a lesson is byte-identical to the one `search` prints for it -> if wrong, a third form appears and neither door is citable
- A3 [which] covers: S2 · the request does not say which rows change; taking EVERY row, including the malformed report, so no reader learns that some lessons are citable and others are not -> if wrong, the exception becomes the thing a reader has to remember
- A4 [when] covers: S1 S2 · the request does not say when the id is absent; taking the LEGACY head — a two-field head carries no id and no date, and both readers already degrade to the file -> if wrong, a legacy line renders an address with an empty fragment, which resolves to nothing
- A5 [absent] covers: S1 · the request does not say what an absent lens stem means; taking it as unreachable — the stem is the spec FILE the delta was read from, so a row exists only because a file did · found: `deltas()` builds items from `path.stem` while walking real spec files -> if wrong, a defensive branch is written for a state no producer can create
- A6 [absent] covers: S2 · the request does not say what happens to the competency letter the old row showed; taking it as REDUNDANT and dropped — `/specs/quality.md` names the lens the `TDD` tag named, and keeping both spends line width twice on one fact -> if wrong, a reader who scanned for `[TDD]` loses their handle
- A7 [order] covers: S1 S2 · the request does not say what orders the rows; taking `deltas()`'s existing order UNCHANGED — this task changes how a row RENDERS, never which rows there are or what sequence they come in -> if wrong, a rendering task silently re-sorts the carried inventory
- A8 [experience] covers: S2 · the receiver is a reader who wants to cite what they just read; what would make it hard is an address they must still assemble, so the row leads with the complete address and the lesson follows it -> if wrong, the address is present but buried and the copy-paste still fails
- A9 [experience] covers: S1 · the receiver is the next author adding a third view of a lesson; taking a NAMED shared function rather than a documented convention, so the third view is a call and not a re-derivation -> if wrong, view three re-derives the form and X4 reopens

## PLAN
contract: `delta_address(stem, delta_id)` returns `/specs/<stem>.md#<id>`, or `/specs/<stem>.md` when the id is falsy. `search()` stops composing the address inline and calls it; `deltas()` renders each row as the address followed by the lesson text. The competency tag and the repeated lens name are dropped as redundant with the path. `fold` the X4 delta only after both readers are proven to agree.
strategy: write the agreement check FIRST — one test that drives both verbs over one lesson and compares the emitted strings — so R:DRIFT is red before either renderer is touched.

## EDGES
- E1 a dated delta with an id renders the same address in both readers
- E2 a legacy two-field head with no id degrades to the bare file in both readers
- E3 the malformed-line report is unaffected — it names a line, not a concept
- E4 the lesson text survives in full; the address is added, not traded for it

## CHECKS
- test_both_readers_emit_one_address · covers: M1, M2, A2, R:DRIFT, E1 · one lesson driven through both verbs yields the identical address string
- test_address_has_one_builder · covers: M2, A9 · `delta_address` exists and both `deltas` and `search` call it, asserted from the source
- test_legacy_head_degrades_alike · covers: M3, E2, A4 · an id-less head renders the bare file address in both readers
- test_lesson_text_is_not_traded_for_the_address · covers: R:LOSTID, E4 · the full lesson text is still present in the row
- test_malformed_report_is_unchanged · covers: E3 · the malformed section still names the raw line
- test_row_order_is_unchanged · covers: A7 · the sequence of rows is identical to the pre-change order, pinned by value
- test_x4_is_folded_only_when_both_agree · covers: M4, R:HALFFOLD · X4 is folded in `.add/specs/experience.md`, and the agreement check above is green
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
