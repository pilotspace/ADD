---
type: Task
title: cut the `sites:` record the model does not write; keep "grep every other site" as an action
status: build
kind: docs
risks: [method-drift]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_cut_sites_record.py, add-method/tests/test_blind_spots.py, add-method/CHANGELOG.md]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: the Quick record asks only for lines the model writes · why: blind-spots accepted the risk that `sites:` appeared in 2 of 30 runs and did not flip django-13265, with the owner to cut or rework it; SKILL.md § Learn says a control whose yield stays at zero is cut or fixed. Owner decided 2026-10-07: cut the record, keep the action

## RULES
- M1 Quick still greps every other site that calls or emits what it changes (from: blind-spots M1 — the action)
- M2 the Quick record no longer asks for a `sites:` line (from: blind-spots EVIDENCE — 2 of 30 transcripts; owner 2026-10-07)
- M3 the record keeps `lane:`, `intent:`, `red→green:` and the `suite: unavailable` form (from: maintainer-intent M3, blind-spots M2)
- R:BUDGET ≤ 200 lines · R:MIRROR three trees identical · R:INVARIANTS earlier guards stay green, with test_blind_spots' site check moved from the record to the action

## ASSUMPTIONS
- A1 [which] removing an unwritten record changes no measured behaviour → not re-benchmarked; the fresh-300 result was produced with the record present but unused

## PLAN
strategy: guards first; delete the one field from the Quick paragraph; mirror
check: cd add-method && python3 -m pytest -q tests/test_cut_sites_record.py tests/test_blind_spots.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1, M2 · acceptance · add-method/tests/test_cut_sites_record.py::test_quick_keeps_the_grep_and_drops_the_record · falsifier: the grep instruction removed along with the record
- C2 covers: M3 · acceptance · add-method/tests/test_cut_sites_record.py::test_quick_record_keeps_what_transferred · falsifier: `intent:` or the unavailable form cut too
- C3 covers: R:BUDGET, R:MIRROR, R:INVARIANTS · regression · add-method/tests/test_cut_sites_record.py::test_skill_stays_within_budget + add-method/tests/test_skill_only.py + test_blind_spots.py + test_maintainer_intent.py · falsifier: mirror drift, or an earlier guard red

## LOG
- test_blind_spots.py::test_quick_lists_every_site_of_the_change now checks the action, not the `sites:` record (M2).

## EVIDENCE
<written once, at verify>
