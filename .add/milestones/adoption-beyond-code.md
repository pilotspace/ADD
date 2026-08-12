---
type: Milestone
title: Adoption beyond code — the front door a non-code lead actually hits
status: direction
generated: { by: add/3.1.0, at: 2026-08-12 }
verified: []
advised_by: method-steward
---
## CARD
goal: a finance or research lead can read the front door, install, and run one real task to a bound receipt — without ever being told they are in the wrong place
why: `all-domain-evidence` proved the trust spine is domain-general and wrote `domains.md` to say so. But `domains.md` is a skill ref — an agent loads it at the Verify beat, which a non-code adopter reaches only after deciding to adopt. Everything BEFORE that decision is still code-only: both READMEs say `state.json` (a 2.x marker the engine's own comment calls dead), disagree with each other on the verb count (31 vs 21, where the CLI registers 22), and never once name `--profile doc` — the single non-code affordance already shipping. The walkthrough teaches one feature, `POST /transfers`, in `src/,tests/`. And `init --profile finance` still silently writes code lenses. Four walls, all hit before `domains.md` is ever loaded.
next: add freeze front-door-truth

## SCOPE
In:  both READMEs (truth, then positioning) · a runnable non-code walkthrough at `add-method/BEYOND-CODE.md` · `init --profile` refusing what it cannot honour · guards that derive their expectation from the engine
     NOTE: intake also wrote "plus the profiles the walkthrough needs" into this line. Corrected before `profile-refusal` was frozen: whether `code`/`doc` actually serve a reconciliation is a question the walkthrough ANSWERS, so adding a profile now would be guessing ahead of the evidence. If `doc` mis-serves it, that lands as its own decision — and shipping a domain profile names a domain ADD claims, which is human-owned like the naming question still open.
Out: the name "AI-Driven Development" and the `@pilotspace/add` package identity — human-owned, and unanswered at intake · the domains book chapter · the general prose-vs-engine drift guard (this milestone does the front-door slice only) · `add-method/.add/tooling/add.py`, an untracked book-bundle twin already drifted BEFORE this milestone · rewriting `GETTING-STARTED.md`'s code walkthrough, which stays the code walkthrough

## GROUND
touches: README.md · add-method/README.md · add-method/BEYOND-CODE.md (new) · add-method/tooling/add.py + its two live twins (`src/add_method/_bundled/tooling/`, `.add/tooling/`) · add-method/tests/skill/ · add-method/tests/
risks:
  - **this milestone edits the engine the milestone is being driven by.** `.add/tooling/add.py` is the copy every `freeze`/`gate` in this run executes. A bad edit does not fail a test, it breaks the notary mid-flight — so `profile-refusal` lands canonical-first, runs the suite, and only then re-vendors.
  - a refusal where there was silence is a **breaking CLI change**: anyone scripting `init --profile <typo>` gets an exit code they did not get yesterday. That is the point, and it is why the task carries the architecture floor — but the refusal must name the shipped set, or it trades a silent wrong answer for an unhelpful one.
  - shipping a `finance` profile to serve the walkthrough is the additivity promise under test: a profile selects LENSES, never rules. A profile that changed what passes would invert the method. Lens names only, no floor words, no new evidence kinds.
  - README claims are the loudest surface ADD has and the least guarded — the corrected numbers rot again the day the next verb lands unless the guard DERIVES them (`test_evidence_ladder.py`'s extractor is the pattern; a pinned literal is the failure mode it exists to prevent).
  - a walkthrough that is only prose is exactly the artifact this milestone is fixing. It has to be executed by a test, the way `domains.md`'s recipe is, or it is another unchecked claim.

## EXIT
- [ ] no README states a fact the engine contradicts — bundle files, verb count and shipped profiles all derived from `add.py`/`cli.py`, never pinned   (← front-door-truth)
- [ ] `init --profile <unknown>` refuses and names what it does ship, instead of silently writing `code` lenses   (← profile-refusal)
- [ ] the profiles named in the shipped docs are exactly the profiles the engine honours — the same both-directions rule the evidence ladder now holds to   (← profile-refusal)
- [ ] a non-code reader can run one real task end to end from a doc that a test EXECUTES, earning `kind: test-ids` with `covers:`-bound checks   (← beyond-code-walkthrough)
- [ ] the front door names a non-code audience and reaches the non-code walkthrough — no orphan doc   (← positioning)
- [ ] zero floor names introduced outside `security · data · architecture`, and no evidence rung added   (← profile-refusal)

## CLOSE
evidence: <one row per task>
