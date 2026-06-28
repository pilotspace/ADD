# Appendix D · The worked example, end to end

[← Appendix C Glossary](./appendix-c-glossary.md) · [Contents](./README.md) · Next: [Appendix E Checklists →](./appendix-e-checklists.md)

The running example, assembled in one place so you can see a complete pass through the flow without flipping between chapters. The feature: **transfer money between a user's own accounts.**

---

## Step 1 — Specify → `SPEC.md`

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
  ⚠ same currency only (no FX) in v1 — lowest confidence because the ticket never said; if wrong: the amount/rounding model changes and this contract is wrong
  - [x] no daily limit in v1 — confirmed: out of scope for v1
```

The product owner read the flagged assumption first — the single-currency choice, the one most likely to be wrong and most expensive if it were — and confirmed it: v1 is single-currency with no daily limit.

## Step 2 — Scenarios → `features/transfer.feature`

```
Scenario: successful transfer
  Given A has 100 and B has 0, both mine
  When I transfer 30 from A to B
  Then A has 70 and B has 30

Scenario: amount must be positive
  Given A has 100, mine
  When I transfer 0 from A to B
  Then it is rejected "amount_invalid"
  And no balance changes

Scenario: same account
  Given A has 100, mine
  When I transfer 10 from A to A
  Then it is rejected "same_account"
  And no balance changes

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

Five scenarios for four rejections plus the happy path — every rule from the spec is covered.

## Step 3 — Contract → `contracts/transfer.md`

```
POST /transfers   body: { fromAccountId, toAccountId, amount }
  200 -> { transferId, fromBalance, toBalance }
  400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
  403 -> { error: "forbidden" }
Schema: accounts.balance (read + write, must be transactional)
Status: FROZEN @ v1
```

Frozen at v1. The schema note flags the atomicity requirement the verification step will check.

## Step 4 — Tests → `tests/transfer_test.py` (run first; all fail)

```python
def test_successful_transfer():
    a = account(balance=100, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 30)
    assert r.status == 200
    assert a.balance == 70 and b.balance == 30

def test_amount_must_be_positive():
    a = account(balance=100, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 0)
    assert r.status == 400 and r.error == "amount_invalid"
    assert a.balance == 100 and b.balance == 0

def test_same_account():
    a = account(balance=100, owner=me)
    r = transfer(a.id, a.id, 10)
    assert r.status == 400 and r.error == "same_account"
    assert a.balance == 100

def test_insufficient_funds():
    a = account(balance=20, owner=me); b = account(balance=0, owner=me)
    r = transfer(a.id, b.id, 50)
    assert r.status == 400 and r.error == "insufficient_funds"
    assert a.balance == 20

def test_not_my_account():
    c = account(balance=100, owner=someone_else); b = account(balance=0, owner=me)
    r = transfer(c.id, b.id, 10)
    assert r.status == 403 and r.error == "forbidden"
```

Run now, with no implementation: all five fail. That is the honest baseline.

## Step 5 — Build → the prompt given to the AI

```
Read SPEC.md, contracts/transfer.md, and tests/transfer_test.py.
Implement POST /transfers so that EVERY test passes.
Constraints:
  - Do NOT change any test.
  - Do NOT change the contract.
  - Make the balance update atomic: debit and credit in a single transaction,
    and re-check the balance inside the transaction.
  - Stop and ask if any requirement is unclear — do not guess.
  - Use only packages in dependencies.allowlist.
Report which tests pass and exactly what you changed.
```

The AI implements, runs the suite, iterates, and reports all five green, listing the files it changed.

## Step 6 — Verify → the human checks

- **Evidence:** all five tests pass; coverage held; no test or contract was altered. ✓
- **Concurrency (the key check):** two simultaneous transfers from account A must not both pass the balance check and overdraw it. The reviewer confirms the balance re-check happens *inside* the transaction and that the row is locked for the update — so a race cannot double-spend. ✓
- **Security:** no hardcoded secrets; inputs validated; no new dependency added. ✓
- **Architecture:** the change respects the layering in `CONVENTIONS.md`. ✓
- **Outcome recorded:** `PASS`, reviewed by the senior engineer.

## The loop — observe

Released behind a feature flag to 5% of users. Monitored:

- transfer error rate (target: well under 0.1% of attempts);
- the rate of each rejection — a spike in `insufficient_funds` would suggest a UX problem (users not seeing their balance) rather than a code defect;
- latency of the atomic update under load.

A week later, telemetry shows an unexpectedly high `forbidden` rate. The `6_observe` prompt clusters it: users are trying to transfer *into* a shared account they can see but do not own. That observation becomes a `SPEC.md` delta — "support transfers into accounts I am authorized on, not only accounts I own" — and the flow returns to Step 1 for the next cycle.

---

This is the whole method in one feature: four artifacts written in order, an AI build bounded by them, a verification grounded in evidence plus the one check tests miss, and a loop that turns production reality into the next specification.

---

## Multi-component, end to end

The example above is a single codebase with one green bar. Real slices often cross components — a backend endpoint and the frontend that calls it. ADD ships that slice *inside one milestone* using the component pillar (chapter 17). Here is the same flow, now spanning two components: a `gateway` backend that **produces** an `orders` contract, and a `web` frontend that **consumes** it.

### Declare the components

The two parts and the boundary between them are declared in `.add/components.toml` — never inferred:

```toml
[component.gateway]
root      = "apps/gateway"
green_bar = "pytest + pyright"
verify    = "pytest -q apps/gateway"

[component.web]
root      = "apps/web"
green_bar = "vitest + a11y"
verify    = "pnpm -C apps/web test"

[contract.orders]
producer  = "gateway"
consumers = ["web"]
```

One milestone, **list-orders slice**, holds two tasks: `orders-api` (the BE, `produces: orders`) and `orders-list` (the FE, `consumes: orders`).

### The backend freezes first → an immutable snapshot

`orders-api` carries a `component: gateway` and a `produces: orders` header. It runs the normal flow — specify, scenarios, contract — and the human freezes its §3:

```
GET /orders?status=  ->  200 { orders: [{ id, status, total, placedAt }], nextCursor }
                          400 { error: "bad_status" }
Status: FROZEN @ v1 — approved by the tech lead
```

The moment that contract freezes and the task crosses contract→tests, the engine writes an immutable snapshot — `.add/contracts/orders.json` — recording the id, producer, version, frozen date, and a hash over the frozen §3 shape. That file *is* the published interface.

### The frontend is held until the backend freezes

`orders-list` (`component: web`, `consumes: orders`) was started in the same milestone, but it must not commit to a shape the backend has not frozen. When it tries to advance scenarios→contract before the snapshot exists, the engine refuses:

```
$ python3 .add/tooling/add.py advance
add: error: producer_contract_unfrozen: orders-list consumes 'orders' but no frozen producer snapshot exists yet — the FE is held until gateway freezes
```

Once `orders.json` exists, the same `advance` succeeds: the FE writes its §3 against the frozen shape and **pins that snapshot's hash**. The slice is ordered by the contract, not by splitting BE and FE across two milestones.

If the backend later *re-opens* its §3 to change the shape, the engine holds the consumer `producer_contract_stale` rather than letting it pin a shape that is mid-change — and `add.py check` separately surfaces `contract_producer_stale` / `contract_snapshot_hashless` as never-red warnings. Freeze-recency, not just existence.

### Each task verifies against its own green bar

At the gate, the engine holds each task to *its* component. `orders-api` must cite `pytest + pyright` in its §6 evidence; `orders-list` must cite `vitest + a11y` — cite the wrong bar (or none) and the gate refuses `component_green_bar_uncited`. The engine never runs either suite; it **surfaces** the component's `verify` command so the operator sees exactly what to run:

```
$ python3 .add/tooling/add.py gate PASS
task 'orders-api' gate -> PASS
component: gateway · expected green-bar: pytest + pyright · verify: pytest -q apps/gateway   # run this suite — the engine does not (NO-EXEC)
```

Two tasks, one milestone, two green bars — each held to its own, each suite run by you.

### Across repositories — federation

When `gateway` and `web` live in *separate* repos, only the snapshot transport changes. The `web` repo declares where the producer publishes:

```toml
[federation.orders]
source = "../gateway/.add/contracts/orders.json"
pin    = "v1"
```

`add.py federate pull orders` validates the producer repo's published snapshot (valid JSON, matching id, a hash, matching version) and lands a byte-for-byte copy locally — from there the FE holds and pins exactly as in a monorepo. The pull is fail-loud: an unknown id, an unreadable source, a `source` that escapes the repo's allowlist (`federation_source_escapes`), an invalid snapshot, or a version mismatch each HARD-STOPS and lands nothing. Federation never builds the FE against a guessed, out-of-tree, or stale endpoint.

That is the component pillar in one slice: declare the parts, freeze the boundary, hold the consumer behind the producer, verify each part on its own bar, and carry the frozen contract across repos — all within the same six-step flow and its single contract-freeze approval.
