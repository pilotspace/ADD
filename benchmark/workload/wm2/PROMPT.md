# Workload Milestone 2 — business rules + auth

Extend the task/booking REST API and CLI from the previous milestone with:

- Authentication: every request must include a header `Authorization: Bearer
  <token>`. Exactly these tokens are valid, mapping to these user ids
  (hardcoding this fixed set is expected — it is the test credential set):
  `test-token-alice` -> `alice` and `test-token-bob` -> `bob`. Requests
  without a valid token get `401`.
- Ownership: a booking now has an `owner_id` field, set from the
  authenticated caller on create. A caller may only `PATCH`/`DELETE` a
  booking they own — otherwise `403`.
- Business rule — no double-booking: two bookings for the SAME owner may not
  overlap in time (`start_time` .. `start_time + duration_minutes`). A
  create/update that would overlap an existing booking for that owner
  returns `409` with a `conflict_booking_id` field naming the clashing
  booking.
- Business rule — cancellation window: a booking may only transition to
  `status: cancelled` if `start_time` is more than 1 hour in the future;
  otherwise `422`.
- The `GET /bookings` and CLI list command must only return bookings owned
  by the authenticated caller (no cross-tenant leakage).

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
