---
type: Task
title: Quick writes only the important tests; evidence proves the rest
status: done
kind: method
risks: [method-drift, skipped-verification]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_important_tests_only.py, add-method/CHANGELOG.md, README.md, add-method/README.md, benchmark/results/]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: a small change is made directly, with a new test only when it is important · why: the owner asked for it 2026-10-07 ("just write new important tests only; all the rest is caught via the evidence phase"). On the fresh 300, ADD gained nothing on 1–2 line fixes (51 vs 57 of 63) at 1.9× the dollars and 3.3× the seconds, added a median of 11 test lines to a 2-line fix, and the review study preferred the shorter output in 6 of 6

## RULES
- M1 Quick makes the change directly and writes a new test only when it is important: a plausible wrong fix would pass every existing check and break something a caller relies on (from: owner 2026-10-07; derived: the definition — the owner said "important", the falsifier test is ADD's existing meaning of a test worth writing)
- M2 an important test still tests the request's own example and the wrong fix's case, and is watched failing first (from: value-final M1, kept)
- M3 without a new test the change is still proven by evidence: the request's repro seen failing before and passing after, the suite run, the diff reviewed (from: owner — "the evidence phase"; blind-spots M2 — nothing ships unexecuted)
- M4 the Quick record says which path was taken: `red→green: <test>` or `test: none — <what covers it>` (from: derived: a skipped test must be visible to the reviewer, constraint 4 "no silent outcomes")
- M5 the lane table no longer promises a test for every Quick change (from: M1)
- M6 the docs say the 300-issue numbers were measured while Quick required a test on every fix (from: owner chose to ship inside 4.1.0; an honest front door)
- R:FLOOR the floor, the Task loop and its "at least one per Must and Reject" checks are unchanged (from: owner scoped the complaint to small changes)
- R:BUDGET ≤ 200 lines · R:MIRROR three trees identical · R:INVARIANTS earlier Quick guards stay green

## ASSUMPTIONS
- A1 [which] "small changes" means the Quick lane only → Task checks keep one per Must and Reject → if the owner meant Tasks too, a second change is needed
- A2 [which] "important" is defined by the wrong-fix test in M1 → an agent may read it loosely and skip tests that mattered → the probe below measures how it reads it; the fix rate is NOT re-measured (owner chose a small probe, not a paid screen)
- A3 [when] shipped inside 4.1.0 → the published 299-of-300 "shipped with a test" figure describes the skill before this change → stated in the docs (M6)

## PLAN
strategy: guards first; rewrite the Quick paragraph and one table cell; mirror; note the docs; then a small local probe (typo · rename · config · covered fix · uncovered fix · new behavior) comparing the old and new skill on which changes get a test
check: cd add-method && python3 -m pytest -q tests/test_important_tests_only.py
regression: cd add-method && python3 -m pytest -q
observes: M1 → share of Quick changes with `test: none` in the next benchmark run · above 80% on real bug fixes → tighten the definition

## CHECKS
- C1 covers: M1, M2 · acceptance · add-method/tests/test_important_tests_only.py::test_quick_writes_a_test_only_when_it_is_important · falsifier: the test stays mandatory, or "important" is left undefined
- C2 covers: M3 · acceptance · add-method/tests/test_important_tests_only.py::test_untested_changes_are_still_proven_by_evidence · falsifier: dropping the test also drops running anything
- C3 covers: M4, M5 · acceptance · add-method/tests/test_important_tests_only.py::test_record_and_table_name_the_path_taken · falsifier: a skipped test leaves no line in the record
- C4 covers: R:FLOOR · regression · add-method/tests/test_important_tests_only.py::test_floor_and_task_checks_are_untouched · falsifier: the Task loop's one-check-per-rule relaxed too
- C5 covers: M6 · acceptance · add-method/tests/test_important_tests_only.py::test_docs_say_what_the_numbers_were_measured_on · falsifier: the README implies 299 of 300 describes the shipped skill
- C6 covers: R:BUDGET, R:MIRROR, R:INVARIANTS · regression · add-method/tests/test_important_tests_only.py::test_budget_and_mirror + the full suite · falsifier: mirror drift or an earlier guard red

## EVIDENCE
freeze: 73c7800c · head: ac2cb738
seal: git diff 73c7800c ac2cb738 -- .add/tasks/important-tests-only.md add-method/tests/test_important_tests_only.py → empty
check: `cd add-method && python3 -m pytest -q tests/test_important_tests_only.py` → exit 0 · 6 passed
regression: `cd add-method && python3 -m pytest -q` → exit 0 · 202 passed; benchmark/tests/test_arm_effort.py + test_arm_models.py → 21 passed
consumers: S1 skill tree → three trees byte-identical (C6); READMEs, CHANGELOG and the results page carry the measured-before note (C5)
probe (A2): six requests on a toy repo, old skill (9853bf93) against new, Sonnet 5.5 at medium, one run each
  | request | old: new tests | new: new tests | new record |
  | typo in a message | 1 | 0 | test: none — nothing checks the text |
  | rename a constant | 0 | 0 | test: none — the existing test imports it |
  | config default | 1 | 0 | test: none — a test would restate the constant |
  | failing CI test | 1 | 0 | red→green on the existing failing test |
  | subtle bug (adjacent duplicates) | 2 | 1 | red→green on a new test |
  | small feature (free shipping) | 3 | 3 | red→green on new tests |
  totals: 8 new tests / 49 test lines → 4 / 24; 154 s → 106 s; every run ran the suite and left it green
  not comparable: cost ($0.90 → $0.54) — the new arm ran second on a warm prompt cache
residue: security — text-only; skipped-verification — every probe run still ran the suite and wrote the path it took
probes: none beyond the above — no security risk
lens: build=self · refute=self cold reread · found: 1 (an earlier guard pinned "The last lines of your reply"; the text was restored, not the test)
open: the SWE harness prompt (benchmark/swe/runner.py wrap_prompt) still says "Start from a test that reproduces the issue", so a rerun would not exercise this change until that sentence is removed
verdict: RISK-ACCEPTED — every check held on this commit, and the probe reads "important" as intended on six requests at n = 1. The effect on the SWE fix rate is not measured; owner: Tin Dang, who chose a small probe and to ship inside 4.1.0 (2026-10-07).
