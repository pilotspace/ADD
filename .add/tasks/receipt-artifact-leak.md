---
type: Task
title: the receipt artifact leaks into the repo root
status: direction
depth: standard
milestone: all-domain-evidence
scope:
  - .gitignore
  - add-method/skill/add
  - add-method/docs
  - add-method/GETTING-STARTED.md
gives:
  - S1 <the surface this publishes — an endpoint, function, or section>
generated: { by: add/3.1.0, at: 2026-08-12 }
verified: []
---
## CARD
goal: following the documented receipt command must not leave an untracked artifact in the repo root
why: `r.xml` is gitignored nowhere, and the cookbook every agent copies writes it to CWD — so the next `git add -A` commits a JUnit report. Hit live during domain-evidence-recipe; the artifact reached the index and had to be force-removed.
ground: the leak is 9 source files, not one line — SKILL.md (2 lines), phases/verify.md, domains.md across THREE skill trees, plus GETTING-STARTED.md and docs/{05-verify,13-command-reference,17-components,appendix-d-worked-example}.md. domains.md propagated it: the ref shipped one task ago already tells readers to write r.xml.
order: MUST settle before or with `skill-pointer-truth` — both edit SKILL.md, and the milestone's tasks are otherwise scope-disjoint.
beat: direction · next: add freeze receipt-artifact-leak

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
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: <the shape this publishes>
scope: <files>

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
