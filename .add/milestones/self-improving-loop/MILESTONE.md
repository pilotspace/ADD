# MILESTONE: The observe loop optimized for self-improvement across the 5 domains

goal: the observe→deltas→fold→compact loop actually converges — persona-targeted lessons grow the NEW schema sections, the engine surfaces compaction debt + the carried backlog instead of letting them rot silently, and the self-improving loop is readable as ONE surface across the 5 domains
rationale: sub-milestone — Tin 2026-07-07 'fix all then review ADD flow to make sure ADD are optimized for self-improving SKILL via 5 Domains - 8 step'; investigation found: fold's persona allowlist frozen at the pre-1.16.1 schema (Anti-patterns/Abilities unroutable) · compaction last rolled at fv20 (now fv64; 303 folded bullets live) · 88 carried deltas with no resurfacing trigger · persona learning loop used once ever
stage: mvp · status: active · created: 2026-07-06T17:39:09+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  fold routes `anti-pattern`/`ability` persona hints · observe/agents recommend persona-targeted lessons · status surfaces compaction tail + carried count · release-report lists carried · loop.md gathers carried · a self-improving-loop review with the guide-file decision
Out: auto-compaction (write stays human) · delta dedup tooling · per-competency CONVENTIONS split · milestone reactivation

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
- [x] A `· persona:<slug> · anti-pattern|ability` lesson folds into that section — test_fold_persona_sections 7/7        (← fold-persona-sections)
- [x] `status` shows the foundation tail + carried backlog (live: carried 88 · compaction 221, fv20→fv64); `release-report` lists carried        (← loop-surfacing-nudges)
- [x] The self-improving loop is one navigable surface — skill/add/self-improve.md (1.4KB map, pointed from 7-observe)        (← self-improving-guide)

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
