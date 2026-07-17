# TASK: Median-of-3 judging + persist raw judge outputs

slug: bench-judge-median · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/judge.py:judge_fidelity` (single-call; observed ±0.05–0.10 spread across identical calls in the post-pilot sweep) · `benchmark/score.py:score_record` (M3 seam: `spec_fidelity` recomputed via the injectable judge) — raw judge stdout is currently discarded, so a recorded score cannot be audited
Context (working folder): pilot round-3 evidence — add wm2 recorded 0.85 from one call whose reruns gave 0.95/0.97/0.95; variance swamps arm-vs-arm gaps
Honors (patterns / conventions): injectable `judge_cmd` argv seam preserved verbatim (tests inject fake judges); fail-loud BenchError codes; write_record_atomic single writer
Anchors the contract cites: `judge_fidelity` (unchanged single call) · `judge_fidelity_median` (new) · `score_record`
Ground SHA: (post pilot-cwd-hardening commit on feat/add-bench-scaffold)

---

## 1 · SPECIFY — the rules

Feature: median-of-N judge scoring with auditable raw outputs
Must:
  - New `judge_fidelity_median(workspace, wm, oracle_report, *, judge_cmd=None, n=3)` runs `judge_fidelity` up to n times, tolerates individual call failures, and returns `(median, scores)` where scores is the list of successful floats.
  - `score_record` uses `judge_fidelity_median` and persists `artifacts["judge_scores"] = ";".join(str(s) for s in scores)` so every recorded fidelity is auditable.
Reject:
  - fewer than 2 successful judge calls out of n -> BenchError("unparseable_judge_output: only <k>/<n> judge calls succeeded")
Accept: Given a fake judge argv that emits 0.9, 0.5, 0.9 across three calls, When score_record runs, Then metrics.spec_fidelity == 0.9 (median) And artifacts.judge_scores == "0.9;0.5;0.9".
Assumptions: ⚠ ~3× judge cost per score is acceptable — judge calls are pennies vs agent runs; if wrong: n is a parameter, dial to 1.

---

## 3 · CONTRACT — freeze the shape

```
judge.judge_fidelity_median(workspace, wm, oracle_report, *, judge_cmd=None, n=3) -> tuple[float, list[float]]
    runs judge_fidelity n times; each BenchError is caught and counted;
    < 2 successes -> raise BenchError("unparseable_judge_output: only {k}/{n} judge calls succeeded; last: {err}")
    median = statistics.median(scores)
score_record: spec_fidelity, scores = judge_fidelity_median(...); artifacts["judge_scores"] = ";".join(map(str, scores))
judge_fidelity itself: UNCHANGED (single-call primitive stays the tested seam)
```

`Least-sure flag surfaced at freeze:` [test] fake-judge-with-state — a stateless injected argv emits the same float every call, so the median test needs a fake judge that varies per call (a script counting its own invocations via a file); if wrong: test rewrite, small cost.
Status: FROZEN @ v1 — approved by Tin Dang (intake confirmed in-session, "yes, intake A1+A2 as fast tasks").

---

## 4 · TESTS — failing-first (red)

Plan: `benchmark/tests/test_judge_median.py` — test_median_of_three_varying_scores (stateful fake judge emits 0.9/0.5/0.9; median 0.9 + scores persisted) · test_tolerates_one_failed_call (fake judge errs once, succeeds twice → median of 2) · test_two_failures_raise (1/3 success → BenchError) · test_score_record_persists_judge_scores (artifacts["judge_scores"]).
Tests live in: `benchmark/tests/` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/judge.py` · `benchmark/score.py` · `benchmark/tests/test_judge_median.py`
Strategy & known-problem fixes: statistics.median over successful floats (trap: median of 2 = mean — acceptable, document) · catch ONLY BenchError per call, let unexpected exceptions crash loud · artifacts write stays inside score_record's single validate-then-write path.
Approach (domain strategy): obvious, correctness-first.
Strategy actually used: as planned.
Code lives in: `benchmark/` · Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (90/90 incl. 4 new) · coverage held · no test or contract altered during build
- [x] green was EARNED — stateful fake judge varies per call; median/tolerance/raise all asserted on behavior
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): median lands in spec_fidelity, all successful raw scores persisted in artifacts.judge_scores, <2 successes raises — confirmed by the 4 new tests + full benchmark suite green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07
