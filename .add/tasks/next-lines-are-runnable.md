---
type: Task
title: every next
status: done
depth: standard
sensitivity: architecture
scope:
  - line is a command that runs and clears what it was named for:add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tests/engine/
gives:
  - S1 BEAT_NEXT — the table every next: line is read from
  - S2 the refusals that name a fix (stale receipt, unknown lens, missing ref)
generated: { by: add/3.3.0, at: 2026-09-02 }
verified:
  - { by: "Tin Dang", at: 2026-09-02, act: freeze, authority: human, direction: "sha256:cbb9ddfc431e4a4a", binding: "sha256:22249aa61fd2594e" }
  - { by: "Tin Dang", at: 2026-09-02, act: brief, authority: process, brief: "sha256:78fb840292191435" }
  - { by: "process:run", at: 2026-09-02, act: run, authority: process, outcome: PASS, receipt: /tasks/next-lines-are-runnable.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-02, act: gate, authority: plan, outcome: PASS, receipt: /tasks/next-lines-are-runnable.d/runs/1.md, brief: "sha256:8e8f5257d0c2f2e6" }
---
## CARD
goal: every `next:` line is a command that runs and clears what it was named for.
why: measured — the build hint guaranteed `ids: unknown` and the gate then named RISK-ACCEPTED as the only exit.
beat: done · next: add status

## RULES
<must>
- M1 the build hint names the canonical double-`--junitxml` idiom
- M2 every `add <verb>` a hint names is a real verb whose flags parse
- M3 a receipt with no ids is not answered with a waiver alone
- M4 the non-git freshness refusal names `git init`
- M5 a closed vocabulary is named when a value falls outside it
- M6 no verb raises at the operator on a missing ref
</must>
<reject>
- R:DEADEND a refusal names a fix that cannot clear the state it was printed for -> "DEADEND"
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
contract: `BEAT_NEXT` carries the canonical run idiom (braces doubled for `.format`) and a runnable gate line; the stale-receipt, unknown-lens and `check --all` paths each name a fix that works.
scope: add-method/tooling/, add-method/tests/

## EDGES
- E1 a non-git bundle, where re-running `add run` loops forever

## CHECKS
- test_the_build_next_names_the_canonical_junit_idiom · covers: M1 · bindable evidence
- test_the_verify_next_is_a_runnable_command · covers: M2 · not an argparse error
- test_every_beat_next_starts_with_a_real_verb · covers: M2, R:DEADEND · a census over the table
- test_an_unbound_gate_names_the_run_idiom_when_the_receipt_carries_no_ids · covers: M3 · no false waiver
- test_the_non_git_freshness_refusal_names_git_init · covers: M4, E1 · the unbounded loop
- test_an_unknown_lens_names_the_closed_set · covers: M5 · name the vocabulary
- test_no_verb_tracebacks_on_a_missing_ref · covers: M6 · records or refuses, never crashes
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- one table feeds fourteen call sites; a wrong idiom there is wrong everywhere -> add learn add
