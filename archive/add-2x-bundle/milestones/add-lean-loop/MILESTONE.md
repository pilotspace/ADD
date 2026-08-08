# MILESTONE: add-lean-loop — cut ADD's token cost, hold the trust floor

slug: add-lean-loop · created: 2026-07-07 · status: draft (await-confirm)
parent: ADD method (add-method/)

## Goal

Cut ADD's per-milestone token cost by ≥50% on the benchmark workload while
holding fidelity and the non-negotiable trust floor (frozen contract · red
test before build · recorded verify gate · security HARD-STOP).

## Why (evidence from the add-bench round-3 pilot)

- ADD spent $16.30 vs gsd $4.82 / spec-kit $2.54 for the same 3-milestone job
  at the SAME quality (median-of-3 judge: all 0.90–0.97; ADD the most stable).
- Decomposition (PILOT-REPORT.md Appendix B): 41–64% of each milestone's
  tokens burn BEFORE the first line of app code — 21–27 `add.py` round-trips
  and ~17 TASK.md section writes per milestone, each turn re-reading the full
  growing context. The cost is a per-turn context tax, not a one-time init.

## Scope

- add-method/tooling/add.py (+ 3-tree parity) — engine ergonomics only;
  no gate, freeze, or evidence rule may weaken.
- The `add` skill prompt + phase guides — loading discipline, not content.
- benchmark/ — reused as the measuring stick (no scoring changes).

## Tasks (breadth-first)

1. **engine-batch-ops** — one round-trip per phase transition:
   `add.py advance --fill <file|stdin>` writes the section AND advances in a
   single call; a combined `status --brief` that stops printing what the agent
   already has in context. Target: engine calls per milestone 21–27 → ≤8.
2. **progressive-task-context** — `add.py show <section>` + guide guidance to
   read ONLY the active TASK.md section instead of the whole file each turn;
   phase guides state the anti-context-rot loading rule explicitly.
3. **lightweight-setup** — init seeds SKELETON foundation files (headings +
   one-line seeds + `<!-- living: grows with milestones -->` markers) instead
   of full upfront drafts; sections fill on first touch by the milestone/task
   that needs them; the existing delta→fold loop keeps them living. The human
   baseline approval approves the skeleton + first-milestone intent — the
   trust floor is unchanged. (Human-added 2026-07-07: attacks the bootstrap
   half of WM1's 9.7M pre-code tokens.)
4. **fast-lane-intake-heuristic** — intake proposes `--fast` automatically for
   small/mechanical requests (human still confirms; flag stays human-owned).
   The full bundle for a CRUD-sized milestone is where the 41–55% pre-code
   share came from.
5. **bench-rerun-add-arm** — re-run ONLY the add arm on WM1–WM3 with the lean
   loop and compare against the round-3 records (kept as baseline).

## Exit criteria

- [x] add arm tokens_total per WM ≤50% of round-3 baseline — **NOT MET under honest
      enforcement**: the −79% was loop-bypass (census 3/0/0). Enforced+seeded:
      18.1M / 3.2M / 2.1M = 23.4M vs 20.5M. Valid lean win = incremental cost
      AFTER wm1 (wm2+wm3 = 5.3M vs 7.1M baseline, −25%, at higher fidelity);
      wm1 remedy VALIDATED: post-hint wm1 = 12.8M (−29%) at fid 0.97 unanimous,
      12 × advance --fill adopted. Honest loop total 18.2M vs 20.5M (−11%) at
      higher fidelity. ≤50% still unmet — remaining levers: --brief/--section
      moment-of-use hints (adoption 0), setup drafting volume, heal churn.
      **WAIVED by Tin Dang 2026-07-08** (close at honest 4/5; benchmark verdict of record in
      benchmark/BENCHMARK.md — remaining lever re-scoped to the risk-proportional-ceremony milestone).
- [x] add arm median-of-3 spec_fidelity within ±0.05 of round-3 (0.94–0.97 band) — enforced+seeded 0.97 / 0.98 / 0.97 (above baseline)
- [x] context_rot_slope stays ≥ −0.01 — 0.0 (enforced+seeded; fidelity_trajectory 0.97;0.98;0.97)
- [x] trust floor intact — RESOLVED by the enforced+seeded rerun (human-chosen
      path): every workspace task carries a FROZEN contract + a recorded gate;
      censuses 208/74/27 prove the loop was driven; fidelity 0.97/0.98/0.97
      (fidelity_min 0.97, slope 0.0) — the best of any arm-run in the pilot.
      Engine suite 3203 green · benchmark suite 110 green.
- [x] no gate/freeze/evidence semantics changed — engine diff is ergonomics (advance --fill, status --brief/--section) + prose/guides; guard tests pin gate/freeze behavior unchanged
