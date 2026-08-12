---
type: Task
title: A month-end reconciliation, run end to end
status: done
depth: standard
milestone: adoption-beyond-code
scope:
  - add-method/BEYOND-CODE.md
  - add-method/tests/skill/
gives:
  - S1 the BEYOND-CODE walkthrough — the first document a non-code lead reads end to end
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:42a2e90f35cf813b" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:d6eaae0a765738b9" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:1a0bb46f85c0287b" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/beyond-code-walkthrough.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/beyond-code-walkthrough.d/runs/1.md, brief: "sha256:1a0bb46f85c0287b" }
advised_by: method-steward
---
## CARD
goal: a finance lead follows one document from install to a bound `test-ids` receipt on a reconciliation, and every command in it is one a test actually ran
why: `domains.md` proves the trust spine is domain-general, but it is SKILL surface — an agent loads it at the Verify beat, which a reader reaches only after they have already decided to adopt. Everything before that decision teaches a code project: `GETTING-STARTED.md` walks `POST /transfers` in `src/,tests/` with pytest, and tells the reader to "write those tests now" when there is no code and no runner in their world at all. So the one artifact that would answer "is this for me?" does not exist, and the honest answer is currently reachable only by someone who has finished onboarding. This walkthrough is that artifact, and it is executed rather than asserted: a doc that teaches an unrun command is the same defect this milestone has now found six times.
beat: done · next: add status

## RULES
<must>
- M1 the walkthrough's own commands and files, lifted from the shipped document, drive a real bundle from `init` to a recorded `PASS`
- M2 that receipt reaches the top rung — `kind: test-ids`, with every `covers:` referent bound to a passing id
- M3 the walkthrough shows both refusals actually firing: a threshold breach fails the run, and an artifact edited after the run makes the gate refuse the stale green
- M4 the walkthrough teaches only what ships — a profile the engine honours, floors from the closed set, and no evidence rung the engine cannot stamp
</must>
<reject>
- R:PROSEONLY no command or file may appear in the walkthrough that the test does not execute -> "prose_only"
- R:GATEBUY the walkthrough must never teach a cheaper route to a verdict — no instructed RISK-ACCEPTED, no hand-lowered authority -> "gate_buy"
- R:FIXTUREFORK the test must lift the data, the checker and the rules FROM the document, never carry its own copy -> "fixture_fork"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say whether the reader is assumed able to run Python at all; taking it as yes — the walkthrough asks them to save a ~20-line checker and run it — because ADD's own install already requires Python 3.10+, so a reader who cannot has no path in regardless -> if wrong, the document targets an audience that cannot complete step one, and the real gap is a no-code checker path this task does not build
- A2 [which] covers: S1 · it does not say which reconciliation this is — bank, intercompany, subledger; taking a bank-to-ledger month-end close with a materiality threshold and cited source documents, because that is the shape already proved end to end in `all-domain-evidence` rather than one invented for the page -> if wrong, the numbers read as a toy to the very readers meant to recognise their own work
- A3 [when] covers: S1 · it does not say whether the walkthrough must survive a future engine version or only pass today; taking it as executed on every test run against the shipped engine, so it fails the day a verb or receipt shape moves -> if wrong, it rots exactly like the prose this milestone spent five tasks correcting
- A4 [absent] covers: S1 · it does not say what happens when the reader's artifact is not in git; taking it as stated out loud in the document — freshness degrades to mtime and the receipt says so — rather than quietly assumed, since a reader who skips `git init` would otherwise believe they earned stale-green protection they did not -> if wrong, the walkthrough's central promise is silently conditional
- A5 [order] covers: S1 · it does not say whether the beats may be read out of order; taking them as strictly ordered — freeze precedes any build, and a gate needs a fresh receipt — because that ordering IS the method and a walkthrough that reads as a menu teaches the wrong thing -> if wrong, a reader cherry-picks the gate and gets a refusal they cannot interpret

## PLAN
contract: `add-method/BEYOND-CODE.md` walks one reconciliation from `init --profile doc` to `gate PASS`, with every runnable part behind a named HTML anchor so the test lifts it rather than forking it: the ledger data, the checker, the frozen RULES, the CHECKS, and the run command. The test drives the real vendored CLI in a temp git repo and asserts the receipt, the bindings, and both refusals. Nothing in the document is a claim the test did not execute.
scope: add-method/BEYOND-CODE.md, add-method/tests/skill/

## EDGES
- E1 the two refusals must fail for DIFFERENT reasons and the test must tell them apart: a blown threshold is a failing check inside a valid run, while a post-run edit is a stale-freshness refusal at the gate. A test that only asserts "it refused" would pass if one collapsed into the other.

## CHECKS
- test_walkthrough_runs_end_to_end · covers: M1, M2, R:FIXTUREFORK · lifts every anchored block from the shipped document and drives init → freeze → run → gate in a temp git repo, asserting `kind: test-ids`, `freshness: content` and both referents bound
- test_walkthrough_shows_both_refusals · covers: M3, E1 · a variance over materiality fails the run with the threshold check named, and an artifact edited after the run makes the gate refuse for staleness — asserted as two distinct failures, not one
- test_walkthrough_teaches_only_shipped_surface · covers: M4, R:GATEBUY · every `--profile` it names is in `add.PROFILES`, every floor word is in the closed set, no unstampable evidence kind appears, and it instructs no RISK-ACCEPTED or lowered authority
- test_every_shown_command_is_executed · covers: R:PROSEONLY · every fenced `add …` command line in the document appears in the set the test actually ran
- test_the_shown_sequence_is_sufficient · covers: M1 · the reverse direction — every verb the test had to run to reach a PASS is one the document actually shows, in the same order. ADDED after the first build: the walkthrough omitted `add brief`, so a reader following it literally reaches the gate and is refused with `R:UNBRIEFED`. The forward check could not see it, because a MISSING step is not a shown-but-unrun command. M1 says the walkthrough's own commands drive a bundle to a PASS; a sequence with a hole in it does not.
red-first: every check MUST fail first — the document does not exist yet, and each check reads it before asserting anything, so a missing file is a failure rather than a vacuous pass.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
