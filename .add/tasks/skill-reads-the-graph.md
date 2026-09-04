---
type: Task
title: SKILL.md teaches the graph — read a node whole, query by field, before the loop plans
status: direction
depth: quick
milestone: okf-graph-lookup
depends_on:
  - /tasks/show-verb.md
  - /tasks/search-structured-filters.md
scope:
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
gives:
  - S1 SKILL.md's cookbook and Intake routing — `add show` and `add search`'s field filters named as the read-before-you-plan step, byte-identical across all three shipped skill trees
  - S2 the funding — every added byte paid for by compression inside the existing 176-line and 13258-byte pins, and the prose sha256 pin re-aimed in the same change
  - S3 intake.md — the Task and Project/milestone routes name reading the node and its neighbourhood before drafting scope
generated: { by: add/3.4.0, at: 2026-09-04 }
verified: []
---
## CARD
goal: <one line>
why: <why this task exists — optional>
beat: scaffold · next: author skill-reads-the-graph's RULES, ASSUMPTIONS and CHECKS, then add freeze skill-reads-the-graph

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
