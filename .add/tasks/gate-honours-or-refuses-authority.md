---
type: Task
title: an accepted flag is read or refused, never silently dropped
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tests/engine/
gives:
  - S1 add.claimed_authority() — the shared floor reader
  - S2 the CLI's refusal of `gate --authority`
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:759abd179e53772a", binding: "sha256:b85b43f28c97dd59" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:91956291fd87d0c1" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/gate-honours-or-refuses-authority.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-02, act: gate, authority: plan, outcome: PASS, receipt: /tasks/gate-honours-or-refuses-authority.d/runs/1.md, brief: "sha256:cfe90bfa00117ec2" }
---
## CARD
goal: an accepted flag is read or refused, never silently dropped.
why: measured — `gate --authority human` printed `authority: process`; `freeze --authority process` downgraded a security freeze.
beat: done · next: add status

## RULES
<must>
- M1 `gate --authority` is refused by the CLI rather than parsed and discarded
- M2 frozen M3 is untouched: the engine still computes the gate floor
- M3 `freeze` refuses a claim below the computed floor
- M4 a claim at or above the floor is recorded as given
</must>
<reject>
- R:FLOORDIVE a claim sinks below the floor the node computed for itself -> "FLOORDIVE"
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
contract: One reader, `claimed_authority(claim, floor, verb, slug)`, serves both verbs: a claim may rise above the computed floor, never sink below it. `gate` keeps frozen M3 and the CLI refuses the flag.
scope: add-method/tooling/, add-method/tests/

## EDGES
- E1 an unreadable authority string is refused, not treated as the lowest
- E2 a security floor (`human`) cannot be talked down to `process`

## CHECKS
- test_the_cli_refuses_a_gate_authority_it_will_not_honour · covers: M1, R:FLOORDIVE · the silent drop
- test_the_engine_still_computes_the_gate_floor · covers: M2 · frozen M3 holds
- test_freeze_refuses_an_authority_below_the_computed_floor · covers: M3, E2 · the 3.3.0 hole
- test_freeze_still_accepts_a_claim_at_or_above_the_floor · covers: M4, E1 · claims may rise
- test_freeze_with_no_claim_uses_the_computed_floor · covers: M4 · the default path
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- accepting a flag and discarding it is the one option that misleads -> add learn add
