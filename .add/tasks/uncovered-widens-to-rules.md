---
type: Task
title: freeze refuses an uncovered Must
status: done
depth: standard
milestone: refuse-in-one-voice
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine/test_uncovered_widens_to_rules.py
  - add-method/tests/engine/test_freeze_binds_what_you_authored.py
  - add-method/tests/engine/test_freeze_seal.py
gives:
  - S1 `freeze`'s R:UNCOVERED rung — which authored obligations it demands a check for before it seals direction
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:refuse-in-one-voice", at: 2026-09-10, act: freeze, authority: process, direction: "sha256:fa1ab2edf36d3316", binding: "sha256:e9a79d98e3503d91" }
  - { by: "plan:refuse-in-one-voice", at: 2026-09-10, act: refreeze, authority: plan, direction: "sha256:fa1ab2edf36d3316", binding: "sha256:e9a79d98e3503d91" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/uncovered-widens-to-rules.d/runs/1.md }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:bc40563d7aeb2aaf" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/uncovered-widens-to-rules.d/runs/2.md }
  - { by: "plan:refuse-in-one-voice", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/uncovered-widens-to-rules.d/runs/2.md, brief: "sha256:bc40563d7aeb2aaf" }
---
## CARD
goal: a Must or a Reject that no check covers is refused at the freeze, when the fix is one line of authoring, not at the gate after the whole build
why: the gate is the wrong place to learn a Must has no check. By then the whole build is done, and the fix is one line of authoring that should have been asked for at the freeze. `uncovered_obligations` already binds edges and probed assumptions and says in its own docstring that Musts and Rejects stay out `until the cost of widening is MEASURED rather than estimated`
beat: done · next: add status

## RULES
<must>
- M1 `freeze` refuses a node whose `## RULES` names a Must or a Reject that no check's `covers:` lists, naming each one
- M2 the rung reuses `referents_of`'s own components — `rules_of` — and never a second reading of what a rule is (R:SECOND_TRUTH)
- M3 the gate's refusal is UNCHANGED: the same obligation refused at freeze is still refused at gate, because a check can be deleted after the seal
- M4 the exemptions the rung already grants are unchanged — an `explore` node has no RULES to cover, and a Milestone is not held to a task's shape
- M5 the refusal names the fix that runs: which ids are uncovered, and the one edit that satisfies them
</must>
<reject>
- R:SECOND_TRUTH the rung reads RULES its own way, so `freeze` and `gate` can disagree about what an obligation is -> "SECOND_TRUTH"
- R:LATEREFUSAL an obligation the engine could have demanded at the freeze is first reported at the gate, after the build -> "LATEREFUSAL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who pays for the widening; taking "the author at the freeze, who is already in the file — the whole point is that they are holding the pen when the engine asks" -> the rung is added and the cost lands on someone who has already moved on
- A2 [which] covers: S1 · the request does not say which nodes the widened rung would newly refuse; taking "none of the existing corpus, because the GATE already enforces this and nothing could ship without it" · found: 0 of 105 nodes carrying RULES in this bundle have an uncovered Must or Reject; 21 carry no RULES at all and are untouched (evidence: rules_of/covers over `.add`, run at direction) -> a rung is shipped that refuses a hundred sealed nodes and gets reverted the first time someone re-freezes one
- A3 [when] covers: S1 · the request does not say when the two rungs may disagree; taking "never at the same instant, but freeze runs EARLIER, so a check deleted between freeze and gate must still be caught at the gate — the gate rung stays exactly as it is (M3)" -> the gate rung is removed as redundant and a post-seal deletion ships uncaught
- A4 [absent] covers: S1 · the request does not say what a node with NO RULES means; taking "nothing to cover, so nothing to refuse — an explore node and a scaffold alike pass this rung untouched, and the 21 such nodes measured above prove the case is real" -> a node with no rules is refused for failing to cover rules it does not have
- A5 [order] covers: S1 · the request does not say where the rung sits among freeze's ten; taking "with the existing R:UNCOVERED rung, extending it rather than adding an eleventh — one refusal listing every uncovered obligation beats two refusals a re-run apart" -> the author fixes the edges, re-freezes, and is then told about the Musts
- A6 [experience] covers: S1 · the request does not say what the widened message says; taking "one list, with the ids grouped by what they are, and the single `covers:` edit that satisfies them — identical in shape to what the rung already prints for edges" -> the author learns two vocabularies for one refusal

## PLAN
contract: `uncovered_obligations` adds `rules_of(node)` to the set it already builds from `edges_of` and `probed_assumptions` — the third component of `referents_of`, so the freeze rung and the gate rung read one definition (M2 · R:SECOND_TRUTH). Nothing else moves: the rung's position, its exemptions and the gate's own check are untouched. The docstring's deferral is replaced by the measurement that discharged it.
strategy: measure first (done, at direction: 0 of 105), then one line, then the checks that pin the exemptions.

## EDGES
- E1 a node whose Musts are covered but whose Reject is not — the reject is an obligation exactly as a Must is
- E2 an `explore` node — exempt from the rung, and must stay exempt
- E3 a Milestone — carries no `## RULES` in a task's shape, and must not be refused for it
- E4 a node that passes freeze, then has its check deleted before the gate — the gate must still refuse it (M3)

## CHECKS
- test_freeze_refuses_an_uncovered_must · covers: M1, M2, M5, R:LATEREFUSAL, A5, A6, E1 · a Must and a Reject with no covering check are both named in one refusal, at the freeze
- test_the_rung_reads_one_definition_of_a_rule · covers: M2, R:SECOND_TRUTH · the freeze rung and the gate resolve the same ids for the same node, driven through both
- test_the_exemptions_are_unchanged · covers: M4, A4, E2, E3 · an explore node, a Milestone and a node with no RULES all pass the rung
- test_the_gate_still_refuses_a_deleted_check · covers: M3, A3, E4 · a node frozen clean, then stripped of the check, is refused at the gate
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/uncovered-widens-to-rules.d/runs/2.md · kind: test-ids · 24/24 reported · exit 0 · 2026-09-10
gate: PASS · authority process · by plan:refuse-in-one-voice · receipt /tasks/uncovered-widens-to-rules.d/runs/2.md · 2026-09-10

## LESSONS
- [method · M46 · folded] A rung held NARROW 'until the cost is measured' is a debt with a due date. When the measurement lands, retire the check that asserts the narrowing — kept, it asserts against its own condition being met. (evidence: /tasks/uncovered-widens-to-rules.md)
- [quality · Q33 · folded] A check that pins a COUNT (`1 uncovered`) is pinned to its fixture's shape as much as to the rule. Widen the producer and the count moves — the repair is to re-aim the FIXTURE so the number is again about one thing, never to edit the expected number. (evidence: /tasks/uncovered-widens-to-rules.md)
