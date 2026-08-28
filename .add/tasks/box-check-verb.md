---
type: Task
title: add check toggles a checklist box and stamps who did it
status: done
depth: standard
sensitivity: architecture
milestone: checkbox-verb
scope:
  - add-method/tooling
  - add-method/src/add_method/_bundled/tooling
  - add-method/.add/tooling
  - add-method/tests
  - add-method/skill/add
  - .claude/skills/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/docs
  - README.md
  - add-method/README.md
gives:
  - S1 `add.py check(root, cid, indices, off, section, by)` — the box writer; returns the engine's `(node, message)` pair
  - S2 the `cli.py` `check` subcommand — `add check REF N... [--all] [--off] [--section S] [--by WHO]`
  - S3 the `verified:` stamp `act: check` recording who marked which boxes
  - S4 `milestone_done`'s close line, extended to name who checked
  - S5 the skill text listing the wired loop surface, in all three trees
  - S7 every registry that enumerates the verb set — the CLI's WIRED set, both README verb counts, the book command reference, and the phantom-detector fixture that used `check` as its example of a verb that does not exist
  - S6 engine tests for S1–S4 plus the re-aimed `ENGINE_MD5` / `ENGINE_PKG_MD5` pins
generated: { by: add/3.2.0, at: 2026-08-28 }
verified:
  - { by: "Tin Dang", at: 2026-08-28, act: freeze, authority: plan, direction: "sha256:12467f090bf4b729" }
  - { by: "Tin Dang", at: 2026-08-28, act: refreeze, authority: plan, direction: "sha256:37c522350eef23cd" }
  - { by: "cli", at: 2026-08-28, act: brief, authority: process, brief: "sha256:ecd3a500e2600dfa" }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/box-check-verb.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-28, act: refreeze, authority: plan, direction: "sha256:5c0ed67fd85bd9fa" }
  - { by: "cli", at: 2026-08-28, act: brief, authority: process, brief: "sha256:ce0dd54b20e1a8d4" }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/box-check-verb.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-28, act: gate, authority: plan, outcome: PASS, receipt: /tasks/box-check-verb.d/runs/2.md, brief: "sha256:ce0dd54b20e1a8d4" }
---
## CARD
goal: Give the engine a verb for the tally it already reads — `add check <ref> <n>…` marks boxes, `--off` unmarks, one `verified:` stamp per invocation records who did it, and `milestone-done` names those people at close so a self-served goal-gate is visible rather than silent.
why: `milestone_done` gates on a `- [x]` tally it cannot write; this session closed a milestone with a
  throwaway script. The human chose the general verb (any box, any node, any section) over the narrower
  notary design, and chose an audit stamp over a refusal — so the affirmation is no longer defended by
  the engine and must instead be legible in the record. That makes S3 and S4 load-bearing, not garnish.
beat: done · next: add status

## RULES
<must>
- M1 `check(root, cid, indices, off=False, section=None, by=None)` marks the named boxes `- [x]`; with `off=True` it restores them to `- [ ]`. Indices are 1-based over the boxes in document order; `--section <name>` narrows to one `## <name>` section and re-indexes from 1 within it; `--all` takes every box in range.
- M2 A box already in the requested state is reported as unchanged, not an error, and consumes no stamp of its own — the invocation still stamps once if ANY box moved, and stamps nothing when none did.
- M3 Every invocation that moves at least one box appends exactly ONE `verified:` entry: `{ by: "<who>", at: <date>, act: check, authority: <authority_for(node)>, boxes: "<section>:<n>[,<n>…]" }` — `off` runs record `act: uncheck`. `by` defaults to `process:check` when the caller names nobody, so an unattributed tick is visible AS unattributed.
- M4 Refusals, each naming the node and what was wrong, writing nothing: an unknown ref; an index outside the range; `--section` naming a heading the node does not carry; a node with no checkbox at all. A refusal never leaves a partial write.
- M5 The body write goes through the same atomic replace `_transition` uses — read, edit in memory, atomic replace — so an interrupted run leaves the node either fully old or fully new, never truncated.
- M6 `milestone_done`'s success line names who checked: `… (n/n exit criteria met, checked by <who>[, <who>])`, read from the node's `act: check` stamps; a milestone whose boxes carry no stamp says `checked by hand` rather than inventing a name.
- M7 The verb reaches ANY node type and ANY section — Task `## PLAN`, Milestone `## EXIT`, a Persona — since the human chose reach over the evidence-bound notary design. It never consults a `(← task)` referent and never refuses on WHO is ticking.
- M8 All four engine twins carry the change identically (`add-method/tooling/`, `src/add_method/_bundled/tooling/`, `add-method/.add/tooling/`, this bundle's `.add/tooling/`), and BOTH pins are re-aimed: `ENGINE_MD5` (add.py) and `ENGINE_PKG_MD5` (cli.py).
- M10 Every registry that ENUMERATES the verb set learns the 23rd verb, in the same task that ships it: `tests/engine/test_cli.py`'s WIRED set, the `22-verb kernel` counts in BOTH READMEs, `add-method/README.md`'s CLI row, the book's command-reference table, and `test_shipped_docs.py`'s phantom fixture — which used `add check` precisely BECAUSE no such verb existed, and must now pick a verb that still does not.
- M9 The skill's list of the wired loop surface names `check` in all three live skill trees, within the 176-line SKILL.md pin.
</must>
<reject>
- R:SILENT_TICK A box moved with no `verified:` stamp, or a stamp that names neither a caller nor the `process:check` default. The stamp is the only thing left guarding the goal-gate. -> "SILENT_TICK"
- R:PARTIAL_WRITE A refusal or a crash that leaves some boxes moved, or a node truncated by a non-atomic write. -> "PARTIAL_WRITE"
- R:SILENT_NOOP An out-of-range index, an unknown section or a boxless node treated as success. -> "SILENT_NOOP"
- R:PIN_DRIFT An `add.py` or `cli.py` edit shipped without re-aiming its pin, or landed in fewer than four engine twins. -> "PIN_DRIFT"
- R:STALE_REGISTRY A shipped verb the CLI advertises that any enumerating registry still omits, or a verb count that contradicts `len(cli_verbs())`. -> "STALE_REGISTRY"
- R:BUDGET_BUMP Funding the SKILL.md mention by raising the 176-line pin. -> "BUDGET_BUMP"
- R:GATE_GUARD Adding a refusal based on WHO is ticking, or on whether a `(← task)` referent is done — the human decided against it 2026-08-28; reopening it is a new task, not a build-time judgment call. -> "GATE_GUARD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · the request does not say who may tick a box; taking ANYONE — agent or human, no authority check — per the human's 2026-08-28 choice, with attribution as the only control -> if wrong an agent closes its own milestone and the record shows it did · probe: no code path compares the caller against `authority_for`
- A2 [who] covers: S3 · the request does not say what an unattributed call records; taking the literal `process:check`, never a blank or a guessed human name -> if wrong an agent tick is indistinguishable from a human one, which is the exact failure the stamp exists to prevent · probe: a `check` with no `--by` stamps `process:check`
- A3 [which] covers: S1 · the request does not say which checkbox syntax counts; taking GitHub-flavored `- [ ]` / `- [x]` at line start after optional indent, case-insensitive on the `x`, and nothing else -> if wrong `* [ ]` or `- [X]` boxes are invisible to the verb but visible to `milestone_done`'s tally · probe: the verb's pattern and `milestone_done`'s tally use the SAME compiled pattern
- A4 [which] covers: S1, S2 · the request does not say which sections are eligible; taking every section of every node type -> if wrong the verb refuses a box the user can plainly see · probe: a Task `## PLAN` box ticks as readily as a Milestone `## EXIT` box
- A5 [when] covers: S3 · the request does not say when the stamp lands; taking after a successful write and only then — a refusal stamps nothing -> if wrong the audit trail records ticks that never happened · probe: a refused call leaves `verified:` byte-identical
- A6 [when] covers: S1 · the request does not say when a no-op is a failure; taking never — an already-marked box reports unchanged and exits 0, so re-running a command is safe -> if wrong scripts and retries break on their second run · probe: running the same `check` twice succeeds twice and stamps once
- A7 [absent] covers: S1, S2 · the request does not say what a bare `add check <ref>` with no index means; taking a REFUSAL that lists the node's boxes with their indices, never an implicit `--all` -> if wrong a slip ticks every box in a milestone · probe: no-index is a refusal whose message enumerates the boxes
- A8 [absent] covers: S6 · the request does not say what a node with zero boxes means; taking a refusal naming the node, not a silent success -> if wrong a typo'd ref reports success having done nothing · probe: R:SILENT_NOOP
- A9 [order] covers: S1 · the request does not say how boxes are numbered; taking document order, 1-based, from the top of the body (or of the named section) -> if wrong the index a human reads off the file disagrees with the one the verb uses · probe: index n names the nth box counting down the rendered file
- A10 [order] covers: S1, S5 · the request does not say the order of multiple indices; taking apply-all-or-refuse — every index is validated BEFORE any write, so a bad index in a list writes nothing -> if wrong `check m 1 2 99` half-ticks · probe: R:PARTIAL_WRITE
- A11 [experience] covers: S2 · the request does not say what the operator sees; taking a line per box moved, naming its text, plus the `next:` affordance — the operator should not need to reopen the file to see what changed -> if wrong the verb is trusted blindly, which is worse than the hand edit it replaces · probe: stdout quotes each box's text
- A12 [experience] covers: S4 · the request does not say how the close line reads; taking `checked by <who>` appended to the existing tally sentence, `by hand` when no stamp exists -> if wrong a self-served close reads exactly like a human-affirmed one · probe: closing a milestone whose boxes were ticked by `process:check` says so
- A13 [experience] covers: S6 · the request does not say who reads a guard failure; taking the next engine editor cold — each message names the verb, the node and the expectation -> if wrong the guard gets loosened instead of the engine fixed · probe: every assertion carries a message
- A14 [absent] covers: S4 · the request does not say what `milestone_done` does for a milestone ticked before this verb existed; taking `checked by hand` — the honest reading of no stamp -> if wrong every historical milestone reads as unattributed-agent work · probe: a milestone with no `act: check` stamp closes saying `by hand`
- A36 [who] covers: S7 · the request does not say who maintains the registries; taking this task — a verb and every count of it ship together or the front door lies -> if wrong the READMEs claim 22 while the CLI ships 23 · probe: both README counts read 23
- A37 [which] covers: S7 · the request does not say which registries count; taking the five that FAILED when the verb landed, found by running the suite rather than by grepping -> if wrong a sixth registry rots silently · probe: the full suite is green, not just the new guards
- A38 [when] covers: S7 · the request does not say when they update; taking this same commit -> if wrong a release ships a front door that undercounts · probe: one commit
- A39 [absent] covers: S7 · the request does not say what the phantom fixture should use once `check` is real; taking a verb that does not and will not exist, so the fixture keeps testing the detector rather than the roster -> if wrong the detector test passes vacuously · probe: the fixture's verb is absent from `cli_verbs()`
- A40 [order] covers: S7 · the request does not say the order; taking engine first, registries after — the count is derived from the shipped CLI, never hand-set ahead of it -> if wrong a count is invented · probe: the counts equal `len(cli_verbs())`
- A41 [experience] covers: S7 · the request does not say who reads the counts; taking a prospective adopter at the front door, for whom a wrong number is a trust defect not a typo -> if wrong the README oversells precision it lacks · probe: the number matches the CLI
- A16 [who] covers: S4 · the request does not say whose name the close line shows when several people ticked; taking every distinct checker in stamp order, deduplicated -> if wrong a two-person close credits one · probe: two checkers both appear
- A17 [who] covers: S5 · the request does not say who the skill sentence is for; taking the agent driving the loop, not a human reader — it names the verb where the wired surface is already listed -> if wrong the verb ships undiscoverable · probe: `check` sits in the same sentence as `fold · reopen · deltas`
- A18 [who] covers: S6 · the request does not say who runs the guards; taking plain pytest on both roots, no fixture beyond a tmp bundle -> if wrong the guard passes only on one machine · probe: the guards build their bundle under tmp_path
- A19 [which] covers: S3 · the request does not say which fields the stamp carries; taking by · at · act · authority · boxes, matching the shape every other stamp uses -> if wrong the audit row is unparseable beside its siblings · probe: the stamp's key set matches an existing `act: gate` row
- A20 [which] covers: S4 · the request does not say which stamps feed the close line; taking `act: check` only, ignoring `act: uncheck` — what matters is who left a box marked at close -> if wrong an unticker is credited with the affirmation · probe: an uncheck-then-recheck names the rechecker
- A21 [which] covers: S5 · the request does not say which skill files change; taking only the sentence listing the wired surface, in all three trees — no new section -> if wrong SKILL.md grows past its pin · probe: the diff is one sentence per tree
- A22 [which] covers: S6 · the request does not say which pins move; taking BOTH — `add.py` and `cli.py` are each edited, so `ENGINE_MD5` and `ENGINE_PKG_MD5` both re-aim -> if wrong CI fails at the pin, late · probe: both pin literals change in this task's diff
- A23 [when] covers: S2 · the request does not say when flags are validated; taking argparse first, then index range, then the write — so a flag typo never reaches the file -> if wrong a malformed call partially applies · probe: a bad `--section` refuses before any read of the body
- A24 [when] covers: S4 · the request does not say when the close line reads the stamps; taking at close time from the node itself, never cached -> if wrong a stamp added after the last scan is missed · probe: the clause is computed inside `milestone_done`
- A25 [when] covers: S5 · the request does not say when the skill text ships; taking with this task, not at release — the verb and its mention land together -> if wrong a released engine has an unnamed verb · probe: same commit
- A26 [when] covers: S6 · the request does not say when the pins re-aim; taking LAST, after the engine files are final, since they are md5s of the finished bytes -> if wrong the pin is re-aimed twice and the first is noise · probe: the pins match the committed files
- A27 [absent] covers: S3 · the request does not say what an empty `boxes:` value would mean; taking impossible by construction — no stamp is written when no box moved (M2/M3) -> if wrong the trail records empty ticks · probe: no stamp exists with an empty `boxes:`
- A28 [absent] covers: S5 · the request does not say what a skill tree missing the sentence means; taking FAIL, not skip — all three trees are git-tracked -> if wrong a mirror gap reads as green · probe: an absent sentence is an assertion, not a skip
- A29 [order] covers: S2 · the request does not say the precedence of `--all` against explicit indices; taking a refusal when both are given, rather than silently preferring one -> if wrong the operator's intent is guessed · probe: `--all 2` refuses
- A30 [order] covers: S3 · the request does not say where the stamp lands among existing ones; taking appended last, newest-last, as every other stamp is -> if wrong the audit order lies · probe: the new row follows the prior one
- A31 [order] covers: S4 · the request does not say the order of names in the close line; taking stamp order, oldest first -> if wrong the reading of who affirmed first is wrong · probe: the first checker is named first
- A32 [order] covers: S6 · the request does not say the order of twin mirroring against pin re-aiming; taking mirror the four trees FIRST, then re-aim, so the pin is taken over the final bytes -> if wrong the pin matches a tree that is about to change · probe: A26's probe holds after mirroring
- A33 [experience] covers: S1 · the request does not say what a caller of the library function receives; taking the engine's existing `(node, message)` pair, so `check` composes with every other verb -> if wrong the CLI needs a special case · probe: the return shape matches `milestone_done`'s
- A34 [experience] covers: S3 · the request does not say who reads the stamp; taking a human auditing a close months later — `boxes:` names the section and the indices, not opaque ids -> if wrong the row records that something happened but not what · probe: the value reads `EXIT:1,3`
- A35 [experience] covers: S5 · the request does not say how much skill text this warrants; taking the verb's NAME in the existing list and nothing more — the CLI help carries the flags -> if wrong the always-loaded budget pays for reference material · probe: SKILL.md grows by no full line
- A15 [order] covers: S8 n/a — retired: M8's twin/pin discipline is mechanical and has no ordering question the request could answer.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `add.py` gains `check(root, cid, indices, off=False, section=None, by=None)` beside
  `milestone_done`, sharing ONE compiled box pattern with that function's tally so the two can never
  disagree. It validates every index first, edits the body in memory, writes through the atomic
  replace `_transition` uses, then appends one `verified:` entry. `cli.py` gains the `check`
  subcommand and its dispatch. `milestone_done` grows a `checked by` clause read from the node's
  `act: check` stamps. Skill trees name `check` in the wired-surface sentence. Engine tests cover
  mark · unmark · refusals · atomicity · the stamp · the close line; both MD5 pins re-aimed.
scope: add-method/tooling · add-method/src/add_method/_bundled/tooling · add-method/.add/tooling ·
  add-method/tests · add-method/skill/add · .claude/skills/add ·
  add-method/src/add_method/_bundled/skill/add
strategy (preferred): tests first, red against today's engine (no `check` verb at all). Then `add.py`,
  then `cli.py`, then `milestone_done`'s close line, then the skill sentence; mirror the four engine
  twins with cp; re-aim both pins last, since they are md5s of the finished files. Both roots at the end.
regression floor: `add-method/tests/` AND `add-method/tooling/` green — the second root owns the pins,
  and BOTH will move in this task, so neither root is optional.

## EDGES
- E1 `check m 1 2 99` on a 3-box milestone: 99 is out of range, so NOTHING is written — the guard must assert the file is byte-identical after the refusal, not merely that the exit code is non-zero.
- E2 Ticking the last unchecked box of a milestone: this is the moment the goal-gate falls. It must succeed (the human chose that), stamp, and then `milestone-done` must name the checker.
- E3 A node whose `## EXIT` is present but empty of boxes, versus a node with no `## EXIT` at all — two different refusals, both naming what they looked for.
- E4 `--off` on a box already `- [ ]`: unchanged, exit 0, no stamp.
- E5 A box inside a fenced code block in a node body (the milestone `why:` of THIS task quotes `- [x]`). Document-order indexing must not silently count a quoted example as a real box; if it does, the index a human reads is wrong.
- E6 A body line that is `- [x]` inside `## CLOSE` evidence prose — same class as E5, and the reason the pattern must be anchored rather than loose.

## CHECKS
- test_check_marks_and_unmarks_by_index · covers: M1, A3, A9 · marking box 2 rewrites only that line; `--off` restores it; the file is otherwise byte-identical
- test_check_shares_one_box_pattern_with_the_tally · covers: M1, A3 · the verb and `milestone_done` reference the SAME compiled pattern object, so a syntax either both see or neither does
- test_check_reaches_any_node_and_any_section · covers: M7, A4 · a Task `## PLAN` box and a Milestone `## EXIT` box both tick; `--section` re-indexes from 1 within the named section
- test_check_stamps_exactly_one_verified_entry · covers: M3, A2, A5, A19, A30, A34, R:SILENT_TICK · one stamp per invocation naming the boxes; no `--by` stamps `process:check`; `--off` records `act: uncheck`
- test_check_is_idempotent_and_stamps_nothing_when_nothing_moved · covers: M2, A6, A27, E4 · the second identical run exits 0, reports unchanged, and leaves `verified:` byte-identical
- test_check_refuses_out_of_range_without_writing · covers: M4, M5, A10, E1, R:PARTIAL_WRITE, R:SILENT_NOOP · a bad index in a list writes nothing; the node is byte-identical after the refusal
- test_check_refuses_bare_ref_by_listing_the_boxes · covers: A7 · no index is a refusal whose message enumerates each box with its index — never an implicit `--all`
- test_check_refuses_missing_section_and_boxless_node · covers: M4, A8, E3, R:SILENT_NOOP · two distinct refusals, each naming what it looked for
- test_check_ignores_boxes_inside_fenced_blocks · covers: A3, E5, E6 · a `- [x]` inside a fence is not counted, so the index a human reads off the file is the index the verb uses
- test_milestone_done_names_who_checked · covers: M6, A12, A16, A20, A24, A31, E2 · closing after a `process:check` tick says so in the success line
- test_milestone_done_says_by_hand_without_stamps · covers: M6, A14 · a milestone whose boxes were hand-edited closes saying `checked by hand`, inventing no name
- test_check_never_refuses_on_who · covers: M7, A1, R:GATE_GUARD · no code path in `check` consults `authority_for` or a `(← task)` referent
- test_cli_exposes_check_with_its_flags · covers: M1, A11, A23, A29, A33 · the subcommand parses `<ref> <n>… --all --off --section --by` and stdout quotes the text of each box moved
- test_four_engine_twins_and_both_pins · covers: M8, A22, A26, A32, R:PIN_DRIFT · the four engine trees are byte-identical and both MD5 pins match their files
- test_skill_names_check_in_the_wired_surface · covers: M9, A17, A21, A25, A28, A35, R:BUDGET_BUMP · all three skill trees name `check`; SKILL.md ≤176 lines
- test_every_registry_learned_the_new_verb · covers: M10, A36, A37, A38, A39, A40, A41, R:STALE_REGISTRY · the CLI WIRED set, both README counts, the README CLI row, the book command reference and the phantom fixture all agree with `len(cli_verbs())` — proven by running the five existing guards that enumerate the set, not by reading the diff
- test_check_guard_messages_name_their_target · covers: A13, A18 · every assertion in the new engine guards carries a message naming the verb, node and expectation
red-first: every check MUST fail first — run them against today's engine, which has no `check` verb, before a line of it exists.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
