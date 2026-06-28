# Phase 5 — Build (AI writes the code)

Goal: implement the feature so EVERY failing test passes — without changing any
test or the contract. This is the only phase the AI leads. It works because §1–§4
removed all ambiguity. Write code into `.add/tasks/<slug>/src/`.

## Work in small batches

Pick ONE task-sized slice, restate the tests it must satisfy, implement, run
tests, iterate to green. Keep each batch small enough to review in full.

## Declaring the scope of impact (Scope + Strategy)

§5 of TASK.md opens with two declarations, drafted WITH the specification bundle and frozen by the §3 approval — never invented mid-build:

- **Scope (may touch)** — the allowlist of every file the build may write (backticked tokens). Needing a file outside the declared Scope is a **STOP → change request** back to Specify, never improvisation.
- **Strategy (ordered batches)** — the planned build order. Guidance, not enforced.

Enforced: a completing verify gate refuses an out-of-scope build (`scope_violation` → self-heal); `add.py check` surfaces it.

## The cardinal rule

**Never weaken or delete a test to make it pass, and never edit the frozen
contract.** A genuine need to change either is a change request back to Specify. Honor the feature-specific safety rule named in §5 (e.g. atomic balance update).

## AI prompt

<prompt>
Role: implement the feature so EVERY failing test passes — the build phase.
Read first: §1 · §3 · §4 · CONVENTIONS.
Objective: every §4 test green, one small batch at a time.
Steps:
  1. Make EVERY failing test pass, one small batch at a time, honoring the §5 safety rule.
  2. Report which tests pass and exactly what changed.
Never: change a test or the contract; use a package off the allow-list; or push past something unclear instead of asking.
</prompt>

## Exit gate

<exit_gate>
- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test and no contract modified by the AI.
- [ ] No dependency outside the allow-list.
- [ ] No file outside the declared §5 Scope was touched.
- [ ] Change small enough to review in full.
</exit_gate>

> **Advisor · Confidence** — delegate an independent, well-scoped batch (advisor.md); self-score before you present green, and refine while it is cheap (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/6-verify.md`.
Book: `docs/07-step-5-build.md`.

> Under `autonomy: auto` Build and Verify run together as one evidence-auto-gated run. See `run.md`.
>
> **Honest redo.** A confirmed cheat returns the task HERE — revert the tampered file or de-overfit src, then advance again. This is the bounded self-heal loop (`run.md`), capped: after the cap it HARD-STOPs to the human. Never weaken a test or edit the frozen contract to pass.
