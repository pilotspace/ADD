---
type: Milestone
title: A guard asks whether what a stamp attests is TRUE, not whether the stamp is well-formed
status: done
generated: { by: add/3.3.0, at: 2026-09-02 }
verified: []
---
## CARD
goal: every guard asks what a stamp ATTESTS, not merely whether it is well-formed.
why: four critic passes over merged 3.3.0 found the same shape one level below #210: `done` counted that a gate existed and never read its verdict, so a security task with a red run closed on a HARD-STOP.
next: add milestone-done verdict-truth

## SCOPE
In:  add.py's done/gate/freeze/new, the freeze seal, and the engine's public surface census
Out: the skill corpus, the front doors, and the persona roster — those are the other two milestones

## GROUND
touches: add-method/tooling/add.py, add-method/tests/engine/
risks:
  - a seal widened carelessly re-digests every already-frozen node and strands it

## EXIT
- [x] a HARD-STOP no longer entitles the terminal write, and a human may override only as a deliberate act with a reason   (← done-reads-the-verdict)
- [x] every class of id the gate BINDS is inside a freeze seal   (← seal-covers-what-binds)
- [x] a slug names one node bundle-wide, so a receipt cannot cross nodes   (← slug-is-unique-across-types)
- [x] no single engine call spans the ONE human approval, pinned by shape   (← delete-the-unwired-quick-lane)

## CLOSE
evidence:
  - done-reads-the-verdict — PASS at authority `human`, lens gate-security-reviewer, receipt runs/2.md
  - seal-covers-what-binds — PASS, receipt runs/2.md, one re-cross for an unbound Reject
  - slug-is-unique-across-types — PASS, receipt runs/2.md, one re-cross for an unbound Reject
  - delete-the-unwired-quick-lane — PASS at authority `human`, lens gate-security-reviewer, receipt runs/1.md
