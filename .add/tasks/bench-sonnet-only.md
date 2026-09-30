---
type: Task
title: ADD's benchmark arms run on Sonnet only — the Haiku advisor arm retires and the lean skill keeps Build in the Sonnet session
status: build
kind: change
risks: [measurement-validity]
scope: [benchmark/arms/, benchmark/tests/test_arm_models.py, benchmark/tests/test_arms.py]
gives: [the lean variant as a two-edit Sonnet-only skill]
---
## CARD
goal: every ADD arm runs each beat on one Sonnet model; the lean variant keeps only the two edits that cut work
why: round 6 (Sonnet 5.5, 3 reps) — the Haiku main session never consulted its Sonnet advisor in 6 runs, failed all 3 wm1 apps on Flask/FastAPI, and cost 1.6–1.8× plain add-4 at twice the wall time; the lean arm never handed Build to a Haiku subagent (0 of 6), so that line is dead text

## RULES
- M1 the `add-4-advisor` arm retires: it leaves `ARM_NAMES` and its toml is deleted (from: request — "use sonnet only")
- M2 the lean variant differs from the shipped skill in exactly two places — stub only what the checks import; pick the lead persona by grepping `.add/personas/` — and names no Haiku model; Build and Verify stay in the main session (from: request; PILOT r6 — 0 subagent hand-offs in 6 lean runs)
- M3 an arm that pins a model pins a Sonnet one (from: request — "use sonnet only")
- R:KEEP the `model` / `advisor` arm keys and `run-all --model` stay — `--model claude-sonnet-5-5` needs them (from: .add/tasks/bench-model-switch.md M1–M4)
- R:ARMCOUNT `ARM_NAMES` shrinks from 10 to 9; the fairness fields stay identical across all arms (from: benchmark/tests/test_arms.py::test_all_arms_validate_with_fairness_parity)

## ASSUMPTIONS
- A1 [which] "sonnet only" means the arms and the ADD skill, not the harness plumbing → R:KEEP; the advisor key stays generic and unused
- A2 [experience] round-6 lean data still describes the two-edit variant → the Haiku line was never acted on in 6 runs, so the model saw it but did nothing with it; the report says so

## PLAN
strategy: re-aim C6/C7 of bench-model-switch and add an all-arms Sonnet check (red); delete the advisor toml, drop it from ARM_NAMES, cut the variant's Haiku hand-off back to the shipped Build line
check: python3 -m pytest -q benchmark/tests/test_arm_models.py benchmark/tests/test_arms.py
regression: python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 R:ARMCOUNT · acceptance · benchmark/tests/test_arm_models.py::test_lean_arm_loads_and_advisor_arm_retired · falsifier: the advisor toml deleted but its name still in ARM_NAMES
- C2 covers: M2 · acceptance · benchmark/tests/test_arm_models.py::test_lean_variant_changes_exactly_two_things · falsifier: the Haiku hand-off line survives
- C3 covers: M3 · acceptance · benchmark/tests/test_arm_models.py::test_every_pinned_arm_model_is_sonnet · falsifier: a new arm pins claude-haiku-4-5
- C4 covers: R:KEEP · regression · benchmark/tests/test_arm_models.py::test_argv_carries_model_effort_and_advisor_only_when_set · falsifier: the advisor plumbing removed with the arm
- C5 covers: R:ARMCOUNT · regression · benchmark/tests/test_arms.py::test_all_arms_validate_with_fairness_parity · falsifier: the count left at 10

## LOG

## EVIDENCE
<written once, at verify>
