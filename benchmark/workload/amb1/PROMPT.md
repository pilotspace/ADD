# Workload Milestone A1 — waitlist and cancellation policy

The booking app must now support a **waitlist** and a firmer **cancellation
policy**. Build the following onto the existing app.

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

Keep every behavior from the previous milestones working. The app must still
run as `python -m app` on `$PORT`.
