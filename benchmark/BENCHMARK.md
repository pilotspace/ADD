# add-bench — final pilot results

Final results of record for the add-bench pilot (2026-07-07/08). One rep,
5 arms × 3 workload milestones (task/booking REST API + CLI: CRUD → auth/rules
→ breaking-shape refactor), agent + median-of-3 judge on `claude --model
claude-sonnet-5`. Frozen metrics (5): regression_rate · spec_fidelity ·
tokens_total (+cost_usd) · context_rot_slope · time_to_first_edit. Advisory
artifacts: judge_scores · engine_calls (loop-adherence census) ·
fidelity_trajectory / fidelity_min. Full per-run detail: `runs/PILOT-REPORT.md`
(gitignored with the run artifacts).

## Final cross-arm comparison

The add row is the **final validated configuration**: loop enforced (census-
verified), WM(k) seeded from WM(k−1) (truly longitudinal), moment-of-use
engine hints. Other arms ran their stock configuration.

| arm | fidelity wm1→wm3 | fidelity min | tokens (3 WMs) | cost | time-to-first-edit (s) | trust evidence |
|-----|------------------|-------------|---------------:|-----:|------------------------|----------------|
| **add (final)** | **0.97 / 0.98 / 0.97** | **0.97** | 18.2M | ~$15 | 242 / 242 / 348 | frozen contract + recorded gate per task; census 251/74/27 |
| spec-kit | 0.97 / 0.95 / 0.95 | 0.95 | 3.8M | $2.53 | 44 / 68 / 103 | none recorded |
| gsd | 0.97 / **0.50** / 0.95 | 0.50 | 7.8M | $4.81 | 84 / 103 / 123 | none recorded |
| vanilla | 0.97 / 0.95 / 0.93 | 0.93 | 12.7M | $6.25 | 61 / 132 / 127 | none recorded |
| plan-mode | 0.00 / 0.00 / 0.00 | 0.00 | 11.7M | $6.44 | 59 / 160 / 418 | structural failure — never shipped a running app |

The verdict in one line: **ADD buys the highest and most stable fidelity
(best floor 0.97, no catastrophic milestone, auditable trust evidence) at a
cost premium that is front-loaded in the greenfield first milestone** —
incremental milestones after WM1 cost 3.2M / 2.1M (−25% vs baseline ADD)
as the foundation amortizes (census 251 → 74 → 27).

Shared caveats: single rep · one small CRUD domain · 3-WM horizon (too short
for context-rot separation: at n=3 the OLS slope is (f3−f1)/2, the middle WM
has zero weight — gsd's 0.50 collapse is invisible to it; hence fidelity_min).
The 0.67 regression_rate at wm3 is a workload artifact shared by every arm.

## Lessons of record

1. **Audit loop adherence before crediting a token cut.** An early "−79% lean
   win" was the agent bypassing the engine entirely (census 3/0/0);
   engine_calls is now a recorded artifact of every run.
2. **Discovery beats documentation.** Engine features named only in guides got
   0 adoption; the same features named in the engine's own output were adopted
   immediately (`advance --fill`: 0 → 12 uses, −29% WM1 tokens at identical
   fidelity). Same pattern as run-entry invariants (obeyed only once in the
   CLAUDE.md block agents re-read).
3. **A longitudinal benchmark must actually carry state forward.** WM prompts
   assumed the prior app; the harness gave fresh dirs; every arm silently
   rebuilt — exposed when an enforced ADD agent honestly refused an empty WM3.
4. **Greenfield bootstrap dominates ADD's cost** (~250 turns × growing context);
   setup tokens stay in tokens_total (every arm pays its own bootstrap) —
   amortized comparisons use the per-WM incremental numbers.
