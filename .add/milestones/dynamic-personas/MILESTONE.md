# MILESTONE: Dynamic teacher-grade personas routed by flow:

goal: the persona system's value proposition — DYNAMIC per-domain personas at teacher-grade depth (distilled from `.add/personas-teacher/`) — is actually wired: every drafted persona carries `flow:` routing and every consuming surface (roster agents · design.md · advisor.md) selects by it
rationale: sub-milestone — investigation (2026-07-06, Tin: "correct ADD flow with personas and design.md flow" · "personas for agents team" · "we offer dynamic personas but high performance as personas_teacher") found the 1.16.1 `flow:` + `## Abilities` schema landed in template+docs with ZERO consumers: nothing writes flow: (dogfood 0/6, add-persona drafts the stale schema) and nothing reads it (all 5 roster agents, design.md, advisor.md select by archetype prose) — the routing mechanism is dead wiring
stage: mvp · status: active · created: 2026-07-06T16:50:24+00:00
release: 1.17.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  add-persona drafts to the CURRENT schema (flow:/Abilities/source:, teacher-distilled) and returns flow in its verdict · the 4 other roster agents select flow:-first (archetype as tie-break) · design.md's persona evidence checklist routes through `flow: design` · advisor.md's <persona> block prefers flow-matched personas · the 6 dogfood personas gain `flow:` · a routing guard test
Out: engine-checked flow: validation (stays presence-based/RECOMMENDED) · new personas · any gate-semantics change (personas stay advisory, never lower a gate) · teacher-library content changes

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- <cross-cutting rule, named from GLOSSARY.md>

## Shared / risky contracts (freeze these first)
- <contract name> -> owning task <slug>

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] <slug>   depends-on: none     — <one line>
- [ ] <slug>   depends-on: <slug>   — <one line>

## Exit criteria (observable; map each to the task that delivers it)
- [x] A dynamically drafted persona is born routable — flow:/source:/## Abilities in the draft, flow in the verdict, and every consuming surface (5 roster agents ×3 trees · design.md · advisor.md ×3 trees · 6/6 dogfood personas) selects by flow:, guarded by test_persona_flow_routing (10 green)        (← persona-flow-routing)
- [x] A loaded persona is current-schema, invariant-true, and command-anchored (## Abilities + ## Anti-patterns on all 6; 0 rotted literals), and selection is frontmatter-first (~5KB, not 25KB) with teacher routing by division dir        (← persona-load-performance)

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
