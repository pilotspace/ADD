# 03 · Direction — rules, plan, checks

[← 02 The three-beat loop, and what is disposable](./02-the-flow.md) · [Contents](./README.md) · Next: [04 Build — red to green, inside scope →](./04-build.md)

---

## Why Direction is first

Direction is the steering; Build is the engine. You do not start the engine until the wheel is set. In one beat the AI authors a single node — its **RULES**, its **PLAN**, and its **CHECKS** — and runs the checks red. A person freezes it, once, and that freeze is the only human decision in the whole task.

Everything vague here does not stay vague: it becomes a concrete wrong guess in the code, discovered late. The cheapest moment to remove an ambiguity is now, in a sentence, before anything depends on it. There is a diagnostic value too — **if you cannot state the rules, you do not yet understand the feature well enough to build it.** The inability to specify is information, not an obstacle to push past.

## How the node gets authored

`add new Task <slug>` scaffolds the node file with a `## CARD` (its `goal:`, a one-line `why:`, the current beat) and empty `## RULES / ## PLAN / ## CHECKS` sections. **There is no author verb** — you fill those sections by editing the node directly. The engine records; it never writes the method for you.

Before drafting, **ground the real code.** Gather the actual files, symbols, signatures, and conventions the task touches into a lean grounding map, and surface the anchors the contract will cite. Grounding is AI-owned and adds no approval; it aims the whole node at reality instead of assumption.

The node is not dictated by one side. It is co-specified in three moves:

1. **Diverge — brainstorm by both.** Before drafting, the AI surfaces the *decision space*: the two or three genuine ways to frame the feature, and the open questions it would otherwise resolve by guessing. You react — add, kill, redirect. This lives in the conversation, not in a new document.
2. **Converge — the AI drafts, and ranks its own uncertainty.** The AI authors the whole node in one silent draft, then ranks where its confidence is lowest. It does not hand you a flat list of equal-looking assumptions to nod through; it tells you *where it is most likely wrong, and what that would cost.*
3. **Validate — you decide, with the AI's advice.** You read the ranked uncertainty first, then confirm, correct, or send it back. Your approval is real because your attention was aimed.

Compose the whole node in **one draft**, then present it for the one approval, lowest-confidence-first.

---

## RULES — what it must do, and refuse

The RULES section is four short lists plus the one thing most likely to be wrong.

1. **Must** — the behaviors the feature is required to perform.
2. **Reject** — the inputs or situations it must refuse, each paired with a **named error code**.
3. **After** — the state that is true once it succeeds (what changed).
4. **The one riskiest assumption** — the single thing you are taking for granted that is *most likely wrong and most expensive to get wrong*, flagged with `⚠`, *why* it is uncertain, and *what it costs* if it is wrong. A node with genuinely nothing uncertain still names its single biggest risk — the AI never claims a blank mind.

Naming the errors matters. "Reject bad amounts" is an instruction to guess; `amount <= 0 -> "amount_invalid"` is a rule that produces a testable check and a defined contract response.

Give each Must a stable `M<n>:` ID; a Reject's own error code already *is* its ID, referenced later as `R:<code>`. These IDs are what the checks bind to.

### ▶ Example — RULES

```
Feature: Transfer money between my own accounts
Framings weighed: synchronous single-currency transfer (chosen) · queued transfer · multi-currency with FX
Must:
  M1: move an amount from one of my accounts to another of mine
  M2: source and destination are different accounts
  M3: source has enough balance
Reject:
  amount <= 0           -> "amount_invalid"
  source == destination -> "same_account"
  balance < amount      -> "insufficient_funds"
  account not mine      -> "forbidden"
After:
  - source balance -= amount, destination balance += amount
⚠ same currency only (no FX) in v1 — lowest confidence because the ticket never said;
   if wrong: the whole amount/rounding model changes and this contract is wrong
```

The `Framings weighed:` line shows what was considered and dropped, so the chosen shape is a *decision*, not a default. The `⚠` line is the one the stakeholder reads first: the assumption most likely to be wrong and most expensive to get wrong.

---

## PLAN — the contract, the strategy, the scope

PLAN turns the grounded code into the shape neighbours can depend on. It carries three things:

- **The contract shape** — the interface this node publishes: the endpoints, functions, or messages, their request and response shapes, the names (drawn from the project glossary so one concept has one name everywhere), and a contracted response for every error code the rules reject. This shape becomes the node's **frozen `gives:`** — the interface other nodes depend on and the build is not allowed to disturb.
- **The build strategy** — how the code will satisfy the rules, and any place where correctness depends on more than shape (a transaction boundary, an ordering guarantee).
- **The `scope:` tokens** — the paths this node may touch. Scope is also the *freshness set*: the files a verify receipt must observe unchanged. Nothing outside scope is edited during Build.

### The frozen contract is the decision point

The AI is allowed to write and rewrite code quickly. That is only safe if there is a stable surface the rest of the system depends on and the AI is not allowed to move. The frozen `gives:` is that surface. Below it, the code is disposable and can be regenerated freely; above it, nothing breaks, because the shape it depends on does not move. Freezing is not bureaucracy — it is the precondition for letting the AI build freely and fast.

### ▶ Example — PLAN

```yaml
# authored into the node's frontmatter before the freeze
gives: "POST /transfers { fromAccountId, toAccountId, amount }
        -> 200 { transferId, fromBalance, toBalance }
        -> 400 { error: amount_invalid | same_account | insufficient_funds }
        -> 403 { error: forbidden }"
scope:
  - src/transfers/**
```

```
Strategy: read both accounts in one transaction; check ownership, then amount,
          then balance; debit + credit atomically or not at all.
Schema:   accounts.balance (read + write, must be transactional).
```

Every error code traces back to a Reject rule; the `must be transactional` note flags the one place where correctness depends on more than shape — a hint Verify will follow up. The graph and every compiled brief read `gives:` from the frontmatter, so it must be hand-authored there before the freeze — nothing records it for you.

### The change-request rule

Once frozen, a `gives:` does not change casually. A needed change is a **change request**: you fold the new shape back into RULES, re-freeze, and come forward again. The AI never alters a frozen contract on its own initiative — if it could drift, nothing built on it would be safe.

> **Do:** freeze the contract shape before any implementation.
> **Don't:** let Build quietly change an interface to make the code easier — that breaks everything depending on it.

---

## CHECKS — the red suite

CHECKS is where "correct" is pinned down so a machine can judge it. Before writing a single assertion, rewrite each rule as a concrete, pass-or-fail **scenario** — readable by a person and checkable by a machine at the same time.

### Scenarios — Given / When / Then

- **Given** — the starting situation.
- **When** — the action taken.
- **Then** — the result that must follow.
- **And** — what must *not* change (add this wherever a rule constrains side effects).

```
Scenario: insufficient funds          # covers: R:insufficient_funds
  Given A has 20, mine
  When I transfer 50 from A to B
  Then it is rejected "insufficient_funds"
  And no balance changes
```

The `And no balance changes` line does real work: it specifies that a rejected transfer leaves the world untouched — a property the AI could easily violate by deducting before checking.

### One check per rule, each with a `covers:` referent

Author **one check per Must, per Reject, and per edge case that changes behavior.** Each check carries a `covers:` key naming the rule it proves — `M<n>` for a Must, `R:<code>` for a Reject, `E<n>` for an enumerated edge. A Must or Reject encoded in **no** check means the rules are not understood — stop and say so. Minor variants are build guidance, not gated checks.

The `covers:` binding is enforced at the **gate**: it refuses a PASS while any `M<n>` or `R:<code>` is covered by no check, or when the named checks did not demonstrably pass on a fresh receipt. Freeze only stamps the node approved; the coverage proof is checked when the verdict is recorded. Coverage is a binding, not a label.

### Red for the right reason

After authoring the checks, run them: they **must fail**, and fail because the behavior is *absent* — not because a name is misspelled or an import is missing. A check that passes before any code exists is testing nothing; it is a false reassurance that will later wave bad code through. Confirming the suite is "red for the right reason" is what makes it genuinely protective.

Tests assert **behavior, not internals** — the observable result, never how it is implemented — so the code can be regenerated freely beneath them.

### ▶ Example — CHECKS

```python
def test_successful_transfer():            # covers: M1
    a = account(balance=100, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 30)
    assert r.status == 200
    assert a.balance == 70 and b.balance == 30

def test_insufficient_funds():             # covers: R:insufficient_funds
    a = account(balance=20, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 50)
    assert r.status == 400 and r.error == "insufficient_funds"
    assert a.balance == 20      # unchanged — the side-effect assertion

def test_not_my_account():                 # covers: R:forbidden
    c = account(balance=100, owner=someone_else); b = account(balance=0, owner=me)
    r = transfer(c.id, b.id, 10)
    assert r.status == 403 and r.error == "forbidden"
```

Run these now, with no implementation: all fail. That is the correct, honest starting point for Build.

### Sweep the edge cases

Beyond the Reject rules, sweep the recurring gaps that apply and add an `E<n>` check for each (or rule it out on purpose): boundary, duplicate/idempotent, ownership, stale/out-of-order, partial failure, concurrency, malformed input, limits/volume. A case earns a check when getting it wrong is a defect a reader would call a bug; otherwise reference it in prose as build guidance.

### Acceptance mode — for non-code tasks

Not every task ships code. A documentation task, a release, or an infrastructure change has no unit to exercise; forcing an executable test onto it is ceremony. For these (`kind: docs · release · infra`, or when the human declares acceptance mode), CHECKS becomes a **failing-first acceptance list** — short, concrete, verifiable pass/fail evidence, red before the artifact exists and green once it does:

```
## CHECKS — acceptance (failing-first)
- [ ] `mkdocs build` succeeds (fails now: the page does not exist)   # covers: M1
- [ ] the Personas chapter covers author · validate · flow           # covers: M2
- [ ] every internal link resolves                                   # covers: M3
```

Only the *form* is relaxed. Everything else holds — red before build, one check per rule, evidence not internals, and a person confirms it at the gate. A coding task keeps the executable red suite; the two modes never mix within one task.

---

## Common mistakes

- **Stating only the happy path.** The Reject list is where most real complexity lives; an empty one usually means it has not been thought through.
- **Free-text errors.** Errors must be named codes, not sentences, so they can become checks and contract responses.
- **A flat list of "confirmed" assumptions.** Eight equal-looking ticks invite a reflex approval. Rank them; flag the one that is load-bearing. An unranked list hides the risk inside the noise.
- **"Existing behavior" claims without a citation.** Any assumption or wiring claim that depends on the current state of an existing path must carry a grep/line citation (e.g. `file.rs:203`) — and it must name the production caller chain from a real entry point, not just a symbol's location. A function nothing calls is dead, not wired.
- **Inconsistent names.** If the contract says `fromAccountId` and the schema says `src_acct`, the AI produces subtle mismatches. Use the glossary everywhere.
- **Freezing too early or too late.** Freeze once the rules and contract are stable — not before they are agreed, and not after code has been written against an unfrozen shape.
- **Vague check results.** "Then it works" is not checkable; the result must be a specific, observable fact ("A has 70").
- **Forgetting the unchanged state.** For any rejection, assert that nothing changed, or a corrupting partial failure passes silently.
- **Tests that assert internals.** Coupling a check to private detail defeats disposability — assert observable behavior only.
- **A green check before the build.** A lying red (a `should_panic` / skipped test that passes while unimplemented) proves nothing. Declare unimplemented paths with `todo!()` (or the equivalent) so the check actually fails.

## Exit check

Direction is done when:

- [ ] Every required behavior is a Must; every rejection is a named error code; the success state-change is stated.
- [ ] The assumptions are ordered lowest-confidence first, with the one `⚠` flag carrying *why* + *cost* — or, for trivial scope, an honest "none material" that still names the single biggest risk.
- [ ] The contract shape is authored into `gives:`, versioned in intent, and every rejection has a contracted response.
- [ ] There is one check per Must, per Reject, and per behavior-changing edge — each with a `covers:` referent.
- [ ] The suite (or the acceptance list) runs in the pipeline and is **red for the right reason**.
- [ ] Checks assert observable behavior, not internals.

## If the check fails

If you cannot state a rule clearly, the feature is not ready to build — stop, take the question to whoever owns the requirement, and resolve it. A rule with no check will never be verified: write the missing check or remove the rule. If a check passes before any implementation, it is a fake check — repair it now, because it is your only independent standard for the build.

---

## The one approval — freeze

When RULES, PLAN, and CHECKS are authored and the checks are red for the right reason, a person freezes the node. This is the single human decision of the task, and it opens Build:

```bash
add freeze <slug> --by "<name>" --authority human
```

The freeze stamps direction closed — it approves the whole node at once. Reject any part and the whole node returns to draft (backward correction, not failure). Freeze is the approval; the gate in Verify is the proof.

The lowest-confidence flag is **node-wide**: at this one decision point the AI leads with *"of everything I'm asking you to freeze, this one point is most likely wrong"* — and it may point at an uncovered edge or the contract shape, not only a Must. The authority floor is set by the task's sensitivity: mechanical work carries a light floor, but anything touching **data**, **architecture**, or **security** is held to a human at the freeze, and **security is never derived and never batched** (see [09 Governance](./09-governance.md)).

> **When the feature has a user interface.** Extend Direction with a quick design: the user flows (happy path and main alternatives) and every screen state — loading, empty, error, success. Correct logic behind a confusing or incomplete interface is still a poor product, and undesigned states are exactly where an AI will improvise something ugly. Those states become CHECKS in acceptance mode where no unit test fits.
