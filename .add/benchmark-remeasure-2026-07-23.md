# WM1 re-measure — 2026-07-23 (the paid run for the 4 held-open call/ceremony milestones)

> Ran to earn the `(paid, human-gated) WM1 re-measure` exit criteria of **call-floor**,
> **orientation-honesty**, **call-residuals**, **ceremony-to-effort**. Arm `add` (this branch,
> `feat/gate-udd-reconcile-thin-engine`), WM1 (booking CRUD REST+CLI), n=3 reps, model PINNED
> `claude-sonnet-5 --effort medium` (todo #28's model-drift blocker is fixed in
> `benchmark/runner/agent.py`; the todo is stale). `benchmark/` is gitignored — numbers recorded
> here durably. Runs at `benchmark/runs-remeasure-2026-07-23/rep{0,1,2}/add/wm1/`.

## Result vs the bars

| Bar (across the 4 milestones) | Target | Measured (n=3) | Verdict |
|---|---|---|---|
| mean `add.py` calls (true tool-use invocations) | ≤ 12 | **15.0** (13 · 20 · 12) | ✗ UNMET |
| requirement_coverage / fidelity | ≥ 0.97 | **1.00** (1.0·1.0·1.0) | ✓ MET |
| cost / rep | ≤ $2.97 | **$2.59** ($2.98·$2.46·$2.31) | ✓ MET |
| `--help` probes / rep | ≤ 1 (0 for ceremony) | **1.33** (2·2·0 — `re-cross -h` usage checks) | ✗ UNMET |
| double-init | 0 | **0** — CORRECTED: each rep's single `init` was the workspace's LEGITIMATE first init (the harness setup's init never landed in the workspace; first `status` root-walked to the ancestor with the warn). The earlier "~2 refusals/rep" miscounted the routine "project exists — do not re-init" status banner. | ✓ MET |
| post-freeze re-cross | 0 | **~2/rep** (2·3·1) | ✗ UNMET |
| scope_violation returns | 0 | **~4.3/rep** (8·3·2) | ✗ UNMET |
| regression_rate | 0 | **0** | ✓ MET |

## Reading (honest)

- **Fidelity + cost are excellent and clear their bars**: every rep built a fully-correct WM1
  (coverage 1.0, 0 regressions) at $2.59/rep — the cheapest honest ADD round on record.
- **The ≤12 call bar is UNMET at 15.0**, but the trend is real: 27 (baseline-r3) → 18.7
  (2026-07-13 ceremony re-measure) → **15.0** here (−44% from baseline, −20% since July 13).
- **The excess is concretely attributable** (root-caused from the transcripts, 3/3 reps):
  1. **`unflagged_freeze` fails the FIRST freeze in 100% of reps** (+1 call) — PLAN.md.tmpl
     has NO `Least-sure flag surfaced at freeze:` slot, so every agent drafts §3 without it,
     is refused, learns the format from the error, and re-freezes. Deterministic template gap.
  2. **Scope grammar-intuition traps** (+2–3 calls) — rep0 declared tokens WITHOUT backticks
     ("every token dropped — garbage grants NO cover"); rep1/2 declared `./app/` (which the
     grammar resolves to the TASK dir `.add/tasks/<slug>/app/`) while the WM's entry contract
     (`python -m app`) forces writes to workspace-root `app/`. Cover never matches the
     write-set → the freeze still SUCCEEDS (echo warns, propose-not-impose) → scope_violation
     at the gate → `re-cross` (+ `re-cross -h` probe) → gate again. The template default
     `` `./src/` `` itself teaches the task-dir shape.
  3. Trailing `status` after the final gate (+1, minor).
  The startup `status → init → status` is NOT waste: the workspace had no local `.add/` (the
  harness setup's init never landed there), so the agent's init was the designed first init.

## Verdict for the 4 milestones

The paid re-measure does **NOT** clear the closing criteria: the call-count floor (≤12) and the
zero-double-init / zero-re-cross / zero-scope_violation / --help sub-bars are all unmet. The
milestones' SHIPPED features are all done + test-verified; only these aspirational loop-economy
bars miss. DECIDED 2026-07-23 (human): lean-pass first, then one more n=3 re-measure — the two
levers are (1) a drafted-blank freeze-flag slot in PLAN.md.tmpl §3 (kills the 100% first-freeze
`unflagged_freeze` retry) and (2) fail-closed freeze on a zero-cover scope declaration + a
root-relative Scope default (kills the scope_violation→re-cross cycle). Projected census after
both: ~9–12 calls/rep.

Concurrency caveat: the run executed from inside an active claude session (≥1 concurrent) — the
model-pin removes the dominant cost invalidator, but cost/turn may carry minor concurrency skew.
