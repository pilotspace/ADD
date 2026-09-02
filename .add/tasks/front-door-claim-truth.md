---
type: Task
title: Every cost and ceremony claim on the front door is one the repo can back
status: done
depth: quick
milestone: first-run-truth
scope:
  - README.md
  - add-method/README.md
  - add-method/skill/add
  - add-method/tests
gives:
  - S1 the README Highlights claims — what a stranger is told ADD costs and requires
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:d21a167ba9d442b9" }
  - { by: "builder", at: 2026-09-01, act: replan, authority: process, note: "scope widens to the repo-root README.md: the same retracted cost claim ships on BOTH front doors, and test_promised_capabilities already binds both. Fixing one leaves the refuted sentence on the page most visitors land on first." }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:d21a167ba9d442b9" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:170231b753baf332" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/front-door-claim-truth.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:6ee64226d1e252d4" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:3d997dd4ea2dd050" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/front-door-claim-truth.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: process, outcome: PASS, receipt: /tasks/front-door-claim-truth.d/runs/2.md, brief: "sha256:3d997dd4ea2dd050" }
---
## CARD
goal: No cost or ceremony claim on the front door is contradicted by this repo's own evidence, the direct lane is visible to a human evaluator, and the two stale engine facts in the cookbook and the skill's own version are corrected under a parity check that enumerates every version source.
why: `README.md:58` claims "a thin 24-verb kernel, a 3-call task walk, one file per feature keep ADD the cheap option, not the heavyweight one". The verb count is right; the rest is not. The real minimum walk is five calls — `new → freeze → brief → run → gate` — because `brief` is mandatory and enforced (skipping it refuses with `R:UNBRIEFED`), and "3-call" appears nowhere else in the repository. "The cheap option" is contradicted by this repo's own `benchmark/results/2026-07-add-2.0-remeasure.md:30-33`: ADD $17.51 against spec-kit $10.05, at identical 1.0/0 scores. It is the first claim a skeptical evaluator disproves, and they disprove it from our own results directory. Separately, the kind×size ladder — the answer to "does this pay for a two-file bug fix", and genuinely well designed — is invisible on the front door: `grep -ni "quick\|ladder\|no node" README.md` returns only install headings, so a stranger reads README then GETTING-STARTED and concludes every change means an eight-section node. Two smaller falsehoods ride along: `SKILL.md:148` says `add doctor` "never writes" while `--sync` rewrites `index.md`, node CARDs and the vendored engine (the persona-author sub-skill documents the writing form, contradicting the cookbook in the same shipped tree), and all three skill trees declare `version: "3.1.0"` on a 3.3.0 release because `test_version_parity.py` enumerates five declarations and there are seven.
beat: done · next: add status

## RULES
<must>
- M1 No claim in README Highlights asserts a cost or call-count this repository's own evidence contradicts.
- M2 The README shows the kind×size ladder, stating that most changes never create a node.
- M3 The cookbook line for `doctor` names `--sync` and what it writes.
- M4 All three skill trees declare the shipped version, and the version-parity check enumerates every declaration — skill trees included.
- M5 Any measured claim that survives carries its provenance (sample size and engine version) beside it, not only in a footnote.
</must>
<reject>
- R:UNBACKEDCLAIM the front door must never assert a measured advantage this repo's own results refute -> "R:UNBACKEDCLAIM"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S1 · the request does not say which claims to cut versus qualify; taking CUT for the unbacked cost claim and QUALIFY for the context-rot measurement, because one is refuted and the other is merely thin (n=1, ADD 2.0.0, across a declared format break) -> if wrong an honest measurement is discarded or a refuted one survives · probe: the cost clause is gone and the measurement carries its provenance inline.
- A2 [absent] covers: S1 · the request does not say what replaces the deleted clause; taking the guarantees the repo can actually back — a receipt, a frozen contract, a refusal — since those are demonstrable today -> if wrong the bullet loses its point · probe: the replacement claim is one a shipped test binds.
- A3 [experience] covers: S1 · the request does not say where the ladder belongs; taking immediately after Highlights, because the ceremony question is what a lead asks before reading further -> if wrong the answer arrives after the reader has already decided · probe: the ladder appears before the install instructions.
- A4 [who] covers: S1 · n/a · the front door is read identically by every visitor.
- A5 [when] covers: S1 · n/a · a published claim has no temporal boundary beyond the release it ships in.
- A6 [order] covers: S1 · n/a · the claims are independent of one another.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: the unbacked cost clause is deleted and replaced with a backed guarantee; the kind×size ladder table lands after Highlights; the `doctor` cookbook line names `--sync`; the three skill trees declare 3.3.0 and `test_version_parity.py` enumerates seven declarations; the context-rot measurement carries its provenance inline.
scope: add-method/README.md, add-method/skill/add, add-method/tests

## EDGES
- E1 the verb COUNT (24) — accurate today and must stay bound to the real parser count, not frozen as a literal.
- E2 the benchmark report itself — honest, and not to be edited; only the README's summary of it changes.
- E3 the SKILL.md line pin — the `doctor` line is a replacement, not an addition, so the budget is unmoved.
- E4 the three skill trees plus `_bundled` — the version bump must land in every tracked twin or tree-parity reds.

## CHECKS
- test_no_front_door_claim_contradicts_the_benchmark · covers: M1, A1, R:UNBACKEDCLAIM · the cost clause is absent.
- test_the_readme_shows_the_size_ladder · covers: M2, A3 · the ladder rows appear before the install section.
- test_the_doctor_cookbook_line_names_sync · covers: M3, E3 · the line names the flag and what it writes.
- test_version_parity_enumerates_every_declaration · covers: M4, E4 · seven sources, all equal, skill trees included.
- test_the_measured_claim_carries_its_provenance · covers: M5, A2 · sample size and engine version sit with the claim.
- test_the_verb_count_is_read_from_the_parser · covers: E1 · the count is bound, not literal.
- test_the_benchmark_report_is_untouched · covers: E2 · the report is byte-identical to HEAD and still carries the retraction.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
