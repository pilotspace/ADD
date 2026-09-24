---
type: Task
title: repair-or-contract-change
status: done
depth: standard
milestone: state-that-tells-truth
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/CHANGELOG.md
  - README.md
  - add-method/README.md
  - add-method/docs/13-command-reference.md
  - add-method/skill/add/phases/build.md
  - add-method/src/add_method/_bundled/skill/add/phases/build.md
  - add-method/tests/engine/test_repair_or_contract_change.py
  - add-method/tests/engine/test_cli.py
  - add-method/tests/engine/test_authoring_beat.py
  - add-method/tests/engine/test_refute_verb.py
  - add-method/tests/engine/test_show_verb.py
  - add-method/tests/engine/test_stamp_reader_census.py
  - add-method/tests/engine/test_refuse_with_one_shape.py
  - add-method/tests/skill/test_search_registry.py
  - add-method/tests/skill/test_evidence_ladder.py
gives:
  - S1 `repair` routes a frozen open Task with a recorded cause to Build for an implementation defect or Direction for an unknown or changed contract
generated: { by: add/3.6.0, at: 2026-09-15 }
verified:
  - { by: "plan:codex", at: 2026-09-24, act: freeze, authority: plan, direction: "sha256:311da355498dd2a3", binding: "sha256:4d7ca83e0cec0cea", gives: "sha256:dca4ecd6856b0c87", scope: "sha256:2add9d54bf9832a7", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-24, act: brief, authority: process, brief: "sha256:bcfab4d8bb43ed35" }
  - { by: "plan:codex", at: 2026-09-24, act: refreeze, authority: plan, direction: "sha256:6ffa1597bb60ffd3", binding: "sha256:60b3aed15d2d819b", gives: "sha256:dca4ecd6856b0c87", scope: "sha256:a2db0343db7b8e4e", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-24, act: brief, authority: process, brief: "sha256:b2b966ce6df264e4" }
  - { by: "plan:codex", at: 2026-09-24, act: refreeze, authority: plan, direction: "sha256:17c895cd25da3a7c", binding: "sha256:60b3aed15d2d819b", gives: "sha256:dca4ecd6856b0c87", scope: "sha256:bfcb70bcdc8bee42", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-24, act: brief, authority: process, brief: "sha256:7ef0a7fc7e10bf9b" }
  - { by: "process:run", at: 2026-09-24, act: run, authority: process, outcome: PASS, receipt: /tasks/repair-or-contract-change.d/runs/1.md }
  - { by: "process:run", at: 2026-09-24, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/repair-or-contract-change.d/runs/2.md }
  - { by: "plan:codex", at: 2026-09-24, act: refreeze, authority: plan, direction: "sha256:1f5d4074eaef112d", binding: "sha256:60b3aed15d2d819b", gives: "sha256:dca4ecd6856b0c87", scope: "sha256:bc29471b2741dfae", carries: "sha256:4f53cda18c2baa0c" }
  - { by: "cli", at: 2026-09-24, act: brief, authority: process, brief: "sha256:0dd5a1a90f106f15" }
  - { by: "process:run", at: 2026-09-24, act: run, authority: process, outcome: PASS, receipt: /tasks/repair-or-contract-change.d/runs/3.md }
  - { by: "process:run", at: 2026-09-24, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/repair-or-contract-change.d/runs/4.md }
  - { by: "agent:repair-adversarial-t2", at: 2026-09-24, act: refute, authority: process, outcome: held, probes: 8, receipt: /tasks/repair-or-contract-change.d/runs/3.md, tier: T2, note: "Fresh independent probes covered PASS, RISK-ACCEPTED, HARD-STOP, repeated repair/refreeze, reopen/refreeze, stale gates, direct done, and fresh-evidence closure." }
  - { by: "plan:codex", at: 2026-09-24, act: gate, authority: process, outcome: PASS, receipt: /tasks/repair-or-contract-change.d/runs/3.md, brief: "sha256:87cf5a05bde76fb2" }
---
## CARD
goal: a failing build can be repaired under its approved intent, while an open decision or changed requirement visibly returns to Direction
why: `replan` currently records any nonblank steering note and says keep building; `gate` later catches some digest drift, but an open frozen Task has no Direction-return verb, and `scope:` is not compared with the old approval.
beat: done · next: add status

## RULES
<must>
- M1 on an open frozen Task, an implementation failure with unchanged frozen RULES, CHECKS, EDGES/probed obligations, `gives:` and scope records its concrete cause and stays in Build (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a harmless code defect triggers routine reapproval)
- M2 a changed Must, Reject, check obligation, published surface, scope, or accepted `carries:` mapping returns the Task to Direction, records the cause, and leaves the old freeze stamp intact until a new freeze/refreeze. A caller claiming `implementation` over such drift is refused atomically and must resubmit `change` or `unknown`; a semantic `change` may return to Direction even before authored text changes. (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a changed contract is repaired under old authority)
- M3 uncertainty or silence about what the frozen requirement means returns the Task to Direction even when its text digest is unchanged (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a builder silently chooses a new rule)
- M4 a `repair kind=change|unknown` stamp is an invalidation boundary: only a later freeze/refreeze is active. The shared chronology reader drives derived beat/next, brief, run, every closing gate, and done, so no old freeze, brief, run/green receipt, or closing verdict can authorize Build or closure after Direction return. A reopened Task explicitly returned to Direction also needs a new freeze. Refreeze must reapply the computed authority floor before Build resumes. (from: /milestones/state-that-tells-truth.md EXIT 4 · fails-on: a `process` note becomes a substitute human/security approval)
</must>
<reject>
- R:CAUSELESS a repair route with no concrete cause is recorded -> "CAUSELESS"
- R:SEAL_TOUCH a caller labels frozen text or scope drift as an implementation defect and stays in Build -> "SEAL_TOUCH"
- R:OLDSEAL a Direction return is briefed, run, or gated on the prior freeze -> "OLDSEAL"
- R:WRONGNODE a Milestone, done Task, unfrozen Task, or Task already returned to Direction is routed as an open Build repair -> "WRONGNODE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · an implementation defect can be diagnosed by the builder, but a semantic silence cannot be adjudicated by the engine; taking the cause class as an explicit operator declaration guarded by structural comparisons -> a dishonest declaration still needs review
- A2 [which] covers: S1 · the milestone calls out frozen requirements and scope; taking RULES, CHECKS, `gives:`, EDGES/probed A ids and `scope:` as the mechanically compared surfaces -> a moved authority floor cannot hide behind an unchanged rule text
- A3 [when] covers: S1 · this route is for active frozen Tasks; taking done Task corrections through the existing `reopen`/successor rule -> closed history stays intact
- A4 [absent] covers: S1 · an unexplained failure is not enough to distinguish implementation from intent; taking blank cause as refusal and explicit unknown as Direction -> no silent Build decision
- A5 [order] covers: S1 · the old seal remains evidence while intent is reauthored; taking a Direction return as invalidating Build entry before a second freeze -> no stale brief or receipt crosses the boundary
- A6 [experience] covers: S1 · the author needs a runnable next step; taking the result as Build fix/run or Direction revise/interview/refreeze with the cause named -> the route is visible in `status` and the record

## PLAN
contract: expose `add repair <ref> --kind implementation|change|unknown --cause <text> [--by <actor>]` for an open actively frozen Task. A successful `act: repair` stamp records `kind`, safely serialized one-line `cause`, `to: build|direction`, and process authority. Invalid kind or blank cause refuses without a write. Compare current direction, binding, gives, scope, and any accepted carries against the latest active freeze-class stamp. `implementation` with any observed drift or a missing/malformed legacy seal refuses R:SEAL_TOUCH without writing; the caller must choose `change` or `unknown`. A semantic `change` may return to Direction with unchanged text. One shared active-freeze chronology reader treats `repair to: direction` and `reopen to: direction` as invalidating every earlier freeze/brief/run/gate until a later freeze/refreeze. A Direction return preserves prior stamps but resets Build entry; `brief`, `run`, every closing `gate`, and direct `done` refuse R:OLDSEAL before writing or executing. `freeze` continues to compute its authority; the route never issues a human/security signature.
strategy: consume the existing scope seal and compare all sealed surfaces before choosing Build; update derived beat/next and all Build-entry readers through one chronology predicate. A claimed legacy freeze with missing or malformed scope is unknown, never clean for `implementation`; `change`/`unknown` can return it to Direction. Keep `replan` as no-seal steering and document the public CLI/stamp contract in FORMAT.
regression: affected · python3 -m pytest -q add-method/tests/engine/test_repair_or_contract_change.py add-method/tests/engine/test_node_verbs.py add-method/tests/engine/test_carries_preserves_responsibility.py add-method/tests/engine/test_cli.py add-method/tests/engine/test_stamp_reader_census.py add-method/tests/engine/test_refuse_with_one_shape.py add-method/tests/engine/test_check_verb.py · shared freeze, brief, run, gate, transfer, CLI, and registry readers; run the full suite separately before close

## EDGES
- E1 Given a frozen Task whose check fails because code rejects a valid input but no approved surface moved · When an implementation repair with a concrete cause is routed · Then the Task stays in Build and its cause is stamped
- E2 Given a frozen Task whose Must, Reject, check, `gives:` or scope changed · When the builder claims an implementation repair · Then it cannot remain in Build, and Direction/refreeze is named
- E3 Given unchanged text but a requirement silence discovered in Build · When unknown is routed · Then Direction is recorded and the prior freeze cannot authorize a run/gate
- E4 Given a Direction return on a human-floor Task · When the old signer or a process claim attempts to resume Build · Then refreeze requires the freshly computed human floor
- E5 Given a Task with an old green run that returns to Direction · When status, brief, run, and gate read it · Then Direction is shown and none may execute or close until a later refreeze; after refreeze Build resumes
- E6 Given a legacy or malformed scope seal · When implementation is claimed · Then it refuses atomically as unknown coverage; change/unknown may return to Direction
- E7 Given a Milestone, done Task, unfrozen Task, or already-returned Task · When repair is called · Then R:WRONGNODE refuses without a stamp
- E8 Given a carried obligation whose mapping changes, or an old closing gate/receipt after a Direction return · When repair or closure is attempted · Then no implementation repair or terminal shortcut uses the old seal

## CHECKS
- test_same_contract_defect_records_cause_and_stays_build · covers: M1, R:CAUSELESS, E1 · acceptance
- test_drift_cannot_be_called_implementation_and_returns_direction · covers: M2, R:SEAL_TOUCH, E2 · acceptance
- test_scope_move_returns_direction_and_recomputes_authority · covers: M2, M4, E2, E4 · acceptance
- test_unknown_requirement_returns_direction_and_old_seal_cannot_run · covers: M3, M4, R:OLDSEAL, E3 · acceptance
- test_direction_return_outranks_an_old_run_for_the_current_beat · covers: M4,A5,E5 · old green cannot restore Verify
- test_direction_return_blocks_brief_run_and_gate_without_execution_or_receipt · covers: M4,R:OLDSEAL,A5,E5 · no-exec invalidation boundary
- test_refreeze_after_direction_return_restores_build_entry · covers: M4,A5,E4,E5 · fresh approval restores Build
- test_legacy_and_malformed_scope_seals_are_uncertain_not_clean · covers: M1,M2,R:SEAL_TOUCH,A2,A4,E6 · unknown coverage cannot authorize Build
- test_repair_refuses_wrong_node_states · covers: R:WRONGNODE,A3,E7 · Task-only active-freeze route
- test_semantic_change_without_text_edit_returns_direction · covers: M2,M3,E3 · operator declaration is visible even before text edit
- test_repair_cli_and_stamp_contract · covers: M1,M2,R:CAUSELESS,R:WRONGNODE,A6,E1,E7 · public verb grammar and exact stamp fields
- test_every_registry_learned_the_new_verb · covers: A6,E1 · public verb count and command reference stay aligned with CLI
- test_carry_mapping_drift_is_not_an_implementation_repair · covers: M2,R:SEAL_TOUCH,E8 · accepted transfer cannot change under a code-only repair
- test_direction_return_blocks_risk_accepted_and_direct_done · covers: M4,R:OLDSEAL,E8 · terminal paths cannot reuse old approval
- test_refreeze_does_not_reuse_a_pre_return_receipt_for_risk_accepted · covers: M4,R:OLDSEAL,E5,E8 · refreeze alone does not make prior run evidence current
- test_reopened_direction_needs_a_new_freeze · covers: M4,R:OLDSEAL,E5 · explicit Direction return invalidates old seal
- test_repair_cause_is_a_readable_one_line_stamp · covers: M1,A6,E1 · braces and quotes cannot corrupt the ledger
- test_kind_parameter_annotation_is_not_an_evidence_rung · covers: A6 · the skill's evidence parser ignores the repair API type annotation
- test_existing_replan_preserves_seal_as_steering_control · covers: A1 · control
red-first: `python3 -m pytest add-method/tests/engine/test_repair_or_contract_change.py -q` must fail the four acceptance routes before Build; the old `replan` control must pass.

## EVIDENCE
receipt: /tasks/repair-or-contract-change.d/runs/3.md · kind: test-ids · 22/22 reported · exit 0 · 2026-09-24
refute: held · 8 probe(s) · tier T2 · by agent:repair-adversarial-t2 · against /tasks/repair-or-contract-change.d/runs/3.md · 2026-09-24 · Fresh independent probes covered PASS, RISK-ACCEPTED, HARD-STOP, repeated repair/refreeze, reopen/refreeze, stale gates, direct done, and fresh-evidence closure.
gate: PASS · authority process · by plan:codex · receipt /tasks/repair-or-contract-change.d/runs/3.md · 2026-09-24

## LESSONS
none yet
- none filed — no lesson cites /tasks/repair-or-contract-change.md (add learn <lens> "<lesson>" --evidence /tasks/repair-or-contract-change.md)
