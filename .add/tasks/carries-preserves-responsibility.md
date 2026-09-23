---
type: Task
title: Carries preserves responsibility
status: done
depth: standard
kind: feature
milestone: state-that-tells-truth
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/FORMAT.md
  - add-method/CHANGELOG.md
  - add-method/tests/engine/test_carries_preserves_responsibility.py
  - add-method/tests/engine/test_quick_lane_tripwire.py
  - add-method/tests/engine/test_refuse_with_one_shape.py
  - add-method/tests/engine/test_stamp_field_integrity.py
  - add-method/tests/engine/test_stamp_reader_census.py
gives:
  - S1 exact carried-obligation validation and inherited authority at destination freeze/close
generated: { by: add/3.6.0, at: 2026-09-15 }
verified:
  - { by: "plan:codex", at: 2026-09-15, act: freeze, authority: plan, direction: "sha256:594e85d452e72a67", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:fa2bddd4999ed2a1" }
  - { by: "plan:codex", at: 2026-09-23, act: refreeze, authority: plan, direction: "sha256:594e85d452e72a67", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881", scope: "sha256:6d78ba9fbf752060" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:fa2bddd4999ed2a1" }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, outcome: FAIL, receipt: /tasks/carries-preserves-responsibility.d/runs/1.md }
  - { by: "plan:codex", at: 2026-09-23, act: refreeze, authority: plan, direction: "sha256:594e85d452e72a67", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881", scope: "sha256:d79e25cd59908dba", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:6665793f1ce48f1f" }
  - { by: "plan:codex", at: 2026-09-23, act: refreeze, authority: plan, direction: "sha256:594e85d452e72a67", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881", scope: "sha256:874872daee11aead", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:00200aa54884d5c9" }
  - { by: "plan:codex", at: 2026-09-23, act: refreeze, authority: plan, direction: "sha256:f2b00279c4f9b14f", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881", scope: "sha256:874872daee11aead", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:0d5a9f9ff38694e9" }
  - { by: "plan:codex", at: 2026-09-23, act: refreeze, authority: plan, direction: "sha256:1fbc6a14f3256d6d", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881", scope: "sha256:874872daee11aead", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:c328ac3a7cf88302" }
  - { by: "plan:codex", at: 2026-09-23, act: refreeze, authority: plan, direction: "sha256:85cd9cac53a85b71", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:5f1e588f57a93881", scope: "sha256:874872daee11aead", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-23, act: brief, authority: process, brief: "sha256:b3cbc8818aeb2d0b" }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, outcome: PASS, receipt: /tasks/carries-preserves-responsibility.d/runs/2.md }
  - { by: "process:run", at: 2026-09-23, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/carries-preserves-responsibility.d/runs/3.md }
  - { by: "advisor:carry-adversarial-review", at: 2026-09-23, act: refute, authority: process, outcome: held, probes: 39, receipt: /tasks/carries-preserves-responsibility.d/runs/2.md, tier: T2, note: "39 fresh adversarial scenarios covered malformed mappings, duplicate and cyclic claims, stale or missing source and destination seals, authority laundering, blank human signers, two-hop inheritance, correction recovery, terminal deletion, and source immutability; no remaining counterexample", changed: "Prior T2 counterexamples fixed before this receipt: distinct-Must self-edge, empty signer, stale intermediate deletion, legacy refreeze, authority reset, and destination deletion at done" }
  - { by: "plan:codex", at: 2026-09-23, act: gate, authority: process, outcome: PASS, receipt: /tasks/carries-preserves-responsibility.d/runs/2.md, brief: "sha256:aa09a23f5580c4fa" }
---
## CARD
goal: An accepted destination can carry one named original obligation while its original record and closure remain facts
why: B2 moves an EXIT criterion's state; this edge transfers responsibility for a frozen Task obligation, including the authority needed to approve and close it
beat: done · next: add status

## RULES
<must>
- M1 A destination Task's `carries:` entry maps exactly one bundle-absolute original `/tasks/<slug>.md#RULES:M<n>` to one local `/tasks/<slug>.md#RULES:M<n>` with an arrow. Both IDs name real authored Musts; source, destination, and mapping are stable addresses, never list ordinals or matching prose. A carried Must stays on the original Task, including a done Task. (from: state-that-tells-truth EXIT B3 · fails-on: an obligation silently changes identity)
- M2 The destination accepts the mapping only at its own latest freeze-class stamp. The stamp seals a deterministic digest of its complete `carries:` list separately from legacy direction/binding seals; a draft, old stamp, post-freeze edit, or source with no readable freeze-class direction is not accepted. `freeze` refuses invalid mappings before it writes, and `done` rechecks acceptance. (from: state-that-tells-truth EXIT B3 · fails-on: hand-editing an edge becomes approval)
- M3 The destination's authority floor is the maximum of its own computed floor, the original's computed floor, and the original's latest freeze-class authority, transitively along accepted carries. `process < ai-verify < plan < human` never lowers. A human-floor transfer needs its own human interview/freeze and human closing gate: the original human approval cannot sign the next Task. Security remains HARD-STOP, with no risk-accepted shortcut. (from: FORMAT §3.1 and state-that-tells-truth EXIT B3 · fails-on: a transfer launders security to process)
- M4 A transfer refuses a dangling/wrong-type/wrong-ID endpoint, malformed or ambiguous mapping, duplicate claim on one original Must, self-edge, or cycle before writing a new acceptance/closure. A chain walks exact obligation IDs with a visited set. Refusal names the original locator and repairable cause. (from: state-that-tells-truth EXIT B3 · fails-on: nobody is answerable or two Tasks claim one duty)
- M5 Readers do not rewrite the source's RULES, status, verified ledger, receipt, or closed milestone; a carried obligation adds destination responsibility without retroactively marking the source unmet or changing B2 EXIT totals. The ordinary destination gate/done path still requires its own evidence. (from: state-that-tells-truth SCOPE · fails-on: old closure facts are silently reopened)
</must>
<reject>
- R:BAD_CARRY a mapping has zero/multiple endpoints or an endpoint is not a real Task Must -> "R:BAD_CARRY"
- R:UNACCEPTED_CARRY a source/destination has no valid freeze-class attestation of this mapping -> "R:UNACCEPTED_CARRY"
- R:DUPLICATE_CARRY two destination obligations claim the same original Must -> "R:DUPLICATE_CARRY"
- R:CYCLIC_CARRY a chain revisits an obligation -> "R:CYCLIC_CARRY"
- R:LOWERED_CARRY_AUTHORITY a destination freeze/gate/done proceeds below inherited floor -> "R:LOWERED_CARRY_AUTHORITY"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · destination acceptance needs a new approver; taking the destination's own freeze/refreeze as the authority event, never reusing a source signature -> a security transfer without a fresh human decision refuses · probe: process freeze cannot carry a human Must
- A2 [which] covers: S1 · exact Must IDs and a Task-only arrow mapping distinguish B3 from B2's criterion `moves-to:` -> prose similarity and criterion IDs cannot rebind duty · probe: wrong section/ID refuses
- A3 [when] covers: S1 · latest freeze-class stamp owns the live `carries:` digest -> editing after acceptance cannot change the responsibility silently · probe: post-freeze mutation refuses at done
- A4 [absent] covers: S1 · no `carries:` means existing Task paths retain their behavior -> old controls remain green · probe: ordinary Task freeze/done
- A5 [order] covers: S1 · a chain inherits the maximum floor and checks every exact CID once -> the second hop cannot lose the first approval floor · probe: two-hop security origin
- A6 [experience] covers: S1 · refusals name original and destination locators and cause -> author can repair one edge without editing the closed source · probe: dangling/duplicate/cycle messages

## PLAN
contract: Add a Task-only, destination-authored `carries:` list of `"/tasks/source.md#RULES:M1 -> /tasks/dest.md#RULES:M2"` mappings. Parse exact Must addresses; validate graph-wide uniqueness, self-edges, and cycles; seal the list on destination freeze/refreeze with a separate `carries` digest; require that seal at done and at downstream source validation. Extend the shared authority reader with the transitive max of source floor, latest freeze-class authority, and historically accepted carried floor so freeze, gate, and done agree even after correction. Reject human-floor process claims and require the destination's own named-human interview, freeze, and gate; never mutate old source or its milestone. B2 `[~]`, `moves-to:`, and `accepts:` remain separate.
regression: affected · python3 -m pytest -q add-method/tests/engine/test_carries_preserves_responsibility.py add-method/tests/engine/test_moved_is_a_real_exit_state.py add-method/tests/engine/test_node_verbs.py add-method/tests/engine/test_security_floor.py · transfer, move, authority, and old Task controls
- O1 covers: M1,M5 · signal any byte change in original done Task or old milestone while validating a carry · window every freeze/done · threshold zero · action rollback

## EDGES
- E1 Given a frozen, done original Must and a distinct destination Must, When the destination maps and freezes the carry, Then its new seal accepts exactly that duty and later done leaves original bytes untouched.
- E2 Given a draft source, bad locator, wrong node/section/ID, or an edited mapping after freeze, When the destination freezes or closes, Then it refuses by the original identity.
- E3 Given two destinations claiming one original Must, or a self/two-node cycle, When acceptance is attempted, Then it refuses before writing a stamp.
- E4 Given an original security Must carried through two Tasks, When a process actor freezes or a lower gate closes the second Task, Then inherited human authority refuses; each accepted hop needs its own human approval.
- E5 Given no carry, or a B2 moved EXIT criterion, When ordinary Task close or milestone accounting runs, Then those existing state rules remain independent.

## CHECKS
- test_accepted_carry_preserves_original_and_seals_mapping · covers: M1,M2,M5,A2,A3,E1 · positive flow and immutable history
- test_dangling_wrong_id_and_wrong_type_refuse_before_freeze · covers: M1,M4,R:BAD_CARRY,A2,A6,E2 · exact identity, no ordinal/prose fallback
- test_post_freeze_edit_refuses_at_done · covers: M2,R:UNACCEPTED_CARRY,A3,E2 · current mapping must match accepted mapping
- test_removed_destination_carry_refuses_gate_and_done · covers: M2,R:UNACCEPTED_CARRY,A3,E2 · deleting the whole list cannot bypass terminal acceptance
- test_removed_intermediate_carry_cannot_be_laundered_downstream · covers: M2,R:UNACCEPTED_CARRY,A3,E2 · downstream acceptance checks an intermediate's historical seal
- test_legacy_refreeze_cannot_erase_intermediate_carry_history · covers: M2,R:UNACCEPTED_CARRY,A3,E2 · missing latest seal cannot hide prior accepted responsibility
- test_removal_and_refreeze_cannot_lower_historical_human_floor · covers: M3,R:LOWERED_CARRY_AUTHORITY,A1,A5,E4 · correction cannot reset the human floor
- test_duplicate_and_cycle_refuse_before_freeze · covers: M4,R:DUPLICATE_CARRY,R:CYCLIC_CARRY,A5,A6,E3 · single owner and bounded graph walk
- test_self_edge_between_distinct_musts_refuses_before_freeze · covers: M4,R:CYCLIC_CARRY,A6,E3 · different local IDs do not make a self-transfer
- test_security_authority_inherits_across_hops_without_reusing_approval · covers: M3,R:LOWERED_CARRY_AUTHORITY,A1,A5,E4 · human floor and one approval per destination
- test_human_carry_rejects_empty_identity_at_interview_and_freeze · covers: M3,R:LOWERED_CARRY_AUTHORITY,A1,E4 · prefix alone is not a signer
- test_revisiting_a_task_through_a_distinct_must_is_not_a_cycle · covers: M4,A5,E3 · obligation walk stays exact without Task-level false positives
- test_no_carry_control_and_b2_move_are_independent · covers: M5,A4,E5 · old Task and EXIT state controls
red-first: all new carry cases fail before Build; old controls remain green.

## EVIDENCE
receipt: /tasks/carries-preserves-responsibility.d/runs/2.md · kind: test-ids · 14/14 reported · exit 0 · 2026-09-23
refute: held · 39 probe(s) · tier T2 · by advisor:carry-adversarial-review · against /tasks/carries-preserves-responsibility.d/runs/2.md · 2026-09-23 · 39 fresh adversarial scenarios covered malformed mappings, duplicate and cyclic claims, stale or missing source and destination seals, authority laundering, blank human signers, two-hop inheritance, correction recovery, terminal deletion, and source immutability; no remaining counterexample · changed: Prior T2 counterexamples fixed before this receipt: distinct-Must self-edge, empty signer, stale intermediate deletion, legacy refreeze, authority reset, and destination deletion at done
gate: PASS · authority process · by plan:codex · receipt /tasks/carries-preserves-responsibility.d/runs/2.md · 2026-09-23

## LESSONS
none yet
- none filed — no lesson cites /tasks/carries-preserves-responsibility.md (add learn <lens> "<lesson>" --evidence /tasks/carries-preserves-responsibility.md)
