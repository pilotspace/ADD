# TASK: attach existing task to a milestone

slug: set-milestone-cmd · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Must:
  - `set-milestone <task> <milestone>`: attach/move an existing task to a milestone
  - `set-milestone <task> none`: detach a task from any milestone (sets milestone=null)
  - validate before writing: the task must exist; the milestone must exist (unless "none")
  - print a confirmation of the new linkage
After:
  - state.tasks[<task>].milestone == <milestone> (or null when "none"); nothing else changes
Reject:
  - unknown task        -> "unknown_task"
  - unknown milestone   -> "unknown_milestone"
Assumptions (confirm before building):
  - [x] "none" is the reserved word to detach (cannot name a milestone "none")
  - [x] does NOT change active_task or active_milestone — pure relinking
  - [x] moving a task between milestones is just calling it again with a new target

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: attach an existing task to a milestone
  Given a task "t" with no milestone and a milestone "mvp"
  When I run `set-milestone t mvp`
  Then state.tasks.t.milestone == "mvp"

Scenario: detach with "none"
  Given task "t" currently in milestone "mvp"
  When I run `set-milestone t none`
  Then state.tasks.t.milestone is null

Scenario: unknown task rejected
  Given no task "ghost"
  When I run `set-milestone ghost mvp`
  Then it is rejected "unknown_task" (exit 1)
  And no state changes

Scenario: unknown milestone rejected
  Given task "t" and no milestone "ghost"
  When I run `set-milestone t ghost`
  Then it is rejected "unknown_milestone" (exit 1)
  And task t's milestone is unchanged
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI:  add.py set-milestone <task> <milestone|none>

writes: state.tasks[<task>].milestone   (only this field)
prints: "task '<task>' -> milestone '<milestone>'"  or  "... -> (none)"

rejects (stderr `add: error: <code>`, exit 1):
  unknown_task · unknown_milestone

reserved word: "none" -> detach (milestone=null)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 4 scenarios.
Plan (added to add-method/tooling/test_milestone.py):
  - test_set_milestone_attaches
  - test_set_milestone_none_detaches
  - test_set_milestone_unknown_task_rejected
  - test_set_milestone_unknown_milestone_rejected
MUST run red (command doesn't exist yet) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): validate task + milestone BEFORE writing; touch only
the task's `milestone` field (never active_task/active_milestone or other tasks).
Code lives in: `add-method/tooling/add.py` (shared tooling).
Constraints: do NOT change any test or the frozen contract; stdlib only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 32/32 via `npm test`
- [x] coverage did not decrease — +4 tests; existing 28 still green
- [x] no test or contract was altered during build — contract FROZEN; tests untouched
- [x] concurrency / timing — N/A (local single-process atomic write)
- [x] no exposed secrets / injection / unexpected deps — stdlib only
- [x] layering & deps follow CONVENTIONS.md — touches only one state field; no new deps
- [x] a person reviewed — live `set-milestone … v1-1` on this repo; check 25/25

### GATE RECORD
Outcome: PASS
Evidence: 32/32 tests green; live run linked a task and check stayed green
Reviewed by: Tin Dang · date: 2026-05-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): how often users move tasks between milestones.
Spec delta for the next loop: a `--depends-on` editor for existing tasks (sibling gap
to this one); `ready --milestone <m>` to scope readiness. Unblocks: milestone-archive.
