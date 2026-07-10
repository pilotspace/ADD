# MILESTONE: Add Bench V2

goal: measure ADD's actual value proposition — regression safety, gaming resistance, resumability, direction-mining, security floors, traceability — on the pinned meter, deterministically scored, and report cost-per-TRUSTED-feature alongside v1's raw cost; if a competing flow also holds the floors, report that honestly
rationale: sub-milestone — v1 (add-bench) only measured simple-greenfield WM1 cost, spec-kit's optimal case (~3.3× cheaper, confirmed fair, `benchmark/results/2026-07-sonnet-campaign.md`); none of the trust dimensions ADD's ceremony pays for have ever been run on the fixed meter, and the v1 LLM fidelity judge is proven untrustworthy. Design confirmed by human 2026-07-10 (`benchmark/v2/DESIGN.md`, commit 26b2084).
stage: mvp · status: active · created: 2026-07-10T02:03:19+00:00
release: pending

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

## Shared / risky contracts (freeze these first)
- probe-suite format (per-WM deterministic fidelity oracle: endpoint × payload × expected) -> owning task v2-meter-fixes
- per-WM record schema v2 (adds regression_rate · tests_weakened · trusted flag) -> owning task v2-meter-fixes

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] v2-meter-fixes    depends-on: none            — deterministic probe suites + regression oracle + tamper detector + judge pin (#28-judge); retire the LLM fidelity float as primary
- [ ] v2-wv1-longitudinal depends-on: v2-meter-fixes — WM1→WM2→WM3 same-workspace workload (prompts + probe suites) + the 3-arm n=3 campaign (human spend gate before runs)
- [ ] v2-wv2-hostile-change depends-on: v2-meter-fixes — contradicting change-request workload with a test-weakening temptation + campaign (human spend gate before runs)
- [ ] v2-scoring-report depends-on: v2-wv1-longitudinal, v2-wv2-hostile-change — two-axis scorer + cost-per-trusted-feature headline + campaign report in benchmark/results/

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A WM's fidelity is scored by a deterministic probe suite (LLM float demoted to secondary), and re-running earlier probes yields a mechanical regression_rate        (← v2-meter-fixes)
- [ ] tests_weakened is computed by mechanical diff of snapshotted test files — no judge        (← v2-meter-fixes)
- [ ] WV1 campaign complete on the pinned meter, n≥3 per arm, regression_rate reported per WM for add/spec-kit/vanilla        (← v2-wv1-longitudinal)
- [ ] WV2 campaign complete: each arm's response to the contradicting change request scored via tests_weakened + untouched-endpoint regression        (← v2-wv2-hostile-change)
- [ ] One report prints BOTH axes — v1-style cost-per-feature AND cost-per-trusted-feature — with the honest-outcome clause applied (any floor spec-kit/vanilla holds is stated)        (← v2-scoring-report)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] fold the WV1/WV2 campaign results into `benchmark/results/` alongside the 2026-07 ledger; update DESIGN.md status DRAFT → EXECUTED
- [ ] open/extend the `feat/add-bench-scaffold` PR with the v2 harness + results; the human reviews + merges
- [ ] decide WV3–WV6 (new intake) from the WV1+WV2 evidence — human call
