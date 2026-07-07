# TASK: Split WM3 regression suite: must-survive vs legacy-shape (by-construction) tests

slug: bench-regression-split · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/workload/wm3/oracle/test_refactor.py` (10 re-exported wm1+wm2 tests all tagged `regression`) — 7 of them create bookings with `duration_minutes`, which WM3\'s own frozen contract REQUIRES rejecting with 400, so they fail for every arm by construction; observed floor: regression_rate 0.8–0.9 across all passing arms
Context (working folder): round-3 records — vanilla/spec-kit 0.8, add/gsd 0.9, plan-mode 1.0; the metric currently measures the workload\'s trap, not the arm\'s carefulness
Honors (patterns / conventions): compute_regression_rate stays `-m regression` (no scoring-code change — this is a workload change-request, marker-level only); wm1/wm2 oracle files untouched
Anchors the contract cites: the 10 re-export names in test_refactor.py; markers `regression` (must-survive) and `legacy_shape` (by-construction)
Ground SHA: (post bench-judge-median gate on feat/add-bench-scaffold)

---

## 1 · SPECIFY — the rules

Feature: regression marker split — count only shape-independent behaviors
Must:
  - Must-survive (keep `regression` marker): wm1_missing_required_field_rejected · wm1_unknown_booking_is_404 · wm2_unauthenticated_request_rejected — behaviors independent of the duration_minutes→end_time shape change.
  - Legacy-shape (re-tag `legacy_shape`): the other 7 re-exports (create/list/update-delete, double-booking, ownership, cancellation, list-scoped) — their payloads use `duration_minutes`, doomed by WM3\'s contract.
Reject:
  - a re-export carrying BOTH markers, or carrying neither -> guard test fails ("marker_census_violation")
Accept: Given the split, When `pytest -m regression --collect-only` runs on test_refactor.py, Then exactly 3 tests collect (the must-survive set) And `-m legacy_shape` collects exactly 7.
Assumptions: ⚠ the 3 must-survive behaviors are truly shape-independent — 404/401/missing-field probes don\'t send duration_minutes payloads that WM3 rejects; verified by reading the oracle sources (missing-field posts an incomplete payload; 404/401 need no body); if wrong: rate skews, caught at rescore review.

---

## 3 · CONTRACT — freeze the shape

```
test_refactor.py re-export tagging:
  pytest.mark.regression   -> {wm1_missing_required_field_rejected, wm1_unknown_booking_is_404, wm2_unauthenticated_request_rejected}
  pytest.mark.legacy_shape -> the remaining 7 re-exports (unchanged callables, marker swap only)
compute_regression_rate: UNCHANGED (`-m regression` now selects exactly the 3 must-survive tests)
guard: benchmark/tests/test_regression_split.py asserts the 3/7 census via --collect-only
```

`Least-sure flag surfaced at freeze:` [spec] whether wm1_missing_required_field\'s incomplete payload accidentally includes duration_minutes (making it legacy-shape too) — read before tagging; if wrong: move it to legacy_shape, census becomes 2/8, cost one retag.
Status: FROZEN @ v1 — approved by Tin Dang (intake confirmed in-session, "yes, intake A1+A2 as fast tasks").

---

## 4 · TESTS — failing-first (red)

Plan: `benchmark/tests/test_regression_split.py` — test_must_survive_census (collect-only `-m regression` on test_refactor.py == exactly the 3 names) · test_legacy_shape_census (`-m legacy_shape` == exactly 7) · test_no_double_or_missing_markers.
Tests live in: `benchmark/tests/` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/workload/wm3/oracle/test_refactor.py` · `benchmark/tests/test_regression_split.py`
Strategy & known-problem fixes: marker swap on the existing decorator-application lines only (trap: the callables are shared imports from wm1/wm2 — mark the re-exported NAMES, never mutate the source modules\' functions in place... they already are wrapped via pytest.mark call-form which returns a marked copy? pytest.mark applied to a function attaches to that object — shared! Apply MarkDecorator to create distinct wrappers is unnecessary: wm1/wm2 suites run in their own files without -m filters, so an attached marker is harmless there. Document this.)
Approach (domain strategy): obvious, correctness-first — retag + census guard.
Strategy actually used: as planned.
Code lives in: `benchmark/workload/` · Constraints: change no scoring code, no frozen wm1/wm2 oracle bodies.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (94/94 incl. 3 census + 1 must-survive-failure) · sibling test_score.py expectation migrated via re-cross (doc-truth ripple), not weakened
- [x] green was EARNED — census asserted via real pytest --collect-only; >0 rate path re-covered with a broken-401 fixture
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `-m regression` collects exactly 3 must-survive tests, `-m legacy_shape` exactly 7 — confirmed by the census guard tests + full suite green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07
