---
type: Task
title: Moved is a real EXIT state
status: done
depth: standard
kind: feature
milestone: state-that-tells-truth
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tooling/test_tree_parity.py
  - add-method/FORMAT.md
  - add-method/tests/engine/test_moved_is_a_real_exit_state.py
  - add-method/tests/engine/test_stamp_reader_census.py
  - add-method/tests/engine/test_refuse_with_one_shape.py
gives:
  - S1 milestone EXIT moved-criterion tally and accepted-destination validation at milestone-done
generated: { by: add/3.6.0, at: 2026-09-15 }
verified:
  - { by: "plan:codex", at: 2026-09-15, act: freeze, authority: process, direction: "sha256:ee5ec3626014504d", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:265207d924f111b1" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:524c43550eaf56ba" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:314a97d7957292c0", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:265207d924f111b1" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:0859154019187e34" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:0184ea0adcd9afa9", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:265207d924f111b1" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:c73ee7c0d25d50b9" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/moved-is-a-real-exit-state.d/runs/1.md }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:9dd8e5bb0de31f1e", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:265207d924f111b1" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:743232c0cae830ae" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/moved-is-a-real-exit-state.d/runs/2.md }
  - { by: "agent:gpt-5.6-moved-b2-fresh-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 8, receipt: /tasks/moved-is-a-real-exit-state.d/runs/2.md, tier: T2, note: "balanced mixed fences in EXIT: backtick block containing tilde opener/closer and [x] example is counted as real; a single outside [x] criterion closes 2/2 rather than 1/1" }
  - { by: "plan:codex", at: 2026-09-16, act: refreeze, authority: plan, direction: "sha256:8cbc589c75b7ed8e", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:265207d924f111b1" }
  - { by: "cli", at: 2026-09-16, act: brief, authority: process, brief: "sha256:4de414700046b856" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/moved-is-a-real-exit-state.d/runs/3.md }
  - { by: "agent:gpt-5.6-moved-b2-fresh-refute", at: 2026-09-16, act: refute, authority: process, outcome: held, probes: 8, receipt: /tasks/moved-is-a-real-exit-state.d/runs/3.md, tier: T2, note: "receipt 3 nine Git blob hashes match, 102 JUnit cases include all eleven frozen CHECKS; mixed/wide/unclosed fences, three-hop accepted move, stale acceptance, and cycle probes held after receipt 2 mixed-fence finding was repaired" }
  - { by: "plan:codex", at: 2026-09-16, act: refreeze, authority: plan, direction: "sha256:c88d01c6a9501340", binding: "sha256:e9142d9bb1b8b3df", gives: "sha256:265207d924f111b1" }
  - { by: "cli", at: 2026-09-16, act: brief, authority: process, brief: "sha256:68e868b8fabd2553" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/moved-is-a-real-exit-state.d/runs/4.md }
  - { by: "agent:gpt-5.6-moved-b2-fresh-refute", at: 2026-09-16, act: refute, authority: process, outcome: held, probes: 8, receipt: /tasks/moved-is-a-real-exit-state.d/runs/4.md, tier: T2, note: "receipt 4 nine Git blob hashes and all eleven exact-named frozen CHECKS bind to 97 passing JUnit cases; former four locator, two acceptance, and two cycle cases remain isolated; engine and FORMAT unchanged from held behavior probes" }
  - { by: "agent:codex", at: 2026-09-16, act: gate, authority: process, outcome: PASS, receipt: /tasks/moved-is-a-real-exit-state.d/runs/4.md, brief: "sha256:1fb39f02739c0d18" }
---
## CARD
goal: A moved EXIT criterion remains an original obligation with a named, accepted destination
why: loop-that-closes authored eleven criteria, marked EXIT:9 [~], and closed as 10/10 because the goal gate ignored that line
beat: done · next: add status

## RULES
<must>
- M1 Count every real EXIT `[x]`, `[ ]`, and `[~]` line in the original denominator; preserve its authored line and explicit `C<n>` identity. A moved line is moved, never met. Fenced examples, including a different marker sequence inside an active fence, do not count. (from: state-that-tells-truth EXIT B2 · fails-on: 10/10 instead of 10/11)
- M2 A `[~] C<n>` line names exactly one bundle-absolute `moves-to: /milestones/<slug>.md#EXIT:C<n>` target. The distinct target is a real Milestone EXIT criterion whose line reciprocally names `accepts: /milestones/<source>.md#EXIT:C<n>`. Its Milestone has a latest freeze-class verified stamp carrying the current EXIT direction digest, so acceptance added or removed after freeze does not count. Ordinary `[ ]`↔`[x]` completion ticks do not move that direction digest; `[~]` remains a distinct transfer state. A legacy stamp without that digest cannot establish acceptance. (from: state-that-tells-truth EXIT B2 · fails-on: orphan, dangling, or unauthenticated prose move)
- M3 `milestone-done` refuses unresolved moves by original CID/id before member or lesson advice; a valid move reports original `met/total` and moved count/identity without changing original lines. Already-done milestones and stamps are not rewritten by this reader. (from: loop-that-closes CLOSE · fails-on: false closure)
- M4 A move chain terminates at a non-moved criterion; self-targets and cycles refuse. The original denominator never migrates. B3 `carries:` will specify obligation-transfer authority separately. (from: state-that-tells-truth EXIT B2/B3 · fails-on: circular resolution)
</must>
<reject>
- R:INVISIBLE_MOVE A `[~]` line vanishes from the original tally -> "R:INVISIBLE_MOVE"
- R:ORPHAN_MOVE A moved line lacks one exact target -> "R:ORPHAN_MOVE"
- R:DANGLING_MOVE The target CID/id is no real Milestone EXIT criterion -> "R:DANGLING_MOVE"
- R:REJECTED_MOVE The target lacks reciprocal, frozen accepted direction -> "R:REJECTED_MOVE"
- R:CYCLIC_MOVE Traversal revisits a criterion -> "R:CYCLIC_MOVE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · acceptance needs an author; taking the destination Milestone's latest freeze-class stamp as direction authority -> a raw target line cannot approve itself · probe: unfrozen target refuses
- A2 [which] covers: S1 · B2 has no locator grammar; taking explicit `C<n>` and bundle-absolute milestone EXIT references -> insertion cannot retarget a move · probe: wrong ID never falls back to ordinal
- A3 [when] covers: S1 · B2 has no migration command; taking validation on new close and read-only reporting on done history -> loop-that-closes remains exact · probe: a read changes no bytes
- A4 [absent] covers: S1 · old `[~]` prose has no accepted destination; taking it as an orphan with 10/11 original accounting -> prose is evidence of incompletion · probe: real counterexample stays 10/11
- A5 [order] covers: S1 · multiple moves exist; taking source EXIT order and visited criterion CIDs -> stable refusal and bounded cycle detection · probe: first authored invalid move named
- A6 [experience] covers: S1 · closer needs a repairable refusal; taking source CID/id and target locator in note -> the box to repair is clear · probe: refusal names source C id

## PLAN
contract: Extend the real EXIT reader to classify `[x]`, `[ ]`, `[~]` and explicit `C<n>` IDs while retaining old `check` behavior. Fence skipping tracks opener marker kind and length; a different marker inside it remains quoted content. A new Milestone freeze stamps an EXIT direction digest that normalizes ordinary checked/unchecked progress while retaining all identities, move/acceptance locators, and `[~]` state; resolve each `moves-to:` exact target, verify reciprocal `accepts:` and the destination's latest freeze-class EXIT digest still matches, and walk moved targets with a visited set to a non-moved criterion. A legacy freeze without EXIT digest is unresolved. The gate reports `met/total` plus moved count, keeping source lines and historical stamps. Missing, malformed, ambiguous, wrong-type, self, cyclic, and rejected links refuse. No new beat or implicit transfer authority.
regression: affected · python3 -m pytest -q add-method/tests/engine/test_moved_is_a_real_exit_state.py add-method/tests/engine/test_milestone_done.py add-method/tests/engine/test_check_verb.py add-method/tests/engine/test_freeze_seal.py add-method/tests/engine/test_milestone_freeze_is_interviewed.py add-method/tests/engine/test_stamp_reader_census.py add-method/tests/engine/test_refuse_with_one_shape.py add-method/tests/engine/test_source_dead_code.py add-method/tests/engine/test_brief_gate.py add-method/tests/engine/test_todo.py add-method/tooling/test_tree_parity.py --junitxml=/private/tmp/moved-is-a-real-exit-state-v4.xml · new move states, old goal/check/freeze/navigation controls, registered stamp and refusal-message readers, source/bundle/live parity
- O1 covers: M1,M3 · signal reported denominator differs from authored EXIT count · window each close · threshold any mismatch · action rollback

## EDGES
- E1 Given loop-that-closes `[~]`, When tally is read, Then EXIT:9 remains original and total is eleven without editing history.
- E2 Given no target, nonexistent target, wrong ID, or wrong node type, When close is attempted, Then original criterion is named in a refusal.
- E3 Given a target lacking reciprocal acceptance, a current EXIT-bound freeze, or an acceptance edited after freeze, When close is attempted, Then it refuses.
- E4 Given self-target or two-node cycle, When close is attempted, Then it refuses without looping.
- E5 Given reciprocal, frozen, terminal destination, When close is attempted, Then original total includes the moved line and source/target obligations remain authored.

## CHECKS
- test_real_counterexample_keeps_exit_nine_and_eleven_total · covers: M1,M3,R:INVISIBLE_MOVE,A3,A4,E1 · historical count and identity
- test_mixed_fences_do_not_turn_examples_into_exit_criteria · covers: M1,R:INVISIBLE_MOVE,E1 · quoted mixed-marker boxes stay outside the goal tally
- test_orphan_and_dangling_moves_refuse_by_original_identity · covers: M2,M3,R:ORPHAN_MOVE,R:DANGLING_MOVE,A2,A6,E2 · exact locator, no ordinal fallback
- test_unaccepted_destination_refuses_without_laundering_a_target · covers: M2,R:REJECTED_MOVE,A1,E3 · reciprocal direction and freeze evidence
- test_acceptance_edited_after_freeze_refuses · covers: M2,R:REJECTED_MOVE,E3 · acceptance cannot be inserted under an old EXIT seal
- test_check_cannot_erase_a_moved_criterion · covers: M1,R:INVISIBLE_MOVE · `check` cannot convert transfer into met
- test_destination_completion_keeps_its_frozen_acceptance · covers: M2,E5 · an ordinary tick preserves the approved acceptance mapping
- test_the_reader_set_is_enumerated · covers: M2 · the new freeze/refreeze interpretation is registered in the stamp-reader census
- test_the_messages_are_untouched · covers: M1,M3 · two new refusal messages are intentionally re-aimed and no helper result is misclassified as a verb refusal
- test_self_and_two_node_cycles_refuse · covers: M4,R:CYCLIC_MOVE,A5,E4 · bounded traversal
- test_accepted_terminal_move_preserves_original_denominator_and_bytes · covers: M1,M2,M3,M4,A3,E5 · positive moved state, original totals, and an already-done read that leaves bytes unchanged
red-first: all eleven original acceptance cases failed against the baseline before Build; the later check-identity case failed against the unchanged baseline's invisible moved index; the destination-completion case failed against the first candidate's overbroad EXIT digest; the stamp-reader census failed before its new freeze/refreeze reader was registered; the fresh T2 mixed-fence case failed against receipt 2's candidate; the refusal-message pin failed when two intentional refusals were added and was re-aimed with their reason. Receipt 3 exposed ADD's exact-name binding gap for parametrized JUnit names, so those eight cases now run inside three exact-named bound checks without dropping any assertions. Destination freeze fixtures use the real engine stamp rather than forged flow-map text.

## EVIDENCE
receipt: /tasks/moved-is-a-real-exit-state.d/runs/4.md · kind: test-ids · 97/97 reported · exit 0 · 2026-09-16
refute: held · 8 probe(s) · tier T2 · by agent:gpt-5.6-moved-b2-fresh-refute · against /tasks/moved-is-a-real-exit-state.d/runs/4.md · 2026-09-16 · receipt 4 nine Git blob hashes and all eleven exact-named frozen CHECKS bind to 97 passing JUnit cases; former four locator, two acceptance, and two cycle cases remain isolated; engine and FORMAT unchanged from held behavior probes
gate: PASS · authority process · by agent:codex · receipt /tasks/moved-is-a-real-exit-state.d/runs/4.md · 2026-09-16

## LESSONS
none yet
- none filed — no lesson cites /tasks/moved-is-a-real-exit-state.md (add learn <lens> "<lesson>" --evidence /tasks/moved-is-a-real-exit-state.md)
