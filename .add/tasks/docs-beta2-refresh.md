---
type: Task
title: docs site teaches the beta.2 checkpoints
status: done
milestone: v3-final-collateral
depth: doc
scope:
  - add-method/docs/03-direction.md
  - add-method/docs/04-build.md
  - add-method/docs/05-verify.md
  - add-method/docs/11-adoption.md
  - add-method/docs/12-bundle-format.md
  - add-method/docs/13-command-reference.md
  - add-method/tests/book/test_beta2_coverage.py
gives:
  - S1 `docs/03-direction.md` — the `· probe:` grammar taught where assumptions are authored
  - S2 `docs/04-build.md` — the brief as Build's recorded entry
  - S3 `docs/05-verify.md` — R:UNBRIEFED and probed-assumption binding among the gate's refusals
  - S4 `docs/11-adoption.md` — the 2.x `add upgrade` path for adopters with an existing bundle
  - S5 `docs/12-bundle-format.md` — the `act: brief` stamp shape, the probe token, and the OKF-alignment note
  - S6 `docs/13-command-reference.md` — every wired verb has a row, `brief` described as the checkpoint it now is
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:0ad3ab322e0c9a58" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:7cfcc8814d971c28" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/docs-beta2-refresh.d/runs/1.md }
  - { by: "human:tindang", at: 2026-08-11, act: refreeze, authority: process, direction: "sha256:5d7f0d0de088b7de" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:500c07d4503bf936" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/docs-beta2-refresh.d/runs/2.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/docs-beta2-refresh.d/runs/2.md, brief: "sha256:500c07d4503bf936" }
---
## CARD
goal: the mkdocs book teaches the engine that ships — brief entry, probes, broader collapse, routing freshness, upgrade — instead of the beta.1 subset
why: only 2 of 25 pages name any beta.2 checkpoint; the site is the cold reader's first hour, and a book that under-describes the engine re-creates the overclaim/underclaim drift the advisor pass already burned us on once
beat: done · next: add status
## RULES
<must>
- M1 every wired CLI verb has a row in the command reference — the oracle is `cli.build_parser()`, never a hand list
- M2 the three beat chapters teach their own beta.2 checkpoint in place: Direction the probe grammar, Build the brief entry, Verify the R:UNBRIEFED refusal and probe binding
- M3 the bundle-format chapter shows the `act: brief` stamp and the `· probe:` token verbatim, and states the OKF alignment only as far as it is true (trust-layer shape, not conformance certification)
- M4 `mkdocs build --strict` stays exit 0 and the existing tests/book suite stays green
</must>
<reject>
- R:OVERCLAIM a doc line promising an enforcement the engine does not perform -> "OVERCLAIM"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1,S2,S3,S4,S5,S6 · the request does not say who the pages address; taking "the cold adopter reading the site before installing — the skill docs keep owning the in-session agent voice" -> cost if wrong: duplicated audience, drifting twins
- A2 [which] covers: S1,S2,S3,S4,S5,S6 · the request does not say which beta.2 items are in; taking "the five engine checkpoints (brief, probes, collapse breadth, routing freshness, upgrade) — campaign.py stays a benchmark doc, not a book chapter" -> cost if wrong: a reader hunts for tooling the book never names
- A3 [when] covers: S1,S2,S3,S4,S5,S6 · the request does not say which version the pages describe; taking "beta.2 as shipped — no forward promises; the final-release delta lands with the final tag" -> cost if wrong: the book promises futures again · probe: no page names an unshipped feature
- A4 [absent] covers: S1,S2,S3,S4,S5,S6 · the request does not say what happens to pages not in scope; taking "untouched — 02/06 already describe the loop abstractly and stay valid" -> cost if wrong: a stale cross-reference survives in an untouched page
- A5 [order] covers: S1,S2,S3,S4,S5,S6 · the request does not say where in each page the additions land; taking "inside the existing section that owns the concept, matching each page's voice — never a bolted-on appendix" -> cost if wrong: cosmetic incoherence only
## PLAN
contract: six page edits + one new red-first book test module; the verb-roster check reads the parser as its oracle
scope: the six docs pages above plus tests/book/test_beta2_coverage.py
## EDGES
- E1 a verb wired after this task — the M1 check must fail on the NEXT missing verb too, not just `upgrade`
## CHECKS
- test_command_reference_carries_every_wired_verb · covers: M1,E1 · parser-derived roster, each verb named in a table row
- test_direction_teaches_the_probe_grammar · covers: M2 · `· probe:` taught where assumptions are authored
- test_build_teaches_the_brief_entry · covers: M2 · `add brief` as the recorded entry into Build
- test_verify_names_the_unbriefed_refusal · covers: M2 · R:UNBRIEFED among the gate's refusal ladder
- test_bundle_format_shows_stamp_probe_and_okf · covers: M3 · `act: brief` + probe token verbatim; OKF named as alignment, not certification
- test_adoption_names_the_upgrade_path · covers: M2 · `add upgrade` where adopters with a 2.x bundle land
- test_no_page_promises_unshipped_enforcement · covers: A3,R:OVERCLAIM · the probe: the six pages name no unshipped feature verbs
- test_scoped_pages_stay_buildable · covers: M4 · nav membership + resolving links — the portable proxy for `mkdocs build --strict` (also run directly: exit 0)
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
## LESSONS
- <lesson> -> add learn <lens>
