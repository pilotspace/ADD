---
type: Milestone
title: A refusal names a fix that runs and actually clears it
status: done
generated: { by: add/3.3.0, at: 2026-09-02 }
verified: []
---
## CARD
goal: a refusal names a fix that runs, and a verb reads the flag it accepts.
why: the engine was steering users into the holes Tier 1 had just closed: its own build hint guaranteed `ids: unknown`, and the gate then offered a signed waiver as the only exit from correct work.
next: add milestone-done refusals-that-work

## SCOPE
In:  BEAT_NEXT and the refusal messages, run/gate/freeze flag handling, the brief's lens resolution, the seeded persona templates
Out: the freeze seal and the verdict semantics — that is verdict-truth

## GROUND
touches: add-method/tooling/add.py, add-method/tooling/cli.py, add-method/tooling/templates/personas/, add-method/tests/engine/
risks:
  - a refusal reworded without re-reading its call sites moves the defect rather than fixing it

## EXIT
- [x] `run` refuses a node that does not exist instead of fabricating a receipt   (← run-refuses-a-phantom-node)
- [x] no verb accepts a flag it silently discards, and no claim sinks below a computed floor   (← gate-honours-or-refuses-authority)
- [x] every `next:` line runs as printed and clears what it was named for   (← next-lines-are-runnable)
- [x] a recorded lens reaches the brief that spawns the worker   (← the-persona-reaches-the-worker)
- [x] every seeded persona orients with commands the engine actually has   (← seeded-personas-orient-on-real-verbs)

## CLOSE
evidence:
  - run-refuses-a-phantom-node — PASS, receipt runs/1.md
  - gate-honours-or-refuses-authority — PASS, receipt runs/1.md
  - next-lines-are-runnable — PASS, receipt runs/1.md
  - the-persona-reaches-the-worker — PASS, receipt runs/1.md
  - seeded-personas-orient-on-real-verbs — PASS, receipt runs/1.md
