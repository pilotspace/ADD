# TASK: Milestone (SDD) tier + dependency ordering

slug: milestone-layer · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Must:
  - `new-milestone <slug> --goal G --stage S`: scaffold .add/milestones/<slug>/MILESTONE.md
    (the SDD living doc), register it in state, set it active. No-clobber w/o --force.
  - `new-task` gains `--milestone <slug>` (defaults to active milestone) and
    `--depends-on a,b` (comma list); both stored on the task in state.
  - `ready`: list tasks that are not done AND whose every depends-on task is done.
    A task with no deps ("depends-on: none") is immediately ready.
  - `milestone-done <slug>`: exit gate — succeed only if every task in the milestone is
    phase=done AND gate=PASS; then set milestone status=done. Else list blockers, exit 1.
  - `status`: roll up the active milestone (X/Y tasks done) above the task list.
  - `check`: also flag drift — a task referencing an unknown milestone, a depends-on
    referencing an unknown task, a dependency cycle, or a done milestone w/ unfinished tasks.
  - all schema additions are backward-compatible (old state without these keys still loads).
After:
  - state.json has `milestones{}`, `active_milestone`, and per-task `milestone`+`depends_on`;
    `ready` and `milestone-done` reflect the dependency graph; old commands unaffected.
Reject:
  - new-milestone slug not alphanumeric/-/_      -> "bad_slug"
  - new-milestone when it already exists (no --force) -> "milestone_exists"
  - --milestone naming an unknown milestone        -> "unknown_milestone"
  - milestone-done with any task not done/PASS      -> "milestone_incomplete" (exit 1, lists blockers)
Assumptions (confirm before building):
  - [x] tasks stay slug-keyed; deps are slugs (slugs+deps give GSD-style insert-without-renumber)
  - [x] exit criteria live as human-checked "User can …" lines in MILESTONE.md; the machine
        gate checks task completion only (no prose-checkbox parsing in v1)
  - [x] backlog (999.x) and milestone archiving are deferred to a later task (avoid GSD bloat)
  - [x] a task may still have no milestone (unsequenced) — backward compatible

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: new-milestone scaffolds and activates
  Given an initialised project
  When I run `new-milestone mvp --goal "core money movement" --stage mvp`
  Then .add/milestones/mvp/MILESTONE.md exists and state.active_milestone == "mvp"

Scenario: task links to active milestone and records deps
  Given active milestone "mvp"
  When I run `new-task transfer --depends-on accounts,login`
  Then the task has milestone="mvp" and depends_on=["accounts","login"]

Scenario: ready lists only unblocked, unfinished tasks
  Given task A (done) and task B (depends-on A, not done) and task C (depends-on B)
  When I run `ready`
  Then B is listed and C is not (its dep B is unfinished)

Scenario: milestone-done blocks on incomplete tasks
  Given milestone "mvp" with one task not at gate PASS
  When I run `milestone-done mvp`
  Then it is rejected "milestone_incomplete", exits 1, and milestone status stays active

Scenario: milestone-done passes when all tasks done
  Given every task in "mvp" is phase=done and gate=PASS
  When I run `milestone-done mvp`
  Then milestone status becomes "done" and it exits 0

Scenario: check detects a dependency cycle
  Given task A depends-on B and task B depends-on A
  When I run `check`
  Then it fails (exit 1) naming the cycle

Scenario: unknown milestone rejected
  Given no milestone "ghost"
  When I run `new-task x --milestone ghost`
  Then it is rejected "unknown_milestone" and no task is created
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
state.json additions (all optional / backward-compatible):
  milestones: { <slug>: { title, goal, stage, status: active|done, created, updated } }
  active_milestone: <slug> | null
  tasks.<slug>.milestone:   <slug> | null
  tasks.<slug>.depends_on:  [ <task-slug>, ... ]   # [] == no deps == immediately ready

files:
  .add/milestones/<slug>/MILESTONE.md   (SDD living doc — template below)

CLI:
  new-milestone <slug> --title T --goal G --stage S   [--force]
  new-task <slug> [--title T] [--milestone M] [--depends-on a,b,c] [--force]
  ready
  milestone-done <slug>
  status            # gains a milestone rollup block
  check             # gains drift + cycle checks

exit codes / rejects (stderr `add: error: <code>`, exit 1):
  bad_slug · milestone_exists · unknown_milestone · milestone_incomplete
  check failures (drift/cycle) -> exit 1 with FAIL lines

MILESTONE.md template sections (thin — NO per-task detail here):
  goal · stage · status
  ## Scope (In / Out)
  ## Shared decisions & glossary deltas      (living)
  ## Shared / risky contracts (freeze first)
  ## Tasks (breadth-first)  - [ ] <slug>  depends-on: none  — one line
  ## Exit criteria          - [ ] User can <behavior>   (← <task>)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 7 scenarios.
Plan (test file: add-method/tooling/test_milestone.py — shared-tooling deviation):
  - test_new_milestone_scaffolds_and_activates
  - test_new_task_links_milestone_and_deps
  - test_ready_lists_only_unblocked
  - test_milestone_done_blocks_incomplete
  - test_milestone_done_passes_when_all_done
  - test_check_detects_cycle
  - test_new_task_unknown_milestone_rejected
  - test_backward_compat_old_state_still_loads (status/check on pre-milestone state)
MUST run red (commands don't exist yet) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): schema changes MUST be backward-compatible — every
new key read via `.get(...)` with a default so a pre-milestone state.json still loads.
Validate milestone/deps BEFORE any write (no partial task creation on reject).
Code lives in: `add-method/tooling/add.py` (shared tooling).
Constraints: do NOT change any test or the frozen contract; stdlib only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 28/28 via `npm test` (8 new milestone tests)
- [x] coverage did not decrease — +8 tests; existing 20 still green
- [x] no test or contract was altered during build — contract FROZEN; tests untouched
- [x] concurrency / timing — N/A (local CLI, atomic single-process writes)
- [x] no exposed secrets / injection / unexpected deps — stdlib only
- [x] layering & deps follow CONVENTIONS.md — backward-compatible `.get` reads; no new deps
- [x] a person reviewed — verified backward compat on this repo's old-format state (11/11 check)

### GATE RECORD
Outcome: PASS
Evidence: 28/28 green; `status`/`check` run on pre-milestone state without crash; acyclic check live
Reviewed by: Tin Dang · date: 2026-05-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): how often `check` flags drift/cycles in real use;
whether users want to attach EXISTING tasks to a milestone (no command for that yet).
Spec delta for the next loop:
  - `set-milestone <task> <milestone>` to attach/move an existing task (gap found while dogfooding)
  - milestone archive: collapse a done milestone (GSD pattern) to keep things small
  - backlog `999.x` parking for out-of-scope ideas (GSD pattern)
  - `ready --milestone <m>` to scope readiness to one milestone
