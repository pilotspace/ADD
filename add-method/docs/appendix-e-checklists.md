# Appendix E · Checklists

[← Appendix D Worked example](./appendix-d-worked-example.md) · [Contents](./README.md) · Next: [Appendix G References →](./appendix-g-references.md)

Every exit check in the book, collected. Each list comes from its chapter — [07 Setup](./07-setup-and-lanes.md), [03 Direction](./03-direction.md), [04 Build](./04-build.md), [05 Verify](./05-verify.md), [06 Learn](./06-the-loop.md).

---

## Setup (once per project)

- [ ] The skill is installed (`.claude/skills/add/`), or the agent's context file carries the managed ADD block.
- [ ] `.add/PROJECT.md` has `goal:`, `invariants:` and `test_cmd:`, and the test command runs green on the current tree.
- [ ] The five specs exist under `.add/specs/`, each with `## Now`, `## Decisions that bind`, `## Deltas`.
- [ ] The model behind the work is recorded.

## Sizing

- [ ] Anything touching security · data · architecture, or a consumed surface, is at least a Task.
- [ ] Quick only for mechanical or small behavior: ≤3 adjacent files, one sitting, no unknowns.
- [ ] A question whose answer would change the contract goes to Explore first.

## Direction

- [ ] Grounded in the code the task touches and the binding decisions in `.add/specs/`.
- [ ] Every required behavior is a Must, every refusal a Reject with a named error, each citing its source.
- [ ] Every public surface swept on `who · which · when · absent · order · experience`; each silence is one assumption line, or retired with a reason; cheap guesses checked and marked `found:`.
- [ ] A silence about who may act or see takes the least-privilege reading: only the owner.
- [ ] `scope:`, `gives:`, `check:` and `regression:` written.
- [ ] Every Must and Reject covered by a check aimed at a plausible wrong implementation; checks in files of their own.
- [ ] Checks send inputs the way a real caller sends them: the body itself malformed as well as each field, and every value form the spec allows.
- [ ] The checks ran and failed because the behavior is absent.
- [ ] `status: build`; task file and check files committed as `freeze(<slug>)`.

## Build

- [ ] Every check in CHECKS passes.
- [ ] No sealed file changed since the latest freeze or refreeze; any change of contract is a `refreeze(<slug>)` commit with its reason under `## LOG`.
- [ ] Every edit inside `scope:`; no `gives:` surface moved.
- [ ] The `regression:` suite is green; the work is committed.

## Verify

- [ ] `git diff <freeze> HEAD -- <sealed files>` prints nothing.
- [ ] `check:` and `regression:` ran fresh on a clean, committed tree; real exit codes and counts recorded.
- [ ] Residue read: security, concurrency, architecture, plus the kind's lens (migration reversibility · rollback path · keyboard and screen-reader reach · retries and idempotency).
- [ ] New code is wired: each new entry point has a production caller.
- [ ] One to three refute probes derived from the sealed rules; a fresh subagent only for security work, a cold reread otherwise.
- [ ] Exactly one verdict in `## EVIDENCE` — `PASS`, `RISK-ACCEPTED` (non-security, with reason and owner) or `HARD-STOP` — and the `verify(<slug>): <verdict>` commit made.
- [ ] A security finding is a `HARD-STOP` at the top of the report.

## Learn and report

- [ ] Lessons recorded as deltas with evidence in the matching spec.
- [ ] Deltas that held are promoted to `## Decisions that bind`.
- [ ] Milestone EXIT boxes ticked only with evidence on the line.
- [ ] The report leads with HARD-STOPs and open risks, then per task: goal, verdict, freeze commit, evidence, every assumption taken — costliest if wrong first.
- [ ] `PROJECT.md`'s CARD updated (`state:`, `next:`).

---

## Master shippable checklist

A change is shippable only when all are true:

- [ ] Rules stated, refusals named, every silence written as an assumption.
- [ ] Every rule covered by a check that would fail without it.
- [ ] The checks were red for the right reason before the build, and sealed in a `freeze` commit.
- [ ] The sealed files are unchanged since the latest freeze or refreeze.
- [ ] Task checks and the full suite green, fresh, on the committed tree — with the output recorded.
- [ ] Security, concurrency and architecture read; any security finding is a `HARD-STOP`.
- [ ] Someone other than the builder tried to break it, for security, data or architecture work.
- [ ] One verdict in `## EVIDENCE`, and the human has the report listing every assumption.
