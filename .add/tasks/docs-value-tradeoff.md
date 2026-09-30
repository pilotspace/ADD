---
type: Task
title: the READMEs sell ADD by what it gives a user's project against vanilla Claude — the same request as two flows, animated, with round 6's price beside every gain
status: build
kind: docs
risks: [overclaim, measurement-validity]
scope: [README.md, add-method/README.md, add-method/docs/add-vs-vanilla.html, add-method/docs/add-value.html, add-method/docs/README.md, add-method/docs/20-whats-new-in-4.md, add-method/CHANGELOG.md, benchmark/results/2026-09-add-4.0-vs-vanilla.md, add-method/tests/test_docs_tradeoff.py]
gives: [the animated flow page add-vs-vanilla.html]
---
## CARD
goal: a reader of either README sees, before installing, what ADD adds to their project over vanilla Claude Code and what it costs — as the same request run both ways, animated from two real round-6 transcripts
why: request — "rewrite README what ADD values for user project when trade-off with vanilla claude by show off mockup flow of both use animate HTML"; round 6 (Sonnet 5.5) moved the numbers: vanilla now matches ADD on edges and mutation, so the pitch must rest on what still differs

## RULES
- M1 the results page carries round 6: `claude-sonnet-5-5`, a link to `../PILOT-4v3-2026-09-30-r6.md`, the dollars and minutes per run with their multiples, where vanilla ties (held-out edges, mutation within noise) and wins (surfacing the contradiction 2 of 3 against 1 of 3), owner-only cancel across rounds, and the saturation disclosure (from: benchmark/PILOT-4v3-2026-09-30-r6.md)
- M2 both READMEs open their value pitch with what ADD gives a project, then a section that runs one request both ways — a side-by-side mockup of the vanilla flow and the ADD flow — linking the animated page (from: request)
- M3 each README's "Measured on 4.0" section quotes round 6 with the dollars multiple and the time multiple beside the gains, and names where vanilla ties; its numbers all trace to the results page (from: request — "trade-off"; .add/tasks/docs-4-value.md R:OVERCLAIM)
- M4 `add-method/docs/add-vs-vanilla.html` plays both flows on one clock: vanilla done at 46 s for $0.28, ADD done at 195 s for $0.63, condensed from `vanilla-amb/rep1` and `add-4-amb/rep1` of round 6; it is self-contained, shows the finished state under reduced motion and without JavaScript, and every number in its data block is on the results page (from: request — "animate HTML"; .add/tasks/docs-4-value.md M8)
- M5 ch 20's measured section and the CHANGELOG 4.0.0 entry add the Sonnet 5.5 round (from: request — "update document")
- M6 the flow page is linked from both READMEs, `add-method/docs/README.md` and the value page (from: request)
- R:OVERCLAIM no page claims a quality gain vanilla matched on Sonnet 5.5, and no brag words (from: .add/tasks/docs-4-value.md R:OVERCLAIM)
- R:STRAWMAN the vanilla pane shows vanilla's real best: it caught the contradiction, chose the same default, and listed its choices — in its chat reply (from: benchmark/runs-4v3-2026-09-30-r6/vanilla-amb/rep1 transcript)

## ASSUMPTIONS
- A1 [which] "README" means both the repo README and the package README → both carry the sections; C5-C9 of docs-4-value still hold them to the results page
- A2 [which] a GitHub README cannot run an animation → the README carries a static side-by-side mockup; the animation lives on the book site at /add-vs-vanilla.html, linked from it
- A3 [what] the pitch leads with durable value (decisions on disk, sealed checks, re-runnable evidence, least-privilege guesses), not test quality → round 6 shows vanilla matching on edges and mutation at Sonnet 5.5
- A4 [experience] a mockup from one pair of runs could cherry-pick → it names its two runs, and the page's scoreboard quotes the n = 3 means, not the pair

## PLAN
strategy: red checks first; results page gains a round-6 section; rewrite the value half of both READMEs; build the flow page from the two transcripts; ch 20 + CHANGELOG + links
check: python3 -m pytest -q add-method/tests/test_docs_tradeoff.py
regression: python3 -m pytest -q add-method/tests/test_docs_value.py

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_docs_tradeoff.py::test_results_page_carries_round_6 · falsifier: round 6 quoted without the model id, the pilot link or the saturation disclosure
- C2 covers: M2 R:STRAWMAN · acceptance · add-method/tests/test_docs_tradeoff.py::test_readmes_run_one_request_both_ways · falsifier: a README section with the ADD flow and no vanilla flow, or no link to the animated page
- C3 covers: M3 R:OVERCLAIM · acceptance · add-method/tests/test_docs_tradeoff.py::test_measured_sections_price_every_gain_in_dollars_and_time · falsifier: a round-6 gain quoted with the dollar multiple but not the time multiple, or vanilla's ties left out
- C4 covers: M4 R:OVERCLAIM R:STRAWMAN · acceptance · add-method/tests/test_docs_tradeoff.py::test_flow_page_plays_both_runs_and_traces · falsifier: a remote asset, no reduced-motion or no-JS state, a number not on the results page, or a vanilla pane that omits the contradiction it caught
- C5 covers: M5 · acceptance · add-method/tests/test_docs_tradeoff.py::test_ch20_and_changelog_carry_sonnet_5_5 · falsifier: ch 20 quoting a Sonnet 5.5 number that is not on the results page
- C6 covers: M6 · acceptance · add-method/tests/test_docs_tradeoff.py::test_flow_page_is_linked · falsifier: the page exists but only one README links it
- C7 covers: R:OVERCLAIM · regression · add-method/tests/test_docs_value.py · falsifier: the rewrite drops the add-value link or a README number leaves the results page

## LOG

## EVIDENCE
<written once, at verify>
