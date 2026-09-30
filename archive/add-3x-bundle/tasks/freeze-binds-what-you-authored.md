---
type: Task
title: freeze refuses an authored edge or probed assumption no check covers
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
  - S1 the `R:UNCOVERED` rung on `freeze` — a FILLED edge or a PROBED assumption that no CHECKS line covers refuses at direction instead of at the gate
  - S2 the `todo` direction hint's uncovered count, beside the unswept-pairs count it already carries
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:293eeef80b1b7ee5", binding: "sha256:cc10da8e41085e16" }
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: refreeze, authority: plan, direction: "sha256:dd3fa2012839785a", binding: "sha256:cc10da8e41085e16" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:b400ad092d1267ad" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/freeze-binds-what-you-authored.d/runs/1.md }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/freeze-binds-what-you-authored.d/runs/2.md }
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: gate, authority: plan, outcome: PASS, receipt: /tasks/freeze-binds-what-you-authored.d/runs/2.md, brief: "sha256:0d821bfe8e7f665d" }
---
## CARD
goal: the obligation you author is bound before the seal, not discovered after a build and a receipt
why: M31 recorded three tasks in one milestone gating red on an authored edge or a probed assumption with no covering check. M38 recorded the FOURTH, on this very milestone — E1 on orientation-sees-carried-work, caught after a full build, a brief and three receipts. Knowing the lesson and having written it changed nothing, because the gate is the last place in the loop and the cost of learning there is the whole build. The refusal has to move to where the obligation is created.
beat: done · next: add status

## RULES
<must>
- M1 `freeze` refuses `R:UNCOVERED`, naming each id, when a FILLED `E`-numbered edge or a PROBED `A`-numbered assumption appears in no CHECKS `covers:` list
- M2 the enumeration calls the SAME functions `gate` composes into `referents_of` — never a second copy — so the two can never disagree about what an obligation is
- M3 the rung covers filled edges and probed assumptions ONLY: a Must or a Reject with no covering check still freezes, because that blast radius is estimated and not measured
- M4 an untouched template edge line and an assumption declaring no probe are not obligations and never refuse
- M5 the rung sits among the DOCUMENT checks, before the interview rung, so a human is still never shown template text
- M6 `todo` names the uncovered count on a task in direction, beside the unswept-pairs count, using the same computation the refusal uses
</must>
<reject>
- R:SECOND_TRUTH the freeze rung must never enumerate obligations by its own copy of the rule -> "SECOND_TRUTH"
- R:DELETEPAST the refusal must never be cheaper to clear by deleting the obligation than by binding it, so its `next:` names binding first -> "DELETEPAST"
- R:WIDENED the rung must never refuse on a Must or a Reject until that breakage is measured -> "WIDENED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who the refusal is for; taking the reading that it addresses the AUTHOR mid-draft rather than a reviewer, so it names ids and the section to edit and never a person -> a refusal phrased at a reviewer teaches the author nothing
- A2 [which] covers: S1 · the request does not say which depths the rung applies to; taking the reading that it applies at EVERY depth including quick, because the rung adds no work — it moves work earlier — and a quick task that would fail its gate on an uncovered probe should be told while it is still cheap to fix · probe: a quick task with a probed assumption and no covering check refuses at freeze
- A3 [which] covers: S1 · the request does not say which edges count as filled; taking the reading that it is exactly what `edges_of` already returns, the function the gate already trusts (this is M2) · probe: an untouched template edge line does not refuse
- A4 [which] covers: S2 · the request does not say which tasks the hint appears on; taking the reading that it appears only on a task in the direction beat, where the hint already lives, and never on a frozen or building task -> a hint on a sealed node names an edit that would tamper
- A5 [when] covers: S1 · the request does not say where in the ladder the rung sits; taking the reading that it goes immediately after the unswept-pairs refusal — both read the document, both name a section to edit, and the interview stays last so no human is shown an unfinished contract (this is M5) · probe: a node that is both unswept and uncovered reports the unswept pairs first
- A6 [when] covers: S2 · the request does not say when the hint yields to the ones already there; taking the reading that the existing hints keep priority in the order they already have, and the uncovered count appends rather than replaces -> re-ranking a tuned hint chain would change what an author is told first for reasons unrelated to this task
- A7 [absent] covers: S1 · the request does not say what an absent CHECKS section means; taking the reading that absent CHECKS with a filled edge refuses exactly as an incomplete one does, because zero covers: lists cover zero obligations -> exempting the empty case would make deleting the section the way past the rung
- A8 [absent] covers: S2 · the request does not say what to show when the count is zero; taking the reading that nothing is shown, matching the unswept hint's own behaviour -> a `0 uncovered` hint on every clean task is noise in a report tuned for one line per task
- A9 [order] covers: S1 · the request does not say what order the named ids take; taking the reading that they are sorted, exactly as `unbound` sorts the gate's list, so the same node names the same ids in the same order at both ends of the loop
- A10 [order] covers: S2 · n/a — the hint carries a COUNT and not a list, so there is nothing in it to order
- A11 [experience] covers: S1 · the receiver is an author who just wrote an edge, and what would make this hard is a refusal whose cheapest exit is deleting the edge; taking the reading that the `next:` line names writing the check FIRST and retiring the obligation second (this is R:DELETEPAST) · probe: the refusal text names adding a covers: entry before it names any other exit
- A12 [experience] covers: S2 · the receiver is an agent reading `todo` to pick up work, and what would make this hard is a count with no verb; taking the reading that the existing hint format already answers this, because the row it rides names the next verb already -> inventing a second verb hint would widen a line the report keeps to one

## PLAN
contract: one rung in `freeze`, immediately after the unswept-pairs refusal: `sorted(set(edges_of(node_t2) + probed_assumptions(node_t2)) - set(covers(node_t2)))`, refusing `R:UNCOVERED` when non-empty. Those are the same two functions `referents_of` composes, called directly, so there is no second definition of an obligation (M2, R:SECOND_TRUTH). `rules_of` is deliberately NOT called (M3, R:WIDENED). `todo` gains the same computation appended to its existing hint chain.
strategy: checks red first, including one that asserts the rung and the gate agree on a node carrying every shape at once. Then the four engine twins, the `engine_pin` re-aim, and the full suite BEFORE the receipt — this task edits `freeze`, which two suites grep the source of (M32).

## EDGES
- E1 a node whose CHECKS section is entirely absent, with one filled edge, refuses
- E2 a node whose only edge line is the untouched template placeholder freezes clean
- E3 a node that is both unswept and uncovered reports the unswept pairs, not the uncovered ids
- E4 a node with an uncovered Must and no uncovered edge or probe freezes clean
- E5 a quick-depth node with a probed assumption and no covering check refuses

## CHECKS
- test_freeze_refuses_an_uncovered_edge · covers: M1, R:DELETEPAST, A9, A11, E1 · a filled edge with no covers: refuses R:UNCOVERED naming the id, the ids are sorted, and the next: line names adding a covers: entry before any other exit
- test_freeze_refuses_an_uncovered_probe · covers: M1, A2, E5 · a probed assumption with no covers: refuses, at standard depth and at quick depth alike
- test_the_rung_and_the_gate_agree · covers: M2, R:SECOND_TRUTH · on a node carrying a filled edge and a probed assumption, the ids the freeze rung names are exactly the edge-and-probe subset of what `referents_of` returns
- test_the_rung_does_not_widen_to_musts · covers: M3, R:WIDENED, E4 · a Must with no covering check freezes clean, and the refusal never names an M id
- test_a_template_edge_is_not_an_obligation · covers: M4, A3, E2 · an untouched template edge line and an assumption with no probe both freeze clean
- test_the_unswept_refusal_still_comes_first · covers: M5, A5, E3 · a node both unswept and uncovered reports the unswept pairs, and the interview rung still runs last
- test_todo_names_the_uncovered_count · covers: M6, A4, A6, A8 · a task in direction shows the count beside the existing hints, a clean task shows nothing, and a frozen task shows no uncovered hint at all
- test_an_absent_checks_section_still_refuses · covers: A7 · a node with a filled edge and no CHECKS section at all refuses rather than passing on the empty case
- test_the_refusal_addresses_the_author · covers: A1, A12 · the refusal names the section to edit and no person, and the todo hint adds no second verb to its row
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/freeze-binds-what-you-authored.d/runs/2.md · kind: test-ids · 23/23 reported · exit 0 · 2026-09-08
gate: PASS · authority plan · by plan:loop-that-drains · receipt /tasks/freeze-binds-what-you-authored.d/runs/2.md · 2026-09-08

## LESSONS
- pending
- [quality · Q25 · folded] a parametrized check binds NOTHING and neither does a module: JUnit reports a parametrized case as name[param], and the gate resolves a covers: citation by the BARE function name, so freeze-binds-what-you-authored gated red on A2 and E5 while its own tests were green. Cite one plain test function and loop its cases from a module constant inside the body. (evidence: /tasks/freeze-binds-what-you-authored.md — gate refused 'no reported passing check: A2, E5' on test_freeze_refuses_an_uncovered_probe[standard]/[quick], green after de-parametrizing)
