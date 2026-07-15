# Hostile Milestone 4 — resilient outbound settlement & input hardening

The final hardening of the payments app from Hostile Milestone 3. A completed
transfer can now be **paid out** to an external provider, and that outbound call
must be **resilient**: it fails, retries, gives up, and protects itself with a
circuit breaker — never hangs, never double-pays. All Hostile Milestone 1–3
behavior (accounts, split transfers, invoices, pricing, API keys, per-key rate
limiting) must keep working unchanged. Every mutating endpoint below still
requires a valid `X-API-Key` and draws from its per-key bucket.

## Simulated provider (so the resilient path is observable)

The app talks to a simulated external payout provider whose behavior is driven
for testing:

- `PUT /admin/payout-backend` `{ "fail_next": int>=0, "mode": "error"|"timeout" }`
  — the next `fail_next` provider calls fail (`error` = transient failure;
  `timeout` = the call exceeds the per-attempt timeout). Sets provider health
  ONLY; it does NOT reset the circuit breaker.
- `POST /admin/reset` — clears ALL resilient state (circuit breaker, provider
  counters, `fail_next`).
- `GET /admin/payout-backend` → `{ "calls", "applied", "circuit_state", "fail_next" }`
  where `calls` counts provider invocations, `applied` counts DISTINCT settled
  transfers, and `circuit_state` ∈ `closed|open`.

## Payouts — the resilient wrapper

`POST /payouts` `{ "transfer_id": str }` pays out a completed transfer through
the wrapper and returns
```json
{ "payout_id", "transfer_id", "status", "attempts", "provider_applied" }
```
with `status` ∈ `settled|failed|circuit_open`. The wrapper's fixed contract:

1. **Timeout + bounded retries.** Each attempt has a **200 ms** timeout; the
   wrapper makes at most **3 attempts** (initial + 2 retries) with a short
   backoff. On a transient failure or a timeout it retries; if all attempts
   fail, `status="failed"`.
2. **Idempotency — never double-pay.** Every attempt for the same transfer
   carries the transfer id as its idempotency key, so the provider applies a
   given transfer **at most once** even across retries (`provider_applied` is
   `1` on `settled`, `0` on `failed`/`circuit_open`; `applied` never exceeds one
   per transfer).
3. **Circuit breaker.** After **3 consecutive failed payouts** the breaker
   **opens**: further payouts return `status="circuit_open"` immediately, WITHOUT
   calling the provider (`calls` does not increase). After a **1 s** cooldown the
   breaker goes **half-open** and allows one probe payout; if it succeeds the
   breaker **closes**, otherwise it re-opens.
4. An unknown `transfer_id` → `404`.

## Input hardening

Across every endpoint, malformed input is a `4xx` with a JSON error body — never
a `500`, never a stack trace: a JSON body that is not an object (a string, a
number, an array), a wrong-typed field (`amount_cents` as a string, `weight` as
a float), and the Hostile Milestone 1–2 malformed cases all return `400`.

Entry contract (unchanged): the app runs as `python -m app` serving HTTP on
`$PORT`, standard library only.
