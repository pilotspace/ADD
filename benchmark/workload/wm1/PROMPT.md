# Workload Milestone 1 — task/booking core CRUD

Build a small task/booking REST API and CLI. A "booking" has: `id` (string,
server-generated), `title` (string, required), `start_time` (ISO-8601 string,
required), `duration_minutes` (positive integer, required), `status` (one of
`pending`, `confirmed`, `cancelled` — default `pending`).

Requirements:
- REST endpoints: `POST /bookings` (create), `GET /bookings` (list),
  `GET /bookings/{id}` (fetch one), `PATCH /bookings/{id}` (update fields),
  `DELETE /bookings/{id}` (remove).
- A CLI (`app-cli`) that can create, list, show, update, and delete a booking
  by calling the same underlying logic as the REST API (no separate storage).
- Storage may be in-memory or a local file — your choice — but must persist
  for the lifetime of the running process.
- Return `404` for an unknown booking id on GET/PATCH/DELETE, and `400` for a
  create/update payload missing a required field.

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
