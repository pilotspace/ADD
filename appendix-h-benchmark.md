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

## The scoreboard (same meter, same day, n=1 rep)

Three milestones, same workspace evolving. The primary table is a fresh run of all
three flows on one day, one meter, one workload
(`2026-07-14-v2-sameday.md`) — so they compare without vintage skew. Vanilla carries
its 2026-07-10 WV1 figure (`2026-07-wv1-rep0.md`), the last time it was run.

The "pass" column is `oracle_pass_rate` — the v2 meter's *deterministic* fidelity
of record (the milestone's own probe suite run against the built app; no LLM in the
scoring path).

| arm | WM1 pass/reg | WM2 pass/reg | WM3 pass/reg | rep cost | tokens |
|---|---|---|---|---|---|
| **ADD** (current main) | 1.00 / 0 | 1.00 / 0 | 1.00 / 0 | $9.11 | 18.19M |
| GitHub **spec-kit** (v0.12.5) | 1.00 / 0 | 1.00 / 0 | 1.00 / 0 | $4.20 | 6.03M |
| **GSD** (get-shit-done-cc 1.42.3) | 1.00 / 0 | **0.80** / 0 | 1.00 / 0 | $3.01 | 3.70M |
| **vanilla** Claude Code † | 1.00 / 0 | 1.00 / 0 | 1.00 / 0 | $3.07 | 4.3M |

† vanilla not re-run this round; 2026-07-10 WV1 figure carried forward.

**The honest headline: on a friendly workload at n=1, cost separates and trust
does not.** Every arm held its oracle. If your project is a weekend prototype,
spec-kit, vanilla, or GSD is genuinely cheaper — ADD's own `prototype` stage says
the same thing (run light, code is throwaway). ADD costs 2.2× spec-kit and 3.0× GSD
here, the same ordering the 2026-07-10 WV1 campaign found. Two honest notes on the
cost gap: **(1)** current ADD is ~$9, not the ~$14 the older WV1 `add-main` control
showed — that control was pinned before the lean / ceremony-to-effort / six-phase
reductions merged, and this same-day run measures the merged main. **(2)** adjusted
for the trust vector (own-suite evidence weighted by weakened-test adjudication), the
WV1 scoring report put cost *per trusted feature* at spec-kit $1.14 · vanilla $1.53 ·
ADD $4.65 — ADD's premium is real, and it buys enforcement, not output.

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

- **Fidelity that stays put while the spec evolves — and stays green under an
  *audited* floor.** ADD held oracle 1.00/1.00/1.00 across the evolving milestones
  in the same-day run (so did spec-kit and vanilla on clean state — on a friendly
  workload, fidelity does not separate the flows, and this appendix says so). What
  is ADD-specific is *how* that green is earned: the 2026-07-14 loop re-measure held
  0.98 × 3 reps with zero regressions under the frozen-contract + tamper-tripwire
  discipline, and the one ADD fidelity miss all campaign (an earlier branch WM2,
  0.80) was root-caused to tests speaking a *friendlier input dialect* than the
  spec's own examples — then became a shipped floor (the spec-dialect check). The
  failure mode is now detected mechanically, for every future task.
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

## GSD on the fixed v2 meter (re-run 2026-07-14)

GSD (`get-shit-done-cc` 1.42.3) was originally measured only on the retired v1
meter, whose LLM judge proved untrustworthy — so it sat outside the comparable
tables. It has now been **re-run on the fixed v2 meter** (`2026-07-gsd-v2-rep0.md`),
same model, effort, and workload as the other arms. The result moves it *into* the
scoreboard above, and corrects the record:

- **Functionally it holds up.** Oracle pass 1.00 / 0.80 / 1.00 — one probe short at
  WM2, full recovery at WM3, zero regression on clean state. The same *shape* as the
  ADD lean branch, and on par with spec-kit / vanilla.
- **It is cheap.** $3.01 total / 3.70M tokens — the cheapest arm in the same-day
  run, below spec-kit ($4.20) and 3.0× below ADD ($9.11). GSD's planning-doc weight
  did not translate into a cost penalty at this workload size.
- **The old v1 "WM2 fidelity 0.50" does not reproduce as a functional miss.** On v2
  the deterministic oracle passes WM2 at 0.80 (one probe), not a collapse — the 0.50
  was an unpinned-judge artifact of the retired meter. This correction cuts in GSD's
  favor, and is stated as such.

One honest wrinkle worth showing rather than hiding: the v2 run's *deprecated* LLM
judge scored GSD's WM2 and WM3 fidelity at **0.00 despite the oracle passing** (WM3
oracle 1.00 = every probe green). A working app scoring judge-0.00 is implausible —
it is the same judge-untrustworthiness this appendix opened with, reproduced sharply
here (the single-float judge parse-fails to 0.00 as the evolved app grows). It is
exactly *why* every cross-arm fidelity claim in this appendix rests on the
deterministic `oracle_pass_rate`, never the judge. GSD's real signal is the oracle
line: 1.00 / 0.80 / 1.00.

## How to choose (the same advice ADD's stages encode)

| situation | measured recommendation |
|---|---|
| throwaway prototype, demo, spike | vanilla / spec-kit / GSD — ≈3–4.6× cheaper, floors don't bind |
| spec evolves, data persists, users exist | ADD — the only flow whose trust floors are enforced rather than assumed, at $3.17/WM1 and falling |
| hostile or ambiguous change requests | ADD — frozen contract + tamper tripwire make the honest path the only green path |
| compliance / security surface | ADD — security findings HARD-STOP mechanically; no other measured flow has an un-forceable floor |

Method notes: pinned model + effort, self-carried permissions, per-run archived
transcripts and records (`benchmark/runs/`), oracle probes derived from each
track's own prompts, controls validated both ways before scoring. Re-run it
yourself: `python3 -m benchmark.run run --arm <add|spec-kit|vanilla|gsd> --wm 1`.
