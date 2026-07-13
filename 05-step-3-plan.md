# 05 · Step 3 — Contract

[← 04 Step 2 Scenarios](./04-step-2-scenarios.md) · [Contents](./README.md) · Next: [06 Step 4 Tests →](./06-step-4-tests.md)

> **Purpose:** fix the external shape of the feature — interfaces, data structures, names, and error cases — and freeze it.
> **Produces:** `contracts/<name>.md` (plus a mock and contract tests).
> **Person's job:** approve and freeze the shape. **AI's job:** generate the first draft, the mock, and the contract tests.

> **The one approval lands here (v7).** In the default flow the AI drafts spec, scenarios, this contract, and the failing tests as **one specification bundle**, and a person gives a **single approval at this freeze**. Freezing the contract is the one human gate of the bundle, not the third of three sign-offs; reject any part and the whole bundle returns to draft (backward correction, not failure). See [11 Governance](./11-governance.md).

---

## The decision point of the whole method

This step is the decision point between the human-led and machine-led halves of the flow, and it is what makes everything after it safe.

The reasoning is simple. The AI is allowed to write and rewrite code quickly. That is only safe if there is a stable surface that the rest of the system depends on and that the AI is not allowed to disturb. The frozen contract is that surface. Below it, the code is disposable and can be regenerated freely; above it, nothing breaks, because the shape it depends on does not move.

Freezing the contract is therefore not bureaucracy — it is the precondition for granting the AI real autonomy in the build step. Without it, every regeneration risks silently changing an interface that another part of the system relies on.

## What the contract contains

- **Interfaces** — the endpoints, functions, or messages, with their inputs and outputs.
- **Data structures** — the request and response shapes, and the persistent schema.
- **Names** — drawn from the project glossary, so the same concept has the same name everywhere.
- **Error cases** — the defined failures, using the error codes from the spec.

## Template

```
# contracts/<name>.md
<METHOD> <path>   body: { <fields> }
  200 -> { <success fields> }
  4xx -> { error: "<code>" | "<code>" }
Schema: <tables/fields touched, and access pattern>
Status: FROZEN @ v<n>
```

## ▶ Example

```
POST /transfers   body: { fromAccountId, toAccountId, amount }
  200 -> { transferId, fromBalance, toBalance }
  400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
  403 -> { error: "forbidden" }
Schema: accounts.balance (read + write, must be transactional)
Status: FROZEN @ v1
```

Every error code traces back to a rejection rule in the spec, and the schema note (`must be transactional`) flags the one place where correctness depends on more than shape — a hint the verification step will follow up.

## The AI's role here

The AI generates the contract from the spec and design, and additionally produces two things that make the contract enforceable: a **mock server** that returns the contracted shapes, and **contract tests** that pin those shapes. With the mock in place, work that depends on this feature can proceed before the real code exists. See `playbook/3_contract.md` in [Appendix B](./appendix-b-prompts.md).

## The change-request rule

Once frozen, a contract does not change casually. A needed change is a **change request**: you return to [Step 1](./03-step-1-specify.md), adjust the spec, re-freeze at a new version, and come forward again. The AI never alters a frozen contract on its own initiative.

This rule is what keeps the contract trustworthy as a foundation. If it could drift, nothing built on it would be safe.

> **Do:** version and freeze the contract before any implementation.
> **Don't:** let the build step quietly change an interface to make code easier — that breaks everything depending on it.

## Common mistakes

- **Inconsistent names.** If the contract calls it `fromAccountId` and the schema calls it `src_acct`, the AI will produce subtle mismatches. Use the glossary everywhere.
- **Undefined errors.** Every failure the spec rejects must have a contracted response, or callers cannot handle it.
- **Freezing too early or too late.** Freeze once the spec and design are stable — not before they are agreed, and not after code has already been written against an unfrozen shape.

## Exit check

- [ ] Contract is versioned and marked `FROZEN`.
- [ ] Contract tests pass against the mock.
- [ ] Every name matches the project glossary.
- [ ] Every spec rejection has a contracted error response.

## If the check fails

If the contract is not yet stable enough to freeze, the upstream artifacts are not settled — return to the spec or scenarios and resolve what is still open. If a frozen contract later needs to change, treat it as a change request rather than an edit; the discipline is the point.
