# MILESTONE: WM1 lean-to-twelve — kill the two measured freeze/scope call sinks

goal: The WM1 loop's two 100%-reproducible call sinks die at the source: the first freeze no longer fails unflagged_freeze (the template carries a drafted-blank flag slot), and a zero-cover scope declaration is refused AT the freeze with a paste-ready fix (never surfacing later as scope_violation->re-cross). Earned when a fresh n=3 WM1 re-measure lands mean add.py calls <= 12 with fidelity held.
stage: mvp · status: active · created: 2026-07-23T13:27:27+00:00 · lane: tiny
release: pending

> Tiny plan — small scope, one approval. Keep it to a handful of lines; if it
> outgrows this shape, recreate without --tiny (the full SDD scaffold).

## Plan
- [x] freeze-flag-slot — PLAN.md.tmpl drafted-blank flag slot; unfilled part-menu never satisfies the gate (gate PASS)
- [x] scope-first-freeze — zero-cover §3 Scope refuses `scope_unresolved` AT the freeze; task-dir teach note; `src/` default flip; warn repair (gate PASS)
- [x] scope-walk-prune — .venv/venv/.tox/.mypy_cache/.ruff_cache/.eggs pruned from the scope walk; self-explaining default warn (gate PASS)
- [x] egg-info-prune — *.egg-info suffix-pruned (project-derived name, no literal covers it) (gate PASS)

## Done when
- [x] a fresh n=3 WM1 re-measure lands mean add.py calls <= 12 with fidelity held — **WAIVED 2026-07-23, signed: Tin Dang** (decision: 'Fix + close on trend'). Measured: run-2 mean 14.3 [11/17/15], run-3 mean 13.3 [13/17/10]; fidelity 1.00 on all 6 reps; unflagged_freeze 0/6 (was 3/3); rep-floor 10. Each run's misses trace to one artifact-dir trap, both since pruned (.venv wave, *.egg-info) — the fixes land AFTER their measuring run by construction. Full trend + tables: .add/benchmark-remeasure-2026-07-23.md
