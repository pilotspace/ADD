---
type: Task
title: a roadmap of queued tasks is legible without opening every file
status: done
depth: standard
sensitivity: architecture
milestone: rules-that-hold-for-us
scope:
  - add-method/tooling
  - add-method/tests
  - add-method/.add/tooling
  - add-method/src/add_method/_bundled/tooling
  - .add/tooling
gives:
  - S1 the authored `title:` rendered by the orientation verbs — `status` rows and the `show` header
  - S2 the scaffold tally in the `status` headline, beside the open-delta count it already carries
  - S3 `add new --goal`, writing the CARD line, with `new` refusing a field it does not know
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:2078b02dc2d3032f", binding: "sha256:056837997abb52b3" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/a-roadmap-reads-as-a-roadmap.d/runs/1.md }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:50292afa0f2bbf91" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/a-roadmap-reads-as-a-roadmap.d/runs/2.md }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: gate, authority: plan, outcome: PASS, receipt: /tasks/a-roadmap-reads-as-a-roadmap.d/runs/2.md, brief: "sha256:50292afa0f2bbf91" }
  - { by: loop, at: 2026-09-08, act: reopen, to: build, reason: "M4 named the front door (add new has no --goal) but its check exercised only the library; --goal was never wired into cli.py, so the Must was gated on a surface no planner types" }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: refreeze, authority: plan, direction: "sha256:295588f69ae35eb5", binding: "sha256:056837997abb52b3" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:28f4d2fb11ce7a78" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/a-roadmap-reads-as-a-roadmap.d/runs/3.md }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: gate, authority: plan, outcome: PASS, receipt: /tasks/a-roadmap-reads-as-a-roadmap.d/runs/3.md, brief: "sha256:28f4d2fb11ce7a78" }
---
## CARD
goal: a bundle of queued tasks says what it is queuing, from `status` alone, without opening one file
why: a real 40-task roadmap shipped for review with 38 nodes still scaffold. Every engine surface reported it — `doctor` warned 38 times, every `status` row read `[scaffold]`, `todo` said `38 open task(s)` — and the reviewer still concluded the tool had failed, because the ONE field those 40 nodes had authored was their `title:`, and no orientation verb renders it. `search` is the only verb that does. So the roadmap's entire content was invisible, and reading it meant opening forty files. Separately the planner that wrote those titles had nowhere to put the one-line goal it also held: `add new` has no `--goal`, and the library accepts `goal=` and writes it into FRONTMATTER while the CARD keeps its scaffold, leaving two contradicting goal lines in one node.
beat: done · next: add status

## RULES
<must>
- M1 a `status` row carries its node's authored `title:`, truncated to keep the row within one terminal line
- M2 the `show` header carries the node's authored `title:`
- M3 the `status` headline names how many lifecycle nodes are still scaffold, beside the open-delta count, and says nothing when none are
- M4 `add new` accepts `--goal`, which writes the `## CARD` `goal:` line — the place every reader and every guard looks
- M5 `new` REFUSES a field it does not recognise rather than writing it into frontmatter
- M6 a node with no authored title, or a title that is still a slot, renders no title rather than a placeholder
</must>
<reject>
- R:GHOSTFIELD an unrecognised field must never reach frontmatter, where it reads as authored data nothing wrote -> "GHOSTFIELD"
- R:TWOGOALS a seeded goal must never leave a node carrying one authored goal and one scaffold goal -> "TWOGOALS"
- R:T2SCAN the title and the scaffold tally must cost no read above T0 -> "T2SCAN"
- R:ROWBLOAT a row must never exceed one line, and the report must not gain a line -> "ROWBLOAT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who orientation serves; taking the reading that it serves a REVIEWER who has not opened the bundle, not only the agent resuming it — the failure that prompted this task was a reviewer's, and an agent can always run `show` -> tuning only for the agent is what produced forty anonymous rows
- A2 [who] covers: S3 · the request does not say who seeds a goal; taking the reading that it is the PLANNER at creation, which is the only moment the one-line intent exists and has nowhere to go
- A3 [which] covers: S1 · the request does not say which nodes show a title; taking the reading that every listed node does, since a title is authored on every node type the roster creates · probe: a Milestone row and a Task row both carry their title
- A4 [which] covers: S2 · the request does not say which nodes count as scaffold; taking the reading that it is exactly what `doctor` already counts as `unauthored_node` — LIFECYCLE_TYPES standing in their creation scaffold — so the headline and the report can never disagree · probe: the status tally equals the count of `unauthored_node` findings
- A5 [which] covers: S3 · the request does not say which fields `new` should accept; taking the reading that the accepted set is exactly the CLI's flags plus the edge keys it already writes, and everything else refuses · probe: a field outside that set refuses and writes nothing
- A6 [when] covers: S1, S2 · the request does not say when the title is read; taking the reading that it is read at T0 from frontmatter, where it already lives, so orientation stays within its tier (this is R:T2SCAN) · probe: the existing T0 spy sees no read above T0 while titles and the tally are produced
- A7 [when] covers: S3 · the request does not say when `--goal` may be passed; taking the reading that it is creation-only, because after creation the CARD is authored by editing the node like any other section -> a seeding flag that also updates would be a second write path into a section the Direction beat owns
- A8 [absent] covers: S1 · the request does not say what an absent or slot title means; taking the reading that the row renders no title at all rather than a placeholder or an empty column (this is M6) · probe: a node whose title is still a template slot renders no title text
- A9 [absent] covers: S2 · the request does not say what a zero scaffold count means; taking the reading that nothing is shown, matching the open-delta clause's own behaviour -> a `0 scaffold` clause on every healthy bundle is noise in a headline tuned for one line
- A10 [absent] covers: S3 · the request does not say what an absent `--goal` means; taking the reading that the CARD keeps its scaffold exactly as today, so nothing about the current flow changes for a caller that does not pass it
- A11 [order] covers: S2 · the request does not say where the tally sits; taking the reading that it follows the open-delta clause on the same line, because both are counts of carried work and the report must not gain a line (this is R:ROWBLOAT)
- A12 [order] covers: S1 · the request does not say where in a row the title sits; taking the reading that it goes LAST, after slug, beat and type, so the existing columns keep their positions and a guard reading the prefix still reads what it read
- A13 [order] covers: S3 · n/a — `--goal` writes one line into one section; there is no sequence in it to order
- A14 [experience] covers: S1, S2 · the receiver is a reviewer reading a PR diff or a terminal, and what would make this hard is a row that wraps; taking the reading that the title is truncated so the whole row fits a conventional width · probe: no row exceeds 100 characters on a bundle whose titles are long
- A15 [experience] covers: S3 · the receiver is a planner creating a task list, and what would make it hard is a refusal that does not say which fields are legal; taking the reading that the refusal ENUMERATES the accepted set · probe: the unknown-field refusal names the fields it would have accepted

## PLAN
contract: `status`'s row gains a truncated `title:` after the type column and its headline gains a `N scaffold` clause computed from the same predicate `doctor` uses; `show`'s header line gains the title. `new` gains a `--goal` flag that writes the CARD `goal:` line, and validates its `**fields` against an explicit accepted set, refusing anything else with the set named.
strategy: checks red first, including one asserting the status tally and the `doctor` count are the same number on the same bundle — the defect would be two counters disagreeing. Then the four engine twins, the `engine_pin` re-aim, and the full suite before the receipt (B-M3).

## EDGES
- E1 a node whose `title:` is still a template slot renders no title, not a placeholder
- E2 a very long title is truncated so the row stays within one line
- E3 a bundle with zero scaffold nodes shows no tally clause at all
- E4 `add new --goal` leaves exactly ONE goal line in the node, in the CARD
- E5 `new` given an unrecognised field refuses, writes no file, and names the accepted set

## CHECKS
- test_status_rows_carry_their_title · covers: M1, A1, A3, A12, E1 · a Task row and a Milestone row both carry their authored title after the type column, and a slot title renders nothing
- test_status_headline_names_the_scaffold_count · covers: M3, A4, A9, E3 · the headline names the count beside the delta clause, the number equals `doctor`'s `unauthored_node` count, and a fully authored bundle shows no clause
- test_orientation_stays_t0_and_bounded · covers: R:T2SCAN, R:ROWBLOAT, A6, A14, E2 · the T0 spy sees no read above T0, no row exceeds 100 characters with long titles, and the report gains no line
- test_show_header_carries_the_title · covers: M2 · the `show` header line names the node's authored title
- test_the_front_door_takes_the_goal · covers: M4 · `add new --goal` through cli.py argv — the surface a planner actually types, since `add.py` is a library that prints nothing
- test_new_goal_writes_the_card · covers: M4, R:TWOGOALS, A2, A7, A10, E4 · `--goal` writes the CARD line, the node carries exactly one goal line, and omitting the flag leaves today's scaffold untouched
- test_new_refuses_a_field_it_does_not_know · covers: M5, R:GHOSTFIELD, A5, A15, E5 · an unrecognised field refuses, no file is written, and the refusal enumerates the accepted set
- test_a_slot_title_is_not_a_title · covers: M6, A8 · a node whose title is a template slot is treated as untitled by every surface that renders one
red-first: every check MUST fail first.

## EVIDENCE
receipt: pending
gate: pending

## LESSONS
- pending
