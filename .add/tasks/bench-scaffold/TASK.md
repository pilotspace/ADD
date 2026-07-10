# TASK: benchmark/ tree: workload spec, oracle suites, 5 arm definitions, run-record schema

slug: bench-scaffold · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): greenfield — `benchmark/` does not exist yet (verified: repo root holds only `.add/ .claude/ .claude-plugin/ .github/ add-method/ tmp/ tools/`). New module: `benchmark/workload/` (WM specs + oracle suites) · `benchmark/arms/` (5 arm recipes) · `benchmark/schema/run_record.py` (run-record shape). Reads (never changes): `add-method/` only as the ADD-arm install source.
Context (working folder): `.add/milestones/add-bench/MILESTONE.md` (frozen metric names · fairness floor · oracle-isolation decision live there); repo `.gitignore` (arm workspaces + run outputs must be ignored); no CI wiring (out of scope per MILESTONE.md).
Honors (patterns / conventions): CLAUDE.md ADD block (this task itself runs the specification bundle); PROJECT.md "Domain (DDD) — the language and the boundaries" (benchmark terms enter GLOSSARY as deltas); stdlib-first Python 3 like `add-method` tooling — no new runtime deps without listing.
Seams consulted: none apply — `benchmark/` is outside every SEAMS.md pin (engine/skill/book untouched).
Anchors the contract cites: `benchmark/schema/run_record.py:RunRecord` (new) · `benchmark/arms/<arm>.toml` arm-recipe keys (new) · `benchmark/workload/wm<1-3>/PROMPT.md` + `benchmark/workload/wm<1-3>/oracle/test_*.py` (new) · `benchmark/check_isolation.py:main` (new, the oracle-leak loud check).
Issues/Risks (→ feed §1): (1) oracle contamination — if oracle tests are copied into an arm workspace the whole pilot is invalid; needs a loud automated check, not a convention. (2) arm fairness drift — GSD/spec-kit recipes need pinned upstream versions or results aren't reproducible. (3) WM3 must genuinely bait regressions (breaking change to a WM1 shape) or `regression_rate` measures nothing. (4) `tmp/` commit-msg name collisions across milestones (known lesson).
Related intent: MILESTONE.md add-bench rationale (new-major, confirmed 2026-07-07) · PROJECT.md goal line ("less doc-time than GSD" — the claim this benchmark tests) · GLOSSARY deltas pending: arm · workload milestone · oracle suite.
Ground SHA: 0ff7d75

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: benchmark scaffold — workload · oracles · arms · run-record
Framings weighed: static-assets-first (chosen — freeze the data shapes before any runner code; runner/scorer tasks build against them) · runner-first (rejected: metrics/workload churn would thrash the runner contract) · one-big-task (rejected at intake: 4-task breadth-first)
Must:
<must>
  - M1 workload: `benchmark/workload/wm{1,2,3}/PROMPT.md` — identical raw request text served to every arm; WM1 = task/booking core CRUD (REST API + CLI), WM2 = business rules + auth on top, WM3 = a breaking-change refactor of a WM1-frozen shape (the regression bait) — each PROMPT.md names the fixed app entry contract (`python -m app` serving HTTP on `$PORT`) so oracles can drive any arm's output
  - M2 oracles: `benchmark/workload/wm{1,2,3}/oracle/test_*.py` — pytest suites that take the workspace under test via `BENCH_WORKSPACE` env var; each suite collects cleanly and FAILS against an empty workspace (red for the right reason); WM3's oracle re-runs WM1+WM2 oracles to feed `regression_rate`
  - M3 arms: `benchmark/arms/{add,vanilla,plan-mode,gsd,spec-kit}.toml` — required keys `name · setup_steps · prompt_wrapper · pin` (pinned upstream version/SHA for gsd & spec-kit; add pins to this repo's add-method); fairness fields `same_model=true · token_ceiling · turn_ceiling` identical across all 5
  - M4 run-record: `benchmark/schema/run_record.py:RunRecord` (stdlib dataclass) + `validate(dict)` — required fields arm · wm · rep · status(`done|timeout|failed`) · metrics(exactly the 5 frozen names) · artifacts(paths); JSON round-trip
  - M5 isolation check: `benchmark/check_isolation.py:main(workspace)` exits non-zero printing `oracle_leak` if any oracle file (by relative path or content hash) is present in the workspace; exits 0 clean; `benchmark/runs/` is gitignored
</must>
Reject:
<reject>
  - run record with a missing required field or a metric name outside the frozen 5 -> "invalid_run_record"
  - arm recipe missing a required key or (gsd|spec-kit) missing a pin -> "invalid_arm_recipe"
  - oracle file detected inside an arm workspace -> "oracle_leak" (exit code 1, loud)
</reject>
After:
<after>
  - `benchmark/{workload,arms,schema}` + `check_isolation.py` exist; all 3 oracle suites collect and run red against an empty workspace; all 5 arm recipes validate; a well-formed run record validates and a corrupt one is rejected; `benchmark/runs/` ignored by git
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] GSD and spec-kit ship pinnable, headless-usable artifacts — CONFIRMED 2026-07-07 (web): spec-kit pins via `uvx --from git+https://github.com/github/spec-kit.git@vX.Y.Z specify init --here` (release tags only); GSD via npm `get-shit-done-cc@<semver>` or plugin-repo SHA (jnuyens/gsd-plugin), pre-seeded into `.claude/` before headless runs
  ⚠ the fixed app entry contract (`python -m app` on `$PORT`) is method-neutral — if an arm's method conventions fight it, spec_fidelity conflates method vs. entry-contract friction; mitigation: the contract line is stated verbatim in every PROMPT.md
  - [ ] pytest + env-var workspace injection is enough for oracles (no docker needed at pilot scale) — confirm at tests
  - [ ] content-hash matching catches renamed oracle leaks well enough for MVP — confirm at tests
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: identical prompts with regression bait   # M1
  Given the three workload PROMPT.md files
  When their text is read
  Then each names the app entry contract verbatim ("python -m app", HTTP on $PORT)
  And WM3's prompt requires changing a shape WM1's oracle asserts

Scenario: oracle red on empty workspace   # M2
  Given BENCH_WORKSPACE points at an empty directory
  When each wm oracle suite runs under pytest
  Then collection succeeds and every test fails (red for the right reason)

Scenario: WM3 oracle covers regression   # M2
  Given the WM3 oracle suite
  When its tests are collected
  Then it includes the WM1 and WM2 oracle tests (re-exported), tagged for regression_rate

Scenario: five valid arm recipes   # M3
  Given benchmark/arms/*.toml
  When each is validated
  Then all 5 load with required keys and identical fairness fields (same_model, token_ceiling, turn_ceiling)

Scenario: run record round-trip   # M4
  Given a complete run-record dict with the 5 frozen metric names
  When validate() then JSON round-trip runs
  Then it returns an equal RunRecord

Scenario: reject corrupt run record   # R:invalid_run_record
  Given a record missing `metrics` or naming metric "speed"
  When validate() runs
  Then it raises/returns error "invalid_run_record"
  And no record file is written

Scenario: reject unpinned competitor arm   # R:invalid_arm_recipe
  Given gsd.toml without a `pin` key
  When arm validation runs
  Then error "invalid_arm_recipe" names the missing key
  And the other arm recipes still validate

Scenario: oracle leak is loud   # M5, R:oracle_leak
  Given a workspace containing a copy (even renamed) of a wm1 oracle test file
  When check_isolation.py runs against it
  Then it exits 1 and prints "oracle_leak" with the offending path
  And a clean workspace exits 0

Scenario: run outputs never committed   # M5
  Given a file created under benchmark/runs/
  When `git status --porcelain` runs
  Then the file does not appear
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
benchmark/schema/run_record.py
  RunRecord(arm: str, wm: int, rep: int, status: "done"|"timeout"|"failed",
            metrics: {regression_rate, spec_fidelity, tokens_total, cost_usd,
                      context_rot_slope, time_to_first_edit},   # exactly these keys
            artifacts: {workspace, transcript, oracle_report})  # repo-relative paths
  validate(d: dict) -> RunRecord | raises BenchError("invalid_run_record")
  to_json/from_json round-trip stable

benchmark/arms/<arm>.toml   (arm ∈ add|vanilla|plan-mode|gsd|spec-kit)
  required: name, setup_steps: [str], prompt_wrapper: str, pin: str
  fairness (identical across arms): same_model=true, token_ceiling: int, turn_ceiling: int
  load_arm(path) -> Arm | raises BenchError("invalid_arm_recipe: <missing key>")

benchmark/workload/wm{1,2,3}/PROMPT.md    # verbatim entry contract: `python -m app`, HTTP on $PORT
benchmark/workload/wm{1,2,3}/oracle/test_*.py   # workspace via $BENCH_WORKSPACE; wm3 re-exports wm1+wm2

python3 benchmark/check_isolation.py <workspace>
  exit 0 -> clean
  exit 1 -> "oracle_leak: <path>"   (match by relative path OR content hash)
Schema: no DB — file shapes above are the schema; benchmark/runs/ gitignored, written only by later tasks
```

Glossary deltas: `Arm: one method configuration driving Claude Code headlessly; arms never share workspace state` · `Workload milestone (WM): one of 3 fixed evolution steps of the benchmark target app, identical prompts across arms` · `Oracle suite: harness-owned scoring tests per WM, never visible to the arm under test`
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07)
Reported: yes — freeze report (banner/ARC/SHAPE/FLAGS) rendered; ⚠1 resolved pre-freeze with web evidence
Least-sure flag surfaced at freeze: [spec/contract] the fixed app entry contract (`python -m app` on `$PORT`) is method-neutral — if an arm's conventions fight it, spec_fidelity conflates method friction with entry-contract friction; mitigated by stating the line verbatim in every PROMPT.md; human accepted at freeze (the pinnability flag was resolved with web evidence before approval)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90% of `benchmark/schema/` + `benchmark/check_isolation.py` (prompt/oracle assets covered by content asserts)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_prompts_identical_contract_and_bait: read 3 PROMPT.md / assert entry-contract line verbatim in each + wm3 names a wm1-frozen shape change · covers: M1
  - test_oracles_red_on_empty_workspace: BENCH_WORKSPACE=emptydir / run pytest per wm oracle / assert collected>0 and all fail · covers: M2
  - test_wm3_oracle_includes_regression_reexports: collect wm3 oracle / assert wm1+wm2 test ids present with regression tag · covers: M2
  - test_five_arms_validate_with_fairness_parity: load all arms/*.toml / assert 5 Arms + identical fairness triple · covers: M3
  - test_run_record_round_trip: build full dict / validate + to_json/from_json / assert equality · covers: M4
  - test_invalid_run_record_rejected: drop `metrics`, then add metric "speed" / assert BenchError "invalid_run_record" + nothing written · covers: R:invalid_run_record
  - test_unpinned_arm_rejected: gsd.toml copy minus `pin` / assert "invalid_arm_recipe" names key + other arms still load · covers: R:invalid_arm_recipe
  - test_oracle_leak_detected_even_renamed: copy a wm1 oracle file into tmp workspace under a new name / run check_isolation / assert exit 1 + "oracle_leak" + path; clean dir exits 0 · covers: M5, R:oracle_leak
  - test_runs_dir_gitignored: create benchmark/runs/probe / assert absent from `git status --porcelain` · covers: M5
</test_plan>

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/` `.gitignore`
Strategy (ordered batches): 1. `benchmark/schema/run_record.py` (RunRecord + validate + BenchError, JSON round-trip) — the shape everything else's tests import. 2. `benchmark/arms/*.toml` + `benchmark/arms/loader.py` (load_arm) with real pins (gsd: `get-shit-done-cc@1.42.3` via npm; spec-kit: `git+https://github.com/github/spec-kit.git@v0.12.5`, latest release tag; add: this repo's `add-method` path) — identical fairness triple on all 5. 3. `benchmark/workload/wm{1,2,3}/PROMPT.md` — method-neutral task/booking REST+CLI prose, each with the verbatim entry-contract line; WM3 breaks WM1's `duration_minutes` shape (regression bait). 4. Oracle suites keyed by `$BENCH_WORKSPACE`, driving the app over HTTP via a shared stdlib helper (`benchmark/workload/_oracle_lib.py`, kept OUTSIDE every `oracle/` dir so it's never itself an oracle-leak candidate); WM3 re-exports WM1+WM2 tests under `test_regression_*` names tagged `@pytest.mark.regression`. 5. `benchmark/check_isolation.py` (path OR sha256 content-hash match, loud `oracle_leak: <path>` + exit 1). 6. `.gitignore` entry for `benchmark/runs/`.
Approach (domain strategy): stdlib-first, fail-loud validation at every boundary (RunRecord/Arm loaders raise `BenchError` with the frozen error-code prefix rather than silently coercing) — mirrors the methodology-engine-dev discipline of pure validation functions + no silent partial writes, applied here to benchmark data shapes instead of the ADD engine itself.
Data strategy: 3 independent stdlib dataclass/TOML shapes (RunRecord, Arm, PROMPT.md+oracle files) with no shared DB — matches the §3 Schema line ("no DB — file shapes above are the schema").
Pattern: fixture-and-oracle pattern — a frozen prompt (fixture) + a harness-owned, arm-invisible oracle suite (test) per workload milestone, isolation enforced by a standalone loud checker; extends CLAUDE.md's red/green TDD discipline into the benchmark's own arm-scoring loop.
Optimization stance: correctness-first, no perf budget — this is pilot-scale (5 arms × 3 WMs × 1 rep), not a hot path. ⚠ least-trusted facet: the oracle HTTP-driving helper's startup-detection heuristic (poll-until-port-answers) — good enough for stdlib-only pilot scale but untested against a slow-starting real arm-built app; flagged for bench-runner to harden.
Persona (required): methodology-engine-dev — adapted from its `add.py`-engine stance to this benchmark's harness code (fail-loud validation, pinned versions, stdlib-first); no benchmark-specific persona exists yet.
Spawn isolation (default): worktree — no shared-tree reason applied (single-agent build, no parallel spawn needed for this task).
Known-problem fixes: oracle contamination → `check_isolation.py` matches by path AND content-hash (catches a rename) · arm fairness drift → `pin` required at load time for gsd/spec-kit, resolved to a real, dated, reproducible upstream reference (npm registry / GitHub release tag, confirmed via `npm view`/`gh api`) · WM3 must genuinely bait regressions → WM1's `duration_minutes` field is removed (not just renamed) and its oracle suite is re-run verbatim against the WM3 workspace.
Strategy actually used: as planned (batches 1→6, in order) — no deviation, except the RED-suite's own `test_oracles_red_on_empty_workspace` assertion was tightened mid-TESTS (a substring check on "error"/"errors" false-positived on urllib traceback text; replaced with an "errors during collection" / "failed" check) before any implementation existed, so it never weakened a post-green assertion.
Safety rule (feature-specific): oracle files never resolve inside an arm workspace — `check_isolation.py` fails closed (non-zero + loud "oracle_leak: <path>") on any path-or-hash match, and the check itself lives outside every `wm*/oracle/` directory so it cannot be the leak it's checking for.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `uv run --with pytest pytest benchmark/tests -v` -> 13 passed (local `pytest` binary absent from PATH; ran via `uv run --with pytest`, same pytest 9.1.1/py3.12 the build used)
- [x] coverage did not decrease — pre-build coverage was 0 (module didn't exist); post-build `benchmark/schema/run_record.py` 86% line coverage (target 90%, see 🟡 concern below); `check_isolation.py` is exercised only via `subprocess.run` in tests so line-coverage tooling reports it "never imported" — its behavior was instead confirmed by 5 live adversarial invocations (see Refute-read)
- [x] no test or contract was altered during build — `git log` on this branch shows §3 unchanged since freeze; the one test edit (`test_oracles_red_on_empty_workspace` substring tightened) happened mid-TESTS before any implementation existed, i.e. before the suite was ever green — judged legitimate, not a post-green weakening (see Refute-read)
- [x] the green was EARNED, not gamed — see Refute-read verdict below
- [x] concurrency / timing of the risky operation is safe — see Advisor lens 2
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor lens 1
- [x] layering & dependencies follow CONVENTIONS.md — see Advisor lens 3
- [ ] a person reviewed and approved the change — pending human gate (this verify pass is the AI-side evidence, not the human review)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `pytest benchmark/tests` prints 13 passed and, on the pre-build tree, printed failures/errors only from missing implementation — confirmed live: `uv run --with pytest pytest benchmark/tests -v` -> "13 passed in 7.37s"; build report's red-first log (collection/import errors on the greenfield tree) accepted as the pre-build evidence, not re-derived here (tree is now green, can't re-run red without reverting)
- [x] `python3 benchmark/check_isolation.py <dir-with-renamed-oracle-copy>` exits 1 printing `oracle_leak: <path>`; a clean dir exits 0 — confirmed live at the gate: renamed-copy dir -> exit 1 `oracle_leak: /tmp/adv_ws/renamed_leak.py`; clean dir -> exit 0 `clean: /tmp/adv_ws`
- [x] all 5 `benchmark/arms/*.toml` load via `load_arm` with an identical fairness triple, and gsd/spec-kit pins resolve to real upstream refs (`get-shit-done-cc@1.42.3`, `spec-kit@v0.12.5`) — confirmed by `test_five_arms_validate_with_fairness_parity` PASSED + direct read of `benchmark/arms/gsd.toml` (`pin = "get-shit-done-cc@1.42.3"`) and `spec-kit.toml` (`pin = "git+https://github.com/github/spec-kit.git@v0.12.5"`)
- [x] each `wm*/PROMPT.md` contains the verbatim `python -m app` / `$PORT` entry-contract line and WM3 removes WM1's `duration_minutes` shape — confirmed by reading all three prompts + `test_prompts_identical_contract_and_bait` PASSED (note: the WM3 bait assertion is an `or`-chain over loose keywords — see 🟡 concern)
- [x] `git status --porcelain` shows nothing for a probe file under `benchmark/runs/` — confirmed live: `benchmark/runs/probe.tmp` created, `git status --porcelain benchmark/runs` empty (`.gitignore:49` `benchmark/runs/`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `RunRecord`/`validate` imported+called by `benchmark/tests/test_run_record.py` and reused (`BenchError`) by `arms/loader.py`; `load_arm`/`Arm` imported+called by `test_arms.py`; `check_isolation.main` invoked via `subprocess.run([sys.executable, str(CHECK_ISOLATION), ...])` from `test_isolation.py`. No symbol is unreferenced (grep-confirmed each new public name resolves to a call site). `validate`/`load_arm` have no NON-test caller yet — expected: `bench-runner`/`bench-scoring` (downstream tasks) are the intended callers per MILESTONE.md's breadth-first decomposition, not dead code.
- [x] DEAD-CODE (code) — no orphaned symbol found; `_oracle_lib.py`'s `running_app`/`http_call` are unused by any oracle test in THIS task (`grep -rn "_oracle_lib" benchmark/workload/wm*/oracle/` -> no hits) — 🟡 concern, see below.
- [ ] SEMANTIC (prose / non-code) — n/a, code-path deep check applied above

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct Python import: `RunRecord`, `validate` (benchmark.schema.run_record), `load_arm` (benchmark.arms.loader), `check_isolation.main` (benchmark.check_isolation) all import cleanly; `benchmark/arms/<arm>.toml` (5 files), `benchmark/workload/wm{1,2,3}/PROMPT.md`, `benchmark/workload/wm{1,2,3}/oracle/test_*.py` all present on disk (`find benchmark -type f`)
- [x] no anchor moved/renamed since Ground SHA (0ff7d75) — greenfield task, every anchor was created fresh at its §3-cited path; nothing to reconcile

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (add-verify) · adversarially checked:
- `check_isolation.py` probed with: (1) renamed oracle copy at top level -> caught, exit 1; (2) renamed oracle copy nested 3 dirs deep -> caught, exit 1 (confirms `rglob` recursion, not a top-level-only shortcut); (3) a symlink pointing at an oracle file -> caught, exit 1 (content-hash follows the symlink's bytes); (4) a byte-edited copy (oracle content plus one appended comment line, new name) -> correctly exits 0 clean, proving the hash match is exact-content, not a fuzzy/near-miss detector giving false confidence; (5) a genuinely clean workspace -> exit 0. All 5 probes matched documented behavior; `find_leaks` walks the real filesystem with no fixture-only shortcut.
- `validate()` probed by reading (not just running) the two rejection tests: confirmed the exact-5-keys check (`metric_keys != set(REQUIRED_METRICS)`) rejects BOTH a missing key and an added key, not just the single case each test happens to exercise — traced by hand, not assumed.
- `load_arm` probed by reading the pin-required branch: the `PIN_REQUIRED_ARMS` gate keys off the recipe's declared `name` field (not its file path), so `test_unpinned_arm_rejected`'s tmp_path copy of `gsd.toml` genuinely exercises the same branch the real file would hit — not a fixture-only shortcut.
- Mid-TESTS tightening of `test_oracles_red_on_empty_workspace` (substring "error" -> explicit "errors during collection"/"failed" check): read the diff's intent — this is strictly narrower/more precise (the old check false-positived on urllib traceback text containing "error"), and it happened before any implementation existed (suite was still red) — this tightened an assertion pre-green, it did not weaken one post-green; consistent with the tdd-verifier rule.
- The `run_record.py` coverage gap (86%, defensive not-a-dict/non-int branches unexercised) is a real gap, not evidence of gaming — the required §2 scenarios are all covered by genuine, hand-traced logic, not stubs.
No vacuous asserts, no stubbed-away logic, no overfit-to-fixture pattern found.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self (add-verify)
1. Security: CLEAR — no secret/credential literals in any new file (grepped key/secret/password/token patterns: none); no shell-string execution, no dynamic-eval config loading anywhere in `benchmark/`; every subprocess call uses list-form argv (`[sys.executable, "-m", "app"]` / `[sys.executable, str(CHECK_ISOLATION), str(tmp_path)]`) — no shell interpolation surface; TOML parsed via stdlib `tomllib` (no arbitrary-code-on-parse risk); arm-recipe `setup_steps`/`prompt_wrapper` are stored as inert data in this task, not executed — execution is `bench-runner`'s job (out of this task's scope; flagged forward, not a finding here).
2. Concurrency: CLEAR — no shared mutable state across tests; `find_leaks` is a pure per-invocation read-only filesystem walk; `_oracle_lib.running_app` allocates an OS-assigned free port per call (avoids fixed-port races), bounds its startup poll to a 10s deadline, and terminates the subprocess in a `finally` (no orphan-process path found); every pytest test uses its own `tmp_path`, no cross-test fixture sharing.
3. Architecture: CLEAR, one recorded scope note (non-blocking) — `benchmark/pytest.ini` (registers the `regression` marker) was not named in §3/§4 but falls inside the declared §5 Scope token `benchmark/` (directory token = whole subtree per the §5 footnote); it exists only to support the contract's own `@pytest.mark.regression` tagging — judged in-scope, not creep. stdlib-first honored (tomllib, dataclasses, hashlib, urllib — no new third-party runtime dependency; pytest is existing dev/test tooling, not new runtime). Layering is clean: `schema/` has no dependency on `arms/`/`workload/`; `arms/loader.py` depends only on `schema/` (for `BenchError`); no circular imports.
Verdict: PASS
Residue: none blocking — 2 non-blocking 🟡 concerns recorded: (1) `run_record.py` line coverage 86% vs the 90% target, all misses are defensive/never-triggered validation branches; (2) `_oracle_lib.py`'s `running_app`/`http_call` are not yet called by any wm oracle test in this task (built ahead for the runner per the build's own strategy note) — confirm at `bench-runner` that they get wired, or fold as dead code there if they don't.
Binding: advisory — architecture/coverage sensitivity (no mechanical trigger; no security finding)

### GATE RECORD
Reported: yes — this verify pass rendered the evidence above (suite re-run, adversarial probes, symbol resolution, 3-lens review) before drafting an outcome
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a
Reviewed by: add-verify (independent agent) + orchestrator; residue (1) CLOSED before gating — defensive-branch tests added via tests→build re-cross, run_record.py coverage 86%→100% (20/20 green); residue (2) carried to bench-runner as a named check · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): oracle_leak rate at every bench-runner workspace teardown (check_isolation.py wired into the runner loop) · invalid_run_record / invalid_arm_recipe rejections during pilot runs (should be zero once the runner is correct) · the ⚠ startup-detection heuristic (poll-until-port-answers) against real arm-built apps at bench-runner

### Decisions (ADR)
- [AI] specify — chose static-assets-first; rejected runner-first (rejected: metrics/workload churn would thrash the runner contract) · one-big-task (rejected at intake: 4-task breadth-first)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (2026-07-07))
- [AI] build — approach: stdlib-first, fail-loud validation at every boundary (RunRecord/Arm loaders raise `BenchError` with the frozen error-code prefix rather than silently coercing) — mirrors the methodology-engine-dev discipline of pure validation functions + no silent partial writes, applied here to benchmark data shapes instead of the ADD engine itself.
- [AI] build — data strategy: 3 independent stdlib dataclass/TOML shapes (RunRecord, Arm, PROMPT.md+oracle files) with no shared DB — matches the §3 Schema line ("no DB — file shapes above are the schema").
- [AI] build — pattern: fixture-and-oracle pattern — a frozen prompt (fixture) + a harness-owned, arm-invisible oracle suite (test) per workload milestone, isolation enforced by a standalone loud checker; extends CLAUDE.md's red/green TDD discipline into the benchmark's own arm-scoring loop.
- [AI] build — optimization stance: correctness-first, no perf budget — this is pilot-scale (5 arms × 3 WMs × 1 rep), not a hot path. ⚠ least-trusted facet: the oracle HTTP-driving helper's startup-detection heuristic (poll-until-port-answers) — good enough for stdlib-only pilot scale but untested against a slow-starting real arm-built app; flagged for bench-runner to harden.
- [AI] build — strategy used: as planned (batches 1→6, in order) — no deviation, except the RED-suite's own `test_oracles_red_on_empty_workspace` assertion was tightened mid-TESTS (a substring check on "error"/"errors" false-positived on urllib traceback text; replaced with an "errors during collection" / "failed" check) before any implementation existed, so it never weakened a post-green assertion.
- [AI] verify — gate PASS (reviewed by add-verify (draft, pending human sign-off))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] the `add` arm's pin is a repo path (`add-method/`), not a version tag — bench-runner must resolve it to a reproducible ref (installed version or commit SHA) at execution time (evidence: benchmark/arms/add.toml pin field vs the gsd/spec-kit tag pins)
- [SPEC · open] `_oracle_lib.running_app`/`http_call` shipped uncalled in this task — bench-runner must wire them (its oracle-scoring path) or they fold as dead code (evidence: §6 DEAD-CODE check, grep shows no oracle/ caller)
- [SPEC · open] the WM3 regression-bait assertion in test_prompts_identical_contract_and_bait is a loose or-chain over keywords — tighten to an exact `duration_minutes`-removal assertion when bench-scoring defines regression_rate extraction (evidence: §6 Build-expectations note)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] a coverage-target miss disclosed at verify is closable cheaply via the sanctioned tests→build re-cross (add.py phase tests) instead of gating with residue — close-gap-before-gate held (evidence: run_record.py 86%→100%, commit "cover run_record defensive branches")
- [ADD · open] the engine's freeze-flag vocabulary is `[spec|scenario|contract|test]` — `[specify]` is rejected by unflagged_freeze; phase-guide names ≠ flag-tag names (evidence: two failed advance attempts before the tag fix)
- [SDD · open] benchmark fairness rules (identical prompts/model/ceilings, ceremony-in-budget) belong in MILESTONE.md shared decisions, not per-task — all 4 remaining tasks consume them unchanged (evidence: bench-scaffold TASK.md cites, never restates)

