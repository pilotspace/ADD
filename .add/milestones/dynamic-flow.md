---
type: Milestone
title: Dynamic Flow — adaptive path, deterministic trust
status: done
generated: { by: add/3.0.0, at: 2026-08-11 }
verified: []
---
## CARD
goal: an uncertain request runs Explore-first to a cited findings brief, mid-build steering is recordable without re-freeze, and every trust floor (freeze · receipts · security HARD-STOP) holds byte-identical
why: ADD 3.0 is pure fixed-path workflow; the field's validated gains (effort-as-decision · research loops · replanning) are all path-side, and ADD's path has no adaptivity at all
next: direction on explore-lane

## SCOPE
In:  add-method/skill/add + .claude/skills/add mirror (lane, phases, intake, streams) · add-method/tooling + .add/tooling (sources rung, replan stamp)
Out: freeze authority · gate verdict logic · security floors · wave/join write-safety · any new ABF node type (Explore = Task + kind:explore)

## GROUND
touches: add-method/skill/add · .claude/skills/add · add-method/tooling · .add/tooling
risks:
  - SKILL.md is byte-pinned at exactly 12,288 — the Explore lane must be funded by compressing existing prose, never by raising the budget
  - engine edits ripple into twin trees + engine_pin; both engine tasks carry sensitivity architecture (plan floor) for that reason
  - a "dynamic" lane that quietly lowers a floor would invert the method — every task's Reject set must pin the floors

## EXIT
- [x] an explore request runs end-to-end: scoped questions + budget → query/read/reflect/refine → compressed cited ## FINDINGS → recorded sufficiency gate   (← explore-lane, sources-receipt)
- [x] a downstream task consumes the brief via needs: /tasks/<explore>.md#findings and add brief compiles it into Direction   (← explore-lane)
- [x] a high-unknown request is routed Explore-first at intake by an explicit unknowns score the human vetoes   (← uncertainty-routing)
- [x] a mid-build steering amendment lands as a replan record with no re-freeze; a frozen gives: change still demands one   (← replan-verb)
- [x] a priced assumption is discharged by recorded evidence (· found:) instead of a guess in a live run   (← assumption-microspike)
- [x] read-only beats fan out with no wave ceremony; build-wave behavior unchanged   (← read-fanout)
- [x] full suite green; freeze/gate/security behavior byte-identical; SKILL.md still exactly 12,288   (← all)

## CLOSE — ship review

Ship by domain:
- **skill** — `phases/explore.md` NEW (94 lines) · intake.md (+Explore lane · +unknowns tally · +floor-first routing · classification carries depth) · `phases/direction.md` (+micro-spike discharge) · `phases/build.md` (+steering-vs-contract split) · streams.md (+read fan-out) · SKILL.md (+Explore lane + `--kind explore`, exactly 150/150 lines) — all three trees byte-identical
- **tooling** — add.py: `replan()` verb + explore budget floor (R:UNBOUNDED) + sufficiency gate (R:HOLLOW_EXPLORE, `kind: sources` stamp) · cli.py: replan parser+dispatch · engine_pin.py: both pins re-aimed with prior pointers — all three tooling twins byte-identical
- **book** — 13-command-reference.md (+replan row, docs + root mirror)

Cross-task evidence (gate · tests · residue):
- explore-lane        — PASS (process) · 42/42 · clean
- uncertainty-routing — PASS (process) · 57/57 · clean
- assumption-microspike — PASS (process) · 57/57 · clean
- read-fanout         — PASS (process) · 57/57 · clean
- replan-verb         — PASS (plan)    · 623/623 full suite · clean (1 disclosed design call)
- sources-receipt     — PASS (plan)    · 623/623 full suite · clean

Goal met? — each criterion below maps to the receipts above; the full suite finished
623 passed / 0 failed / 7 skipped, and no freeze/gate/security behavior moved (the whole
pre-existing engine suite ran unmodified).

## Release steps
- [x] review the working tree and commit (tmp/ commit-msg ritual)
- [x] PR + reviewers — human call (PR #197, merged 2622b3fd)
- [ ] npm/PyPI cut rides the normal release ritual, NOT this milestone
