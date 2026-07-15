# Hostile Milestone 1 — split-payment ledger core

Build a small **payments ledger** REST API and CLI. Money is the domain, so
correctness is measured to the cent. An **account** has `id` (server-assigned
string), `name`, and `balance_cents` (integer minor units, starts at `0`).

All amounts are **integer cents** — never a float, never a fractional balance,
anywhere in a request or response.

## Requirements

1. **Accounts.**
   - `POST /accounts` `{ "name": str }` → `201` `{ "id", "name", "balance_cents": 0 }`.
   - `GET /accounts/{id}` → the account; `404` if unknown.
   - `GET /accounts` → a JSON array of accounts.
   - `POST /accounts/{id}/credit` `{ "amount_cents": int>0 }` funds an account
     (an external deposit): balance increases by `amount_cents`, returns the
     updated account. Non-positive or non-integer `amount_cents` → `400`.

2. **Split transfer — reconciles exactly.**
   `POST /transfers`
   ```json
   { "source_id": str, "amount_cents": int>0,
     "payees": [ { "account_id": str, "weight": int>=1 }, ... ] }
   ```
   debits `source_id` by `amount_cents` and splits that amount across the
   payees **proportional to their integer weights**. The split MUST reconcile
   **exactly**: the sum of the payees' credited shares equals `amount_cents` —
   not a cent created, not a cent lost. Compute it with integer arithmetic:

   - `W = sum(weight)`, `base_i = (amount_cents * weight_i) // W`.
   - Hand out the leftover `amount_cents - sum(base_i)` cents (which is
     `0..len(payees)-1`) **one cent each** to the payees with the largest
     remainder `(amount_cents * weight_i) mod W`, breaking ties by **lowest
     payee index** (position in the `payees` array).
   - `share_i = base_i (+1 if it received a leftover cent)`.

   Response `201`:
   ```json
   { "id", "source_id", "amount_cents",
     "splits": [ { "account_id", "amount_cents" }, ... ] }
   ```
   Each payee account's balance increases by its share; the source's balance
   decreases by `amount_cents`. Worked example: `amount_cents=100`, three
   payees of equal `weight` → shares `[34, 33, 33]` (payee 0 wins the tie).

3. **Insufficient funds.** A transfer whose `amount_cents` exceeds the source
   balance → `409`, with **no** balance change to any account (all-or-nothing;
   never a partial debit).

4. **Idempotent create.** `POST /transfers` honors an optional
   `Idempotency-Key` request header. Retrying the SAME key with the SAME body
   returns the ORIGINAL transfer (same `id`, `200` or `201`) and never debits
   twice. The SAME key with a DIFFERENT body → `409`.

5. **Input hardening.** `amount_cents` non-positive or non-integer, an empty
   `payees` array, a `weight < 1`, an unknown `source_id` or payee
   `account_id` → a `4xx` (`400` for malformed input, `404` for an unknown
   account) with a JSON error body — **never** a `500`, never a raw stack
   trace, never a partial mutation.

6. **Conservation.** Across any sequence of credits and transfers, no money is
   created or destroyed: the sum of all account balances equals the total ever
   credited via `POST /accounts/{id}/credit`. (A transfer only moves cents
   between existing balances.)

7. **CLI parity.** A CLI lists accounts via the same underlying store (e.g.
   `python -m app.cli list-accounts`).

Entry contract (must hold for every hostile milestone in this benchmark): the
app must run as `python -m app` serving HTTP on `$PORT`, using only the Python
standard library.
