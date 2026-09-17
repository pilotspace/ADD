---
type: Milestone
title: One approval binds one complete decision set
status: direction
generated: { by: add/3.6.0, at: 2026-09-16 }
verified: []
---
## CARD
goal: make one human approval name the immutable complete decision candidate it covers
why: the current interview digest seals only the questions `_open_decisions` happens to ask, so sourced Musts, published surfaces, retired assumptions, and other non-question declarations disappear from the approval record; a refreeze cannot show what was added, changed, or removed, and a legacy stamp cannot distinguish unknown coverage from a complete candidate
next: complete the `seal-what-you-signed` dependency, preserve stable Milestone EXIT identities, then review and interview decision-manifest-binds-approval

## SCOPE
In: one immutable schema-v1 decision manifest per frozen node · complete Task S/M/R/A/E and Milestone C candidate inventories with authored stable IDs · a `decisions:` digest plus `decision_schema: 1` on freeze/refreeze · the existing per-node interview as the question subset · an added/changed/removed/unchanged refreeze delta plus a separately computed whole-interview stale set · fail-closed reads of a claimed manifest · an explicit unknown baseline for legacy stamps
Out: a second approval · answers inside the manifest · inferred answers from omissions, Git identity, persona output, or empty input · cross-node or milestone-wide approval of security Tasks · identity authentication · lowering authority, gate, or HARD-STOP rules · changing `confirm|correct|defer` meanings · implementing scope seals or stable EXIT IDs in this milestone

## GROUND
touches: add-method/tooling/add.py (`_open_decisions`, `interview_digest`, `interview_gap`, `interview`, `freeze`, `exit_digest`, `direction_digest`, flow-map stamps) · add-method/tests/engine/test_freeze_interview.py · add-method/tests/engine/test_scope_in_the_seal.py · add-method/tests/engine/test_moved_is_a_real_exit_state.py · add-method/FORMAT.md
risks:
  - the candidate inventory and the question set are different facts: compiling only `_open_decisions` would produce a stable but incomplete approval record, while treating every candidate row as a question would add ceremony and silently change the current interview contract
  - this work consumes human authority and stamp truth, so Build depends on the separate scope-seal Task, stable authored Milestone EXIT IDs, and one real human interview for this security Task; no existing approval is carried over

## EXIT
- [ ] C1 every Task freeze/refreeze is bound to a complete immutable schema-v1 S/M/R/A/E manifest, and every Milestone freeze/refreeze is bound to a complete immutable schema-v1 C manifest whose authored IDs survive reorder   (← decision-manifest-binds-approval)
- [ ] C2 refreeze presentation distinguishes candidate added/changed/removed/unchanged rows from the current whole-interview stale set and preserves the existing sparse `confirm|correct|defer` semantics   (← decision-manifest-binds-approval)
- [ ] C3 a claimed missing, malformed, or digest-mismatched manifest refuses without a stamp, while a legacy stamp with no manifest claim is reported as unknown and gains a full baseline only on refreeze   (← decision-manifest-binds-approval)
- [ ] C4 manifests contain no answers and cannot aggregate or satisfy another security Task's interview, freeze, gate, or HARD-STOP requirement   (← decision-manifest-binds-approval)

## CLOSE
evidence: <one row per task>
