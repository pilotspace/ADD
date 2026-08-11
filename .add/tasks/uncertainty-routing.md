---
type: Task
title: Intake third axis — unknowns score; lane+depth as decision output
status: done
depth: standard
milestone: dynamic-flow
depends_on:
  - /tasks/explore-lane.md
needs:
  - /tasks/explore-lane.md#gives
scope:
  - add-method/skill/add
  - .claude/skills/add
  - add-method/src/add_method/_bundled/skill/add
  - add-method/tests/skill
gives:
  - S1 `intake.md` § shape-read — an explicit unknowns tally as a numbered step of reading the request into shape
  - S2 `intake.md` routing rule — uncertainty dominates size, high unknowns route Explore-first, the sensitivity floor still dominates everything
  - S3 the intake classification shape — the emitted proposal names lane, depth AND the unknowns rationale, as one decision output the human vetoes
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:9ecfab06cd2c207b" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:37a127c948dec436" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/uncertainty-routing.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/uncertainty-routing.d/runs/1.md, brief: "sha256:37a127c948dec436" }
---
## CARD
goal: intake routes on how much is UNKNOWN, not just how big or how sensitive — the unknowns are tallied explicitly and lane + depth are emitted as one vetoable decision output
why: routing today is structural (size · sensitivity); a high-unknowns request gets a frozen contract on a guess because nothing measures the guessing

## RULES
<must>
- M1 `intake.md` adds an explicit unknowns step to the shape-read: tally the unknowns — every named-unstated item or unmeasurable latent requirement whose answer would change the contract shape counts as one
- M2 `intake.md` states the routing rule: high unknowns route Explore-first whatever the size; on a lane tie, uncertainty dominates size (the reading the explore-lane contract froze)
- M3 the emitted classification carries lane, depth AND rationale naming the unknowns tally — depth becomes a decision output the human vetoes, never a silent constant
- M4 all three git-tracked skill trees stay identical
</must>
<reject>
- R:FLOOR_UNDERCUT uncertainty scoring never lowers the closed floor — security · data · architecture size up to a real task whatever the tally says -> "FLOOR_UNDERCUT"
- R:BUDGET any budget breached — intake.md over 350 lines, total surface over 1500, SKILL.md over 150 -> "BUDGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who tallies the unknowns; taking: the AI during the shape-read, silently, as the rest of the read already works -> cost: none material
- A2 [who] covers: S2 · the request does not say who applies the routing rule; taking: the AI routes, the human vetoes — the frozen intake pattern -> cost: mis-routes surface at the confirm
- A3 [who] covers: S3 · the request does not say who consumes the classification; taking: the human at the one intake confirm, rendered via gate.md -> cost: none material
- A4 [which] covers: S1 · the request does not say which unknowns count; taking: only ones whose answer would change the contract shape — trivia and build detail do not count -> cost: tally inflation makes everything an explore · probe: intake.md states the counting rule
- A5 [which] covers: S2 · the request does not say where "high" begins; taking: judgment, not a numeric threshold — ONE contract-shaping unknown already justifies explore-first; stated as guidance, never a gate -> cost: inconsistent routing between sessions
- A6 [which] covers: S3 · the request does not say which fields the classification carries; taking: the existing shape (lane · rationale · command) extended with depth — additive, no field removed -> cost: none material
- A7 [when] covers: S1 · the request does not say when the tally happens; taking: during the shape-read, before the lane is judged — the score must exist before it can route -> cost: none material
- A8 [when] covers: S2 · the request does not say the tie order against sensitivity; taking: the closed floor is checked FIRST and always wins; uncertainty only orders the lanes the floor allows -> cost: a floored request mis-lanes · probe: intake.md states floor-first
- A9 [when] covers: S3 · the request does not say when depth is presented; taking: inside the one intake proposal — never a second serialized ask -> cost: ceremony creep
- A10 [absent] covers: S1 · the request does not say what a zero tally means; taking: normal structural routing, unchanged from today -> cost: none material
- A11 [absent] covers: S2 · the request does not say what an explicit research ask with a low tally does; taking: the explicit ask wins — still Explore, the reading the explore-lane contract froze -> cost: none material
- A12 [absent] covers: S3 · the request does not say what an omitted depth means; taking: the proposal always names one; standard is the default it recommends when nothing argues otherwise -> cost: none material
- A13 [order] covers: S1 · [order] n/a · a tally has no ordering semantics
- A14 [order] covers: S2 · [order] n/a · the rule orders lanes, not items; lane order is fixed by the floor-first reading in A8
- A15 [order] covers: S3 · [order] n/a · gate.md already owns option ordering (recommended first)

## PLAN
contract: S1–S3 as `gives:` — one edited doc (`intake.md`), no engine edit, no SKILL.md edit (the router already points at intake)
scope: add-method/skill/add/intake.md → mirrored to the two twin trees; checks in add-method/tests/skill/test_uncertainty_routing.py
strategy: red suite first → extend the shape-read with the unknowns step + counting rule → state the floor-first routing rule → extend the classification line with depth → sync twins → green
regression floor: add-method/tests/skill (all) + add-method/tooling/test_tree_parity.py stay green

## EDGES
- E1 a request that is BOTH floored and high-unknowns — the floor picks the lane family (real task), uncertainty may still argue explore-first inside it; intake must show the floor won
- E2 intake.md line growth — the new step and rule must not push the file past 350 lines

## CHECKS
- test_intake_names_unknowns_tally · covers: M1, A4 · the shape-read carries an unknowns step with the contract-shaping counting rule
- test_intake_routes_high_unknowns_explore_first · covers: M2, A5 · the routing rule is stated — explore-first on high unknowns, uncertainty dominates size
- test_intake_floor_dominates_tally · covers: R:FLOOR_UNDERCUT, A8, E1 · intake.md states the closed floor is checked first and always wins over the tally
- test_intake_classification_carries_depth · covers: M3 · the emitted classification names depth alongside lane and rationale
- test_intake_within_budget · covers: R:BUDGET, E2 · intake.md ≤ 350 lines and SKILL.md untouched at ≤ 150
- test_skill_bundle_matches_canonical · covers: M4 · canonical and bundled trees byte-identical
- test_dogfood_skill_matches_canonical_when_present · covers: M4 · canonical and dogfood trees identical
- test_total_surface_within_budget · covers: R:BUDGET · total skill surface ≤ 1500 lines
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
