# Appendix D · The worked example, end to end

[← Appendix C Glossary](./appendix-c-glossary.md) · [Contents](./README.md) · Next: [Appendix E Checklists →](./appendix-e-checklists.md)

The running example in one place: **transfer money between a user's own accounts**, taken through the whole 4.0 loop — task file, red run, seal, build, verify, verdict, report.

Every command output and commit hash on this page is real: the example was run in a scratch Python repository with `pytest`. The agent's reasoning between the commands is paraphrased.

---

## The starting point

A small project with an `Account` type and one test. `.add/PROJECT.md`:

```markdown
---
type: Project
title: payments
goal: let customers hold and move money between their own accounts
invariants:
  - money is never created or destroyed by a transfer
  - the test suite runs offline with no credentials
test_cmd: python3 -m pytest -q
stage: mvp
---
## CARD
goal: let customers hold and move money between their own accounts
state: accounts exist; transfers not started
next: transfer between own accounts
```

The request: *"Let users transfer money between their own accounts."* It moves money, so it touches **data** — the floor makes it at least a Task, never Quick.

## Direction — the task file

After reading `src/accounts.py` (balances are integer cents and may be 0), the agent writes `.add/tasks/transfer-own-accounts.md` in one pass:

```markdown
---
type: Task
title: transfer between own accounts
status: build
kind: feature
sensitivity: data
scope: [src/transfers.py, tests/test_transfer_contract.py]
gives:
  - S1 transfer(ledger, caller, from_id, to_id, amount) -> {from_balance, to_balance} | raises TransferError(status, code)
---
## CARD
goal: move money between two accounts the caller owns
why: the first payments slice; later payment features build on this shape

## RULES
- M1 a transfer between two accounts the caller owns debits the source and credits the destination by the amount (from: request)
- R:AMOUNT_INVALID amount <= 0 is refused with 400 "amount_invalid"; no balance changes (from: request)
- R:SAME_ACCOUNT source == destination is refused with 400 "same_account" (from: request)
- R:INSUFFICIENT a source balance below the amount is refused with 400 "insufficient_funds"; no balance changes (from: request)
- R:FORBIDDEN an account the caller does not own is refused with 403 "forbidden"; no balance changes (from: request)

## ASSUMPTIONS
- A1 [which] currency is not mentioned → one currency, amounts in integer cents · found: balances are integer cents (evidence: src/accounts.py:8)
- A2 [order] two transfers from one account at once are not mentioned → the check and the debit happen under one lock → without it, two transfers can both pass the balance check and overdraw
- A3 [when] amount == balance is not mentioned → allowed; leaves 0 · found: a balance may be 0 (evidence: src/accounts.py:8)
- A4 [who] the destination's owner is not mentioned → both source and destination must be the caller's → if transfers to others are wanted, R:FORBIDDEN is too strict
- A5 [absent] an unknown account id is not mentioned → refused as "forbidden", so the response never reveals whether an id exists → a caller cannot tell a typo from a foreign account
- A6 [experience] n/a · internal service call; the error code is the contract

## PLAN
strategy: look up both accounts, check ownership, then amount, then same-account, then balance, all under one lock; debit and credit together
check: python3 -m pytest -q tests/test_transfer_contract.py
regression: python3 -m pytest -q

## CHECKS
- C1 covers: M1 · acceptance · tests/test_transfer_contract.py::test_moves_the_amount
- C2 covers: R:AMOUNT_INVALID · acceptance · tests/test_transfer_contract.py::test_non_positive_amount_refused_nothing_moves
- C3 covers: R:SAME_ACCOUNT · acceptance · tests/test_transfer_contract.py::test_same_account_refused
- C4 covers: R:INSUFFICIENT, A3 · acceptance · tests/test_transfer_contract.py::test_overdraw_refused_exact_balance_allowed
- C5 covers: R:FORBIDDEN, A4, A5 · acceptance · tests/test_transfer_contract.py::test_foreign_or_unknown_account_forbidden
- C6 covers: A2 · property · tests/test_transfer_contract.py::test_parallel_transfers_never_overdraw
```

Two assumptions (A1, A3) were cheap to check, so they carry `found:` with a citation. A4 and A5 are real product decisions the request did not make — exactly what the human should read in the report.

## Direction — the checks, red for the right reason

The checks live in their own file. Every refusal is asserted to leave balances untouched:

```python
def refused(led, *args):
    before = led.balances()
    with pytest.raises(TransferError) as err:
        transfer(led, *args)
    assert led.balances() == before, "a refused transfer moved money"
    return err.value.status, err.value.code


def test_foreign_or_unknown_account_forbidden():
    led = ledger(a=5_000, b=0, x=5_000)
    assert refused(led, "me", "x", "a", 100) == (403, "forbidden")      # foreign source
    assert refused(led, "me", "a", "x", 100) == (403, "forbidden")      # foreign destination
    assert refused(led, "me", "a", "nope", 100) == (403, "forbidden")   # unknown id
```

A one-line stub (`def transfer(...): raise NotImplementedError`) gives the checks a seam to call, so they fail on missing behavior rather than on an import error:

```text
$ python3 -m pytest -q tests/test_transfer_contract.py
FAILED tests/test_transfer_contract.py::test_moves_the_amount - NotImplemente...
FAILED tests/test_transfer_contract.py::test_non_positive_amount_refused_nothing_moves[0]
FAILED tests/test_transfer_contract.py::test_non_positive_amount_refused_nothing_moves[-1]
FAILED tests/test_transfer_contract.py::test_same_account_refused - NotImplem...
FAILED tests/test_transfer_contract.py::test_overdraw_refused_exact_balance_allowed
FAILED tests/test_transfer_contract.py::test_foreign_or_unknown_account_forbidden
FAILED tests/test_transfer_contract.py::test_parallel_transfers_never_overdraw
7 failed, 20 warnings in 0.03s
```

Every failure is `NotImplementedError` — the behavior is absent. Red for the right reason.

## The seal

With `status: build` set in the task file:

```bash
git add .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py src/transfers.py
git commit -m "freeze(transfer-own-accounts): move money between two accounts the caller owns"
```

```text
1bfa9ee freeze(transfer-own-accounts): move money between two accounts the caller owns
```

## Build

The agent writes `src/transfers.py` — ownership first (so no error reveals whether an id exists), then amount, same-account and balance, all under one lock:

```python
def transfer(ledger, caller, from_id, to_id, amount):
    with ledger.lock:
        source = ledger.owned(caller, from_id)
        dest = ledger.owned(caller, to_id)
        if amount <= 0:
            raise TransferError(400, "amount_invalid")
        if source is dest:
            raise TransferError(400, "same_account")
        if source.balance < amount:
            raise TransferError(400, "insufficient_funds")
        source.balance -= amount
        dest.balance += amount
        return {"from_balance": source.balance, "to_balance": dest.balance}
```

```text
$ python3 -m pytest -q tests/test_transfer_contract.py
7 passed in 0.01s
```

```text
f536334 feat(transfers): transfer between own accounts under one lock
```

## Verify — and a check that could not fail

**Seal intact.** `git diff 1bfa9ee HEAD -- .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py` prints nothing.

**Refute.** A2 — concurrency — is the one property the other checks do not force, so the first probe goes there: remove the lock and see whether C6 notices.

```text
$ python3 -m pytest -q tests/test_transfer_contract.py      # lock removed, five runs
7 passed in 0.01s
7 passed in 0.01s
7 passed in 0.01s
7 passed in 0.01s
7 passed in 0.01s
```

C6 passes without the lock. Nothing in it forces a thread switch between the balance check and the debit, so it cannot fail on the implementation it exists to catch. The build is fine; **the check was mis-aimed** — which is a refreeze, not a quiet edit. The check's accounts now yield on every balance read:

```python
class SlowAccount(Account):
    """Yields to other threads on every balance read, so an unguarded check-then-debit interleaves."""

    @property
    def balance(self):
        time.sleep(0.001)
        return self._balance

    @balance.setter
    def balance(self, cents):
        self._balance = cents
```

Against the lock-free build it now fails; against the real build it passes:

```text
$ python3 -m pytest -q tests/test_transfer_contract.py      # lock removed
FAILED tests/test_transfer_contract.py::test_parallel_transfers_never_overdraw
1 failed, 6 passed in 0.03s
$ python3 -m pytest -q tests/test_transfer_contract.py      # the real build
7 passed in 0.09s
```

The reason goes under `## LOG`, and the task file and check file are committed together:

```markdown
## LOG
- refreeze: C6 could not fail — with the lock removed it still passed 5 of 5 runs, because nothing forced a thread switch between the balance check and the debit; its accounts now yield on every balance read, and the lock-free build fails it
```

```text
3a4b3a7 refreeze(transfer-own-accounts): C6 could not fail under the lock-free mutant; accounts now yield on balance reads
```

**Verify again, from the refreeze.**

```bash
F=$(git log -1 --format=%H --grep='freeze(transfer-own-accounts)')    # → 3a4b3a7
git diff $F HEAD -- .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py   # → empty
```

On a clean tree:

```text
$ python3 -m pytest -q tests/test_transfer_contract.py      → exit 0
7 passed in 0.09s
$ python3 -m pytest -q                                      → exit 0
8 passed in 0.09s
```

**Residue.** Security — ownership is checked before amount or balance, so no error reveals whether an id exists. Concurrency — check and debit run under one lock, and C6 now proves it. Architecture — one new module, no new dependency.

**Refute.** The task is `sensitivity: data`, so the skill has a fresh subagent read the task file before the diff and derive probes from the sealed rules. Three probes, run against the real build:

```text
smallest amount, exact balance: a->b 1 -> {'from_balance': 0, 'to_balance': 1}
foreign source AND zero amount: x->a 0 -> 403 forbidden
unknown source AND overdraw: nope->a 999 -> 403 forbidden
```

All consistent with the rules and with A3 and A5. Held.

## The verdict

`status: done`, and `## EVIDENCE` is written:

```markdown
## EVIDENCE
freeze: 3a4b3a7 (refreeze of 1bfa9ee) · head: 3a4b3a7
seal: git diff 3a4b3a7 3a4b3a7 -- .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py → empty
check: `python3 -m pytest -q tests/test_transfer_contract.py` → exit 0 · 7 passed
regression: `python3 -m pytest -q` → exit 0 · 8 passed
residue: security — ownership is checked before amount or balance, so no error reveals whether an id exists; concurrency — check and debit run under one lock, and C6 now fails without it; architecture — src/transfers.py only, no new dependency
refute: a->b 1 from a balance of 1 → allowed, leaves 0; foreign source + amount 0 → 403 forbidden; unknown source + overdraw → 403 forbidden · held
verdict: PASS
```

```text
99f2b86 verify(transfer-own-accounts): PASS
3a4b3a7 refreeze(transfer-own-accounts): C6 could not fail under the lock-free mutant; accounts now yield on balance reads
f536334 feat(transfers): transfer between own accounts under one lock
1bfa9ee freeze(transfer-own-accounts): move money between two accounts the caller owns
56ad754 chore: accounts
```

The history tells the whole story without anyone narrating it: sealed, built, a check found wanting and re-aimed in the open, verified.

## Learn

One lesson is worth keeping, with its evidence, in `.add/specs/quality.md`:

```markdown
## Deltas
- 2026-09-28 open · a concurrency property check passes without the lock unless the test forces a thread switch between check and write — verify it against a lock-free mutant (evidence: refreeze(transfer-own-accounts) 3a4b3a7)
```

## The report

```markdown
No HARD-STOPs. No open risks.

transfer-own-accounts — move money between two accounts the caller owns
  verdict: PASS · freeze 1bfa9ee, refrozen 3a4b3a7 (C6 could not fail; re-aimed) · verify 99f2b86
  evidence: 7/7 task checks, 8/8 suite, fresh on 3a4b3a7; 3 refute probes held
  assumptions taken — please check:
    A2 check and debit under one lock (a single-process ledger; a database would need a row lock)
    A4 both accounts must be the caller's — transfers to other users are refused as forbidden
    A5 unknown account ids are refused as "forbidden", indistinguishable from foreign ones
    A1, A3 checked in code (integer cents; zero balances allowed)
next: PROJECT.md CARD — state: own-account transfers verified · next: transfer history
```

The human reads this once. If A4 is wrong — transfers to other users *were* wanted — that is one sentence back, and a new task.
