# TASK: Emit a per-WM coverage_detail artifact — which checklist requirement each WM covered (non-gating)

slug: coverage-detail · created: 2026-07-15 · stage: mvp
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
Feature: `coverage_detail` — score_record emits a per-WM artifact recording which frozen checklist requirement the built app covered (id + covered bool), so every `requirement_coverage` score is self-explaining. Non-gating (an `artifacts` string, never a metric).
Must:
  - M1: `score_record` writes `artifacts["coverage_detail"]` — a JSON string encoding one `{"id","covered"}` row per checklist requirement, in checklist order, for the WM being scored.
  - M2: the detail AGREES with the aggregate by construction — `requirement_coverage == (#covered / #rows)` from the SAME hermetic boot (one boot, not two; the float is derived from the detail, so they can never disagree).
  - M3: on an unbootable app the detail is still emitted with EVERY row `covered:false` (and coverage 0.0) — this is the whole point: a 0.0 becomes self-explaining (which requirements failed / that nothing booted), fixing the re-score blindness.
  - M4: `coverage_detail` NEVER enters `metrics` — it stays an `artifacts` string (mirrors the `code_quality_annotation` non-gating law); the frozen v3 metric set is byte-for-byte unchanged.
Reject:
  - R1: `coverage_detail` as a `metrics` key -> `validate()` raises "invalid_run_record" (neither required nor optional) — pinned so the diagnostic can never silently become a gating metric.
  - R2: a checklist whose rows lack a stable `id` -> "invalid_checklist" (the detail must key on `id`; enforced by the existing `validate_checklist` guard, extended if needed).
Accept: scoring a workspace that covers 4 of wm2's 5 rows writes `artifacts["coverage_detail"]` = 5 `{"id","covered"}` rows with exactly the uncovered requirement flagged `covered:false`, AND `metrics["requirement_coverage"] == 0.8` (detail and float agree).
Boundary: bootable app (mixed covered true/false) vs unbootable app (every row `covered:false`, coverage 0.0) — the detail is emitted in BOTH, so a 0.0 is never mute.
Assumptions: ⚠ every frozen checklist row already carries a stable `id` (verified: wm1-6 all have `id`,`description`,`probe`) — if a future checklist row omits `id`, R2 fails loud; cost: that WM's detail can't be keyed, caught at score-time, never silently wrong.

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols):
  - `benchmark/score.py:compute_requirement_coverage`@187 — REFACTOR: extract the hermetic boot + per-row probe loop into NEW `compute_coverage_detail(workspace, wm, family) -> list[dict]` (returns `[{"id","covered"}]` in checklist order; fail-closed → all `covered:False` on an unbootable app). `compute_requirement_coverage` becomes `_coverage_from_detail(compute_coverage_detail(...))` — signature + returned float UNCHANGED (behavior-preserving).
  - `benchmark/score.py` — NEW `_coverage_from_detail(detail) -> float` = `#covered/#rows` with the existing R3 `invalid_coverage` guard (single source of truth, used by both `compute_requirement_coverage` and `score_record`).
  - `benchmark/score.py:score_record`@347 — after coverage, call `compute_coverage_detail` ONCE (single boot), derive `requirement_coverage = _coverage_from_detail(detail)`, and set `artifacts["coverage_detail"] = json.dumps(detail, separators=(",",":"))`. `json` already imported@13.
Context (working folder): `benchmark/` harness; the frozen `workload/{wm}/checklist.py` REQUIREMENTS rows (each carries `id`,`description`,`probe`) are the detail's key source; `schema/run_record.py` REQUIRED/OPTIONAL_METRICS is the floor R1 pins against.
Honors (patterns / conventions): the hermetic `isolated_workspace`+`running_app` boot (reused, not re-added) · fail-closed coverage (unbootable → 0.0, never a crash) · the non-gating law (diagnostic lives in `artifacts`, never `metrics` — mirrors `code_quality_annotation`) · artifacts are string-valued (store the detail as a compact JSON string).
Anchors the contract cites: `compute_coverage_detail`, `_coverage_from_detail`, `compute_requirement_coverage`, `score_record`, `validate_checklist`, REQUIRED_METRICS/OPTIONAL_METRICS.
Ground SHA: 7e3712f — stamped by freeze

### Contract

```
compute_coverage_detail(workspace: str|pathlib.Path, wm: int, family: str = "wm") -> list[dict]:
  - boots ONE hermetic store-reset copy (isolated_workspace + running_app), runs each
    frozen checklist row's probe, returns [{"id": row["id"], "covered": bool}, ...] in
    checklist order
  - fail-closed: unbootable app / raising probe -> that row covered=False (never raises for a probe)
  - malformed checklist (row missing id/description/probe) -> "invalid_checklist" (R2, via validate_checklist)

_coverage_from_detail(detail: list[dict]) -> float:
  - #covered / #rows; value ∉ [0,1] -> "invalid_coverage" (R3)

compute_requirement_coverage(workspace, wm, family) -> float:   # UNCHANGED signature/behavior
  - == _coverage_from_detail(compute_coverage_detail(workspace, wm, family))

score_record(...):
  - detail = compute_coverage_detail(workspace, wm, family)   # single boot
  - metrics["requirement_coverage"] = _coverage_from_detail(detail)   # v3 set byte-unchanged
  - artifacts["coverage_detail"] = json.dumps(detail, separators=(",",":"))   # non-gating

R1: "coverage_detail" ∉ REQUIRED_METRICS ∪ OPTIONAL_METRICS -> a record placing it under
    metrics fails validate() with "invalid_run_record" (never gating)
```

`Least-sure flag surfaced at freeze:` [contract] the detail rows carry only `{id, covered}` (not `description`) — keeps the artifact lean and matches the confirmed shape, but a report renderer must re-import the checklist to show human text; if that's friction, `description` can be added later (additive, non-breaking) — cost: a follow-up field add, never a re-score.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `benchmark/score.py` `benchmark/tests/`
Strategy & known-problem fixes: 1. RED tests first (benchmark/tests/): (a) M1/M2 — score a workspace, assert `artifacts["coverage_detail"]` is JSON with one `{id,covered}` per row AND `#covered/#rows == requirement_coverage`; (b) M3 — an unbootable/empty workspace → detail with every row `covered:false` + coverage 0.0 (detail still present); (c) R1 — `coverage_detail` ∉ REQUIRED∪OPTIONAL and a record with it under `metrics` fails `validate()`; (d) `compute_requirement_coverage` float is UNCHANGED vs the pre-refactor value on a known workspace (behavior-preserving pin). 2. extract `compute_coverage_detail` + `_coverage_from_detail`, rewire `compute_requirement_coverage`. 3. wire `score_record`'s single-boot detail + artifact. Trap: do NOT boot twice in score_record (derive coverage from the one detail call, don't also call `compute_requirement_coverage`). Trap: `coverage_detail` is an `artifacts` string only — never a metric.
Approach (domain strategy): "derive-both-from-one-boot"

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
Strategy actually used: as planned — extracted `compute_coverage_detail` (per-row {id,covered}, one hermetic boot, fail-closed all-False) + `_coverage_from_detail` (R3 guard); rewired `compute_requirement_coverage` to derive from them; `score_record` single-boot detail → `artifacts["coverage_detail"]` (compact JSON). Divergence: 5 pre-existing tests monkeypatched the old `compute_requirement_coverage` seam that `score_record` no longer calls directly — forward-migrated them to seed `compute_coverage_detail` (same assertions, new wiring), re-crossed to re-baseline the tamper snapshot.
Code lives in: `benchmark/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — `benchmark/tests/` 210 passed (6 new in test_coverage_detail.py + 5 forward-migrated seams), 0 failed; frozen contract untouched
- [x] green was EARNED — the 4 detail tests were RED (functions absent); the 2 invariant pins (R1/R2 already-guaranteed) documented the non-gating law; migrations preserved every behavioral assertion (0.5/0.6/1.0/slope), only the mock seam moved
- [x] input dialect held — detail keys on the frozen checklist `id`s (R-*); the artifact is a compact JSON string matching the artifacts-are-strings convention
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — stdlib `json` only; reuses the existing hermetic boot; no new IO, no shell, no user input

Build expectations (from §1 Accept + §3 CONTRACT): on the REAL archived `gsd-v2meter-r0/wm2` (the one sub-1.0 arm) `compute_coverage_detail(ws,2)` names the single uncovered requirement — `R-cancellation-window-422` `covered:false`, other 4 `true` — and `_coverage_from_detail == compute_requirement_coverage == 0.8`; on `spec-kit-preexisting/wm2` (401 auth-drift) the detail shows exactly which 4 of 5 failed → coverage 0.2 (a formerly-mute 0.2 is now self-explaining). Confirmed live.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate, autonomy: auto — evidence-complete; human spot-audit backstop) · date: 2026-07-15
OBSERVE: [SPEC · open] coverage_detail makes the wm2-6 granularity delta actionable — a report column showing per-requirement covered/uncovered now lets the "coverage 1.0 but oracle<1.0" gaps be pinpointed to a specific requirement id; the natural next step is surfacing coverage_detail (+ code_quality_annotation) in report.py's per-record view.

