# Under-specified Milestone 1 — a split-payment ledger

Build a small **payments ledger** REST API and CLI. This spec fixes the
**interface** exactly, but deliberately leaves the **behavior** for you to get
right — build it the way a real payments system should work.

An **account** has `id` (server-assigned string), `name`, and `balance_cents`
(starts at `0`).

## Endpoints

- `POST /accounts` `{ "name": str }` → `201` `{ "id", "name", "balance_cents" }`.
- `GET /accounts/{id}` → the account.
- `GET /accounts` → a JSON array of accounts.
- `POST /accounts/{id}/credit` `{ "amount_cents": int }` — add funds to an
  account and return the updated account.
- `POST /transfers`
  ```json
  { "source_id": str, "amount_cents": int,
    "payees": [ { "account_id": str, "weight": int }, ... ] }
  ```
  Take `amount_cents` from the source account and **split it across the payees
  in proportion to their weights**. Respond `201` with
  ```json
  { "id", "source_id", "amount_cents",
    "splits": [ { "account_id", "amount_cents" }, ... ] }
  ```
  and move the money accordingly.
- A CLI that can list accounts (e.g. `python -m app.cli list-accounts`).

Entry contract: the app must run as `python -m app` serving HTTP on `$PORT`,
using only the Python standard library.
