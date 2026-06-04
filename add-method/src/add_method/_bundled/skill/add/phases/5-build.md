# Phase 5 — Build (AI writes the code)

Goal: implement the feature so EVERY failing test passes — without changing any
test or the contract. This is the only phase the AI leads. It works because §1–§4
removed all ambiguity. Write code into `.add/tasks/<slug>/src/`.

## Work in small batches

Pick ONE task-sized slice, restate the tests it must satisfy, implement, run
tests, iterate to green. Keep each batch small enough to review in full — you
cannot move faster than you can verify.

## The cardinal rule

**Never weaken or delete a test to make it pass, and never edit the frozen
contract.** That makes the code judge itself. A genuine need to change either is a
change request back to Specify. Honor the feature-specific safety rule named in §5
(e.g. atomic balance update) — the one property tests alone may not force.

## AI prompt

> Read §1, §3, §4, and CONVENTIONS. Make EVERY failing test pass, one small batch
> at a time. Constraints: do NOT change any test; do NOT change the contract; honor
> the §5 safety rule; use only allow-listed packages; stop and ask if unclear.
> Report which tests pass and exactly what changed.

## Exit gate

- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test and no contract modified by the AI.
- [ ] No dependency outside the allow-list.
- [ ] Change small enough to review in full.

## Next

`python3 .add/tooling/add.py advance` → read `phases/6-verify.md`.
Book: `docs/07-step-5-build.md`.

> Under `autonomy: auto` (the default) Build and Verify run together as one dynamic,
> evidence-auto-gated run — not two manual stops. See `run.md`.
