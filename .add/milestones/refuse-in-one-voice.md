---
type: Milestone
title: the loop refuses in one voice, and early
status: done
generated: { by: add/3.6.0, at: 2026-09-10 }
verified: []
---
## CARD
goal: every verb refuses with the same falsy shape, and the checks a task owes are demanded at the freeze rather than discovered at the gate
why: two checks in one branch were GREEN only because `freeze` refused with `False` and `False is not None` — 11 verbs still answer that way, so the class is live. And the gate is the wrong place to learn a Must has no check: by then the whole build is done, when the fix is one line of authoring
next: add new task <slug>

## SCOPE
In:  the falsy first element every engine verb returns on a refusal, the checks that assert on it, and the R:UNCOVERED rung that decides which authored obligations owe a check.
Out: the refusal MESSAGES (untouched, byte for byte), `cli.py`'s exit codes (which read the same element by truthiness and are unaffected), and the gate rung, which still refuses a check deleted after the seal.

## GROUND
touches: add-method/tooling/add.py (+ 3 twins) · add-method/tests/engine/
risks:
  - a caller that tests the refusal by truthiness passes under BOTH shapes, so the change looks safe and the check that was already vacuous stays vacuous — the reason M6 enumerates the callers instead of trusting the suite

## EXIT
- [x] every verb in the engine refuses with `None`, and a check enumerates them so a new verb cannot answer differently   (a task)
- [x] `freeze` refuses a Must or a Reject that no check covers, naming it — the same rung that already binds edges and probed assumptions   (a task)
- [x] no check anywhere asserts a refusal by truthiness where identity is what it means   (all)
- [x] the full suite is green, and the two changes are separable in history   (all)

## CLOSE
evidence: recorded at close
