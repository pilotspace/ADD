# TASK: Runnable Quickstart: GETTING-STARTED.md

slug: quickstart-guide · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Must:
  - take a brand-new user from install to a PASS gate using the book's transfer example
  - every shell command shown must be real, copy-pasteable, and actually run
  - teach the cross-session resume workflow (`add.py status` as the entry point)
  - map each step to its book chapter (`.add/docs/`) for deeper reading
  - be short enough to finish in ~10 minutes (onboarding, not the full book)
After:
  - a reader who follows it has one task at phase=done with gate=PASS
Reject:
  - a documented command that errors or does not exist -> "broken_command"
  - a step that needs a concept not yet introduced       -> "out_of_order"
Assumptions (confirm before building):
  - [x] lives at `add-method/GETTING-STARTED.md`, linked from README
  - [x] uses the transfer worked-example for continuity with the book
  - [x] the tooling-command spine is covered by an executable test; the creative
        fill-in-the-spec steps are prose (cannot be unit-tested)

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: new user reaches a PASS following the guide
  Given a fresh project and the guide's documented command spine
  When the spine is executed in order (init -> new-task -> advance... -> gate PASS)
  Then the project ends with one task at phase=done and gate=PASS

Scenario: guide teaches the resume entry point
  Given the guide text
  When I search it
  Then it contains `add.py status` as the "where am I / resume" command

Scenario: no broken command (broken_command)
  Given every `add.py <cmd>` shown in the guide
  When checked against the tool's real subcommands
  Then each one is a recognized command (else the build is rejected)

Scenario: install + check are documented
  Given the guide text
  When I search it
  Then it contains `npx @mrq/add init` and `add.py check`
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Artifact: add-method/GETTING-STARTED.md (Markdown)

Required sections (in order):
  1. What you get / prerequisites
  2. Install            -> `npx @mrq/add init --name "..." --stage prototype`
  3. Orient             -> `python3 .add/tooling/add.py status`
  4. Start a feature    -> `add.py new-task transfer --title "..."`
  5. Walk the 7 phases  -> fill each TASK.md section + `add.py advance`
     (with transfer worked-example snippets) ending at `add.py gate PASS`
  6. Self-check         -> `add.py check`
  7. Resume next session-> `add.py status`
  8. Where to read more -> pointers into .add/docs/

Golden command spine (the part under executable test):
  new-task -> advance x5 (specify..build->verify) -> gate PASS  => done/PASS

Must literally contain the strings:
  "npx @mrq/add init" , "add.py status" , "add.py new-task" ,
  "add.py advance" , "add.py gate PASS" , "add.py check"
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 4 scenarios; the guide is the artifact under test.
Plan (test file: add-method/tooling/test_quickstart.py — shared-tooling deviation, see add-check):
  - test_guide_exists: GETTING-STARTED.md is present (RED until written)
  - test_guide_contains_required_commands: literal command strings from the contract present
  - test_documented_commands_are_real: every `add.py <cmd>` token in the guide is a real subcommand
  - test_golden_spine_reaches_pass: run new-task->advance x5->gate PASS in a temp project => done/PASS
Wire-up: `npm test` switches to unittest discovery so both test files run.
MUST run red (guide does not exist yet) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): every `add.py <cmd>` written in the guide must be a
REAL subcommand (the test enforces this) — no aspirational/invented commands. The
guide must not document `--flags` or commands that don't exist in this version.
Code lives in: `add-method/GETTING-STARTED.md` (the artifact) + test_quickstart.py.
Constraints: do NOT change any test or the frozen contract; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 20/20 via `npm test` (unittest discovery)
- [x] coverage did not decrease — added 4 guide tests; existing 16 still green
- [x] no test or contract was altered during build — contract FROZEN; tests untouched
- [x] concurrency / timing — N/A (a static doc + read-only test); golden spine runs serially
- [x] no exposed secrets / injection / unexpected deps — Markdown + stdlib test only
- [x] layering & deps follow CONVENTIONS.md — no new deps; doc lives in the package
- [x] a person reviewed — guide read end-to-end; all 6 documented commands verified real

### GATE RECORD
Outcome: PASS
Evidence: 20/20 tests green; guide documents only real commands; golden spine -> done/PASS
Reviewed by: Tin Dang · date: 2026-05-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): where new users get stuck (support questions);
whether the golden-spine test ever goes red after a CLI change (drift signal).
Spec delta for the next loop:
  - add an `alias add=...` one-liner per shell (done inline; expand if users ask)
  - consider a Vietnamese translation for the MRQ community
  - once `add.py guide` exists, link it from step 2 as the interactive companion
