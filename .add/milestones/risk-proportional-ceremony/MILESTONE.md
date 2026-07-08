# MILESTONE: Risk Proportional Ceremony

goal: cut ADD's big-milestone cost premium (1.8x dollars / 2x wall-clock vs spec-kit) toward ~1.3x by scaling ceremony to task risk — never by lowering the trust floor (frozen contract, red suite, recorded gate hold in every lane)
rationale: sub-milestone (user-signaled after the add-bench WM4-6 verdict): the benchmark proved the premium is turn fragmentation + suite-run churn + done-phase ceremony on big milestones — not the spec phases (~3%) — and that ceremony pays only where risk lives; scale it to risk.
stage: mvp · status: active · created: 2026-07-08T08:28:21+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  <what this milestone delivers>
Out: <explicitly deferred — the anti-scope-creep list>

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **lane** — a ceremony depth (full | fast); changes suite-run cadence + observe timing, NEVER which gates exist.
- **suite-run census** — count of full-suite invocations per task, derivable from the run transcript (like engine_calls).

## Shared / risky contracts (freeze these first)
- trust-floor-frozen (frozen contract + red suite + recorded gate in EVERY lane) -> binds all tasks
- lane-is-a-suggestion (engine scores + prints; human/agent declares; never self-elects fast for security/data/architecture) -> lane-suggest-at-intake
- deferred-observe-keeps-deltas (per-task lessons buffer to milestone close, attribution + deltas.md grammar intact) -> defer-observe-to-close
- census-countable (full-suite runs countable from transcript) -> bench-premium-recheck

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] tiny-plan-small-scope       depends-on: none — `new-milestone --tiny`: one compact plan (goal + ≤5-line task list + exit checks), member tasks default to the fast lane, observe deferred to close — the whole small-scope flow in ONE approval
- [ ] lane-suggest-at-intake      depends-on: none — engine scores a new task's risk (sensitivity + scope size) and SUGGESTS the fast lane in new-task output (moment-of-use, adoption-measurable)
- [ ] three-canonical-suite-runs  depends-on: none — loop teaches exactly red (tests) · green (build) · gate (verify) full-suite runs; targeted tests between (benchmark: 13-16 runs/WM vs 3 needed)
- [ ] defer-observe-to-close      depends-on: none — per-task done/observe ceremony (16% of turns, zero artifact yield on wm4/wm5) batches at milestone close
- [ ] turn-batching-hints         depends-on: none — footer/guide hints that batch engine ops; fragmentation (~112 extra turns on wm4) is the #1 cost
- [ ] bench-premium-recheck       depends-on: lane-suggest-at-intake, three-canonical-suite-runs, defer-observe-to-close, turn-batching-hints — rerun one big-WM head-to-head on the new defaults; premium + floor of record

## Exit criteria (observable; map each to the task that delivers it)
- [ ] big-WM cost premium vs spec-kit ≤1.4x in cost_usd on the recheck (was 3.1x on wm4)        (← bench-premium-recheck)
- [ ] fidelity floor ≥0.97 and regression_rate 0.0 on the recheck        (← bench-premium-recheck)
- [ ] full-suite runs per task ≤4 on the recheck transcripts        (← three-canonical-suite-runs)
- [ ] no gate/tripwire weakened — tamper-tripwire + engine full suite green        (← all)
- [ ] fast-lane suggestion adopted ≥1 time in the recheck run        (← lane-suggest-at-intake)
- [x] a WM1-6-scale milestone completes under --tiny with ONE plan approval and the full trust floor        (← tiny-plan-small-scope; engine capability shipped + 8/8 suite — the recheck run exercises it end-to-end)

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
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
