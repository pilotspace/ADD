# 04 · Build — red to green, inside the lines

[← 03 Direction — rules, assumptions, checks, the seal](./03-direction.md) · [Contents](./README.md) · Next: [05 Verify — evidence, residue, refute, verdict →](./05-verify.md)

---

## The beat the AI is best at

Build works because Direction already removed the ambiguity. The agent is no longer guessing what to build: it has the task's RULES, its ASSUMPTIONS, its `scope:` and `gives:`, and a set of failing checks that define "done" exactly. Its job is narrow and checkable — turn the red checks green.

This is the difference between ADD and vague-prompt coding. The same agent that produces confident nonsense from "build me a transfer feature" produces correct, bounded code from "make these specific failing checks pass without changing them". The agent did not change; the direction did.

## Three lines you do not cross

1. **Never edit a sealed check or the contract to get green.** A hard check is telling you about the code, not about the check. Weakening it inverts the method: the code would then be judging itself. Verify will catch it anyway — `git diff <freeze> HEAD` on the sealed files must print nothing.
2. **Never move a `gives:` surface silently.** Internals are free; the shape other code depends on is not.
3. **Stay inside `scope:`.** Needing another path means the plan was wrong — which is a refreeze, not a quiet edit.

Every other test is yours. Write throwaway tests to debug, delete them when they stop paying, refactor freely. Only the checks named in CHECKS are sealed.

## When the direction was wrong

Sometimes the build shows that a rule was wrong, a check was aimed at the wrong thing, or scope must grow. That is legitimate, and it has one honest path: edit the task file and the checks, write why under `## LOG`, and commit

```bash
git commit -m "refreeze(transfer-own-accounts): C6 used the wall clock; now uses the injected clock"
```

Verify then diffs against the **latest** freeze or refreeze commit. The history shows what changed and why — which is the difference between a changed mind and a weakened test.

## Work in small, reviewable steps

Commit build progress normally. Keep each step small enough that its diff can be read in full: one enormous change that turns everything green at once is not a triumph, it is an unreviewable blob — and Verify's residue read (next chapter) depends on the diff being readable.

## The iteration loop

```
write code → run the task's check: command → some still fail
   → adjust → … → all green → run the regression: command → hand to Verify
```

The loop is tight and self-directed. The agent runs the checks, reads what fails, and adjusts. Run the full `regression:` suite before calling the build done: a green on a filtered run says nothing about checks outside the filter.

## Common mistakes

- **Batches too large to read.** Shrinks the residue review to approving without reading.
- **Patching around a failure in someone else's check.** A red test the task does not own means the build crossed a boundary. Find out why before continuing.
- **Trusting a filtered run.** A scoped run was green; the full suite was never run. Run `regression:`.
- **"All checks pass" as the finish line.** It is necessary, not sufficient — that is what Verify is for.

## Exit check

- [ ] Every check in CHECKS passes.
- [ ] No sealed file changed since the latest freeze or refreeze commit.
- [ ] Every edit is inside `scope:`; no `gives:` surface moved.
- [ ] The `regression:` suite is green.
- [ ] The work is committed and the tree is clean.
