---
type: Task
title: The carried inventory is windowed the way search already windows it
status: done
depth: standard
milestone: read-cost
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tests/engine

gives:
  - S1 add.deltas(...)'s rendered item rows — windowed at the constant `search` already uses, with the address never truncated
  - S2 the measured before-and-after of a task-intake session — reported as data, not claimed
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:read-cost", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:01b5d2ee3cfae76b", binding: "sha256:e9a79d98e3503d91" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:4f3a273089595e94" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:4f3a273089595e94" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/bounded-delta-listing.d/runs/1.md }
  - { by: "plan:read-cost", at: 2026-09-04, act: gate, authority: process, outcome: PASS, receipt: /tasks/bounded-delta-listing.d/runs/1.md, brief: "sha256:640eb3bb925614fc" }
---
## CARD
goal: the carried inventory is windowed the way `search` already windows it, and the saving is measured rather than asserted.
why: `deltas` emits 27,374 bytes and 51 of its 66 lines exceed the 300-character bound `search` is HELD TO BY TEST, the longest at 830. The two verbs render the same records at 409 and 169 bytes each; `search` windows at `SEARCH_SNIPPET` and `deltas` windows at nothing. It is about 90% of a task-intake session, and it grows every time a lesson is filed — 21 to 40 to 61 open deltas across three minors. The helper and the constant already exist and are already tested. This is safe to do now and was not safe before: `address-dereferences` made one lesson a 608-byte read, so a truncated listing has a cheap way back to the full text.
beat: done · next: add status

## RULES
<must>
- M1 no line `deltas` emits exceeds the bound `search` is already tested against
- M2 the ADDRESS is never truncated — it is the whole point of the row, and the way back to the full text
- M3 the window is the constant `search` uses, not a second one, so the two verbs cannot drift apart
- M4 a truncated row is visibly truncated, so a reader knows there is more and does not quote a fragment as the whole lesson
- M5 the malformed report is untouched: it names a raw LINE, and truncating evidence of a broken line would hide the break
- M6 the before and after are measured on the live bundle and recorded
</must>
<reject>
- R:LOSTADDRESS a row must never be cut in a way that damages the address -> "LOSTADDRESS"
- R:SECONDWINDOW the window must not be a new constant beside `SEARCH_SNIPPET` -> "SECONDWINDOW"
- R:SILENTCUT a truncated row must not look complete -> "SILENTCUT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · n/a · a render change in a read-only verb and a measurement; no stamp, no floor, no write path
- A2 [which] covers: S1 · the request does not say which part of the row is windowed; taking the TEXT only, never the address or the status — the address is the recovery path this whole milestone built -> if wrong, the cut removes the thing that made the cut safe
- A3 [which] covers: S2 · the request does not say which session is measured; taking `status` + `deltas` + one spec read, the sequence SKILL.md teaches for task intake · found: baseline recorded at 41,681 bytes before this milestone -> if wrong, the reported saving describes a session nobody runs
- A4 [when] covers: S1 · the request does not say when a row is windowed; taking ALWAYS, including a short row that is unaffected — a conditional render is two renders and they drift -> if wrong, long and short rows take different code paths
- A5 [when] covers: S2 · the request does not say when the measurement is taken; taking AFTER the change on the same bundle and the same commands as the baseline -> if wrong, the comparison measures two different things
- A6 [absent] covers: S1 · the request does not say what an empty lesson text is; taking the existing render unchanged — `deltas` already shows what it has, and an empty text is a malformed line the report already names -> if wrong, a defensive branch is written for a state the parser rejects
- A7 [absent] covers: S2 · the request does not say what to report when nothing changed; taking the measurement AS IT COMES, including a smaller saving than hoped — a number chosen to look good is not a measurement -> if wrong, the milestone reports its intent instead of its result
- A8 [order] covers: S1 · the request does not say whether order changes; taking `deltas`' existing order UNCHANGED — this windows how a row renders, never which rows there are -> if wrong, a render change silently re-sorts the carried inventory
- A9 [order] covers: S2 · the request does not say the order of measurement; taking baseline-then-change, with the baseline already committed -> if wrong, the baseline is taken after the fact and proves nothing
- A10 [experience] covers: S1 · the receiver is a planner reading the inventory to propose the next tasks; what would make it hard is a truncated lesson they mistake for a whole one, so the cut is visible and the address is intact -> if wrong, the loop plans from half a lesson and the failure is silent
- A11 [experience] covers: S2 · the receiver is a human deciding whether this milestone paid; taking measured bytes on their own bundle rather than a percentage -> if wrong, the claim cannot be checked

## PLAN
contract: `deltas`' item rows render the text through the same `_snippet`/`SEARCH_SNIPPET` path `search` uses, with the address emitted whole. The malformed report is untouched. The intake session is re-measured and recorded beside the committed baseline.
strategy: write the line-length check FIRST, over the LIVE bundle, so the red is the 830-character line that exists today.

## EDGES
- E1 a lesson longer than the window renders truncated and visibly so
- E2 a lesson shorter than the window is unchanged
- E3 the address is intact on a truncated row
- E4 the malformed report still names the raw line in full

## CHECKS
- test_no_emitted_line_exceeds_the_bound · covers: M1, E1 · the live bundle's longest `deltas` line is within the bound `search` is tested against
- test_the_address_survives_truncation · covers: M2, R:LOSTADDRESS, E3 · a long lesson's row still carries its whole address
- test_the_window_is_the_search_constant · covers: M3, R:SECONDWINDOW · asserted from the source: `deltas` uses `SEARCH_SNIPPET`, and no second constant is introduced
- test_a_truncated_row_says_so · covers: M4, R:SILENTCUT, A10 · a cut row is visibly cut
- test_a_short_lesson_is_unchanged · covers: E2, A4 · a lesson under the window renders exactly as before
- test_the_malformed_report_is_untouched · covers: M5, E4 · a malformed line is still reported whole
- test_row_order_is_unchanged · covers: A8 · the sequence of rows matches the carried items
- test_the_saving_is_recorded · covers: M6, A3, A7, A11 · the measured before and after are written down and the after is smaller
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
