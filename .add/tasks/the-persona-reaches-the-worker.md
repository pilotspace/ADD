---
type: Task
title: an advised persona appears in the brief that spawns the worker
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 add.brief() — the persona block a spawned worker reads
  - S2 the lens resolution shared with advise and wave
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:259be2d4a3f25f67", binding: "sha256:22249aa61fd2594e" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:32e7d6da50b1e35b" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/the-persona-reaches-the-worker.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-02, act: gate, authority: plan, outcome: PASS, receipt: /tasks/the-persona-reaches-the-worker.d/runs/1.md, brief: "sha256:990f9066b283ca06" }
---
## CARD
goal: an advised persona appears in the brief that spawns the worker.
why: measured — no seeded lens has ever reached a brief, by either key.
beat: done · next: add status

## RULES
<must>
- M1 `advise` and `persona:` reach the brief identically
- M2 a brief with no lens says so rather than reading like a lensed one
</must>
<reject>
- R:LENSLOST a recorded lens is dropped between the record and the worker -> "LENSLOST"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A2 [which] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A3 [when] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A4 [absent] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A5 [order] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
- A6 [experience] covers: S1,S2 · the request does not say the plain reading is contested; taking the plain reading -> a re-freeze
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `brief` resolves the roster by persona slug the way `advise` and `wave` do — the path grammar normalised a bare slug against the SOURCE's directory — and reads `advised_by:` as well as `persona:`, the two the gate's R:NOCOVERAGE already treats as equals.
scope: add-method/tooling/, add-method/tests/

## EDGES
- E1 the gate accepts either key; the brief must not accept fewer

## CHECKS
- test_advise_and_persona_reach_the_brief_identically · covers: M1, R:LENSLOST · the measured drop
- test_a_brief_with_no_lens_says_so · covers: M2 · a silent omission reads as a quiet lens
- test_the_gate_and_the_brief_agree_on_what_counts_as_a_lens · covers: M1, E1 · scoped to brief's own body
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- two verbs writing the same fact under different keys is a fact neither can read -> add learn add
