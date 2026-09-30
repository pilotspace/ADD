---
type: Task
title: spend where round 4 found value — a Direction that is actually short, checks that send real callers' inputs, guesses that fail safe
status: build
kind: docs
risks: [method-drift, turn-cost, teaching-to-the-meter]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_skill_only.py, add-method/CHANGELOG.md, benchmark/PILOT-4v3-2026-09-30-r5.md]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: act on benchmark/PILOT-4v3-2026-09-30.md — cut Direction's messages, make checks send inputs the way a real caller does, make silent authorization fail safe and lead the report — then measure it the same day
why: the falsifier is the one practice with a measured gain (mutation +0.17/+0.26); Direction is 41–44% of tokens at ~20 messages against "two turns"; both escapes were the check sharing the builder's picture of the input; ASSUMPTIONS changed no decision — every run in both arms let any caller cancel any booking

## RULES
- M1 SKILL.md's Direction step names a batched plan: one command grounds and finds how the tests run (installing what is missing in that same command), one message writes the task file, tests and stubs as parallel writes, one command runs red and seals (from: PILOT-4v3-2026-09-30 cost ledger — 6 of 17 Direction messages probed the environment one command at a time)
- M2 CHECKS send inputs the way a real caller sends them: the body itself malformed (not JSON, `null`, a number, a list) as well as each field wrong-typed, and each value in every form the spec allows — a timestamp with and without an offset (from: PILOT-4v3-2026-09-30 — body-level garbage 5xx'd in 4 of 6 add-4 runs; one DELETE crashed on offset-aware timestamps its tests never sent)
- M3 a silence about who may act or see takes the least-privilege reading (only the owner), recorded as an ASSUMPTION (from: PILOT-4v3-2026-09-30 — 6 of 6 runs in both arms let any caller cancel any booking and listed every caller's bookings) (derived: deny by default — widening access later is compatible, narrowing it is a breaking change)
- M4 the report lists the ASSUMPTIONS costliest-if-wrong first (from: PILOT-4v3-2026-09-30 — the riskiest guess was written down in 1 of 3 runs and never led)
- R:BUDGET SKILL.md stays ≤ 200 lines (from: add-method/tests/test_skill_only.py)
- R:MIRROR the three shipped skill trees stay identical (from: add-method/tests/test_skill_only.py)

## ASSUMPTIONS
- A1 [which] M2's body list overlaps the held-out edge suite (null / number / non-object bodies) → an edge gain after this change is partly taught; the timestamp half is off-meter (the oracle sends offset-aware times) → reported that way
- A2 [which] M3 moves amb1's cancel-authority and list-scope items to their defensible readings → that is the rule working as meant, but it is also what the ambiguity meter scores → disclosed as such, not claimed as emergent
- A3 [experience] least privilege can deny an action the human wanted (an admin cancelling for someone) → it is an ASSUMPTION the review can widen, and M4 puts it first
- A4 [when] round 5 runs the same day as round 4 → cost is comparable to round 4 only through a fresh same-day vanilla arm, which round 5 reruns
- A5 [experience] the ~20 → ~10 message target is a guess about what batching buys → measured, not asserted · found: a traced run spent 6 of 17 Direction messages on environment probes and 4 on the seal commit (evidence: benchmark/PILOT-4v3-2026-09-30.md cost ledger)

## PLAN
strategy: red guard tests pin M1–M4 in SKILL.md; rewrite the Turns, CHECKS, ASSUMPTIONS and Report lines, compressing elsewhere to stay ≤ 200; mirror the trees; then round 5 the same day — add-4 and vanilla, wm1 + amb1, n = 3 each — is the behavioural evidence, written to benchmark/PILOT-4v3-2026-09-30-r5.md
check: cd add-method && python3 -m pytest -q tests/test_skill_only.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1 · acceptance · tests/test_skill_only.py::test_direction_is_a_batched_plan · falsifier: the round-4 wording — "Direction = two turns" with no batching the model can follow
- C2 covers: M2 · acceptance · tests/test_skill_only.py::test_checks_send_inputs_as_a_real_caller_would · falsifier: field-level wording only ("malformed or wrong-typed input is refused")
- C3 covers: M3 M4 · acceptance · tests/test_skill_only.py::test_silent_authority_fails_safe_and_leads_the_report · falsifier: the sweep asks *who* may but takes no side, and the report lists guesses in the order they were written
- C4 covers: R:BUDGET · regression · tests/test_skill_only.py::test_skill_md_stays_short · falsifier: the rules land by growing past the ceiling
- C5 covers: R:MIRROR · regression · tests/test_skill_only.py::test_shipped_skill_trees_are_identical · falsifier: only skill/add is edited

## EVIDENCE
<written once, at verify>
