# add-bench — pilot results of record

Committed summary of the add-bench pilot (2026-07-07/08). Full per-run detail
lives in `benchmark/runs/PILOT-REPORT.md` (gitignored with the run artifacts);
this file persists the numbers and lessons that outlive the runs.

Harness: 5 arms (add · vanilla · gsd · spec-kit · plan-mode) × 3 workload
milestones (task/booking REST API + CLI: CRUD → auth/rules → breaking-shape
refactor), agent + median-of-3 judge on `claude --model claude-sonnet-5`.
Frozen metrics (5): regression_rate · spec_fidelity · tokens_total (+cost_usd)
· context_rot_slope · time_to_first_edit. Advisory artifacts: judge_scores ·
engine_calls (loop-adherence census) · fidelity_trajectory / fidelity_min.

## Cross-arm round 3 (heavy-baseline ADD) — full comparison

| arm | fidelity wm1→wm3 | slope | tokens (3 WMs) | cost | time-to-first-edit (s) | regression @wm3 |
|-----|------------------|-------|---------------:|-----:|------------------------|-----------------|
| add | 0.97 / 0.95 / 0.95 | −0.01 | 20.5M | $16.30 | 242 / 242 / 348 | 0.67 |
| spec-kit | 0.97 / 0.95 / 0.95 | −0.01 | 3.8M | $2.53 | 44 / 68 / 103 | 0.67 |
| gsd | 0.97 / **0.50** / 0.95 | −0.01 | 7.8M | $4.81 | 84 / 103 / 123 | 0.67 |
| vanilla | 0.97 / 0.95 / 0.93 | −0.02 | 12.7M | $6.25 | 61 / 132 / 127 | 0.67 |
| plan-mode | 0.00 / 0.00 / 0.00 (structural failure) | 0.0 | 11.7M | $6.44 | 59 / 160 / 418 | 1.00 |

Reading: at n=1 rep these separate into tiers, not rankings. spec-kit is the
cost/latency frontier; add is the stability/trust frontier (no catastrophic
milestone, frozen-contract + gate evidence, best fidelity floor — see the
enforced+seeded arc below where add reaches 0.97/0.98/0.97 at 18.2M);
gsd's wm2 collapse (0.50, invisible to the slope) is the variance cautionary
tale; plan-mode failed structurally (never shipped a running app). The 0.67
regression is a shared workload artifact (wm1 re-exports under wm3 auth),
arm-independent. Caveats: single rep, one small CRUD domain, 3-WM horizon —
too short for context-rot separation (see slope caveat below).

Slope caveat: at n=3 the OLS slope is (f3−f1)/2 — the middle WM has zero
weight, so gsd's wm2 collapse is invisible to it (hence fidelity_min).

## The add-arm cost arc (the lean-loop milestone)

| run | wm1 | wm2 | wm3 | loop total | valid? |
|-----|-----|-----|-----|-----------|--------|
| heavy baseline | 13.4M / 0.97 | 3.1M / 0.95 | 4.0M / 0.95 | 20.5M | yes |
| lean, unenforced | 2.1M / 0.95 | 1.2M / 0.92 | 1.1M / 0.95 | 4.4M | **no — census 3/0/0, loop bypassed** |
| enforced, unseeded | 18.1M / 0.97 / census 208 | 7.7M / 0.97 / 150 | agent refused empty workspace | — | exposed the carry-forward flaw |
| enforced + seeded | 18.1M / 0.97 / 208 | 3.2M / 0.98 / 74 | 2.1M / 0.97 / 27 | 23.4M | yes |
| **+ moment-of-use hint (wm1 rerun)** | **12.8M / 0.97 / --fill×12** | (3.2M) | (2.1M) | **18.2M (−11%)** | yes |

Trust floor under enforcement: every workspace task carries a frozen contract
and a recorded gate; fidelity 0.97 / 0.98 / 0.97 (fidelity_min 0.97, slope 0.0)
— the best of any arm-run in the pilot, at −11% tokens vs the heavy baseline.
Carry-forward economics: census falls 208 → 74 → 27 as the foundation
amortizes; incremental milestones cost −25% vs baseline at higher fidelity.

## Lessons of record

1. **Audit loop adherence before crediting a token cut.** The −79% "lean win"
   was the agent bypassing the engine (census 3/0/0). engine_calls is now a
   recorded artifact of every run.
2. **Discovery beats documentation.** `advance --fill` had 0 adoption while it
   lived only in guides; one appearance in the engine's `next:` footer produced
   12 adoptions and −29% wm1 tokens at identical fidelity. Same pattern as the
   run-entry invariants (obeyed only once in the CLAUDE.md block agents re-read).
3. **A longitudinal benchmark must actually carry state forward.** WM2/WM3
   prompts assumed the prior app; the harness gave fresh dirs; every arm
   silently rebuilt — masked until an enforced ADD agent honestly refused an
   empty wm3. WM(k) now seeds from WM(k−1).
4. **wm1 (greenfield bootstrap) dominates ADD's cost**: ~250 turns × growing
   context (48M cumulative cache-reads). Remaining levers: status --brief /
   --section moment-of-use hints (adoption still 0), setup drafting volume,
   heal/phase-override churn.
5. Setup tokens stay in tokens_total (every arm pays its own bootstrap);
   amortized comparisons use the per-WM incremental numbers above.
