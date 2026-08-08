# Appendix E · Checklists

[← Appendix D Worked example](./appendix-d-worked-example.md) · [Contents](./README.md) · Next: [Appendix G References →](./appendix-g-references.md)

Every exit check in the book, collected for quick use. Print this page.

Each list is the one from its chapter — [03 Direction](./03-direction.md),
[04 Build](./04-build.md), [05 Verify](./05-verify.md), [06 The loop](./06-the-loop.md).
Where a line is something the **engine refuses**, it says so; everything else is
discipline the engine cannot see for you.

---

## Setup (once per project)

- [ ] The pipeline runs and is green on the empty skeleton.
- [ ] `add init` has run; `.add/` holds the five living specs and `add status` answers.
- [ ] The model behind the work is recorded.
- [ ] `sensitive_paths:` in `.add/index.md` names the paths that must floor to a human.
- [ ] At least one persona is seeded for the domain, so a sensitive task has a lens to route to.

## Direction

- [ ] Every required behavior is a Must; every rejection is a named error code; the success state-change is stated.
- [ ] The assumptions are ordered lowest-confidence first, with the one `⚠` flag carrying *why* + *cost* — or, for trivial scope, an honest "none material" that still names the single biggest risk.
- [ ] "Existing behavior" assumptions carry grep/line citations; wiring claims name the production caller chain.
- [ ] The contract shape is authored into `gives:`, versioned in intent, and every rejection has a contracted response.
- [ ] `scope:` lists the files or directories the build may touch.
- [ ] There is one check per Must, per Reject, and per behavior-changing edge — each with a `covers:` referent. *(Engine: an uncovered rule or edge blocks the gate.)*
- [ ] The suite (or the acceptance list) runs in the pipeline and is **red for the right reason** — no lying reds; an unimplemented path fails because it is unimplemented.
- [ ] Checks assert observable behavior, not internals.
- [ ] Collateral checks for globally-enumerated things are listed by exact name.
- [ ] Arithmetic is checked: fixtures can actually reach green against the frozen constants.
- [ ] A person froze the node. *(This is the single human decision that opens Build.)*

## Build

- [ ] Every red check is now green.
- [ ] No check and no frozen contract was modified by the AI.
- [ ] Every edit stayed inside the node's `scope:`.
- [ ] The change is small enough to review in full.

## Verify

- [ ] The receipt is **fresh** (every in-`scope:` file unchanged since the run) and **bound** (every check the rules `covers:` passed). *(Engine: no receipt, a stale receipt, or a receipt whose exit code is non-zero is refused.)*
- [ ] No check or frozen contract was altered during the build.
- [ ] Concurrency/timing of the risky operation is safe.
- [ ] No exposed secrets, injection openings, or unexpected dependencies.
- [ ] Layering and dependency boundaries are respected.
- [ ] Deep check: for code, every new symbol is referenced (wiring) and no new dead code was introduced; for prose, a semantic read is recorded.
- [ ] A security finding was escalated, not waved through. *(Engine: a security-floored node cannot record `RISK-ACCEPTED`, and its `PASS` needs a named lens.)*
- [ ] Exactly one outcome is recorded — `PASS` / `RISK-ACCEPTED` / `HARD-STOP` — with an accountable owner.

## The loop

- [ ] Released behind a flag or gradual rollout.
- [ ] Checks reused as production monitors.
- [ ] What was learned is recorded with `add learn`, against evidence.
- [ ] Confirmed lessons are folded into the living specs (`add fold`).
- [ ] The milestone stays open until its exit criteria are met; anything reopened went back through the loop, not around it.

---

## Master shippable checklist

A change is shippable only when all are true:

- [ ] Direction complete: behavior stated, rejections named, assumptions ranked lowest-confidence first with the biggest risk flagged.
- [ ] Wiring and "existing behavior" assumptions carry grep/line citations; wiring claims name the production caller chain.
- [ ] Every rule and every behavior-changing edge has a check bound to it by `covers:`.
- [ ] The contract shape is authored and the node was frozen by a person.
- [ ] The suite was red before the build, for the right reason.
- [ ] Collateral checks listed by exact name; arithmetic checked against the frozen constants.
- [ ] All checks green; no check and no frozen contract touched by the AI; every edit inside `scope:`.
- [ ] The receipt is fresh and bound — the gate is reading evidence, not a plausible diff.
- [ ] Wiring trace recorded: every new symbol reachable from the production entry point.
- [ ] Concurrency, security, and architecture checked by a person; any security finding escalated.
- [ ] Gate outcome recorded with an accountable owner.
- [ ] Released behind a flag, with monitors in place.
