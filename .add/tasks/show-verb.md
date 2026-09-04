---
type: Task
title: add show reads one node whole, with its neighbourhood to three levels
status: direction
depth: standard
sensitivity: architecture
milestone: okf-graph-lookup
depends_on:
  - /tasks/graph-neighborhood.md
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/README.md
  - README.md
  - add-method/docs/13-command-reference.md
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/engine
  - add-method/tests/skill
gives:
  - S1 <the surface this publishes — an endpoint, function, or section>
generated: { by: add/3.4.0, at: 2026-09-04 }
verified: []
---
## CARD
goal: <one line>
why: <why this task exists — optional>
beat: scaffold · next: author show-verb's RULES, ASSUMPTIONS and CHECKS, then add freeze show-verb

## RULES
<must>
- M1 <the rule that must hold>
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
contract: <the shape this publishes>

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- <test_name> · covers: M1 · <what it proves>
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
