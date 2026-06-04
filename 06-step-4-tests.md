# 06 · Step 4 — Tests

[← 05 Step 3 Contract](./05-step-3-contract.md) · [Contents](./README.md) · Next: [07 Step 5 Build →](./07-step-5-build.md)

> **Purpose:** turn the scenarios and contract into automated tests, and confirm they fail before any code exists.
> **Produces:** a failing (red) automated test suite.
> **Person's job:** set the targets and coverage. **AI's job:** generate the tests.

> **Part of the one-approval front (v7).** In the default flow these tests are drafted by the AI as part of the front **bundle** (spec · scenarios · contract · tests) and approved by a person **once**, at the contract freeze — the tests are part of what that single approval covers. They still must be **red before the build**. See [11 Governance](./11-governance.md).

---

## Why tests come before code

This is the step that operationalizes the second principle — *trust through evidence, not inspection.* The tests written here are how you will judge the AI's code in [Step 5](./07-step-5-build.md). For that judgment to be honest, the tests must exist *before* the code.

The reason is mechanical. If code is written first and tests after, the tests are unconsciously shaped to match whatever the code happens to do — including its mistakes. Tests written first, from the scenarios, are shaped only by the agreed definition of correct. They are an independent standard the code must rise to meet, not a description of what the code already does.

## The must-fail principle

After generating the tests, you run them — and they must **fail**, because no implementation exists yet. This sounds trivial and is not. A test that passes before any code is written is testing nothing; it is a false reassurance that will later wave bad code through. Confirming the suite is "red for the right reason" (a missing implementation, not a broken test) is what makes it a genuine safety net.

## What to test

- **One test per scenario** — every scenario from [Step 2](./04-step-2-scenarios.md) becomes an executable test.
- **Contract conformance** — tests that pin the shapes and error responses from [Step 3](./05-step-3-contract.md).
- **Edge cases from the spec** — the boundary values implied by the "Reject" rules.
- **Behavior, not internals** — tests assert what the feature does (the observable result), never how it is implemented, so the code can be regenerated freely beneath them.

## ▶ Example

```python
def test_successful_transfer():
    a = account(balance=100, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 30)
    assert r.status == 200
    assert a.balance == 70 and b.balance == 30

def test_insufficient_funds():
    a = account(balance=20, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 50)
    assert r.status == 400 and r.error == "insufficient_funds"
    assert a.balance == 20    # unchanged — the side-effect assertion

def test_not_my_account():
    c = account(balance=100, owner=someone_else); b = account(balance=0, owner=me)
    r = transfer(c.id, b.id, 10)
    assert r.status == 403 and r.error == "forbidden"
```

Run this now, with no implementation: all three fail. That is the correct, honest starting point for the build.

## The AI's role here

The AI generates the test suite from the scenarios and contract. Your job is to confirm two things it cannot judge for itself: that each test asserts *behavior* rather than internal detail, and that none of them pass by accident before code exists. See `playbook/4_tests.md` in [Appendix B](./appendix-b-prompts.md).

## Common mistakes

- **Tests that test the implementation.** Asserting on private internals couples the test to one version of the code and defeats disposability.
- **A green suite before the build.** Means the tests are not actually exercising the missing feature — fix them now.
- **Skipping the side-effect assertions.** Without `assert a.balance == 20` on the rejection path, a corrupting partial failure passes silently.
- **No coverage target.** Without a recorded target, coverage can quietly erode during the build.

## Exit check

- [ ] One test exists per scenario.
- [ ] The suite runs in the pipeline and is **red for the right reason**.
- [ ] Tests assert observable behavior, not internals.
- [ ] A coverage target is recorded.

## If the check fails

If a test passes before any implementation, it is a fake test — repair it before continuing, because it is your only independent check on the AI. If the suite is red for the wrong reason (a syntax or harness error), fix the harness first; a build cannot be judged against a broken net.
