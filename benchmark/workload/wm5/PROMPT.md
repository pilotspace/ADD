# Workload Milestone 5 — rooms: a cross-cutting scheduling change

Bookings now happen in **rooms**, and scheduling conflicts are per-room
rather than per-user. This cuts across every existing feature (as of
Workload Milestone 4: `end_time` shape, auth, ownership, filters,
pagination, recurring).

Requirements:
- Every booking has a required `room_id` (non-empty string). Create/update
  payloads missing it get `400`; existing endpoints include it in responses.
- **The overlap rule changes scope**: two bookings in the SAME room may not
  overlap in time, regardless of which user owns them (`409` on conflict).
  Bookings in different rooms never conflict. This replaces the per-owner
  overlap rule; recurring creation applies the new rule per instance
  (still all-or-nothing).
- `GET /rooms/{room_id}/schedule` returns that room's non-cancelled bookings
  ordered by `start_time` (auth required; every caller may read any room's
  schedule; each entry includes `id`, `title`, `start_time`, `end_time`,
  `owner`).
- All WM2–WM4 behavior (auth, ownership of edits, cancellation window,
  filters, pagination, recurring, `end_time` shape) keeps working, now
  room-aware. The CLI create/update commands accept `--room`.

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
