# three-phase-flow — benchmark proof (ADD vs spec-kit)

**Question:** does the `three-phase-flow` enhancement (oneshot/benchmark tasks
skip the optional ceremony phases `scenarios` · `observe`) let ADD beat
spec-kit in the add-bench harness?

**Answer (honest):** ADD **already beats spec-kit on 2 of 3 milestones** (WM2,
WM3) on both tokens and cost at equal-or-better fidelity. It trailed only on
**WM1** (the greenfield first milestone). The enhancement **halved WM1 token
throughput and cut engine calls 60%**, taking WM1 from 2× spec-kit's tokens to
a **dead tie** at identical fidelity — but WM1's *dollar* cost is structural
(tests-first generation, not the skipped ceremony) and stays ~2× spec-kit. The
"skip ceremony → cheaper" lever is real but modest; ADD's win over spec-kit is
carried by its whole-milestone efficiency, which the enhancement sharpens.

---

## What shipped

Three tasks (all committed on `feat/add-bench-scaffold`):
1. **phase-bundles** — the 8 phases run as 3 agent-owned bundles (DIRECTION ·
   BUILD · VERIFY), agent-call-preferred.
2. **ai-plan-verify-gate** — a two-way DIRECTION gate: an AI can verify + auto-
   freeze the contract EXCEPT for `security`/`data`/`architecture` (→ human;
   security HARD-STOP).
3. **fast-lane-skips** (`ea0462a`) — a cleared oneshot/benchmark/fast task
   declares an AI-chosen skip-set drawn ONLY from `{scenarios, observe}`; the
   contract is never skipped, tests/build/verify are never skippable, every
   skip is recorded (no silent skips), security stays a human HARD-STOP.
4. **benchmark wiring** (`7b41081`) — the `add-loop` arm wrapper now tells the
   headless agent to run the fast lane (`new-task --oneshot`, `skips:
   scenarios, observe`) while stating the floor.

## Deterministic proof ($0, reproducible)

- **Mechanism** — `test_fast_lane_skips.py` (45 tests) proves the skip *fires*
  and is *recorded*, backed by 4 mutation refute-reads (widen the skip tuple to
  include `contract` · strip the skip recording · drop lane-eligibility · let
  the freeze gate permit `security`) — each confirmed to turn the suite red,
  then reverted. Verify gate: architecture/high-risk → **human PASS**.
- **WM1 ceremony cost analysis** — bucketing the recorded baseline WM1
  transcript by phase (using `add.py advance` transitions as boundaries):

  | phase | turns | ~cost share |
  |---|--:|--:|
  | verify | 72 | **40%** |
  | tests | 47 | **23%** |
  | ground | 59 | 17% |
  | build | 19 | 11% |
  | contract | 15 | 6% |
  | **scenarios** (skipped) | **4** | **1.6%** |
  | observe (skipped) | 0 | ~0% (baseline already closed at the verify gate) |

  **Finding:** the skipped ceremony is ~1.6% of WM1's cost. WM1's gap vs
  spec-kit is structural — it lives in `verify` + `tests` (ADD's tests-first
  rigor), not in the optional phases the enhancement removes.

## Live corroboration — enhanced-ADD WM1 (1 rep, real `claude -p`)

Ran the enhanced engine headless into a separate runs-root (baseline
preserved). The enhancement engaged live: task `booking-core` created
`--oneshot` (oneshot=true, fast=true); `scenarios` skip **recorded** with
reason + timestamp + actor; app fully built; closed at a recorded verify gate.

| WM1 | fidelity | tokens_total | cost | engine_calls |
|---|--:|--:|--:|--:|
| add (baseline) | 0.97 | 17,297,527 | $7.48 | 261 |
| **add (enhanced)** | **0.97** | **8,894,397** | **$7.77** | **104** |
| spec-kit | 0.97 | 8,899,660 | $4.00 | 0 |

- **tokens_total −48.6%** (17.3M → 8.89M) → **tied with spec-kit** (8.894M vs
  8.900M) at identical fidelity 0.97.
- **engine_calls −60%** (261 → 104) — the ceremony reduction is real and
  measurable.
- **cost ~flat** ($7.48 → $7.77). Why cost didn't follow tokens down: 8.63M of
  the 8.89M total are *cache-read* tokens (~0.1× price). `tokens_total` is 97%
  cheap cache-read throughput and a poor $ proxy; cost tracks the expensive
  tokens (cache-creation 152K + output 68K + fresh input 47K), which is the
  structural tests-first generation the skip does not touch. So on **$ cost**,
  WM1 stays ~2× spec-kit — consistent with the 1.6% deterministic finding.

## Aggregate verdict (WM1–3, current single-rep records)

| WM | fidelity (add / sk) | tokens (add / sk) | cost (add / sk) | ADD verdict |
|---|---|---|---|---|
| WM1 (enhanced) | 0.97 / 0.97 | 8.89M / 8.90M | $7.77 / $4.00 | tokens **tie**, cost trails |
| WM2 | **0.98** / 0.95 | **3.16M** / 4.47M | **$1.27** / $2.65 | **ADD wins both** |
| WM3 | 0.97 / 0.97 | **2.11M** / 5.35M | **$1.12** / $2.80 | **ADD wins both** |

Plus (from the pilot report): ADD holds a **regression-rate and context-rot**
edge spec-kit does not — trust properties, not just throughput.

**Bottom line:** ADD beats spec-kit on 2 of 3 milestones on both cost and
tokens at equal-or-better fidelity, with a regression/context-rot edge. The
`three-phase-flow` enhancement closed WM1's token gap to a tie and cut engine
calls 60%; it does not flip WM1's dollar cost, which is structural. The claim
"ADD beats spec-kit" holds — carried by whole-milestone efficiency, sharpened
(not created) by the skip mode.

## Caveats

- **Single rep per cell** — high model variance; these are directional, not
  statistically settled. The enhanced-WM1 tokens landing within 0.06% of
  spec-kit is partly coincidence. A multi-rep run would firm the intervals.
- Baseline WM1 was recorded earlier; `total_cost_usd` is API-computed at run
  time. Same-model fairness floor holds across arms.
- Reproduce: `python3 -m benchmark.pilot run-all --arms add --wms 1` (writes to
  the default runs-root; point a separate root to preserve baselines).
