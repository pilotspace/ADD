# MILESTONE: Persona GEPA loop — routes that learn from run outcomes

goal: The persona's routing rules EVOLVE from evidence — every gated task records a route-outcome trace (route taken · turns · heals · gate result), and at fold-time the PM persona reflects on the traces GEPA-style, proposing route-rule deltas (keep what cut turns without gate regressions, prune rules that never fired) that the human folds into the persona file — the method literally improves per project.
rationale: bucket sub-milestone — queued follow-up to thin-engine-loop (which records routes but does not learn from them) and strategy-intake (which gives personas the PM surface). Mutation rails: personas evolve ONLY via the existing fold seam (human-confirmed, never-clobber, persona_clobber_forbidden); frozen contracts, tests, SKILL core, and the security HARD-STOP are never persona-editable.
stage: mvp · status: queued · created: 2026-07-16T09:46:41+00:00
release: pending
depends-on: thin-engine-loop
extends: strategy-intake, self-improving-loop, dynamic-personas

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the READ side of the M1 route-trace stream (`deltas` route scoreboard, per-lane) + the
     GEPA reflection beat in loop.md (keep/prune/propose via delta-append; human folds into
     the persona file).
Out: per-PERSONA rollup (no board has trace volume yet — build on evidence) · automatic
     rule mutation of any kind (the human fold IS the design) · milestone reactivation.

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): add.py `_append_route_trace` (writer, M1) · `cmd_deltas` ·
  skill/add/loop.md · .add/traces/route-outcomes.jsonl
Anchors: `_route_scoreboard` / `_print_route_scoreboard` (add.py, before cmd_deltas)
Honors (conventions): <PROJECT.md · CONVENTIONS.md · SEAMS.md rules every task honors>
Issues/Risks (shared): <traps in the shared code that feed each task's §1 expectations>

> Gather this ONCE per milestone (the drafting step in `scope.md`). Each task's `specify`
> PROJECTS its §1 expectations from here + the specific request — light, not re-grounded per task.

## Shared decisions & glossary deltas   (living — every task must honor these)
- <cross-cutting rule, named from GLOSSARY.md>

## Shared / risky contracts (freeze these first)
- <contract name> -> owning task <slug>

## Tasks (breadth-first decomposition; detail lives in each PLAN.md)
- [x] route-scoreboard   depends-on: none — deltas rolls route-outcomes.jsonl up per lane +
      GEPA nudge; loop.md gains the reflection beat (`ea3b5bf2`, corpus 2451 green)
- [ ] persona-rollup     depends-on: route-scoreboard — per-persona rollup once real traces
      accumulate (deferred: evidence-first)

## Exit criteria (observable; map each to the task that delivers it)
- [ ] User can read a per-lane route scoreboard from `add.py deltas` on any board with
      recorded gates, and it is silent on a board with none        (← route-scoreboard)
- [ ] User can follow loop.md's GEPA beat: reflect on the scoreboard, propose a route-rule
      delta via `add.py delta-append`, and fold it into `.add/personas/` by hand — with the
      engine never editing a persona        (← route-scoreboard)

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
