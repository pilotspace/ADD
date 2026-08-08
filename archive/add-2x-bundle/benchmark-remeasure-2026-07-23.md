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


---

## Run 2 — post lean-pass (freeze-flag slot + scope-first freeze), n=3

| rep | engine calls | coverage | oracle | regr | cost | cause of overage |
|---|---|---|---|---|---|---|
| 0 | 11 | 1.00 | 1.00 | 0 | $3.39 | .venv scope_violation tail only |
| 1 | 17 | 1.00 | 1.00 | 0 | $3.65 | .venv + warn-instructed re-cross thrash x3 |
| 2 | 15 | 1.00 | 1.00 | 0 | $6.03 | .venv scope_violation loop |
| **mean** | **14.3** ✗ | 1.00 ✓ | 1.00 ✓ | 0 ✓ | $13.07 | |

unflagged_freeze: 0/3 (was 3/3) — the flag slot killed sink 1. New sink: `_SCOPE_EXCLUDE_DIRS`
pruned node_modules but not `.venv` → 3/3 reps tripped scope_violation on virtualenv files.
The untouched-Scope-default warn INSTRUCTED `re-cross --by` and reprints on every re-cross → thrash.
Fix wave: scope-walk-prune (.venv/venv/.tox/.mypy_cache/.ruff_cache/.eggs + self-explaining warn).

## Run 3 — post scope-walk-prune, n=3

| rep | engine calls | coverage | oracle | regr | cost | cause of overage |
|---|---|---|---|---|---|---|
| 0 | 13 | 1.00 | 1.00 | 0 | $4.36 | app.egg-info violation + agent dropped the flag slot rewriting §3 (1 unflagged_freeze) |
| 1 | 17 | 1.00 | 1.00 | 0 | $4.55 | app.egg-info + real root .gitignore write + --help exploration |
| 2 | **10** ✓ | 1.00 | 1.00 | 0 | $2.24 | app.egg-info only |
| **mean** | **13.3** ✗ | 1.00 ✓ | 1.00 ✓ | 0 ✓ | $11.15 | |

`pip install -e .` writes the PROJECT-DERIVED `app.egg-info/` — no literal prune covers it; 3/3 reps.
Fix wave: egg-info-prune (suffix match in _scope_walk's dirnames filter). Counterfactual without
that loop: ~10/14/8 → ~10.5 mean.

## Resolution — 2026-07-23 (human decision: "Fix + close on trend")

Trend: 27 → 18.7 → 15.0 → **14.3** → **13.3** mean engine calls (−51%); fidelity 1.00 on every
measured rep across all runs; rep-floor 10. Both named engine sinks are dead (unflagged_freeze 0/6,
scope-grammar garbage refused at the freeze) and three artifact-dir prune waves shipped. The strict
<=12 MEAN is **waived, signed: Tin Dang** — each remaining miss traced to one artifact-dir trap whose
fix necessarily lands after its measuring run. Milestones closed on this evidence: wm1-lean-to-twelve ·
call-floor · orientation-honesty · call-residuals · ceremony-to-effort. Open backlog kept honest:
ceremony-to-effort's <=30KB read-burden tail (SKILL.md flow-table trim) and any future re-measure.
