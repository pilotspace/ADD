# 04 · Build — red to green, inside scope

[← 03 Direction — rules, plan, checks](./03-direction.md) · [Contents](./README.md) · Next: [05 Verify — evidence, residue lenses, the gate →](./05-verify.md)

---

## The only beat the AI leads

This is the beat the AI is genuinely good at, and the only one where it should be doing the heavy lifting. It works precisely because Direction already removed the ambiguity: the AI is no longer guessing what to build. It has the task node's `## RULES` (what the code must do and must reject), its `## PLAN` (the frozen `gives:` contract and the `scope:` it may touch), and a suite of failing `## CHECKS` that define "done" exactly. Its task is narrow and checkable — turn the red checks green.

This is the difference between ADD and vague-prompt coding. The same agent that produces confident nonsense from "build me a transfer feature" produces correct, bounded code from "make these specific failing checks pass without changing them." The agent did not change; the direction did.

## The build prompt

The instruction is explicit about constraints, because the constraints are what keep the speed safe.

```
Read the task node — its RULES, its PLAN (the frozen `gives:` contract and its `scope:`),
and its CHECKS.
Write code so that EVERY red check passes.
Constraints:
  - Do NOT change any check.
  - Do NOT move the frozen `gives:` contract.
  - Stay inside the paths listed in `scope:`.
  - <feature-specific safety rule>.
  - Stop and ask if any requirement is unclear — do not guess.
Report which checks pass and exactly what you changed.
```

For the running example, the feature-specific safety rule is *"make the balance update atomic — debit and credit occur in a single transaction."* This is the one correctness property the checks alone may not force, so it is named directly to the builder — it is the riskiest assumption Direction wrote into `## RULES`.

## The three lines you may not cross

The build runs fast because Direction fixed *what* correct means. It stays safe because three lines hold, and crossing any of them is not a shortcut — it is a signal that the work has left its lane:

- **Change no check.** A check that is hard to pass is telling you something about the code, not about the check. Weakening or deleting it to reach green inverts the method: the code would then be judging itself.
- **Move no frozen `gives:` contract.** The build implements *against* the frozen interface. Its internals may change freely; its external shape may not. A genuine need to change the contract is a change request that returns to Direction, not a silent edit here.
- **Stay inside `scope:`.** The paths in the node's `scope:` are the freshness set the gate will hash. Touching a path outside it means the node is mis-scoped — fix the scope in Direction, do not sneak the edit.

The strategy the build follows was set in Direction, in the node's `## PLAN`. The builder may improve on it as reality pushes back, and reports the strategy it actually used at Verify — so the record reflects what happened, not what was planned.

## Work in small batches

Direct the AI one task at a time, and keep each task small enough that its result can be reviewed in full. This is a direct application of the principle *you cannot move faster than you can verify.* A single enormous change that turns the whole suite green at once is not a triumph — it is an unreviewable blob. Small batches keep the verification beat (next chapter) tractable and keep a human genuinely in the loop.

Progress for a task in build is read straight from the working tree — `git status` intersected with the node's `scope:`. It is never stored and always current, so there is no separate status to keep in sync.

## The iteration loop

```
AI writes code → run the checks → some still fail
   → AI iterates → ... → all green → hand to Verify
```

The loop is tight and largely self-directed within a task: the AI runs the checks, sees what fails, and adjusts. Your attention is needed at the boundaries — defining the task going in, and reviewing the result coming out — not on each internal iteration. When every check is green and the residue is clean, the task advances to Verify.

## The cardinal rule: never change a check to pass

An AI under pressure to make a suite green has an available shortcut: weaken or delete the failing check. This must be forbidden explicitly and caught reliably. A check changed to fit the code inverts the entire method. If you find a check was altered during the build, reject the change outright and re-prompt with the constraint restated.

The same applies to the contract: the build may not edit the frozen `gives:`. A genuine need to change either the checks or the contract is a change request that returns to Direction, re-freezes, and comes forward again — never a quiet patch.

## Common mistakes

- **Batches too large to review.** Shrinks verification to approving without reading.
- **Crossing a check outside the task's own suite.** A failure in a check the node does not own means the build crossed a boundary. Find the node that owns it before continuing; do not patch around it.
- **Accepting "all checks pass" without reading the change.** Passing checks are necessary, not sufficient — the next beat exists for exactly this reason.

## Exit check

- [ ] Every red check is now green.
- [ ] No check and no frozen contract was modified by the AI.
- [ ] Every edit stayed inside the node's `scope:`.
- [ ] The change is small enough to review in full.

## If the check fails

If the AI weakened a check, reject and re-prompt with the constraint restated. If an edit strayed outside `scope:`, the node is mis-scoped — return to Direction and fix the scope rather than expanding the build. If the batch is too large to review, ask the AI to split the work and resubmit. Only once the exit check passes, with green checks and clean residue, does the change proceed to verification.
