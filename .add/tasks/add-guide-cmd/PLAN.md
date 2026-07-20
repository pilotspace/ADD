# TASK: interactive add.py guide

slug: add-guide-cmd · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

`add.py guide [slug]` answers one question — "what do I do next?" — for the active task
(or an explicit one). NON-interactive, read-only print (decision: focused print, not a
prompt loop — scriptable + testable + stdlib, matches the rest of the tool).

Must:
  - Print the resolved task's CURRENT phase, the ONE concrete next action for that
    phase, a pointer to that phase's book chapter (`.add/docs/<NN>-*.md`), and the
    exact `then:` command to run when the phase is satisfied.
  - The `then:` command is phase-aware: `verify` -> `add.py gate ...`; `done` ->
    `add.py new-task ...`; every other phase -> `add.py advance`.
  - With NO active task and no slug, guide is still helpful (not an error): point the
    user at `add.py new-task` + the flow chapter. Exit 0.
  - Read-only: `guide` NEVER mutates state.json or any TASK.md.
Reject:
  - An explicit slug that is not a known task -> `_die("unknown task '<slug>'")` (exit 1).
After:
  - The user has a concrete next action + the chapter to read, without opening any file.
Assumptions (confirm before building):
  - [x] non-interactive focused print (user-picked) — not an interactive walkthrough
  - [x] points at `.add/docs/<chapter>` (the installed book location)
  - [x] covers all 8 phases incl. `observe` (reachable only by manual advance)

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: guide a task in the specify phase
  Given an active task at phase "specify"
  When I run `add.py guide`
  Then output shows "phase: specify", the specify next-action, ".add/docs/03-step-1-specify.md"
  And the then-line is "add.py advance"

Scenario: verify phase points at the gate, not advance
  Given an active task at phase "verify"
  When I run `add.py guide`
  Then the then-line names `add.py gate` and the chapter is 08-step-6-verify.md
  And the word "advance" does NOT appear

Scenario: a done task points at the next feature
  Given an active task at phase "done"
  When I run `add.py guide`
  Then output names `add.py new-task`

Scenario: no active task is guidance, not an error
  Given a fresh project with no tasks
  When I run `add.py guide`
  Then exit code is 0 and output names `add.py new-task`
  And state.json is unchanged

Scenario: an explicit slug overrides the active task
  Given active task A (specify) and another task B at phase "build"
  When I run `add.py guide B`
  Then output shows B at "phase: build" (07-step-5-build.md)

Scenario: an unknown explicit slug is rejected
  Given any project
  When I run `add.py guide does-not-exist`
  Then it exits non-zero with "unknown task"
  And state.json is unchanged

Scenario: guide never mutates state
  Given any active task
  When I run `add.py guide`
  Then state.json is byte-identical before and after
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cli:  add.py guide [slug]            (new subcommand; requires a .add/ root; read-only)

PHASE_GUIDE: dict[phase -> (next_action_text, chapter_filename)] for all 8 PHASES.
  chapter filenames (already on disk in .add/docs/ of an installed project):
    specify->03-step-1-specify.md  scenarios->04-step-2-scenarios.md
    contract->05-step-3-contract.md  tests->06-step-4-tests.md
    build->07-step-5-build.md  verify->08-step-6-verify.md
    observe->09-the-loop.md  done->02-the-flow.md

cmd_guide(args):
  slug = args.slug or state["active_task"]
  - slug is None              -> print "(none)" guidance (new-task + 02-the-flow.md); exit 0
  - slug given but unknown    -> _die("unknown task '<slug>'")                       (exit 1)
  - otherwise                 -> print active/next/read/then for tasks[slug]["phase"]
  then-line:  verify -> "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
              done   -> "start the next feature -> add.py new-task <slug>"
              else   -> "add.py advance"
  NO writes — load_state only; never save_state, never touch a TASK.md.
output shape (4 aligned lines):  active: / next: / read: / then:
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 7 scenarios (new file add-method/tooling/test_guide.py).
Plan (one test per scenario; assert behavior — printed lines, exit, state immutability):
  - test_guide_specify_phase:        new-task / guide / assert phase+action+03-chapter+"advance"
  - test_guide_verify_points_at_gate: phase verify / guide / "gate" present, "advance" absent, 08-chapter
  - test_guide_done_points_at_new_task: phase done / guide / "new-task" present
  - test_guide_no_active_task:       fresh init / guide / exit 0 + "new-task" + state unchanged
  - test_guide_explicit_slug:        two tasks / guide B / shows B at build (07-chapter)
  - test_guide_unknown_slug_errors:  guide bogus / SystemExit + "unknown task"
  - test_guide_is_read_only:         guide / state.json bytes identical before/after

Tests live in: `add-method/tooling/test_guide.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): guide is STRICTLY read-only — it calls `load_state`
only, never `save_state` and never writes a TASK.md (a regression here would corrupt the
"tool is the only writer + writes are intentional" invariant). stdlib only.
Code lives in: `add-method/tooling/add.py` (PHASE_GUIDE constant + cmd_guide + subparser).
Keep `.add/tooling/add.py` byte-identical to source.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 53/53 green (`unittest discover`); 7 new in test_guide.py
- [x] coverage did not decrease — tests only added; red-first confirmed (6 errors + 1 non-vacuous FAIL)
- [x] no test or contract was altered during build — contract FROZEN @ v1
- [x] concurrency / timing safe — read-only command; no writes, no shared mutable state
- [x] no exposed secrets / injection / unexpected deps — stdlib only; prints static PHASE_GUIDE text
- [x] layering & deps follow CONVENTIONS.md — flat stdlib add.py; `load_state` only (no writer path)
- [x] a person reviewed — author self-review (read-only, +7 tests green); combined adversarial
      review of the v1-1 batch runs before the final push. Human author sign-off: pending.

### GATE RECORD
Outcome: PASS
Reviewed by: author (self) · date: 2026-05-29 · combined v1-1 adversarial review pending pre-push
Evidence: 53/53 green · read-only verified by test_guide_is_read_only + test_guide_no_active_task
(state.json byte-identical) · live smoke on this repo matches the approved preview.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do users run `guide` and act, or ignore it? is the
per-phase next-action wording still true as the method evolves (keep PHASE_GUIDE in sync
with the chapter EXIT lines)? Spec delta for the next loop: optional `--verbose` that
prints the phase's EXIT criteria inline; surface `ready` tasks in the no-active-task case.

Post-review hardening (v1-1 adversarial review, 2026-05-29): a hand-corrupted `phase:` value
in state.json used to raise a raw `KeyError` from `PHASE_GUIDE[phase]`. Now `cmd_guide` uses
`PHASE_GUIDE.get(phase)` and `_die`s naming the bad phase — covered by
test_guide_unknown_phase_dies_clean (RED→GREEN). Robustness fix only; the v1 contract is unchanged.
