# MILESTONE: v1.1 — adoption & ergonomics

goal: make ADD easier to adopt and operate
stage: mvp · status: active · created: 2026-05-28

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  ergonomics + adoption — attach existing tasks to milestones, an interactive
     next-step guide, a Quickstart (Vietnamese translation descoped → English-only),
     milestone archiving.
Out: backlog (999.x) parking; web UI; multi-repo workspaces (later milestones).

## Shared decisions & glossary deltas   (living — every task must honor these)
- Stay stdlib-only Python + Node built-ins (no new deps) — keep `npx @mrq/add` zero-install.
- Every new command keeps state writes atomic + backward-compatible (`.get` defaults).
- Tool remains the only writer of state.json.

## Shared / risky contracts (freeze these first)
- `add.py set-milestone <task> <milestone>` signature -> owning task set-milestone-cmd
  (milestone-archive depends on it; freeze it first so the archive task can build against it)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] set-milestone-cmd   depends-on: none              — attach/move an existing task to a milestone
- [x] add-guide-cmd       depends-on: none              — `add.py guide`: print the next concrete step
- [x] vi-quickstart       depends-on: add-guide-cmd     — DESCOPED to English-only; `guide` now covered in the Quickstart
- [x] milestone-archive   depends-on: set-milestone-cmd — collapse a done milestone, keep state small

## Exit criteria (observable; map each to the task that delivers it)
- [x] User can move an existing task into a milestone without editing JSON   (← set-milestone-cmd)
- [x] User can ask the tool "what do I do next?" and get a concrete answer   (← add-guide-cmd)
- [~] DESCOPED — kept English-only; the Quickstart now teaches `guide`        (← vi-quickstart)
- [x] A finished milestone collapses so state.json/status stay small         (← milestone-archive)
