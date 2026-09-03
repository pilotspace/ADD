---
type: Task
title: every task kind routes to a seeded persona
status: done
kind: docs
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/templates/personas
  - add-method/tests/engine/
gives:
  - S1 the starting roster `init` seeds
  - S2 the coverage guard binding the roster to PERSONA_TASK_KINDS
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: human, direction: "sha256:4d00adf3a63a2745", binding: "sha256:ce3302faea043e0b" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:7c633ca9a9506ce3" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/seed-the-missing-lenses.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/seed-the-missing-lenses.d/runs/1.md, brief: "sha256:64e404d55ef31c6a" }
---
## CARD
goal: every kind in the closed taxonomy routes to a seeded lens, and a guard fails when the next one does not.
why: measured — 4 seeded templates covered 6 of 11 kinds. `security` was among the uncovered, and the security gate REFUSES a PASS without a named lens (R:NOCOVERAGE), so a fresh install dead-ended on its first security task. The lens this branch authored to clear that refusal was written into this repo's bundle and never seeded, so the fix did not ship.

## RULES
<must>
- M1 every kind in PERSONA_TASK_KINDS is declared by at least one seeded persona's `task-kinds:`
- M2 the guard enumerates the taxonomy from the constant, so the next kind added fails it
- M3 every seeded persona declares only kinds and flows from the closed taxonomies
- M4 each new lens names the teacher file it was distilled from
- M5 `init` seeds all of them and still never overwrites an edited one
</must>
<reject>
- R:DEADTIER a task kind routes to no lens, so the generic fallback runs and the receipt records no expert -> "DEADTIER"
- R:UNSOURCED a seeded lens claims expertise with no material behind it -> "UNSOURCED"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · a seeded roster is the project's from the moment it lands; `put` never overwrites, so no authority question arises
- A2 [which] covers: S1, S2 · the request does not say which of the five to author; taking all five uncovered kinds — docs, ui, data, security, explore -> a partial seeding leaves the same dead-tier hole with a smaller number on it, and the user chose complete coverage over my recommendation of security-only · probe: the guard passes over the whole taxonomy, not a subset
- A3 [when] covers: S1, S2 · the request does not say where the content comes from, nor when the guard should fail; taking distillation from `personas-teacher/` and a guard that fails at COMMIT rather than at the gate that would have hit the gap -> inventing a lens produces confident prose with nothing behind it, which is worse than an absent lens because it is trusted, and a guard that only fires on a live task discovers the hole from the person it blocked · probe: every seeded lens names its teacher source, and the guard is a test not a doctor finding
- A4 [absent] covers: S1, S2 · the request does not say what a kind with no lens should do; taking the guard as the answer — the absence becomes a failing test, not a silent fallback -> a doctor nudge for a structural gap is a gap · probe: removing a template fails the guard
- A5 [order] covers: S1, S2 · the request does not say which lens wins when several declare a kind; taking the roster selector's existing order, unchanged -> overlap is legitimate (build-craftsman and security-reviewer both take `test`) and narrowing it would be a second decision · probe: overlapping declarations are accepted
- A6 [experience] covers: S1, S2 · the request does not say who reads a seeded lens or the guard's failure; taking the author who inherits the roster on day one, and the maintainer who adds the twelfth kind -> a lens with no `not-when:` cannot be told apart from its siblings and one with no source cannot be judged, and a guard that fails without naming the unclaimed kind sends the maintainer reading nine files · probe: every seeded lens carries not-when and source, and the guard names the kind it could not route

## PLAN
contract: five new persona templates — docs-writer, interface-designer, data-steward, security-reviewer, explore-investigator — each distilled from a named teacher file, seeded by the existing `init` loop with no engine change. A guard enumerates PERSONA_TASK_KINDS and fails when any kind is unclaimed.
scope: add-method/tooling/templates/personas, add-method/tests/engine/test_seed_the_missing_lenses.py

## EDGES
- E1 a kind claimed by two lenses, which is legitimate and must not fail the guard
- E2 a lens declaring a kind or flow outside the closed taxonomy, which doctor already refuses

## CHECKS
- test_every_task_kind_routes_to_a_seeded_lens · covers: M1, A2, A4, R:DEADTIER · the measured 6-of-11
- test_the_guard_enumerates_the_taxonomy · covers: M2, A4 · the next kind added must fail this
- test_every_seeded_lens_declares_only_closed_taxonomy_values · covers: M3, E2 · a lens doctor would refuse is not seeded
- test_every_seeded_lens_names_its_source · covers: M4, A3, A6, R:UNSOURCED · expertise with material behind it
- test_overlapping_claims_are_legitimate · covers: A5, E1 · two lenses may claim one kind
- test_init_seeds_them_all_and_overwrites_none · covers: M5, A1 · the roster is the project's
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a fix authored into this repo's own bundle is not a fix that ships; the seeded template is the artifact -> add learn method
