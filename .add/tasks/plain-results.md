---
type: Task
title: results a normal user can read — an animated plain-language page, and a plain-words opening for both READMEs
status: build
kind: docs
risks: [front-door-claim-truth]
scope: [add-method/docs/add-results.html, add-method/docs/README.md, README.md, add-method/README.md, add-method/tests/test_plain_results.py, add-method/CHANGELOG.md]
gives: []
---
## CARD
goal: a person who has never heard of SWE-bench understands in two minutes what ADD gives over plain Claude Code, what it costs, and what is not proven
why: owner 2026-10-07 — "rewrite this result for normal user can understand easily and use animate HTML … enhance README also"; the current front door speaks benchmark jargon (McNemar, held-out, P2P, oracle)

## RULES
- M1 a self-contained animated page add-method/docs/add-results.html tells the fresh-300 result in plain words, side by side: bugs fixed, checked before shipping, shipped with a test, unclear requests, price, and the effort setting (from: owner request; benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md)
- M2 every number the page draws traces to the 2026-10 results page; it respects reduced motion and loads nothing remote (from: test_docs_value value-page discipline)
- M3 the page never overclaims and says in words what is not proven, what costs more, and what was not measured (from: publish-300 / publish-medium front-door truth)
- M4 both READMEs open with "## ADD in plain words" before Highlights: the four headline facts with no jargon, linking the page (from: owner request)
- M5 the docs index links the page (derived: discoverability)
- R:GUARDS every existing front-door guard stays green (from: add-method/tests)

## ASSUMPTIONS
- A1 [experience] "normal user" = a developer or manager who uses AI coding tools but not benchmarks → words like "bug", "checked", "test", "price"; no statistics vocabulary → if wrong, the page is too simple for experts, who still have the results page

## PLAN
strategy: guards first (test_plain_results.py); page reusing add-value.html's design tokens; README plain-words section; docs index link
check: cd add-method && python3 -m pytest -q tests/test_plain_results.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1, M2 · acceptance · add-method/tests/test_plain_results.py::test_page_is_self_contained_and_respects_motion + test_page_numbers_trace_to_the_results_page · falsifier: a CDN script, or a number not on the results page
- C2 covers: M3 · acceptance · add-method/tests/test_plain_results.py::test_page_speaks_plainly_and_never_overclaims · falsifier: "guarantee", jargon, or no "not proven"
- C3 covers: M4 · acceptance · add-method/tests/test_plain_results.py::test_readmes_open_with_plain_words_and_link_the_page · falsifier: section after Highlights, or jargon in it
- C4 covers: M5 · acceptance · add-method/tests/test_plain_results.py::test_docs_index_links_the_page · falsifier: no link
- C5 covers: R:GUARDS · regression · add-method/tests/ · falsifier: an existing guard red

## EVIDENCE
<written once, at verify>
