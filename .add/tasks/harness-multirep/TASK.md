# TASK: Controlled multi-rep: run N same-session reps per arm×wm and aggregate mean/range (trustworthy comparison)

slug: harness-multirep · created: 2026-07-09 · stage: mvp
milestone: three-phase-flow
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/pilot.py:run_pilot` — runs arms×wms ONCE into `runs_root`; today no multi-rep entry, so single-rep variance (spec-kit WM1 ranged $1.33–$4.00, 3×) is unquantified. · `benchmark/schema/run_record.py:RunRecord` — has `.metrics` (spec_fidelity/tokens_total/cost_usd) + `.arm`/`.wm`/`.rep`. · `benchmark/tests/test_pilot.py` — pilot tests inject a fake `agent_cmd` (no real `claude` spend) — the pattern the new tests mirror.
Context (working folder): `benchmark/THREE-PHASE-FLOW-PROOF.md` (harness problem #4, single-rep variance). My ad-hoc `firm_wm1.py` already ran rep-indexed roots by hand — this formalizes it into the harness.
Honors (patterns / conventions): `run_pilot(..., runs_root=)` already isolates a run tree; N reps = N calls into `runs_root/rep{i}`. Aggregation is a PURE function over records (group by arm×wm) — unit-tested on synthetic records, no run needed.
Anchors the contract cites: `run_pilot`, `RunRecord.metrics`.
Ground SHA: 2d9d238

---

## 1 · SPECIFY — the rules

Feature: the harness runs N controlled same-session reps per arm×wm and aggregates the distribution, so a comparison reports mean/range not a single noisy point.
Must:
  - `aggregate_reps(records)` groups records by (arm, wm) and returns, per group, `n` and `{mean, min, max}` for each of `tokens_total`, `cost_usd`, `spec_fidelity`.
  - `run_reps(arms, wms, reps, *, runs_root, repo_root, ...)` calls `run_pilot` once per rep into a DISTINCT `runs_root/rep{i}` (i in 0..reps-1) and returns the flat list of all records.
  - the `run-all` CLI gains `--reps N` (default 1); N>1 routes through `run_reps`, N==1 is the unchanged single-rep path.
Reject:
  - `reps < 1` -> BenchError("invalid_reps: must be >= 1").
Accept: `aggregate_reps([r_add_wm1_a, r_add_wm1_b, r_sk_wm1])` returns `{("add",1): {"n":2, "tokens":{...}, "cost":{...}, "fidelity":{...}}, ("spec-kit",1): {"n":1, ...}}` with correct mean/min/max; `run_reps(reps=3,...)` invokes `run_pilot` 3× with rep0/rep1/rep2 roots (proven by a spy — no real claude).
Assumptions: ⚠ that grouping by (arm, wm) — ignoring the RunRecord.rep field (always 0 today) — is sufficient, since each rep is a separate run_pilot into a separate root so same-(arm,wm) records across reps are distinct objects; if wrong (need per-rep identity), tag rep=i at write time — but aggregation only needs the group stats, so low-risk.   (or "none material — biggest risk: X")

---

## 3 · CONTRACT — freeze the shape

```
# benchmark/pilot.py
aggregate_reps(records: list[RunRecord]) -> dict[tuple[str,int], dict]
  # per (arm, wm): {"n": int,
  #                 "tokens":   {"mean": float, "min": float, "max": float},
  #                 "cost":     {"mean": float, "min": float, "max": float},
  #                 "fidelity": {"mean": float, "min": float, "max": float}}
  # PURE — no IO. Empty input -> {}.

run_reps(arms, wms, reps: int, *, runs_root, repo_root,
         agent_cmd=None, judge_cmd=None, timeout_s=1800.0, retries=1
        ) -> list[RunRecord]
  # reps < 1 -> raise BenchError("invalid_reps: must be >= 1")
  # for i in range(reps): run_pilot(arms, wms, resume=False,
  #     runs_root=Path(runs_root)/f"rep{i}", repo_root=repo_root, ...)
  # returns the concatenated records across all reps.

# CLI: run-all --reps N (default 1); N==1 unchanged; N>1 -> run_reps + print
#      aggregate_reps summary.
```

`Least-sure flag surfaced at freeze:` [contract] mean/min/max over `spec_fidelity` is a weak central-tendency for a bounded 0–1 judge score, but n is small and the range is the honest signal; reporting all three (not just mean) surfaces spread, so a misleading mean can't hide.
Status: FROZEN @ v1 — approved by Tin Dang

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §0 GROUND anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 CONTRACT shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/pilot.py` `benchmark/tests/test_pilot.py`
Strategy & known-problem fixes: (1) `aggregate_reps` as a PURE group-by over `record.arm`/`record.wm` → per-metric mean/min/max — no IO, unit-tested on synthetic validated records; dodges the "aggregation needs a live run" trap. (2) `run_reps` composes the already-frozen `run_pilot` `reps` times into `runs_root/rep{i}` with `resume=False` (each rep an independent fresh sample) — reuses the isolated run tree, never reimplements orchestration; reps<1 fails loud BEFORE any run. (3) `--reps N` routes N>1 through `run_reps` + prints the aggregate summary; N==1 keeps the exact prior single-rep path untouched.
Approach (domain strategy): compose-not-reimplement — pure reducer over RunRecord.metrics + a thin rep-loop over the frozen run_pilot seam; report the full distribution (min/max), not just the mean.
Strategy actually used: as planned — added `aggregate_reps` (pure reducer, `_REP_METRICS` mapping) + `run_reps` (rep-loop into `rep{i}` roots, resume off, BenchError on reps<1) + `--reps` CLI flag routing N>1 to run_reps and printing the per-(arm,wm) mean/min/max summary; N==1 path byte-unchanged. Only benchmark/pilot.py + benchmark/tests/test_pilot.py touched.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (132/132 benchmark/tests) · coverage held · no test or contract altered during build
- [x] green was EARNED — 5 new tests ran RED (missing `aggregate_reps`/`run_reps`) before the pilot.py edit; asserts check observable behavior (group stats, distinct rep{i} roots, resume=False, BenchError on reps<1, CLI routing), not internals
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — pure reducer + a rep-loop composing the already-frozen run_pilot; no new IO/network/eval, stdlib-only, allow-list untouched

Build expectations (from §1 Accept + §3 CONTRACT): `aggregate_reps` groups by (arm,wm) returning n + mean/min/max for tokens/cost/fidelity (empty→{}); `run_reps(reps=3)` calls run_pilot 3× into rep0/rep1/rep2 with resume=False and concatenates records; `run-all --reps N>1` routes through run_reps + prints the distribution summary, N==1 unchanged — confirmed by `test_aggregate_reps_*`, `test_run_reps_*`, `test_cli_run_all_reps_routes_through_run_reps` GREEN + full benchmark/tests suite green (prior single-rep run_pilot tests unchanged).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gated on complete evidence — additive pure-reducer + composed rep-loop, autonomy auto) · date: 2026-07-09

