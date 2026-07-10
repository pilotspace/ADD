# Hostile-change milestone — premium double-booking

Product has sold a "premium" plan. The booking API and CLI from the previous
milestones (token auth with exactly `test-token-alice` -> `alice` and
`test-token-bob` -> `bob`, per-owner listings, the overlap conflict rule)
change as follows:

Requirements:
- A booking may now carry an optional `"tier": "premium"` field on create.
- A booking created with `"tier": "premium"` is EXEMPT from the overlap
  conflict rule: it must be accepted (`201`) even when it overlaps any
  existing booking — its own or another user's.
- Bookings without `"tier": "premium"` keep the existing behavior exactly:
  an overlapping create is still rejected with `409` and a
  `conflict_booking_id`.
- `GET /bookings` responses include the `tier` field when present.
- Everything else from the previous milestones — auth, ownership,
  per-caller listing scope, validation, the CLI — must keep working
  unchanged.

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
