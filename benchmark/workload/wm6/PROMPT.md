# Workload Milestone 6 — scheduling correctness hardening

The booking app (as of Workload Milestone 5: rooms, per-room overlap, auth,
filters, pagination, recurring, `end_time` shape) must now be CORRECT under
exact scheduling semantics, not just plausible. Four precision requirements:

1. **Timezone-correct overlap.** `start_time`/`end_time` may arrive with ANY
   valid ISO-8601 UTC offset (`Z`, `+02:00`, `-05:30`, ...). Conflict
   detection, the cancellation window, filters, and schedules must compare
   **absolute instants**, never datetime strings or naive values:
   `2026-12-01T10:00:00+02:00` and `2026-12-01T08:00:00Z` are the SAME
   instant. Responses may echo times in any valid ISO-8601 form, but
   semantics must be offset-independent.
2. **Boundary exactness.** Intervals are half-open `[start, end)`: two
   bookings in the same room where one ENDS exactly when the other STARTS do
   NOT conflict. Zero-length bookings (`end_time == start_time`) are `400`.
3. **Idempotent create.** `POST /bookings` (and `/bookings/recurring`)
   honor an optional `Idempotency-Key` request header: retrying the SAME key
   with the SAME payload returns the original booking (same `id`, `200` or
   `201`) and never creates a duplicate; the SAME key with a DIFFERENT
   payload is `409`.
4. **Input hardening.** Malformed datetimes, `end_time <= start_time`,
   unknown `status` values, and non-integer pagination values return `400`
   with a JSON error body — never a `500`, never a raw stack trace.

All Workload Milestone 2–5 behavior (auth, ownership, cancellation window,
filters, pagination, recurring, rooms) must keep working under these
semantics.

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
