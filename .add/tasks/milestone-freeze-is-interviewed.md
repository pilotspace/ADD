---
type: Task
title: a milestone human freeze needs proof the exit criteria were put to a human
status: done
depth: standard
sensitivity: architecture
milestone: loop-that-drains
scope:
  - add-method/tooling
  - add-method/tests
  - add-method/.add/tooling
  - add-method/src/add_method/_bundled/tooling
  - add-method/skill
  - add-method/src/add_method/_bundled/skill
  - .claude/skills/add
  - .add/tooling
gives:
  - S1 `interview` accepts a Milestone — its EXIT criteria compile as open decisions and its sidecar lands beside the milestone, not under tasks
  - S2 the `R:UNINTERVIEWED` rung extended to a Milestone whose freeze CLAIMS human authority while a criterion is unanswered
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:d8ce9001289254a5", binding: "sha256:e08973969f65cf0b" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:380d6d56a56bddb5" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/milestone-freeze-is-interviewed.d/runs/1.md }
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: gate, authority: plan, outcome: PASS, receipt: /tasks/milestone-freeze-is-interviewed.d/runs/1.md, brief: "sha256:dc1074f5a5a7ea45" }
---
## CARD
goal: a human-authority stamp on a milestone is proof a human read the criteria, not proof someone typed a name
why: M34 records a false attestation that cannot be withdrawn. A go-ahead on a RECOMMENDATION was treated as approval of exit criteria written afterwards, the stamp went in at human authority on text no human had seen, and the append-only ledger made it impossible to take back — the correction cost a second stamp and erased nothing. A task at a human floor already has proof-of-conversation; a milestone, which is where the expensive stamp lives, has none. This milestone's own freeze sits at plan authority for exactly that reason.
beat: done · next: add status

## RULES
<must>
- M1 `interview` accepts a Milestone and compiles each `## EXIT` criterion as an open decision, answerable with the same verdicts a task's decisions take
- M2 the interview sidecar is written beside the node it belongs to, so a Milestone's lands under `milestones/` and never under `tasks/`
- M3 `freeze` refuses `R:UNINTERVIEWED` on a Milestone when the freeze CLAIMS human authority and a criterion is unanswered
- M4 a freeze claiming plan or process authority never refuses on the interview: stamping lower is the honest move under a standing go-ahead, not an evasion
- M5 editing a criterion re-opens the interview for that criterion, because the digest is taken over the criteria themselves
- M6 a Milestone with no EXIT criteria has nothing to ask and never refuses
</must>
<reject>
- R:OFFSWITCH the rung must never be silenceable by an argument that makes the claim it guards -> "OFFSWITCH"
- R:TASKSIDECAR a milestone's interview record must never be written into the tasks tree -> "TASKSIDECAR"
- R:STALEANSWER an answer given to one wording must never satisfy a criterion since reworded -> "STALEANSWER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S2 · the request does not say whose claim arms the rung; taking the reading that it is the CLAIMED authority and not the computed floor, inverting the rule the task rung uses — a milestone carries no `sensitivity:` so its computed floor is never human, and keying on the floor would make the rung dead code. Claiming plan authority is a LOWER, honest claim and is exactly what M34 prescribes, so it is not an off switch (this is M4, R:OFFSWITCH) · probe: a freeze at plan authority on an uninterviewed milestone succeeds, and the same freeze at human authority refuses
- A2 [who] covers: S1 · the request does not say who may answer; taking the reading that the engine records the `--by` name verbatim and cannot know a human typed it, exactly as the task interview already states — R:SELFANSWER stays discipline carried by the skill -> claiming otherwise would make the engine assert something it cannot check
- A3 [which] covers: S1 · the request does not say which part of a Milestone is interviewed; taking the reading that it is the `## EXIT` boxes and nothing else — the goal and why are the human's own words, and SCOPE and GROUND are not what a stamp attests · probe: a milestone with an authored goal, why and GROUND but unanswered criteria still has open decisions
- A4 [which] covers: S2 · the request does not say which criteria count; taking the reading that every box counts whether ticked or not, because a ticked box states the criterion was MET and never that a human approved its wording -> reading a tick as an answer would let the goal-gate silently satisfy the interview
- A5 [when] covers: S1, S2 · the request does not say when an answer expires; taking the reading that it expires when the criteria text changes, reusing `interview_digest` unchanged (this is M5, R:STALEANSWER) · probe: rewording one criterion after a full interview re-opens exactly that pass
- A6 [absent] covers: S2 · the request does not say what an absent EXIT section means; taking the reading that nothing to ask is not something to refuse — the same rule the task rung already applies (this is M6) -> refusing a milestone with no criteria would block the scaffold the engine itself writes
- A7 [absent] covers: S1 · the request does not say what an unanswered criterion looks like in the record; taking the reading that it simply does not appear in the answer map, so the sidecar records what was asked and what was answered and never invents a default -> a defaulted answer is the false attestation this task exists to prevent
- A8 [order] covers: S2 · the request does not say where the rung sits; taking the reading that it stays LAST in the freeze ladder, exactly where the task interview already sits, so no human is ever shown an unfinished contract -> moving it earlier would put template text to a person
- A9 [order] covers: S1 · the request does not say what order criteria are asked in; taking the reading that it is document order, because the criteria are a checklist a human reads top to bottom and any other order would fight the file
- A10 [experience] covers: S1 · the receiver is a human being asked to approve a milestone, and what would make this hard is being shown ids without their text; taking the reading that each question renders the criterion in full, as the task interview renders its reading and cost · probe: the compiled questions contain the criterion text, not only its id
- A11 [experience] covers: S2 · the receiver is an agent driving under a standing go-ahead, and what would make this hard is a refusal with no legitimate way forward; taking the reading that the refusal names BOTH exits — interview the human, or stamp at plan authority — so the honest lower claim is visible · probe: the refusal text names plan authority as well as the interview verb

## PLAN
contract: `_open_decisions` gains a Milestone branch compiling each `## EXIT` box as `{id: C<n>, of: criterion}` in document order; `interview_digest`, `interview_gap` and `_answer_map` are reused unchanged, so staleness and folding come for free. `interview`'s sidecar directory is derived from the node's own path rather than hardcoded to `tasks/`. `freeze`'s existing R:UNINTERVIEWED rung gains a second arming condition: the node is a Milestone and the CLAIMED authority is human.
strategy: checks red first, including one that proves the plan-authority path still freezes (the R:OFFSWITCH question cuts both ways and the honest lower claim must stay open). Then the four engine twins, the `engine_pin` re-aim, and the full suite BEFORE the receipt (M32/B-M3).

## EDGES
- E1 a Milestone whose EXIT section is absent or empty freezes at human authority with no interview
- E2 a Milestone fully interviewed, then one criterion reworded, refuses again naming only that criterion
- E3 a criterion already ticked `- [x]` is still an open decision until it is answered
- E4 a Task's interview is unaffected: its sidecar still lands under `tasks/` and its decisions are still its assumptions and rejects
- E5 a Milestone freeze at plan authority succeeds while criteria are unanswered

## CHECKS
- test_interview_compiles_milestone_criteria · covers: M1, A3, A9, A10 · each EXIT box becomes an open decision in document order, the compiled questions carry the criterion text, and an authored goal and GROUND do not satisfy them
- test_the_sidecar_lands_beside_its_node · covers: M2, R:TASKSIDECAR, E4 · a milestone interview writes under `milestones/` and a task interview still writes under `tasks/`
- test_human_claim_refuses_while_criteria_are_unanswered · covers: M3, A4, A11, E3 · a human-authority freeze refuses naming the criteria, a ticked box does not answer one, and the refusal names plan authority as well as the interview verb
- test_a_lower_claim_still_freezes · covers: M4, R:OFFSWITCH, A1, E5 · the same milestone freezes at plan authority, and refuses at human authority, in one test
- test_rewording_a_criterion_reopens_it · covers: M5, R:STALEANSWER, A5, E2 · a fully answered milestone refuses again after one criterion is reworded, naming only that one
- test_nothing_to_ask_is_not_something_to_refuse · covers: M6, A6, E1 · a milestone with no EXIT criteria freezes at human authority
- test_the_record_invents_no_answer · covers: A2, A7 · the sidecar records the `--by` name verbatim and an unanswered criterion appears in neither the answer map nor as a default
- test_the_rung_stays_last · covers: A8 · a milestone that is both unauthored and uninterviewed reports the unauthored slot first
red-first: every check MUST fail first.

## EVIDENCE
receipt: pending
gate: pending

## LESSONS
- pending
