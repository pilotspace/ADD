# MILESTONE: Guard the AI-first flow (runtime)

goal: A project nudges work back toward the intake to milestone structure: add.py warns (never blocks) when a task lives outside a milestone, giving the documented AI-first flow a runtime backstop
stage: mvp · status: active · created: 2026-06-02

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> **Why now (sibling of v8).** v8 made the docs *teach* the AI-first flow
> (orient → intake → milestone → one-approval → run). But nothing *guards* it: an
> agent can still scaffold a bare task outside any milestone, skipping the intake
> layer the docs now lead with. v8-1 gives the documented flow a runtime backstop —
> a structural nudge back toward intake → milestone, so the words and the tool agree.

## Scope
In:  **`add.py` warns when a task lives outside a milestone** (created bare /
     outside intake) — a non-blocking nudge back to the `/add` → intake → milestone
     flow. Surfaced in `add.py check` (a new rule) and at `add.py new-task` (a hint
     when no milestone is attached and none is active).
Out: **Blocking** anything (warn-never-block — the bare `new-task` escape hatch
     stays open; `add.py` stays a reporter, not a decider — honors v8's frozen
     non-goal). **Proving an intake conversation happened** (unobservable — see the
     honesty rule below). **Enforcing v7-designed one-approval / auto behavior**
     (still at `verify`, not shipped — honors v8's release-ordering hold). Any change
     to the 7-phase sequence or phase semantics.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Honesty rule (structure, not the act).** `add.py` can only observe the
  *structural footprint* intake leaves — `state.json`'s task→milestone mapping and
  TASK.md shape. It **cannot** observe whether an intake conversation or a human
  seam-approval actually happened (an agent could hand-fabricate a milestone+task and
  the guard stays green). So every claim here is "this task is *outside the intake
  structure*", never "the flow *was followed*". Same `words-exist ≠ method-works`
  caveat as v8's guards.
- **Warn-never-block.** The guard nudges; it never halts. `new-task` without a
  milestone still succeeds (escape hatch). This is the load-bearing invariant that
  keeps `add.py` a reporter and out of v8's "not a decider" non-goal — freeze it.
- **Shipped structure only.** Guard the *shipped* intake→milestone structure
  (v4-1 scope-loop / v6), not the v7-designed one-approval/auto front. If v7 is
  referenced at all, the designed-vs-shipped label applies.

## Shared / risky contracts (freeze these first)
- **the warning surface + trigger** (where the nudge appears — `check` rule code +
  `new-task` hint — and the exact orphan-detection rule: task has no `milestone` in
  state.json) → owning task `orphan-task-guard`. Riskiest because it touches `add.py`
  behavior; the warn-never-block + non-zero-exit semantics must be frozen first.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] orphan-task-guard   depends-on: none   — `add.py check` gains an orphan-task rule + `new-task` emits an intake nudge when a task has no milestone; non-blocking; structural guard test  · gate PASS

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py check` reports a task that has no milestone as a WARNING (not a failure), naming the intake/`/add` flow   (← orphan-task-guard)
- [x] `add.py new-task <slug>` with no `--milestone` and no active milestone prints a nudge toward intake, and still creates the task (warn-never-block)   (← orphan-task-guard)
- [x] the warning text labels structure, not the act ("outside a milestone", never "flow not followed") — honesty rule   (← orphan-task-guard)

## Close note (2026-06-02)
Single task gated PASS; all three exit criteria met. Milestone marked **done**. Evidence: orphan-guard
7/7, full suite 173 OK, `add.py check` 116 passed / 0 failed (3 warnings) exit 0, add.py md5-parity.
Dogfood note: this milestone was itself driven entirely through the v8 AI-first flow (`/add` → intake →
v8-1 confirm → one-approval front → conservative self-driving run → gate) — the first feature to test
the on-ramp v8 shipped. Same release-ordering hold applies: this builds on shipped intake→milestone
structure only and does not depend on v7.
