# 03 · Direction — rules, assumptions, checks, the seal

[← 02 The loop, and what is disposable](./02-the-flow.md) · [Contents](./README.md) · Next: [04 Build — red to green, inside the lines →](./04-build.md)

---

## Why Direction is first

Everything vague at this point does not stay vague: it becomes a confident wrong guess in the code, discovered late. The cheapest moment to remove an ambiguity is now, in a sentence, before anything depends on it. There is a diagnostic value too: **if you cannot state the rules, you do not yet understand the change well enough to build it.**

Direction produces one file, `.add/tasks/<slug>.md` (shape: [12 · The bundle](./12-bundle-format.md)), written in one pass, and ends with one commit that seals it.

## Ground first

Before writing a line of the task file, the agent reads what the task touches: the files, the signatures, the conventions, and the `## Decisions that bind` in the relevant `.add/specs/` files. If a persona fits the work, it loads that lens ([10 · Personas](./10-personas.md)). It reads what the task touches — never the whole repository.

## CARD — the goal in two lines

```markdown
## CARD
goal: move money between two accounts the caller owns
why: the first payments slice; later payment features build on this shape
```

## RULES — what it must do, and what it must refuse

Two kinds of rule, each with a stable id the checks will cite:

- **Musts** — `M<n>` — the behaviors the change must perform.
- **Rejects** — `R:<CODE>` — the inputs or situations it must refuse, each with a named error.

Only what the request said, or what the code and specs require — and each rule says where it came from: `(from: request | <file> | <spec>)`. Naming the errors matters: "reject bad amounts" is an instruction to guess; `R:AMOUNT_INVALID amount <= 0 is refused with 400 "amount_invalid"` is a rule a check can hold.

### ▶ Example — RULES

```markdown
## RULES
- M1 a transfer between two accounts the caller owns debits the source and credits the destination by the amount (from: request)
- R:AMOUNT_INVALID amount <= 0 is refused with 400 "amount_invalid"; no balance changes (from: request)
- R:SAME_ACCOUNT source == destination is refused with 400 "same_account" (from: request)
- R:INSUFFICIENT a source balance below the amount is refused with 400 "insufficient_funds"; no balance changes (from: request)
- R:FORBIDDEN an account the caller does not own is refused with 403 "forbidden"; no balance changes (from: request)
```

## ASSUMPTIONS — every silence, on the record

A request never says everything. The agent must fill the gaps to build anything at all, and each gap it fills is written down:

```
A<n> [<dim>] <what is not said> → <reading taken> → <cost if wrong>
```

**Sweep; don't free-associate.** For each public surface the change exposes, ask six questions:

| dim | the question |
|---|---|
| `who` | who may do this? (authorization, ownership) |
| `which` | which cases are in, which are out? |
| `when` | boundaries — inclusive or exclusive? timing? |
| `absent` | what happens when a value is missing? defaults? |
| `order` | sequencing, ties, concurrency |
| `experience` | who receives the result, and what would make it hard for them? |

One silence per line. A dimension that cannot apply is retired on the record: `A3 [experience] n/a · internal API, no end user reads the error text`. A guess that can be checked cheaply is checked now, and the answer is appended: `· found: <answer> (evidence: <file:line | command>)`.

This section replaces up-front approval. The human reviews it afterwards — so a guess is never hidden inside a Must, where nobody can see it was a guess.

### ▶ Example — ASSUMPTIONS

```markdown
## ASSUMPTIONS
- A1 [which] currency is not mentioned → one currency, amounts in integer cents · found: balances are integer cents (evidence: src/accounts.py:8)
- A2 [order] two transfers from one account at once are not mentioned → the check and the debit happen under one lock → without it, two transfers can both pass the balance check and overdraw
- A3 [when] amount == balance is not mentioned → allowed; leaves 0 · found: a balance may be 0 (evidence: src/accounts.py:8)
- A4 [who] the destination's owner is not mentioned → both source and destination must be the caller's → if transfers to others are wanted, R:FORBIDDEN is too strict
- A5 [absent] an unknown account id is not mentioned → refused as "forbidden", so the response never reveals whether an id exists → a caller cannot tell a typo from a foreign account
- A6 [experience] n/a · internal service call; the error code is the contract
```

A4 and A5 are real product decisions the request did not make. That is exactly what the human should see.

## PLAN — scope, surfaces, strategy, commands

```markdown
## PLAN
strategy: look up both accounts, check ownership, then amount, then same-account, then balance, all under one lock; debit and credit together
check: python3 -m pytest -q tests/test_transfer_contract.py
regression: python3 -m pytest -q
```

The task's frontmatter carries the two lists the build is held to:

- **`scope:`** — the paths the build may touch. Needing another path means the plan was wrong.
- **`gives:`** — surfaces other code will depend on, e.g. `S1 transfer(ledger, caller, from_id, to_id, amount) -> {from_balance, to_balance}`. Internals may change freely; a `gives:` surface may not move silently.

The `check:` command runs this task's checks; the `regression:` command runs the host suite, so a task cannot ship green over a broken project.

## CHECKS — each written to fail on the likely wrong implementation

```
C<n> covers: <M/R/A ids> · <mode> · <test id>
```

At least one check per Must and per Reject, each aimed at **the most plausible wrong implementation** — a check that any implementation passes is decoration. Prefer **acceptance** checks through the public seam; add a **property** check where an invariant can be named, and a **contract** check where a consumer exists. Keep the task's checks in files of their own, so the seal covers them cleanly. A Must you cannot encode as a check is not understood yet.

### ▶ Example — CHECKS

```markdown
## CHECKS
- C1 covers: M1 · acceptance · tests/test_transfer_contract.py::test_moves_the_amount
- C2 covers: R:AMOUNT_INVALID · acceptance · tests/test_transfer_contract.py::test_non_positive_amount_refused_nothing_moves
- C3 covers: R:SAME_ACCOUNT · acceptance · tests/test_transfer_contract.py::test_same_account_refused
- C4 covers: R:INSUFFICIENT, A3 · acceptance · tests/test_transfer_contract.py::test_overdraw_refused_exact_balance_allowed
- C5 covers: R:FORBIDDEN, A4, A5 · acceptance · tests/test_transfer_contract.py::test_foreign_or_unknown_account_forbidden
- C6 covers: A2 · property · tests/test_transfer_contract.py::test_parallel_transfers_never_overdraw
```

The `nothing moves` in C2's name does real work: it pins that a refused transfer leaves every balance untouched — a property an implementation that debits before checking would break.

## Red for the right reason

Write the checks as real tests and run them. They **must fail because the behavior is absent** — not on an import error, a typo, or a missing fixture. A check that is green before the build proves nothing; fix it before going on.

```text
$ python3 -m pytest -q tests/test_transfer_contract.py
...
7 failed, 20 warnings in 0.03s      # every failure is NotImplementedError from a one-line stub
```

A one-line stub gives the checks a seam to call, so they fail on missing behavior rather than an import error. The full run is in [Appendix D](./appendix-d-worked-example.md).

## The seal — one commit

Set `status: build` in the task's frontmatter, then commit the task file and its check files together:

```bash
git add .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py
git commit -m "freeze(transfer-own-accounts): move money between two accounts the caller owns"
```

That commit is the seal. From here the task file and every file named in CHECKS are frozen. Verify will prove it with `git diff <freeze> HEAD -- <those files>`, which must print nothing.

**Changed your mind later?** A rule was wrong, a check was aimed badly, scope must grow — that is legitimate. Edit the task file and checks, note why under `## LOG`, and commit `refreeze(<slug>): <why>`. History shows the change and its reason; nothing is silent.

> **When the change has a user interface.** Extend the sweep with the screen states — loading, empty, error, success — and the `experience` dimension in earnest: who receives this screen, with what device and what urgency. Each state that matters is a rule with a check.

## Common mistakes

- **Only the happy path.** The Rejects are where most real complexity lives; an empty Reject list usually means it was not thought through.
- **Free-text errors.** Name the code, so it becomes a check and a contract response.
- **A guess inside a Must.** If the request did not say it, it is an assumption — write it where the reviewer will see it.
- **Unswept surfaces.** Free association follows the request's emphasis; the dimension nobody wrote about is exactly the one that ships as a silent guess.
- **"Existing behavior" without a citation.** A claim about the current code carries `file:line`, or a command and its output.
- **Checks that assert internals.** Assert observable behavior, so the code can be regenerated underneath.
- **A green check before the build.** It proves nothing. Make it fail for the right reason.

## Exit check

- [ ] Every required behavior is a Must, every refusal a Reject with a named error, each citing its source.
- [ ] Every public surface is swept on the six dimensions; each silence is one assumption line, or retired with a reason.
- [ ] `scope:`, `gives:`, `check:` and `regression:` are written.
- [ ] Every Must and Reject is covered by at least one check aimed at a plausible wrong implementation.
- [ ] The checks ran and failed because the behavior is absent.
- [ ] `status: build`, and the task file plus check files are committed as `freeze(<slug>)`.
