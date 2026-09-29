---
type: Task
title: measure code quality beyond the oracle — six deterministic dimensions
status: build
kind: feature
risks: [false-signal, measurement-drift]
scope: [benchmark/quality.py, benchmark/workload/wm1/edge/, benchmark/workload/amb1/edge/, benchmark/tests/test_quality.py, benchmark/tests/fixtures/quality/]
gives: [S1 `python -m benchmark.quality <run dirs…>` → quality.json per run + a table; S2 quality.score_quality(workspace, wm, family) -> dict]
---
## CARD
goal: score each benchmark run on six quality dimensions the oracle cannot see — edge robustness, test strength, static quality, security smells, test quality, evidence honesty
why: oracle pass rate is 1.00 on every arm and rep (09-28 pilot, 09-29 runs), so it no longer separates ADD 4.0 from 3.7 or from no method; the visible oracles hold 5 (wm1) and 8 (amb1) tests

## RULES
- M1 edge robustness runs a held-out suite of behaviors the PROMPT implies but the visible oracle never checks (typed-field validation, malformed JSON → 400, no 5xx on garbage, delete-then-get 404, distinct ids) and reports passed/total (from: request · wm1/amb1 PROMPT.md)
- M2 edge suites never test a planted amb1 ambiguity (waitlist order, cancel authority, cancelled visibility, list scope, conflict response) (from: benchmark/workload/amb1/oracle/test_amb1_clean.py docstring)
- M3 test strength = share of deterministic AST mutants of the app code that the run's OWN test suite kills; a suite that is not green on the unmutated app scores n/a, not 0 (from: derived: a red baseline would count every mutant as killed)
- M4 static quality reports app LOC, max/mean cyclomatic complexity, functions over 50 lines, duplicate function bodies, annotation ratio, bare/broad-pass excepts — app code only (tests, .venv, .add excluded) (from: request)
- M5 security smells counts eval/exec, shell=True, unsafe deserializer loads, SQL built by string formatting, and secret-named values passed to logging/print (from: request)
- M6 test quality reports test count, tests with zero assertions, asserts per test (from: request)
- M7 evidence honesty compares the passed-count claimed on the `regression:` line of each task's EVIDENCE with a fresh run of the suite at HEAD; no ADD bundle → n/a (from: derived: EVIDENCE is the ADD claim a reviewer trusts)
- R:NODEPS stdlib + pytest only — nothing new installed into workspaces or the harness (from: benchmark/score.py "stdlib-first")
- R:READONLY a run's workspace is never modified; mutation runs on a temp copy (from: derived: re-scoring must be repeatable)

## ASSUMPTIONS
- A1 [which] "positive integer" in wm1 implies 0, negatives, strings and floats are 400 → typed validation is part of the spec → a reviewer may call it gold-plating; it is scored as its own dimension, never folded into oracle pass rate
- A2 [which] amb1 end_time before start_time → 400 is implied by "booking" semantics, not stated → kept out; only stated types and malformed input are tested
- A3 [when] mutation cap 24 mutants, seeded, 60 s per suite run → bounded cost per run (~1–3 min) → a very slow agent suite gets fewer mutants tried; reported as tried/killed
- A4 [experience] edge suites validated against two reference apps in fixtures (a correct one must pass all, a no-validation one must fail the validation cases) so the instrument itself has evidence

## PLAN
strategy: red unit tests on synthetic workspaces + reference apps first; quality.py stdlib AST; edge suites reuse workload/_oracle_lib; then score every run under benchmark/runs-4v3-2026-09-2{8,9}
check: python3 -m pytest -q benchmark/tests/test_quality.py
regression: python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 · acceptance · test_quality.py::test_wm1_edge_suite_passes_the_reference_app · falsifier: an edge case the spec doesn't imply (a correct app fails it)
- C2 covers: M1 · acceptance · test_quality.py::test_wm1_edge_suite_catches_the_sloppy_app · falsifier: edge cases that assert nothing a lax app gets wrong
- C3 covers: M1 M2 · acceptance · test_quality.py::test_amb1_edge_suite_passes_reference_and_catches_sloppy · falsifier: an amb1 edge that grades a planted ambiguity
- C4 covers: M3 · acceptance · test_quality.py::test_mutation_score_separates_strong_and_weak_suites · falsifier: a score that ignores which tests exist (strong == weak)
- C5 covers: M3 · acceptance · test_quality.py::test_mutation_score_is_na_on_red_baseline · falsifier: counting a red suite as killing every mutant
- C6 covers: M4 M6 · acceptance · test_quality.py::test_static_and_test_quality_on_known_code · falsifier: counting test files or .venv as app code
- C7 covers: M5 · acceptance · test_quality.py::test_security_smells_found_and_clean_code_is_zero · falsifier: flagging a safe `logging.info("user %s", name)`
- C8 covers: M7 · acceptance · test_quality.py::test_evidence_honesty_true_false_and_na · falsifier: honesty computed from the claim alone, never rerun
- C9 covers: R:READONLY · acceptance · test_quality.py::test_scoring_leaves_the_workspace_untouched · falsifier: mutating in place

## EVIDENCE
<written once, at verify>
