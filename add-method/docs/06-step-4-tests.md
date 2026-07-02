# 06 · Step 4 — Tests

[← 05 Step 3 Contract](./05-step-3-contract.md) · [Contents](./README.md) · Next: [07 Step 5 Build →](./07-step-5-build.md)

> **Purpose:** turn the scenarios and contract into automated tests, and confirm they fail before any code exists.
> **Produces:** a failing (red) automated test suite.
> **Person's job:** set the targets and coverage. **AI's job:** generate the tests.

> **Part of the specification bundle (v7).** In the default flow these tests are drafted by the AI as part of the specification **bundle** (spec · scenarios · contract · tests) and approved by a person **once**, at the contract freeze — the tests are part of what that one approval covers. They still must be **red before the build**. See [11 Governance](./11-governance.md).

---

## Why tests come before code

This is the step that operationalizes the second principle — *trust through evidence, not inspection.* The tests written here are how you will judge the AI's code in [Step 5](./07-step-5-build.md). For that judgment to be honest, the tests must exist *before* the code.

The reason is mechanical. If code is written first and tests after, the tests are unconsciously shaped to match whatever the code happens to do — including its mistakes. Tests written first, from the scenarios, are shaped only by the agreed definition of correct. They are an independent standard the code must rise to meet, not a description of what the code already does.

## The must-fail principle

After generating the tests, you run them — and they must **fail**, because no implementation exists yet. This sounds trivial and is not. A test that passes before any code is written is testing nothing; it is a false reassurance that will later wave bad code through. Confirming the suite is "red for the right reason" (a missing implementation, not a broken test) is what makes it genuinely protective.

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

### Declaring which rule a test covers (optional — opt-in by usage)

If §1's Musts and Rejects carry stable IDs, add a trailing `covers: M1, R:amount_invalid` to a test-plan line to declare which ID(s) that test satisfies. Once any test in a task declares a `covers:` line (or any §2 scenario carries a tag), `add.py check` confirms every §1 ID is covered by a tag or a `covers:` line somewhere — a task that never uses either is left alone. See the template's own inline example for the exact grammar.

## The AI's role here

The AI generates the test suite from the scenarios and contract. Your job is to confirm two things it cannot judge for itself: that each test asserts *behavior* rather than internal detail, and that none of them pass by accident before code exists. See `playbook/4_tests.md` in [Appendix B](./appendix-b-prompts.md).

## Common mistakes

- **Tests that test the implementation.** Asserting on private internals couples the test to one version of the code and defeats disposability.
- **A green suite before the build.** Means the tests are not actually exercising the missing feature — fix them now.
- **Skipping the side-effect assertions.** Without `assert a.balance == 20` on the rejection path, a corrupting partial failure passes silently.
- **No coverage target.** Without a recorded target, coverage can quietly erode during the build.
- **`should_panic` as a red test.** Marking a test `#[should_panic(expected = "implement in green wave")]` (or the equivalent in any language) passes immediately and stays green while red — it is a lying red. Declare unimplemented paths with `todo!()` (or `unimplemented!()`) so the test actually fails. If a test is intentionally designed to flip from red to green during the build, say so with a comment: `// flip authorized at green wave`.
- **Collateral tests named by category, not by exact name.** When a spec adds a slash command, a new CLI subcommand, or any other globally-enumerated thing, there is a fixed collateral set of tests that count or enumerate it (e.g. a command-registry count test, a help-text snapshot, an autocomplete positional assert). Pre-list these tests by their **exact test names** in §4 — not categories — so the build agent's edits to those "pre-existing" tests are expected and the count is right. Naming only the category means the agent finds the wrong test or misses one.
- **Arithmetic not checked against frozen constants.** Before freezing, check that the red suite can reach green: a fixture with N bytes fails a hard-coded M-byte budget if N > M — the suite can never pass. Run the numbers before freeze, and add an additive override (e.g. `set_budget`) when the scenario implies a limit the production constant cannot satisfy in test.
- **Non-hermetic tests that read real user state.** Tests that call a loader with `None` (defaulting to `~/.helios/settings.json` or the real home dir) become torn-read flakes under a parallel suite and assert nothing useful. Red tests that create or read production paths must redirect them to a temp dir; grep new tests for `home_dir`, `~/.config`, real-path defaults before freeze.
- **Tests that share a per-machine singleton without isolation.** Background services (embedded servers, filesystem watchers) bind to fixed ports or paths. Tests that start such a service must tear it down, or they collide with a parallel run or an already-running dev instance. If the singleton cannot be isolated, gate those tests as serial (one thread, no parallel execution) and document it.

## Exit check

- [ ] One test exists per scenario.
- [ ] The suite runs in the pipeline and is **red for the right reason**.
- [ ] Tests assert observable behavior, not internals.
- [ ] A coverage target is recorded.
- [ ] No `should_panic` lying reds — unimplemented paths use `todo!()` or equivalent so they actually fail.
- [ ] Collateral tests for globally-enumerated things (command counts, help snapshots) are listed by exact name.
- [ ] Arithmetic checked: the red fixtures can reach green against the frozen constants.

## If the check fails

If a test passes before any implementation, it is a fake test — repair it before continuing, because it is your only independent check on the AI. If the suite is red for the wrong reason (a syntax or harness error), fix the harness first; a build cannot be judged against a broken net.
