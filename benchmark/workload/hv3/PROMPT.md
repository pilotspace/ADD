# Hostile Milestone 3 — API keys & per-key token-bucket rate limiting

A cross-cutting change to the payments app from Hostile Milestone 2. Every
**mutating** request must now be authenticated and rate limited **per API key**.
All Hostile Milestone 1–2 behavior (accounts, split transfers, invoices,
pricing, settlement, conservation) must keep working for an authenticated caller
under the limit.

## API keys

- A valid API key is any non-empty string beginning with `bench-key-` (e.g.
  `bench-key-alice`), sent in the `X-API-Key` request header.
- Every **mutating** request (`POST`) requires a valid key. A missing key, or a
  key that does not begin with `bench-key-`, → `401`.
- **Reads** (`GET`) are open: no key required, and never rate limited.

## Per-key token bucket

Each API key has its own **token bucket**, isolated from every other key:

- **capacity 120 tokens**, refilling at **20 tokens per second**, up to capacity.
- A bucket starts full. Each mutating request consumes **1 token**.
- When the caller's bucket has no token, the request is rejected with `429` and a
  `Retry-After` response header — **without** performing the operation.
- Refill is computed from a **monotonic** clock (never wall-clock, which can jump
  backward and either stall or over-grant), so elapsed time drives the refill.
- Buckets are **per key**: one key exhausting its bucket must not throttle or
  delay any other key. There is no global/shared limiter.

## Rules

- A `429` never mutates state — a throttled transfer does not debit, a throttled
  invoice does not settle.
- Reads remain available even when a key's mutating bucket is exhausted.

Entry contract (unchanged): the app runs as `python -m app` serving HTTP on
`$PORT`, standard library only.
