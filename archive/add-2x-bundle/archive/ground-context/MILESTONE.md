# MILESTONE: Ground context — gather the whole working folder, efficiently

goal: A task's ground phase gathers the full task-relevant working-folder context — not only code symbols but docs/textbase, TODOs, config/manifests, and data/fixtures — and the `0-ground.md` guide directs the AI to gather it efficiently (prefer a small-model subagent / fast index / skim for the broad sweep) and task-specifically (deepen on what THIS task actually needs, never lock a code-only shallow first pass).
rationale: sub-milestone — a slice of the just-shipped ground theme, too big for one task. Extends the §0 GROUND gather additively (new context categories + guide methodology); does NOT change the frozen §0 anchors-keyed measure (so not a change-request). Risk:medium — guide/template prose across ×3/×4 trees; the engine measure stays untouched. Shape confirmed by the human: gather docs + todos + config + data, and hint a subagent/fast-index/skim + task-specific deepening.
stage: mvp · status: active · created: 2026-06-11

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- **Broaden the §0 GROUND gather** — the `## 0 · GROUND` template + `0-ground.md` guide gather the working-folder context the task touches: code (existing **Touches**) **+ docs/textbase** (README, `*.md`, design notes) **+ TODOs/task markers** (`TODO.md`, `FIXME`/`TODO`/`HACK` comments, task lists) **+ config/manifests** (configs, `.env.example`, `pyproject`/`package`, CI descriptors) **+ data/fixtures** (sample data, fixtures, schemas). Task-specific delta only — still defers to PROJECT.md / CONVENTIONS.md for architecture; never re-runs the setup brownfield scan. (→ ground-context-sources)
- **The gather-method hint** — `0-ground.md` adds an instruction to gather *efficiently*: **prefer a small-model subagent / fast index / skim** for the broad sweep (anti-context-rot — offload to a cheap context, return a compact map), and to **deepen task-specifically** (follow what THIS task needs deeper into the codebase, never lock a shallow first pass). A recommendation, never an engine-spawned action. (→ ground-gather-hint)
- Both synced across canonical · dogfood · bundled skill trees (×3), and the book/glossary where they describe the gather (×4 if touched).

Out (deferred — the anti-scope-creep list):
- Changing the grounding **measure** (`_grounded_state` keys on the §0 "Anchors the contract cites:" line) — stays as-is; this milestone adds gather *content* + *method*, not a new measure/gate. (measure-not-block, unchanged)
- A **mechanical gate** that blocks freeze until every context category is gathered — no; the gather is guidance, not a hard per-category checklist count.
- **Engine-spawning** a subagent — the hint RECOMMENDS one; `add.py` never spawns it (the method is tool-agnostic; the orchestrating agent decides). The engine stays prose/measure only (no add.py change expected → pin unchanged).
- Re-running the one-time **setup brownfield scan** — separate concern; ground gathers the task-specific delta.
- A heavy GSD-style RESEARCH.md / PATTERNS.md, or indexing the WHOLE repo — rejected for the lean, task-relevant §0 map.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **working-folder context** — what ground gathers beyond code: docs/textbase · TODOs · config/manifests · data/fixtures, scoped to what the task touches. (extends the `grounding map / anchors` term)
- **gather-method hint** — `0-ground.md` recommends a fast small-model subagent / index / skim for the broad sweep + task-specific deepening; a recommendation, never an engine-spawned action (tool-agnostic).
- **§0 stays lean** — enrich the GUIDE to gather the categories; keep the §0 artifact light (do NOT add a rigid per-category field block that bloats every TASK.md).

## Shared / risky contracts (freeze these first)
- **§0 GROUND template shape** — how the broadened context is recorded (a light addition to **Touches** vs a new field set) -> owning task `ground-context-sources`; the second task's hint refers to it. Forward decision resolved at that task's §3 freeze (lean addition preferred; human approves at the freeze).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] ground-context-sources   depends-on: none                    — broaden the §0 GROUND gather + `0-ground.md` to the working-folder context (code + docs/textbase + todos + config/manifests + data/fixtures); §0 template ×3, guide ×3/×4 synced. First ever task to START at `ground` (closes the zero-lived-run ceiling).
- [x] ground-gather-hint       depends-on: ground-context-sources  — the gather-method hint in `0-ground.md`: prefer a small-model subagent / fast index / skim for the broad sweep + deepen task-specifically; guide ×3/×4 synced.

## Exit criteria (observable; map each to the task that delivers it)
- [x] the `## 0 · GROUND` template + `0-ground.md` name the working-folder context categories (docs · todos · config · data) beyond code, byte-synced across trees  (verify: test_ground_context.py — §0/guide carry the new categories + ×3/×4 parity)  (← ground-context-sources)
- [x] `0-ground.md` instructs the AI to prefer a fast small-model subagent / index / skim for the sweep AND to deepen task-specifically, byte-synced across trees  (verify: test_ground_context.py — guide carries the gather-method hint + ×3/×4 parity)  (← ground-gather-hint)
