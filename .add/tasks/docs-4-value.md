---
type: Task
title: the docs tell the truth about the merged 4.0 skill and what it measurably buys Claude Code — plus an animated page that shows it
status: build
kind: docs
risks: [overclaim, stale-docs]
scope: [README.md, add-method/README.md, add-method/CHANGELOG.md, add-method/docs/, benchmark/results/2026-09-add-4.0-vs-vanilla.md, add-method/tests/test_docs_value.py]
gives: [S1 add-method/docs/add-value.html — the page the READMEs and the book link to]
---
## CARD
goal: bring the book, READMEs and CHANGELOG in line with the skill merged in ae2c87d6 and the benchmark rounds 3–5, and ship an animated page showing ADD's measured value to Claude Code
why: the book still sends data and architecture work to a subagent and tells Explore to fan out; the checklist lacks the input-shape, least-privilege and costliest-first rules; the front doors cite only a 2.0-era benchmark; nothing shows what 4.0 was measured to buy

## RULES
- M1 no book page sends data or architecture work to a fresh subagent or tells a lane to fan out parallel subagents; the pages that describe the second reader and refute say a fresh subagent is for security work only (from: add-method/skill/add/SKILL.md at ae2c87d6 — "Security work: one fresh subagent does it. Anything else: your own cold reread"; "at most one per beat, in the foreground")
- M2 ch 03 and the Direction checklist state three rules the skill carries: checks send inputs the way a real caller sends them (the body itself as well as each field, every value form the spec allows); a silence about who may act or see takes the least-privilege reading; every RULES id sits on some `covers:` line (from: SKILL.md CHECKS and ASSUMPTIONS bullets)
- M3 ch 06 and the Learn-and-report checklist say the report lists the assumptions costliest-if-wrong first (from: SKILL.md Report section)
- M4 `benchmark/results/2026-09-add-4.0-vs-vanilla.md` consolidates rounds 3–5: each measure with arm, workload, n and values, the disclosures (operator config loaded by both arms, saturated oracle, reruns, estimated lost-attempt cost) and a link to each PILOT report it draws from (from: benchmark/PILOT-4v3-2026-09-29.md, -30.md, -30-r5.md)
- M5 both READMEs carry a "measured on 4.0" section and a Highlights line with n and version; every number in the section appears on the results page (from: request; add-method/tests/test_front_door_claim_truth.py — a measured claim carries its provenance)
- M6 ch 20 gains a "Measured on 4.0" section that cites the results page by its `github.com/pilotspace/ADD/blob/main/benchmark/…` URL (from: request; test_the_migration_page_cites_evidence_that_exists)
- M7 the 4.0.0 CHANGELOG entry lists the skill changes made after 2026-09-28 and the benchmark quality tooling (from: `git log 0ec8b2d5^..ae2c87d6`)
- M8 `add-method/docs/add-value.html` is an animated, self-contained page showing ADD's measured value to Claude Code: every figure it draws comes from one embedded JSON data block, and every value in that block appears on the results page; it loads nothing external, honours `prefers-reduced-motion`, and is linked from both READMEs and the book home (from: request)
- R:OVERCLAIM no touched page claims ADD is cheaper than vanilla or scores higher on the correctness oracle; wherever a gain is quoted, the cost multiple is quoted on the same surface (from: test_front_door_claim_truth R:UNBACKEDCLAIM; PILOT-4v3-2026-09-30.md — oracle saturated, 2.2–2.8× cost)

## ASSUMPTIONS
- A1 [who] the reader is a developer deciding whether to put ADD on Claude Code → plain language, every number with its n and a link → cost if wrong: a manager needs a shorter page
- A2 [which] the page lives in the book's docs dir so the site publishes it next to the chapters → found: `docs_dir: add-method/docs` (evidence: mkdocs.yml:17); MkDocs copies non-markdown files as-is
- A3 [when] the new changes belong in the 4.0.0 CHANGELOG entry, not `[Unreleased]` → found: no v4.0.0 tag exists (evidence: `git tag -l 'v4*'` → empty)
- A4 [experience] a reader without JavaScript or with reduced motion still gets every number → the figures are also written in the page's text and the animation is decoration over them
- A5 [which] "vanilla" in every quoted number is Claude Code carrying the operator's `~/.claude` config, not bare Claude Code → said on the results page, the READMEs' fine print and the HTML
- A6 [which] the 2.0-era context-rot benchmark stays the lead claim of the READMEs; the 4.0 numbers are added beside it → the existing guard pins that claim and the report it cites

## PLAN
strategy: red doc checks in add-method/tests/test_docs_value.py; fix the stale book pages; write the results page from the three PILOT reports; add the README and ch 20 sections and CHANGELOG bullets; build the HTML (dataviz method: form → colour by job → validated palette → marks → hover → a11y → render and look)
check: cd add-method && python3 -m pytest -q tests/test_docs_value.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1 · acceptance · tests/test_docs_value.py::test_no_page_sends_non_security_work_to_a_subagent · falsifier: ch 05 fixed but the checklist or ch 20 still says "security, data or architecture"
- C2 covers: M2 · acceptance · tests/test_docs_value.py::test_direction_pages_state_the_merged_rules · falsifier: ch 03 updated, the checklist left behind
- C3 covers: M3 · acceptance · tests/test_docs_value.py::test_report_pages_lead_with_the_costliest_guess · falsifier: the rule lands in ch 06 only
- C4 covers: M4 · acceptance · tests/test_docs_value.py::test_results_page_carries_provenance · falsifier: a results page with numbers and no n, no disclosure or a dead PILOT link
- C5 covers: M5 R:OVERCLAIM · acceptance · tests/test_docs_value.py::test_readme_numbers_trace_to_the_results_page · falsifier: a README number rounded or invented, or a gain quoted with no cost beside it
- C6 covers: M6 · acceptance · tests/test_docs_value.py::test_migration_page_cites_the_4_0_results · falsifier: ch 20 quotes 4.0 numbers without the in-repo citation
- C7 covers: M7 · acceptance · tests/test_docs_value.py::test_changelog_lists_the_post_release_skill_changes · falsifier: the CHANGELOG still describes the skill as of 2026-09-28
- C8 covers: M8 R:OVERCLAIM · acceptance · tests/test_docs_value.py::test_value_page_is_self_contained_and_traceable · falsifier: a page that pulls a CDN script or font, shows a figure that is not on the results page, ignores reduced motion, or claims "cheaper"
- C9 covers: M8 · acceptance · tests/test_docs_value.py::test_value_page_is_linked · falsifier: the page ships but nothing links to it

## EVIDENCE
<written once, at verify>
