# TASK: Hermetic scoring — isolate the app store per boot so coverage/oracle are reproducible on archived builds

slug: hermetic-scoring · created: 2026-07-15 · stage: mvp
milestone: honest-fidelity-meter
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: Hermetic scoring — coverage / oracle / regression boot the app in an ISOLATED copy of the workspace with the persistent store RESET, so scores are reproducible on archived builds and scoring never mutates the source workspace.
Must:
  - M1: `compute_requirement_coverage` boots the app in an isolated copy of the workspace, not the source; scoring never modifies the source workspace's store file.
  - M2: coverage is REPRODUCIBLE — scoring the same archived workspace repeatedly yields the identical value even though probes create bookings (the store no longer accumulates across scorings; each boot starts reset).
  - M3: the oracle + regression pytest paths (`_run_oracle_suites`) run against the same isolated, store-reset copy (`BENCH_WORKSPACE` points at the temp copy), so oracle_pass_rate is reproducible too.
  - M4: the isolation copy EXCLUDES heavy/irrelevant dirs (`.venv`, `.git`, `__pycache__`, `node_modules`, `.add`) — the stdlib entry contract (`python -m app`) means the app boots without them.
Reject:
  - R1: a source workspace that does not exist / cannot be copied -> the app cannot boot from the (empty) isolated dir -> coverage 0.0, oracle 0.0 (fail-closed, never a scorer crash) -> "" (no new error code; preserves coverage-scorer M3).
Accept: scoring `add-v2meter-r0/wm2` twice in a row yields the identical `requirement_coverage`, AND the source workspace's `bookings.json` is byte-unchanged after scoring.
Boundary: the store filename VARIES per arm (`bookings.json` for add/gsd · `bookings_data.json` for spec-kit) — reset by clearing root-level `*.json` in the copy, never a hardcoded name.
Assumptions: ⚠ the app's persistent store is a root-level `*.json` file (the booking-store convention holds for every arm) — if an arm persisted to a subdir or a non-`.json` file, the reset misses it and that arm stays non-hermetic; cost: that arm's wm2+ re-score still drifts, caught per-arm by the reproducibility test.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `benchmark/workload/_oracle_lib.py` — NEW `isolated_workspace(workspace) -> contextmanager[pathlib.Path]`: `shutil.copytree` src→temp with an `ignore` for the heavy dirs, `unlink` every root-level `*.json` in the copy, `yield` the temp Path, remove it on exit; the source is never written. Sits beside `running_app`@32 (same module the probes already import).
  - `benchmark/score.py:compute_requirement_coverage`@187 — wrap the `running_app(str(workspace))`@204 boot in `with isolated_workspace(workspace) as ws:` so probes hit the reset copy.
  - `benchmark/score.py:_run_oracle_suites`@85 — copy to an isolated workspace and set `env["BENCH_WORKSPACE"]`@109 to the temp copy, so the oracle + regression pytest probes (which read BENCH_WORKSPACE and call `running_app`) boot the reset copy too.
Context (working folder): `benchmark/` harness; the archived `runs/<label>/wm<n>/workspace/*.json` stores are the contamination source the isolation neutralizes.
Honors (patterns / conventions): `compute_oracle_pass_rate`'s fail-closed stance (unbootable → 0.0, never a crash) · the stdlib `python -m app` entry contract (no venv needed at boot, so the copy omits it) · NO LLM in the metric path.
Anchors the contract cites: `isolated_workspace` (new), `compute_requirement_coverage`, `_run_oracle_suites`, `running_app`.
Ground SHA: d8b86c2 — stamped by freeze

### Contract

```
isolated_workspace(workspace: str | pathlib.Path) -> ContextManager[pathlib.Path]:
  - copytree(workspace -> a fresh temp dir), IGNORING {.venv, .git, __pycache__, node_modules, .add}
  - unlink every root-level *.json in the copy (the app's persistent store, name-agnostic)
  - yield the temp dir Path; remove it on __exit__
  - the SOURCE workspace is NEVER modified (no writes, no store mutation)
  - source missing/uncopyable -> yield a temp dir the app cannot boot from (fail-closed, no raise)

compute_requirement_coverage(workspace, wm, family):
  boots running_app on the ISOLATED copy (probes' bookings land in the throwaway copy)

_run_oracle_suites(workspace, oracle_paths, ...):
  runs pytest with BENCH_WORKSPACE = the ISOLATED copy

Property (M2/M3): score(ws) == score(ws) across repeated calls (store reset each boot);
                  ws's root *.json store is byte-identical before and after any scoring.
```

`Least-sure flag surfaced at freeze:` [contract] the store-reset = "unlink root-level `*.json` in the copy" — if any arm persisted its store in a subdirectory or a non-`.json` file, the reset misses it and that arm stays non-hermetic; cost: its wm2+ re-score still drifts (caught per-arm by the reproducibility test, so it fails loud, never silently wrong).
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `benchmark/score.py` `benchmark/workload/_oracle_lib.py` `benchmark/tests/`
Strategy & known-problem fixes: 1. add `isolated_workspace` to `_oracle_lib.py` (copytree with `ignore_patterns` for the heavy dirs · unlink root `*.json` · `tempfile.mkdtemp` + `try/finally shutil.rmtree`). 2. wrap `compute_requirement_coverage`'s boot. 3. `_run_oracle_suites`: isolate + repoint BENCH_WORKSPACE. Trap: copytree must NOT follow into `.venv` (huge/slow) — ignore it; and rmtree the temp even when a probe raises (finally). 4. red tests: reproducibility (same ws twice → identical), source-store-byte-unchanged, copy-excludes-.venv.
Approach (domain strategy): "copy-to-temp store-reset boot"

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — `isolated_workspace` in `_oracle_lib.py` (copytree with `ignore_patterns` + root `*.json` unlink + `mkdtemp`/`finally rmtree`); wrapped `compute_requirement_coverage`'s boot and repointed `_run_oracle_suites`'s `BENCH_WORKSPACE` at the copy.
Code lives in: `benchmark/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — `benchmark/tests/` 196 passed (4 new hermetic tests), 0 failed
- [x] green was EARNED — the 3 isolation tests were RED for the right reason (source store MUTATED / `isolated_workspace` missing); the fix is the minimal copy-reset-boot, no fixture overfit
- [x] input dialect held — the store reset is name-agnostic (root `*.json`), covering both observed store dialects (`bookings.json` · `bookings_data.json`)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — stdlib only (`shutil`/`tempfile`); copies a local trusted tree; no shell, no user input

Build expectations (from §1 Accept + §3 CONTRACT): scoring the REAL archived `add-v2meter-r0/wm2` workspace three times yields identical `requirement_coverage` (1.0 × 3, was drifting 0.8→0.4 under store contamination) AND the source `bookings.json` md5 is byte-unchanged (af6e3f4a… → af6e3f4a…) — confirmed live.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate, autonomy: auto — evidence-complete; human spot-audit backstop) · date: 2026-07-15
OBSERVE: [SPEC · open] hermeticity revealed the wm2+ arms are MORE conformant than the contaminated re-scores showed (add-v2meter-r0 wm2: 0.4 polluted → 1.0 clean) — the trustworthy cross-arm progression can now be produced; a still-open follow-up is tightening the wm2–wm6 checklist granularity where coverage 1.0 but oracle < 1.0.

