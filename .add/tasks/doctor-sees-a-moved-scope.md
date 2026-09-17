---
type: Task
title: doctor-sees-a-moved-scope
status: direction
depth: standard
sensitivity: security
milestone: seal-what-you-signed
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tests/engine
  - add-method/FORMAT.md
  - add-method/CHANGELOG.md
gives:
  - S1 `doctor` reports a lifecycle node whose current `scope:` digest no longer equals its latest freeze-class scope digest
  - S2 `doctor` reports a lifecycle node whose latest freeze-class stamp has no readable scope seal
generated: { by: add/3.6.0, at: 2026-09-13 }
verified: []
advised_by: engine-notary
---
## CARD
goal: doctor makes a scope moved after its seal visible to the operator who can refreeze it
why: a scope edit currently changes routing authority without changing either seal digest and doctor reports a clean node
beat: direction · next: add interview doctor-sees-a-moved-scope, then add freeze doctor-sees-a-moved-scope --by "human:<name>"

## RULES
<must>
- M1 `doctor` reports `scope_moved_after_seal` for a lifecycle node whose latest freeze-class scope digest differs from its current scope digest (from: /milestones/seal-what-you-signed.md EXIT 4 · fails-on: a post-seal scope edit remains invisible to the conformance report)
- M2 `doctor` reports `scope_seal_missing` for every lifecycle node whose latest freeze-class stamp omits or malforms the scope digest (from: /milestones/seal-what-you-signed.md GROUND migration · fails-on: legacy human-frozen work stops routing with no explanation)
- M3 each finding names the affected node and refreeze remedy without writing or repairing its scope (from: /personas/engine-notary.md Critical Rules · fails-on: doctor silently changes the record it was asked to inspect)
</must>
<reject>
- R:SCOPE_SILENCE a node whose scope moved after sealing receives no doctor finding -> "SCOPE_SILENCE"
- R:LEGACY_SILENCE a legacy latest freeze-class stamp with no valid scope seal receives no doctor finding -> "LEGACY_SILENCE"
- R:REPAIRAWAY doctor mutates scope or appends a seal while reporting drift -> "REPAIRAWAY"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · the milestone does not say who owns a scope-seal repair; taking the node's human approver or current operator as the party prompted to refreeze -> doctor must not manufacture a new approver
- A2 [which] covers: S1 S2 · the milestone does not say which nodes receive migration diagnostics; taking lifecycle nodes with at least one freeze-class stamp -> drafts and living documents should not be told to refreeze
- A3 [when] covers: S1 S2 · the milestone does not say whether every historical stamp is compared; taking the latest freeze-class stamp only -> an earlier scope is history, not current authority
- A4 [absent] covers: S1 S2 · the milestone does not say whether a malformed scope digest differs from a missing one; taking both as `scope_seal_missing` -> neither can establish approval coverage and both need the same refreeze
- A5 [order] covers: S1 S2 · the milestone does not say how findings are ordered among doctor output; taking existing stable graph order -> CI output remains diffable
- A6 [experience] covers: S1 S2 · the milestone does not say whether these findings are info or warn; taking warn with a runnable refreeze remedy -> fail-closed migration remains visible without inventing a new gate

## PLAN
contract: reuse the scope-digest and latest-freeze-class reader from scope-in-the-seal; compare without mutation and emit a stable `scope_moved_after_seal` finding that names a refreeze path. The tracked canonical and bundled `add.py` are the implementation pair; ignored runtime copies are parity/vendor evidence, not manually edited scope.
strategy: freeze an authored task, change only its `scope:`, and assert doctor reports the node while its file remains byte-identical across the read
regression: affected · python3 -m pytest add-method/tests/engine/test_doctor_sees_a_moved_scope.py -q · run the full engine suite before a receipt because doctor walks all nodes

## EDGES
- E1 Given a scope changed after a freeze · When doctor reads the bundle · Then it names that task with `scope_moved_after_seal` and a refreeze remedy
- E2 Given doctor finds either scope-seal problem · When it returns findings · Then the node's bytes and verified stamp list are unchanged
- E3 Given a legacy or malformed latest freeze-class stamp · When doctor reads the bundle · Then it names that task with `scope_seal_missing` and a refreeze remedy

## CHECKS
- test_doctor_names_a_scope_moved_after_its_seal_without_repairing_it · covers: M1, M3, R:SCOPE_SILENCE, R:REPAIRAWAY, E1, E2 · acceptance · proves a valid sealed digest changed in scope is reported and the read writes nothing
- test_doctor_names_legacy_and_malformed_scope_seals · covers: M2, M3, R:LEGACY_SILENCE, R:REPAIRAWAY, E2, E3 · migration · proves every undigested latest seal is discoverable and no report rewrites it
red-first: `python3 -m pytest add-method/tests/engine/test_doctor_sees_a_moved_scope.py -q` fails before Build because doctor currently has no scope-drift reader.

## EVIDENCE
receipt: pending — targeted red run is recorded in tmp/seal-direction-evidence.md
gate: HARD-STOP until the human answers the open assumptions, rejects, and edges

## LESSONS
none yet
