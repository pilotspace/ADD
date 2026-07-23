# MILESTONE: Honest fidelity meter: deterministic requirement_coverage replaces artifact-blind spec_fidelity

goal: Replace the artifact-blind LLM spec_fidelity metric with a deterministic requirement_coverage meter (frozen per-requirement checklists + probes across all 6 WMs), promote oracle_pass_rate to the headline, and demote the LLM judge to an advisory source-aware code_quality_annotation
rationale: sub-milestone — a live investigation (2026-07-15) proved the LLM `spec_fidelity` judge is artifact-blind: its rubric (judge.py:43-56) = PROMPT.md + 2 oracle booleans, NEVER the built code. Two runs fed byte-identical rubric (md5 69e8f629) yet scored 0.98 vs 0.95 — pure sampling noise incl. a 0.0 hallucination on a working app. A deterministic requirement-coverage meter is the honest replacement. User-confirmed scope 2026-07-15 (3 AskUserQuestion calls: replace-in-place · all-6-WMs · judge→advisory).
stage: mvp · status: active · created: 2026-07-15T02:56:10+00:00
release: pending
relations: relates-to: add-bench-v2

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) swap `spec_fidelity` → `requirement_coverage` in the frozen `REQUIRED_METRICS` set + `validate()`; (2) a deterministic coverage scorer that reads a frozen per-WM requirement checklist, runs its probes against the built app, scores `covered/total`; (3) frozen requirement checklists + probes for WM1–WM6; (4) `context_rot_slope` recomputed over the `requirement_coverage` trajectory (with a back-compat read shim for archived records that only carry `spec_fidelity`); (5) `oracle_pass_rate` promoted to REQUIRED (headline); (6) the LLM judge demoted to an advisory, source-aware `code_quality_annotation` artifact (non-gating). Migrate the ~10 test files that pin the old metric.
Out: no change to the WORKLOAD specs (PROMPT.md wm1–6 stay frozen) · no re-measure of any arm (this is meter code only — re-running arms is a separate paid step) · no new WMs · no scoring of arms other than `add` · the coverage checklists describe EXISTING PROMPT.md requirements, they do not add new ones.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols):
  - `benchmark/schema/run_record.py` — `REQUIRED_METRICS` (stale "5" comment, actually 6: regression_rate, spec_fidelity, tokens_total, cost_usd, context_rot_slope, time_to_first_edit), `OPTIONAL_METRICS` {oracle_pass_rate, tests_weakened}, `validate()` (rejects keys ∉ REQUIRED∪OPTIONAL)
  - `benchmark/score.py` — `score_record`@234 (judge call@297, `metrics["spec_fidelity"]=`@324), `compute_context_rot_slope`@59, `compute_oracle_pass_rate`@131, `_run_oracle_suites`@85, `_fidelity_artifacts`@195 (WM3 trajectory), `_engine_call_census`@225, prior read `prior.metrics["spec_fidelity"]`@270 + slope input@313
  - `benchmark/judge.py` — `judge_fidelity`@59, `judge_fidelity_median`@101, `build_rubric_prompt`@43 (the artifact-blind rubric), `default_judge_cmd`@22
  - `benchmark/workload/wm{1..6}/oracle/*.py` + `PROMPT.md` — the existing behavioral probes to reuse/extend into coverage checklists; `_oracle_lib.py` (`http_call`, `running_app`)
  - `benchmark/report.py` — `METRIC_COLUMNS`@17 (`spec_fidelity` label), `_render_cell`@53 (spec_fidelity_audit hook)
  - `benchmark/tests/` — ~10 files pin the metric: test_score, test_run_record, test_report, test_v2_meter, test_judge_median, test_runner_records, test_run_cli, test_pilot, test_runner_resume, test_wv1_aggregate
Anchors: `RunRecord`, `REQUIRED_METRICS`, `validate()`, `score_record`, `compute_oracle_pass_rate`, `compute_context_rot_slope`, `build_rubric_prompt`
Honors: PROJECT.md invariants (bare-runtime entry contract) · the benchmark's own frozen-metric discipline (a metric-set change is a frozen-contract migration, not a silent edit) · reproducibility pin `claude-sonnet-5` UNCHANGED · never weaken a probe to pass
Issues/Risks (shared):
  - `context_rot_slope` is computed FROM the fidelity trajectory (score.py:313) — swapping the metric silently changes what the slope means; archived records carry only `spec_fidelity`, so prior-WM reads need a `.get("requirement_coverage", .get("spec_fidelity"))` shim or WM3+ scoring of old records breaks
  - the coverage scorer runs real probes against a live app (`running_app`) — same timeout/flake surface as the oracle; design for probe failure (a crashed probe = requirement NOT covered, never a scorer crash)
  - CHANGING a REQUIRED metric NAME ripples into every test that constructs a RunRecord — expect broad, legitimate test migration (TESTS phase, not a tamper)

## Shared decisions & glossary deltas   (living — every task must honor these)
- `requirement_coverage` ∈ [0,1] = (requirements whose probe PASSES) / (total frozen requirements for that WM). Deterministic, reproducible, artifact-reading. This is the fidelity-of-record.
- `oracle_pass_rate` = black-box behavioral pass fraction (existing) — promoted to REQUIRED, the headline floor.
- `code_quality_annotation` = the (fixed, source-aware) LLM judge output — an ADVISORY artifact, NEVER a metric, NEVER gating.
- A per-WM requirement checklist is FROZEN (like a contract): it enumerates the EXISTING PROMPT.md requirements as `(id, description, probe)` rows; adding/removing a row is a deliberate versioned change.

## Shared / risky contracts (freeze these first)
- `requirement_coverage` metric name + [0,1] semantics + the checklist row schema `(id, description, probe_fn)` -> owning task `coverage-scorer`
- the frozen `REQUIRED_METRICS` new membership (spec_fidelity out, requirement_coverage + oracle_pass_rate in) + the archived-record read shim -> owning task `coverage-scorer`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] coverage-scorer   depends-on: none            — swap the frozen metric set + validate() + the deterministic coverage scorer + score.py wiring (slope over coverage, archived-record shim) + report label; ships WM1's checklist as the end-to-end proof on the 2 existing runs
- [x] wm-checklists      depends-on: coverage-scorer   (delivered inside coverage-scorer/coverage-detail/hermetic-scoring — never a standalone task) — frozen requirement checklists + probes for WM2–WM6 (WM1 landed in coverage-scorer), each enumerating that WM's existing PROMPT.md requirements
- [x] judge-advisory     depends-on: coverage-scorer — demote judge.py: rename output to `code_quality_annotation`, feed it the built source tree (fix the artifact-blindness), mark non-gating artifact; drop it from the metric path
- [x] rescore-progression depends-on: wm-checklists, judge-advisory   (delivered 2026-07-23 as a close-out sweep — .add/rescore-progression-2026-07-23.md; 25/25 records, stale post-move artifact paths mechanically repaired) — re-score EVERY existing run under `benchmark/runs/` with the new deterministic meter (no paid agent re-run — probes hit the already-built workspaces; skip + report any workspace that no longer runs), then render a progression view (arm × WM × rep → requirement_coverage + oracle_pass_rate over time) for the user

## Exit criteria (observable; map each to the task that delivers it)
- [x] `run.py score --arm add --wm 1` records a `requirement_coverage` metric computed from WM1's frozen checklist run against the built app — deterministic (same workspace → same score, no LLM call in the metric path)   (← coverage-scorer)
- [x] a RunRecord with `spec_fidelity` instead of `requirement_coverage` is REJECTED by `validate()`; `oracle_pass_rate` is now required   (← coverage-scorer)
- [x] each of WM1–WM6 has a frozen requirement checklist whose row count matches its PROMPT.md's enumerated requirements, and `score` reports a coverage fraction for each   (← wm-checklists + coverage-scorer)
- [x] the LLM judge output appears as a `code_quality_annotation` artifact built from the actual source tree, and NO metric in the record comes from an LLM call   (← judge-advisory)
- [x] every re-scorable existing run under `benchmark/runs/` carries a fresh deterministic `requirement_coverage`, and the user is shown a progression view of the scores across arms/WMs/reps (with any un-re-scorable run explicitly listed, not silently dropped)   (← rescore-progression)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : untouched (benchmark-only milestone)
- skill   : untouched
- book    : untouched
- benchmark : run_record.py REQUIRED_METRICS swap + validate() · score.py deterministic coverage path (compute_coverage_detail, hermetic boot, engine-call census, slope-over-coverage + legacy shim) · judge.py demoted to code_quality_annotation (claude-less by default) · workload/wm1..6/checklist.py frozen checklists · report.py coverage columns + diagnostics

### Cross-task evidence   (one row per task)
- coverage-scorer : gate=PASS · residue=none
- hermetic-scoring : gate=PASS · residue=none
- coverage-detail : gate=PASS · residue=none
- judge-advisory : gate=PASS · residue=none
- report-diagnostics : gate=PASS · residue=none
- status-lean-default : gate=PASS · residue=none
- rescore-progression sweep (close-out, 2026-07-23) : 25/25 records re-scored deterministically, 0 un-re-scorable · 22 stale post-move artifact paths repaired · view: .add/rescore-progression-2026-07-23.md

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (C1/C2 ← coverage-scorer; C3 ← checklists ×6 + live sweep scores for wm1-3 + suite-green wm4-6; C4 ← judge-advisory (judge_cmd=None → "unavailable", zero LLM in any metric); C5 ← the 2026-07-23 rescore sweep)
- goal: deterministic requirement_coverage IS the fidelity-of-record — 2026-07-23 evidence: the WM1 re-measure scored cov=1.00 on 3/3 fresh reps and the sweep reproduced identical scores from identical archived workspaces with no LLM call. Residue noted: WM4's checklist has no row for its CLI filter-flags line (delta filed, not blocking).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
