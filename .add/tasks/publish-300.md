---
type: Task
title: publish the full SWE-bench Lite trade-off — ADD fixes fewer issues than vanilla, verifies and ships tests far more often, at 1.4× the cost — with what was not measured
status: build
kind: docs
risks: [front-door-claim-truth]
scope: [README.md, add-method/README.md, benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md, add-method/tests/test_publish_300.py, add-method/tests/test_value_final.py, add-method/CHANGELOG.md, benchmark/SWE-LITE-PILOT-2026-10-03.md]
gives: []
---
## CARD
goal: the front door states the 300-issue result as measured: the loss, the price, the test discipline, the diagnostic, and the unmeasured human side
why: the READMEs still quote the 30-issue slice (ADD 23 vs 21), which the full run reversed (201 vs 215 of 300, McNemar p = 0.016); a user choosing a tool must see the real trade-off

## RULES
- M1 both READMEs' measured section states 201 of 300 vs 215 of 300 with p = 0.016 and says in words that vanilla fixes more (from: benchmark/runs-swe/full300 + r11-testenv reports)
- M2 the value table quotes the full-run test discipline: a passing test run seen 255 of 300 vs 42 of 300, tests shipped 298 of 300 vs 14 of 300; this supersedes value-final M4's 30-issue facts (from: full300 transcripts; value-final M4)
- M3 the results page leads with an all-300 section: score, per-repo split, AI effort, review proxies, the diagnostic, and a Not measured list naming human review time (from: user 2026-10-05 "publish this real trade-off for user")
- M4 "When vanilla is the right call" drops the 4–5× speed claim, which came from the operator's plugin (from: PILOT-4v3 r7 contamination finding)
- R:TRACE every README number traces to the cited results page (from: add-method/tests/test_docs_value.py::test_readme_numbers_trace_to_the_results_page)

## ASSUMPTIONS
- A1 [experience] the recall hypothesis (vanilla reproduces upstream fixes) is stated as a hypothesis with its numbers, never as an excuse → if stated as fact, the page overclaims

## PLAN
strategy: red guards in test_publish_300.py and the superseding facts in test_value_final.py; write the results section, then both READMEs
check: cd add-method && python3 -m pytest -q tests/test_publish_300.py tests/test_value_final.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_publish_300.py::test_readmes_state_the_300_result_with_the_loss · falsifier: the 300 numbers quoted without the loss in words
- C2 covers: M2 · acceptance · add-method/tests/test_publish_300.py::test_value_table_quotes_the_300_test_discipline + add-method/tests/test_value_final.py::test_readmes_value_table_is_measured · falsifier: the table keeps the 30-issue facts
- C3 covers: M3 · acceptance · add-method/tests/test_publish_300.py::test_results_page_leads_with_the_300_and_names_what_was_not_measured · falsifier: the 300 section is appended at the end, or omits human review time
- C4 covers: M4 · acceptance · add-method/tests/test_publish_300.py::test_vanilla_call_drops_the_contaminated_speed_claim · falsifier: "4–5× faster" remains
- C5 covers: R:TRACE · regression · add-method/tests/test_docs_value.py · falsifier: a README number missing from the results page

## LOG
- test_value_final.py's README facts change from the 30-issue pilot to the 300-issue run (M2): same rule, larger evidence.

## EVIDENCE
<written once, at verify>
