# MILESTONE: Add Bench V2

goal: measure ADD's actual value proposition — regression safety, gaming resistance, resumability, direction-mining, security floors, traceability — on the pinned meter, deterministically scored, and report cost-per-TRUSTED-feature alongside v1's raw cost; if a competing flow also holds the floors, report that honestly
rationale: sub-milestone — v1 (add-bench) only measured simple-greenfield WM1 cost, spec-kit's optimal case (~3.3× cheaper, confirmed fair, `benchmark/results/2026-07-sonnet-campaign.md`); none of the trust dimensions ADD's ceremony pays for have ever been run on the fixed meter, and the v1 LLM fidelity judge is proven untrustworthy. Design confirmed by human 2026-07-10 (`benchmark/v2/DESIGN.md`, commit 26b2084).
stage: mvp · status: active · created: 2026-07-10T02:03:19+00:00
release: 1.18.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  meter fixes (deterministic fidelity probes · regression oracle · mechanical tamper detector · judge pin) → WV1 longitudinal workload + campaign → WV2 hostile-change workload + campaign → the two-axis scoring/report (cost axis + trust axis, headline = cost-per-trusted-feature). Arms: add · spec-kit · vanilla.
Out: WV3–WV6 (interrupted-session · underspecified · security-floor · traceability) — GATED on WV1+WV2 results, intaken as follow-on tasks only if the first campaigns justify the spend; plan-mode/gsd arms; any change that tilts scoring toward a predetermined ADD win (the honest-outcome clause in DESIGN.md binds every task); engine changes (this milestone measures, it does not add levers).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Pinned meter is law**: every run `claude -p --model claude-sonnet-5 --effort medium --output-format stream-json --verbose --disable-slash-commands --strict-mcp-config` (pin `4d0c52e`); a number from any other meter is VOID.
- **Deterministic-first scoring**: no LLM float is ever a primary metric; the pinned LLM judge survives only as a secondary annotator.
- **Honest-outcome clause** (from DESIGN.md): if spec-kit/vanilla also hold a trust floor, the report says so — a rigged win gets retracted, a fair loss is information.
- **n≥3 reps** for any headline claim; single reps are labeled n=1 and never headline.
- **Spend is human-gated per campaign**: harness code builds freely; every paid agent-run campaign gets an explicit human go (WV1 ≈ $60–90 · WV2 ≈ $25–40).
- Run all campaigns via `benchmark.pilot run-all` (run.py bypasses resolve_setup_steps — todo #27).
- **Trusted-flag floor (2026-07-10, human fairness challenge)**: a feature is `trusted` only if probes pass AND regression = 0 AND tests_weakened = 0 AND **the arm's own test suite exists and is green** — a testless arm can never score trusted (closes the tests_weakened loophole). Trust axis reports as a vector, never one collapsed float.
- **Control arm (2026-07-10, human directive)**: campaigns also run `add-main` — ADD installed from the MAIN branch — so branch-engine changes are controlled against the released flow, not just against other tools.

## Shared / risky contracts (freeze these first)
- probe-suite format (per-WM deterministic fidelity oracle: endpoint × payload × expected) -> owning task v2-meter-fixes
- per-WM record schema v2 (adds regression_rate · tests_weakened · trusted flag) -> owning task v2-meter-fixes

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] v2-meter-fixes    depends-on: none            — deterministic probe suites + regression oracle + tamper detector + judge pin (#28-judge); retire the LLM fidelity float as primary   (gate PASS `02d5cfd`)
- [x] v2-wv1-longitudinal depends-on: v2-meter-fixes — WM1→WM2→WM3 same-workspace workload (prompts + probe suites) + the 3-arm n=3 campaign (human spend gate before runs)   (gate PASS `ba1e621` — rep0 only; human redirected reps 1–2 spend to WV2, 2026-07-10)
- [x] v2-wv2-hostile-change depends-on: v2-meter-fixes — contradicting change-request workload with a test-weakening temptation + campaign (human spend gate before runs)   (gate PASS `aa19ea4`)
- [x] v2-scoring-report depends-on: v2-wv1-longitudinal, v2-wv2-hostile-change — two-axis scorer + cost-per-trusted-feature headline + campaign report in benchmark/results/   (gate PASS `adb12c2`)

## Exit criteria (observable; map each to the task that delivers it)
- [x] A WM's fidelity is scored by a deterministic probe suite (LLM float demoted to secondary), and re-running earlier probes yields a mechanical regression_rate        (← v2-meter-fixes; `compute_oracle_pass_rate` + `compute_regression_rate_v2` live in every rep0 record)
- [x] tests_weakened is computed by mechanical diff of snapshotted test files — no judge        (← v2-meter-fixes; `tamper.py` fingerprint diff + trust.py's rename-tolerant adjusted verdict on top)
- [x] WV1 campaign complete on the pinned meter, regression_rate reported per WM for add/add-main/spec-kit/vanilla        (← v2-wv1-longitudinal; **human-accepted at n=1**: the n≥3 clause was consciously traded for WV2 spend by the human 2026-07-10 — rep0 is labeled n=1 everywhere and never headlines a claim, per the n≥3 shared decision's own labeling rule)
- [x] WV2 campaign complete: each arm's response to the contradicting change request scored via tests_weakened + untouched-endpoint regression        (← v2-wv2-hostile-change; n=1, same human-accepted labeling; verdict: NO ARM GAMED)
- [x] One report prints BOTH axes — v1-style cost-per-feature AND cost-per-trusted-feature — with the honest-outcome clause applied (any floor spec-kit/vanilla holds is stated)        (← v2-scoring-report; rendered on both real rep0 archives at the gate: spec-kit holds every floor and is cheapest on BOTH axes — stated in the report and both ledgers)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : untouched (milestone measured, added no engine levers — per Scope Out)
- skill   : untouched
- book    : untouched
- benchmark (this milestone's own domain): score.py oracle/regression-v2 · tamper.py fingerprint diff · trust.py trust vector · report.py two-axis + CLI · runner PINNED_MODEL + permission self-carry · family seam (wm|hv) end-to-end · hv1–hv3 workload track · wm2 survivors disjoint 2028 windows · 2 rep0 ledgers in benchmark/results/ · DESIGN.md → EXECUTED

### Cross-task evidence   (one row per task)
- v2-meter-fixes : gate=PASS `02d5cfd` · tests=154 green · residue=none (tests_weakened limits disclosed in-task)
- v2-wv1-longitudinal : gate=PASS `ba1e621` · tests=full suite green at close · residue=n=1 (human-accepted, reps redirected to WV2); add wm2 pass 0.80 is a REAL branch finding, ledgered
- v2-wv2-hostile-change : gate=PASS `aa19ea4` · tests=12 family pins + suite green · residue=n=1 (human-accepted); NO ARM GAMED — hypothesis fails at this temptation strength, ledgered honestly
- v2-scoring-report : gate=PASS `adb12c2` · tests=190 green · residue=none (honest-outcome tie line unexercised by real archives; proven live on a tie fixture)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row (criteria 1–2 ← v2-meter-fixes row; 3 ← v2-wv1-longitudinal row; 4 ← v2-wv2-hostile-change row; 5 ← v2-scoring-report row + the two rendered reports)
- goal: measure ADD's actual value proposition on the pinned meter, deterministically scored, cost-per-TRUSTED-feature beside raw cost, honest about competing flows — PROVEN by the two-axis report rendered on both rep0 archives stating spec-kit holds every trust floor at the lowest cost on both axes (WV1 $1.14 vs add $4.65 vs add-main $13.94 per trusted feature) while the branch holds −27% cost vs add-main at equal trust; the honest-outcome clause was applied at full strength (a fair loss is information).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [x] fold the WV1/WV2 campaign results into `benchmark/results/` alongside the 2026-07 ledger (2026-07-wv1-rep0.md · 2026-07-wv2-rep0.md); update DESIGN.md status DRAFT → EXECUTED (done at close)
- [ ] open/extend the `feat/add-bench-scaffold` PR with the v2 harness + results; the human reviews + merges (push authorized 2026-07-10 — in flight)
- [ ] decide WV3–WV6 (new intake) from the WV1+WV2 evidence — human call
