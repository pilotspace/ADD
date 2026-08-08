# TASK: Deterministic probe suites, regression oracle, tamper detector, judge pin — retire the LLM fidelity float as primary

slug: v2-meter-fixes · created: 2026-07-10 · stage: mvp
milestone: add-bench-v2
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `benchmark/judge.py:default_judge_cmd` (unpinned `["claude","-p",rubric]` — the #28-judge defect) · `benchmark/judge.py:build_rubric_prompt` (grounds ONLY on PROMPT.md + app_check/isolation bits) · `benchmark/score.py:compute_regression_rate` (real ONLY at wm==3 via WM3_REGRESSION_TEST_PATH refactor bait; 0.0 by definition elsewhere) · `benchmark/score.py:score_record` (spec_fidelity = LLM median-of-3 is the PRIMARY fidelity; oracle suites feed nothing numeric) · `benchmark/score.py:_pytest_argv` (pytest-capable interpreter resolution, reuse verbatim) · `benchmark/schema/run_record.py:REQUIRED_METRICS` (frozen EXACT-set of 6 keys — additive keys need a v2 validate) · `benchmark/pilot.py:run_pilot` (execute_wm → score_record per WM; the wiring point for post-WM snapshots) · `benchmark/workload/wm{1..6}/oracle/test_*.py` (deterministic pytest probe suites ALREADY EXIST, driven via BENCH_WORKSPACE + `workload/_oracle_lib.py:running_app` HTTP calls — they are red/green but never scored)
Context (working folder): `benchmark/` harness (v1, all green) · `benchmark/v2/DESIGN.md` (the confirmed design, commit 26b2084) · `benchmark/results/2026-07-sonnet-campaign.md` (the v1 findings this task fixes) · todos #27 (run.py bypasses resolve_setup_steps) + #28-judge (judge unpinned)
Honors (patterns / conventions): stdlib-only, fail-loud `BenchError("<code>: ...")` before any disk write (bench-scaffold convention) · injectable-argv seam for anything that would spawn `claude` (judge_cmd/agent_cmd pattern) · `write_record_atomic` single-writer · all-or-nothing scoring (validate in memory before write)
Seams consulted: none apply (benchmark tree, not the engine — SEAMS.md entries are add.py/add_engine anchors)
Anchors the contract cites: `default_judge_cmd` · `compute_regression_rate` · `score_record` · `validate`/`REQUIRED_METRICS` · `_pytest_argv` · `run_pilot` · `workload/wm*/oracle/` suites
Issues/Risks (→ feed §1): (1) REQUIRED_METRICS is an exact-set equality check — naively adding keys invalidates every archived v1 record; v2 must be ADDITIVE-OPTIONAL. (2) regression_rate's MEANING changes in v2 (earlier-oracle re-runs vs wm3-bait-only) — records must self-describe which semantics produced the number. (3) A mechanical tests_weakened counter can be gamed by assert-replacement (swap a real assert for a trivially-true one — not a removal); count both removals AND weakenings we can detect mechanically, disclose the residual gap. (4) Oracle suites HTTP-probe a live app — a workspace that never boots scores 0.0 pass rate (correct: unreachable = unfaithful), never a harness crash (running_app already guarantees this). (5) `benchmark/runs/` contains archived v1 records — never rewritten by this task.
Related intent: MILESTONE add-bench-v2 exit criteria 1–2 (deterministic fidelity + mechanical tests_weakened) · GLOSSARY: deterministic-first scoring, pinned meter · shared/risky contracts: probe-suite format + record schema v2 both owned HERE
Ground SHA: `26b2084`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: v2 meter fixes — deterministic fidelity primary (oracle pass rate) · generalized regression oracle · mechanical tamper detector · pinned judge demoted to secondary
Framings weighed: extend-the-existing-scorer additively (chosen — v1 records stay valid, oracle suites reused as-is, smallest diff) · new parallel v2 scorer module (rejected: two scorers drift; report ambiguity) · rewrite RunRecord schema breaking-v2 (rejected: invalidates the archived campaign evidence this milestone cites)
Must:
<must>
  - M1 `compute_oracle_pass_rate(workspace, wm)` runs the WM's OWN oracle suite (`workload/wm{wm}/oracle/`) via the existing `_pytest_argv` + `BENCH_WORKSPACE` mechanism and returns passed/total in [0.0, 1.0] — the new PRIMARY fidelity metric `oracle_pass_rate`
  - M2 `compute_regression_rate_v2(workspace, wm)` re-runs ALL earlier WMs' oracle suites (wm1..wm-1) against the current workspace; returns (failed+errored)/total; wm==1 -> 0.0 by definition
  - M3 `tamper.snapshot_tests(workspace, arm_runs_root, wm)` copies the workspace's test files (test_*.py + *_test.py, recursive, excluding .git/.venv/node_modules/__pycache__) into `<arm_runs_root>/snapshots/wm{wm}/` after a done WM
  - M4 `tamper.compute_tests_weakened(arm_runs_root, wm)` mechanically diffs the wm snapshot vs the wm-1 snapshot via ast ASSERT FINGERPRINTS — a fingerprint = the normalized `ast.dump` of an assert's test expression, collected per test function; tests_weakened = (# removed test functions) + Σ over surviving test functions of |prior fingerprints − current fingerprints| (multiset difference — a REPLACED assert counts, not only a removed one); trivially-true asserts (constant-truthy test expression, e.g. `assert True`, `assert 1 == 1`) are EXCLUDED from current fingerprints so swapping a real assert for trivia earns no credit; wm==1 -> 0 by definition
  - M5 `default_judge_cmd` pins the judge model: argv gains `--model claude-sonnet-5`; spec_fidelity stays computed (v1-comparable) but is SECONDARY — score_record writes oracle_pass_rate as the fidelity of record
  - M6 record schema v2 is ADDITIVE-OPTIONAL: `validate` accepts metrics = the 6 REQUIRED keys ∪ any subset of OPTIONAL {oracle_pass_rate, tests_weakened}; every archived v1 record still validates byte-unchanged
  - M7 `score_record` computes + writes oracle_pass_rate (always) and tests_weakened (when a wm snapshot pair exists); regression_rate uses v2 semantics with artifact `regression_source: "v2-earlier-oracles"` self-describing the change
  - M8 `run_pilot` snapshots tests after every status=="done" WM, before score_record — so tests_weakened is computable at wm>=2 with no manual step
</must>
Reject:
<reject>
  - oracle suite collects zero tests or pytest exits outside {0,1} -> "oracle_run_failed"
  - regression re-run collects zero earlier-suite tests at wm>=2 or pytest exits outside {0,1} -> "regression_run_failed"
  - wm>=2 tests_weakened requested but the wm-1 snapshot is missing -> "missing_test_snapshot"
  - a metrics dict carrying any key outside REQUIRED ∪ OPTIONAL -> "invalid_run_record" (unknown keys stay rejected — additive is not open-ended)
  - judge output unparseable/out-of-range -> "unparseable_judge_output" (unchanged v1 behavior)
</reject>
After:
<after>
  - A scored v2 record carries oracle_pass_rate (deterministic, primary) + tests_weakened (mechanical) + v2 regression_rate, alongside the v1 six — and every archived v1 record still loads
  - The LLM judge is pinned to claude-sonnet-5 and demoted to a secondary annotator; no LLM float is a primary metric anywhere in the scorer
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the assert-fingerprint diff now catches removal AND replacement, so the residual risk flips to FALSE POSITIVES: a legitimate test refactor (renamed variable, reshaped assertion of the same behavior) changes fingerprints and counts as weakened; if wrong: an honest arm looks like a gamer. Mitigation: normalization (strip locations/var-name-insensitive dump where safe) reduces cosmetic churn; interpretation stays with the workload scorer — WV2 pairs the number with whether the arm DISCLOSED a spec-change (an approved change request may legitimately rewrite asserts); the number is "departure from prior asserts", never auto-labeled cheating. Residual semantic gap (fixture-neutering) disclosed in docstring + report.
  - [x] the existing wm oracle suites are complete enough to be the fidelity of record for v1-era WMs — confirmed: they encode PROMPT.md behaviors endpoint-by-endpoint (wm1 bookings CRUD, wm2 business rules, wm3 refactor); WV1/WV2 tasks add their own suites.
  - [x] re-running earlier oracle suites against a later workspace is valid — confirmed: suites drive only the fixed entry contract (`python -m app` on $PORT) via BENCH_WORKSPACE; no per-WM harness state leaks.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: oracle pass rate scores a working app deterministically   # M1
  Given a workspace whose app answers 3 of 4 wm1 oracle probes
  When compute_oracle_pass_rate(workspace, 1) runs
  Then it returns 0.75
  And repeated runs return the identical value (no LLM in the path)

Scenario: unbootable workspace scores zero, not a crash   # M1
  Given an empty workspace (python -m app exits immediately)
  When compute_oracle_pass_rate(workspace, 1) runs
  Then it returns 0.0 via ordinary probe failures

Scenario: zero-collection is an error, never a silent 0/0   # R1
  Given a wm whose oracle dir collects no tests in this run
  When compute_oracle_pass_rate runs
  Then it raises BenchError("oracle_run_failed: ...")
  And no record is written

Scenario: v2 regression re-runs every earlier suite   # M2
  Given a wm3 workspace that breaks 2 of the 8 wm1+wm2 oracle probes
  When compute_regression_rate_v2(workspace, 3) runs
  Then it returns 0.25
  And wm==1 returns 0.0 by definition without spawning pytest

Scenario: post-WM snapshot then mechanical weakening count   # M3+M4
  Given a wm1 snapshot holding tests with 5 test functions / 12 asserts
  And a wm2 snapshot where 1 test function was deleted and a surviving one lost 2 asserts
  When compute_tests_weakened(arm_runs_root, 2) runs
  Then it returns 3
  And the count derives from ast alone (no subprocess, no judge)

Scenario: a replaced assert counts as weakened   # M4
  Given a surviving test function whose `assert resp.status == 409` became `assert resp.status != 500`
  When compute_tests_weakened(arm_runs_root, 2) runs
  Then the lost prior fingerprint counts 1 toward tests_weakened

Scenario: trivia earns no credit   # M4
  Given a surviving test function whose real assert was swapped for `assert True`
  When compute_tests_weakened(arm_runs_root, 2) runs
  Then it counts 1 (prior fingerprint lost; the trivial assert is excluded from current fingerprints)
  And an UNCHANGED test function contributes 0

Scenario: missing prior snapshot fails loud   # R3
  Given no wm1 snapshot exists
  When compute_tests_weakened(arm_runs_root, 2) runs
  Then it raises BenchError("missing_test_snapshot: ...")

Scenario: judge is pinned and demoted   # M5
  Given no judge_cmd injection
  When build_judge_argv resolves
  Then the argv contains "--model" "claude-sonnet-5"
  And score_record still records spec_fidelity from the judge seam as a SECONDARY value

Scenario: archived v1 records still validate   # M6
  Given every record.json under benchmark/runs/ and the archive (6 metric keys, no v2 keys)
  When validate() loads it
  Then it returns a RunRecord unchanged
  And a metrics dict with an unknown key still raises "invalid_run_record"   # R4

Scenario: score_record writes the v2 metrics   # M7
  Given a done wm2 record with wm1+wm2 snapshots present
  When score_record runs (fake judge injected)
  Then the written record carries oracle_pass_rate and tests_weakened in metrics
  And artifacts carry regression_source: "v2-earlier-oracles"

Scenario: pilot wires snapshots automatically   # M8
  Given run_pilot completes a done WM (fake agent + fake judge)
  When the WM's score completes
  Then <arm_runs_root>/snapshots/wm{n}/ exists with the workspace's test files
  And a failed/timeout WM takes no snapshot
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
benchmark/score.py:
  compute_oracle_pass_rate(workspace: Path, wm: int) -> float            # M1, in [0.0,1.0]
    runs workload/wm{wm}/oracle/ via _pytest_argv + BENCH_WORKSPACE
    raise -> BenchError("oracle_run_failed: ...")                        # exit ∉ {0,1} or zero collected
  compute_regression_rate_v2(workspace: Path, wm: int) -> float          # M2
    wm==1 -> 0.0 (no pytest spawn); wm>=2 -> re-run wm1..wm-1 oracle suites, (failed+errored)/total
    raise -> BenchError("regression_run_failed: ...")                    # same policy as v1
  score_record(...) additionally writes:                                 # M7
    metrics["oracle_pass_rate"]  (always) · metrics["tests_weakened"] (when wm snapshot pair exists)
    metrics["regression_rate"]   (v2 semantics) · artifacts["regression_source"]="v2-earlier-oracles"
    spec_fidelity: kept, judge-sourced, SECONDARY                        # M5

benchmark/tamper.py (NEW, stdlib+ast only):
  snapshot_tests(workspace: Path, arm_runs_root: Path, wm: int) -> Path  # M3
    -> <arm_runs_root>/snapshots/wm{wm}/ · test_*.py + *_test.py recursive
       excluding .git/.venv/node_modules/__pycache__
  compute_tests_weakened(arm_runs_root: Path, wm: int) -> int            # M4
    wm==1 -> 0; else ast ASSERT-FINGERPRINT diff wm vs wm-1 snapshot:
    fingerprint = normalized ast.dump of an assert's test expr, per test function
    count = removed test functions
          + Σ surviving fns: |prior fingerprints − current fingerprints|  (multiset — replacement counts)
    trivially-true asserts (constant-truthy expr) excluded from CURRENT fingerprints (no credit for trivia)
    raise -> BenchError("missing_test_snapshot: ...")                    # wm>=2, no wm-1 snapshot

benchmark/judge.py:
  default_judge_cmd(rubric) -> ["claude","-p",rubric,"--model","claude-sonnet-5"]   # M5 pin

benchmark/schema/run_record.py:
  OPTIONAL_METRICS = frozenset({"oracle_pass_rate","tests_weakened"})    # M6
  validate(): metric keys must be REQUIRED_METRICS ∪ (subset of OPTIONAL_METRICS)
    unknown key -> BenchError("invalid_run_record: ...")                 # R4, still exact-bounded

benchmark/pilot.py:
  run_pilot: after each status=="done" execute_wm, snapshot_tests(...) BEFORE score_record  # M8
    failed/timeout WM -> no snapshot, no score (unchanged halt semantics)

Schema: record.json metrics gains 2 OPTIONAL keys; artifacts gains regression_source (str);
        snapshots live under <runs_root>/<arm>/snapshots/wm{n}/ — read at score time only.
```

Glossary deltas: `oracle_pass_rate: the deterministic fidelity of record — the WM's own probe-suite pass fraction` · `tests_weakened: mechanical ast-diff count of removed test functions + removed asserts vs the prior WM snapshot` · `regression_source: record artifact naming which semantics produced regression_rate (v1 wm3-bait vs v2-earlier-oracles)`
Least-sure flag surfaced at freeze: [spec/contract] the assert-fingerprint diff (removal + replacement both count; trivia earns no credit) may FALSE-POSITIVE on legitimate test refactors — mitigated by fingerprint normalization and by WV2 pairing the number with change-request disclosure; fixture-neutering remains the disclosed residual gap.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — freeze report rendered 2026-07-10 (banner/ARC/SHAPE, AskUserQuestion)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90% of new/changed lines (tamper.py + the new score/judge/schema branches)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_oracle_pass_rate_partial: arrange fake workspace app answering 3/4 wm1 probes (injected pytest-run seam or real tiny suite) / act compute_oracle_pass_rate / assert 0.75, and identical on re-run · covers: M1
  - test_oracle_pass_rate_unbootable_zero: arrange empty workspace / act / assert 0.0 · covers: M1
  - test_oracle_zero_collection_raises: arrange no-collect oracle run / act / assert BenchError "oracle_run_failed" + no record written · covers: R1
  - test_regression_v2_reruns_earlier_suites: arrange wm3 workspace breaking 2/8 earlier probes / act compute_regression_rate_v2(ws,3) / assert 0.25 · covers: M2
  - test_regression_v2_wm1_zero_no_spawn: arrange wm1 / act / assert 0.0 with no pytest subprocess (spy on the run seam) · covers: M2
  - test_snapshot_copies_test_files: arrange workspace with nested tests + .venv decoys / act snapshot_tests / assert only test files land under snapshots/wm1/ · covers: M3
  - test_tests_weakened_counts_removals: arrange wm1 snapshot (5 fns/12 asserts) + wm2 snapshot (−1 fn, survivor −2 asserts) / act compute_tests_weakened(root,2) / assert 3 · covers: M4
  - test_tests_weakened_counts_replacement: arrange survivor whose assert expr changed / act / assert 1 · covers: M4
  - test_trivial_assert_no_credit: arrange survivor with real assert swapped for `assert True` / act / assert 1; unchanged fn contributes 0 · covers: M4
  - test_tests_weakened_wm1_zero: act compute_tests_weakened(root,1) / assert 0 · covers: M4
  - test_missing_snapshot_raises: arrange no wm1 snapshot / act compute_tests_weakened(root,2) / assert BenchError "missing_test_snapshot" · covers: R3
  - test_judge_pinned_model: act build_judge_argv(rubric, None) / assert "--model" "claude-sonnet-5" present · covers: M5
  - test_v1_records_still_validate: arrange every record.json under benchmark/runs/ (skip-if-none) + a synthetic 6-key record / act validate / assert RunRecord returned · covers: M6
  - test_unknown_metric_key_rejected: arrange metrics with key "bogus" / act validate / assert BenchError "invalid_run_record" · covers: R4
  - test_optional_keys_accepted: arrange metrics with the 6 + both optional keys / act validate / assert ok · covers: M6
  - test_score_record_writes_v2_metrics: arrange done wm2 record + both snapshots + fake judge / act score_record / assert oracle_pass_rate + tests_weakened in metrics, regression_source artifact set · covers: M7
  - test_pilot_snapshots_after_done_wm: arrange fake agent+judge run / act run_pilot / assert snapshots/wm{n}/ exists · covers: M8
  - test_pilot_no_snapshot_on_failed_wm: arrange fake agent forcing timeout / act / assert no snapshot dir · covers: M8
</test_plan>

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/`
Strategy (ordered batches): 1. schema v2 (OPTIONAL_METRICS + validate) — the contract everything else writes into. 2. tamper.py (pure, no subprocess — fastest red→green). 3. score.py additions (oracle_pass_rate + regression v2, reusing _pytest_argv/_extract_count). 4. judge.py pin. 5. score_record wiring. 6. pilot.py snapshot hook. 7. full benchmark pytest suite.
Approach (domain strategy): additive extension of the v1 scorer (chosen §1 framing) — every new number is computed from artifacts alone, deterministic-first; the LLM float survives only as a pinned secondary annotator. Mechanical-diff-over-judgment for tamper detection: ast facts (function/assert counts) not semantic opinion.
Data strategy: metrics dict grows two OPTIONAL keys (exact-bounded: REQUIRED ∪ subset(OPTIONAL)); snapshots are plain file copies under <runs_root>/<arm>/snapshots/wm{n}/ read only at score time — agrees with §3 Schema.
Pattern: bench-scaffold conventions (§0 Honors): stdlib-only, BenchError fail-loud pre-write, injectable-argv seams, write_record_atomic single-writer.
Optimization stance: determinism-first, no perf budget (score paths are offline); ⚠ least-trusted facet: the ast weakening heuristic (the §3 least-sure flag).

Persona (required): methodology-engine-dev — deterministic, fail-loud, no silent defaults.
Spawn isolation (default): n/a — inline build (standing user directive: inline over heavy spawns for sequential work).
Known-problem fixes: exact-set metrics equality would void archived records → additive-OPTIONAL validate (R4 keeps it bounded) · 0/0 pass rate → zero-collection raises oracle_run_failed · homebrew python has no pytest → reuse _pytest_argv fallback · snapshot of a huge .venv → exclusion list in §3 · benchmark tests run via pytest from repo root (pytest.ini), NOT unittest.
Strategy actually used: as planned (schema → tamper → score → judge → wiring → pilot), with two in-build improvements: the security hook's finding replaced dynamic evaluation with an explicit operator table in _is_trivial_assert, and trivia-exclusion was made BOTH-side (an `assert True` present in both WMs is not a lost fingerprint — a false positive the one-sided contract reading would have shipped)
Safety rule (feature-specific): never rewrite an existing record.json except through score_record's validate-then-atomic-write path; archived v1 records are read-only fixtures.
Code lives in: `benchmark/` (score.py · judge.py · tamper.py NEW · schema/run_record.py · pilot.py)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — benchmark suite 154/154 (21 new in test_v2_meter.py)
- [x] coverage did not decrease — every new symbol (compute_oracle_pass_rate · compute_regression_rate_v2 · _run_oracle_suites · snapshot_tests · compute_tests_weakened · OPTIONAL_METRICS · the pilot hook) is directly asserted
- [x] no test or contract was altered during build — the 4 superseded v1 pins (old regression semantics ×2 · exact-6 metric set · "wm == 3" source pin) were amended in a TESTS re-cross (`phase tests` → amend → `phase build`), each STRENGTHENED to pin the frozen v2 behavior, none deleted
- [x] the green was EARNED — refute-read below; real-subprocess coverage exists beside every monkeypatched seam (unbootable-workspace 0.0 runs real pytest; the amended test_score.py regression pins run real fixture apps → 0.2/0.3 from live probes)
- [x] concurrency / timing safe — scoring is offline + sequential per arm; snapshot happens before score in the same thread; no shared mutable state
- [x] no exposed secrets / injection / unexpected deps — tamper.py is stdlib+ast with NO dynamic code evaluation (explicit operator table; security-hook finding honored); subprocess argv are fixed lists, no shell
- [x] layering & dependencies follow conventions — additive to the bench-scaffold shapes; BenchError codes; write_record_atomic single-writer untouched
- [ ] a person reviewed and approved the change — auto-gate under `autonomy: auto`; human spot-audit backstop

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `python3 -m pytest benchmark/tests/test_v2_meter.py` — **21 passed** — confirmed by the pytest summary line 2026-07-10
- [x] the FULL benchmark suite — **154 passed** — confirmed by the summary line (4 superseded v1 pins amended via the TESTS re-cross, disclosed above)
- [x] live smoke — all **46** archived records under benchmark/runs/ validate() unchanged; `build_judge_argv('x', None)` → `['claude','-p','x','--model','claude-sonnet-5']` — confirmed by one-liner output
- [x] tamper.py imports: ast · operator · pathlib · shutil · collections.Counter · schema BenchError — stdlib only, no subprocess — confirmed by its import block

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — compute_oracle_pass_rate/compute_regression_rate_v2/compute_tests_weakened called by score_record; snapshot_tests called by run_pilot, and run_reps delegates to run_pilot per rep so the `run-all` campaign path snapshots too (confirmed by reading run_reps); OPTIONAL_METRICS read by validate
- [x] DEAD-CODE (code) — v1 `compute_regression_rate` + WM3_REGRESSION_TEST_PATH retain no production caller (score_record now routes v2); KEPT deliberately: still pinned by test_regression_split.py + the zero-before-wm3 guard and documents the semantics archived v1 records carry — disclosed as architecture residue below
- [x] SEMANTIC (prose) — tamper.py docstring read in full: both disclosed limits (refactor false-positives · fixture-neutering blindness) match the §3 least-sure flag verbatim

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 cites resolves in the current tree — default_judge_cmd (judge.py) · compute_oracle_pass_rate/compute_regression_rate_v2/score_record/_pytest_argv (score.py) · snapshot_tests/compute_tests_weakened (tamper.py NEW) · OPTIONAL_METRICS/validate (run_record.py) · run_pilot (pilot.py) — confirmed by the green import-time suite + the live smoke
- [x] no §0 anchor moved since Ground SHA 26b2084 — same-session build, tree untouched by others

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) the 4 amended v1 tests — each still pins an EXACT value (0.2 / 0.3 / exact key set / symbol pin), none loosened to a range or removed; (2) monkeypatched seams each have a real-subprocess sibling (unbootable-zero, fixture-app regression pins) so parsing logic cannot be stubbed away; (3) test_pilot_no_snapshot_on_failed_wm was vacuously green pre-build — post-build it actively guards the status!="done" branch (its score_record stub pytest.fails if reached); (4) trivia-exclusion probed both directions (swap-for-trivia counts 1; unchanged trivia counts 0 — both-side exclusion fixed a false positive found during build); (5) 0/0 pass-rate impossible: zero-collection raises before any ratio

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no dynamic code evaluation (explicit operator table), fixed argv lists, no shell, no secrets; snapshot copies confined under runs_root
2. Concurrency: CLEAR — offline sequential scoring; snapshot-then-score same-thread ordering
3. Architecture: RESIDUE — v1 compute_regression_rate kept without a production caller (test-pinned + documents archived-record semantics); prune candidate for a later task
Verdict: PASS
Residue: v1 regression function retained (disclosed, non-blocking)
Binding: advisory — default sensitivity

### GATE RECORD
Reported: yes — gate report (banner/ARC/SUMMARY/EVIDENCE) rendered 2026-07-10 before recording
Outcome: PASS
Reviewed by: auto-resolved on evidence (autonomy: auto) · date: 2026-07-10

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose extend-the-existing-scorer additively; rejected new parallel v2 scorer module (rejected: two scorers drift; report ambiguity) · rewrite RunRecord schema breaking-v2 (rejected: invalidates the archived campaign evidence this milestone cites)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: additive extension of the v1 scorer (chosen §1 framing) — every new number is computed from artifacts alone, deterministic-first; the LLM float survives only as a pinned secondary annotator. Mechanical-diff-over-judgment for tamper detection: ast facts (function/assert counts) not semantic opinion.
- [AI] build — data strategy: metrics dict grows two OPTIONAL keys (exact-bounded: REQUIRED ∪ subset(OPTIONAL)); snapshots are plain file copies under <runs_root>/<arm>/snapshots/wm{n}/ read only at score time — agrees with §3 Schema.
- [AI] build — pattern: bench-scaffold conventions (§0 Honors): stdlib-only, BenchError fail-loud pre-write, injectable-argv seams, write_record_atomic single-writer.
- [AI] build — optimization stance: determinism-first, no perf budget (score paths are offline); ⚠ least-trusted facet: the ast weakening heuristic (the §3 least-sure flag).
- [AI] build — strategy used: as planned (schema → tamper → score → judge → wiring → pilot), with two in-build improvements: the security hook's finding replaced dynamic evaluation with an explicit operator table in _is_trivial_assert, and trivia-exclusion was made BOTH-side (an `assert True` present in both WMs is not a lost fingerprint — a false positive the one-sided contract reading would have shipped)
- [AI] verify — gate PASS (reviewed by auto-resolved on evidence (autonomy: auto))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] trivia-exclusion is BOTH-side, not current-only as §3 literally read — an `assert True` present in both WMs must not count as a lost fingerprint (evidence: false positive found during build; test_tests_weakened_unchanged_suite_is_zero pins it)
- [SPEC · open] v1 `compute_regression_rate` + WM3_REGRESSION_TEST_PATH retained without a production caller — prune or re-purpose when the WV1 workload task touches the wm3 bait (evidence: §6 architecture residue)
- [SPEC · open] WV1/WV2 report must state the tests_weakened false-positive caveat wherever the number prints (evidence: §3 least-sure flag; owned by v2-scoring-report)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] when a frozen contract SUPERSEDES sibling tests' pinned semantics, the honest path is a TESTS re-cross that STRENGTHENS each pin to the new behavior — never an in-build edit, never a deletion (evidence: 4 v1 pins amended, suite 154/154)
- [ADD · open] ground before design: the "missing" deterministic probes already existed as unscored oracle suites — grounding turned an invention task into a wiring task (evidence: §0 Touches)
- [SDD · open] a metric whose MEANING changes needs a self-describing artifact on every record (regression_source), or archived numbers silently mix semantics (evidence: M7)

