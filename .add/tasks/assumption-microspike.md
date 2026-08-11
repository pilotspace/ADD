---
type: Task
title: direction.md: discharge high-cost assumptions by recorded micro-explore
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
  - S1 `phases/direction.md` § ASSUMPTIONS — the micro-spike discharge rule, turning a priced guess into recorded evidence before freeze
  - S2 the found-line grammar — a discharged assumption carries `found:` plus its evidence ref on the same line, replacing the taken reading, never the line
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "Tin Dang", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:85e0df066d874c7d" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:fe9f73adfa09b264" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/assumption-microspike.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/assumption-microspike.d/runs/1.md, brief: "sha256:fe9f73adfa09b264" }
---
## CARD
goal: an assumption whose cost-if-wrong is high can be discharged before freeze by a bounded, recorded micro-explore — evidence where guessing is expensive, guessing where evidence is not worth its cost
why: the sweep currently forces a priced guess on every silence; the most expensive guesses are exactly the ones a few tool calls could answer

## RULES
<must>
- M1 `phases/direction.md` documents the discharge: a high cost-if-wrong assumption MAY be answered before freeze by a bounded micro-explore — a few targeted tool calls inline, not a task
- M2 the record is on the line: the discharged assumption gains `found:` with the answer and its evidence ref; the line itself stays in ASSUMPTIONS, auditable, never deleted
- M3 the escalation is named: when the question outgrows a few calls, it routes to the Explore lane through intake — the discharge never becomes a shadow research task
- M4 all three git-tracked skill trees stay identical
</must>
<reject>
- R:CEREMONY_CREEP the discharge stays optional — the guide never requires a micro-spike per line, and an undischargeable silence stays a legitimate priced guess -> "CEREMONY_CREEP"
- R:BUDGET direction.md over 350 lines or total surface over 1500 -> "BUDGET"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who runs the micro-explore; taking: the AI, inline during Direction authoring — it adds no approval and moves no seam -> cost: none material
- A2 [who] covers: S2 · the request does not say who may challenge a found-line; taking: the human at freeze, exactly as any assumption — found means evidenced, not settled -> cost: none material
- A3 [which] covers: S1 · the request does not say which assumptions qualify; taking: the author's judgment keyed on cost-if-wrong — highest cost first, checkability second -> cost: effort mis-spent on cheap silences · probe: direction.md keys the rule on cost
- A4 [which] covers: S2 · the request does not say which evidence refs qualify; taking: anything citable — a file+line, a doc, a URL, a command output — the same evidence spirit as learn -> cost: weak refs weaken the audit
- A5 [when] covers: S1 · the request does not say when the discharge happens; taking: during Direction, before freeze — after freeze the same act is Build-time learning, not an assumption edit -> cost: none material
- A6 [when] covers: S2 · the request does not say when a found-line may change; taking: assumption lines stay freely editable (they are unknowns/facts, not rules — the seal never covered them) -> cost: none material
- A7 [absent] covers: S1 · the request does not say what happens when a micro-explore finds nothing; taking: the line stays a priced guess with the reading taken — a failed probe is not a block -> cost: none material
- A8 [absent] covers: S2 · the request does not say what a found-line without an evidence ref means; taking: it is not a discharge — found without evidence is just a louder guess; the guide says so -> cost: fake discharges · probe: direction.md requires the ref
- A9 [order] covers: S1 · the request does not say the discharge order; taking: highest cost-if-wrong first — the same lowest-confidence-first spirit the method already uses -> cost: none material
- A10 [order] covers: S2 · [order] n/a · a line-level grammar carries no ordering semantics

## PLAN
contract: S1–S2 as `gives:` — one edited doc (`phases/direction.md`), no engine edit, no new verb, no freeze-refusal change
scope: add-method/skill/add/phases/direction.md → mirrored to the two twin trees; checks in add-method/tests/skill/test_assumption_microspike.py
strategy: red suite first → add the discharge paragraph to the ASSUMPTIONS section of direction.md (rule · found-grammar · escalation to Explore) → sync twins → green
regression floor: add-method/tests/skill (all) + add-method/tooling/test_tree_parity.py stay green

## EDGES
- E1 the discharge text sits inside the existing ASSUMPTIONS guidance without disturbing the probe grammar the engine's gate already binds
- E2 direction.md is the largest phase guide (129 lines) — the addition must stay well under the 350-line file budget

## CHECKS
- test_direction_documents_microspike_discharge · covers: M1, A3 · the ASSUMPTIONS guidance names the bounded micro-explore discharge, keyed on cost-if-wrong
- test_found_grammar_requires_evidence · covers: M2, A8 · the found-line grammar is documented with its required evidence ref, and the line stays on the record
- test_discharge_escalates_to_explore_lane · covers: M3 · the guide routes an outgrown question to the Explore lane through intake
- test_discharge_stays_optional · covers: R:CEREMONY_CREEP · the guide states the discharge is optional and a priced guess stays legitimate
- test_direction_within_budget · covers: R:BUDGET, E1, E2 · direction.md ≤ 350 lines and the probe grammar line survives verbatim
- test_skill_bundle_matches_canonical · covers: M4 · canonical and bundled trees byte-identical
- test_dogfood_skill_matches_canonical_when_present · covers: M4 · canonical and dogfood trees identical
- test_total_surface_within_budget · covers: R:BUDGET · total skill surface ≤ 1500 lines
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
