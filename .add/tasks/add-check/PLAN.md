# TASK: add.py check: validate .add project integrity

slug: add-check · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Must:
  - find the nearest `.add/` root by walking up from the cwd (reuse `find_root`)
  - validate `state.json` parses and has keys: project, stage, active_task, tasks
  - for every task in state, confirm `.add/tasks/<slug>/TASK.md` exists on disk
  - confirm each task's TASK.md `phase:` marker matches its phase in state.json
  - print one line per check (`PASS`/`FAIL <reason>`) and a final summary count
  - be read-only: never write or mutate any file
After:
  - exit code 0 when all checks pass; exit code 1 when any check fails
Reject:
  - no `.add/` project found     -> "no_project"
  - state.json is not valid JSON -> "state_invalid"
Assumptions (confirm before building):
  - [x] read-only; the check never repairs, only reports (repair is a separate future task)
  - [x] operates on the nearest `.add/` root, same discovery rule as the other commands
  - [x] a missing `src/`/`tests/` dir is NOT a failure (they are optional until build)

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: clean project passes
  Given an initialised .add project with one task whose TASK.md exists and marker matches state
  When I run `add.py check`
  Then every check line reads PASS and the command exits 0

Scenario: missing TASK.md fails
  Given an initialised project with a task registered in state
  And that task's TASK.md has been deleted from disk
  When I run `add.py check`
  Then a FAIL line names the missing TASK.md and the command exits 1
  And no file is created or modified (read-only)

Scenario: phase marker mismatch fails
  Given a task whose state.json phase is "build" but whose TASK.md marker says "specify"
  When I run `add.py check`
  Then a FAIL line names the mismatch and the command exits 1
  And no file is created or modified

Scenario: no project rejected
  Given a directory with no .add root anywhere above it
  When I run `add.py check`
  Then it is rejected "no_project" and the command exits 1

Scenario: corrupt state rejected
  Given a .add/state.json that is not valid JSON
  When I run `add.py check`
  Then it is rejected "state_invalid" and the command exits 1
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI:  add.py check
  (no arguments; operates on the nearest .add root found by walking up from cwd)

stdout: one line per check, then a summary line:
  "PASS  <check description>"
  "FAIL  <check description>: <reason>"
  "check: <n> passed, <m> failed"

exit code:
  0  -> all checks passed
  1  -> any check failed, OR a reject below

reject (printed to stderr as `add: error: <code>`, exit 1):
  no .add root         -> "no_project"
  state.json bad JSON  -> "state_invalid"

Reads (never writes): .add/state.json, .add/tasks/<slug>/TASK.md
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new `cmd_check` branches (5 scenarios).
Plan (one test per scenario, asserting observable behavior — exit code + output):
  - test_check_passes_on_clean_project: init + new-task -> check exits 0
  - test_check_detects_missing_task_md: delete TASK.md -> SystemExit(1), file not recreated
  - test_check_detects_phase_mismatch: edit state phase only -> SystemExit(1)
  - test_check_no_project: empty dir -> SystemExit(1) ("no_project")
  - test_check_state_invalid: corrupt state.json -> SystemExit(1) ("state_invalid")

DEVIATION (recorded): this task edits the shared `add.py`, so per CONVENTIONS the
tests live in `add-method/tooling/test_add.py` (the project's test harness, run by
`npm test`), NOT in this task's `./tests/`. The per-task `src/`/`tests/` dirs stay
empty for shared-tooling features.
MUST run red (command does not exist yet) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the check is strictly READ-ONLY — it must never
call any write/save function. It uses `find_root` + reads files only. A diagnostic
that mutates the thing it diagnoses is a bug.
Code lives in: `add-method/tooling/add.py` (shared tooling — see §4 deviation).
Constraints: do NOT change any test or the frozen contract; stdlib only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 16/16 (`python3 -m unittest test_add`)
- [x] coverage did not decrease — added 5 tests; all `cmd_check` branches exercised
- [x] no test or contract was altered during build — contract FROZEN untouched; tests
      were tightened at the RED stage (before any code), never weakened to fit code
- [x] concurrency / timing safe — read-only command, no shared mutable state, no races
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — stdlib, snake_case, no new deps
- [x] a person reviewed and approved the change — orchestrator review + live run on this repo

### GATE RECORD
Outcome: PASS
Evidence: 16/16 unit tests green; `add.py check` on this repo -> "6 passed, 0 failed", exit 0
Reviewed by: Tin Dang · date: 2026-05-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of FAIL lines in CI; most common failing
check (missing TASK.md vs marker mismatch) signals where users drift.
Spec delta for the next loop:
  - wire `add.py check` into CI as a gate (fail the build on exit 1)
  - add `--fix` mode (re-sync markers) as a SEPARATE task — keeps `check` read-only
  - extend checks: validate stage/phase enums, detect orphan task dirs not in state
