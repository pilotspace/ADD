---
type: Task
title: close the two SWE-bench blind spots — every site of a change accounted for, and a recorded fallback when the suite cannot run
status: build
kind: docs
risks: [method-drift, teaching-to-the-meter]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_blind_spots.py, add-method/CHANGELOG.md]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: two instructions with an artifact each, aimed at the failure classes round 10 showed ADD has, not at instances
why: of ADD-low's 6 SWE losses, django-13265 was an incomplete fix whose second site sat in the agent's own grep output, and sklearn-14087 shipped untested because the suite could not run (its next line crashes on the issue's own default input); ADD-medium shipped a SyntaxError into matplotlib-24265 for the same reason (16 tests broken). The other 4 losses need facts the issue never states — no instruction should target them

## RULES
- M1 Quick lists every other site that calls or emits what it changes, each `fixed` or `unaffected: <why>`, as `sites:` in its record (from: benchmark/runs-swe/pilot30-s0-value — django-13265 transcript: grep returned `generate_altered_order_with_respect_to`, never followed; gold moves its call)
- M2 Quick with no runnable suite runs the request's repro as written; if that cannot run, imports every touched file and traces the request's inputs through the edit; records `suite: unavailable — <why>` and what ran instead (from: 9/30 ADD-low and 7/30 ADD-medium runs never saw a green test; sweep-add-medium matplotlib-24265 SyntaxError, 16 P2P broken; sklearn-14087 `l1_ratios_=[None]` crash on the default penalty)
- M3 a Task whose check cannot run is never PASS — at best RISK-ACCEPTED (derived: constraint 2, "trusted because checks you ran pass")
- R:METER no rule names an instance, an API, a message or a layout the issue does not state (from: subagent analysis — xarray-4248, pytest-8365, sympy-14308 gold is unknowable from the issue)
- R:BUDGET SKILL.md ≤ 200 lines · R:MIRROR three trees identical · R:INVARIANTS closed-loop phrases stay (from: PROJECT.md invariants; test_skill_only.py)

## ASSUMPTIONS
- A1 [which] M1 costs a grep and a line per change → cheap on SWE (one turn) → if it adds turns everywhere, the cost shows in the re-measure
- A2 [experience] the records land in the commit body, which transferred poorly in foreign repos (7/30) → the instruction also names the final report → measured by the behaviour, not the record
- A3 [when] the harness now gives the agent the image's env (--testenv docker), so M2 fires less there than in a bare checkout → measured on both the behaviour and the resolved count

## PLAN
strategy: red guards in test_blind_spots.py; rewrite the Quick paragraph and Verify step 2 with compensating cuts; mirror three trees; re-measure SWE ADD-low and vanilla-medium on the same 30 under --testenv docker
check: cd add-method && python3 -m pytest -q tests/test_blind_spots.py
regression: cd add-method && python3 -m pytest -q ; python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_blind_spots.py::test_quick_lists_every_site_of_the_change · falsifier: Quick says "grep callers" with no per-site record
- C2 covers: M2 · acceptance · add-method/tests/test_blind_spots.py::test_quick_has_a_fallback_when_the_suite_cannot_run · falsifier: a fallback with no `suite: unavailable` record, or only "compile it"
- C3 covers: M3 · acceptance · add-method/tests/test_blind_spots.py::test_verify_never_passes_a_check_it_could_not_run · falsifier: step 2 silent on an unrunnable check
- C4 covers: R:BUDGET, R:MIRROR, R:INVARIANTS, R:METER · regression · add-method/tests/test_blind_spots.py::test_skill_stays_within_budget + add-method/tests/test_skill_only.py · falsifier: the file grows past 200 or a mirror drifts; R:METER is read at verify (residue)

## EVIDENCE
<written once, at verify>
