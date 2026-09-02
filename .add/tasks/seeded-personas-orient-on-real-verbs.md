---
type: Task
title: a seeded lens orients with commands the engine actually has
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/
gives:
  - S1 the four seeded persona templates' ORIENT commands
  - S2 a census binding every shipped template
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:35db12f4a9700399", binding: "sha256:22249aa61fd2594e" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:210e814c4d7b7acb" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/seeded-personas-orient-on-real-verbs.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-02, act: gate, authority: plan, outcome: PASS, receipt: /tasks/seeded-personas-orient-on-real-verbs.d/runs/1.md, brief: "sha256:51f17f14d6a291af" }
---
## CARD
goal: a seeded lens orients with commands the engine actually has.
why: measured — `add.py status --all` exits 0 with NO output; a planner reads that as a clean bundle.
beat: done · next: add status

## RULES
<must>
- M1 every command a persona names is a real verb
- M2 no persona drives the library instead of the entrypoint
- M3 every ORIENT command parses and runs clean
</must>
<reject>
- R:SILENTORIENT a lens orients on an empty string and reads it as a clean bundle -> "SILENTORIENT"
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
contract: Every template points at `cli.py` and real verbs, under a census over the shipped templates so a lens added later cannot skip it.
scope: add-method/tooling/, add-method/tests/

## EDGES
- E1 a real verb with a flag that does not parse (`status --brief`)

## CHECKS
- test_every_command_a_persona_names_is_a_real_verb · covers: M1 · a census, never a hand list
- test_no_persona_drives_the_library_instead_of_the_entrypoint · covers: M2, R:SILENTORIENT · the silent shape
- test_the_library_really_is_silent · covers: M2 · the premise, executed
- test_every_orient_command_runs_clean · covers: M3, E1 · flags parse too
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- an instruction that fails silently is worse than one that errors -> add learn add
