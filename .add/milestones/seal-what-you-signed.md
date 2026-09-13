---
type: Milestone
title: A stamp says what it covered — the seal binds the scope it signed
status: direction
generated: { by: add/3.6.0, at: 2026-09-13 }
verified: []
---
## CARD
goal: a freeze stamp records WHICH scope it signed, and every control that reads a stamp as authority names the fields that stamp's digest covers
why: quick-lane-tripwire was refuted EIGHT times, each round finding the same class one gate to the left — matcher, freeze, authority, signature, and finally the SEAL's own coverage. Its security floor is gated HARD-STOP because `scope:` is in neither `direction_digest` (RULES · CHECKS · `gives:`) nor `binding_digest` (EDGES · probed A-ids): hand-adding one entry to a human-frozen node's `scope:` routes a sensitive path with no verb, no new stamp and no name typed, while both stamp digests still verify and `doctor` reports nothing. Two sibling gaps were accepted at that node's round-seven gate and belong here too. All three are one theme: a stamp must say what it covered, and `freeze` must refuse to sign what nobody chose to sign.
next: add new task <slug>

## SCOPE
In:  the freeze/refreeze stamp gains a `scope:` digest · `_scoped_by_any` routes only on the LATEST freeze-class stamp, digest-bound · `freeze` refuses the default `--by cli` at a computed human floor · `freeze` refuses non-lifecycle types · `_scope_files` anchored to the cited commit's tree so a routed DELETION or RENAME has a route · `doctor` gains `scope_moved_after_seal` · `_scoped_by_any` and the owner half read the full scope list and count a refreeze
Out: re-opening A17's matcher (`_paths_touch`) — engine-wide authority is not this milestone's to move · verifying that a `human:` signature belongs to a person, which a notary cannot do · promoting any 3.7 two-mode notice to a refusal (loop-that-closes measured that the count cannot yet decide)

## GROUND
touches: add-method/tooling/add.py (+ 3 twins) · add-method/tests/engine/ · add-method/FORMAT.md · .add/tasks/quick-lane-tripwire.md (its gate reopens here)
risks:
  - an undigested legacy stamp must route NOTHING, so every human-frozen node in every existing bundle stops routing until one human refreeze — fail-closed is correct for a security control, and it is a migration with a cost that must be stated, not discovered
  - `scope:` folded into `direction_digest` would be the cheaper edit, but that function's own docstring says why not: it re-digests every frozen node and a seal that demands reflexive refreezing decays into a rubber stamp
  - this milestone changes the stamp shape, which is the widest blast radius in the engine — every reader of `verified[]` is a candidate for the ONE FACT, MANY READERS class these eight rounds kept finding

## EXIT
- [ ] a freeze/refreeze stamp carries a `scope:` digest; `_scoped_by_any` routes only on the latest freeze-class stamp whose digest matches the node's current scope, and a stamp without one routes nothing   (← scope-in-the-seal)
- [ ] `freeze` refuses the default `--by cli` at a computed human floor, and refuses a type with no lifecycle to seal   (← freeze-refuses-an-unsigned)
- [ ] a lesson about a path a human-frozen node owns lands when the commit DELETED or RENAMED it, and the answer does not depend on which branch the author is standing on   (← holds-against-the-commit)
- [ ] `doctor` names a node whose `scope:` moved after its seal   (← doctor-sees-a-moved-scope)
- [ ] quick-lane-tripwire's HARD-STOP is closed and its gate re-earned at a fresh T2 read   (← quick-lane-tripwire)

## CLOSE
evidence: <one row per task>
