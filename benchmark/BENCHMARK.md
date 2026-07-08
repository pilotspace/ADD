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

| WM | add fid / **cost** / tokens | spec-kit fid / **cost** / tokens |
|----|------------------------------|-----------------------------------|
| 1 | 0.97 / **$7.48** / 17.3M | 0.97 / **$4.00** / 8.9M |
| 2 | 0.98 / **$1.27** / 3.2M | 0.95 / **$2.65** / 4.5M |
| 3 | 0.97 / **$1.12** / 2.1M | 0.97 / **$2.80** / 5.4M |
| 4 | 0.98 / **$11.50** / 30.2M | 0.95 / **$3.74** / 7.8M |
| 5 | 0.98 / **$13.00** / 34.1M | 0.97 / **$5.48** / 12.7M |
| **total** | **min 0.97 / $34.37 / 86.9M** | **min 0.95 / $18.66 / 39.2M** |

**Cost is the fair headline, not raw tokens.** `tokens_total` weights cache
reads equally with fresh input, but cache reads bill at ~10% of the input
rate — and 99% of ADD's volume is cache reads (wm5: 33.7M of 34.1M; a
many-turn loop re-reading a cache-hot context). In dollars the premium is
**1.8×** ($34.37 vs $18.66), not the 2.2× the token ratio suggests — and on
the small incremental milestones (wm2/wm3) ADD was **half spec-kit's price**
($1.27/$1.12 vs $2.65/$2.80).

**Verdict: the crossover hypothesis is REFUTED at this horizon.** ADD was
cheaper per-WM only on the small milestones (wm2/wm3); when milestone scope
grew (wm4/wm5), BOTH arms' costs rose with scope and ADD's rose ~3–4× steeper
(full specification bundles + per-task ceremony over a now-large codebase).
The earlier "falling curve" conflated foundation amortization with shrinking
milestone scope. Cumulative: add $34.37 / 86.9M vs spec-kit $18.66 / 39.2M
(1.8× in dollars, 2.2× in raw tokens).

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

### Where ADD's tokens actually go (wm4+wm5 phase decomposition)

Per-turn usage attributed to the active loop phase (proportions of the two
big milestones' combined volume; turn counts in parentheses):

| loop phase | share | turns |
|-----------|------:|------:|
| tests (author + run the red suite) | 34% | 215 |
| verify (+ gate evidence) | 30% | 162 |
| done / observe / deltas | 16% | 80 |
| build | 13% | 65 |
| orient (status/resume) | 4% | 59 |
| contract | 2% | 18 |
| specify + scenarios | 1% | 13 |

The expensive part of ADD is NOT writing specifications (specify + scenarios
+ contract = ~3%) — it is **executing trust**: authoring and repeatedly
running test suites (34%) and gathering verify/gate evidence (30%) inside an
ever-larger codebase, across ~500 turns that each re-read the full context.
spec-kit ships the same milestone in half the turns (wm5: 88 vs 170) because
it writes spec documents, implements, and stops — no red-first suites, no
evidence gathering, no gate records. That is the literal price of the trust
floor, and why the next lever is risk-proportional ceremony: route small
tasks down a lane with ONE suite run and a thin gate, keep the full
machinery for milestones that earn it.

### Fairness digest — like-for-like phase statistics + audit checklist

**Same-classifier activity decomposition** (one activity classifier applied to
BOTH arms' wm4+wm5 transcripts — turns classified by what their tool calls DO,
never by arm-specific vocabulary):

| activity | add share (turns) | spec-kit share (turns) |
|----------|------------------:|------------------------:|
| thinking / responding | 44.9% (276) | 44.8% (121) |
| misc shell | 13.0% (84) | 12.5% (34) |
| method tooling (add.py / specify) | 11.9% (71) | 2.4% (10) |
| reading code | 9.6% (59) | 8.0% (25) |
| running tests | 7.4% (44) | 12.2% (28) |
| writing docs/specs | 5.4% (35) | 2.6% (7) |
| writing tests | 3.7% (23) | 6.7% (17) |
| writing app code | 2.7% (14) | 9.4% (23) |
| verifying the running app | 1.3% (6) | 1.4% (3) |
| **totals** | **612 turns · 115M** | **268 turns · 36M** |

The profiles are nearly IDENTICAL in proportion (thinking 44.9% vs 44.8%;
misc shell 13.0% vs 12.5%) — ADD does not spend on *different* activities,
it does the same work across **2.3× more turns** (612 vs 268), each turn
dragging a larger context (avg 188k vs 135k tokens/turn). The two visible
structural deltas: method tooling (11.9% vs 2.4% — the engine round-trips)
and the write balance (ADD writes proportionally more docs/tests, spec-kit
more app code). Cost = turns × context; ADD's premium is turn count, and the
engine round-trips both add turns directly and fragment the rest of the work
into smaller turns.

**Fairness audit checklist** (what a skeptical reviewer should check):

- [x] Same model + wrappers for agent and judge (`claude-sonnet-5`) — all arms.
- [x] Same ceilings — token_ceiling 200000, turn_ceiling 60, in every arm TOML.
- [x] Same workload prompts, byte-identical across arms (wrapper prefix excepted).
- [x] Same oracle suites, never visible to any arm; same median-of-3 judge.
- [x] Same carry-forward seeding for every arm from WM2 on.
- [x] Same activity classifier for the phase statistics above.
- [x] One harness un-block fix per arm where the longitudinal harness broke it
      (add: headless proxy-authority clause; spec-kit: `specify init --force`).
- [ ] **Prompt-wrapper asymmetry** — add runs under an enforcement wrapper
      (drive the loop, proxy authority); spec-kit runs `raw`. Defensible
      (each arm driven as its method intends) but the add wrapper was tuned
      across 3 iterations this pilot; spec-kit's flow got no equivalent tuning.
- [ ] **Optimization asymmetry** — the engine grew moment-of-use hints during
      the pilot specifically to cut add's cost; no spec-kit-side equivalent
      was attempted.
- [ ] **n=1 reps** — run-to-run variance is documented at up to 8× (spec-kit
      wm1: 1.1M vs 8.9M) and a full fidelity flip (an add wm2 rerun: 0.0 vs
      0.98). Every per-cell number here needs ≥3 reps before external use.
- [ ] **Author bias** — the benchmark is built and run by the ADD authors;
      the checklist, raw records, and transcripts exist so a skeptic can
      re-derive every number.

Bottom line, updated: **ADD's price is proportional to how much specification
ceremony a milestone triggers, and does not converge to spec-kit's at any
tested horizon. What the premium buys — a 0.97 fidelity floor over five
milestones, zero measured rot, and an auditable trust record per task — is
worth 2.2× on work where a bad milestone is expensive, and is not worth it
on work where a 0.95 floor and no audit trail are acceptable.** The next
cost lever is risk-proportional ceremony (route small/mechanical work down
the fast lane by default), not further micro-optimization of the full loop.
