# six-phase-loop WM1 re-measure — 2026-07-14

3 reps · `add` arm · pinned meter (`claude-sonnet-5 --effort medium`) · engine =
six-phase-loop merged into main (`8360b06` resolved pin; PRs #146/#149/#148),
installed editable by the arm's own setup. Archived: `benchmark/runs/sixphase-r{1,2,3}`.
Method: same transcript anatomy as the ceremony re-measure (assistant-message turns;
`add.py <subcommand>` invocations in Bash tool_use).

## Per rep

| rep | turns | add.py calls | --help | cost | fidelity | regressions |
|-----|------:|-------------:|-------:|------:|---------:|------------:|
| r1  | 119   | 19           | 1      | $3.05 | 0.98     | 0 |
| r2  | 138   | 22           | 1      | $3.02 | 0.98     | 0 |
| r3  | 137   | 21           | 1      | $3.44 | 0.98     | 0 |
| **mean** | **131** | **20.7** | **1.0** | **$3.17** | **0.98** | **0** |

Prior round (ceremony, same meter): 134 turns · 18.7 calls · $3.51 · fid 0.98 · 0 regr.

## Verdict vs the milestone exit bar

- fidelity ≥ 0.97 held → **MET** (0.98 ×3, oracle pass 1.0, zero regressions)
- calls ≤ 12 → **UNMET** (mean 20.7; ceremony was 18.7 — flat within rep noise)
- cost −10% vs ceremony ($3.17 vs $3.51) — the cheapest honest ADD round measured
- turns −2% (131 vs 134)

## Anatomy — why the phase merge didn't move the call count

The merge did what it claims mechanically: crossings are 5-6 `advance`s (was 7-8
pre-merge), one freeze, one gate. But the call budget is dominated by residuals
ORTHOGONAL to phase count, the same four levers the ceremony report named:

1. **double init** — r1 and r3 ran `init` twice (+`lock` ×2 in r1) although the
   arm's setup already initialized; status still doesn't say "do NOT init".
2. **re-cross repairs** — r2 ×3, r3 ×1: scope declarations repaired post-freeze.
   (The scope echo surfaces the resolution; a mis-drafted line still costs a
   re-cross round-trip.)
3. **status re-reads** — 3-4/rep, orientation re-anchoring.
4. **--help habit** — exactly 1/rep, stubborn.

Sum of those ≈ 8-10 calls/rep — removing them alone would land ~11-12, i.e. the
bar is reachable but through the message/ergonomics layer, not more phase surgery.

## Decision

Recorded at milestone close (six-phase-loop): fidelity criterion MET; calls
criterion UNMET on this meter — disposition per the human's close decision.
