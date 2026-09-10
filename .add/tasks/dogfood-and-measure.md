---
type: Task
title: dogfood evidence-over-tests on real work and decide whether a bench is warranted
status: direction
kind: explore
milestone: evidence-over-tests
scope:
  - .add
gives:
  - S1 <the surface this publishes — an endpoint, function, or section>
generated: { by: add/3.6.0, at: 2026-09-10 }
verified: []
---
## CARD
goal: <one line>
why: <why this task exists — optional>
beat: queued · next: author dogfood-and-measure's RULES, ASSUMPTIONS and CHECKS, then add freeze dogfood-and-measure

## RULES
<must>
- M1 <the question this explore must answer, stated so `answered` is judgeable>
</must>
<reject>
- R:<NAME> <what must never happen> -> "<NAME>"
</reject>

## ASSUMPTIONS
- A1 [who] covers: <S ids> · the request does not say <who may act / whose data>; taking <reading> -> <cost if wrong>
- A2 [which] covers: <S ids> · the request does not say <which rows/cases are in>; taking <reading> -> <cost if wrong>
- A3 [when] covers: <S ids> · the request does not say <where the boundary falls>; taking <reading> -> <cost if wrong>
- A4 [absent] covers: <S ids> · the request does not say <what a missing value means>; taking <reading> -> <cost if wrong>
- A5 [order] covers: <S ids> · the request does not say <what orders / breaks a tie>; taking <reading> -> <cost if wrong>
- A6 [experience] covers: <S ids> · the request does not say <who receives this and what would make it hard for them>; taking <reading> -> <cost if wrong>
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: <what this explore will have settled>
budget: <one hard number — tool calls / sources / wall-clock; the loop stops when it is spent>

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- <acceptance line> · covers: M1 · <what a sufficient answer to M1 looks like>
judged at the gate against ## FINDINGS, not by pytest.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## FINDINGS
<empty until the loop runs — then one line per finding:
 F1 (answers M1) · <what was found> · (evidence: <file:line | url | command>)>

## LESSONS
- <lesson> -> add learn <lens>
