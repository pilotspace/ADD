# TASK: benchmark/ tree: workload spec, oracle suites, 5 arm definitions, run-record schema

slug: bench-scaffold · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto   <!-- level: manual < conservative < auto — lower for a high-risk task (`add.py autonomy set`). Multi-component repo? add a `component: <name>` line (.add/components.toml) to join that root to §5 Scope. -->
phase: tests   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + a lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

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

<!-- EXIT: every rule + rejection stated; assumptions ranked lowest-confidence first, top 1–2 ⚠-flagged with why + cost (or an honest "none material" naming the biggest risk). -->

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

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

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
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen contract = change request back to SPECIFY. EXIT: frozen · every §1 rejection has a contracted response · names match GLOSSARY (new terms = Glossary delta) · flag surfaced. -->

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
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

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

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token with "/" = project root · a bare name = sibling of the previous token's dir · a DIRECTORY token covers its whole subtree (diverges from §4's non-recursive counting) · outside-root resolutions drop fail-closed · absent line = UNDECLARED (grandfathered, never retro-red) · enforcement live: a completing verify gate refuses an out-of-scope build (scope_violation → self-heal); check surfaces it. EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>
- [ ] <another observable outcome> — confirmed by <evidence seen>

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [ ] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by <how / where>
- [ ] any anchor that moved/renamed since Ground SHA is named here, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: <agent-id | self>
1. Security: <CLEAR | HARD-STOP: finding>
2. Concurrency: <CLEAR | RESIDUE: finding>
3. Architecture: <CLEAR | RESIDUE: finding>
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- Security is ALWAYS HARD-STOP; record exactly one outcome — no silent pass. The Advisor 3-lens and Refute-read verdicts are audit-measured (`advisor_verdict_unrecorded` · `refute_unrecorded`), never engine-blocked; a human spot-audit backstops anything unrecorded. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
