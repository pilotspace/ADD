---
type: Task
title: Every lesson is an addressable concept with a validity interval
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-time
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/engine
  - add-method/tests/skill
  - add-method/scripts
  - .add/specs
  - .add/tooling
  - add-method/.add/tooling
gives:
  - S1 add.learn(root, lens, lesson, evidence) — appends a delta carrying a stable id and a valid-from date
  - S2 add.deltas(root, status) — each item exposes .id, .valid_from and .valid_to, and a line it cannot place is still reported
  - S3 add.fold(root, lens, match) — closes the matched delta's validity interval at today
  - S4 add.parse_delta_head(head) — the one head parser every read path and the migration share
  - S5 the frozen grammar section and reject-code block in `deltas.md`
  - S6 the re-runnable backfill `migrate_delta_ids.py` — dates recovered from git, uncorroborated ones reported
  - S7 add.delta_carried_on(item, date) — the closed-closed interval predicate, so no consumer re-derives the boundary
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:1255589d77f7b7d1", binding: "sha256:694f23500cc13271" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:4c5e8a558f1adc8e" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/dated-addressable-deltas.d/runs/1.md }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/dated-addressable-deltas.d/runs/2.md }
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/dated-addressable-deltas.d/runs/2.md, brief: "sha256:13be0ecca47fd506" }
---
## CARD
goal: a delta becomes an addressable concept with a validity interval — id plus valid-from, closed on fold — and all 43 live lines are migrated with dates recovered from git
why: 43 lessons across five specs are reachable only by opening a file and reading all thirty, and none of them can answer "was this true in August" — an id makes a lesson a target a typed relation can point at, and the date pair is the only thing that makes --as-of possible at all
beat: done · next: add status

## RULES
<must>
- M1 learn writes the dated head — `- [COMP · ID · open · YYYY-MM-DD] lesson (evidence: ptr)` — with the date taken from the engine's own clock: learn exposes no date parameter for a caller to supply one
- M2 the id is a lens letter plus an integer, and the integer is strictly greater than every integer ever allocated in that spec file: the high-water is max(frontmatter delta_seq, the largest id in the body) and learn writes delta_seq back through set_key, leaving every other frontmatter byte untouched
- M3 deltas() exposes .id, .valid_from and .valid_to on every item while the three-tuple (spec, comp, text) unpack it already publishes keeps working unchanged, and equality stays the three-tuple's so no existing comparison changes meaning
- M4 fold closes the interval — status open to folded, and valid_from becomes valid_from then the arrow then today
- M5 the PARSER reads a terminal status as interval-closing and open as one-ended: folded and rejected may carry two endpoints, open may not. Only fold writes a terminal status, and it writes folded; rejected reaches a spec by a human's hand
- M6 the LEGACY two-part head stays readable forever — it lists in deltas() with id, valid_from and valid_to all None, and is never counted malformed
- M7 every live delta line in .add/specs is migrated by a re-runnable script, every line parses as dated afterwards, and the OPEN count is unchanged across the migration — measured before and after, never pinned to a literal a later add learn would invalidate
- M8 the skill's grammar surface states the dated head — deltas.md's frozen-grammar block and the one-line delta definition in terms.md — and deltas.md documents every reject code the engine can emit, enumerated from the engine's own DELTA_REJECTS rather than a hand-kept list
- M9 the id is fragment-safe — a letter then letters, digits, underscore or hyphen — and unique within its spec file, because it is the fragment of the concept address /specs/lens.md#id; learn mints a lens letter followed by an integer, which is one shape inside that set
- M10 the tail after the head stays OPEN: a second trailing clause following the evidence clause leaves the delta parseable and its evidence still found, so a later typed-relation clause cannot empty the inventory
- M11 the persona-target hint moves out of the head and into that open tail, so the head has exactly ONE four-field shape — the claim personas.md makes survives verbatim, and its worked example is restated in the new position
</must>
<reject>
- R:SILENTDROP a delta line the parser cannot place must never be absent from the output entirely, whatever the shape of its failure -> "SILENTDROP"
- R:BADID an id field that is not fragment-safe must never be read as a lesson id -> "BADID"
- R:BADDATE an endpoint that is not a YYYY-MM-DD date must never pass unreported -> "BADDATE"
- R:BADINTERVAL a close earlier than its open, or an open head carrying a close, must never pass unreported — and each reports its OWN code, because the code is the whole message the author gets -> "BADINTERVAL"
- R:REUSEDID no writer may put two deltas carrying one id in one spec file — not learn, and not join, which appends a stream's delta lines verbatim while keeping main's frontmatter and therefore discards the stream's counter -> "REUSEDID"
- R:INVENTEDDATE the migration must never write a date it could not recover from git — including the trap that blaming a folded line returns the commit that FOLDED it, not the commit that FILED it -> "INVENTEDDATE"
- R:RENUMBER a fold, a reject or a delete must never renumber a surviving delta — ids retire in place, because a renumber silently re-points every relation that targets them -> "RENUMBER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3, S4, S5, S6, S7 · the request does not say who may mint an id or stamp a date; taking: only the engine allocates (learn mints, fold closes) and only from its own clock, while a hand-written id is read and honoured but never re-minted -> a hand-numbered id that is too high (M900) permanently burns the id space, and the delta_seq write-back makes the burn outlive deleting the offending line; un-burning is the one case where a human must edit the counter by hand
- A2 [which] covers: S6 · the request does not say which lines the migration set contains; taking: every line matching the delta SHAPE in all five .add/specs files, every status, and an already-dated line is skipped so the script is re-runnable -> if a delta ever lives outside .add/specs it is silently not migrated
- A3 [which] covers: S1, S2, S3, S4, S5, S7 · the request does not say which statuses close an interval; taking: rejected is terminal exactly like folded, so both carry two endpoints -> if rejected were meant to stay open-ended, an --as-of query before the rejection would still correctly show the lesson carried, so the cost is nil
- A4 [when] covers: S1, S2, S3, S4, S5, S6, S7 · the request does not say whether the interval boundary is inclusive; taking: closed-closed — an --as-of on the exact valid_to date still sees the delta, and dates are calendar dates from the engine's own _today() with no timezone or time component -> a consumer that assumes half-open will show a delta one day too long, a one-day error at the seam and never a missing lesson · probe: a delta folded today is still visible to a read at today's date
- A5 [absent] covers: S1, S2, S4, S6 · the request does not say what an absent delta_seq means; taking: absent means derive the high-water from the body, so no migration of frontmatter is needed before the first learn and the init scaffold is not touched -> a file whose highest delta was deleted before delta_seq was ever written can reuse that one id; and because join keeps MAIN's frontmatter, the body-max term is not belt-and-braces but the only thing standing between a merged stream's delta and a colliding mint
- A6 [absent] covers: S2, S3, S5, S7 · the request does not say what a missing date means on a terminal delta; taking: a terminal head carrying one date parses with valid_to None — an unknown close, still listed, never malformed -> an --as-of query cannot tell when such a delta stopped being carried and treats it as still carried, which over-reports rather than losing a lesson
- A7 [order] covers: S1, S2, S3, S4, S5, S7 · the request does not say what orders the ids; taking: ids ascend with time, so the newest-first file reads as descending id and learn keeps prepending -> nothing, unless a reader assumes file order is id order ascending
- A8 [order] covers: S6 · the request does not say how the migration breaks a tie between two deltas blamed to the same commit; taking: number ascending from the BOTTOM of the file upward, so the oldest line gets the lowest id and a same-commit tie is broken by file position -> two lessons filed in one commit get an arbitrary but stable relative order
- A9 [experience] covers: S1, S2, S3, S4, S5, S6, S7 · the request does not say who reads this or what would make it hard; taking: the recipient is the loop agent reading `add deltas` at close and the human scanning the raw spec file, and the difficulty is that a four-field head pushes an already-long lesson further right — so the id and dates are short, lead the line, and the rendered listing shows the id beside the competency rather than the raw head -> a listing that leads with sixteen characters of metadata buries the lesson it exists to surface
- A11 [when] covers: S6 · the request does not say WHICH commit dates a folded line; taking: git blame on a folded line returns the commit that FOLDED it, so valid_from is recovered by pickaxing the lesson text to its filing commit and valid_to from the status-changing commit, and an endpoint neither recovers is left absent and reported -> a folded lesson would otherwise carry a valid_from equal to its valid_to, a date genuinely recovered from git and still a fiction, which R:INVENTEDDATE would not catch · probe: a line filed in one commit and folded in a later one carries the filing date as valid_from
- A10 [when] covers: S6 · the request does not say what date a line whose blame is unavailable gets; taking: none at all — the script reports it and leaves the line untouched rather than stamping today -> a line stays undated until someone dates it by hand, which is visible, where a stamped-today date would be an invisible fiction · probe: a delta line in an untracked spec file comes back reported and unmodified

## PLAN
contract: the id shape is part of THIS frozen contract because two downstream tasks implement against it — fragment-safe `[A-Za-z][A-Za-z0-9_-]*`, unique within its spec file, minted as a lens letter plus an integer, retired in place and never renumbered; the concept address is `/specs/<lens>.md#<id>` and teaching FORMAT §3.3 to resolve that third form belongs to `typed-relations`, not here. The tail after the head stays open so a later `(refines: ...)` clause cannot break the evidence check. one head parser, `parse_delta_head(head)`, returns a dict for the dated four-field head, the legacy two-field head, or None with a reject code. `deltas()`, `fold()` and the migration all read through it, so a grammar change lands in one place. `deltas()` items become a three-element tuple subclass carrying `.id`, `.valid_from`, `.valid_to` as attributes, which keeps every existing `(spec, comp, text)` unpack working and lets `deltas-time-filters` and `search-verb` read the interval without a second parser.
strategy: extend the parser first with the legacy path proven still-green by the pre-existing delta suite running unmodified; then `learn` (mint + delta_seq write-back); then `fold` (close the interval); then `deltas.md` (and the one-line delta definition in `terms.md`) and their two mirror trees; then the migration script; then run it on the live bundle and re-count. Re-aim ENGINE_MD5 and copy add.py to the `_bundled` twin and to `.add/tooling/` in the same change.
scope: add-method/tooling/add.py · add-method/tooling/engine_pin.py · add-method/src/add_method/_bundled/tooling/add.py · add-method/skill/add · add-method/src/add_method/_bundled/skill/add · .claude/skills/add · add-method/tests/engine · add-method/tests/skill · add-method/scripts · .add/specs · .add/tooling · add-method/.add/tooling
regression floor: 35 pre-existing tests are green today across test_delta_grammar.py, test_deltas_verb.py, test_fold_verb.py, test_deltas_never_drop_silently.py, test_receipts_learn.py and tooling/test_tree_parity.py. Three of them pin the OLD write shape and this frozen contract changes their subject, so they are RE-AIMED, never weakened, each keeping its original claim: test_learn_writes_open_tagged_grammar and test_competency_derives_from_lens pin the two-field literal learn writes, and test_deltas_excludes_folded hand-replaces that literal — a fixture that would silently no-op and leave the test passing VACUOUSLY, which is why it is re-aimed rather than left alone. Every other pre-existing test passes UNMODIFIED; the tree-parity guard is green with ENGINE_MD5 re-aimed and both untracked dogfood engines refreshed.

## EDGES
- E1 fold on a legacy two-part head flips the status and invents no date — it records what it can rather than refusing a real user's fold on an un-migrated bundle
- E2 a spec file holding zero deltas mints its first id as 1 and the migration leaves it untouched
- E3 the arrow separator survives the read-write round trip byte-identical through learn, fold and the migration

## CHECKS
- test_learn_writes_an_id_and_a_valid_from_date · covers: M1 · a freshly learned delta matches the four-field dated head with today's date, and learn's signature exposes no parameter a caller could supply it through
- test_a_minted_id_is_the_lens_letter_and_the_next_integer · covers: M2 · two learns on one spec mint 1 then 2, and delta_seq lands in the frontmatter
- test_learn_touches_only_the_delta_seq_key · covers: M2 · every other frontmatter byte is identical before and after a learn
- test_a_deleted_top_delta_does_not_free_its_id · covers: R:REUSEDID · deleting the highest delta then learning again mints a higher id, not the freed one
- test_join_cannot_mint_a_duplicate_id · covers: R:REUSEDID · two streams that each minted the same id merge without two deltas sharing it
- test_a_hand_written_higher_id_is_never_clobbered · covers: M2 · a body id above delta_seq raises the high-water, so the next mint clears it
- test_delta_items_expose_the_interval_and_still_unpack_as_three · covers: M3 · the same item yields spec, comp, text by unpacking and id, valid_from, valid_to by attribute
- test_delta_equality_stays_the_three_tuple · covers: M3 · two deltas differing only in id compare equal, so no existing comparison changed meaning
- test_fold_closes_the_validity_interval · covers: M4 · the folded head carries valid_from, the arrow and today
- test_a_rejected_delta_parses_with_both_endpoints · covers: M5 · the parser reads a hand-written rejected interval, which no engine writer produces
- test_a_legacy_two_part_head_is_still_a_lesson · covers: M6 · an undated legacy line lists in deltas() with a None interval and no malformed report
- test_a_bad_id_field_is_reported_not_read · covers: R:BADID · a head whose id is not fragment-safe reports bad_id and yields no lesson id
- test_a_dotted_id_is_not_fragment_safe · covers: R:BADID · an id carrying punctuation could not survive as a fragment
- test_a_bad_date_is_reported_by_its_own_code · covers: R:BADDATE · an unparsable endpoint reports bad_date, not a shared catch-all
- test_a_reversed_or_early_closed_interval_is_reported · covers: R:BADINTERVAL · a reversed interval and an open head carrying a close each report their own code
- test_every_malformed_shape_is_reported_by_name · covers: R:SILENTDROP · a table of every failure the parser can reach, each proved to put its OWN line text in the report
- test_fold_on_a_legacy_head_invents_no_date · covers: E1 · one fold over a mixed file closes the dated line and leaves the legacy line two-field
- test_an_empty_spec_mints_its_first_id_as_one · covers: E2 · a spec with no deltas learns id 1
- test_the_interval_arrow_survives_the_round_trip · covers: E3, A4 · learn then fold then re-read returns the arrow byte-identical, and the closed-closed predicate still sees a delta folded today
- test_the_minted_id_is_fragment_safe · covers: M9 · every minted id matches the fragment-safe shape and no two deltas in one file share one
- test_a_second_trailing_clause_leaves_the_delta_readable · covers: M10 · a relation clause after the evidence clause keeps the line listed with its evidence found
- test_the_persona_hint_rides_the_tail_not_the_head · covers: M11 · the documented persona-target example parses as a dated delta and keeps its hint
- test_folding_never_renumbers_a_survivor · covers: R:RENUMBER · the ids of every other delta are byte-identical before and after a fold
- test_the_migration_is_rerunnable · covers: M7 · a second run reports nothing changed and rewrites no byte
- test_the_migration_recovers_a_filing_date_not_a_fold_date · covers: M7, A11 · a line filed in one commit and folded in a later one gets the FILING date as valid_from
- test_the_migration_reports_a_line_it_cannot_date · covers: R:INVENTEDDATE, A10 · an unblamable line comes back reported and byte-identical, with no date stamped
- test_the_live_specs_are_fully_dated_and_no_lesson_was_lost · covers: M7 · every live delta line parses as dated and the open count equals the scanned lines less the terminal ones
- test_the_head_shape_is_stated_once_across_the_skill · covers: M11 · the glossary and the persona-delta example both teach the one dated head, with the persona hint moved to the tail and not deleted
- test_deltas_md_states_the_dated_head_and_every_reject_code · covers: M8 · the grammar block shows the four-field head and deltas.md documents every code in the engine's own DELTA_REJECTS
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
