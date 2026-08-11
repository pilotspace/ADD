---
type: Task
title: Planning loads a persona — intake/loop lens + seeded starter roster
status: done
depth: standard
scope:
  - add-method/skill/add
  - .claude/skills/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/tests/skill
  - .add/personas
gives:
  - S1 `intake.md` § planning lens — the Project/milestone lane loads the best-fit advisor-flow persona before the proposal is drafted, and the confirmed artifact records which
  - S2 `loop.md` § Propose — the next-task proposal loads the same lens before drafting
  - S3 `personas.md` planning reading — planning (intake proposals · milestone drafts · loop proposals) loads through the EXISTING advisor flow; no new vocabulary word
  - S4 the seeded starter roster — two authored personas under the bundle's personas directory, distilled from the teacher, each carrying flow and use-when routing
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:ef6260f10aa51c43" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:3a3edd7b3e012ef9" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-carried-planning.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/persona-carried-planning.d/runs/1.md, brief: "sha256:3a3edd7b3e012ef9" }
advised_by: method-steward
---
## CARD
goal: milestone drafting and next-task proposals are persona-carried — the best-fit lens loads before the plan is drafted, recorded on the artifact — and this bundle finally has a roster to load
why: the beats load lenses but planning never did, so milestone judgment ran bare; and with zero seeded personas even the beat-level loading had nothing to load

## RULES
<must>
- M1 the Project/milestone lane in `intake.md` says: load the best-fit persona whose flow includes advisor BEFORE drafting the milestone proposal, and record the lens on the confirmed artifact (the milestone node carries it via the advise verb)
- M2 the Propose step in `loop.md` says the same lens loads before the next-task proposal is drafted
- M3 `personas.md` documents the planning reading: intake proposals, milestone drafts and loop proposals load through the EXISTING advisor flow — the flow vocabulary stays exactly design · build · advisor · verify
- M4 two starter personas are seeded in the bundle's personas directory, distilled from the teacher corpus (never invented), each with the four machine-readable parts plus flow and use-when frontmatter
- M5 all three git-tracked skill trees stay identical
</must>
<reject>
- R:VOCAB_CREEP a new flow vocabulary word, or any engine edit — planning rides the advisor surface as-is -> "VOCAB_CREEP"
- R:MANDATORY_LENS the load becomes required — a bundle with no personas must keep behaving exactly as before; the additivity promise survives verbatim -> "MANDATORY_LENS"
- R:BUDGET any budget breached — every edited skill file over 350 lines or total surface over 1500 -> "BUDGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who picks the planning lens; taking: the AI, silently, by use-when fit — the human vetoes at the proposal confirm exactly as they veto the lane -> cost: a mis-fit lens colors one proposal
- A2 [who] covers: S4 · the request does not say who confirms the seed; taking: the human at this task's freeze — the drafted personas are shown BEFORE the ask, per seed.md -> cost: none material
- A3 [which] covers: S1, S2 · the request does not say which flow qualifies for planning; taking: advisor (the add-advisor charter IS proposing plans); design also loads where a draft is design-shaped -> cost: none material · probe: personas.md names the reading
- A4 [which] covers: S4 · the request does not say which lenses this repo wants; taking: method-steward (specs · skill docs · budgets · floors — the planning lens) and engine-notary (add.py/cli.py · twins · pins · refusal grammar — the build/verify lens), grounded in what this repo actually is -> cost: a dead-weight persona; pruned at close per personas.md
- A5 [when] covers: S1, S2 · the request does not say when the lens loads; taking: before drafting, not after — a lens applied to a finished draft reviews, it does not carry -> cost: none material
- A6 [when] covers: S4 · the request does not say when seeding may happen; taking: seed.md says "at setup" but the ritual is additive and human-confirmed — seeding mid-project through this task is the same act, later -> cost: none material
- A7 [absent] covers: S1, S2 · the request does not say what a bundle with no personas does at planning; taking: skip silently — the load is by-fit, and no roster means no fit; behavior identical to today -> cost: none material · probe: the additivity check
- A8 [absent] covers: S4 · the request does not say what an unused seeded persona means; taking: a prune candidate at milestone close, personas.md already owns that rule -> cost: none material
- A9 [order] covers: S1, S2, S3 · [order] n/a · a load-before-draft instruction carries no further ordering semantics
- A10 [order] covers: S4 · [order] n/a · two sibling personas with disjoint use-when have no ordering
- A11 [which] covers: S3 · the request does not say which planning surfaces the reading lists; taking: the three that exist — intake proposals, milestone drafts, loop next-task proposals — and no invented fourth -> cost: none material
- A12 [when] covers: S3 · [when] n/a · a documented reading has no timing semantics
- A13 [who] covers: S3 · [who] n/a · the reading binds the skill, not an actor
- A14 [absent] covers: S3 · [absent] n/a · the reading either exists (checked) or the build is not done

## PLAN
contract: S1–S4 as `gives:` — three one-line-ish doc edits + two seeded persona files; no engine edit, no new verb, no vocab change
scope: add-method/skill/add/{intake.md,loop.md,personas.md} → mirrored to the two twin trees · .add/personas/{method-steward,engine-notary}.md · checks in add-method/tests/skill/test_persona_planning.py
strategy: red suite first → intake milestone-lane lens line → loop Propose lens line → personas.md planning reading → seed the two personas via add new Persona + direct authoring → sync twins → green → dogfood: advise THIS task with method-steward
regression floor: add-method/tests/skill (all) + add-method/tooling/test_tree_parity.py stay green

## EDGES
- E1 the additivity promise in personas.md ("opt-in and additive… behaves exactly as before") must survive verbatim — the planning reading extends it, never replaces it
- E2 seeded personas must carry NO invented statistic — success metrics only name numbers the lens can check in-session (line budgets, suite counts, refusal codes)

## CHECKS
- test_intake_milestone_lane_loads_lens · covers: M1, A5 · the Project/milestone lane names the advisor-flow lens load before drafting and the advise record
- test_loop_propose_loads_lens · covers: M2 · the Propose step names the lens load
- test_personas_documents_planning_surface · covers: M3, R:VOCAB_CREEP, A3, A11 · the planning reading names all three surfaces AND the flow vocabulary line is still exactly design · build · advisor · verify
- test_additivity_promise_survives · covers: R:MANDATORY_LENS, A7, E1 · the opt-in/additive promise survives verbatim and the intake line carries the no-roster silent skip
- test_seeded_personas_exist_with_routing · covers: M4, E2 · both persona files exist with flow:, use-when:, the four parts, and no invented percentage statistic
- test_skill_budgets_hold · covers: R:BUDGET · every edited file ≤ 350 lines
- test_skill_bundle_matches_canonical · covers: M5 · canonical and bundled trees byte-identical
- test_dogfood_skill_matches_canonical_when_present · covers: M5 · canonical and dogfood trees identical
- test_total_surface_within_budget · covers: R:BUDGET · total skill surface ≤ 1500 lines
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
