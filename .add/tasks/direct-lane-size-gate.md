---
type: Task
title: The direct lane is size-gated with an inline checklist; sizing text ships in CLAUDE.md, the skill and the installer pointer
status: done
depth: standard
sensitivity: architecture
milestone: right-sized-lane
scope:
  - .claude/skills/add
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/src/add_method/_installer.py
  - add-method/bin/cli.js
  - add-method/tests
  - CLAUDE.md
gives:
  - S1 `intake.md` §Quick — size-gated admission (floor first), route-and-go, the 5-step inline checklist, the receipt rule, the medium/large mapping
  - S2 the SKILL.md Quick bullet stating the same rule within the 176-line pin
  - S3 this repo's CLAUDE.md ADD block — sizing paragraph, retired verbs removed
  - S4 `_installer.py` `_agent_pointer_block` carrying the sizing sentence
  - S5 `cli.js` `agentPointerBlock` carrying the byte-identical sizing sentence
  - S6 the skill guard `tests/skill/test_quick_lane_size_gate.py`
  - S7 the pointer guard `tests/test_agent_pointer_sizing.py`
  - S8 the routing LADDER — one table, keyed kind x size, whose columns are route · effort+review owed · what persists — rendered in `intake.md`, the CLAUDE.md block and (as one sentence) the pointer twins
generated: { by: add/3.2.0, at: 2026-08-28 }
verified:
  - { by: "Tin Dang", at: 2026-08-28, act: freeze, authority: plan, direction: "sha256:f4cbe506381f6d78" }
  - { by: "Tin Dang", at: 2026-08-28, act: brief, authority: process, brief: "sha256:8258c5ec64fef156" }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: FAIL, receipt: /tasks/direct-lane-size-gate.d/runs/1.md }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/direct-lane-size-gate.d/runs/2.md }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/direct-lane-size-gate.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-08-28, act: refreeze, authority: plan, direction: "sha256:09f68689803b1b3c" }
  - { by: "cli", at: 2026-08-28, act: brief, authority: process, brief: "sha256:5a5b166e2bd92d8e" }
  - { by: "process:run", at: 2026-08-28, act: run, authority: process, outcome: PASS, receipt: /tasks/direct-lane-size-gate.d/runs/4.md }
  - { by: "Tin Dang", at: 2026-08-28, act: gate, authority: plan, outcome: PASS, receipt: /tasks/direct-lane-size-gate.d/runs/4.md, brief: "sha256:5a5b166e2bd92d8e" }
advised_by: method-steward
---
## CARD
goal: Route by KIND and SIZE, and say what each rung OWES: Size-gate the Quick lane — small (≤3 adjacent files, small new behavior allowed) goes direct under an inline 5-step ADD checklist with no node; medium/large size up — every rung carrying its own effort+review and its own persistence, so ceremony falls with size while REVIEW never does; and put that ladder in front of every reader: the skill (3 trees), this repo's CLAUDE.md block, the installer pointer twins.
why: `intake.md` §Quick admits only "behavior the specs already cover" and its discipline is "make the
  edit" — no checklist, no red→green, no invariants, and `intake.md:78` still says the human confirms the
  classification, which contradicts a no-ceremony lane. `CLAUDE.md:13` says "Each task drafts the
  specification bundle" with no sizing at all, and `:8`/`:11` tell the agent to run `add.py status` and
  `add.py guide` — `add.py` prints nothing (it is the library; `cli.py` is the entry) and `guide` is a
  retired verb. The installer pointer (`_installer.py:446`, `cli.js:222`) also says nothing about size.
  Human decisions 2026-08-28: size-based admission, floor closed · route-and-go · inline card + commit +
  mandatory `add learn` trace · ship in skill + CLAUDE.md + installer twins.
beat: done · next: add status

## RULES
<must>
- M1 Quick admits by SIZE: at most ~3 adjacent files, a diff one reviewer reads in one sitting, unknowns tally zero. Small NEW behavior is admitted. It is refused — sizing up to a Task — when the change adds or alters a `gives:` surface anything else consumes, touches frozen scope, or trips the closed floor (security · data · architecture). The floor is checked BEFORE size, in the text's order.
- M2 Quick is route-and-go: the agent states one line `quick: <intent> — <fit>` and proceeds; the human vetoes after ("make it a task" always wins). Task · Explore · Milestone keep the confirm-first rule unchanged.
- M3 Quick carries a 5-step inline checklist, in order: (1) the route line · (2) an inline card in the reply — intent · edges · the check to run · invariants touched — never written under `.add/` · (3) red→green: a behavior change writes or extends its check first and runs it red; a mechanical change runs the existing check · (4) PROJECT.md `invariants:` hold under the bare runtime · (5) the receipt.
- M4 The receipt is the commit (body names the check run and its result) PLUS one `add learn <dd> "…" --evidence <sha>` line — a real lesson when one was learned, otherwise the trace `quick: <intent>`. Every Quick change leaves exactly one learn line.
- M5 Medium and large reuse existing vocabulary: medium = Task `--depth quick`; large = Task `standard|deep` or a Milestone. No new lane, tier, verb or stamp.
- M6 The sizing rule is stated to every reader: the SKILL.md Quick bullet (within the 176-line pin), `intake.md` §Quick, this repo's CLAUDE.md ADD block, and the installer pointer in BOTH twins (`_installer.py`, `cli.js`) with the sizing sentence byte-identical across the twins.
- M7 This repo's CLAUDE.md block names no retired verb: `add.py status`/`add.py guide` become `python3 .add/tooling/cli.py status`; the "Generated by sync-guidelines" trailer goes (the engine no longer injects the block).
- M8 The edit lands in all three live skill trees — `add-method/skill/add/` as source, `.claude/skills/add/` and `_bundled/skill/add/` as mirrors — identical.
- M9 The routing text is a LADDER, not a size threshold: each rung states three things in the same row — the ROUTE (direct · Task `--depth quick|standard|deep` · Task `--kind explore` · Milestone), the EFFORT + REVIEW it owes (self-review · advisor pressure-test at direction · persona-led plan), and WHAT PERSISTS (commit + one learn line · node + frozen contract + run receipt · node + cited FINDINGS · milestone + its tasks). KIND is an axis beside size: mechanical · behavior · unanswered question · theme.
- M10 Effort scales UP with the rung and review NEVER scales down: the ladder states in words that a direct change still runs red->green and still holds `invariants:`, and that skipped ceremony is never skipped review. No rung has an empty review cell.
</must>
<reject>
- R:SIZE_OVER_FLOOR A change admitted to Quick because it is small while it trips the closed floor or consumes a `gives:` surface. Size never outranks the floor. -> "SIZE_OVER_FLOOR"
- R:PERSIST A Quick change writing a node, a run receipt, or any file under `.add/tasks|runs|milestones`. The `add learn` line is the only bundle write. -> "PERSIST"
- R:SILENT_QUICK A Quick change with no route line, no inline card, or no learn line. -> "SILENT_QUICK"
- R:BUDGET_BUMP Funding the SKILL.md bullet by raising the 176-line pin. -> "BUDGET_BUMP"
- R:TWO_TREE Editing fewer than the three live skill trees, or one installer twin without the other. -> "TWO_TREE"
- R:NEW_TIER A new lane name, depth value, verb or stamp for size. -> "NEW_TIER"
- R:CEREMONY_AS_EFFORT A rung whose review or red->green is cut because its ceremony was cut, or a ladder row with an empty effort/review or persistence cell. -> "CEREMONY_AS_EFFORT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who judges size; taking the agent, silently, with the human vetoing after the fact — decided 2026-08-28 -> if wrong the agent under-sizes real work and nobody sees it until the diff · probe: the text names the veto sentence
- A2 [who] covers: S3, S4, S5 · the request does not say who reads the CLAUDE.md/pointer text; taking a non-Claude agent that never loads the skill (Cursor · Codex · Copilot) -> if wrong the sentence is redundant with the skill · probe: the block's sizing sentence stands alone without a skill reference
- A3 [which] covers: S1 · the request does not say what "small" is; taking ≤~3 adjacent files + one-sitting diff + zero contract-shaping unknowns, with small new behavior admitted -> if wrong either trivial edits take a node or a real feature slips through · probe: intake names all three limits
- A4 [which] covers: S6, S7 · the request does not say which tests guard this; taking a skill-tree guard in `add-method/tests/skill/` plus a pointer-twin guard beside `test_npm_pip_parity.py` -> if wrong the rule rots like the Gather cue did · probe: both guards exist and are red first
- A5 [when] covers: S1 · the request does not say when the card is emitted; taking BEFORE the first edit -> if wrong the card is post-hoc narration · probe: the checklist orders card before edit
- A6 [when] covers: S4, S5 · the request does not say whether the pointer sentence must survive the installer re-run; taking yes — it lives inside the marked block so a re-run replaces it in place -> if wrong users on 3.2.x never see it · probe: the sentence is inside `_agent_pointer_block`/`agentPointerBlock`
- A7 [absent] covers: S1 · the request does not say what a Quick change with nothing learned files; taking the mandatory trace line `quick: <intent>` with the commit sha as evidence — decided 2026-08-28 -> if wrong the specs fill with trivia or lose the trail · probe: intake names the trace form
- A8 [absent] covers: S3 · the request does not say what replaces the retired `guide` step; taking removal — `cli.py status` already names the beat -> if wrong a reader loses a step they relied on · probe: no `guide` verb remains in the block
- A9 [order] covers: S1 · the request does not say the order of floor vs size; taking floor first, then contract surface, then size (M1) -> if wrong R:SIZE_OVER_FLOOR is the default reading · probe: the text lists the floor before the size limits
- A10 [order] covers: S2 · the request does not say what funds the SKILL.md lines; taking compression of the existing Quick bullet + adjacent prose, not a pin bump -> if wrong the always-loaded cost grows · probe: line count ≤176 after the edit
- A11 [experience] covers: S1, S2 · the request does not say how the checklist should read for an agent mid-task; taking five numbered steps under 12 lines, each one imperative -> if wrong it is skimmed and skipped · probe: §Quick has exactly five numbered steps
- A12 [experience] covers: S3, S4, S5 · the request does not say how much sizing text a CLAUDE.md reader tolerates; taking one sentence + the floor clause in the pointer, one short paragraph in the repo block -> if wrong the block bloats or under-explains · probe: the pointer sizing text is ≤2 sentences
- A13 [experience] covers: S6, S7 · the request does not say who reads a guard failure; taking the next skill editor cold — the message names the file and the missing element -> if wrong the guard is loosened instead of the text fixed · probe: each assertion message names its target
- A14 [which] covers: S2, S3, S4, S5 · the request does not say which sentences change; taking only the Quick bullet, the block's orient/loop lines and the pointer's status line — every other sentence untouched -> if wrong an unrelated wording pin trips · probe: the diff outside those sentences is empty
- A15 [when] covers: S2, S3 · the request does not say when the reader meets the sizing rule; taking BEFORE the loop text, right after orient -> if wrong the reader has already started the bundle · probe: the sizing text precedes the loop paragraph
- A16 [absent] covers: S2, S4, S5 · the request does not say what a reader who never loads the skill does with medium/large; taking the pointer says "otherwise take a Task" and the skill bullet names `--depth` -> if wrong a Cursor user cannot act on the rule · probe: the pointer names the Task fallback
- A17 [order] covers: S3, S4, S5 · the request does not say where sizing sits among the orient steps; taking after `cli.py status`, before the loop sentence -> if wrong sizing reads as an afterthought · probe: order in the rendered block
- A18 [who] covers: S6, S7 · the request does not say who runs the guards; taking plain pytest in CI on both roots and locally, no fixture beyond repo paths -> if wrong the guard passes only on one machine · probe: the guards import nothing outside the repo
- A19 [when] covers: S6, S7 · the request does not say when the guards run; taking every run against the working tree -> if wrong drift lands between releases · probe: no skip marker in the guards
- A20 [absent] covers: S6, S7 · the request does not say what a missing skill tree means; taking FAIL, not skip — all three trees are git-tracked -> if wrong a mirror gap reads as green · probe: an absent tree is an assertion, not a skip
- A21 [order] covers: S6, S7 · the request does not say guard-first or text-first; taking guards red on the unedited tree first -> if wrong the guards ship never having refused · probe: first run is red naming the missing elements
- A22 [who] covers: S8 · the request does not say who reads the ladder; taking an agent mid-request deciding its own route — not a human planner reading it once -> if wrong the rows are written as policy prose nobody applies at the moment of choice · probe: every rung reads as an instruction the agent can act on without a second document
- A23 [which] covers: S8 · the request does not say which rungs exist; taking exactly four — direct · Task · Task `--kind explore` · Milestone — reusing today's vocabulary -> if wrong a fifth rung becomes a new tier (R:NEW_TIER) · probe: the ladder has four rungs and names no lane word outside those
- A24 [when] covers: S8 · the request does not say when the ladder is consulted; taking after the floor check and BEFORE the first edit, once per request -> if wrong the route is chosen post-hoc to justify work already done · probe: the floor paragraph precedes the table in every rendering
- A25 [absent] covers: S8 · the request does not say what a change fitting no rung does; taking size UP to the next rung ("when in doubt, size up" already stands) -> if wrong an unclassifiable change gets the cheapest rung by default · probe: the size-up sentence survives beside the ladder
- A26 [order] covers: S8 · the request does not say the column order; taking change -> route -> effort+review -> persists, so the cost and the residue are read after the route, never instead of it -> if wrong a reader takes the route and stops · probe: the four columns appear in that order in both renderings
- A27 [experience] covers: S8 · the request does not say the ladder's form; taking a four-row table read in one glance, each cell a phrase not a sentence -> if wrong it becomes prose that is skimmed exactly like the paragraph it replaces · probe: the ladder is a markdown table with four rungs and no cell over ~15 words
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `intake.md` §Quick rewritten — heading kept, admission by size with the floor listed first, the
  route-and-go line, the 5-step checklist, the receipt rule (commit + one mandatory learn line), and a
  one-line medium/large mapping onto `--depth`/Milestone; `intake.md` "What you emit" exempts Quick from
  confirm-first. SKILL.md Quick bullet re-cut to the same rule within 176 lines. This repo's CLAUDE.md block
  gains a sizing paragraph and drops `add.py status`/`add.py guide`/the sync-guidelines trailer. The
  installer pointer gains one byte-identical sizing sentence in both twins. Two guard tests.
scope: .claude/skills/add · add-method/skill/add · add-method/src/add_method/_bundled/skill/add ·
  add-method/src/add_method/_installer.py · add-method/bin/cli.js · add-method/tests · CLAUDE.md
strategy (preferred): guards first, red against the tree as it stands (no size rule, no checklist,
  retired verbs in CLAUDE.md). Then author `intake.md`/SKILL.md in the source tree, mirror with cp, then
  CLAUDE.md, then the two pointer twins. Both test roots at the end.
regression floor: `add-method/tests/` AND `add-method/tooling/` green (two roots — the second holds the
  ENGINE_MD5 pins; `_installer.py` is not `add.py`, so no re-pin is expected — verify, don't assume).

## EDGES
- E1 A one-file change that adds a new `gives:` surface (a new CLI flag another node `needs:`). Small by size, refused by contract — the text must make this the example.
- E2 A Quick change on a security-tagged path (`index.md` `sensitive_paths:`). Floor wins; the text must say the floor is checked first.
- E3 SKILL.md at 172/176: the new bullet must land at ≤176 with the pin untouched (`test_surface.py:36`, `test_uncertainty_routing.py:52`, `test_skill_profile_truth.py:124`).
- E4 `test_retired_verbs_survive_only_inside_the_opaque_marker` strips only the BEGIN marker; the new pointer text must not mention `sync-guidelines`, `add.py migrate` or `add.py guide`.
- E5 The book's `test_part2.py` pins the phrase "specification bundle" in the book, not in CLAUDE.md — the CLAUDE.md rewording is free of that pin; confirm rather than assume.
- E6 The `_bundled/` tree is regenerated by `prepare_bundle.py` at release; a hand `cp` now must match what regeneration would produce (identical files, so it does).

## CHECKS
- test_quick_lane_admits_by_size_with_floor_first · covers: M1, A3, A9, E1, E2, R:SIZE_OVER_FLOOR · §Quick names the three size limits, admits small new behavior, and lists security·data·architecture and the consumed-`gives:` refusal BEFORE the size limits
- test_quick_lane_is_route_and_go · covers: M2, A1 · §Quick carries the `quick: <intent>` route line and the veto sentence; "What you emit" exempts Quick from confirm-first
- test_quick_lane_has_five_step_checklist · covers: M3, A5, A11 · exactly five numbered steps, card before edit, red→green named, invariants named, in ≤12 lines
- test_quick_receipt_is_commit_plus_one_learn_line · covers: M4, A7, R:SILENT_QUICK, R:PERSIST · the receipt names the commit and the mandatory `add learn … --evidence` line with the `quick: <intent>` trace form, and says nothing is written under `.add/tasks|runs`
- test_medium_large_reuse_depth_and_milestone · covers: M5, R:NEW_TIER · §Quick maps medium→`--depth quick`, large→`standard|deep`/Milestone; no new lane heading appears in intake.md
- test_skill_bullet_states_size_rule_within_budget · covers: M6, A10, E3, R:BUDGET_BUMP · SKILL.md Quick bullet names the size rule and the floor; line count ≤176; the pin in the three tests is unchanged
- test_three_skill_trees_identical · covers: M8, A20, E6, R:TWO_TREE · the three live trees are byte-identical
- test_repo_claude_md_states_sizing_and_no_retired_verb · covers: M6, M7, A2, A8, A12, A15, E5 · the ADD block names the sizing rule, `cli.py status`, and contains neither `add.py status`, `add.py guide` nor `Generated by`
- test_installer_pointer_twins_carry_identical_sizing_sentence · covers: M6, A6, A12, A16, E4, R:TWO_TREE · `_agent_pointer_block` and `agentPointerBlock` output contain the same sizing sentence (≤2 sentences), inside the markers, naming no retired verb
- test_ladder_rows_carry_route_effort_and_persistence · covers: M9, A22, A23, A24, A26, A27 · every rung in intake.md and in the CLAUDE.md block names its route, the review it owes, and what persists; the four kinds (mechanical · behavior · question · theme) all appear
- test_review_never_scales_down_with_ceremony · covers: M10, A25, R:CEREMONY_AS_EFFORT · the direct rung names red->green AND `invariants:`; the ladder states that skipped ceremony is not skipped review; no rung's effort/review cell is empty
- test_guards_are_plain_and_unskippable · covers: A4, A18, A19, A21 · neither guard carries a skip marker or an import from outside the repo, so it runs on every machine on every run
- test_untouched_surfaces_kept_their_wording · covers: A14, A17 · every heading outside the edited sentences stands unchanged, and the CLAUDE.md block orders orient -> ladder -> loop
- test_guard_messages_name_their_target · covers: A13 · every assertion in the two new guards carries a message naming file + missing element
red-first: every check MUST fail first. The two guards are run against the unedited tree before any text changes.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
