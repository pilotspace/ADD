---
type: Task
title: publish the fresh 300 at medium effort — ADD 226 vs vanilla 215 — and recommend --effort medium everywhere
status: build
kind: docs
risks: [front-door-claim-truth]
scope: [README.md, add-method/README.md, benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md, benchmark/GAP-TRACK-2026-10-06.md, add-method/CHANGELOG.md, add-method/tests/test_publish_medium.py, add-method/tests/test_publish_300.py, add-method/tests/test_value_final.py]
gives: []
---
## CARD
goal: the front door states the confirmed medium-effort result and recommends `--effort medium` everywhere; the low-effort loss stays on the results page as history
why: owner's bar (ADD ≥ vanilla on a fresh full 300) is met: ADD-medium 226 vs vanilla-medium 215 (24 vs 13 one-arm-only, McNemar p = 0.099); held-out 199 alone 143 vs 135 (p = 0.17). Owner decided 2026-10-07: if met, recommend medium everywhere

## RULES
- M1 both READMEs' measured section states 226 of 300 vs 215 of 300 with p = 0.099 and the 1.8× cost, and no longer states the superseded low-effort loss as current (from: benchmark/runs-swe/screen1 + screen2 + heldout reports)
- M2 both READMEs recommend `--effort medium` (from: owner interview 2026-10-07, "Medium everywhere")
- M3 the value table quotes the medium run's test discipline: green run seen 274 of 300 vs 53 of 300, tests shipped 299 of 300 vs 17 of 300 (from: the fresh-300 transcripts)
- M4 the results page leads with a fresh-300-at-medium section (held-out split, per-repo, cost, Not measured) and keeps the low-effort all-300 section below it (from: publish-300 M3)
- R:TRACE README numbers trace to the cited results page (from: test_docs_value)

## ASSUMPTIONS
- A1 [experience] p = 0.099 is not significant → stated as "at least as many, likely more", never "beats" → overclaim if worded as a win

## PLAN
strategy: guards first (test_publish_medium.py; publish-300's README guards and value-final's facts move to the results page and to the medium run); then the results section, both READMEs, CHANGELOG
check: cd add-method && python3 -m pytest -q tests/test_publish_medium.py tests/test_publish_300.py tests/test_value_final.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_publish_medium.py::test_readmes_state_the_medium_result_with_its_price · falsifier: medium numbers quoted without the cost, or the old loss left as current
- C2 covers: M2 · acceptance · add-method/tests/test_publish_medium.py::test_readmes_recommend_medium · falsifier: fine print still says low
- C3 covers: M3 · acceptance · add-method/tests/test_publish_medium.py::test_value_table_quotes_the_medium_run + add-method/tests/test_value_final.py::test_readmes_value_table_is_measured · falsifier: value table keeps the low-run figures
- C4 covers: M4 · acceptance · add-method/tests/test_publish_medium.py::test_results_page_leads_with_the_medium_300_and_keeps_the_low_run + add-method/tests/test_publish_300.py · falsifier: the low-effort section is deleted, or the medium section is appended last
- C5 covers: R:TRACE · regression · add-method/tests/test_docs_value.py · falsifier: a README number missing from the results page

## LOG
- publish-300's README guards now read the results page (its section stays there as history); value-final's README facts move to the medium run (M3).

## EVIDENCE
<written once, at verify>
