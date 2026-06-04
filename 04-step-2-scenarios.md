# 04 · Step 2 — Scenarios

[← 03 Step 1 Specify](./03-step-1-specify.md) · [Contents](./README.md) · Next: [05 Step 3 Contract →](./05-step-3-contract.md)

> **Purpose:** rewrite each rule from the spec as a concrete, pass-or-fail scenario.
> **Produces:** `features/<name>.feature`.
> **Person's job:** decide what "correct" looks like in concrete situations. **AI's job:** draft the scenarios.

> **Part of the one-approval front (v7).** In the default flow these scenarios are drafted by the AI alongside the spec, contract, and failing tests as **one bundle**, approved by a person **once**, at the contract freeze — not signed off step by step. This chapter is how to get the scenarios *right*; [05 Contract](./05-step-3-contract.md) is where the bundle is frozen. See [11 Governance](./11-governance.md).

---

## Why turn rules into scenarios

A plain rule is still open to interpretation. "Source must have enough balance" leaves open: enough for what, exactly? What happens to the balances when it is *not* enough? A scenario removes the interpretation by pinning a specific situation to a specific expected result.

Scenarios occupy a unique position: they are **readable by people and checkable by machines at the same time.** A product owner can confirm a scenario is what they meant; a test can be generated directly from it. This makes them the bridge between the human-led front of the flow and the machine-led back. They are the single most leverage-bearing artifact in the method, because everything downstream — the tests, and through them the build's definition of success — is generated from them.

## The form

Each scenario has three parts:

- **Given** — the starting situation.
- **When** — the action taken.
- **Then** — the result that must follow.

Where a rule also constrains what must *not* change, add an **And** clause to state it. Unwanted side effects are caught by what you assert stays the same, not only by what you assert changes.

## Template

```
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <expected result>
  And <what must remain unchanged>   # when relevant
```

## ▶ Example

```
Scenario: successful transfer
  Given A has 100 and B has 0, both mine
  When I transfer 30 from A to B
  Then A has 70 and B has 30

Scenario: insufficient funds
  Given A has 20, mine
  When I transfer 50 from A to B
  Then it is rejected "insufficient_funds"
  And no balance changes

Scenario: not my account
  Given account C is not mine
  When I transfer 10 from C to B
  Then it is rejected "forbidden"
```

The `And no balance changes` line is doing real work: it specifies that a rejected transfer must leave the world untouched — a property the AI could easily violate by deducting before checking.

## The AI's role here

Hand the AI the spec and have it draft a scenario for each rule, including the rejection rules. Then read them as the person who owns the requirement: do they describe what you actually meant? Correct any that drift. See `playbook/2_scenarios.md` in [Appendix B](./appendix-b-prompts.md).

## Common mistakes

- **Only happy-path scenarios.** Every "Reject" rule in the spec needs its own scenario, or that rule will never be verified.
- **Vague results.** "Then it works" is not checkable. The result must be a specific, observable fact ("A has 70").
- **Forgetting the unchanged state.** For any rejection, assert that nothing changed; otherwise a partial, corrupting failure can pass.

## Exit check

- [ ] Every "Must" rule has at least one scenario.
- [ ] Every "Reject" rule has at least one scenario.
- [ ] Each scenario's result is a specific, observable fact.
- [ ] Rejections assert what must stay unchanged.

## If the check fails

A rule with no scenario will never be tested, and therefore will never be verified — it is a rule in name only. Either write the missing scenario or remove the rule from the spec. Do not carry an unscenarioed rule into the contract.
