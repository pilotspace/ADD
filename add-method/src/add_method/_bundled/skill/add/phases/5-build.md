# Phase 5 — Build (AI writes the code)

Goal: implement the feature so EVERY failing test passes — without changing any
test or the contract. This is the only phase the AI leads; §1–§4 removed all
ambiguity. Write code into `.add/tasks/<slug>/src/`.

## Work in small batches

Pick ONE task-sized slice, restate its tests, implement, iterate to green.
Keep each batch small enough to review in full.

## Declaring the scope of impact (Scope + Strategy)

§5 opens with two declarations, drafted with the bundle and frozen by the §3 approval — never invented mid-build:

- **Scope (may touch)** — the allowlist of files the build may write (backticked tokens). A file outside it is a **STOP → change request** back to Specify, never improvisation.
- **Strategy (ordered batches)** — the planned build order; guidance, not enforced.

Enforced: a completing verify gate refuses an out-of-scope build (`scope_violation` → self-heal).

## Persona overlay (optional)

You may load the active `.add/personas/<slug>.md` as a domain **overlay** atop `SOUL.md` (SOUL = voice/trust; persona = domain **stance**) — name it in §5. SOUL.md is **human-owned**: the overlay never rewrites it (`soul.md`). Advisory — it never lowers a gate; security still **HARD-STOPs**.

## The cardinal rule

**Never weaken or delete a test to make it pass, and never edit the frozen
contract.** A genuine need to change either is a change request back to Specify. Honor the §5 safety rule (e.g. atomic balance update).

## AI prompt

<prompt>
Role: implement the feature so EVERY failing test passes — the build phase.
Read first: §1 · §3 · §4 · CONVENTIONS.
Objective: every §4 test green, one small batch at a time.
Steps:
  1. Make EVERY failing test pass, honoring the §5 safety rule.
  2. Report which tests pass and exactly what changed.
Never: change a test or the contract; use a package off the allow-list; or push past unclear instead of asking.
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

> **Advisor · Confidence** — delegate a well-scoped batch (advisor.md); self-score before presenting green, refine while cheap (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/6-verify.md`.
Book: `docs/07-step-5-build.md`.

> Under `autonomy: auto` Build and Verify run together as one evidence-auto-gated run. See `run.md`.
>
> **Honest redo.** A confirmed cheat returns the task HERE — revert the tampered file or de-overfit src, then advance again (the bounded self-heal loop, `run.md`; capped, then HARD-STOPs to the human). Never weaken a test or edit the frozen contract to pass.
