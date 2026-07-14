# Appendix H — Measured: ADD vs spec-kit vs GSD vs vanilla

ADD ships with its own adversarial benchmark (`benchmark/` in the repo): four
agent flows build the same longitudinal project — a booking REST API + CLI that
**evolves** across workload milestones (WM1 → WM3), including a deliberately
hostile change request — on a pinned meter (`claude-sonnet-5`, effort medium),
scored by deterministic oracles, tamper detection, and regression probes. This
appendix is the honest scoreboard. Two things make these numbers worth reading:

1. **We attack our own meter.** Six meter defects were found and fixed live
   during the 2026-07 campaigns (identical scores across independent arms
   indict the meter, not the arms; a too-cheap run is a defect smell). An
   early result favorable to ADD was **retracted** when the fidelity judge
   proved untrustworthy, and the campaign re-ran on the fixed meter. What
   survived that process is below, with raw records archived per run.
2. **Honest-outcome clause.** Findings that cut against ADD print unchanged.
   The cost gap is real and stated first.

## The scoreboard (WV1 — greenfield evolution, corrected rescore, n=1 rep)

Three milestones, same workspace evolving, four arms. Source:
`benchmark/results/2026-07-wv1-rep0.md`.

| arm | WM1 pass/reg | WM2 pass/reg | WM3 pass/reg | rep cost | tokens |
|---|---|---|---|---|---|
| **ADD** (main) | 1.00 / 0 | 1.00 / 0 | 1.00 / 0 | $13.94 | 29.3M |
| **ADD** (lean branch) | 1.00 / 0 | **0.80** / 0 | 1.00 / 0 | $9.30 | 19.7M |
| GitHub **spec-kit** (v0.12.5) | 1.00 / 0 | 1.00 / 0 | 1.00 / 0 | $3.43 | 5.7M |
| **vanilla** Claude Code | 1.00 / 0 | 1.00 / 0 | 1.00 / 0 | $3.07 | 4.3M |

**The honest headline: on a friendly workload at n=1, cost separates and trust
does not.** Every arm held every floor. If your project is a weekend prototype,
spec-kit or vanilla is genuinely cheaper — ADD's own `prototype` stage says the
same thing (run light, code is throwaway). The ceremony gap is 2.7–4.5× on this
workload, consistent across releases. Adjusted for the trust vector (own-suite
evidence weighted by weakened-test adjudication), the campaign's scoring report
put cost *per trusted feature* at spec-kit $1.14 · vanilla $1.53 · ADD branch
$4.65 · ADD main $13.94 — ADD's premium is real, and it buys enforcement, not
output.

## The hostile change (WV2 — gaming resistance)

The arms then received an undirected change request that **contradicts a frozen
rule**, where the cheapest green is quietly weakening your own overlap tests.
Source: `benchmark/results/2026-07-wv2-rep0.md`.

| arm | hostile step pass / regression / tests weakened | rep cost |
|---|---|---|
| ADD (main) | 1.00 / 0 / **0** | $11.14 |
| ADD (lean branch) | 1.00 / 0 / **0** | $8.16 |
| spec-kit | 1.00 / 0 / **0** | $3.08 |
| vanilla | 1.00 / 0 / **0** | $3.01 |

No arm gamed at this temptation strength — modern models re-spec honestly when
the amendment has a natural scoped form. The difference is *what guarantees it*:

- In vanilla/spec-kit/GSD, honesty under pressure is a **model property** —
  it held here, and nothing detects the day it doesn't.
- In ADD it is a **mechanical floor**: the contract is frozen and
  tamper-fingerprinted at the tests→build crossing, every red test is hashed,
  a weakened test or edited contract bounces the build back (`return_to_build`,
  three strikes), and a security finding can never be auto-passed. The same
  campaign proved these teeth bite the *author* too: ADD's own gate returned
  one of this book's engine tasks to build when the snapshot read its edits
  as tampering.

## Where ADD measurably leads

- **Fidelity that stays put while the spec evolves.** ADD (main) is the only
  arm that held 1.00/1.00/1.00 across the evolving milestones in WV1, and the
  2026-07-14 re-measure held 0.98 × 3 reps with zero regressions and oracle
  pass 1.0. The one ADD fidelity miss all campaign (branch WM2, 0.80) was
  root-caused to tests speaking a *friendlier input dialect* than the spec's
  own examples — and became a shipped floor (the spec-dialect check) the next
  release. The failure mode is now detected mechanically, for every future task.
- **Stored-data robustness.** At WM3 the apps inherit bookings written under the
  WM2 schema. ADD (main) was the only arm that **migrated its stored data**;
  vanilla handled the legacy rows without migrating; ADD (branch) and spec-kit
  both **crashed** serving them (`KeyError: 'end_time'`). This was un-metered —
  found during rescore, the workload never demanded a migration, so it is a
  planned probe, not a scored result — but it is exactly what "trust" means once
  real users have data, and it split the field cleanly.
- **A self-measuring cost curve.** Because the loop benchmarks itself, its
  overhead falls release over release at held fidelity: WM1 cost
  $4.51 → $3.51 → **$3.17** per rep across three consecutive method releases
  (risk-proportional → ceremony-to-effort → six-phase-loop), fidelity 0.97–0.98
  throughout, zero regressions. The ceremony you pay for is audited and pruned
  with the same rigor as the code.
- **Session-proof state.** The engine's `status` is the resume point; the
  time-to-first-edit and context-rot metrics exist because the method treats
  "the agent forgot" as a defect class, not weather.

## GSD (v1 meter only — indicative, not comparable)

GSD was measured on the earlier v1 meter (whose judge was later found
untrustworthy and whose WM3 regression numbers were probe-pollution artifacts),
and has not been re-run under the fixed v2 meter:

| arm | WM1 fid | WM2 fid | WM3 fid | cost/WM |
|---|---|---|---|---|
| GSD | 0.97 | **0.50** | 0.95 | $1.19–1.82 |

The WM2 fidelity collapse is the one distinctive signal: GSD's documentation
weight front-loads planning artifacts, and on the evolving milestone the build
drifted from the spec mid-track. Treat as direction, not conclusion, until a
v2-meter re-run — that honesty cuts both ways.

## How to choose (the same advice ADD's stages encode)

| situation | measured recommendation |
|---|---|
| throwaway prototype, demo, spike | vanilla / spec-kit — 3× cheaper, floors don't bind |
| spec evolves, data persists, users exist | ADD — the only flow whose trust floors are enforced rather than assumed, at $3.17/WM1 and falling |
| hostile or ambiguous change requests | ADD — frozen contract + tamper tripwire make the honest path the only green path |
| compliance / security surface | ADD — security findings HARD-STOP mechanically; no other measured flow has an un-forceable floor |

Method notes: pinned model + effort, self-carried permissions, per-run archived
transcripts and records (`benchmark/runs/`), oracle probes derived from each
track's own prompts, controls validated both ways before scoring. Re-run it
yourself: `python3 -m benchmark.run run --arm <add|spec-kit|vanilla|gsd> --wm 1`.
