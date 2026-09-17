---
type: Task
title: Freeze binds an immutable complete decision manifest
status: direction
depth: standard
kind: security
sensitivity: security
milestone: approval-is-a-decision-set
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/FORMAT.md
  - add-method/tests/engine/test_decision_manifest_binds_approval.py
gives:
  - S1 a canonical immutable versioned decision manifest bound to each freeze/refreeze
  - S2 a refreeze candidate delta that keeps interview staleness and authority separate
generated: { by: add/3.6.0, at: 2026-09-16 }
verified: []
---
## CARD
goal: bind each freeze to one complete immutable decision candidate
why: `interview_digest` currently proves only which questions were asked; it cannot prove which complete declaration set the freeze approved or recover removed obligations at refreeze
beat: direction · next: complete scope-in-the-seal and the real per-Task security interview, then freeze only after the human reviews this Direction and RED bundle

## RULES
<must>
- M1 Before writing a freeze/refreeze stamp, the engine compiles the node's complete candidate into `<node>.d/decisions/<64-lowercase-hex>.json`. The file is exact compact canonical JSON: UTF-8, keys sorted, separators `,` and `:`, no trailing newline; its filename is the full SHA-256 of those exact bytes. Existing content-addressed files are byte-checked and never overwritten. (from: approval-is-a-decision-set EXIT C1 · fails-on: a mutable sidecar or digest over presentation order)
- M2 Schema 1 has top-level keys `decision_schema`, `node`, `decisions`, and `question_ids`. `decisions` is the complete candidate sorted by kind rank `S,M,R,A,E,C` then numeric ID; every row has exactly `id`, `kind`, `declaration`, `declaration_digest`, `sources`, `examples`, `required_authority`, `proposed_reading`, and `ask_required`. `declaration_digest` is full `sha256:<64hex>` over the exact UTF-8 `declaration` field. `question_ids` is exactly the ordered IDs of candidate rows whose `ask_required` is true. No answer, verdict, signer, persona conclusion, or inferred acceptance appears anywhere in the manifest. (from: approval-is-a-decision-set EXIT C1,C4 · fails-on: serializing the interview receipt as the candidate)
- M3 A Task candidate contains every authored frontmatter `gives:` S row and every authored M/R/A/E list declaration, including sourced Musts, retired `n/a` assumptions, and other rows `_open_decisions` does not ask. A Milestone candidate contains every authored EXIT C obligation independent of `[ ]`, `[x]`, or `[~]`. Each declaration must carry one stable authored class-correct ID, unique within the node; missing, duplicate, generated ordinal, wrong-class, or ambiguous IDs refuse before any manifest or stamp write. (from: approval-is-a-decision-set EXIT C1 and state-that-tells-truth stable EXIT contract · fails-on: reorder silently renames the approved obligation)
- M4 `freeze` and `refreeze` append `decisions: "sha256:<64hex>"` and `decision_schema: 1` beside the existing independent direction/binding/gives/scope fields. The digest addresses the manifest for that exact node; a node path is part of the canonical payload, so one node's artifact cannot approve another. The decision seal does not replace or widen any existing seal. (from: approval-is-a-decision-set EXIT C1,C4 · fails-on: one global approval artifact or a decision digest standing in for scope)
- M5 `_open_decisions` remains the question compiler, projected from the same declarations as rows with `ask_required: true`: non-`n/a` A, filled E, R, unsourced M, and Milestone C. S, sourced M, and retired A remain visible candidate rows with `ask_required: false`. `proposed_reading` preserves the current human-facing reading; `sources` records handed provenance without judging it; `examples` records the concrete edge/falsifier material. Sparse interview stamps still accumulate for one matching interview digest, later answers win, `correct` remains owed until text changes, and explicit `defer` completes that item. Omission and empty input answer nothing. (from: `_open_decisions`, `interview_gap`, and approval-is-a-decision-set EXIT C2,C4 · fails-on: completeness creates more questions or compactness invents answers)
- M6 The latest known manifest and current candidate produce stable `added`, `changed`, `removed`, and `unchanged` ID sets by authored identity plus declaration digest. Removed rows come from the immutable prior sidecar and stay visible. `stale` is separately the current whole `interview_gap`: when the interview digest moves, every current question is owed even if its row is unchanged; a per-row diff never revives an old answer. `interview` shows this distinction before refreeze and successful refreeze repeats it. (from: approval-is-a-decision-set EXIT C2 · fails-on: unchanged-looking rows silently retain answers that the current interview contract invalidates)
- M7 A latest freeze-class stamp that claims both decision fields must resolve one regular file under that same node, parse exact schema 1, have the claimed node, match the content digest/filename, contain unique valid rows, and have `question_ids` consistent with `ask_required`. Missing one claim field, missing/malformed/noncanonical/mismatched content, traversal, symlink escape, or cross-node content refuses with `R:DECISION_MANIFEST` before another stamp. A legacy freeze-class stamp with neither field has unknown decision coverage; refreeze reports `unknown`, asks the current required questions, and writes the first full baseline without fabricating a historical delta. (from: approval-is-a-decision-set EXIT C3 · fails-on: corruption is treated as an empty or legacy candidate)
- M8 Decision completeness never changes authority. This security Task requires its own real human interview and freeze after `scope-in-the-seal` is gated; each later security node retains its own computed human floor, interview, freeze, gate, and HARD-STOP. A manifest, Git name, signer text, persona output, prior node approval, or explicit `defer` cannot approve another node or clear a security stop. (from: approval-is-a-decision-set EXIT C4 and FORMAT security floor · fails-on: presentation becomes delegated authority)
</must>
<reject>
- R:MISSING_DECISION_ID a candidate declaration has no stable authored class-correct S/M/R/A/E/C ID -> "R:MISSING_DECISION_ID"
- R:DUPLICATE_DECISION_ID a node repeats one decision ID or makes it ambiguous -> "R:DUPLICATE_DECISION_ID"
- R:DECISION_MANIFEST a claimed manifest is missing, malformed, noncanonical, cross-node, or digest/schema inconsistent -> "R:DECISION_MANIFEST"
- R:DECISION_ANSWER a manifest contains or implies an answer, verdict, signer conclusion, or persona conclusion -> "R:DECISION_ANSWER"
- R:UNINTERVIEWED a current human-floor question has no explicit current `confirm` or `defer` -> "R:UNINTERVIEWED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · the request does not say whether a complete manifest can authenticate or transfer a human decision; taking it as a per-node local notary record only, with every security Task still requiring its own human interview/freeze and security gate -> treating a manifest as identity or delegated authority would lower the existing hard floor · probe: two identical security Tasks still require two interviews and two manifests
- A2 [which] covers: S1 S2 · the request does not spell the candidate/question boundary; taking the complete candidate as Task S/M/R/A/E or Milestone C and `question_ids` as only current `_open_decisions` -> compiling only questions loses sourced Musts and removed obligations, while asking every candidate row adds ceremony · probe: sourced M and retired A are present with `ask_required: false`
- A3 [when] covers: S1 S2 · the request says immutable/versioned but not when snapshots land; taking one snapshot immediately before each successful freeze/refreeze and no snapshot on refusal -> a draft manifest could be mistaken for approved direction · probe: substantive edits create a new file only when the new stamp lands
- A4 [absent] covers: S1 S2 · the request distinguishes legacy unknown from corruption; taking neither stamp field as legacy unknown, exactly both as a verifiable claim, and any partial/broken claim as refusal -> silently treating a missing claimed sidecar as legacy would erase evidence of tampering · probe: unknown refreeze baselines, missing/malformed claimed files refuse
- A5 [order] covers: S1 S2 · the request requires stability under reorder but not a byte grammar; taking sorted keys, compact separators, no newline, full hashes, canonical declarations, and ID ordering as the one byte contract -> platform formatting or authored list order would otherwise move approval without changing a decision · probe: whitespace/reorder keep one digest while substantive text moves it
- A6 [experience] covers: S1 S2 · the request says show refreeze delta without defining how to explain interview invalidation; taking four candidate-delta sets plus a separately labeled whole-question `stale` set, with removed text recoverable from the prior sidecar -> a reader could mistake row-level unchanged for answer-level current · probe: one changed assumption leaves other rows unchanged while every current question is stale

## PLAN
contract: Add one canonical candidate compiler shared by the manifest writer, validator, delta renderer, and `_open_decisions` projection. Write `<node>.d/decisions/<digest>.json` atomically and immutably immediately before a successful freeze-class transition; append full `decisions` and integer `decision_schema` stamp fields. Load only a claimed prior same-node artifact for delta comparison; treat a fieldless legacy stamp as unknown, never as empty. Keep interview answers only in interview stamps/sidecars. Preserve existing direction, binding, gives, EXIT, scope, authority, and security readers as independent controls.
dependencies: Build is held until `scope-in-the-seal` is human-interviewed, implemented, and gated; Milestone C identities consume the stable authored EXIT rule from `moved-is-a-real-exit-state`; this Task itself must receive a separate real human interview/freeze because its sensitivity is security. No prior milestone or agent authorization satisfies that requirement.
regression: affected · python3 -m pytest -q add-method/tests/engine/test_decision_manifest_binds_approval.py add-method/tests/engine/test_freeze_interview.py add-method/tests/engine/test_moved_is_a_real_exit_state.py add-method/tests/engine/test_scope_in_the_seal.py add-method/tests/engine/test_stamp_reader_census.py · decision, interview, EXIT, scope, and stamp readers share the trust spine

## EDGES
- E1 Given the same Task declarations with whitespace and list order changed, When each candidate is frozen, Then one canonical manifest digest/file remains; changing decision text produces a new digest/file and preserves the prior bytes.
- E2 Given sourced and unsourced Musts, retired and live assumptions, Rejects, examples, and surfaces, When the candidate compiles, Then all appear exactly once while only the existing question subset has `ask_required: true` and no row carries an answer.
- E3 Given sparse passes where a later pass defers one item and a later `correct` overrides an earlier confirm, When `interview_gap` is read, Then only explicit current confirm/defer completes an item; candidate bytes never change with answers.
- E4 Given one proposed reading changes while other decision rows do not, When refreeze is presented, Then the candidate delta marks only that row changed while `stale` names the whole current question set required by the interview digest.
- E5 Given an obligation is removed or a new one is added, When refreeze is presented, Then removed text remains recoverable from the old immutable manifest and added/removed/unchanged sets use authored IDs.
- E6 Given a latest legacy stamp with no decision fields, When refreeze is requested, Then coverage is unknown and the successful refreeze writes a full baseline; given a claimed absent or malformed artifact, the same request refuses without writing.
- E7 Given two separate security Tasks with equivalent declaration text, When only one is interviewed, Then only that node can freeze and its node-bound manifest cannot satisfy the other Task or any HARD-STOP.

## CHECKS
- test_manifest_format_and_reorder_are_stable · covers: M1,M2,M3,M4,A5,E1 · canonical bytes, full content address, authored identities, and freeze/refreeze fields
- test_substantive_change_moves_digest_and_keeps_old_snapshot · covers: M1,M4,A3,A5,E1 · immutable version movement
- test_task_candidate_refuses_missing_and_duplicate_ids · covers: M3,R:MISSING_DECISION_ID,R:DUPLICATE_DECISION_ID,E2 · every Task decision class is stable and unambiguous
- test_milestone_candidate_refuses_missing_and_duplicate_c_ids · covers: M3,R:MISSING_DECISION_ID,R:DUPLICATE_DECISION_ID,E5 · authored Milestone obligation identity
- test_complete_candidate_and_question_subset_have_exact_rows · covers: M2,M3,M5,A2,E2 · declarations, full hashes, sources, examples, authority, readings, and ask flags
- test_answers_never_enter_manifest_and_sparse_verdicts_keep_their_meaning · covers: M2,M5,R:DECISION_ANSWER,R:UNINTERVIEWED,E3 · no auto-answer plus sparse/correct/defer compatibility
- test_stale_interview_is_whole_set_while_candidate_delta_is_per_row · covers: M5,M6,A6,E4 · stale/interview_gap distinction
- test_refreeze_keeps_added_removed_and_unchanged_obligations_visible · covers: M1,M6,A3,E5 · immutable prior recovery and complete delta
- test_legacy_is_unknown_but_missing_or_malformed_claim_refuses · covers: M7,R:DECISION_MANIFEST,A4,E6 · migration baseline versus corrupt claim
- test_security_interviews_and_manifests_remain_per_node · covers: M4,M8,R:UNINTERVIEWED,A1,E7 · authority remains separate and HARD-STOP is unchanged
red-first: `python3 -m pytest -q add-method/tests/engine/test_decision_manifest_binds_approval.py` must fail before Build because no decision manifest is written, freeze/refreeze stamps carry no decision fields/schema, declaration IDs are not yet validated, and no candidate delta can recover removed rows; existing interview controls remain green inside the focused cases.

## EVIDENCE
receipt: pending RED — the exact focused run is required below
gate: HARD-STOP — security Direction is not interviewed or frozen; scope-seal dependency is still open

## LESSONS
none yet
