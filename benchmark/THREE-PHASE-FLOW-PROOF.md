# three-phase-flow — benchmark findings (RETRACTED cost-beat claim)

> **Status: the earlier "ADD beats spec-kit" claim in this file is RETRACTED.**
> The add-bench harness has fairness and isolation problems (documented below)
> that make any ADD-vs-spec-kit **cost** comparison unreliable. What IS verified
> is the enhancement's *mechanism*. Honest cost claims await a fixed harness.

**Question:** does the `three-phase-flow` enhancement (oneshot/benchmark tasks
skip the optional ceremony phases `scenarios` · `observe`) let ADD beat spec-kit
in add-bench?

**Answer:** we cannot honestly say yet. The enhancement works mechanically, but
the harness cannot currently support a cost-beat claim. Under a *controlled*
same-session WM1 comparison, spec-kit was in fact **cheaper** than ADD — partly
because the harness over-charges ADD, and partly because ADD genuinely does more
per-feature work (its value proposition, not a defect).

---

## What IS verified (the mechanism — deterministic, $0)

- **fast-lane-skips fires and is recorded.** `test_fast_lane_skips.py` (45
  tests) + 4 mutation refute-reads prove the skip happens, is logged (no silent
  skip), and the floor holds (contract never skipped, security HARD-STOP).
- **Engaged live.** A headless WM1 run created `booking-crud --oneshot`,
  recorded the `scenarios` skip with reason/timestamp/actor, built a working app
  (HTTP 200), and closed at a recorded gate PASS.
- **Reduced ceremony.** vs the baseline ADD run: engine_calls 261 → 104,
  turns 219 → 163. Real, measurable.

## What is NOT trustworthy (harness problems)

**1. Work asymmetry — ADD is metered doing more.**
ADD delivers + verifies the app at turn 127, then spends **36 turns**
(`milestone-done`/`fold`/`archive-milestone`) on lifecycle bookkeeping with zero
app value — **~$1.80 of its $6.14 (29%)** — that spec-kit is never asked to do.
The add-loop wrapper instructs this ceremony; spec-kit gets a raw prompt.

**2. Environment pollution — not isolated, not reproducible.**
Runs inherit the operator's `~/.claude` (148 skills, 174 commands, 3 MCP
servers) and whatever prompt-cache warmth exists at that instant. This is the
source of the erratic 26K–132K "fresh input" startup — measurement noise, not
method cost, and it hits both arms differently across runs.

**3. Cross-environment comparison — invalid.**
The repo's older `add`/`spec-kit` records were produced in a different
environment than later reps. Comparing across them conflates the enhancement
with environment drift. Only same-session arm pairs are valid.

**4. Single-rep variance is large.** spec-kit WM1 measured **$1.33 (same
session) to $4.00 (older record)** — 3×. No single-rep claim survives that.

## The one controlled comparison we have (same session, same model, WM1)

| WM1 (today) | fidelity | turns | tokens | cost |
|---|--:|--:|--:|--:|
| ADD (fast-lane) | 0.97 | 163 | 7.56M | $6.14 |
| spec-kit | 0.97 | 31 | 786K | $1.33 |

Equal quality; ADD used 5× the turns and 4.6× the cost. Cost is dominated by
**cache_read = turns × context** (ADD 14.0M vs spec-kit 1.4M). Correcting for
the 29% ceremony tail, ADD's feature-delivery cost is ~$4.34 — still ~3.3×
spec-kit. That residual is ADD's genuine tests-first / frozen-contract rigor —
the trust it buys (regression resistance, no lost context), a real cost the
benchmark should report, not hide.

## Next (agreed with the human)

1. **Fix the harness** — meter cost to the app-delivered gate (not through
   milestone ceremony); run each arm in an isolated environment; same-session
   controlled multi-rep only.
2. **Re-measure** honestly on the fixed harness before any beat/lose claim.
3. **Attack ADD's real cost lever** — turn count (5× spec-kit). Batch engine
   round-trips, terser `add.py` output, fewer status/check cycles.

Reproduce the controlled pair: `pilot.run_pilot(arms=[a], wms=[1],
runs_root=<sep>, repo_root=<repo>)` per arm, same session.
