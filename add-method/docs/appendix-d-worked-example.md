# Appendix D · The worked example, end to end

[← Appendix C Glossary](./appendix-c-glossary.md) · [Contents](./README.md) · Next: [Appendix E Checklists →](./appendix-e-checklists.md)

The running example, assembled in one place so you can see a complete pass through
the loop without flipping between chapters. The feature: **transfer money between a
user's own accounts.**

Every command and every engine response on this page was produced by running the
shipped engine against a real bundle. Nothing here is illustrative shorthand.

---

## Open the task

```
$ add new milestone payments
created milestones/payments.md
next: add freeze payments

$ add new task transfer-own-accounts --milestone payments --scope src/transfers.py
created tasks/transfer-own-accounts.md
next: add freeze transfer-own-accounts
```

`add new task` writes a scaffolded node with its sections empty. Authoring those
sections *is* the Direction beat.

## Direction — the authored node

One file carries the whole direction: what must hold, what must never happen, the
contract it publishes, the files it may touch, and the checks that prove each rule.

```markdown
---
type: Task
title: transfer-own-accounts
status: direction
milestone: payments
scope:
  - src/transfers.py
gives:
  - "POST /transfers -> 200 { transferId, fromBalance, toBalance }"
---
## CARD
goal: Move an amount between two accounts the caller owns, atomically.
why: The first payments slice; every later payment feature freezes against this shape.

## RULES
<must>
- M1 A transfer between two accounts I own moves the amount: source -= amount, destination += amount.
</must>
<reject>
- R:NONPOSITIVE an amount <= 0 must never move money -> "amount_invalid"
- R:SAMEACCOUNT source == destination must never be accepted -> "same_account"
- R:OVERDRAW a balance below the amount must never be debited -> "insufficient_funds"
- R:NOTMINE an account the caller does not own must never be a source -> "forbidden"
</reject>

## PLAN
contract: POST /transfers { fromAccountId, toAccountId, amount }
  200 -> { transferId, fromBalance, toBalance }
  400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
  403 -> { error: "forbidden" }
scope: src/transfers.py
assumptions (lowest confidence first):
  - "⚠ single currency, no FX, in v1 — the ticket never said; if wrong the amount and
     rounding model changes and this contract is wrong"
  - "no daily limit in v1 — confirmed out of scope"

## EDGES
- E1 Two simultaneous transfers from the same source must not both pass the balance check and overdraw it.

## CHECKS
- test_successful_transfer · covers: M1 · 100/0, transfer 30, leaves 70/30
- test_amount_must_be_positive · covers: R:NONPOSITIVE · amount 0 is rejected and no balance changes
- test_same_account · covers: R:SAMEACCOUNT · A to A is rejected and no balance changes
- test_insufficient_funds · covers: R:OVERDRAW · 50 from a balance of 20 is rejected and no balance changes
- test_not_my_account · covers: R:NOTMINE · a source I do not own is rejected
- test_concurrent_transfers_cannot_overdraw · covers: E1 · two parallel debits of 60 from 100 leave exactly one winner
red-first: every check MUST fail first.
```

Three things earn their place here:

- **The flagged assumption comes first.** The product owner reads the single-currency
  choice — the one most likely to be wrong and most expensive if it were — and
  confirms it before anything is built.
- **Every rule has exactly one check, named by `covers:`.** A rule nothing covers
  blocks the gate later, so the binding is not a convention you have to remember.
- **The race is an edge case, `E1`, not a hope.** It is written down and covered like
  any rule, which is what stops "we'll check that at review" from quietly meaning
  "nobody checked it."

## Freeze — the one approval

```
$ add freeze transfer-own-accounts
freeze recorded at authority `process`
next: build, then `add run -- <cmd>`
```

The freeze is the single human decision of the task. It stamps the direction and
opens Build.

## The red suite, red for the right reason

The checks run before any implementation exists. The first attempt failed on an
import error — which is a **lying red**: the suite is failing because it cannot load,
not because the behavior is missing. Stubbing the real shape fixes that:

```python
def transfer(source, destination, amount, caller):
    raise NotImplementedError
```

```
$ python3 -m pytest tests -q
FAILED tests/test_transfers.py::test_insufficient_funds - NotImplementedError
FAILED tests/test_transfers.py::test_not_my_account - NotImplementedError
FAILED tests/test_transfers.py::test_concurrent_transfers_cannot_overdraw - A...
6 failed
```

Six checks, six honest failures. That is the baseline the build has to move.

## Build

The AI implements against the frozen direction — it may not edit a check, may not
edit the frozen contract, and may not touch a file outside `scope:`. The one line
that matters for `E1`:

```python
    # The balance is re-checked INSIDE the lock: checking outside it is what lets two
    # concurrent transfers both pass and overdraw the source (E1).
    with _ledger_lock:
        if source.balance < amount:
            return {"error": "insufficient_funds"}
```

```
$ python3 -m pytest tests -q
6 passed
```

## Verify — record the evidence, then gate

The engine never runs your suite ([NO-EXEC](./01-principles.md)). You run it; `add
run` records what happened as a receipt:

```
$ add run transfer-own-accounts --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- python3 -m pytest tests -q --junitxml="${TMPDIR:-/tmp}/add-run.xml"
receipt 1 recorded (exit 0)
next: add gate transfer-own-accounts

$ add gate transfer-own-accounts PASS
gate PASS recorded at authority `process`
  freshness: fresh — every file in scope is byte-identical to the run
  brief sha256:b8e0396b0b7499f5 · receipt /tasks/transfer-own-accounts.d/runs/1.md
/tasks/transfer-own-accounts.md is done
next: add status
```

A `PASS` closes the node. The verdict is on record with the receipt that earned it.

Before signing it, the reviewer still owes the residue — the part checks cannot
reach: that the balance re-check happens *inside* the transaction, that no secret or
unexpected dependency arrived, that the layering held, and that every new symbol is
actually wired in. See [05 Verify](./05-verify.md).

## What the gate actually refuses

These are the engine's own words, not a description of them.

**No evidence at all:**

```
$ add gate transfer-own-accounts PASS
cannot record `PASS` — no receipt has been recorded
next: add run transfer-own-accounts -- <cmd>
```

**Evidence that went stale** — a scoped file was edited after the run, so the receipt
no longer describes the code you are signing for:

```
$ add gate transfer-own-accounts PASS
cannot record `PASS` — the receipt is stale — src/transfers.py changed since the run
next: add run transfer-own-accounts -- <cmd>
```

**A security risk someone tried to sign away.** On a task carrying
`--sensitivity security`, `RISK-ACCEPTED` is not available at all:

```
$ add gate transfer-audit-log RISK-ACCEPTED --reason "ship it"
cannot record `RISK-ACCEPTED` — a security risk cannot be folded into a RISK-ACCEPTED — the security floor is HARD-STOP
next: resolve it (add gate transfer-audit-log PASS) or stop it (add gate transfer-audit-log HARD-STOP --reason "<the finding>")
```

**A security `PASS` with nobody on record for it:**

```
$ add gate transfer-audit-log PASS
cannot record `PASS` — a security PASS needs a named lens — no `persona:`/`advised_by:` is recorded, so no one is on record as having reviewed the security -> "R:NOCOVERAGE"
next: assign a security lens (add advise transfer-audit-log --persona <p>, or run it in a lensed wave), then add gate transfer-audit-log PASS
```

`add doctor` reports the same gap before you reach the gate:

```
$ add doctor
  warn  unadvised_sensitive: tasks/transfer-audit-log.md: security, no lens
1 finding(s) — `add doctor --sync` repairs what it can
```

## Knowing where you are

Two read-only verbs answer "what now?" without re-reading the repo:

```
$ add todo
1 open task(s):
direction:
  · transfer-audit-log       → add freeze transfer-audit-log

$ add status
.add  ·  11 nodes
  · PROJECT                      [—] Project
  · payments                     [direction] Milestone
  · transfer-audit-log           [direction] Task
  · domain                       [—] Spec
  ...
next: add freeze transfer-audit-log
```

## The loop — observe

Released behind a feature flag to 5% of users. Monitored:

- transfer error rate (target: well under 0.1% of attempts);
- the rate of each rejection — a spike in `insufficient_funds` would suggest a UX
  problem (users not seeing their balance) rather than a code defect;
- latency of the atomic update under load.

A week later, telemetry shows an unexpectedly high `forbidden` rate: users are trying
to transfer *into* a shared account they can see but do not own. That observation is
recorded against the evidence with `add learn`, and once confirmed it folds into the
living specs (`add fold`) — "support transfers into accounts I am authorized on, not
only accounts I own" — which is where the next task's direction starts.

---

This is the whole method in one feature: one node holding the direction, a human
freeze, a red suite bound to the rules it proves, a build bounded by scope, a verdict
grounded in a fresh receipt plus the residue only a person can check, and a loop that
turns production reality into the next direction.

---

## Multi-component, end to end

The example above is a single codebase with one green bar. Real slices often cross
components — a backend endpoint and the frontend that calls it. ADD ships that slice
*inside one milestone* using the component pillar
([17 Components](./17-components.md)). Here is the same flow spanning two parts: a
`gateway` backend that **produces** an orders interface, and a `web` frontend that
**consumes** it.

### Scope is declared on the node

There is no registry and nothing scans the tree to guess ownership. Each task names
its own parts:

```yaml
# the backend task
scope:
  - apps/gateway/**

# the frontend task
scope:
  - apps/web/**
```

`add locate apps/gateway/service.py` does the reverse lookup — which node's scope
owns this path.

### The boundary is the producer's frozen `gives:`

The interface is not a separate file type. It is the producer task's `gives:`, frozen
at the freeze stamp, cited by the consumer's `needs:`:

```yaml
# producer task (apps/gateway)
gives:
  - "GET /orders?status= -> 200 { orders: [...], nextCursor } · 400 bad_status"

# consumer task (apps/web)
depends_on:
  - /tasks/orders-api.md
needs:
  - /tasks/orders-api.md#gives
```

The consumer's `needs:` cannot resolve until the producer's `gives:` is frozen, so
the slice is **ordered by the frozen contract** rather than split across two
milestones. A `needs:` pointing at a `gives:` that was never frozen surfaces as an
`edge_unresolved` finding *before* the frontend builds against a shape that does not
exist. If the producer later refreezes a changed shape, every node citing the old
fragment is flagged stale and must re-verify before its next gate.

### Each task verifies on its own bar

A backend task and a frontend task pass on different toolchains, and the gate holds
each to its own through its **bound receipt**: `add run <slug> -- <the suite for this
scope>` records the checks that actually ran, and `add gate <slug> PASS` refuses
unless every check the rules `covers:` appears in that receipt as passed. The engine
never runs either suite. Two tasks, one milestone, two green bars.

### In parallel, and across repositories

When the parts are independent, `add wave <milestone>` plans the wave from the task
DAG by levels — producers land before their consumers — and each stream runs in its
own git worktree under its own persona lens. `add join <bundles…>` folds the finished
streams back, PASS-only.

Across *separate repositories* one honest difference applies: an edge may not escape
its bundle, so a consumer in repo B cannot cite a node in repo A. Each repo carries
its own `.add/` bundle, and the hand-off is the frozen shape itself — committed in
the producer repo, and committed as the contract of record in the consumer repo. The
engine ships no cross-repo fetch verb, because a boundary between two teams' repos is
exactly where a human-carried, committed contract beats a background pull.
