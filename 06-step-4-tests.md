# 06 · Step 4 — Tests & Scenarios

[← 05 Step 3 Contract](./05-step-3-plan.md) · [Contents](./README.md) · Next: [07 Step 5 Build →](./07-step-5-build.md)

> **Purpose:** rewrite each rule as a concrete pass/fail scenario, then turn those scenarios and the contract into automated tests — and confirm they fail before any code exists.
> **Produces:** the **§4 TESTS & SCENARIOS** block of the task's `PLAN.md` — the pass/fail cases and a failing (red) automated test suite (or, for a non-coding task, a failing-first acceptance-check list).
> **Person's job:** decide what "correct" looks like and set the targets. **AI's job:** draft the scenarios, then generate the tests.

> **Part of the specification bundle (v7).** In the default flow the scenarios *and* the tests are drafted by the AI as part of the specification **bundle** (spec · contract · tests & scenarios) and approved by a person **once**, at the contract freeze — they are part of what that one approval covers. The tests still must be **red before the build**. See [11 Governance](./11-governance.md).

---

## Scenarios first — pass/fail cases

A test is only as honest as the case it encodes. Before writing a single assertion, rewrite each rule from the spec as a concrete, pass-or-fail **scenario** — the readable statement of what "correct" looks like that the test is then generated from.

### Why turn rules into scenarios

A plain rule is still open to interpretation. "Source must have enough balance" leaves open: enough for what, exactly? What happens to the balances when it is *not* enough? A scenario removes the interpretation by pinning a specific situation to a specific expected result.

Scenarios occupy a unique position: they are **readable by people and checkable by machines at the same time.** A product owner can confirm a scenario is what they meant; a test can be generated directly from it. This makes them the bridge between the human-led half of the flow and the machine-led back — everything downstream, the tests and through them the build's definition of success, is generated from them.

### The form

Each scenario has three parts:

- **Given** — the starting situation.
- **When** — the action taken.
- **Then** — the result that must follow.

Where a rule also constrains what must *not* change, add an **And** clause to state it. Unwanted side effects are caught by what you assert stays the same, not only by what you assert changes.

```
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <expected result>
  And <what must remain unchanged>   # when relevant
```

### ▶ Scenario example

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

### Cover the edge cases

The transfer above is one domain; the same gaps recur in every domain — an HR leave request, a marketing campaign send, a checkout. Beyond the spec's "Reject" rules, sweep the recurring gaps and add a scenario for each that applies (or rule it out on purpose): boundary, duplicate/idempotent, ownership, stale/out-of-order, partial failure, concurrency, malformed input, limits/volume.

**Primary cases and primary edge cases are the gated floor; minor variants are build-guidance.** Write the pass/fail scenario for every "Must" and "Reject" rule and for the edge cases that actually change behavior — those become the red tests below. Smaller variations (a second phrasing, a low-risk boundary already implied by another case) can be described in prose for the build to honor without a dedicated test. The rule of thumb: a case earns a test when getting it wrong is a defect a reader would call a bug; otherwise reference it in text.

## Why tests come before code

This is the step that operationalizes the second principle — *trust through evidence, not inspection.* The tests written here are how you will judge the AI's code in [Step 5](./07-step-5-build.md). For that judgment to be honest, the tests must exist *before* the code.

The reason is mechanical. If code is written first and tests after, the tests are unconsciously shaped to match whatever the code happens to do — including its mistakes. Tests written first, from the scenarios, are shaped only by the agreed definition of correct. They are an independent standard the code must rise to meet, not a description of what the code already does.

## The must-fail principle

After generating the tests, you run them — and they must **fail**, because no implementation exists yet. This sounds trivial and is not. A test that passes before any code is written is testing nothing; it is a false reassurance that will later wave bad code through. Confirming the suite is "red for the right reason" (a missing implementation, not a broken test) is what makes it genuinely protective.

## What to test

- **One test per primary scenario** — every "Must"/"Reject" scenario above becomes an executable test; minor variants stay as prose build-guidance.
- **Contract conformance** — tests that pin the shapes and error responses from [Step 3](./05-step-3-plan.md).
- **Edge cases from the spec** — the boundary values implied by the "Reject" rules.
- **Behavior, not internals** — tests assert what the feature does (the observable result), never how it is implemented, so the code can be regenerated freely beneath them.

## ▶ Test example

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

### Tagging a scenario or test back to a rule ID (optional — opt-in by usage)

If §1's Musts and Rejects carry stable IDs (`M1:`, and a Reject's own error code as `R:<error_code>`), declare which ID(s) a case satisfies — tag the `Scenario:` line (`# M1, R:amount_invalid`) or add a trailing `covers: M1, R:amount_invalid` to a §4 test-plan line. Once a task uses either anywhere, `add.py check` confirms every §1 ID is covered by a tag or a `covers:` line somewhere — a task that never uses either is left alone. See the template's own inline example for the exact grammar.

## Non-coding tasks — acceptance checks, not scripts

Not every task ships code. A documentation task, a release, an infrastructure change, or a wholly non-coding project has no unit to exercise — forcing an executable test onto it is ceremony. For these (`kind: docs · release · infra`, or when the human declares acceptance mode), §4 becomes a **failing-first acceptance check**: a short list of verifiable pass/fail evidence, red before the artifact exists and green once it does.

The discipline is unchanged — the check must genuinely fail first, and every item is concrete and observable:

```
## 4 · ACCEPTANCE — failing-first checks
- [ ] `mkdocs build` succeeds (fails now: the page does not exist)
- [ ] the Personas chapter covers author · validate · flow
- [ ] every internal link resolves
Checks live in: evidence
```

Only the *form* is relaxed: the check need not be executable code. Everything else holds — red before build, one check per primary scenario, evidence not internals, and a person confirms it at the gate. A coding task keeps the executable red suite above; the two modes never mix within one task.

## The AI's role here

Hand the AI the spec and have it draft a scenario for each rule (including the rejections), then read them as the person who owns the requirement — do they describe what you actually meant? Then have it generate the test suite from those scenarios and the contract. Your job is to confirm two things it cannot judge for itself: that each test asserts *behavior* rather than internal detail, and that none of them pass by accident before code exists. See `playbook/2_scenarios.md` and `playbook/4_tests.md` in [Appendix B](./appendix-b-prompts.md).

## Common mistakes

- **Only happy-path scenarios.** Every "Reject" rule in the spec needs its own scenario, or that rule will never be verified.
- **Vague results.** "Then it works" is not checkable. The result must be a specific, observable fact ("A has 70").
- **Forgetting the unchanged state.** For any rejection, assert that nothing changed; otherwise a partial, corrupting failure can pass.
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

- [ ] Every "Must" and "Reject" rule has at least one pass/fail scenario; each scenario's result is a specific, observable fact, and rejections assert what must stay unchanged.
- [ ] The edge-case categories that apply to this task's domain have a scenario (or are ruled out on purpose); minor variants are noted as build-guidance.
- [ ] One test — or, for a non-coding task, one acceptance check — exists per primary scenario.
- [ ] The suite (or the acceptance-check list) runs in the pipeline and is **red for the right reason**.
- [ ] Tests assert observable behavior, not internals.
- [ ] A coverage target is recorded.
- [ ] No `should_panic` lying reds — unimplemented paths use `todo!()` or equivalent so they actually fail.
- [ ] Collateral tests for globally-enumerated things (command counts, help snapshots) are listed by exact name.
- [ ] Arithmetic checked: the red fixtures can reach green against the frozen constants.

## If the check fails

A rule with no scenario will never be tested, and therefore never verified — write the missing scenario or remove the rule from the spec; do not carry an unscenarioed rule into the build. If a test passes before any implementation, it is a fake test — repair it before continuing, because it is your only independent check on the AI. If the suite is red for the wrong reason (a syntax or harness error), fix the harness first; a build cannot be judged against a broken net.
