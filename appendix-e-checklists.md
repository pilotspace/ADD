# Appendix E · Checklists

[← Appendix D Worked example](./appendix-d-worked-example.md) · [Contents](./README.md) · Next: [Appendix F Requirements matrix →](./appendix-f-requirements-matrix.md)

Every exit check in the book, collected for quick use. Print this page.

---

## Setup (once per project)

- [ ] Pipeline runs and is green on the empty skeleton.
- [ ] AI model pinned in `MODEL_REGISTRY.md`.
- [ ] Dependency allow-list exists; pipeline fails on anything outside it.
- [ ] `playbook/` contains the six prompts.

## Step 1 — Specify

- [ ] Every required behavior stated explicitly.
- [ ] Every rejection has a named error code.
- [ ] Success state-change described.
- [ ] Assumptions ranked lowest-confidence first; the 1–2 most-likely-wrong ⚠-flagged with why + cost (or an honest "none material" that still names the single biggest risk).
- [ ] "Existing behavior" assumptions carry grep/line citations; wiring claims name the production caller chain.

## Step 3 — Contract

- [ ] Contract versioned and `FROZEN`.
- [ ] Contract tests pass against the mock.
- [ ] Names match the glossary.
- [ ] Every spec rejection has a contracted response.

## Step 4 — Tests & Scenarios

- [ ] Every "Must" rule has a pass/fail scenario; every "Reject" rule has one too.
- [ ] Each scenario's result is a specific, observable fact; rejections assert what must stay unchanged.
- [ ] One test per primary scenario; minor variants noted as build-guidance.
- [ ] Suite runs in the pipeline and is red for the right reason.
- [ ] Tests assert behavior, not internals.
- [ ] Coverage target recorded.
- [ ] No `should_panic` lying reds — unimplemented paths use `todo!()` so they fail.
- [ ] Collateral tests for globally-enumerated things listed by exact name.
- [ ] Arithmetic checked: fixtures can reach green against frozen constants.

## Step 5 — Build

- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test or contract modified by the AI.
- [ ] No package outside the allow-list added.
- [ ] Change is small enough to review in full.

## Step 6 — Verify

- [ ] All tests pass (the evidence).
- [ ] Concurrency/timing of the risky operation is safe.
- [ ] No exposed secrets, injection, or unexpected dependencies.
- [ ] Layering and dependencies follow `CONVENTIONS.md`.
- [ ] Deep check: wiring trace recorded (every new symbol reachable from production entry point) and no dead code introduced.
- [ ] Was the green earned? Adversarial refute-read on the unchanged suite (no overfit, no vacuous asserts, no stubbed logic).
- [ ] Full-suite rerun by orchestrator (not only the agent's scoped run).
- [ ] A person reviewed and approved, **or** auto-resolved by the run (under `autonomy: auto`, no residue).
- [ ] Outcome recorded (`PASS` / `RISK-ACCEPTED` / `HARD-STOP`).

## The loop

- [ ] Released behind a flag or gradual rollout.
- [ ] Scenarios reused as production monitors.
- [ ] Learnings written back as a `SPEC.md` delta.

---

## Master shippable checklist

A feature is shippable only when all are true:

- [ ] Spec complete: behavior stated, rejections named, assumptions ranked lowest-confidence first with the biggest risk flagged.
- [ ] Wiring and "existing behavior" assumptions carry grep/line citations; wiring claims name the production caller chain.
- [ ] Every rule has a scenario.
- [ ] Contract frozen; contract tests green.
- [ ] A test per scenario; suite was red before the build (no `should_panic` lying reds).
- [ ] Collateral tests listed by exact name; arithmetic checked against frozen constants.
- [ ] All tests green; coverage held; tests and contract untouched by the AI.
- [ ] Wiring trace recorded: every new symbol reachable from production entry point.
- [ ] Adversarial refute-read confirms the green was earned (no overfit, no vacuous asserts, no stubbed logic).
- [ ] Full-suite rerun by orchestrator; not just the agent's scoped run.
- [ ] Concurrency, security, and architecture checked by a person.
- [ ] Gate outcome recorded with an accountable owner.
- [ ] Released behind a flag, with monitors in place.
