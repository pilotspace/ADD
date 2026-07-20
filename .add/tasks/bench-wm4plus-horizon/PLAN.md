# TASK: WM4/WM5 horizon extension — prove or refute the ADD/spec-kit crossover

slug: bench-wm4plus-horizon · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): benchmark/workload/wm4,wm5 (PROMPT.md + oracle, mirroring wm1-3) · run.py/pilot.py/score.py VALID_WMS · run.py resume range · score.py wm==3 branches (priors + slope generalized to wm>=3; regression stays wm3-only) · benchmark/tests (new module)
Context (working folder): per-WM trajectories — add falls 12.85→3.2→2.1M, spec-kit rises 1.11→1.08→1.64M; crossover extrapolates to WM4-5. Judge + runner are already wm-generic (path-based); find_resume_point is cap-free. Post-WM3 shape: end_time (no duration_minutes) + WM2 auth binds all later WMs.
Honors (patterns · conventions): oracle style = running_app/http_call vs BENCH_WORKSPACE, never visible to the arm; frozen 5-metric semantics extend, never mutate (slope = OLS over wm1..wmk at scoring wm k>=3; regression_rate stays the wm3 refactor bait)
Anchors the contract cites: VALID_WMS · score_record wm>=3 priors loop · workload/wm4|wm5/oracle
Ground SHA: 5397c23

---

## 1 · SPECIFY — the rules

Feature: WM4/WM5 horizon extension
Must:
  - WM4 (feature growth): filtering (`status`, `from`/`to` window) + pagination (`limit`/`offset`) on GET /bookings, and POST /bookings/recurring (weekly ×N, each instance passing the WM2 overlap rule) — on the inherited WM3 app (end_time shape, auth)
  - WM5 (cross-cutting change): required `room_id`; the overlap rule becomes PER-ROOM ACROSS USERS (not per-owner); GET /rooms/{{id}}/schedule lists that room's bookings time-ordered; auth + WM4 features keep working
  - harness: VALID_WMS -> (1,2,3,4,5) in run.py/pilot.py/score.py; resume range follows; score_record at wm>=3 loads ALL priors and computes slope over the full trajectory + fidelity_trajectory/min artifacts; regression_rate real ONLY at wm3 (its bait), 0.0-by-definition elsewhere
Reject:
  - scoring wm k without prior records 1..k-1 -> missing_prior_wm_record (existing code, now general)
Accept: Given wm1-wm4 records with fidelities f1..f4, When wm4 is scored, Then slope = OLS over 4 points, fidelity_trajectory has 4 values, regression_rate == 0.0; Given the wm5 oracle census, Then >=5 tests exist per new WM.
Assumptions: ⚠ WM4/WM5 difficulty may not match WM1-3's scale (uncalibrated new prompts) — why: authored today, single rep; if wrong: crossover read gains noise (mitigate: compare per-WM trajectories, not absolutes)

---

## 3 · CONTRACT — freeze the shape

```
workload/wm4/PROMPT.md + oracle/test_growth.py   (filter · pagination · recurring)
workload/wm5/PROMPT.md + oracle/test_rooms.py    (room_id · per-room overlap · schedule)
VALID_WMS = (1, 2, 3, 4, 5)   # run.py · pilot.py · score.py
score_record(wm>=3): priors = wm1..wm(k-1); slope = OLS(full trajectory); regression real @wm3 only
frozen: metric names/count (5) unchanged; wm1-3 prompts/oracles byte-unchanged
```

`Least-sure flag surfaced at freeze:` [spec] WM5's per-room overlap supersedes WM2's per-owner rule — frozen as: per-room ACROSS users is the wm5 rule; wm2's own oracle is never re-run at wm5, so no contradiction; if wrong: wm5 oracle over-constrains (visible as uniform low fidelity)
Status: FROZEN @ v1 — approved by Tin Dang (instruction 2026-07-08: "run WM4+ horizon extension to prove the crossover")

---

## 4 · TESTS — failing-first (red)

Suite: benchmark/tests/test_wm4plus.py — 7 tests (wm4/wm5 prompt+oracle exist with >=5
oracle tests each · prompts restate entry contract + WM3 shape · wm1-3 byte-anchors
untouched · VALID_WMS == (1..5) across run/pilot/score · priors generalized to wm>=3 ·
4-point OLS slope). RED confirmed: wm4/wm5 missing + VALID_WMS still (1,2,3) —
red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/workload/` · `benchmark/run.py` · `benchmark/pilot.py` · `benchmark/score.py` · `benchmark/tests/` · `benchmark/runs/` · `benchmark/BENCHMARK.md` · `tmp/` · `.add/`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass — benchmark suite 117 green (7 new); 3 old-contract pins migrated FORWARD per the frozen §3 (invalid wm probe 4→6; resume counts 2→4; pilot seeds 5 WMs), recorded via re-cross
- [x] green was EARNED — oracle census asserted; slope checked on a 4-point linear decline; wm1-3 byte-anchors pinned untouched
- [x] no security surface — workload prompts/oracles + count constants

Build expectations (from §1 Accept + §3 CONTRACT): add resumes into wm4/wm5 seeded; spec-kit reruns wm1-5; both score with full-trajectory slope — confirmed by the horizon run's records.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08

