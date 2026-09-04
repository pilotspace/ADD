---
type: Task
title: An address a verb prints is an address a verb can read back
status: direction
depth: standard
sensitivity: architecture
milestone: read-cost
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/FORMAT.md
  - add-method/tests/engine

gives:
  - S1 add.resolve_ref(root, ref) reading a `#id` fragment — the address `deltas` and `search` print resolves to the lesson it names
  - S2 add.show(root, ref, expand) answering for one lesson — its text, its status, its interval and its typed relations, without reading the whole spec
  - S3 add.search(root, query) indexing a delta's own id — a lesson is findable by the address it is cited at
  - S4 FORMAT.md's statement that a concept address is resolvable, not merely citable
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:read-cost", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:b98a67a887e0c787", binding: "sha256:bd1235c2e1600e93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:c6dccb042df9309b" }
---
## CARD
goal: the address every verb tells a reader to cite is an address a verb can read back.
why: `deltas` and `search` both print `/specs/method.md#M33` and both tell the reader to cite it. `add show /specs/method.md#M33` refuses `R:NOSUCHNODE`, and `add search M33` reports no hit — though M33 is in that file and `deltas` just listed it. So the only way to read one lesson in full is a 12,762-byte whole-spec read. This is X4 one level up: X4 made the two doors agree on how to WRITE the address; nothing made it resolvable. It is also the precondition for windowing `deltas` — truncating a listing whose full text costs 12.7 KB to recover would make the tool worse, so this lands first and alone.
beat: direction · next: add freeze address-dereferences

## RULES
<must>
- M1 `resolve_ref` resolves `/specs/<lens>.md#<id>` to the lesson that id names, when exactly one lesson carries it
- M2 `show` on a lesson address answers with that lesson alone — its text, status, interval and relations — never the whole spec
- M3 `search` finds a delta by its own id, so a lesson is findable by the address it is cited at
- M4 a fragment naming no lesson REFUSES and names the file it looked in, so the reader learns which half of the address was wrong
- M5 an address with no fragment resolves exactly as it does today — this task adds a reading, it changes none
- M6 FORMAT.md states that a concept address is resolvable, not merely citable
</must>
<reject>
- R:WHOLESPEC a lesson read must not degrade into reading the file that holds thirty of them — that is the cost this task exists to remove -> "WHOLESPEC"
- R:SILENTMISS a fragment that names nothing must never resolve to the file, which would answer a different question and read as success -> "SILENTMISS"
- R:IDCOLLIDE two lessons sharing an id must refuse and list them, never pick one — the same rule the node path already follows -> "IDCOLLIDE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 S4 · n/a · read-only resolution and indexing; no stamp, no floor, no write path, no authority
- A2 [which] covers: S1 S2 · the request does not say which fragments resolve; taking ONLY a delta id on a spec file — `#card` is already emitted by `search` for a CARD goal hit and means a section, not a concept · probe: `search` emits `{cid}#card` for goal hits and `{cid}#{id}` for deltas -> if wrong, `#card` resolves to a lesson that does not exist
- A3 [which] covers: S3 · the request does not say what `search` indexes; taking the id as an ADDITIONAL field, never a replacement — a text query must keep matching text -> if wrong, an id-only index breaks every existing free-text search
- A4 [when] covers: S1 S2 · the request does not say when the fragment is read; taking AFTER the file resolves — an unreadable file is a file error, and reporting it as a missing lesson would name the wrong half of the address (M4) -> if wrong, a typo'd path is reported as a missing lesson
- A5 [when] covers: S3 S4 · the request does not say when the document moves; taking WITH the code, in the same change — a pinned claim that lags is believed and therefore worse than silence -> if wrong, FORMAT promises a resolution the engine does not perform
- A6 [absent] covers: S1 · the request does not say what an absent lesson is; taking a REFUSAL naming the file that was searched, never a fall back to the file itself (R:SILENTMISS) -> if wrong, a typo'd id silently returns 12 KB of spec and reads as success
- A7 [absent] covers: S2 · the request does not say what a lesson with no relations shows; taking an empty related section, exactly as a node with no edges shows one — a recorded answer, never a silence -> if wrong, a lesson with no links is indistinguishable from a lesson that failed to load
- A8 [order] covers: S3 · the request does not say where an id hit ranks; taking the DELTA tier it already occupies, so adding the id as a matchable field changes what is found and never how results are ordered -> if wrong, an unrelated ranking change rides in on an indexing change
- A9 [order] covers: S2 · the request does not say what orders a lesson's relations; taking `neighborhood`'s existing total order, so two reads are byte-identical -> if wrong, byte-stability holds for nodes and not for lessons
- A12 [which] covers: S4 · the request does not say which document states it; taking the section that already defines the concept address, so a reader meets "citable" and "resolvable" in one place rather than two -> if wrong, the promise is made somewhere a consumer does not read
- A13 [absent] covers: S3 · the request does not say what an absent id means for the index; taking a delta with no id as UNINDEXED BY ID and still matched by text, because there is no id to find it by -> if wrong, an id-less legacy delta becomes unfindable by any means
- A14 [absent] covers: S4 · the request does not say what an unstated guarantee means; taking silence as NO PROMISE — a consumer may rely only on what the section says, which is why the resolvable claim has to be written rather than implied -> if wrong, a reader infers a guarantee from an example
- A15 [order] covers: S1 · the request does not say what orders colliding lessons; taking the sorted address order the node path already lists candidates in, so a collision refusal reproduces run to run -> if wrong, two runs list the same collision differently
- A16 [order] covers: S4 · the request does not say where the statement sits; taking it beside the existing address grammar rather than appended, so the promise reads next to the thing it is about -> if wrong, the guarantee is stated far from the shape it constrains
- A10 [experience] covers: S1 S2 S3 · the receiver is a reader who just saw an address in a listing and wants the lesson; what would make it hard is pasting it and being told it does not exist, which is exactly today -> if wrong, the listing keeps advertising an address that only works as a `relations:` target
- A11 [experience] covers: S4 · the receiver is a consumer deciding whether to build on the address; taking an explicit FORMAT statement, because "citable" and "resolvable" are different promises and only one of them was made -> if wrong, the distinction stays folklore

## PLAN
contract: `resolve_ref` splits a trailing `#<id>` off a spec cid and resolves it against that spec's parsed deltas. `show` renders a lesson view — text, status, interval, and its typed relations from `neighborhood` — instead of the node body. `search` adds the delta id to what it matches. FORMAT states the address is resolvable.
strategy: write the paste-the-address check FIRST, driving the exact string `deltas` prints through `show`, so the red is the live defect and not a fixture.

## EDGES
- E1 the address `deltas` prints, pasted into `show`, answers with that lesson
- E2 a fragment naming no lesson refuses and names the file it searched
- E3 an address with no fragment resolves as it does today
- E4 a lesson carrying no relations shows an empty related section, not an error
- E5 `search` by a bare id finds the lesson, and free-text search is unchanged

## CHECKS
- test_the_printed_address_reads_back · covers: M1, M2, R:WHOLESPEC, E1, A10 · the exact string `deltas` emits is driven through `show` and answers with that lesson, not the spec
- test_a_missing_fragment_refuses_and_names_the_file · covers: M4, R:SILENTMISS, E2, A6 · a bad id refuses and the note names the spec it searched
- test_two_lessons_one_id_refuse · covers: R:IDCOLLIDE · a duplicated id refuses and lists both
- test_an_address_without_a_fragment_is_unchanged · covers: M5, E3 · every ref that resolved before returns exactly what it returned before
- test_a_lesson_is_findable_by_its_id · covers: M3, E5 · `search` by a bare id finds the lesson
- test_free_text_search_is_unchanged · covers: A3, E5 · a text query returns what it returned before the id was indexed
- test_a_lesson_shows_its_relations · covers: A9, E4, A7 · a lesson's typed relations appear, ordered, and an unlinked lesson shows an empty section
- test_format_states_the_address_resolves · covers: M6, A5, A11 · FORMAT says resolvable, not merely citable
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
