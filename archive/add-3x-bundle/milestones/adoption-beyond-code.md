---
type: Milestone
title: Adoption beyond code — the front door a non-code lead actually hits
status: done
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
- [x] no README states a fact the engine contradicts — bundle files, verb count and shipped profiles all derived from `add.py`/`cli.py`, never pinned   (← front-door-truth)
- [x] `init --profile <unknown>` refuses and names what it does ship, instead of silently writing `code` lenses   (← profile-refusal)
- [x] the profiles named in the shipped docs are exactly the profiles the engine honours — the same both-directions rule the evidence ladder now holds to   (← profile-refusal)
- [x] a non-code reader can run one real task end to end from a doc that a test EXECUTES, earning `kind: test-ids` with `covers:`-bound checks   (← beyond-code-walkthrough)
- [x] the front door reaches the non-code walkthrough as a PEER of the code one — no orphan doc, and no path offered a nesting level down   (← positioning)
      CORRECTED at close. This read "the front door names a non-code audience and reaches the
      non-code walkthrough". The reaching half is done and guarded. The NAMING half is not, and
      correcting the criterion is more honest than claiming it: naming an audience is the same
      human-owned decision as the name itself, which was asked twice and is still unanswered.
      What shipped names the non-code WORK ("a ledger rather than a repo") without asserting who
      ADD is for. See the residual below — that is a deferred decision, not a delivered one.
- [x] the shipped SKILL stops describing the fallback the engine change removed, in all three trees   (← skill-profile-truth)
      ADDED mid-milestone, not planned at intake. `profile-refusal` turned two skill sentences false
      within minutes of landing, in 9 places, and nothing failed. The milestone's own defect class,
      caught inside the milestone.
- [x] zero floor names introduced outside `security · data · architecture`, and no evidence rung added   (← profile-refusal)

## CLOSE
evidence:
- front-door-truth        — runs/3.md · 9 checks · PASS at process authority (re-gated after a reopen; see below)
- profile-refusal         — runs/2.md · 8 checks · PASS at plan authority (architecture floor), advised by engine-notary
- beyond-code-walkthrough — runs/1.md · 5 checks · PASS · the walkthrough EXECUTED end to end, both refusals proved distinct
- skill-profile-truth     — runs/1.md · 5 checks · PASS · discovered mid-milestone
- positioning             — runs/1.md · 4 checks · PASS
suite: 686 passed, 7 skipped (663 at milestone start). Engine bytes: CHANGED, deliberately — the
"no engine change" constraint was scoped to the previous milestone's skill work and was lifted here.

**The finding.** Seven false claims on shipped surface, all found by writing a guard that asks the
engine instead of asking a person: `state.json` (×4, dead since 3.0), the verb count (×3, two
different wrong numbers), `PLAN.md` (×6), `add.py status` (×3, a library that prints nothing), the
`--profile doc` affordance named nowhere, the installer flag that is silently ignored, and the
silent `code` fallback the engine had already stopped doing. Not one was caught by review. Every
one was caught in minutes by a check that derives.

**Three defects this milestone introduced and then caught — all in the same class it was fixing:**
1. `front-door-truth` shipped `npx @pilotspace/add init --profile doc` through a GREEN GATE. M5
   said "every engine command a README shows"; its check executed only `<engine>.py <verb>` forms.
   The rule quantified over a set the check never enumerated. Repaired via `reopen --to build
   --reason`, so the miss is permanent record rather than a quiet second gate.
2. `profile-refusal` made two shipped SKILL sentences false in 9 places within minutes, and nothing
   failed → `skill-profile-truth`.
3. `beyond-code-walkthrough` omitted `add brief`. Every check passed because the TEST ran it — a
   missing step is not a shown-but-unrun command. The walkthrough worked; following the walkthrough
   did not.
The pattern behind all three: **a gate proves the checks you declared ran and bound. When a rule
quantifies over a set, the check must enumerate that set — in both directions.**

**Open residuals, none of them silent:**
- **the identity decision — the milestone's one undelivered intent.** ADD still reads as AI-driven
  *Development* in its name, tagline, package names and book title. Asked twice, unanswered, so
  `positioning` was scoped to reachability and `R:IDENTITYCREEP` proves it did not drift the name
  while editing the two files where the name lives. A follow-up owns this.
- three shipped PNGs render `state.json`, `PLAN.md` and the retired `§0…§7` numbering. No text edit
  reaches a rasterised word; the alt text no longer restates the claims and the README says the
  diagrams are pending redraw.
- `add-method/.add/tooling/add.py` — the book bundle's vendored engine, drifted BEFORE this
  milestone and untracked. Out of scope, still drifted.
- the general prose-vs-engine drift guard: this milestone did the front-door and skill slices only.
- `GETTING-STARTED.md` remains the code walkthrough by design; `BEYOND-CODE.md` is its peer.
