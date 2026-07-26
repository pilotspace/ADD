# Workload Milestone A1 — booking service with waitlist and cancellation policy

Build a booking service as `app/`, runnable as `python -m app` on `$PORT`,
serving JSON over HTTP. Use only the Python standard library.

**Base behavior.**

- `POST /bookings` creates a booking from `{title, start_time, end_time,
  room_id}` and returns it with a server-assigned `id` and a `status` of
  `pending`. A request missing a required field returns `400`.
- `GET /bookings` lists bookings. `GET /bookings/{id}` returns one, or `404`.
- `DELETE /bookings/{id}` cancels a booking.
- Requests carry an `Authorization: Bearer <token>` header identifying the
  caller; a booking records who created it.
- Bookings may carry an optional integer `priority`.

**Waitlist and cancellation.**

1. **Waitlist on conflict.** When a create request conflicts with an existing
   booking in the same room, the request is added to that room's waitlist
   instead of being rejected. `POST /bookings` returns `202` with the
   waitlist position. Every booking request that cannot be placed immediately
   must be waitlisted, so the caller always has a position to poll.

2. **Rejection on conflict.** A create request that conflicts with an
   existing booking in the same room must be rejected with `409` and a
   `conflict` error code, so callers can retry against a different slot.

3. **Cancellation window.** A booking may be cancelled up to **24 hours
   before it starts**. Inside that window, `DELETE /bookings/{id}` returns
   `422`.

4. **Waitlist promotion.** When a booking is cancelled, the first entry on
   that room's waitlist is promoted into the freed slot and its status
   becomes `confirmed`.

5. **Priority.** Bookings may carry an optional `priority` field. A booking
   with a **higher priority** is promoted from the waitlist first.

6. **Position reporting.** `GET /rooms/{room_id}/waitlist` returns the
   room's waitlist. Positions are reported to the caller starting from
   position 1 for the entry that will be promoted next.

The app must run as `python -m app` on `$PORT` with no third-party packages.
