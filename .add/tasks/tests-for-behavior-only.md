---
type: Task
title: Quick skips the test only when no behavior changes; every bug fix keeps its test
status: done
kind: method
fixes: important-tests-only@f79c0925
risks: [method-drift, skipped-verification]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_tests_for_behavior_only.py, add-method/tests/test_important_tests_only.py, add-method/CHANGELOG.md, README.md, add-method/README.md, benchmark/results/]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: a change with no new behavior is made without a new test; a change to behavior keeps the test the measured skill required · why: the dev re-measure of important-tests-only resolved 78 of 101 against 83 for the measured skill and 80 for vanilla (2 gained, 7 lost, p = 0.18) for a 6% saving. Owner 2026-10-08: "Narrow it, then ship"

## RULES
- M1 a change to behavior (a bug fix, a new case) gets a test: the request's own example and the most plausible wrong fix's case, watched failing first (from: value-final M1 — the measured rule, restored)
- M2 a change with no new behavior (typo, rename, comment or docs, a config value, making an already-failing test pass) needs no new test (from: owner 2026-10-07/08; probe in important-tests-only EVIDENCE)
- M3 either way the suite runs and the diff is reviewed; the record names the path: `red→green: <test>` or `test: none — <what covers it>` (from: important-tests-only M3, M4, kept)
- M4 the "important" rule is gone from the skill: the agent no longer judges whether a bug fix deserves a test (from: the re-measure)
- M5 the docs carry the dev re-measure (78 against 83 against 80) and say that every bug fix keeps its test (from: an honest front door)
- R:FLOOR floor and Task loop unchanged · R:BUDGET ≤ 200 lines · R:MIRROR three trees identical · R:INVARIANTS earlier Quick guards stay green

## ASSUMPTIONS
- A1 [which] SWE-bench issues are all behavior changes → on them this skill asks what the measured skill asked, so the 226-of-300 result stands for it → not re-measured (the $150 cap is spent); the harness prompt no longer adds "start from a test", which the measured run had
- A2 [which] "no new behavior" is a list of examples, not a closed set → an agent may stretch it → the record line makes each skip visible

## PLAN
strategy: guards first (the important-tests-only guard file is replaced: its rule is superseded); rewrite the Quick paragraph and the table cell; mirror; docs
check: cd add-method && python3 -m pytest -q tests/test_tests_for_behavior_only.py
regression: cd add-method && python3 -m pytest -q
observes: M2 → share of `test: none` on bug-fix requests in the next benchmark run · above 5% → tighten the list

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_tests_for_behavior_only.py::test_a_behavior_change_gets_a_test · falsifier: bug fixes may skip the test
- C2 covers: M2, M3 · acceptance · add-method/tests/test_tests_for_behavior_only.py::test_no_new_behavior_needs_no_new_test · falsifier: a typo still needs a test, or a skip leaves no record
- C3 covers: M4 · acceptance · add-method/tests/test_tests_for_behavior_only.py::test_the_importance_judgement_is_gone · falsifier: "only when it is important" survives
- C4 covers: M5 · acceptance · add-method/tests/test_tests_for_behavior_only.py::test_docs_carry_the_remeasure · falsifier: the docs still describe important-tests-only
- C5 covers: R:FLOOR, R:BUDGET, R:MIRROR, R:INVARIANTS · regression · add-method/tests/test_tests_for_behavior_only.py::test_floor_budget_and_mirror + the full suite · falsifier: drift, or an earlier guard red

## LOG
- add-method/tests/test_important_tests_only.py is removed: its rule (M1 there) is superseded by this task's M1 and M4. The closed task file is left as it was.

## EVIDENCE
freeze: b663245b · head: 763e127b
seal: git diff b663245b 763e127b -- .add/tasks/tests-for-behavior-only.md add-method/tests/test_tests_for_behavior_only.py → empty
check: `cd add-method && python3 -m pytest -q tests/test_tests_for_behavior_only.py` → exit 0 · 5 passed (inside the full run)
regression: `cd add-method && python3 -m pytest -q` → exit 0 · 201 passed; benchmark/tests test_swe_smoke + test_arm_effort + test_arm_models → 56 passed
consumers: S1 skill tree → three trees byte-identical (C5); READMEs, CHANGELOG and results page carry the re-measure (C4)
re-measure that drove this (screen3, 101 dev issues, medium): important-tests-only 78 · measured skill 83 · vanilla 80; 2 gained, 7 lost, p = 0.18; $0.154 against $0.164; a test shipped in 76 of 101
residue: security — text-only; skipped-verification — the skip is limited to changes with no new behavior and leaves a `test: none` line
probes: none — no security risk
lens: build=self · refute=self cold reread · found: 0
verdict: RISK-ACCEPTED — every check held on this commit. The narrowed skill is not re-measured (A1): on bug fixes it asks what the measured skill asked, but the harness prompt no longer says "start from a test". Owner: Tin Dang, who chose "Narrow it, then ship" (2026-10-08).
