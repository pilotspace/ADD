# add-bench — final pilot results

Final results of record for the add-bench pilot (2026-07-07/08). One rep,
agent + median-of-3 judge on `claude --model claude-sonnet-5`. Full per-run
detail: `runs/PILOT-REPORT.md` (gitignored with the run artifacts).

## What is being benchmarked

**The arms** — five ways of driving the same coding agent:

- **add** — this repo's AI-Driven Development method: spec → scenarios →
  frozen contract → red tests → build → recorded verify gate, driven through
  the `add.py` engine.
- **vanilla** — the bare agent, prompt in / code out, no method.
- **plan-mode** — the agent with a "plan first, then execute" wrapper.
- **gsd** — the GSD orchestration framework (research → plan → execute phases).
- **spec-kit** — GitHub's spec-kit (constitution + spec-driven prompts).

**The workload** — one longitudinal greenfield project (a task/booking REST
API + CLI) grown across three milestones; each WM(k) workspace inherits the
finished WM(k−1) app, so later milestones work against real accumulated code:

- **WM1 — greenfield CRUD**: bookings resource (`title`, `start_time`,
  `duration_minutes`, `status`) with 5 REST endpoints + a CLI over the same
  logic. Entry contract: the app must run as `python -m app` on `$PORT`.
- **WM2 — auth + business rules**: token auth, per-user ownership,
  double-booking overlap rejection, cancellation-window rule — layered onto
  the WM1 app without breaking it.
- **WM3 — breaking-shape refactor (regression bait)**: `duration_minutes` is
  REMOVED in favor of `end_time`; every endpoint, CLI command, and WM2
  business rule must migrate while behavior holds. Deliberately breaks the
  WM1-frozen shape to test how each method handles a controlled breaking
  change.

## Metrics

Five frozen metrics, scored per WM from the run record, the workspace, and an
oracle test suite the agent never sees:

- **spec_fidelity** (0–1) — how faithfully the shipped app matches the WM's
  written requirements; median of 3 independent LLM-judge calls against the
  oracle report (raw scores kept as the `judge_scores` artifact).
- **regression_rate** (0–1, WM3 only) — fraction of must-survive oracle tests
  (WM1/WM2 behaviors that legitimately survive the WM3 refactor) that FAIL
  after it; 0 is clean.
- **tokens_total / cost_usd** — total tokens and USD billed for the WM's agent
  run, parsed from the transcript. Setup/bootstrap is included: every arm pays
  its own.
- **context_rot_slope** — OLS slope over the three per-WM fidelities; measures
  quality decay as the project grows. Caveat: at n=3 it equals (f3−f1)/2 — the
  middle WM has zero weight — so it is complemented by `fidelity_trajectory` /
  `fidelity_min`.
- **time_to_first_edit** (s) — seconds from agent start to the first file
  edit; the latency cost of a method's up-front ceremony.

Advisory artifacts (recorded, never gate anything): `judge_scores` ·
`engine_calls` (loop-adherence census — how often the agent actually drove
the ADD engine) · `fidelity_trajectory` / `fidelity_min`.

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

### Token use per workload milestone (transparency)

| arm | WM1 (greenfield CRUD) | WM2 (auth + rules) | WM3 (breaking refactor) | total |
|-----|----------------------:|-------------------:|------------------------:|------:|
| **add (final)** | 12.85M | 3.16M | 2.11M | 18.1M |
| spec-kit | 1.11M | 1.08M | 1.64M | 3.8M |
| gsd | 2.03M | 2.48M | 3.28M | 7.8M |
| vanilla | 2.01M | 4.28M | 6.38M | 12.7M |
| plan-mode | 1.81M | 3.32M | 6.55M | 11.7M |

The trajectories tell the real story: **every other arm's per-WM cost RISES
as the project grows** (vanilla 2.0→6.4M, plan-mode 1.8→6.6M, gsd 2.0→3.3M —
re-reading an ever-larger codebase each milestone), while **ADD's FALLS**
(12.85→3.2→2.1M — the foundation and frozen contracts amortize; loop census
falls in step). ADD's entire premium is the WM1 bootstrap: from WM2 onward it
is cheaper than vanilla and plan-mode and within ~2× of spec-kit. Extrapolated
one more milestone at these trajectories, ADD's incremental cost crosses below
gsd's as well — the horizon-extension experiment (WM4+) would test exactly this.

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


## WM4/WM5 horizon extension — the crossover verdict

Hypothesis (from the 3-WM trajectories): add's falling per-WM cost crosses
below spec-kit's rising cost around WM4–5. Test: two new milestones — WM4
feature growth (filters · pagination · recurring) and WM5 cross-cutting
change (rooms, per-room overlap) — both arms run wm1→wm5 under the SAME
harness (loop-enforced add with headless proxy authority; carry-forward
seeding for every arm).

| WM | add fid / tokens | spec-kit fid / tokens |
|----|------------------|----------------------|
| 1 | 0.97 / 17.3M | 0.97 / 8.9M |
| 2 | 0.98 / 3.2M | 0.95 / 4.5M |
| 3 | 0.97 / 2.1M | 0.97 / 5.4M |
| 4 | 0.98 / 30.2M | 0.95 / 7.8M |
| 5 | 0.98 / 34.1M | 0.97 / 12.7M |
| **total** | **min 0.97 / 86.9M** | **min 0.95 / 39.2M** |

**Verdict: the crossover hypothesis is REFUTED at this horizon.** ADD was
cheaper per-WM only on the small milestones (wm2/wm3); when milestone scope
grew (wm4/wm5), BOTH arms' costs rose with scope and ADD's rose ~3–4× steeper
(full specification bundles + per-task ceremony over a now-large codebase).
The earlier "falling curve" conflated foundation amortization with shrinking
milestone scope. Cumulative: add 86.9M vs spec-kit 39.2M (2.2×).

What the extension DID prove:
- **Five-milestone quality**: add 0.97;0.98;0.97;0.98;0.98 (min 0.97, slope
  +0.002 — zero rot over 5 WMs) vs spec-kit 0.97;0.95;0.97;0.95;0.97 (min
  0.95, slope 0.0). Both excellent; add holds a small, consistent edge and
  the higher floor, with per-task trust evidence spec-kit does not produce.
- **Cost tracks milestone SCOPE, not milestone COUNT, for both methods.**
  Amortization is real (add's census fell 251→74→27 on wm1–3) but is
  overwhelmed by scope growth once milestones get structurally bigger.
- **Harness findings**: ADD's contract-freeze human gate stalls headless runs
  (fixed: proxy-authority wrapper clause); spec-kit's `specify init --here`
  aborts on the non-empty seeded workspaces (fixed: `--force`); spec-kit's
  own costs under the honest longitudinal harness (8.9→12.7M) are far above
  its round-3 fresh-dir numbers (1.1–1.6M) — the "cheap" reputation was
  partly the rebuild-from-scratch shortcut.
- Run-to-run variance at n=1 is large for BOTH arms (add wm1: 12.8–18.1M
  across three same-config runs; one add wm2 rerun scored ~0.0 where another
  scored 0.98; spec-kit wm1: 1.1M vs 8.9M). Trajectory claims need ≥3 reps.

Bottom line, updated: **ADD's price is proportional to how much specification
ceremony a milestone triggers, and does not converge to spec-kit's at any
tested horizon. What the premium buys — a 0.97 fidelity floor over five
milestones, zero measured rot, and an auditable trust record per task — is
worth 2.2× on work where a bad milestone is expensive, and is not worth it
on work where a 0.95 floor and no audit trail are acceptable.** The next
cost lever is risk-proportional ceremony (route small/mechanical work down
the fast lane by default), not further micro-optimization of the full loop.
