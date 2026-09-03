---
type: Task
title: the explore scaffold is an explore
status: done
kind: feature
depth: standard
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 the body `new --kind explore` writes
  - S2 the post-create `next:` line an explore is handed
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:17a4045855195cdb", binding: "sha256:ce3302faea043e0b" }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: plan, direction: "sha256:27fd34b1def28232", binding: "sha256:ce3302faea043e0b" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:47463834abd43cd8" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/the-explore-scaffold-is-an-explore.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/the-explore-scaffold-is-an-explore.d/runs/1.md, brief: "sha256:2f773b87316290aa" }
---
## CARD
goal: `new --kind explore` writes the body the explore lane reads, so a freshly scaffolded explore freezes unedited.
why: measured — `--kind explore` emits the identical build-lane body: no `## FINDINGS`, no `budget:` line, and prompts that ask for rules where the lane wants questions. `freeze` then refuses it with R:UNBOUNDED for a `budget:` the scaffold never offered. The lane has real machinery — explore_drift, explore_placeholders, hollow_explore, the sources-receipt gate path — and no front door.

## RULES
<must>
- M1 `new --kind explore` writes a `## FINDINGS` section carrying no finding, which the gate reads and the build body has none of
- M2 the scaffold carries a `budget:` slot in `## PLAN`, the line `freeze` requires
- M3 the RULES prompt asks for a question, not a rule, because a Must in this lane is a question
- M4 `## CHECKS` stays — explore.md keeps it in acceptance form, judged at the gate against FINDINGS
- M5 a non-explore Task's body is byte-for-byte unchanged
- M6 the `next:` an explore is handed names the explore path, not `add run`
</must>
<reject>
- R:UNBUILDABLE a lane's scaffold produces a node that lane's own freeze refuses -> "UNBUILDABLE"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · the body a lane writes is structural; no authority changes which sections a lane reads
- A2 [which] covers: S1, S2 · the request does not say which sections differ; taking explore.md's own list — FINDINGS added, budget required, CHECKS kept in acceptance form -> my first reading had CHECKS and EVIDENCE dropped, which explore.md contradicts in as many words · probe: the explore body still carries ## CHECKS
- A3 [when] covers: S1, S2 · the request does not say whether the budget is seeded with a number or a slot; taking a slot -> a seeded number is a budget nobody chose, and the whole point of the line is that it is a decision · probe: the budget slot is a placeholder, so freeze still refuses until it is filled
- A4 [absent] covers: S1, S2 · the request does not say what "starts empty" means for FINDINGS; taking empty OF FINDINGS while carrying the shape a finding must take, since the `F<n> (answers M<n>) · … · (evidence: <ref>)` form is exacting and the gate refuses anything that misses it -> a blank section teaches the shape to nobody, and a pre-filled one fabricates the answer · probe: the shape hint closes no question, so a fresh explore still gates hollow
- A5 [order] covers: S1, S2 · the request does not say where FINDINGS sits or when the `next:` line changes; taking FINDINGS after CHECKS and before LESSONS, and the `next:` computed at create time from the same `kind` the body branched on -> reading the kind twice from different places is how the two would drift · probe: the explore body and its next line branch on one value
- A6 [experience] covers: S1, S2 · the request does not say who reads the scaffold; taking the author who just chose the explore lane -> being handed a build body and then a refusal for a line it never offered teaches them the lane is broken · probe: a fresh explore freezes after filling only the slots it was given

## PLAN
contract: `new` branches its Task body on `kind == "explore"`: RULES prompts for questions, `## PLAN` carries a `budget:` slot, `## FINDINGS` is present and empty, `## CHECKS` stays in acceptance form. Every other kind is unchanged. The post-create `next:` names the explore path.
scope: add-method/tooling/add.py, add-method/tests/engine/test_the_explore_scaffold_is_an_explore.py

## EDGES
- E1 a Task with no `kind:` at all, which must get the build body
- E2 an explore whose budget slot is left unfilled, which must still be refused

## CHECKS
- test_an_explore_scaffold_carries_findings_and_a_budget · covers: M1, M2, A2, R:UNBUILDABLE · the two missing sections
- test_an_explore_freezes_after_filling_only_what_it_was_given · covers: M2, A6, S2 · the measured refusal, closed
- test_the_rules_prompt_asks_for_a_question · covers: M3, A2 · a Must in this lane is a question
- test_the_explore_body_keeps_its_checks · covers: M4, A2 · explore.md keeps CHECKS in acceptance form
- test_a_non_explore_task_body_is_unchanged · covers: M5, E1 · one lane branched, not the template rewritten
- test_a_fresh_explore_gates_as_hollow · covers: M6, A3, A4, A5, E2 · empty FINDINGS means every question open
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a lane with guards but no scaffold is a lane whose first user meets a refusal instead of a prompt -> add learn method
