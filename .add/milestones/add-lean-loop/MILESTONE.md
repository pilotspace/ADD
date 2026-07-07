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

- [x] add arm tokens_total per WM ≤50% of round-3 baseline (13.4M/3.1M/4.0M) — 2.07M (15%) / 1.22M (39%) / 1.06M (26%); loop total 4.35M vs 20.5M (−79%)
- [x] add arm median-of-3 spec_fidelity within ±0.05 of round-3 (0.94–0.97 band) — 0.95 / 0.92 / 0.95 vs 0.97 / 0.95 / 0.95 (max delta 0.03)
- [x] context_rot_slope stays ≥ −0.01 — 0.0 on all three WMs
- [ ] trust floor intact — **NOT MET / CONFOUNDED**: transcript audit of the lean
      reruns shows the workspace agent largely BYPASSED the engine (wm1: 3 calls,
      wm2: 0, wm3: 0 — vs 167 in baseline wm1); no frozen contract, red suite, or
      gate record exists in the lean workspaces. The −79% token cut is therefore
      substantially "ADD installed but unused", not "ADD run lean". Engine suite
      3202 green (CI-mirror cleared at 1c65269) + benchmark suite 94 green hold,
      but the rerun does not evidence the floor. HUMAN DECISION needed: rerun with
      loop-adherence enforced/measured, or re-scope the exit criterion.
- [x] no gate/freeze/evidence semantics changed — engine diff is ergonomics (advance --fill, status --brief/--section) + prose/guides; guard tests pin gate/freeze behavior unchanged
