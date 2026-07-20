# TASK: status prints unlocked->lock hint when setup.locked is False

slug: status-lock-hint · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto

> Closes the autonomous-setup ADD delta: after `init --await-lock`, `status` told the
> user the GENERIC next-step (/add or resume) instead of the one thing that matters in
> the unlocked window — review `.add/SETUP-REVIEW.md`, then `add.py lock`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: in the non-json `status` output, when the project's setup is present-but-UNLOCKED
(`not _setup_locked(state)` — i.e. `setup.locked is False`), the TERMINAL guidance names
`.add/SETUP-REVIEW.md` and `add.py lock`, and the generic resume / first-run hint is suppressed.
Framings weighed: replace the terminal hint when unlocked (chosen) · add a 2nd always-on line ·
  surface it in `--json` too (rejected — json is a machine view; out of scope this task)
Must:
  - When unlocked, `status` prints a hint that names BOTH `SETUP-REVIEW.md` and `add.py lock`.
  - When unlocked, `status` does NOT print the generic resume line ("start the next feature" /
    "read .add/tasks/...") nor the first-run "/add" panel ("you're set up. In Claude Code").
  - The hint fires in BOTH unlocked sub-states: no tasks yet, AND a drafted first task present.
  - When LOCKED (setup.locked True) or GRANDFATHERED (no "setup" key), behavior is unchanged
    (the existing resume / first-run hint shows; no lock hint).
Reject:
  - n/a — read-only status surface; no inputs to reject.
After:
  - An unlocked setup's `status` ends with the lock hint; `--json` output is byte-identical to today.
Assumptions — least-sure first:
  ⚠ The lock hint should REPLACE the generic terminal hint (not stack on top of it) — least sure
    because a user might still want the resume line; if wrong: cheap to also keep resume.
    Chosen replace: in the unlocked window the ONLY correct next move is review+lock, so a second
    competing "next" would dilute it.
  - [x] `not _setup_locked(state)` is the exact predicate for "setup present AND locked False"
        — confirmed by reading the helper (add.py:202-208); REUSE it (no parallel predicate).
  - [x] `--json` stays unchanged this task — the milestone scopes the human resume hint only.

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: unlocked setup with a drafted first task
  Given a project seeded `init --await-lock` (setup.locked False) with one task at specify
  When I run `add.py status`
  Then the output contains ".add/SETUP-REVIEW.md" and "add.py lock"
  And the output does NOT contain "start the next feature" or "read .add/tasks/"

Scenario: unlocked setup with no tasks yet
  Given a project seeded `init --await-lock` (setup.locked False) with zero tasks
  When I run `add.py status`
  Then the output contains ".add/SETUP-REVIEW.md" and "add.py lock"
  And the output does NOT contain "you're set up. In Claude Code"

Scenario: locked project is unchanged (behavior preserved)
  Given a project seeded `init --await-lock` then `lock`, with one task
  When I run `add.py status`
  Then the output does NOT contain "SETUP-REVIEW.md"
  And the existing resume/next hint is shown as before

Scenario: grandfathered project is unchanged (no setup key)
  Given a plain `init` project (no "setup" key) with one task
  When I run `add.py status`
  Then the output does NOT contain "SETUP-REVIEW.md"
  And the existing resume/next hint is shown as before
```

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py status            (non-json human view)
  when NOT _setup_locked(state):   # setup present AND setup.locked is False
    terminal line(s) -> a hint naming ".add/SETUP-REVIEW.md" AND "add.py lock"
                        (generic resume / first-run "/add" panel SUPPRESSED)
  else (locked or grandfathered):  # unchanged
    terminal line(s) -> existing first-run panel / resume block (verbatim, as today)
add.py status --json     -> UNCHANGED (byte-identical to today)
Schema: read-only; load_state only; no state mutation. Predicate reused: _setup_locked (add.py:202).
```

Status: FROZEN @ v1   <!-- approved at the one-approval front (contract seam) -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every scenario above (4 tests), asserting observable stdout.
Tests live in: `add-method/tooling/test_status_lock_hint.py` · run from `add-method/tooling/`.
Plan:
  - test_unlocked_with_task_shows_lock_hint: await-lock + 1 task → stdout has SETUP-REVIEW.md +
    "add.py lock"; lacks "start the next feature" / "read .add/tasks/". RED now.
  - test_unlocked_no_tasks_shows_lock_hint: await-lock + 0 tasks → stdout has the lock hint;
    lacks "you're set up. In Claude Code". RED now.
  - test_locked_shows_resume_not_lock_hint: await-lock + lock + 1 task → no "SETUP-REVIEW.md".
    GREEN now, must stay green (behavior preserved).
  - test_grandfathered_shows_resume_not_lock_hint: plain init + 1 task → no "SETUP-REVIEW.md".
    GREEN now, must stay green.

<!-- RED driver: the two unlocked tests (no lock hint exists today). The two locked tests are
     the behavior-preserving safety net. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule: REUSE `_setup_locked(state)` (add.py:202) — do NOT write a parallel predicate.
The terminal-hint branch must fire in BOTH unlocked sub-states (the `if not tasks:` early-return
panel AND the resume block); restructure the tail of `cmd_status` so the unlocked hint takes
precedence and the generic hints are suppressed when unlocked.
Code lives in: `add-method/tooling/add.py` (canonical only — orchestrator syncs bundle + dogfood).
Constraints: do NOT change any test or the contract; touch only `cmd_status`'s human-view tail;
leave the `--json` branch untouched; ask if unclear.

### Build notes (2026-06-04)
- Computed `unlocked = not _setup_locked(state)` once after `state = load_state(root)`.
- Two edit sites in `cmd_status` human-view tail (--json branch at lines 598-614 untouched):
  1. No-tasks early-return (~line 649): when `unlocked`, print the lock hint instead of the
     generic first-run panel; preserves `tasks : (none yet)` header; returns early either way.
  2. With-tasks tail (~line 668): `if unlocked: <hint>  elif active and active in tasks: <resume>`.
     Suppresses resume block while unlocked; existing resume text unchanged when locked/grandfathered.
- No parallel predicate written; `_setup_locked` reused verbatim.
- Bundle-parity tests (test_addpy_parity, test_addpy_dual_tree_md5) red as expected — orchestrator
  syncs bundle at integration (touch_boundary explicitly out-of-scope for this stream).

<!-- EXIT: own test file green; --json unchanged; no test/contract touched. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — own file 4/4 · regression net (setup_lock/machine_state/v8_onramp/onboarding_align/min_pillar) green at integration · FULL suite 329/329 OK (the 2 in-worktree bundle-parity fails were the expected stale-bundle state, resolved by the orchestrator's bundle regen + dogfood sync)
- [x] coverage did not decrease — 4 tests added, none removed or weakened
- [x] no test or contract was altered during build — worker commit `16d59a2` touches exactly add.py + this task dir (verified by stat)
- [x] concurrency / timing — n/a (read-only status print)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none added
- [x] layering & dependencies follow CONVENTIONS.md — `_setup_locked` reused, no parallel predicate; --json branch byte-identical
- [x] reviewed — human approved the frozen contract at the one-approval seam (2026-06-04); merged diff manually reviewed by the orchestrator at serial integration; empirical dogfood check (grandfathered repo shows NO hint); verify auto-resolved per `autonomy: auto`

### GATE RECORD
Outcome: PASS  (auto-resolved — evidence gate, run.md)
Owner of record: dynamic run, stream B (worker agent a843de3bd42cd6a05, commit `16d59a2`, integrated by cherry-pick per the worker's stale-base disclosure) + orchestrator serial integration (bundle regen · dogfood sync · full suite 329 OK)
Residue checks performed: security=none · concurrency=n/a (read-only print) · architecture=none (predicate reused) · process=stale worktree base disclosed and resolved (see §7 delta)
Date: 2026-06-04

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: do users still skip the lock step? (the hint should reduce stuck-unlocked sessions)
Spec delta for the next loop: if telemetry shows users still skip lock after seeing the hint,
consider making the hint more prominent (e.g. a WARNING prefix) or blocking new-task creation
after the first until locked.

### Competency deltas
- [ADD · folded] a stream worker's worktree must be VERIFIED to fork from the frozen-front HEAD
  before the run starts — stream B's worktree forked one commit behind the front (7f7ee54 vs
  c896698), forcing an in-run cherry-pick of the front and a cherry-pick (not merge) integration;
  streams.md names this check but the orchestrator did not run it pre-spawn
  (evidence: stream B residue disclosure; deliverable 16d59a2 parented on a duplicated front commit)
- [UDD · folded] at the user's most-lost moment the status surface must show exactly ONE next step —
  the unlocked window previously offered the generic "/add" or resume hint, competing with the only
  correct move (review SETUP-REVIEW.md, then lock)
  (evidence: test_unlocked_no_tasks_shows_lock_hint red before the build; autonomous-setup-guide ADD delta)
