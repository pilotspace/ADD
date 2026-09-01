---
type: Task
title: The walkthrough the front door prints is a walkthrough the suite executes
status: direction
depth: standard
milestone: first-run-truth
scope:
  - add-method/GETTING-STARTED.md
  - add-method/tests/skill
  - add-method/tooling/add.py
gives:
  - S1 `tests/skill/test_getting_started_walkthrough.py` — the suite that EXECUTES the front-door walk
  - S2 the GETTING-STARTED command lines — the flags a reader is told to type
  - S3 `placeholders_in` — the sections freeze admits on
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:90df4ec4776861dc" }
---
## CARD
goal: The walkthrough GETTING-STARTED prints is executed end to end by the suite, every claim it makes about `freeze` is true when executed, and the approval it teaches records as a human one.
why: `BEYOND-CODE.md:12` says every command in it is executed by `tests/skill/test_beyond_code_walkthrough.py`, and that file exists. The PRIMARY code walkthrough — the file most people actually read — is executed by nothing: `tests/test_shipped_docs.py:87` checks GETTING-STARTED only for phantom verbs, and `test_promised_capabilities.py` covers README highlight bullets, admitting at its own line 18 that it cannot judge whether the thing is what the bullet describes. That asymmetry is the root cause; the three defects below are its symptoms, each reproduced 2026-09-01 by walking the guide literally in a scratch repo. (1) `:305` claims freeze "refuses a node that still carries template placeholders — you cannot approve a scaffold"; a node froze with five placeholders surviving, because `placeholders_in` (add.py:2796) scans only RULES · ASSUMPTIONS · CHECKS and matches only lines starting `- `, so CARD's `goal: <one line>` is invisible to it. (2) `:301` shows `add freeze transfer --by "your name"` with no `--authority human`, so the documented walk records `authority: process` — a ledger indistinguishable from an unattended agent stamping itself, which is exactly the audit question a lead asks before adopting. SKILL.md:150 gets this right; the agent-facing doc is correct and the human-facing one is not, which is backwards. (3) the same walk earns no human authority stamp anywhere, freeze or gate. One executed test closes the class, not just the three instances.
beat: direction · next: add freeze getting-started-executed

## RULES
<must>
- M1 A test executes the GETTING-STARTED walkthrough in a temporary bundle: every command block, in order, with the guide's literal flags, asserting each verb's documented outcome.
- M2 `freeze` refuses a node whose `## CARD` still carries a template `goal:`, and the refusal names CARD.
- M3 `## EVIDENCE` and `## LESSONS` remain exempt from the placeholder guard — they are filled by the run and the close, which do not exist at freeze time.
- M4 The guide's freeze line carries `--authority human`, and the walkthrough test asserts the resulting stamp reads `authority: human`.
- M5 Every claim the guide makes about a refusal is executed by the test, not merely printed.
</must>
<reject>
- R:UNEXECUTEDDOC the front-door walkthrough must never assert an engine behaviour no test executes -> "R:UNEXECUTEDDOC"
- R:PROCESSAPPROVAL the documented ONE approval must never record as a process stamp -> "R:PROCESSAPPROVAL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S2 · the request does not say whose name the guide should show; taking a placeholder name plus `--authority human`, because the flag is what makes the stamp human and the name is the reader's own -> if wrong the reader copies a literal name into their ledger · probe: the guide's freeze line carries the flag and a self-evidently substitutable name.
- A2 [which] covers: S3 · the request does not say WHICH sections the placeholder guard should cover; taking CARD's `goal:` and nothing else new — EVIDENCE and LESSONS are legitimately unfilled before the run -> if wrong the guard demands a receipt before the build that produces it · probe: a node with template EVIDENCE and LESSONS still freezes.
- A3 [when] covers: S3 · the request does not say what happens to bundles ALREADY holding a template goal; taking the refusal as it comes — the next REFREEZE refuses and names CARD, and nothing already frozen is rewritten -> if wrong an existing bundle is silently invalidated or history is edited · probe: an existing frozen stamp is untouched; only the next freeze is judged.
- A4 [absent] covers: S1 · the request does not say what a MISSING command block means; taking the test as the authority — a block the guide prints and the test does not execute fails the test -> if wrong the guide grows a block nobody runs, which is the defect · probe: the test enumerates the guide's blocks from the FILE, never from a hand list.
- A5 [order] covers: S1 · the request does not say the order to execute in; taking the guide's own printed order, because that is what the reader does -> if wrong the test passes on a sequence no reader follows · probe: the test's sequence is read from the document.
- A6 [experience] covers: S2 · the request does not say what the reader should feel at the refusal; taking a message that names the SECTION (CARD) and the line, because "a placeholder" without a location teaches nothing -> if wrong the reader hunts · probe: the refusal names CARD.
- A7 [who] covers: S1 · n/a · the suite runs as one actor.
- A8 [who] covers: S3 · n/a · `placeholders_in` is a pure section scan taking no actor.
- A9 [which] covers: S1 · n/a · A4 fixes the block set: enumerated from the document.
- A10 [which] covers: S2 · n/a · the guide's blocks are exactly the set A4 enumerates.
- A11 [when] covers: S1 · n/a · the test runs in a temporary bundle with no boundary of its own.
- A12 [when] covers: S2 · n/a · a document has no temporal boundary; A3 carries the migration reading.
- A13 [absent] covers: S2 · n/a · A4's reading governs: a block absent from the test is a failure.
- A14 [absent] covers: S3 · n/a · an absent `## CARD` is already an unauthored node, refused upstream.
- A15 [order] covers: S2 · n/a · A5 fixes the order for the guide and its test together.
- A16 [order] covers: S3 · n/a · the placeholder scan is order-independent across sections.
- A17 [experience] covers: S1 · n/a · a test's audience is CI, and its failure message is the assertion.
- A18 [experience] covers: S3 · n/a · the scan prints nothing; its experience is the refusal in S2's surface.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: a new `tests/skill/test_getting_started_walkthrough.py` that parses the guide's command blocks from the file and executes them in a temp bundle; `placeholders_in` additionally scans `## CARD` for a template `goal:`; the guide's freeze and refreeze lines carry `--authority human`.
scope: add-method/GETTING-STARTED.md, add-method/tests/skill, add-method/tooling/add.py

## EDGES
- E1 a node with template EVIDENCE and LESSONS but a filled CARD — freezes (M3, A2).
- E2 an already-frozen node carrying a template goal — its existing stamp is untouched; only the next refreeze refuses (A3).
- E3 a Milestone — `milestone_why_unset` already guards `why:`; the new CARD scan must not double-refuse or change its message.
- E4 a `--depth quick` task — the CARD guard applies at every depth, unlike the assumption sweep.
- E5 a guide block that is illustrative output rather than a command — the parser must not try to execute it.

## CHECKS
- test_the_getting_started_walkthrough_runs_green · covers: M1, A5 · every block executes in order with the guide's literal flags.
- test_the_walkthrough_blocks_come_from_the_document · covers: A4, A9, R:UNEXECUTEDDOC · the block set is parsed from the file, not hand-listed.
- test_freeze_refuses_a_template_card_goal · covers: M2, A6 · the refusal fires and names CARD.
- test_freeze_still_admits_template_evidence_and_lessons · covers: M3, A2, E1 · the pre-run sections stay exempt.
- test_the_documented_freeze_records_human_authority · covers: M4, R:PROCESSAPPROVAL · the stamp reads `authority: human`.
- test_every_refusal_the_guide_claims_is_executed · covers: M5 · each claimed refusal has an executing assertion.
- test_an_existing_frozen_stamp_is_not_rewritten · covers: A3, E2 · history is append-only.
- test_a_milestone_why_guard_is_unchanged · covers: E3 · `milestone_why_unset` keeps its own message.
- test_the_card_guard_applies_at_quick_depth · covers: E4 · depth does not exempt it.
- test_illustrative_output_blocks_are_not_executed · covers: E5 · the parser distinguishes command from output.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- Executing the front door found what reading it could not: the walk assumes a git working tree AND that the declared `scope:` paths exist, and said neither. A walkthrough test finds preconditions, not just wrong flags -> add learn add
- `freeze`'s milestone-scaffold refusal returns `False` where every other refusal returns `None`. The CLI's truthiness check hides it, so it is latent, not live — but a library caller testing `node is None` reads a refused freeze as a success -> add learn add
