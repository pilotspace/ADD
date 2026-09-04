---
type: Task
title: status, locate and brief stop spending bytes on what a reader cannot act on
status: done
depth: standard
milestone: read-cost
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - .add/tooling/add.py
  - .add/tooling/cli.py
  - add-method/.add/tooling/add.py
  - add-method/.add/tooling/cli.py
  - add-method/docs/13-command-reference.md
  - add-method/tests/engine

gives:
  - S1 add.status(...)'s bare report — the rows a reader cannot act on are summarised, and `--all` still shows them
  - S2 add.locate(...)'s owner list — open owners in full, closed owners counted, and a flag to see them all
  - S3 add.brief(...)'s ref blocks — a section whose body is only an unauthored placeholder is not compiled into the prompt
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:read-cost", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:6736ec90cd0cecef", binding: "sha256:bd1235c2e1600e93" }
  - { by: "builder", at: 2026-09-04, act: replan, authority: process, note: "two checks owned by other tasks asserted the behaviour this contract deliberately changed: test_non_beat_node_types_are_unchanged read the bare status report, and test_brief_includes_bind_sections found only the placeholder D1 named as noise. Both were re-aimed at what they actually prove (--all, and an AUTHORED bind section) — neither claim was weakened." }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/output-trims.d/runs/1.md }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:0b0346c3dccc100c" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/output-trims.d/runs/2.md }
  - { by: "plan:read-cost", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:308ad25589eae20f", binding: "sha256:bd1235c2e1600e93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:8c479680a1c965cd" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/output-trims.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-09-04, act: gate, authority: process, outcome: PASS, receipt: /tasks/output-trims.d/runs/3.md, brief: "sha256:8c479680a1c965cd" }
---
## CARD
goal: three verbs stop spending a reader's context on what that reader cannot act on, and each cut names what is lost.
why: measured. `status` prints 9 rows carrying `[—]` — the five specs and the seeded personas — that never change and that no reader acts on; they are 53% of the bare report. `locate add.py` lists 50 owners of which 48 are `[done]`: the answer to "who owns this file" is the two that are open, and the other 48 are 93% of the output. `brief` compiles five `<ref>` blocks whose bodies are only the unauthored placeholder `- <the first decision that constrains the rest>` into EVERY brief — already filed as D1. None of these is the big win; the big win was the previous two tasks. These are the measured remainder, and each one has to name what a reader loses or it is a regression wearing a saving's clothes.
beat: done · next: add status

## RULES
<must>
- M1 `status`' bare report summarises the constant rows instead of listing them, and says how to see them
- M2 `--all` still lists every row it lists today, unchanged
- M3 `locate` shows every OPEN owner in full and reports closed owners as a count
- M4 `locate` has a way to show the closed owners, named in its own output
- M5 `brief` omits a ref block whose body is only an unauthored placeholder, and says nothing changed for a block that has real content
- M6 each cut is measured before and after and recorded
</must>
<reject>
- M7 no verb becomes SILENT about a state a reader must act on — an open node, a finding, a refusal -> not a reject, see below
- R:HIDDENSTATE a trim must never remove a row describing something a reader has to act on -> "HIDDENSTATE"
- R:NOWAYBACK a trim must never make information unreachable; every collapse names the flag that expands it -> "NOWAYBACK"
- R:PLACEHOLDERLOSS `brief` must not drop a section that has real content, however short -> "PLACEHOLDERLOSS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · three read-only render changes; no stamp, no floor, no authority, no write path
- A2 [which] covers: S1 · the request does not say which rows are constant; taking a node with NO `status:` whose type is Spec or Persona — those are the seeded lenses, they carry no lifecycle, and 135 of 220 nodes carrying no status was already measured · probe: the bare report's `[—]` rows are exactly the specs and personas -> if wrong, a node with real state is summarised away
- A3 [which] covers: S2 · the request does not say which owners are collapsed; taking `done` only — an archived or reopened node is not settled and stays visible -> if wrong, a reopened owner disappears from the answer to who owns this file
- A4 [which] covers: S3 · the request does not say which blocks are placeholders; taking a body that is ONLY the scaffold text the templates ship, never a short authored one (R:PLACEHOLDERLOSS) -> if wrong, a terse but real decision is dropped from every brief
- A5 [when] covers: S1 S2 · the request does not say when the full list appears; taking an explicit flag, so the default is the common case and the complete answer is one keystroke away -> if wrong, a reader who needs everything cannot get it
- A6 [when] covers: S3 · the request does not say when the omission is decided; taking COMPILE time from the section body as it stands, never a cached judgement -> if wrong, a block authored after the cache is still omitted
- A7 [absent] covers: S1 S2 · the request does not say what happens when there is nothing to collapse; taking the output UNCHANGED, with no summary line about hiding nothing -> if wrong, every small bundle grows a line reporting zero
- A8 [absent] covers: S3 · the request does not say what an absent section is; taking the existing behaviour unchanged — this omits an unauthored PRESENT section, it does not change how a missing one is handled -> if wrong, two different absences print one message
- A9 [order] covers: S1 S2 S3 · the request does not say what order survives; taking every existing order UNCHANGED — these remove rows, they never re-rank the ones that stay -> if wrong, a trim silently re-sorts and a reader cannot diff two runs
- A10 [experience] covers: S1 S2 · the receiver is an agent paying context every turn AND a human orienting; what would make it hard is a complete answer they cannot get back, so every collapse names its flag in its own output (R:NOWAYBACK) -> if wrong, the saving costs a second command to undo
- A11 [experience] covers: S3 · the receiver is a worker reading a brief; what would make it hard is five lines of scaffold text presented as decisions that bind -> if wrong, the brief keeps teaching that a placeholder is a constraint

## PLAN
contract: `status` groups status-less Spec and Persona rows into one summary line naming `--all`. `locate` lists open owners and counts closed ones, naming the flag that shows them. `brief` skips a ref block whose body matches the shipped placeholder. Each is measured before and after.
strategy: measure first, then cut, then re-measure — and write the R:NOWAYBACK check before any trim, so no collapse can ship without its way back.

## EDGES
- E1 a bundle with no constant rows prints no summary line
- E2 a file with only open owners prints no count line
- E3 a ref block with real content is compiled unchanged
- E4 a ref block with a placeholder body is omitted, and the brief still names the section
- E5 `--all` output is byte-identical to today's

## CHECKS
- test_every_collapse_names_its_way_back · covers: R:NOWAYBACK, M4, A10 · each summary line names the flag that expands it
- test_status_summarises_only_constant_rows · covers: M1, A2, R:HIDDENSTATE · a node carrying a status is never summarised away
- test_status_all_is_unchanged · covers: M2, E5 · `--all` lists what it lists today
- test_locate_shows_open_owners_in_full · covers: M3, A3 · every open owner appears; closed ones are counted
- test_brief_omits_only_placeholder_blocks · covers: M5, R:PLACEHOLDERLOSS, E3, E4, A4 · a real block survives, a placeholder block does not
- test_nothing_to_collapse_prints_no_line · covers: E1, E2, A7 · a small bundle grows no line reporting zero
- test_order_is_unchanged · covers: A9 · surviving rows keep their order
- test_the_trims_are_measured · covers: M6, A5 · the before and after are recorded and the after is smaller
- test_no_actionable_state_went_silent · covers: M7 · an open task, a finding and a refusal all still reach the reader
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
