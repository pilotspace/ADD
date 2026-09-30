---
type: Task
title: A bounded persona evaluation protocol preserves causal and claim boundaries
status: done
depth: deep
kind: feature
sensitivity: architecture
milestone: personas-prove-value
scope:
  - benchmark/persona_eval
  - benchmark/tests/test_persona_eval_protocol.py
  - benchmark/tests/test_persona_eval_corpus.py
  - benchmark/tests/test_persona_eval_allocation.py
  - benchmark/tests/test_persona_eval_runner.py
  - benchmark/tests/test_persona_eval_report.py
gives:
  - S1 benchmark.persona_eval.protocol.validate_protocol(payload) -> Protocol
  - S2 benchmark.persona_eval.corpus.validate_corpus(payload) -> Corpus
  - S3 benchmark.persona_eval.allocation.allocate(protocol, corpus) -> tuple[TrialCell, ...]
  - S4 benchmark.persona_eval.runner.run_cell(cell, *, agent_cmd=None) -> TrialRecord
  - S5 benchmark.persona_eval.report.summarize(protocol, corpus, cells, records) -> EvaluationReport
generated: { by: add/3.6.0, at: 2026-09-16 }
verified:
  - { by: "plan:personas-prove-value", at: 2026-09-16, act: freeze, authority: plan, direction: "sha256:f8591b59238ea891", binding: "sha256:bb86e15103bdfd2b", gives: "sha256:23c3a0a1aed36419" }
  - { by: "agent:codex", at: 2026-09-16, act: brief, authority: process, brief: "sha256:e422a99bf8fe014f" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/1.md }
  - { by: "agent:persona-harness-refuter", at: 2026-09-16, act: refute, authority: process, outcome: refuted, probes: 63, receipt: /tasks/persona-eval-protocol-harness.d/runs/1.md, tier: T2, note: "omitted live provenance, caller-raised/reset caps, forged cells, oracle leaks, narration-derived grades, unbound report pins, unenforced ceilings, and short writes can make green evidence false", changed: "protocol/corpus/allocation/runner/report adversarial inputs" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/2.md }
  - { by: "agent:persona-harness-refuter", at: 2026-09-16, act: refute, authority: process, outcome: refuted, probes: 79, receipt: /tasks/persona-eval-protocol-harness.d/runs/2.md, tier: T2, note: "live-disable, isolation, observed-usage, budget-protocol, reservation-settlement, repetitions, allocation-membership, stopped-denominator, fresh-session, held-out-evidence, ceiling, and claim-escalation counterexamples still make receipt 2 false", changed: "live protocol, workspace reuse, budget settlement, allocation membership, stop ledger, report limits, and claim text" }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/3.md }
  - { by: "process:run", at: 2026-09-16, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/4.md }
  - { by: "process:run", at: 2026-09-17, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/5.md }
  - { by: "process:run", at: 2026-09-17, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/6.md }
  - { by: "agent:persona-harness-final-review", at: 2026-09-17, act: refute, authority: process, outcome: held, probes: 97, receipt: /tasks/persona-eval-protocol-harness.d/runs/6.md, tier: T2, note: "97 fresh checks held strict digests, detached inputs, exact allocation and seed/repetition authority, explicit provenance preflight, evaluator-blind treatment delivery, subprocess/workspace isolation, callable refusal, cap and stop replay, runner-attested record integrity, pass evidence/counters, complete denominators, and fixture-only claims", changed: "protocol/corpus digests, allocation seed and repetitions, provenance omissions, treatment envelope, workspace/process isolation, cap settlement and stops, record mutation/fabrication, pass evidence, counters, ceilings, denominator, and claim labels" }
  - { by: "process:run", at: 2026-09-17, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/7.md }
  - { by: "plan:personas-prove-value", at: 2026-09-17, act: gate, authority: plan, outcome: PASS, receipt: /tasks/persona-eval-protocol-harness.d/runs/6.md, brief: "sha256:fd8cbd17dd0df568", reason: "receipt 6 reports all 14 frozen checks, receipt 7 confirms the declared regression floor, and fresh T2 held 97 evaluator-blind fixture probes; claim remains fixture-only and no live effectiveness claim is made" }
---
## CARD
goal: Provide a dry-run-first external harness contract for neutral, acceptable routed, and plausible wrong persona trials with prospective cost and provenance controls
why: instruction-truth fixtures prove that personas are valid and reachable, but cannot show that a fitting lens improves a model's task outcome. A prospective external protocol is required before spending money or interpreting repeated trials, because prompt drift, wrong denominators, leaked oracles and post-hoc stopping can manufacture an apparent persona effect.
beat: done · next: add status

## RULES
<must>
- M1 `validate_protocol` accepts only an exact versioned protocol that pins repository revision, ADD version/revision, corpus version/digest, model id/family/effort, runner/environment digest, tool allowlist, prompt-template digest, token/turn/wall-time/per-cell-cost ceilings, repetitions, allocation seed, aggregate USD cap and stop policy. Live execution is false by default; every missing, unknown, blank, negative, non-finite or internally inconsistent value refuses before allocation. The protocol snapshot is immutable and detached.
- M2 `validate_corpus` accepts only an exact versioned corpus whose cases have stable unique IDs, prompt/workspace/oracle/rubric digests, a non-empty acceptable-persona set or explicit `no_fit: true`, and exactly one plausible-wrong persona outside the acceptable set. A no-fit case has an empty acceptable set; a fitted case has at least one. Labels and answers are evaluator-only and are never copied into the agent workspace or prompt.
- M3 `allocate` emits exactly one neutral, one routed-correct and one plausible-wrong cell for every case and repetition. Routed-correct deterministically selects only from the case's acceptable set; for no-fit it is neutral with no persona. Plausible-wrong uses the declared wrong lens. A seeded permutation changes execution order only: the complete task/rep/condition matrix, cell IDs and condition payloads are stable, unique and balanced.
- M4 all cells in one task/repetition block pin identical repository, ADD, model, effort, tools, budgets, base prompt, workspace fixture and grader; condition changes only the persona injection and its digest. Every cell starts in a clean workspace and fresh session. Oracle/rubric paths or matching content hashes in the workspace, prompt or agent-visible files refuse before invocation.
- M5 `run_cell` is dry-run first and injectable: deterministic fixtures may supply a fake agent command, while a live command refuses unless the frozen protocol explicitly enables it. Before every invocation it checks remaining aggregate cap against the cell ceiling and refuses/stops before overspend; retries, if any, consume the same cap and are prospectively bounded. A timeout, command failure, provenance drift, isolation leak or malformed output becomes a recorded attempted outcome or a named pre-invocation stop, never a silently missing cell.
- M6 each attempted model cell writes one atomic `add.eval-trial/1` model record through `validate_trial_record` without changing that schema. Repository, ADD, task/corpus, model/persona, prompt/brief, independence, environment, outcome/evidence, repair and cost fields derive from observed artifacts and frozen pins. Neutral and no-fit cells record `actor.persona: null`; persona conditions record exact id and digest. Agent narration cannot set task success, gate/refute outcome, severe misses or false blockers.
- M7 independent deterministic graders decide task outcome and severe misses from final workspace artifacts and held-out receipts. A false blocker is a persona-attributable refusal or required repair unsupported by the frozen task/rubric; it is counted independently, so a cell may both fail severely and emit false blockers. Repair rounds and post-freeze contract edits are observable counters, never prose estimates.
- M8 `summarize` joins only records matching the frozen protocol, corpus, allocation and provenance. It reports every planned cell as completed, failed, timed out, stopped or missing; groups repeated outcomes at task level; never treats probes, test cases or repetitions as independent tasks; and displays paired per-condition task outcome, severe-miss, false-blocker, repair and cost distributions without declaring statistical significance or persona effectiveness.
- M9 mechanism fixtures may claim only harness semantics. The report labels results `fixture_only` whenever an injected/fake agent participated and refuses to mix fixture and live records. Model results remain `model_effectiveness`; no report, record or summary derives a human-governance conclusion, approval, authority change or routing rollout recommendation.
</must>
<reject>
- R:INVALID_PROTOCOL an incomplete, unknown, non-finite, non-prospective or live-by-default protocol reaches allocation -> "INVALID_PROTOCOL"
- R:INVALID_CORPUS duplicate cases, leaked evaluator material, an empty fitted set, a populated no-fit set, or a wrong persona inside the acceptable set reaches allocation -> "INVALID_CORPUS"
- R:UNBALANCED_MATRIX a task/repetition lacks or duplicates a condition, or seeded order changes membership/payload -> "UNBALANCED_MATRIX"
- R:CONDITION_DRIFT any field other than persona injection/digest differs inside a task/repetition block -> "CONDITION_DRIFT"
- R:ORACLE_LEAK an oracle/rubric path or content hash is agent-visible -> "ORACLE_LEAK"
- R:CAP_EXCEEDED invocation begins when the prospective worst-case cell spend exceeds remaining aggregate cap -> "CAP_EXCEEDED"
- R:PROVENANCE_DRIFT a pinned repository, ADD, corpus, prompt, persona, model, tool or environment digest differs at execution or report time -> "PROVENANCE_DRIFT"
- R:NARRATED_OUTCOME an agent's text is accepted as task, gate, refute, severe-miss or false-blocker evidence -> "NARRATED_OUTCOME"
- R:DENOMINATOR_DRIFT a missing/stopped cell disappears or a probe/repetition becomes an independent task -> "DENOMINATOR_DRIFT"
- R:CLAIM_ESCALATION fixture evidence is reported as model effectiveness, model evidence as governance quality, or any result as permission/authority -> "CLAIM_ESCALATION"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2,S3,S4,S5 · only an external evaluator may enable and fund live trials; fake-agent fixtures have process authority for mechanism semantics only, and neither personas nor model outputs authorize governance -> prevents a harness toggle from becoming spend or policy authority · probe: fixture reports refuse a live or governance claim.
- A2 [which] covers: S1,S2,S3,S4,S5 · the protocol selects one prospectively frozen campaign; its cases and all acceptable/wrong/no-fit labels are frozen before allocation; the runner accepts only allocated cells from that campaign; later exclusion remains visible as missing/stopped rather than changing the corpus -> prevents outcome-aware cherry-picking · probe: report retains every planned cell and corpus or campaign digest mismatch refuses.
- A3 [when] covers: S1,S2,S3,S4,S5 · protocol and corpus validation precede allocation; cap, provenance and isolation checks occur immediately before each invocation, after workspace materialization but before the agent process starts; summary follows record validation -> prevents a valid plan from authorizing a drifted or over-cap execution · probe: a sentinel fake command is never called on each preflight failure.
- A4 [absent] covers: S1,S2,S3,S4,S5 · absence never implies a favorable default: omitted campaign or corpus fields invalidate input, a missing matrix member is not allocated, missing persona on neutral/no-fit is explicit null, missing outcome is missing, missing evidence cannot pass, and omitted cap/pin/refusal data invalidates input -> prevents invented zero-cost successes · probe: absent fields refuse or remain visible in the denominator.
- A5 [order] covers: S1,S2,S3,S4,S5 · strict protocol and corpus snapshots precede canonical allocation; membership and IDs are fixed before seeded execution ordering; cap reservation precedes invocation, record validation precedes atomic replacement, and complete allocation precedes summary -> prevents randomization from changing treatment and prevents partial records · probe: two seeds reorder an identical cell set and over-cap execution writes nothing.
- A6 [experience] covers: S1,S2,S3,S4,S5 · the recipient is a reviewer deciding whether a later paid pilot is interpretable; named errors, manifest digests, complete denominators and task-level paired rows must make confounds visible without reading transcripts -> prevents a polished aggregate from hiding invalid cells · probe: report exposes status and provenance mismatch by planned cell.
every `gives:` surface is swept on every dimension; no dimension is retired.

## PLAN
contract: new stdlib-only `benchmark.persona_eval` modules publish strict immutable Protocol/Corpus/TrialCell/EvaluationReport values and five functions S1-S5; existing `benchmark.schema.trial_record` is consumed unchanged, and no ADD engine/notary path imports this package.
regression: affected · `python3 -m pytest -q benchmark/tests/test_persona_eval_protocol.py benchmark/tests/test_persona_eval_corpus.py benchmark/tests/test_persona_eval_allocation.py benchmark/tests/test_persona_eval_runner.py benchmark/tests/test_persona_eval_report.py` · proves only deterministic mechanism semantics with fake commands and temporary workspaces; a live-model result is outside this Task.
- O1 covers: M1,M5 · signal prospective spend reserved plus completed cost · window one frozen campaign · threshold reserved worst-case never exceeds aggregate cap · action stop before invocation and retain stopped cells
- O2 covers: M2,M3,M8 · signal planned/completed status by task × repetition × condition · window whole manifest · threshold every planned cell represented exactly once · action reject report on duplicate and render missing/stopped without denominator repair
- O3 covers: M4,M6 · signal equality of non-persona condition fields and pinned digests · window each task/repetition block and report join · threshold zero drift · action refuse invocation/report
- O4 covers: M7,M8 · signal task success, severe misses, false blockers, repair and cost · window paired repetitions grouped under task ID · threshold descriptive only in this mechanism Task · action publish distributions with no effectiveness verdict
- O5 covers: M9 · signal evidence layer and runner kind · window every report and mixed input set · threshold fixture-only stays mechanism and human governance stays absent · action refuse claim escalation

## EDGES
- E1 a case lists two acceptable personas; routed-correct may choose either deterministically and must never mark the other wrong.
- E2 a no-fit case has no acceptable persona; neutral and routed-correct are distinct planned conditions with identical null persona payloads, while plausible-wrong injects its declared lens.
- E3 two seeds produce different order but the same canonical cell IDs and payloads; repeated allocation with one seed is byte-stable.
- E4 remaining cap is one cent below the cell ceiling; no fake-agent sentinel, workspace mutation or trial record is produced.
- E5 the workspace contains a renamed byte-identical oracle; path checks alone would miss it, content hashing refuses it.
- E6 the fake agent prints `PASS`, zero blockers and “all tests pass” while the held-out grader fails; the record remains failed with observed severe misses.
- E7 one cell has a severe miss and an unsupported persona refusal; both counters survive independently.
- E8 one repetition times out and another is absent; both remain in the task-level row and neither becomes a task sample.
- E9 otherwise valid records carry the wrong prompt, persona or environment digest; report join refuses rather than dropping them.
- E10 a fixture record and live-marked record are supplied together; summary refuses mixed evidence layers and never emits governance language.

## CHECKS
- test_protocol_is_strict_immutable_and_dry_run_first · covers: M1,A4,R:INVALID_PROTOCOL · exact keys, finite ceilings, required pins and detached snapshot
- test_protocol_rejects_live_default_and_incoherent_cap · covers: M1,M5,A1,A3,R:INVALID_PROTOCOL · live opt-in and prospective cap are explicit and sufficient for one cell
- test_corpus_accepts_sets_and_no_fit_cases · covers: M2,A2,E1,E2 · acceptable sets and null routed persona have distinct condition semantics
- test_corpus_rejects_wrong_overlap_duplicates_and_evaluator_leaks · covers: M2,M4,A4,E5,R:INVALID_CORPUS,R:ORACLE_LEAK · labels and oracle bytes cannot enter agent-visible material
- test_allocation_is_complete_balanced_and_seed_stable · covers: M3,A5,E1,E2,E3,R:UNBALANCED_MATRIX · canonical matrix is independent of randomized execution order
- test_allocation_detects_condition_drift · covers: M3,M4,E3,R:CONDITION_DRIFT · only persona injection/digest may vary inside a block
- test_preflight_cap_stops_before_agent_or_write · covers: M5,A3,A5,E4,R:CAP_EXCEEDED · prospective cap is checked before side effects
- test_preflight_rejects_pin_drift_and_renamed_oracle · covers: M4,M5,A3,E5,R:PROVENANCE_DRIFT,R:ORACLE_LEAK · repository/environment changes and content-hash leaks never invoke the agent
- test_runner_uses_observed_grader_not_agent_narration · covers: M6,M7,A4,E6,R:NARRATED_OUTCOME · artifact grader owns outcomes despite fluent success text
- test_runner_counts_false_blocker_and_severe_miss_independently · covers: M7,E7 · adverse counters are not mutually exclusive
- test_runner_emits_valid_trial_record_without_schema_change · covers: M6 · exact persona/null provenance validates through existing `add.eval-trial/1`
- test_report_preserves_missing_timeout_and_task_denominator · covers: M8,A2,A6,E8,R:DENOMINATOR_DRIFT · planned cells remain visible and task is the independent unit
- test_report_rejects_record_provenance_drift · covers: M8,A6,E9,R:PROVENANCE_DRIFT · cross-record joins fail closed on every frozen digest
- test_report_labels_fixtures_and_refuses_mixed_or_governance_claims · covers: M9,A1,E10,R:CLAIM_ESCALATION · mechanism proof cannot become effectiveness or governance evidence
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/persona-eval-protocol-harness.d/runs/6.md · kind: test-ids · 14/14 reported · exit 0 · 2026-09-17
refute: held · 97 probe(s) · tier T2 · by agent:persona-harness-final-review · against /tasks/persona-eval-protocol-harness.d/runs/6.md · 2026-09-17 · 97 fresh checks held strict digests, detached inputs, exact allocation and seed/repetition authority, explicit provenance preflight, evaluator-blind treatment delivery, subprocess/workspace isolation, callable refusal, cap and stop replay, runner-attested record integrity, pass evidence/counters, complete denominators, and fixture-only claims · changed: protocol/corpus digests, allocation seed and repetitions, provenance omissions, treatment envelope, workspace/process isolation, cap settlement and stops, record mutation/fabrication, pass evidence, counters, ceilings, denominator, and claim labels
gate: PASS · authority plan · by plan:personas-prove-value · receipt /tasks/persona-eval-protocol-harness.d/runs/6.md · 2026-09-17 · receipt 6 reports all 14 frozen checks, receipt 7 confirms the declared regression floor, and fresh T2 held 97 evaluator-blind fixture probes; claim remains fixture-only and no live effectiveness claim is made

## LESSONS
- none yet — Direction/red work does not establish a reusable implementation lesson
- none filed — no lesson cites /tasks/persona-eval-protocol-harness.md (add learn <lens> "<lesson>" --evidence /tasks/persona-eval-protocol-harness.md)
