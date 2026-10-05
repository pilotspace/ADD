---
type: Task
title: fix what the maintainers meant, not only what the issue literally says — read the nearest tests' conventions first, and put the record in the reply that is always read
status: build
kind: docs
risks: [method-drift, teaching-to-the-meter, cost]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_maintainer_intent.py, add-method/CHANGELOG.md]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: Quick and Direction read the conventions of the nearest tests and sibling code before writing the test, treat the literal fix as a candidate wrong fix, and end the reply with the record
why: at the half-way point of the full SWE-bench Lite run, vanilla-medium leads ADD-low 126 to 116 of 156 (discordant 14 to 4, McNemar p ≈ 0.03). Every ADD miss is an F2P failure with 0 tests broken. On those 13, ADD reproduced 31% of gold's added lines against vanilla's 70%: ADD builds the issue's literal reading (django-15320 skipped the `.clone()` the caller-isolation test needs; django-12747 made path A match B where gold made B match A)

## RULES
- M1 Quick, before its test, reads the tests and sibling code nearest what it changes, and the fix keeps their conventions (inputs not mutated, parallel paths consistent, the neighbours' pattern) (from: full300 vanilla-only set — django-15320, django-12747; derived: conventions are what a maintainer's hidden test encodes)
- M2 the fix the request literally suggests is a candidate wrong fix: the falsifier considers it (from: django-15320 — the issue says "adding query.subquery = True fixes the problem", gold also clones)
- M3 the Quick record (`lane:` · `intent:` · `sites:` · `red→green:`/`suite: unavailable`) is the last lines of the reply, and the commit body only if committing (from: commit-body record 7/30 (lean-bounded-fixes), `sites:` 2/30 (blind-spots), report states a test result 31/106 (full300 interim))
- M4 a non-code Quick uses the check that fits the work (from: user question 2026-10-05 — "isn't it depend on kind of task?"; references/format.md § Non-code work)
- M5 Direction's Ground step reads the nearest tests (derived: M1 for the Task lane)
- R:METER no rule names an instance, API, message or layout (from: blind-spots R:METER)
- R:BUDGET ≤ 200 lines · R:MIRROR three trees · R:INVARIANTS closed-loop phrases and earlier guards (test_blind_spots, test_value_final, test_round8_lessons) stay green

## ASSUMPTIONS
- A1 [which] the vanilla advantage is partly recall of the upstream fix (verbatim 70% vs 31%), which no instruction can or should reproduce → M1 targets only the convention-following part → the re-measure on the 13 bounds what is recoverable
- A2 [when] effort (ADD low vs vanilla medium) may explain part of the gap → settled by the diagnostic (ADD-medium on the 13), not by this task
- A3 [experience] M1 adds a read per fix → cost rises a little → measured; cut if it buys nothing (C12)

## PLAN
strategy: red guards in test_maintainer_intent.py; rewrite Quick and the Ground line with compensating cuts; mirror; measure on the 13 vanilla-only issues against the ADD-low and ADD-medium reruns, then the seed-0 slice
check: cd add-method && python3 -m pytest -q tests/test_maintainer_intent.py
regression: cd add-method && python3 -m pytest -q ; python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_maintainer_intent.py::test_quick_reads_the_conventions_before_the_test · falsifier: conventions mentioned after the test step, or not at all
- C2 covers: M2 · acceptance · add-method/tests/test_maintainer_intent.py::test_the_literal_fix_is_a_candidate_wrong_fix · falsifier: Quick still tests only the literal example
- C3 covers: M3 · acceptance · add-method/tests/test_maintainer_intent.py::test_quick_record_is_the_last_lines_of_the_reply · falsifier: the record stays in the commit body only
- C4 covers: M4 · acceptance · add-method/tests/test_maintainer_intent.py::test_non_code_quick_uses_the_check_that_fits · falsifier: Quick says "test" with no non-code route
- C5 covers: M5 · acceptance · add-method/tests/test_maintainer_intent.py::test_direction_grounds_in_the_nearest_tests · falsifier: Ground reads only the touched code
- C6 covers: R:BUDGET, R:MIRROR, R:INVARIANTS, R:METER · regression · add-method/tests/test_maintainer_intent.py::test_skill_stays_within_budget + add-method/tests/test_skill_only.py + test_blind_spots.py + test_value_final.py + test_round8_lessons.py · falsifier: growth past 200, mirror drift, an earlier guard red; R:METER read at verify

## EVIDENCE
<written once, at verify>
