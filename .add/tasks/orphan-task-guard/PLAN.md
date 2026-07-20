# TASK: add.py warns (never blocks) when a task lives outside a milestone

slug: orphan-task-guard · created: 2026-06-02 · stage: mvp · v8-1 · depends-on: none
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- changes add.py behavior (method-defining) -> self-driving build→verify, then HOLD at verify for human diff review -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

v8 taught the docs to lead with the intake → milestone flow. Nothing *guards* it: an agent can
still `new-task` a bare task outside any milestone, skipping the intake layer. This task gives the
flow a **runtime backstop** — a structural nudge back toward intake → milestone. It can only see the
*footprint* (a task with no milestone in state.json), never the *act* of intake (see Assumptions).

Must:
  - `add.py check` emits a **WARNING** (a third tier, distinct from PASS/FAIL) for every task whose
    `milestone` is null in state.json, naming the intake / `/add` flow. The warning does NOT count
    toward `failed` and does NOT change the exit code — `check` exits 0 when there are 0 FAILs, warnings or not.
  - `add.py new-task <slug>` that resolves to **no milestone** (no `--milestone` and no active
    milestone) prints a nudge toward the intake / `/add` flow AND still creates the task (exit 0).
  - the warning/nudge text labels **structure** ("outside a milestone" / "not attached to a
    milestone"), never the **act** ("flow followed" / "flow not followed").
  - `--json` mode of `check` carries the warnings in a `warnings` list + `warned` count; `passed` /
    `failed` are unchanged and an orphan task NEVER appears in `failed`.
Reject (the design invariants, each a named anti-behavior the build must not produce):
  - `check` exits 1 (blocks) solely because a task is orphan                 -> "blocking_on_orphan"
  - `new-task` refuses to create a task that resolves to no milestone        -> "blocking_escape_hatch"
  - warning/nudge text claims the intake flow was or wasn't followed         -> "overclaiming_text"
After:
  - in a project with an orphan task: `check` exits 0 and prints a WARN line naming the intake flow;
    `new-task` (orphan) exits 0 and prints a nudge; a task WITH a milestone produces neither; all text
    speaks of structure, not the act.
Assumptions (confirm before building):
  - [x] "orphan" = a state.json task whose `milestone` is null — the only observable footprint
        (confirmed in cmd_new_task: `milestone = args.milestone or state.get("active_milestone")`)
  - [x] `check` today is pass/fail only (no warn tier); the WARN tier is new and MUST keep exit 0
        (confirmed in cmd_check: `if failed: raise SystemExit(1)` — warnings must not feed `failed`)
  - [x] `add.py` is mirrored byte-identical (`.add/tooling/add.py` ↔ `add-method/tooling/add.py`) —
        the build edits BOTH and a parity test guards it
  - [x] honesty rule (structure, not the act): the guard CANNOT observe whether intake actually ran —
        an agent could hand-fabricate a milestone+task. It guards the footprint only. (MILESTONE.md)
  - [x] warn-never-block + shipped-structure-only (intake→milestone, not v7 one-approval/auto) — frozen
        in v8-1 MILESTONE.md shared decisions

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: check warns on an orphan task but still passes
  Given a project with a task that has no milestone
  When I run `add.py check`
  Then a WARN line names the task and the intake / `/add` flow
  And the exit code is 0 (warn-never-block)        # reject: blocking_on_orphan

Scenario: check is clean when every task has a milestone
  Given a project where the only task is attached to a milestone
  When I run `add.py check`
  Then there is no orphan WARN line
  And the exit code is 0

Scenario: new-task with no milestone nudges but still creates
  Given a fresh project with no active milestone
  When I run `add.py new-task lonely`
  Then stdout nudges toward the intake / `/add` flow
  And the task `lonely` is created and active (exit 0)   # reject: blocking_escape_hatch

Scenario: new-task with a milestone does not nudge
  Given a project with an active milestone
  When I run `add.py new-task attached`
  Then stdout does NOT print the orphan nudge
  And the task is linked to the milestone

Scenario: the text labels structure, not the act
  Given a project with an orphan task
  When I run `add.py check` and `add.py new-task` (orphan)
  Then the warning/nudge says "outside a milestone" / "not attached"
  And it never claims the intake flow was or wasn't followed   # reject: overclaiming_text

Scenario: check --json carries warnings without inflating failed
  Given a project with an orphan task
  When I run `add.py check --json`
  Then the object has a `warnings` list and `warned` >= 1
  And the orphan task is NOT in `failed` and `failed` is unchanged
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
SURFACE  add.py check  — gains a WARNING tier, separate from PASS/FAIL:
  - for each task with state.json `milestone is None`: print a line `WARN  task '<slug>' is outside
    a milestone — size it via the /add intake flow (or attach with --milestone)`
  - warnings do NOT feed `failed`; exit stays 0 when failed==0 (warn-never-block)
  - text mode: WARN lines print after PASS/FAIL lines; summary gains "(N warnings)" when N>0
  - --json mode: object gains "warnings": [ {"name","reason"} ... ] and "warned": N;
    "passed"/"failed" semantics UNCHANGED; an orphan task is never counted in "failed"

SURFACE  add.py new-task <slug>  — when the resolved milestone is None:
  - the task + state entry are still created and made active (exit 0)  [escape hatch preserved]
  - print a nudge line: `note: '<slug>' is not attached to a milestone — size it via /add (intake),
    or pass --milestone <id>`

TEXT INVARIANT (honesty)  every warning/nudge speaks of STRUCTURE — "outside a milestone" /
  "not attached to a milestone" — and NEVER asserts the intake flow "was" or "was not" followed.

MIRROR   the edit lands byte-identical in BOTH `add.py` trees; a parity assertion guards it.
GUARD    add-method/tooling/test_v8_1_orphan_guard.py — six tests, one per scenario (in-process
         add.main harness, like test_machine_state.py) + addpy md5 parity.
reject codes: blocking_on_orphan · blocking_escape_hatch · overclaiming_text
NON-GOAL: blocking anything; detecting whether intake actually ran; touching v7 one-approval/auto;
          changing the 7-phase sequence; any check that an orphan-attached task is "valid".
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (HUMAN-approved at the seam — AskUserQuestion "Approve & freeze", 2026-06-02)

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Behavioral (real add.py behavior via in-process `add.main`, like test_machine_state.py): a temp
project per test (`init` in a tmpdir; `import add`; `_run(argv)` → (code, stdout, stderr)). After
`init` there is no active milestone, so `new-task t` is naturally orphan — the case under test.
Lives in `add-method/tooling/test_v8_1_orphan_guard.py`.

Plan (one test per scenario):
  - test_check_warns_on_orphan_but_passes:   orphan task → WARN line names intake; exit 0          [RED]
  - test_check_clean_when_attached:          task under a milestone → no orphan WARN; exit 0        [RED]
  - test_new_task_orphan_nudges_and_creates: no active milestone → nudge printed; task created      [RED]
  - test_new_task_attached_no_nudge:         active milestone → no nudge; task linked               [RED]
  - test_text_labels_structure_not_act:      WARN+nudge say "outside/not attached"; never "followed" [RED]
  - test_check_json_warnings_not_failed:     --json has warnings[]/warned>=1; orphan not in failed   [RED]
  - test_addpy_parity:                       md5(.add/tooling/add.py) == md5(add-method/.../add.py)  [RED→guards mirror]

RED now: the WARN tier and the nudge don't exist yet; check is pass/fail only and new-task is silent
on orphan. (addpy_parity may be GREEN pre-build if trees are already identical — it guards the build
keeps them identical, the one test allowed to start green.)

Tests live in: `add-method/tooling/test_v8_1_orphan_guard.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): **warn-never-block** — orphan tasks produce WARN lines (`check`) or
a nudge (`new-task`), NEVER a FAIL or a refusal; `check` exit stays 0 (warnings don't feed `failed`).
Code lives in: `add-method/tooling/add.py` (cmd_check WARN tier + cmd_new_task nudge), mirrored
**byte-identical** to `.add/tooling/add.py` (`cp`, md5 verified).
Constraints: did NOT touch the frozen contract or any test. (The two tmp-path false-greens were fixed
at RED, BEFORE the build — see §4 / the TDD delta — not during build.) stdlib only, no new deps.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — orphan-guard **7/7**; full tooling suite **173 OK**; `add.py check` (repo root)
      **116 passed, 0 failed, 3 warnings, exit 0** (3 real legacy orphans warned, not blocked)
- [x] coverage did not decrease — +7 behavioral tests (in-process add.main harness)
- [x] no test or contract was altered during build — frozen contract @ v1 untouched; the two
      false-green path-matches were fixed at RED (before build), then the suite stayed fixed
- [x] impl matches the frozen contract — advisor caught the text summary drifting from frozen §3
      (`, N warnings` vs the contracted `(N warnings)`); matched the IMPL to the contract (rule 3 —
      never deviate from the frozen shape; matching impl→contract is always allowed). No test broke.
- [x] concurrency / timing — N/A (synchronous CLI, no shared state during a run)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no new deps
- [x] layering & dependencies — `add.py` mirrored byte-identical across both trees (md5 parity test
      `test_addpy_parity` guards it); warn tier is additive (JSON gains `warnings`/`warned`, `failed` unchanged)
- [x] a person reviewed and approved the change — Tin Dang, human diff review, gate PASS 2026-06-02

Blind-spot (completeness-critic): the WARN fires for EVERY legacy orphan task on every `check`
(3 in this repo: add-check, quickstart-guide, milestone-layer) — accurate, but potentially noisy as a
standing CI signal. OBSERVE candidate: a way to acknowledge/silence known-legacy orphans (e.g. a
`milestone: "legacy"` marker) so the nudge targets NEW drift, not history. Not a blocker — it is a
true signal, and warn-never-block means it never fails CI.

### GATE RECORD
Outcome: PASS   <!-- human gate, conservative autonomy: 7/7 · suite 173 OK · check 116/0 exit 0 · parity verified · frozen §3 honored (summary reconciled) -->
Reviewed by: Tin Dang (human diff review) · date: 2026-06-02

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the orphan WARN count from `check --json` (`warned`) over time —
a *rising* count means new tasks are being created outside the intake flow (the drift this guards);
a flat count = only the known legacy orphans.
Spec delta for the next loop: the guard nudges but cannot distinguish *legacy* orphans (created before
milestones existed) from *new* drift. Next loop: a legacy-acknowledge marker so the nudge sharpens onto
new orphans. Bigger open thread (unchanged from v8): nothing yet proves an agent *runs* intake at
runtime — this guards the footprint, the honest limit of what a CLI can observe.

### Competency deltas
- [TDD · folded] A behavioral test's substring assertion can false-GREEN off its OWN test harness —
  the tmpdir was named `add-orphan-guard-XXXX`, so a `/add` assertion matched the absolute path the
  tool prints, not any nudge. Lesson: assert a message-specific phrase ("not attached to a milestone")
  the environment can't accidentally satisfy; never a token that also appears in paths/scaffold.
  Evidence: `test_new_task_orphan_nudges_and_creates` passed pre-build until hardened. Caught at RED.
  [folded foundation-version 8 → CONVENTIONS.md "Assert a message-specific phrase, not an ambient token"]
- [ADD · folded] A runtime guard can only observe STRUCTURE (state.json `milestone is null`), never the
  ACT (did an intake conversation happen). Naming this at SPEC time — "nudge", not "proof" — kept the
  Must satisfiable and avoided a build-time weakened test. Evidence: the option's pitch said "proves an
  agent ran intake"; the buildable spec is narrower and honest. (advisor-surfaced before drafting.)
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Never self-gate" (a guard sees structure, not the act)]
- [SDD · folded] Adding a third output tier (WARN) to a pass/fail surface stays backward-safe when it is
  ADDITIVE: `--json` gained `warnings`/`warned`, `passed`/`failed` semantics unchanged, exit code
  unchanged — so no existing consumer (machine_state tests) broke. Evidence: full suite 173 OK.
  [folded foundation-version 8 → PROJECT.md §Spec "Surfaces evolve additively"]
