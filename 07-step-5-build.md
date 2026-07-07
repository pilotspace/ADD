# 07 · Step 5 — Build

[← 06 Step 4 Tests](./06-step-4-tests.md) · [Contents](./README.md) · Next: [08 Step 6 Verify →](./08-step-6-verify.md)

> **Purpose:** have the AI implement the feature so that every failing test passes.
> **Produces:** working code, plus the evidence that the tests now pass.
> **Person's job:** direct, in small batches. **AI's job:** implement.

---

## The only step the AI leads

This is the step the AI is genuinely good at, and the only one where it should be doing the heavy lifting. It works precisely because the previous four steps removed all the ambiguity: the AI is no longer guessing what to build: it has a spec, a set of scenarios, a frozen contract, and a suite of failing tests that define "done" exactly. Its task is narrow and checkable — turn the suite green.

This is the difference between AIDD and vague-prompt coding. The same agent that produces confident nonsense from "build me a transfer feature" produces correct, bounded code from "make these specific failing tests pass without changing them." The agent did not change; the direction did.

## The build prompt

The instruction is explicit about constraints, because the constraints are what keep the speed safe.

```
Read SPEC.md, contracts/<name>.md, and tests/<name>_test.py.
Implement the feature so that EVERY test passes.
Constraints:
  - Do NOT change any test.
  - Do NOT change the contract.
  - <feature-specific safety rule>.
  - Stop and ask if any requirement is unclear — do not guess.
  - Use only packages listed in dependencies.allowlist.
Report which tests pass and exactly what you changed.
```

For the running example, the feature-specific safety rule is *"make the balance update atomic — debit and credit occur in a single transaction."* This is the one correctness property the tests alone may not force, so it is named directly to the builder.

See `playbook/5_build.md` in [Appendix B](./appendix-b-prompts.md).

## Choosing the implementation strategy

The spec, contract, and tests fix *what* correct means; they deliberately do not fix *how* the build achieves it — and "how" is itself a decision worth making explicitly rather than letting the first plausible implementation win. §5 of the task file declares it as four small **strategy facets**, each derived from work already done, never invented fresh at build time:

- **Approach (domain strategy)** — the core technique and why it fits this task's domain: an algorithm, a data model, a migration path, a prose structure, a UX flow. It comes from the framings §1 already weighed, stated in the loaded persona's domain vocabulary.
- **Data strategy** — the shapes and access patterns the work realizes; it must agree with the schema line the frozen contract states.
- **Pattern** — the domain pattern the build follows, citing the convention (§0 Honors / CONVENTIONS.md) it extends.
- **Optimization stance** — what, if anything, is being optimized and to what budget: latency, memory, token cost, readability. "Correctness-first, no budget" is a legitimate answer; silence is not, because the stance you declare here is the monitor you install at Observe.

The facets are drafted at the tests→build crossing — the moment the red suite makes the shape concrete and a challenge is still cheap — with the facet you trust least ⚠-marked (on a high-risk task, that flag is the natural advisor consult). They are guidance, not a gate: the builder may improve on them as reality pushes back, and reports the strategy actually used at Verify, where it feeds the task's decision record.

## Work in small batches

Direct the AI one task at a time, and keep each task small enough that its result can be reviewed in full. This is a direct application of the principle *you cannot move faster than you can verify.* A single enormous change that turns the whole suite green at once is not a triumph — it is an unreviewable blob. Small batches keep the verification step (next chapter) tractable and keep a human genuinely in the loop.

## The iteration loop

```
AI writes code → pipeline runs the tests → some still fail
   → AI iterates → ... → all green → hand to Verify
```

The loop is tight and largely autonomous within a task: the AI runs the tests, sees what fails, and adjusts. Your attention is needed at the boundaries — defining the task going in, and reviewing the result coming out — not on each internal iteration.

## The cardinal rule: never change the test to pass

An AI under pressure to make a suite green has an available shortcut: weaken or delete the failing test. This must be forbidden explicitly and caught reliably. A test changed to fit the code inverts the entire method — the code is now judging itself. If you find a test was altered during the build, reject the change outright and re-prompt with the constraint restated.

The same applies to the contract: the build implements *against* the frozen contract and may not edit it. A genuine need to change either is a change request that returns to an earlier step.

## How much autonomy

The autonomy granted in this step should match the evidence and your review capacity (see [11 Governance](./11-governance.md)):

- Where the area is new or risky, the AI proposes and a person reviews every change.
- Where the contract and tests are solid, the AI generates freely and a person reviews each batch.
- Only in narrow, well-tested areas, with a full evidence bundle attached, may the AI integrate its own work.

## Common mistakes

- **Batches too large to review.** Shrinks verification to approving without reading.
- **Letting the AI add unknown dependencies.** The allow-list check in the pipeline should block this automatically; if it does not, the supply-chain risk is real (an AI may invent a plausible package name that an attacker has registered).
- **Accepting "all tests pass" without reading the change.** Passing tests are necessary, not sufficient — the next step exists for exactly this reason.

## Exit check

- [ ] All tests pass.
- [ ] Test coverage did not decrease.
- [ ] No test and no contract was modified by the AI.
- [ ] No dependency outside the allow-list was added.
- [ ] The change is small enough to review in full.

## If the check fails

If the AI weakened a test, reject and re-prompt. If it added an out-of-allow-list package, the pipeline blocks it; have the AI find an approved alternative or raise the package for human approval. If the batch is too large to review, ask the AI to split the work and resubmit. Only once the exit check passes does the change proceed to verification.

And in the other direction: if the *verify* gate later finds a confirmed cheat — a tamper, or a build that gamed the green (overfit to the fixtures, vacuous asserts, stubbed-away logic) — the task returns *here* for an honest redo. That return is the **bounded self-heal loop** (see the run chapter): revert the tampered file or de-overfit the code, then advance again. It is capped — after the cap a confirmed cheat HARD-STOPs to the human rather than looping forever, and a gamed green is never auto-passed.
