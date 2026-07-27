# MILESTONE: Direction velocity — cut the pre-code phase, persist cross-task context

goal: cut ADD's direction phase below 38.7% of cost and 31 minutes of wall-clock without losing requirement coverage, and make cross-task invariants inheritable through the task graph
rationale: sub-milestone — measured, not suspected. The pay1–4 campaign (n=1, 8 runs, 2026-07-26) folded ADD's own transcripts into a call-stack flamegraph: direction is 38.7% of billed context (22.9M, ~$6.88) and 45.7% of wall-clock (31.0 of 67.8 min). Only 6.8 of those 31 minutes is reasoning; the rest is structure — 7.3m of strictly serial Reads, 4.9m building PLAN.md through 45 successive Edits, 3.9m of harness bookkeeping. Across 209 direction turns, ZERO emitted more than one tool call. The engine itself is 1.1%, so trimming verbs or output buys nothing.
stage: mvp · status: active · created: 2026-07-27T03:27:28+00:00
relations: relates-to: engine-output-trim, add-bench-v2

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/PLAN.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  benchmark instrument honesty (the comparison arm + meter provenance) · direction-phase velocity (read batching, a one-shot bundle write) · cross-task context persistence (published invariants, graph inheritance, DESIGN.md at build) · edge-case rigor in §4 · an algorithm-dense workload to prove coverage
Out: the frozen-contract semantics themselves · the security HARD-STOP · gate outcomes · `tests_weakened`/`assertions_lost` definitions · any relaxation of an existing refusal · n=3 campaigns (n=1 + mechanical proxies is the evidence tier this milestone buys)

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): `add-method/tooling/add.py` — `cmd_new_task` :888 (`depends_on` :912) · `cmd_freeze` :1178 (`unflagged_freeze` :1215) · `cmd_advance` `--fill` :7153 ("ONE section for ONE crossing") · `_FLAG_LABEL_RE` :5826 · `add-method/tooling/templates/PLAN.md.tmpl` §3/§4 · `benchmark/arms/*.toml` · `benchmark/score.py` `_add_tamper_metrics` · `benchmark/pilot.py` / `report.py` `--family` choices
Anchors: the engine's four twins (`.add/tooling/add.py` · `add-method/tooling/add.py` · `add-method/.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`) + `engine_pin.py` `ENGINE_MD5`/`ENGINE_PKG_MD5` · four template twins · three skill trees (`.claude/skills/add/` · `add-method/skill/add/` · `add-method/src/add_method/_bundled/skill/add/`)
Honors (conventions): four-mirror-trees + engine-pin-3-mandatory-parts · additive-surface-byte-invisible · §5-scope-frozen-at-tests→build · dogfood-at-own-gate · close-gap-before-gate · never weaken a test or edit a frozen contract to pass a build
Issues/Risks (shared): hand-mirrored twins have no parity test (the lock-reclaim class) · a conditional skip breaks `test_ci_tooling_mirror_gap`'s pinned count · `--fill`'s all-or-nothing restore is the model for `draft`, and a failed draft costs a full re-compose · engine running a test suite is a NEW responsibility and the hardest part of the all-or-nothing guarantee

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Measure on mechanical proxies, not cost.** Direction turns ran 41/36/85/47 across four milestones — the within-arm spread exceeds the effect being chased, so n=1 cost deltas cannot resolve a 20% improvement. Every gate's PASS condition is a near-deterministic count (parallel turns, PLAN.md writes, direction turns); cost and wall-clock are recorded as evidence, never as the pass condition.
- **One change measured per gate.** Landing several changes then measuring teaches nothing about which worked. Task order IS the experiment design.
- **Instrument honesty precedes any claim.** The arm labelled `spec-kit` is `prompt_wrapper = "raw"` and produced zero `specs/` artifacts in every automated run; until that is fixed or renamed, no comparative claim is publishable.
- **Persistence lands AFTER velocity.** Published invariants and edge rows ADD to direction. Landing them before the one-shot write would inflate the exact phase this milestone shrinks and destroy attribution.
- **The engine never enforces what it cannot observe.** `add.py` cannot see editor writes, so a "≤N PLAN.md writes" rule is guide prose measured from the transcript — never a claimed engine guard. (`turn_ceiling` is the cautionary precedent: declared in every arm, asserted equal by `test_arms.py`, read by nothing.)

## Shared / risky contracts (freeze these first)
- `add.py draft <slug> --from <bundle> --run-red --freeze` — all-or-nothing bundle write -> owning task `direction-one-shot`
- §3 `Invariants (published)` block + `invariant_without_proof` refusal -> owning task `invariants-publish`

## Tasks (breadth-first decomposition; detail lives in each PLAN.md)
- [ ] arm-honesty        depends-on: none                — the comparison arm runs its own method or is renamed to what it is; no arm claims a method it never invokes
- [ ] meter-provenance   depends-on: none                — every scored record carries the meter version that produced it; close the last `isinstance(body, list)` oracle surface
- [ ] read-batching      depends-on: none                — direction issues independent reads/greps in ONE turn; harness bookkeeping (TaskCreate/sleep) leaves the benchmark path
- [ ] direction-one-shot depends-on: read-batching       — `add.py draft` writes §1+§3+§4 and freezes in one call, all-or-nothing; per-section `--fill` retired for direction
- [ ] invariants-publish depends-on: direction-one-shot  — §3 publishes invariants, each citing the test that proves it; freeze refuses one without a proving test
- [ ] invariant-inherit  depends-on: invariants-publish  — `new-task --depends-on` prints ancestors' invariants (a view, no new store)
- [ ] design-at-build    depends-on: invariants-publish  — DESIGN.md is written during build; a node that published invariants cannot gate without it
- [ ] edge-rigor         depends-on: invariants-publish  — §4 rows carry [GATED]/[edge]; the gate refuses an edge row that is neither green nor reasoned
- [ ] algo-workload      depends-on: edge-rigor          — an algorithm-dense workload exists and has been run head-to-head

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A reader of any benchmark comparison can see what the comparison arm actually does, from the arm's own name and config        (← arm-honesty)
- [ ] A scored record states which meter version produced it, so a stale number is visible without re-reading git history            (← meter-provenance)
- [ ] A direction phase issues independent reads in a single turn — the parallel-turn count is greater than zero                     (← read-batching)
- [ ] A task's direction bundle is written by ONE engine call, and that call refuses to freeze unless the suite ran red              (← direction-one-shot)
- [ ] A task cannot freeze while publishing an invariant that no test proves                                                          (← invariants-publish)
- [ ] Creating a task with `--depends-on` shows the invariants it inherits, without copying them into a second store                 (← invariant-inherit)
- [ ] A node that published invariants cannot record a gate without its DESIGN.md                                                     (← design-at-build)
- [ ] A gate refuses an enumerated edge case that is neither green nor carries a stated reason                                        (← edge-rigor)
- [ ] A workload whose requirements are genuinely algorithmic exists and has produced a head-to-head record                          (← algo-workload)

## Strategy   (AI-drafted WITH the human — the optimized task plan; SOFT/advisory like a task's Build-strategy)
- Approach (sequencing): **instrument-first, then cheapest-attributable-first.** arm-honesty and meter-provenance cost ~nothing and unblock every downstream claim. read-batching is a guide/wrapper change with no engine risk and no re-freeze — the highest payoff-to-risk item in the milestone, and it must be measured BEFORE direction-one-shot or the two effects are inseparable. The persistence wave lands last because it pushes direction back up.
- Freeze-first: `add.py draft`'s signature (direction-one-shot) — invariants-publish, design-at-build and edge-rigor all write through the bundle it owns.
- Waves (parallel): W1 = arm-honesty · meter-provenance · read-batching (independent, no shared files). W2 = direction-one-shot alone (measured in isolation). W3 = invariant-inherit · design-at-build · edge-rigor behind invariants-publish's frozen §3. W4 = algo-workload.
- Tradeoffs weighed: (a) landing the DESIGN.md persistence first — rejected: it inflates direction and destroys the attribution the whole milestone rests on. (b) One combined "direction rewrite" task — rejected: batching and the one-shot verb have different risk profiles and one is free, so bundling them would spend engine risk to buy a wrapper-level win. (c) Gating on total cost — rejected: measured within-arm variance (41/36/85/47 direction turns) exceeds the effect. (d) n=3 campaigns — deferred: ~$65 and still under-powered; mechanical proxies resolve the same questions at n=1.

## Close — ship review   (AI fills when every task is done)

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">
- benchmark : <arms / score / workload — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — the ordered steps to ship this milestone; engine records, human gate)
- [ ] open a PR carrying the already-green meter work (syntax-agnostic `tests_weakened` · the `pay` track · the family-choice fix) — 3 commits on `fix/tamper-syntax-agnostic`, suite 493 green
- [ ] land W1, re-run pay1–4, record Gate A against the 2026-07-26 baseline
- [ ] land W2, re-run pay1–4, record Gate B
- [ ] land W3 + W4, re-run both tracks, record Gate C — coverage ≥ 0.982 must not regress
- [ ] the human reviews the three gate records and cuts the release
