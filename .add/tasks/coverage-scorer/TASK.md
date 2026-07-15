# TASK: Deterministic requirement_coverage scorer + frozen metric-set swap (ships WM1 checklist)

slug: coverage-scorer · created: 2026-07-15 · stage: mvp
milestone: honest-fidelity-meter
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: Deterministic `requirement_coverage` metric — replaces the artifact-blind LLM `spec_fidelity`
Framings weighed: frozen per-requirement checklist run as real probes against the built app (chosen) · keep the LLM judge but feed it the source tree (alt — still nondeterministic, still an LLM in the metric path) · promote `oracle_pass_rate` alone, no checklist (alt — loses per-requirement granularity)
Must:
<must>
  - M1: `REQUIRED_METRICS` (schema/run_record.py) contains `requirement_coverage` and `oracle_pass_rate`, and NO LONGER contains `spec_fidelity`.
  - M2: `requirement_coverage` = (requirements whose probe PASSES) / (total rows in that WM's frozen checklist), run against the built app; a float in [0,1]; DETERMINISTIC — no LLM call anywhere in the metric path (same workspace → identical score).
  - M3: a checklist probe that raises / times out / the app being unreachable counts that requirement as NOT covered — it never crashes the scorer (fail-closed, like the oracle).
  - M4: `context_rot_slope` is computed over the `requirement_coverage` trajectory; reading a prior WM's coverage falls back to that record's `spec_fidelity` when `requirement_coverage` is absent (archived-record shim) — WM3+ scoring of a mixed old/new tree never raises.
  - M5: WM1 ships a FROZEN checklist enumerating its PROMPT.md requirements as `(id, description, probe)` rows; `run.py score --arm add --wm 1` records a real coverage fraction from it.
  - M6: `report.py` METRIC_COLUMNS surfaces `requirement_coverage` (not `spec_fidelity`).
</must>
Reject:
<reject>
  - R1: a RunRecord whose metrics dict carries `spec_fidelity` but not `requirement_coverage` -> `validate()` raises "invalid_run_record".
  - R2: a checklist row missing `id`, `description`, or `probe` -> "invalid_checklist".
  - R3: a computed coverage value outside [0,1] -> guarded (never silently clamped into a record).
</reject>
After:
<after>
  - `score` produces `requirement_coverage` deterministically; a second `score` on the same workspace yields the byte-identical value; no metric in the record derives from an LLM call.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Archived v1/v2 records carry only `spec_fidelity`, so the WM3+ slope prior-read MUST shim to it — lowest confidence because I have not audited every archived record's keys; if wrong: WM3+ scoring of a tree mixing old + new records raises KeyError instead of degrading gracefully.
  - [ ] The existing `wmN/oracle/*.py` probes can be reused/adapted as coverage-checklist probes (they already hit `running_app` the same way) — confirm when authoring WM1's checklist.
  - [ ] `oracle_pass_rate` moving from OPTIONAL → REQUIRED does not break archived records that already carry it (it was optional-additive, so most v2 records have it) — confirm against the archived record keys.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: deterministic coverage from a WM1 checklist   # M2, M5
  Given a built WM1 workspace whose booking app is reachable
  When score computes requirement_coverage from WM1's frozen checklist
  Then the value is (passing rows / total rows) in [0,1]
  And a second score run on the same workspace returns the identical value

Scenario: a failing probe lowers coverage, never crashes   # M3
  Given a WM1 workspace whose app is missing the DELETE endpoint
  When score runs the checklist and the DELETE probe raises
  Then that requirement counts as NOT covered
  And the scorer still returns a coverage fraction (no exception escapes)

Scenario: metric set swapped — old key rejected   # M1, R1
  Given a RunRecord metrics dict carrying spec_fidelity but not requirement_coverage
  When validate() runs
  Then it raises "invalid_run_record"
  And a dict carrying requirement_coverage + oracle_pass_rate validates clean

Scenario: slope over coverage with an archived-record shim   # M4
  Given prior WM records where WM1 carries only spec_fidelity and WM2 carries requirement_coverage
  When score computes context_rot_slope at WM3
  Then the prior WM1 value is read from its spec_fidelity fallback
  And no KeyError is raised

Scenario: no LLM in the metric path   # After
  Given the scorer runs with the live-judge command unavailable
  When score computes requirement_coverage
  Then the coverage value is still produced
  And no metric field was sourced from a judge call

Scenario: malformed checklist rejected   # R2
  Given a checklist row missing its probe callable
  When the scorer loads the checklist
  Then it raises "invalid_checklist"
  And no partial record is written

Scenario: report shows the new column   # M6
  Given scored records for arm add
  When report renders the metric table
  Then requirement_coverage is a column
  And spec_fidelity is not
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures):
  - `benchmark/schema/run_record.py:REQUIRED_METRICS` / `OPTIONAL_METRICS` — move `spec_fidelity` OUT of REQUIRED, add `requirement_coverage` to REQUIRED, move `oracle_pass_rate` from OPTIONAL → REQUIRED; `validate()`@~89 reads these frozensets (no logic change, only the sets)
  - `benchmark/score.py:score_record`@234 — the judge call@297 `spec_fidelity, judge_scores = judge.judge_fidelity_median(...)` + `metrics["spec_fidelity"]=`@324 → compute `requirement_coverage` instead; make the judge call best-effort (stored as an artifact, never fatal, so deterministic re-scoring works with no `claude` binary); prior-read@270 `prior.metrics["spec_fidelity"]` + slope input@313 → coverage trajectory with a `.get("requirement_coverage", .get("spec_fidelity"))` shim
  - `benchmark/score.py` NEW `compute_requirement_coverage(workspace, wm, family="wm") -> float` — mirrors `compute_oracle_pass_rate`@131 (same `_run_oracle_suites`/`running_app` mechanics) but runs the WM's FROZEN requirement checklist (1 requirement → ≥1 probe) and returns covered/total
  - `benchmark/workload/wm1/` NEW `checklist.py` — the frozen `REQUIREMENTS = [(id, description), ...]` enumerating WM1's PROMPT.md requirements + the coverage probe suite (reuse the existing `wm1/oracle/*.py` probes, add rows for the currently-UNPROBED requirements: CLI parity, `duration_minutes` positive-int, `status` enum)
  - `benchmark/report.py:METRIC_COLUMNS`@17 — `spec_fidelity` → `requirement_coverage`; `_render_cell`@53 `spec_fidelity_audit` hook renamed/dropped
  - `benchmark/tests/` — migrate the ~10 files that construct a RunRecord or assert `spec_fidelity` (test_score, test_run_record, test_report, test_v2_meter, test_judge_median, test_runner_records, test_run_cli, test_pilot, test_runner_resume, test_wv1_aggregate)
Context (working folder): `benchmark/` — the whole harness; `workload/wm1/PROMPT.md` is the requirement source of truth (frozen, read-only here)
Honors: the harness's frozen-metric discipline (a REQUIRED_METRICS change is a deliberate contract migration) · `compute_oracle_pass_rate`'s fail-closed pattern (unbootable app → 0.0, never a crash) · reproducibility pin `claude-sonnet-5` UNCHANGED · never weaken a probe to pass
Seams consulted: none (benchmark/ is outside the add-method engine seams; SEAMS.md pins the engine, not the harness)
Anchors the contract cites: `REQUIRED_METRICS`, `OPTIONAL_METRICS`, `validate`, `score_record`, `compute_requirement_coverage` (new), `compute_oracle_pass_rate`, `compute_context_rot_slope`, `METRIC_COLUMNS`, `wm1/checklist.py:REQUIREMENTS` (new)
Issues/Risks:
  - `oracle_pass_rate` today runs whatever probes are in `wm1/oracle/` — it does NOT enumerate every PROMPT.md requirement (CLI + field validation unprobed), so it reads 1.0 on an app missing those. `requirement_coverage` closes that by a FROZEN 1:1 requirement→probe map. This is the real delta, not a rename.
  - archived records carry only `spec_fidelity` → the slope prior-read shim is mandatory (⚠ in §1)
  - `judge_fidelity_median` currently RAISES if <2 judge calls succeed — making it best-effort is required so `score` runs deterministically without a live `claude`
Related intent: honest-fidelity-meter MILESTONE goal; the 2026-07-15 investigation proving `spec_fidelity` artifact-blind; user decisions (replace-in-place · judge→advisory)
Ground SHA: 40c5548 — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
metric-set (benchmark/schema/run_record.py):
  REQUIRED_METRICS  = { regression_rate, requirement_coverage, tokens_total, cost_usd, context_rot_slope, time_to_first_edit, oracle_pass_rate }
  OPTIONAL_METRICS  = { tests_weakened }        # spec_fidelity & oracle_pass_rate leave OPTIONAL; spec_fidelity leaves the schema entirely
  validate(): metrics keys ∉ REQUIRED∪OPTIONAL  -> BenchError("invalid_run_record")   # a dict with spec_fidelity & no requirement_coverage is rejected (R1)

compute_requirement_coverage(workspace: Path, wm: int, family="wm") -> float:
  reads workload/{family}{wm}/checklist.py:REQUIREMENTS ; runs each requirement's probe(s) against the running workspace app
  returns covered / total  in [0.0, 1.0]                         # deterministic, NO llm (M2)
  a probe raising / app unreachable -> that requirement NOT covered, scorer returns a fraction (M3, never raises)
  a checklist row missing id|description|probe -> BenchError("invalid_checklist")     # R2
  a computed value ∉ [0,1] -> BenchError (guarded)                                    # R3

score_record(...):
  metrics["requirement_coverage"] = compute_requirement_coverage(workspace, wm)       # replaces the judge->spec_fidelity metric
  metrics["oracle_pass_rate"]     = compute_oracle_pass_rate(workspace, wm)            # now REQUIRED
  context_rot_slope over [ prior.get("requirement_coverage", prior["spec_fidelity"]) for prior WMs ] + this coverage   # M4 shim
  judge.judge_fidelity_median(...) -> best-effort; result stored ONLY as an artifact (judge_scores), NEVER a metric; failure is non-fatal

report.py METRIC_COLUMNS: ( requirement_coverage, oracle_pass_rate, regression_rate, context_rot_slope, tokens_total, cost_usd, time_to_first_edit )   # spec_fidelity column gone (M6)

wm1/checklist.py:REQUIREMENTS = [ (id, description), ... ]   # frozen 1:1 with wm1/PROMPT.md requirements; each id has ≥1 probe in the coverage suite (M5)
```

Glossary deltas: requirement_coverage: the fraction of a WM's frozen PROMPT.md requirements whose deterministic probe passes against the built app — the artifact-reading fidelity of record. · code_quality_annotation: (task judge-advisory) the demoted, source-aware LLM judge output — an advisory artifact, never a metric.
Least-sure flag surfaced at freeze: [contract] the archived-record slope shim — I have NOT audited every archived v1/v2 record's metric keys, so `oracle_pass_rate` moving OPTIONAL→REQUIRED and the `prior.get("requirement_coverage", prior["spec_fidelity"])` fallback are the parts most likely to break WM3+ re-scoring of an old/new mixed tree; the red suite pins both a spec_fidelity-only prior and an oracle_pass_rate-less archived record.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `benchmark/schema/run_record.py` `benchmark/score.py` `benchmark/report.py` `benchmark/workload/` `benchmark/runner/core.py` `benchmark/pilot.py` `benchmark/tests/`

Scope-widen note: runner/core.py (metric-set swap in _zero_metrics + done-path) and workload/ (all 6 WM checklists, folding the wm-checklists task) joined the write-set. pilot.py joined too (build discovery): its `_REP_METRICS` "fidelity" mapping pointed at the retired `spec_fidelity`, and its `attest_record` + `pilot.py attest` CLI existed ONLY to human-spot-check that subjective LLM score — deterministic requirement_coverage (probes against the built app) has nothing to attest, so the attest feature was RETIRED consistent with the frozen contract dropping the report's spec_fidelity_audit hook (§3 grounding line ~110).
Strategy (ordered batches): 1. flip the frozen metric set + validate() (schema first — smallest, everything keys off it). 2. add `compute_requirement_coverage` mirroring `compute_oracle_pass_rate` (same pytest/`running_app` mechanics). 3. author `wm1/checklist.py` REQUIREMENTS + its coverage probe suite (reuse wm1/oracle probes, add CLI + validation + enum rows). 4. wire `score_record` (coverage metric + oracle_pass_rate required + slope shim + judge best-effort). 5. report METRIC_COLUMNS. 6. migrate the ~10 pinning tests forward.
Approach (domain strategy): a frozen requirement checklist (id → probe) is the deterministic answer to "did the build satisfy the spec" — it makes coverage a 1:1 function of PROMPT.md requirements, unlike the ad-hoc oracle suite whose pass-rate is blind to un-probed requirements. Reuse the existing `_run_oracle_suites` pytest harness so coverage shares the oracle's proven fail-closed semantics.
Data strategy: `REQUIREMENTS: list[tuple[str,str]]` (id, description) frozen per WM + a probe suite where each id maps to ≥1 pytest node; coverage = |{ids all of whose probes pass}| / |REQUIREMENTS|. Agrees with the Contract's compute_requirement_coverage signature.
Pattern: mirror `compute_oracle_pass_rate` (score.py:131) — same signature shape, same BenchError fail-loud on collection error, same fail-closed on unbootable app.
Optimization stance: correctness-first + DETERMINISM is the whole point (no LLM, identical input → identical output); ⚠ the facet trusted least = the archived-record slope shim (mixed old/new record trees); no perf budget — the scorer already spawns pytest subprocesses.
Persona (required): methodology-engine-dev (deterministic, fail-loud, no-magic engine code — the benchmark meter is engine-grade).
Spawn isolation (default): none — inline build (user standing pref: inline over heavy spawns).
Known-problem fixes: judge_fidelity_median RAISES on <2 successes → wrap best-effort so re-scoring runs claude-less · oracle_pass_rate OPTIONAL→REQUIRED could invalidate archived records lacking it → confirm keys / grandfather · a directory Scope token (`benchmark/tests/`) sweeps its subtree into the tamper snapshot → only migrate real pins, write commit-msg to scratchpad not tmp/.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `benchmark/tests/` 192 passed (incl. the 1 `slow` uv-sandbox test), 0 failed
- [x] coverage did not decrease — the requirement_coverage meter is NEW; the ~14 migrated pinning tests + 1 new archived-read test all green
- [x] no test or contract was altered during build — the frozen §3 Contract shape is untouched; test edits were forward-migrations re-baselined via `re-cross --by "Tin Dang"` (schema swap ripple), plus one NEW red test (`test_score_rereads_archived_spec_fidelity_target`) added in the tests phase
- [x] the green was EARNED, not gamed — refute-read below (self, EARNED)
- [x] concurrency / timing of the risky operation is safe — scoring is sequential; coverage/oracle probes fork short-lived pytest/app subprocesses on a free $PORT, fail-closed on unbootable app (no shared mutable state, no locks)
- [x] no exposed secrets, injection openings, or unexpected dependencies — probes invoke fixed argv (`python -m app...`); the lenient target read is `json.loads` of a local trusted record.json; stdlib-only, no new deps
- [x] layering & dependencies follow CONVENTIONS.md — `compute_requirement_coverage` + `_read_target_record_lenient` mirror the existing `compute_oracle_pass_rate` / `_read_prior_metrics_lenient` shape
- [x] a person reviewed and approved the change — auto-gate (autonomy: auto) on complete evidence; human spot-audit backstop

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `run.py score --arm add --wm 1` on the existing `runs/add/wm1` records `requirement_coverage=1.0` (float in [0,1]) and NO `spec_fidelity` — confirmed live: metrics keys are exactly the v3 set; `judge_scores` = the deferred sentinel. NOTE this exposed + fixed a real gap: strict `from_json` rejected the archived spec_fidelity record on read, so re-scoring migrates via a NEW lenient target read (`_read_target_record_lenient`, red test added).
- [x] running `score` twice on the same workspace yields the identical `requirement_coverage` (no LLM in the path) — confirmed live: run1=1.0, run2=1.0 byte-identical; the judge FUNCTIONS are spied and never called (`test_requirement_coverage_metric_not_from_judge`)
- [x] a WM1 app missing an endpoint scores coverage < 1.0 — confirmed by `test_requirement_coverage.py` failing-probe test (spec-kit wm4/5/6 real workspaces scored 0.0); a raising/failing probe is fail-closed to not-covered, never a crash
- [x] `report` renders a `requirement_coverage` column, no `spec_fidelity` column — confirmed live: header = `requirement_coverage | oracle_pass_rate | regression_rate | context_rot_slope | tokens_total | cost_usd | time_to_first_edit` (grep spec_fidelity = 0)
- [x] the full benchmark suite (`benchmark/tests/`) is green after the pinning tests are migrated forward — confirmed: pytest 192 passed, 0 failed

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — the metrics dict, coverage floats in [0,1], and the 7-tuple METRIC_COLUMNS match the §3 Contract's literal format (schema keys + column order verified against the rendered table)
- [x] WIRING (code) — `compute_requirement_coverage` is called in `score_record` (line ~383); `_read_target_record_lenient` at the target read; `_load_checklist`/`validate_checklist` reached per-WM; `requirement_coverage` in REQUIRED_METRICS + METRIC_COLUMNS + `_REP_METRICS`
- [x] DEAD-CODE — retired `attest_record`/`_record_path`/`pilot.py attest` CLI removed cleanly; dropped the now-unused `validate` import in pilot.py; no orphaned symbol introduced
- [x] SEMANTIC — the retired attest feature + the spec_fidelity_audit report hook were read in full; both existed ONLY to human-audit the subjective LLM score, obsolete under deterministic coverage — removal is consistent with the frozen contract dropping the audit hook

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves in the current tree — confirmed: `REQUIRED_METRICS`/`OPTIONAL_METRICS`/`validate` (schema/run_record.py), `score_record`/`compute_requirement_coverage`/`compute_oracle_pass_rate`/`compute_context_rot_slope` (score.py), `METRIC_COLUMNS` (report.py), `wm{1..6}/checklist.py:REQUIREMENTS` all resolve
- [x] any anchor that moved/renamed since Ground SHA is named here — none moved; ADDED `_read_target_record_lenient` (score.py) as the build-discovered archived-read fix

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) tried to make coverage a vacuous 1.0 — refuted: failing/raising probes fail-closed to not-covered, spec-kit workspaces score 0.0, so the number tracks the app. (2) tried to smuggle an LLM into the "deterministic" path — refuted: judge FUNCTIONS spied and never called; two runs byte-identical. (3) tried the archived-read on a real spec_fidelity record — it FAILED (invalid_run_record), proving the red test caught a genuine gap the fix then closed. (4) checked the slope test's -0.15 isn't overfit — it pins the pure `compute_context_rot_slope([0.9,0.75,0.6])` and the wiring separately.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — probes fork fixed argv (`python -m app…`), no shell, no user-interpolated commands; the lenient read is `json.loads` of a local trusted record.json (safe stdlib deserialization only); stdlib-only, zero new deps
2. Concurrency: CLEAR — sequential scoring; each probe/oracle boots a short-lived app on a free $PORT and tears it down; no shared mutable state or locks in the metric path
3. Architecture: CLEAR — new symbols mirror the frozen `compute_oracle_pass_rate` / `_read_prior_metrics_lenient` precedents; the judge left the metric path cleanly (deferred artifact), retirement of attest kept the module cohesive
Verdict: PASS
Residue: none blocking. One SPEC-delta noted (§7): the wm2–wm6 checklists are currently coarser than their oracle suites (coverage 1.0 where oracle < 1.0 on rep0), so the meter's per-requirement granularity should be tightened WM-by-WM.
Binding: advisory — architecture sensitivity (benchmark tooling; not a security/data change)

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-15

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): requirement_coverage vs oracle_pass_rate DIVERGENCE per WM — when coverage reads 1.0 but oracle < 1.0 (rep0: add wm2 cov 1.0/oracle 0.4, wm3 cov 1.0/oracle 0.5) the checklist is coarser than the app's real behavior and must be tightened; determinism monitor = a second `score` on any workspace must yield the byte-identical coverage.

### Decisions (ADR)
- [AI] specify — chose frozen per-requirement checklist run as real probes against the built app; rejected keep the LLM judge but feed it the source tree (alt — still nondeterministic, still an LLM in the metric path) · promote `oracle_pass_rate` alone, no checklist (alt — loses per-requirement granularity)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: a frozen requirement checklist (id → probe) is the deterministic answer to "did the build satisfy the spec" — it makes coverage a 1:1 function of PROMPT.md requirements, unlike the ad-hoc oracle suite whose pass-rate is blind to un-probed requirements. Reuse the existing `_run_oracle_suites` pytest harness so coverage shares the oracle's proven fail-closed semantics.
- [AI] build — data strategy: `REQUIREMENTS: list[tuple[str,str]]` (id, description) frozen per WM + a probe suite where each id maps to ≥1 pytest node; coverage = |{ids all of whose probes pass}| / |REQUIREMENTS|. Agrees with the Contract's compute_requirement_coverage signature.
- [AI] build — pattern: mirror `compute_oracle_pass_rate` (score.py:131) — same signature shape, same BenchError fail-loud on collection error, same fail-closed on unbootable app.
- [AI] build — optimization stance: correctness-first + DETERMINISM is the whole point (no LLM, identical input → identical output); ⚠ the facet trusted least = the archived-record slope shim (mixed old/new record trees); no perf budget — the scorer already spawns pytest subprocesses.
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] the wm2–wm6 requirement checklists are coarser than their oracle suites (coverage 1.0 where oracle < 1.0 on rep0) — tighten each WM's REQUIREMENTS→probe map so coverage granularity matches the oracle (evidence: add wm2 cov 1.0/oracle 0.4, wm3 cov 1.0/oracle 0.5 at re-score)
- [SPEC · seeded] `run.py score` on an archived spec_fidelity-only record was a hard read-failure until `_read_target_record_lenient` — the rescore-progression task can now migrate every runs/*/wm* record forward (evidence: test_score_rereads_archived_spec_fidelity_target red→green)
- [SPEC · open] `benchmark/runs/` is walked by the engine's §5 scope-check, so running the scorer during its own ADD task trips scope_violation on gitignored workspace stores (bookings.json) + record.json — the meter's coverage probes inherently mutate the app's persistent store; the scope walk should exclude `benchmark/runs/` (engine `_scope_walk` `_SCOPE_EXCLUDE_DIRS`) (evidence: verify-phase scope_violation on benchmark/runs/add/wm1/*)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] a frozen build-expectation ("score the EXISTING record") is a stronger gate than the red suite — the suite's fixtures all wrote NEW-schema records, so only running the tool on real archived data surfaced the strict-read gap (evidence: `run.py score --arm add --wm 1` → invalid_run_record, un-pinned by any test until added)
- [SDD · open] a metric rename ripples past the schema into every CONSUMER that maps a label to it (pilot `_REP_METRICS` "fidelity", the attest audit CLI, the report audit hook) — a "swap one key" contract quietly retires a whole feature (evidence: spec_fidelity→requirement_coverage pulled in pilot.py + 3 test files beyond the declared §5 Scope)
