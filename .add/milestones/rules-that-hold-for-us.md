---
type: Milestone
title: the rules we bound today hold for our own tree
status: done
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
---
## CARD
goal: the four decisions this project bound yesterday are true of this project's own code, and no check in the suite fails by calendar
why: `loop-that-drains` wrote 18 decisions into the living specs, and three of them describe defects still standing in this tree — a verb with two refusal shapes, a scope guard pinned to the working tree, and one budget asserted by seven separate files. A decision every future brief carries, that the codebase itself violates, teaches an agent that decisions are advisory. Separately, one check fails by CALENDAR, so CI is red on main today and every day after.
next: add freeze rules-that-hold-for-us

## SCOPE
In: the date-dependent search check · freeze's two falsy refusal shapes · the one guard pinned to a working-tree diff · the seven independent skill-budget assertions
Out: the 3.6.0 release itself, which wants PR 217 merged first and a human-owned tag · widening R:UNCOVERED to Musts and Rejects, which needs its own measured task · authoring a domain decision, which is a human's to write · the Quick lane's untraced learn line

## GROUND
touches: add-method/tooling/add.py and its three twins · add-method/tests/engine · add-method/tests/skill
risks:
  - a refusal-shape change touches a verb every suite drives; the survey must precede the edit, and the full suite must run before the receipt (B-M3)
  - collapsing seven budget assertions risks deleting a guard rather than consolidating it, which is exactly the shape M22 names — every removed assertion must be provably still made by the one that remains
  - a date-stable rewrite must not become a test that asserts nothing: the fix is a fixed clock, never a loosened assertion

## EXIT
- [x] no check in the suite depends on the calendar date it is run: the search filter check pins its clock and still fails when the filter regresses   (a task)
- [x] `freeze` refuses with ONE falsy shape, and a check proves a caller testing that shape sees every rung   (a task)
- [x] every scope guard names the commit range it guards; none is satisfied by committing   (a task)
- [x] the skill budget is asserted by ONE guard that the others call, and an overrun reports one failure   (a task)
- [x] the full suite is green with zero known failures, on any date   (all)

## CLOSE
evidence: one row per task, recorded at close
