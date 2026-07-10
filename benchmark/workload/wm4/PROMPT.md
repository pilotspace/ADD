# Workload Milestone 4 — search, pagination & recurring bookings

The booking app (as it stands after Workload Milestone 3: `end_time` shape,
token auth, ownership, overlap and cancellation rules) grows three features:

Requirements:
- **Filtering**: `GET /bookings` accepts optional query params `status`
  (exact match), `from` and `to` (ISO-8601; return bookings whose time range
  intersects the `[from, to]` window). Params combine (AND).
- **Pagination**: `GET /bookings` accepts optional `limit` (positive int) and
  `offset` (non-negative int) applied AFTER filtering, in stable
  `start_time` order. Invalid values get `400`.
- **Recurring bookings**: `POST /bookings/recurring` accepts a booking body
  (same shape as `POST /bookings`, with `end_time`) plus `"repeats": N`
  (2–52). It creates N bookings, each shifted exactly one week from the
  previous. EVERY instance must pass the existing double-booking overlap
  rule — if any instance would overlap, the whole request is rejected with
  `409` and NO bookings are created (all-or-nothing).
- All WM2/WM3 behavior (auth, ownership, cancellation window, `end_time`
  shape) keeps working unchanged. The CLI gains `list` flags for the same
  filters (`--status`, `--from`, `--to`, `--limit`, `--offset`).

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
