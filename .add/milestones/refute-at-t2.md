---
type: Milestone
title: Refute at T2 — the independent read becomes the default, and the record can count it
status: direction
generated: { by: add/3.6.0, at: 2026-09-10 }
verified: []
advised_by: method-steward
---
## CARD
goal: a plan-or-human-floor green is read by a session that did not build it, by default; the refute stamp says which tier read it and what its probes changed; and a Must carrying one evidence mode is named before the freeze — so the next dogfood can count independence and probe yield from stamps alone
why: dogfood-and-measure measured evidence-over-tests on itself and found its central claim UNMEASURED — every refute was the builder reading its own green (T1), the tier lived only in free text inside `--by`, a probe that changed the build was stamped `held` and so undercounted, and the two-mode rule the session wrote was followed by 0 of 10 Musts one task later. A rule nobody follows and a stamp nobody can count are the same defect: prose that binds nothing
next: add new task <slug>

## SCOPE
In:  `add refute --tier T1|T2|T3` and `--changed "<what>"` as stamp keys, rendered in EVIDENCE and stated in FORMAT §8.4; a freeze-time NOTICE (never a refusal) naming the plan-floor Musts whose covering checks share one evidence mode, the mode word parsed from the closed set; the verify beat's default at floor ≥ plan becomes a SPAWNED fresh refuter (`add-advisor` refute mode, briefed from the frozen node before the diff) recorded at T2, with T1 as the builder's optional prelude; docs 03/05/13 and the cookbook line; one direct fix of the docs/03 "acceptance mode" sentence.
Out: a mode-mismatch REFUSAL at freeze or gate (measure compliance on this milestone first; promote or drop next), a PROOFS schema, a bench (designed only if probes-that-changed is 0 across this milestone), any change to the tier ladder's wording of T0/T4, the README tagline (human-owned wording), and every part of the trust spine the previous milestone kept.

## GROUND
touches: add-method/tooling/{add.py,cli.py} + _bundled/tooling twin + engine_pin repin · add-method/FORMAT.md §8.4 · add-method/skill/add/{SKILL.md,phases/verify.md,phases/direction.md} + two twins · add-method/agents/{add-worker,add-advisor}.md + two twins · add-method/docs/{03,05,13}.md · add-method/tests/{engine,skill}
risks:
  - a `--tier` recorded by the same session that built is still presence-only: the flag makes the CLAIM countable, not true — say so in §8.4 and let the dogfood read `by:` beside it
  - the notice becomes noise on every quick task or process-floor freeze and gets tuned out — arm it only where the rule applies (standard|deep × floor ≥ plan) and print nothing otherwise
  - SKILL.md has 4 bytes of headroom under its byte pin and 0 lines under its line pin; the spawn-default line must be funded by compressing the cookbook, never by raising a budget
  - a new flag ripples FORMAT · docs 13 · cookbook ×3 · EVIDENCE view · tests; the mirror-gap check fails publish if a twin is missed

## EXIT
- [ ] `add refute` records `tier:` and `changed:` on the stamp when given, refuses a tier outside T1–T3, renders both in EVIDENCE, and FORMAT §8.4 states them   (← refute-tier-and-changed)
- [ ] at standard|deep × floor ≥ plan, `add freeze` succeeds AND names every Must whose covering checks carry exactly one mode word; quick · process floor · explore · Rejects · edges print nothing   (← two-mode-notice)
- [ ] verify.md, SKILL.md, add-worker.md and docs 05 say the T2 spawn is the default at floor ≥ plan and T1 is a prelude, parity-pinned across twins; the cookbook line carries `--tier`   (← t2-refute-default)
- [ ] docs/03 no longer says acceptance mode is for "where no unit test fits"   (← direct: docs-03-acceptance-default)
- [ ] every refute recorded on this milestone's own tasks is tier T2 by a spawned session, and the close names probes-that-changed-something   (← this milestone, at close)

## CLOSE
evidence: <one row per task>
