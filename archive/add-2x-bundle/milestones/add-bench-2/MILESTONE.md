# MILESTONE: Add Bench 2

goal: benchmark ADD on the terrain its machinery actually defends: interruption-resume, ambiguity surfacing, regression storms, cold-start maintenance, and security bait — measuring what WM1-6 never triggered
rationale: sub-milestone (human-confirmed 2026-07-08, all 4 tracks): WM1-6 prompts were complete, unambiguous, single-session, regression-free — terrain where ceremony is pure overhead; both discrimination hypotheses refuted there. These tracks stress what ADD structurally has and competitors lack.
stage: mvp · status: active · created: 2026-07-08T08:41:06+00:00
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
- **track** — one adversity dimension with its own harness mode + hidden oracle; arms/judging identical to add-bench.
- **surface-vs-guess** — ambiguity scoring: conflict surfaced (asked/flagged) > guessed right > guessed wrong; guessing right by luck is NOT surfacing.

## Shared / risky contracts (freeze these first)
- oracle-isolation (hidden oracles never visible to arms; check_isolation extended per track) -> binds all tasks
- kill-is-random (interruption points sampled, recorded in the run record, identical distribution across arms) -> bench-interrupt-resume
- bait-is-symmetric (planted conflicts/regression baits/vulns live in the PROMPT, identical bytes for every arm) -> binds all tasks
- security-bait-never-ships (harness quarantines vuln workspaces; findings scored, never released) -> bench-security-bait

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] bench-interrupt-resume   depends-on: none — kill mid-milestone at sampled points, resume fresh-context on "continue"; metrics: recovery success, duplicated work, post-resume fidelity (reuses wm4 workload)
- [ ] bench-ambiguity          depends-on: none — prompts with a planted contradiction, silent gap, misreading trap; surface-vs-guess scoring
- [ ] bench-regression-storm   depends-on: none — 6-8 change requests each baiting 1-2 breaks of earlier behavior; metric: regressions shipped per change
- [ ] bench-coldstart-maint    depends-on: none — fresh agent gets 1 bug + 1 small feature on the built 6-WM codebase; cost + correctness of the cold task
- [ ] bench-security-bait      depends-on: none — a milestone whose easiest implementation embeds a real vuln the prompt subtly invites; binary caught/shipped oracle

## Exit criteria (observable; map each to the task that delivers it)
- [ ] each track runs both arms (add · spec-kit) headlessly and writes schema-valid records with track-specific metrics        (← all tracks)
- [ ] interruption: n=3 kill points per arm; recovery + duplicated-work measured        (← bench-interrupt-resume)
- [ ] ambiguity: surfaced/guessed-wrong/guessed-right recorded per planted item        (← bench-ambiguity)
- [ ] regression storm: regressions-shipped per change of record for both arms        (← bench-regression-storm)
- [ ] verdicts land in BENCHMARK.md with the same honesty bar (refuted is a result)        (← all tracks)

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
