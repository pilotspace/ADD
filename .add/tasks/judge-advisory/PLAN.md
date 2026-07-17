# TASK: Demote the LLM judge to a source-aware, non-gating code_quality_annotation artifact

slug: judge-advisory · created: 2026-07-15 · stage: mvp
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
Feature: `code_quality_annotation` — the demoted LLM judge returns as a SOURCE-AWARE, NON-GATING advisory artifact (never a metric), replacing the `judge_scores` deferred sentinel.
Must:
  - M1: `score_record` writes `artifacts["code_quality_annotation"]` (a string) and NEVER adds it to `metrics` — the deterministic requirement_coverage stays the only fidelity signal.
  - M2: the annotation prompt is SOURCE-AWARE — it includes the BUILT app's source (the workspace's `app/` files), fixing the retired rubric's artifact-blindness (which read only PROMPT.md + oracle booleans, never the code).
  - M3: claude-less by default — when NO `judge_cmd` is configured (the deterministic re-score path), the annotation is `"unavailable: ..."` and NO LLM subprocess is spawned; scoring still succeeds.
  - M4: best-effort when a `judge_cmd` IS provided — the annotation is the judge's output; a judge failure yields `"unavailable: <reason>"`, never raises, never fails scoring.
Reject:
  - R1: `code_quality_annotation` as a `metrics` key -> `validate()` raises "invalid_run_record" (it is neither required nor optional) — pinned so it can never silently become a gating metric.
Accept: `score_record` with NO judge_cmd writes an `"unavailable"` `code_quality_annotation`, spawns zero `claude` subprocesses, and the record still validates with EXACTLY the v3 metric set; with a fake judge_cmd it writes that judge's annotation text.
Boundary: judge availability — `judge_cmd=None` (re-score, claude-less) vs an injected/real `judge_cmd` (live annotation); the built source is bounded (cap files/chars so the prompt can't blow up).
Assumptions: ⚠ bounding the source snapshot (cap the app/ files fed to the judge) is enough context for a useful annotation — if too tight, the annotation is shallow; cost: a weaker advisory note only, never a gate, so near-zero blast.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `benchmark/judge.py` — NEW `build_code_quality_prompt(wm, workspace) -> str`: the WM's `PROMPT.md` requirements + the BUILT app's source (`app/**/*.py` under the workspace), bounded by `_MAX_SOURCE_FILES`/`_MAX_SOURCE_CHARS`. NEW `code_quality_annotation(workspace, wm, *, judge_cmd=None) -> str`: claude-less by default (falsy `judge_cmd` → `"unavailable: ..."`, NO subprocess), best-effort otherwise (subprocess failure/empty → `"unavailable: <reason>"`, never raises). Sits beside `judge_fidelity`@59 (reuses `JUDGE_TIMEOUT_S`@19, `_prompt_path`@39). The retired-metric functions (`judge_fidelity`, `judge_fidelity_median`, `build_rubric_prompt`) stay untouched.
  - `benchmark/score.py:score_record`@347 — replace the `artifacts["judge_scores"] = "deferred: ..."` sentinel@416 with `artifacts["code_quality_annotation"] = judge.code_quality_annotation(workspace, wm, judge_cmd=judge_cmd)` (drop the `judge_scores` key). `judge` already imported@21; `judge_cmd` already a param@351; `workspace` already bound@403.
Context (working folder): `benchmark/` harness; archived `runs/<label>/wm<n>/workspace/app/*.py` is the source the annotation reads; `benchmark/schema/run_record.py` REQUIRED/OPTIONAL_METRICS is the metric-set floor R1 pins against.
Honors (patterns / conventions): `judge_fidelity`'s injectable-`judge_cmd` seam + stdlib-only/`cwd`-guard subprocess shape · the honest-fidelity-meter law "NO LLM in the metric path" (annotation is an `artifacts` string, never a `metrics` key) · fail-closed advisory (a judge problem degrades to `"unavailable"`, never a scorer crash — mirrors `compute_requirement_coverage`'s stance).
Anchors the contract cites: `code_quality_annotation`, `build_code_quality_prompt`, `score_record`, `JUDGE_TIMEOUT_S`, REQUIRED_METRICS/OPTIONAL_METRICS.
Ground SHA: 3c74457 — stamped by freeze

### Contract

```
build_code_quality_prompt(wm: int, workspace: str | pathlib.Path) -> str:
  - text = PROMPT.md(wm) requirements + the built app's source
    (sorted app/**/*.py, capped at _MAX_SOURCE_FILES files / _MAX_SOURCE_CHARS total),
    each chunk headed "# --- <relpath> ---"; "(no app source found)" when the glob is empty
  - closes asking for a SHORT advisory note (never a score) — source-aware, fixing the
    retired rubric's artifact-blindness

code_quality_annotation(workspace, wm, *, judge_cmd: Sequence[str] | None = None) -> str:
  - judge_cmd falsy  -> "unavailable: no judge configured (deterministic scoring)"; NO subprocess spawned
  - judge_cmd given  -> run [*judge_cmd, build_code_quality_prompt(wm, workspace)] (cwd=workspace if it exists,
                        capture_output, timeout=JUDGE_TIMEOUT_S); return stripped stdout
  - subprocess raises / empty stdout -> "unavailable: <reason>" (best-effort; NEVER raises, NEVER a score)

score_record(...):
  - artifacts["code_quality_annotation"] = code_quality_annotation(workspace, wm, judge_cmd=judge_cmd)
  - the "judge_scores" deferred sentinel is REMOVED; metrics dict is byte-for-byte the v3 set (unchanged)

R1: "code_quality_annotation" is NEITHER in REQUIRED_METRICS NOR OPTIONAL_METRICS ->
    a record placing it under metrics fails validate() with "invalid_run_record" (never gating)
```

`Least-sure flag surfaced at freeze:` [contract] the source glob is `app/**/*.py` — the `python -m app` entry contract means every arm's built code lives under `app/`, so this is the arm-agnostic source root; if some arm ever shipped its logic OUTSIDE `app/` the annotation would read an empty/partial tree and degrade to a shallow note — cost: a weaker advisory string only (never a gate, never a metric), so the blast is near-zero and caught by eye at the gate.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `benchmark/judge.py` `benchmark/score.py` `benchmark/tests/`
Strategy & known-problem fixes: 1. RED tests first (benchmark/tests/): (a) `code_quality_annotation(ws, wm, judge_cmd=None)` returns "unavailable…" AND spawns zero subprocesses (spy `judge.subprocess.run`); (b) with a fake failing `judge_cmd` → "unavailable: …", no raise; (c) with a fake echo `judge_cmd` → its stdout is the annotation; (d) `build_code_quality_prompt` includes a known app-source symbol (source-aware); (e) R1: "code_quality_annotation" ∉ REQUIRED∪OPTIONAL and a record with it under `metrics` fails `validate()`; (f) MIGRATE `test_score_record_defers_judge_out_of_metric_path` → assert `artifacts["code_quality_annotation"]` present & "unavailable"-prefixed with no `judge_cmd`, and `"judge_scores"` gone. 2. add the two functions to judge.py (module constants `_MAX_SOURCE_FILES=20`, `_MAX_SOURCE_CHARS=40_000`, glob `app/**/*.py` sorted+capped). 3. rewire score.py@416. Trap: the claude-less default MUST NOT fall through to `default_judge_cmd` (that would spawn the live `claude` during deterministic re-score) — only spawn when `judge_cmd` is truthy. Trap: `code_quality_annotation` never touches `metrics` — it writes `artifacts` only.
Approach (domain strategy): "opt-in source-aware advisory"

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
Strategy actually used: as planned — two new functions in `judge.py` (`build_code_quality_prompt` + `code_quality_annotation`) beside `judge_fidelity`, module bounds `_SOURCE_GLOB`/`_MAX_SOURCE_FILES`/`_MAX_SOURCE_CHARS`; `score.py`@416 sentinel replaced with the annotation call. Retired-metric judge functions untouched.
Code lives in: `benchmark/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — `benchmark/tests/` 203 passed (6 new in test_code_quality_annotation.py + 1 migrated in test_judge_median.py), 0 failed
- [x] green was EARNED — the 6 new tests were RED for the right reason (functions absent / `judge_scores` sentinel gone); the claude-less-default test spies `judge.subprocess.run` and asserts ZERO calls (not a stub) — real behavior, no overfit
- [x] input dialect held — annotation is a string in `artifacts`, R1 pins it out of `metrics` via the real `validate()` (extra-key rejection), not a mocked check
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — stdlib `subprocess` only, spawned ONLY when a caller supplies `judge_cmd` (never auto-spawns the live `claude`); no shell (argv list), `cwd`-guarded; prompt bounded (≤20 files / ≤40k chars)

Build expectations (from §1 Accept + §3 CONTRACT): on the REAL archived `runs/add/wm1/workspace` — `code_quality_annotation(ws, 1, judge_cmd=None)` == `"unavailable: no judge configured (deterministic scoring)"` (zero subprocesses); `build_code_quality_prompt(1, ws)` embeds the built app's real source files (`# --- app/store.py ---`, `app/cli.py`, …, 10327 chars, bounded); with a fake echo `judge_cmd` the annotation == that judge's stdout (`"clean, idiomatic, well-factored"`) — all three confirmed live.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate, autonomy: auto — evidence-complete; human spot-audit backstop) · date: 2026-07-15
OBSERVE: [SPEC · open] the judge is now a source-aware ADVISORY only — a future loop could surface `code_quality_annotation` in `report.py`'s per-record view (a non-metric column) so the qualitative note is visible alongside the deterministic numbers without ever gating on it.

