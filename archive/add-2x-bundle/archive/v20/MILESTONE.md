# MILESTONE: Goal-Driven Dynamic Loop

goal: a milestone self-drives toward its GOAL — verify proves each task's code is wired and dead-code-free (or, for prose, semantically read not skimmed), reopens any task that misses a criterion, and turns folds + extras into the next tasks, looping until the goal is met
rationale: new-major — a goal-driven dynamic milestone loop (deep verify + reopen + self-extending task list) that no active milestone's goal covers. Confirmed via intake interview 2026-06-08; one major over a v20/v20-1 split because dynamic-task-loop depends on both reopen + GOAL (internal deps beat a cross-milestone dep).
stage: mvp · status: active · created: 2026-06-08

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
  1. an explicit project-level GOAL in the foundation, surfaced by `status`/`guide` — the loop's anchor;
  2. deepened verify — wiring cross-check + new-dead-code as EVIDENCE for coding tasks; a recorded semantic no-skim read as evidence for non-coding tasks;
  3. a `reopen` transition returning an already-`done` task to a named phase with a never-silent record (lifecycle contract re-frozen, human-approved);
  4. a dynamic task list — folds + extra items become AI-proposed, human-confirmed next tasks; `milestone-done` holds while the GOAL's criteria are unmet.
Out: engine auto-spawn of tasks without human confirm (chosen: AI-proposes-human-confirms) · a third-party dead-code linter dependency (stdlib/serena only, per the no-`wcwidth` house rule) · auto-rollback in observe · the contract-FREEZE seam staying human (untouched) · real-telemetry monitors (this is a CLI/method, not a running service) · cross-project goal tracking.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **GOAL** (new GLOSSARY term) — the durable outcome a project (and each milestone) runs toward; the loop's orientation anchor; distinct from a task's §1 Must.
- **reopen** (new GLOSSARY term) — returning an already-`done` task to an earlier phase with a recorded reason; distinct from HARD-STOP (which returns a not-yet-done task Build→ within the same run).
- **evidence-for-code / AI-read-for-prose** — the deepened-verify reconciliation: code checks must be evidence (a referenced-symbol assertion, a dead-code scan); prose checks are the AI's recorded semantic read; neither face is "trust the diff looks right" (Constraint 2: trust evidence, not inspection).
- every task created mid-flight is still confirm-before-create (intake invariant) — the loop is dynamic, the human keeps the wheel.
- every verify/observe rule is stated identically in the skill guide AND the book (cross-cutting-reword); both `add.py` copies of any edited skill file stay md5-identical (dogfood-parity).

## Shared / risky contracts (freeze these first)
- the task LIFECYCLE contract (the frozen 7-phase flow) gains `reopen` -> owning task `reopen-transition` (re-freeze vN, human-approved — Rule 3)
- the deepened VERIFY rubric (what evidence a gate now requires) -> owning task `verify-deepen`
- the `status`/`guide` GOAL surface (an additive line on a frozen output seam) -> owning task `project-goal`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] project-goal       depends-on: none                          — explicit project GOAL in PROJECT.md, surfaced by `status`/`guide`; the loop's anchor
- [ ] verify-deepen      depends-on: none                          — wiring + new-dead-code as code-evidence; semantic no-skim as prose-evidence (guide + book, identical)
- [ ] reopen-transition  depends-on: verify-deepen                 — engine `reopen` action + lifecycle re-freeze; fires when deepened verify finds a done task's criterion unmet
- [ ] dynamic-task-loop  depends-on: project-goal,reopen-transition — folds + extras → AI-proposed, human-confirmed next tasks; `milestone-done` holds until GOAL met

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py status` and `guide` print the project GOAL; PROJECT.md carries an explicit goal line                                            (← project-goal)
- [x] verify requires, for a coding task, evidence the new symbol is referenced + no new dead code; for a non-coding task, a recorded semantic no-skim read — stated identically in guide + book   (← verify-deepen)
- [x] `add.py reopen <done-task> --to <phase>` returns the task with a recorded reason; the lifecycle contract is re-frozen vN; the record is never silent                                       (← reopen-transition)
- [x] at observe/close, folds + extra items surface as confirmable next tasks attached to the active milestone, and `milestone-done` does not pass while the GOAL's criteria are unmet            (← dynamic-task-loop)
