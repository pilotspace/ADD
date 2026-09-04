---
type: Task
title: The measured dead and duplicated lines, removed across all four twins
status: done
depth: standard
milestone: read-cost
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - .add/tooling/engine_pin.py
  - add-method/.add/tooling/add.py
  - add-method/.add/tooling/engine_pin.py
  - add-method/tests/engine

gives:
  - S1 add.py with its measured dead source removed, identically in all four twins, both pins re-aimed
  - S2 the ONE boundary definition for a delta's validity interval — the live one, with no dead rival
  - S3 the measured inventory itself: what was removable, what was not, and why
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:read-cost", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:d794ccb4e151e1c0", binding: "sha256:0b417b4206ea56c4" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ed378cee808a3439" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/source-dead-code.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-04, act: gate, authority: process, outcome: PASS, receipt: /tasks/source-dead-code.d/runs/1.md, brief: "sha256:20afd3d45291b89d" }
---
## CARD
goal: the source that no caller reaches is gone from all four twins — and the measurement that says what "no caller reaches" actually amounts to is recorded, because the number this task was created on is wrong.
why: read-cost was planned on a survey claiming ~101 removable lines (1.75% of add.py). Re-measured 2026-09-04 against the parsed AST, cli.py, the standalone validator and the whole test corpus, that number does not survive. Unreferenced module-level definitions: ONE line (`RESERVED_FILES`). Functions no engine or CLI path calls: ONE (`delta_carried_on`, 16 lines). Commented-out code: 3 lines. The nine duplicated "load a node or refuse" preambles are real but return three different conventions (`False`/`None`/a dict), so extracting them saves ~8 net lines and costs every verb its own refusal — not a trim. The measured removable surface is ~22 lines, 0.37%, and the finding that matters is not the bytes: `delta_carried_on` documents the validity interval as CLOSED-CLOSED ("a delta folded today was still carried today") and its docstring claims `--as-of` is wired to it. `--as-of` is not wired to it and implements HALF-OPEN. Probed on the close date: the live filter reports the lesson `folded`, the dead predicate reports it still carried. Two definitions of one boundary, disagreeing on the boundary day, and the dead one has three passing assertions holding it in place.
beat: done · next: add status

## RULES
<must>
- M1 every definition no engine, CLI, validator or test path reaches is removed from add.py
- M2 the removal lands identically in all four add.py twins and both pins are re-aimed
- M3 exactly ONE definition of a delta's validity boundary survives, and it is the one `--as-of` uses
- M4 a test that pinned a removed definition is re-aimed at the live path, never deleted
- M5 the measurement is recorded — what was removable, what was not, and why
</must>
<reject>
- R:BLINDCUT a removal must be proven unreachable by a search over add.py, cli.py, the validator AND the tests, never by reading one file -> "BLINDCUT"
- R:COVERLOSS removing a definition must not remove the CLAIM its test made; the claim moves to the live path -> "COVERLOSS"
- R:CHURN a duplication is only extracted when every site returns the same convention and the emitted bytes are unchanged -> "CHURN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · a source removal with no runtime surface; no stamp, no floor, no authority
- A2 [which] covers: S1 · the request does not say which definitions are dead; taking the four-corpus search (add.py · cli.py · scripts/validate_bundle.py · tests/) as the reachability oracle (R:BLINDCUT) · probe: the search finds `RESERVED_FILES` in the four twins and nowhere else, and `delta_carried_on` only in its own tests -> found: 1 + 16 lines; if the oracle is wrong, a reachable name is deleted and the suite goes red on the spot
- A3 [which] covers: S2 · the request does not say which boundary survives; taking the HALF-OPEN one `deltas --as-of` implements, because its own frozen contract (M4/A3 of deltas-time-filters) says a delta closed ON the queried date was not asserted that day -> if wrong, the surviving boundary is the wrong one and every `--as-of` answer shifts by a day
- A4 [when] covers: S1 · the request does not say when reachability is judged; taking the corpus AS IT STANDS at this commit, not a historical or future caller -> if wrong, a caller added later re-introduces what was removed
- A5 [absent] covers: S2 · the request does not say what happens to a test whose subject is gone; taking RE-AIM at the live path (R:COVERLOSS), never deletion -> if wrong, a claim the suite used to make silently stops being made
- A6 [absent] covers: S3 · the request does not say what to do when the inventory is smaller than planned; taking RECORD IT — a milestone planned on a wrong number is worth more as a corrected number than as churn manufactured to match it -> if wrong, the milestone closes on an EXIT line nobody re-read
- A7 [order] covers: S1 S2 · the request does not say what order the twins take; taking source-then-mirror-then-repin, the order every prior engine edit used, so a half-mirrored tree is never pinned -> if wrong, a pin attests a file that does not exist yet
- A9 [which] covers: S3 · the request does not say which measurement counts; taking the AST parse over the four corpora, because a grep over one file was exactly how the wrong number was produced -> if wrong, the correction is as unreliable as what it corrects
- A10 [when] covers: S2 S3 · the request does not say when the inventory is fixed; taking THIS commit — a later caller or a later survey is a new reading, not a refutation of this one -> if wrong, the recorded number reads as permanent
- A11 [absent] covers: S1 S2 · the request does not say what an already-clean twin means; taking it as done, not as an error (E3) -> if wrong, a no-op write is reported as a change
- A12 [absent] covers: S3 · the request does not say what to record when nothing is removable; taking THAT as the finding, stated plainly -> if wrong, an empty removal reads as an unfinished task
- A13 [order] covers: S3 · the request does not say when the inventory is written; taking AFTER the removal, so it records what happened and not what was planned -> if wrong, the node records an intention
- A14 [experience] covers: S1 S2 · the receiver is the next engineer reading add.py; what would make it hard is a docstring naming a caller that does not exist, which is precisely what is being removed -> if wrong, the file keeps teaching a wiring that was never there
- A8 [experience] covers: S3 · the receiver is whoever reads the milestone's close; what would make it hard is a green EXIT box over a claim that was never true, so the correction is stated in the node and not only in a commit message -> if wrong, the wrong number outlives the task that disproved it

## PLAN
contract: remove `RESERVED_FILES` and `delta_carried_on`; re-aim `delta_carried_on`'s three assertions at `deltas(--as-of)` so the boundary claim survives against the live implementation; mirror to four twins, re-aim both pins; record the corrected inventory in the node.
strategy: prove unreachability across all four corpora BEFORE deleting anything, and write the re-aimed boundary check FIRST — it must fail against the dead predicate's semantics and pass against the live one.

## EDGES
- E1 a name reachable only from a test is NOT dead — it is engine surface, and stays
- E2 the boundary check disagrees with the removed predicate on the close date, and that is the point
- E3 a twin that already matches needs no write, and the pin still verifies

## CHECKS
- test_the_removed_names_are_gone_everywhere · covers: M1, R:BLINDCUT, A2 · neither name survives in any of the four twins
- test_one_boundary_definition_survives · covers: M3, A3, E2 · the close date reads folded, and no rival predicate says otherwise
- test_the_boundary_claim_survived_the_removal · covers: M4, R:COVERLOSS, A5 · the three assertions still run, against the live path
- test_all_four_twins_and_both_pins_agree · covers: M2, A7, E3 · the four add.py twins are byte-identical and both pins verify
- test_engine_surface_was_not_removed · covers: E1 · a name only the tests call is still importable
- test_the_inventory_is_recorded · covers: M5, R:CHURN, A6, A8 · the node records what was removable and what was left alone
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
