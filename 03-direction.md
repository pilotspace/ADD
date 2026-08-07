# 03 · Direction — rules, plan, checks

[← 02 The three-beat loop, and what is disposable](./02-the-flow.md) · [Contents](./README.md) · Next: [04 Build — red to green, inside scope →](./04-build.md)

---

## Why this step is first

The specification is the description the AI will build from. Every other artifact descends from it. Anything vague here does not stay vague — it becomes a concrete wrong guess in the code, discovered late. The cheapest moment to remove an ambiguity is now, in a sentence, before anything depends on it.

There is also a diagnostic value: **if you cannot write the spec, you do not yet understand the feature well enough to build it.** The inability to specify is information, not an obstacle to push past.

## Co-specification — how the spec gets made

A specification is not dictated by one side. It is made in three moves:

1. **Diverge — brainstorm by both.** Before drafting, the AI surfaces the *decision space*: the two or three genuine ways to frame the feature, and the open questions it would otherwise resolve by guessing. You react — add, kill, redirect. This is the brainstorm, and it lives in the conversation, not in a new document.
2. **Converge — the AI drafts, and ranks its own uncertainty.** The AI writes the spec below, then ranks where its confidence is lowest. It does not hand you a flat list of equal-looking assumptions to nod through; it tells you *where it is most likely wrong, and what that would cost.*
3. **Validate — you decide, with the AI's advice.** You read the ranked uncertainty first, then confirm, correct, or send it back. Your approval is real because your attention was aimed.

The brainstorm leaves a *light trace, not a document.* What you chose becomes a rule; what you weighed and dropped becomes a one-line **`Framings weighed:`** note; what stayed genuinely uncertain becomes a **lowest-confidence flag**. Nothing new to maintain — the residue lands in the spec you were writing anyway.

## What a good specification contains

Four parts, kept short:

1. **Must** — the behaviors the feature is required to perform.
2. **Reject** — the inputs or situations it must refuse, each paired with a named error.
3. **After** — the state that is true once it succeeds (what changed).
4. **Assumptions — lowest-confidence first** — the things you are taking for granted, **ranked so the most-likely-wrong come first.** The top one or two carry a `⚠` flag with *why it is uncertain* and *what it costs if wrong*; the rest are the low-stakes tail. A spec with genuinely nothing uncertain still names its single biggest risk, however small — the AI never claims a blank mind.

Naming the errors matters. "Reject bad amounts" is an instruction to guess; `amount <= 0 -> "amount_invalid"` is a rule that produces a testable scenario and a defined contract response.

### Rule IDs (optional — opt-in by usage)

Give each Must a stable `M<n>:` ID; a Reject's own error code already IS its ID (referenced later as `R:<error_code>`). Once a task uses a tag anywhere in §4 TESTS & SCENARIOS, `add.py check` starts asking that every Must/Reject be covered by a scenario tag or a test's `covers:` line — a task that never tags anything is never retro-flagged. See the template's own inline example for the exact grammar.

## Template

```
# SPEC.md
Feature: <name>
Framings weighed: <chosen> (chosen) · <alternative> · <alternative>
Must:
  - <required behavior>
Reject:
  - <bad input / situation> -> "<error_code>"
After:
  - <what is true once it succeeds>
Assumptions — lowest-confidence first:
  ⚠ <most-likely-wrong assumption> — lowest confidence because <why>; if wrong: <cost>
  - [x] <confirmed / low-stakes assumption> — <one line>
```

## ▶ Example

```
Feature: Transfer money between my own accounts
Framings weighed: synchronous single-currency transfer (chosen) · queued transfer · multi-currency with FX
Must:
  - move an amount from one of my accounts to another of mine
  - amount > 0
  - source and destination are different accounts
  - source has enough balance
After:
  - source balance -= amount, destination balance += amount
Reject:
  - amount <= 0           -> "amount_invalid"
  - source == destination -> "same_account"
  - balance < amount      -> "insufficient_funds"
  - account not mine      -> "forbidden"
Assumptions — lowest-confidence first:
  ⚠ same currency only (no FX) in v1 — lowest confidence because the ticket never said; if wrong: the whole amount/rounding model changes and this contract is wrong
  - [x] no daily limit in v1 — confirmed: out of scope for v1
```

The `Framings weighed:` line shows what was considered and dropped, so the chosen shape is a *decision*, not a default. The `⚠` line is the one the stakeholder reads first: the assumption most likely to be wrong and most expensive to get wrong. The flat `[x]` line is real but low-stakes. A reviewer can now spend their attention where it pays.

## The AI's role here

Use the AI to **open the space and then narrow it honestly.** First it brainstorms the genuine framings with you (diverge). Then it drafts the spec from whatever raw material you have — a ticket, an interview, a contract document — listing every assumption it had to make, **ranked lowest-confidence first**, and flagging the one or two it is least confident in with *why* and *what it costs if wrong*. Its instinct is to fill gaps silently and present a confident wall; the method forces those gaps into the open, and forces the confident wall to declare its own soft spots. See `playbook/1_specify.md` in [Appendix B](./appendix-b-prompts.md).

The defining instruction: *if a requirement is unclear, ask — do not resolve it by guessing — and of the things you must assume, say plainly where your confidence is lowest.*

## Common mistakes

- **Stating only the happy path.** The "Reject" list is where most real complexity lives; an empty one usually means it has not been thought through.
- **Free-text errors.** Errors must be named codes, not sentences, so they can become scenarios and contract responses.
- **Hidden assumptions.** If an assumption is not written down, it is not confirmed — it is a future bug with a delay timer.
- **A flat list of "confirmed" assumptions.** Eight equal-looking ticks invite a reflex approval. Rank them; flag the one or two that are load-bearing. An unranked list hides the risk inside the noise.
- **"Existing behavior" claims without a citation.** An assumption row that asserts "this is how X works today" is describing intent, not code. Any wiring claim or assumption that depends on the current state of an existing path must carry a grep/line citation (e.g. `file.rs:203`) — otherwise it is a future bug in disguise.
- **Wiring claims that name a symbol, not a caller chain.** Verifying that a function exists is not the same as verifying it is reachable. A wiring claim is only valid when it names the production caller chain from an actual entry point — not just the symbol's location in a file. A function that nothing calls is dead, not wired.

## Exit check

A spec is done when:

- [ ] Every required behavior is stated explicitly.
- [ ] Every rejection has a named error code.
- [ ] The success state-change is described.
- [ ] The assumptions are ordered lowest-confidence first, and the one or two `⚠` flags carry *why* + *cost* — or, for genuinely trivial scope, an honest "none material" that still names the single biggest risk.

The shift from older practice: you no longer pre-confirm every assumption to advance. You confirm that the AI has *ranked* its uncertainty and that you have *engaged the top of the rank.* Stated honestly: the flag makes a genuine review cheap and a lazy one visibly negligent — it cannot force the read. That is the most a lightweight check can buy.

## If the check fails

If you cannot state a rule clearly, the feature is not ready to build. Stop, take the question to whoever owns the requirement, and resolve it. Do not let the AI proceed on an unresolved point — that is the exact failure the whole method exists to prevent.

---

## The one approval, and where the flag really lands

In the one-approval flow, you do not approve the spec alone — you approve the whole frozen bundle (spec, scenarios, contract, tests) once, at the contract freeze. So the lowest-confidence flag is **bundle-wide**: at that single decision point the AI leads with *"of everything I'm asking you to freeze, these one or two points are most likely wrong"* — and a flag may point at an uncovered scenario or the contract shape, not only a spec assumption. The ranking you do here in Specify is the first input into that one gate. See [05 Contract](./03-direction.md) and the `add` skill's `run.md`.

---

## When the feature has a user interface

For anything with a UI, extend this step with a quick design: the **user flows** (the happy path and the main alternatives) and **every screen state** — loading, empty, error, and success. Correct logic behind a confusing or incomplete interface is still a poor product, and undesigned states are exactly where an AI will improvise something ugly. In the early **Prototype** stage, this design work is the main event and the code is throwaway (see [10 Stages](./07-setup-and-lanes.md)).

---

[← 03 Step 1 Specify](./03-direction.md) · [Contents](./README.md) · Next: [06 Step 4 Tests & Scenarios →](./03-direction.md)

> **Purpose:** fix the external shape of the feature — interfaces, data structures, names, and error cases — and freeze it.
> **Produces:** `contracts/<name>.md` (plus a mock and contract tests).
> **Person's job:** approve and freeze the shape. **AI's job:** generate the first draft, the mock, and the contract tests.

> **The one approval lands here (v7).** In the default flow the AI drafts spec, scenarios, this contract, and the failing tests as **one specification bundle**, and a person gives a **single approval at this freeze**. Freezing the contract is the one human gate of the bundle, not the third of three sign-offs; reject any part and the whole bundle returns to draft (backward correction, not failure). See [11 Governance](./09-governance.md).

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

Once frozen, a contract does not change casually. A needed change is a **change request**: you return to [Step 1](./03-direction.md), adjust the spec, re-freeze at a new version, and come forward again. The AI never alters a frozen contract on its own initiative.

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

---

[← 05 Step 3 Contract](./03-direction.md) · [Contents](./README.md) · Next: [07 Step 5 Build →](./04-build.md)

> **Purpose:** rewrite each rule as a concrete pass/fail scenario, then turn those scenarios and the contract into automated tests — and confirm they fail before any code exists.
> **Produces:** the **§4 TESTS & SCENARIOS** block of the task's `PLAN.md` — the pass/fail cases and a failing (red) automated test suite (or, for a non-coding task, a failing-first acceptance-check list).
> **Person's job:** decide what "correct" looks like and set the targets. **AI's job:** draft the scenarios, then generate the tests.

> **Part of the specification bundle (v7).** In the default flow the scenarios *and* the tests are drafted by the AI as part of the specification **bundle** (spec · contract · tests & scenarios) and approved by a person **once**, at the contract freeze — they are part of what that one approval covers. The tests still must be **red before the build**. See [11 Governance](./09-governance.md).

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

This is the step that operationalizes the second principle — *trust through evidence, not inspection.* The tests written here are how you will judge the AI's code in [Step 5](./04-build.md). For that judgment to be honest, the tests must exist *before* the code.

The reason is mechanical. If code is written first and tests after, the tests are unconsciously shaped to match whatever the code happens to do — including its mistakes. Tests written first, from the scenarios, are shaped only by the agreed definition of correct. They are an independent standard the code must rise to meet, not a description of what the code already does.

## The must-fail principle

After generating the tests, you run them — and they must **fail**, because no implementation exists yet. This sounds trivial and is not. A test that passes before any code is written is testing nothing; it is a false reassurance that will later wave bad code through. Confirming the suite is "red for the right reason" (a missing implementation, not a broken test) is what makes it genuinely protective.

## What to test

- **One test per primary scenario** — every "Must"/"Reject" scenario above becomes an executable test; minor variants stay as prose build-guidance.
- **Contract conformance** — tests that pin the shapes and error responses from [Step 3](./03-direction.md).
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
