---
type: Task
title: A versioned trial record separates mechanism provenance and effectiveness
status: done
depth: standard
kind: test
scope:
  - benchmark/schema
  - benchmark/tests
gives:
  - S1 benchmark.schema.trial_record.validate_trial_record(record) -> TrialRecord
generated: { by: add/3.6.0, at: 2026-09-14 }
verified:
  - { by: "plan:codex", at: 2026-09-14, act: freeze, authority: plan, direction: "sha256:8286fe8623d14b5f", binding: "sha256:f0152cc85f9b363a", gives: "sha256:ea07882a176ce488" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:c2e4845d4c42d2d5" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:c2e4845d4c42d2d5" }
  - { by: "process:run", at: 2026-09-14, act: run, authority: process, outcome: PASS, receipt: /tasks/trial-record-schema.d/runs/1.md }
  - { by: "agent:gpt-5.6-picture-acceptance", at: 2026-09-14, act: refute, authority: process, outcome: refuted, probes: 36, receipt: /tasks/trial-record-schema.d/runs/1.md, tier: T2, note: "model-effectiveness records accept no model/evidence; whitespace provenance and non-finite counters pass; mixed unknown keys escape the error contract; pseudonym representation and public import surface are underspecified" }
  - { by: "plan:codex", at: 2026-09-14, act: refreeze, authority: plan, direction: "sha256:5daff5161f722128", binding: "sha256:5b236f0e13444a03", gives: "sha256:e39d4e370a145c23" }
  - { by: "cli", at: 2026-09-14, act: brief, authority: process, brief: "sha256:9d97aaf48a808439" }
  - { by: "process:run", at: 2026-09-14, act: run, authority: process, outcome: PASS, receipt: /tasks/trial-record-schema.d/runs/2.md }
  - { by: "agent:gpt-5.6-trial-v2-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 161, receipt: /tasks/trial-record-schema.d/runs/2.md, tier: T2, note: "public TrialRecord construction bypasses validation; object.__setattr__ can alter the payload; control/format-only and lone-surrogate strings pass, and surrogate snapshots are not UTF-8 encodable" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:df312914e55ddcd4", binding: "sha256:5b236f0e13444a03", gives: "sha256:e39d4e370a145c23" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:b8ee9448596f6418" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/trial-record-schema.d/runs/3.md }
  - { by: "agent:gpt-5.6-trial-v3-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 307, receipt: /tasks/trial-record-schema.d/runs/3.md, tier: T2, note: "mechanism and human-governance records accept non-null model or persona attribution, contaminating the frozen one-layer claim boundary" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:39a53953244f5564", binding: "sha256:5b236f0e13444a03", gives: "sha256:e39d4e370a145c23" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:c7a8bb7e5a55391c" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/trial-record-schema.d/runs/4.md }
  - { by: "agent:gpt-5.6-trial-v4-refute", at: 2026-09-15, act: refute, authority: process, outcome: held, probes: 764, receipt: /tasks/trial-record-schema.d/runs/4.md, tier: T2, note: "receipt 4 held across layer/claim and actor-attribution matrices, participant boundaries, exact nested keys, Unicode category C, counter edges, construction/mutation, strict JSON, and RunRecord v3 separation" }
  - { by: "plan:codex", at: 2026-09-15, act: gate, authority: process, outcome: PASS, receipt: /tasks/trial-record-schema.d/runs/4.md, brief: "sha256:c893aa6f395f492e" }
advised_by: method-steward
---
## CARD
goal: publish a versioned external trial record that keeps mechanism, provenance, and effectiveness distinct
why: empirical claims need a stable, inspectable record without widening the frozen benchmark harness record
beat: done · next: add status

## RULES
<must>
- M1 `benchmark.schema.trial_record.validate_trial_record` is importable from repository root, accepts only an `add.eval-trial/1` record, and is the public construction path for a lossless trial record whose stored snapshot cannot be replaced through normal assignment, deletion, or `object.__setattr__`. Direct `TrialRecord(...)` construction is rejected; this is an API integrity boundary, not a hostile same-process security boundary. (from: enhancement research plan G1 · fails-on: publishing a shadow module that the external harness cannot import, accepting an unversioned or lossy claim, or letting a caller bypass validation or replace the validated snapshot)
- M2 Every record declares exactly one layer and a matching claim boundary: `mechanism` → `implementation_semantics`, `model` → `model_effectiveness`, or `human_governance` → `governance_decision_quality`. `actor.model` and `actor.persona` may be populated only for the model layer and are explicitly `none` for mechanism and human-governance records. (from: enhancement research plan G2 · fails-on: treating a local deterministic fixture as productivity/governance evidence or smuggling model attribution into a non-model claim)
- M3 A valid record carries machine-readable subject and provenance: required strings and evidence references contain non-whitespace, strict UTF-8 text and no Unicode category-C control, format, surrogate, private-use, or unassigned character; roles are `builder | refuter | advisor`; a model-effectiveness record has a model ID/family and at least one receipt or artifact reference; every numeric counter is finite and non-negative; malformed or non-string mapping keys still fail through `TrialRecordError("invalid_trial_record: ...")`. (from: enhancement research plan G1 · fails-on: an invisible, non-encodable, keyed-but-empty, non-finite, or raw-exception record cannot be reproduced or bounded)
- M4 Human participation appears only in the human-governance layer as a harness-issued `participant:<32 lowercase hex>` opaque token; the validator checks this syntax but claims neither de-identification nor identity authentication. Every quantitative counter is explicit, including zero. (from: enhancement research plan G1 · fails-on: identity-looking text leaks into the record or omitted counters become invented measurements)
</must>
<reject>
- R:RUNRECORD_V3 The schema must never accept or extend the frozen benchmark `RunRecord` v3 shape. -> "invalid_trial_record"
- R:LAYER_AUTHORITY The schema must never accept a layer whose declared claim exceeds that layer's authority. -> "invalid_trial_record"
- R:PARTICIPANT_BOUNDARY The schema must never accept a human trial without a pseudonym or a non-human trial with participant data. -> "invalid_trial_record"
- R:UNKNOWN_FIELD The schema must never silently accept an unknown field. -> "invalid_trial_record"
- R:SHADOW_IMPORT The trial record must never live behind a working-directory-dependent shadow `benchmark` package. -> "invalid_trial_record"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the research plan does not say which actor may place a record; taking the validator as an offline, non-authorizing parser with no identity claim -> a future runner needs a separate write-authority contract
- A2 [which] covers: S1 · the research plan names three layers without saying whether one record may span them; taking one record to represent exactly one layer -> cross-layer studies must emit linked records rather than one blended claim
- A3 [when] covers: S1 · the research plan says repairs occur after the first freeze but does not define a timestamp authority; taking the record as a completed-trial snapshot whose `contract_edits_after_first_freeze` is an explicit count -> longitudinal ordering belongs to the harness ledger
- A4 [absent] covers: S1 · the research plan permits no persona and has model-free human/mechanism trials; taking `persona: none` and `model: none` as explicit values outside model-effectiveness records, while required provenance, evidence and counters may never be omitted -> callers must distinguish absence from zero and from unavailable data
- A5 [order] covers: S1 · the research plan does not prescribe a global trial ordering or aggregation rule; taking `trial_id` as an opaque unique identifier with no implied ranking -> dashboards must declare their own ordering and aggregation protocol
- A6 [experience] covers: S1 · the reader is the repository-root external benchmark harness and its research reviewer; taking the public import to be `benchmark.schema.trial_record` and claim limits to remain visible in each record -> packaging or presentation must not shadow the module or collapse layers into an effectiveness score

## PLAN
contract: `benchmark/schema/trial_record.py` owns the sibling `add.eval-trial/1` data contract and no engine/notary behavior. `validate_trial_record(dict) -> TrialRecord` is the public construction path and accepts an exact-key envelope: `schema`, `trial_id`, `layer`, `claim_scope`, `repository`, `add`, `task`, `actor`, `prompt`, `independence`, `environment`, `outcome`, `evidence`, `cost`, `repair`, and `participant`. `repository` is `{revision}`; `add` is `{version, revision}`; `task` is `{corpus_version, id}`; `actor` is `{role, model, persona}` where `model` is `{id, family}` or `none` and `persona` is `{id, digest}` or `none`; `prompt` is `{digest, brief_digest}`; `environment` is `{runner, digest}`; `outcome` is `{task, gate, refute}`; `evidence` is `{test_receipts, artifacts}` with at least one machine-readable reference for model trials; `cost` is `{turns, tool_calls, tokens, wall_time_seconds, cost_usd}`; `repair` is `{rounds, contract_edits_after_first_freeze, false_blockers, severe_misses}`; and `participant` is `{pseudonym: participant:<32 lowercase hex>}` only for `human_governance`, otherwise `none`. Allowed `independence` values are `same_session`, `fresh_session`, `different_model_family`, `human`, and `protected_ci`. All envelope and nested objects require exact string-key sets and reject unknown keys. Every required string is UTF-8 encodable and excludes Unicode category C. Serialization uses strict JSON. The returned snapshot resists normal assignment, deletion, and `object.__setattr__`; Python introspection and hostile same-process mutation remain outside this data-validation contract. The sibling module must not import, mutate, or widen `benchmark.schema.run_record.RunRecord` v3.
regression: affected · python3 -m pytest -q benchmark/tests/test_trial_record.py benchmark/tests/test_run_record.py · proves both the public external-evaluation contract and the frozen RunRecord sibling from repository root
- O1 covers: M2, M3, M4 · signal records rejected by layer/provenance category · window each corpus release · threshold any category rejection rate above 0 after harness migration · action alert

## EDGES
- E1 Given a completed model trial with fresh-session independence and no participant · When its complete record is validated · Then its version, provenance, cost, repair, and model-effectiveness boundary survive a lossless UTF-8 round trip, and callers cannot replace the stored snapshot through the supported construction or attribute APIs.
- E2 Given a mechanism fixture that declares `model_effectiveness`, or a mechanism/human-governance record carrying model or persona attribution · When it is validated · Then validation rejects the cross-layer claim with `invalid_trial_record`.
- E3 Given a human-governance record with no participant pseudonym · When it is validated · Then validation rejects it with `invalid_trial_record`.
- E4 Given a model-effectiveness record with no model or evidence reference · When it is validated · Then it is rejected rather than upgraded from a keyed but empty narrative.
- E5 Given whitespace or Unicode-category-C provenance, non-UTF-8 text, non-finite cost, or heterogeneous mapping keys · When it is validated · Then the one `TrialRecordError` contract holds without permissive JSON or raw Python exceptions.

## CHECKS
- test_trial_record_round_trips_versioned_model_trial · covers: M1,M3,M4,R:SHADOW_IMPORT,E1 · contract · proves the public exact versioned model-trial envelope is lossless, UTF-8 encodable, validator-constructed, and snapshot-immutable
- test_trial_record_rejects_missing_provenance · covers: M3,E4,E5 · contract · proves material claim provenance/evidence cannot be omitted, blank, invisible/control-bearing, non-UTF-8, non-finite, or malformed
- test_trial_record_enforces_layer_authority_and_participant_boundary · covers: M2,M4,R:LAYER_AUTHORITY,R:PARTICIPANT_BOUNDARY,E2,E3,E4 · contract · proves mechanism, model, and human-governance claims and actor attribution remain separate with an opaque-token boundary
- test_trial_record_rejects_runrecord_v3_and_unknown_fields · covers: R:RUNRECORD_V3,R:UNKNOWN_FIELD,R:SHADOW_IMPORT,E5 · contract · proves the frozen benchmark record cannot become the evaluation schema by accretion and malformed keys preserve the error contract
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/trial-record-schema.d/runs/4.md · kind: test-ids · 14/14 reported · exit 0 · 2026-09-15
refute: held · 764 probe(s) · tier T2 · by agent:gpt-5.6-trial-v4-refute · against /tasks/trial-record-schema.d/runs/4.md · 2026-09-15 · receipt 4 held across layer/claim and actor-attribution matrices, participant boundaries, exact nested keys, Unicode category C, counter edges, construction/mutation, strict JSON, and RunRecord v3 separation
gate: PASS · authority process · by plan:codex · receipt /tasks/trial-record-schema.d/runs/4.md · 2026-09-15

## LESSONS
- none filed — no lesson cites /tasks/trial-record-schema.md (add learn <lens> "<lesson>" --evidence /tasks/trial-record-schema.md)
