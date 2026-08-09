# MILESTONE: Phase-detail drill-down

goal: A person can drill into one task and read each phase's actual result — rules, scenarios, frozen contract, test plan, gate + evidence, observe delta — rendered read-only from its TASK.md, without opening the file
stage: mvp · status: active · created: 2026-06-02

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a per-task PHASE-DETAIL view — a new read-only surface that renders a single task's
     §1–§7 (specify rules · scenarios · frozen contract · test plan · build note · verify
     gate+evidence · observe delta) as a phase-by-phase narrative, each phase tagged with its
     reached/current state from state.json. Answers "what did each phase DECIDE", not just
     "which phase did it reach" (the v9 rollup's job). Reuses v9's read-only + fail-closed
     discipline: a missing/placeholder section renders `(empty)`, never a silent gap.
Out: grading/scoring/editing any phase (read-only — carry the v9 "engine renders, human judges"
     boundary). New phase DATA capture — v9-1 renders what TASK.md ALREADY records; it adds NO
     field, NO phase, NO state.json change. Cross-task or cross-milestone phase comparison/diff
     (single-task scope). Persisting per-task detail to a file (RETRO.md stays milestone-level;
     the drill-down is on-demand stdout only). Reformatting the milestone rollup `report <m>`
     (this is purely additive — the existing rollup is untouched).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **One TASK.md, one parser.** Per-phase extraction reads the SAME `## N · PHASE` headers the
  task template defines (specify→…→observe). A renamed/missing/placeholder section fails CLOSED
  to `(empty)` — never a silent omission (carry v9's fail-closed rule).
- **Read-only surface** (carry v9): the drill-down renders, never writes; state.json untouched.
- **Additive, not a re-skin.** v9-1 adds a view; it does not change `report <m>`'s frozen render
  or its `report_data` facts seam (those stay as shipped in v9).
- New glossary term: **Phase-detail / drill-down** — the per-task phase-by-phase render
  (`report <m> <task>`), distinct from the milestone **rollup** (`report <m>`) and the
  **awareness surface** umbrella (v9).

## Shared / risky contracts (freeze these first)
- the **per-phase extraction shape** — which `## N · PHASE` section maps to which phase, what
  each phase block shows (content + reached/current + gate where relevant), and the `(empty)`
  fail-closed marker. One task consumes it; freeze it in phase-detail-render.  -> phase-detail-render

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] phase-detail-render   depends-on: none   — `report <milestone> <task>`: parse the task's §1–§7 + state.json, render each phase's result + reached/current state + gate; freeze the section-extraction shape + `(empty)` fail-closed rule   (PASS · 219 tests)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py report <m> <task>` (and smart `report <task>`) renders all SEVEN phases for the task, each showing its captured content (rules / scenarios / frozen contract / test plan / build note / verify gate+evidence / observe delta) + the phase's reached/current marker; a missing or placeholder section shows `(empty)`, never a silent gap   (← phase-detail-render)
- [x] the view is read-only — it writes nothing to disk, state.json is unchanged, and the existing `report <m>` milestone rollup renders exactly as before; an unknown task for the milestone is rejected with `unknown_task`   (← phase-detail-render)
