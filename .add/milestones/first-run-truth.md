---
type: Milestone
title: The first run a stranger walks is the run the engine actually performs
status: direction
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:75a11da44c802486" }
---
## CARD
goal: Every instruction on the path a newcomer walks — `status` in a subdirectory, the GETTING-STARTED walkthrough, the `add run` line, the README's cost and ceremony claims — either matches what the engine does or is deleted, and the walkthrough is executed by the suite rather than asserted by prose.
why: A four-lens review on 2026-09-01 walked the documented path in a fresh scratch repo and it fails at
  four separate points, each independently reproduced. `status` from any subdirectory prints
  `next: add init` with NO ancestor guard anywhere in the engine — following the engine's own instruction
  builds a second competing bundle, destroying the "state on disk is the source of truth" claim the README
  leads with. `GETTING-STARTED.md:305` promises freeze refuses template placeholders; a node froze with
  five surviving, because `placeholders_in` scans only RULES · ASSUMPTIONS · CHECKS. The guide omits
  `--authority human`, so the entire documented walkthrough records `authority: process` — a ledger
  indistinguishable from an unattended agent stamping itself. The `add run --junitxml … -- <test cmd>`
  idiom, printed identically in three canonical places, never passes the path to the wrapped command, so
  the first receipt a newcomer earns is `command-exit` and the gate refuses it naming `unbound_covers` —
  a message that says nothing about the missing flag. And `README.md:58` claims "a 3-call task walk" and
  "the cheap option" when the real minimum is five calls (`brief` is enforced by R:UNBRIEFED) and this
  repo's own benchmark has ADD at $17.51 against spec-kit's $10.05 at identical scores. The root cause is
  structural, not clerical: `BEYOND-CODE.md`'s non-code walkthrough is executed by a test and holds;
  the primary code walkthrough is executed by nothing. This milestone closes the asymmetry.
next: add milestone-done first-run-truth

## SCOPE
In:  the ancestor-bundle guard on `status` and `init` · the derived beat that `status` and `brief` report ·
  an executed GETTING-STARTED walkthrough test and the doc corrections it forces · the `add run` receipt
  idiom in all three canonical spots · the README's cost/ceremony claims and the missing direct-lane
  ladder · the `doctor` write-claim and the skill's stale `version:` with the parity test that missed it.
Out: the persona tier (live-persona-tier) · the agent roster (roster-reachable) · the `## EDGES`
  documentation gap (edges-documented) · any new verb · the book chapters under `docs/`.

## GROUND
touches: add-method/tooling/add.py · add-method/GETTING-STARTED.md · add-method/README.md · add-method/skill/add · add-method/tests · add-method/src/add_method/_bundled
risks:
  - Extending `placeholders_in` to CARD `goal:` will refuse the next refreeze of any existing bundle that
    carries a template goal — the guard must be scoped to `goal:` alone, never to EVIDENCE or LESSONS,
    which are legitimately unfilled before the run that produces them.
  - SKILL.md is pinned at EXACTLY 176 lines by three tests; every added line is funded by compression.
  - Any `add.py` edit re-aims `ENGINE_MD5` and ripples to four live twins.

## EXIT
- [ ] `status` in a subdirectory names the ancestor bundle and `init` refuses under one without `--nested`   (← nested-bundle-guard)
- [ ] `status` and `brief` report the derived beat, so a frozen node never reads `direction`   (← beat-read-truth)
- [ ] The GETTING-STARTED walkthrough is executed by the suite, and every claim it makes about freeze holds   (← getting-started-executed)
- [ ] The `add run` line the skill prints earns a `test-ids` receipt when copied verbatim   (← receipt-idiom-truth)
- [ ] No cost or ceremony claim on the front door is contradicted by this repo, and the direct lane is visible   (← front-door-claim-truth)

## CLOSE
evidence:
