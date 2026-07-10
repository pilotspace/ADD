# Benchmark campaign ledger — 2026-07 pinned-sonnet WM1 runs

Meter: `claude -p --model claude-sonnet-5 --effort medium --disable-slash-commands
--strict-mcp-config` (pin `4d0c52e`). Raw evidence (25 transcripts + records + oracles):
`~/add-benchmark-archives/2026-07-sonnet-campaign/` (16 MB, workspaces stripped).

**Every number from a different/unpinned model is VOID** — the 2026-07-09 confound proof
(same work: opus-4-8 $5.62 vs fable-5 $8.7–11) retired the old 63t/$3.99 anchor.

## Headline series (add WM1, n=3 per arm unless noted)

| Arm · engine | Turns (mean) | Cost | Fidelity | add.py calls |
|---|---|---|---|---|
| ADD pre-lever `4fefc0bb` (@94486bb) | 102.0 (82/127/97) | $4.51 | 0.85/0.25/0.00 — unstable | 21–33 + death spirals |
| ADD LOOP-1 `10ffdf96` | 98.0 (101/66/127) | $4.30 | 1.0/0.9/0.9 (judge noise) | 21–33 |
| ADD LOOP-2 `14787483` (@1327e3b) | **77.7** (96/66/71) | **$2.97** | **0.96/0.97/0.97 stable** | 21 (28/19/16) |
| ADD LOOP-3 `147820fd` (@901cd1f, n=1) | 80 | $3.32 | 0.25 (app unreachable at oracle; judge noise) | 20, skip-loop 0 hits |
| spec-kit (n=1) | **22** | **$0.91** | 1.00 | — |

## What the campaign established

1. **The 3-LOOP message-layer series is real**: −24% turns / −34% cost vs pre-lever at
   stable fidelity, first result outside the ~2× run-to-run noise floor. Repair loops
   killed: scope death spiral ~15t → ~3t recipe repair; skip trial-and-error 4–5 calls → 0;
   `--help` spelunking 7 → 2–5 (habit residue).
2. **Spec-kit is ~3.3× cheaper on WM1** (was ~5×). WM1 is a simple greenfield one-shot —
   the exact case a lightweight spec flow is optimal for. The residual ADD premium is
   structural trust ceremony (spec bundle · freeze · red suite · recorded gates), not waste.
3. **The fidelity judge is untrustworthy** (`judge.py` grounds on PROMPT.md + a
   reachable-bit; judge model unpinned): fid 0.0–1.0 spread on runs that all built working
   apps. No fidelity claim from this harness is load-bearing. Fix before the next campaign.
4. **Unmeasured where ADD claims value**: WM2/WM3 longitudinal, regression rate,
   context-rot slope, resumability, change-requests, gaming resistance — none of the
   dimensions ADD's ceremony pays for have ever been run on the fixed meter. That is the
   v2 benchmark's job (`benchmark/v2/DESIGN.md`).

## Run index (archive-relative)

- `mr-lever/`, `mr-baseline/` — fable-5 A/B (n=3+3, model-valid within itself, superseded)
- `mr-lever-sonnet/` (3) · `mr-baseline-sonnet/` (1) + `mr-baseline-sonnet-extra/` (2) — the LOOP-1 vs pre-lever sonnet A/B
- `speckit-sonnet/` (1) — the spec-kit comparator
- `loop2-lever/` (3) — the LOOP-2 re-measure (post `5a76222`+`1327e3b`)
- `loop3-verify/` (1) — the LOOP-3 verification (post `901cd1f`)
- `remeasure-runs/`, `runs-add-jul8-backup/` — earlier unpinned-era runs (VOID for cost, kept for transcript anatomy)
