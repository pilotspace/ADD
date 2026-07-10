# Workload Milestone 3 — breaking-change refactor (regression bait)

The booking shape from Workload Milestone 1 is being replaced: the
`duration_minutes` field (frozen in WM1) is now REMOVED from the booking
resource. Bookings are represented by an explicit `end_time` (ISO-8601
string, required, must be after `start_time`) instead of a duration. This is
a genuine breaking change to the WM1-frozen booking shape — every endpoint
and CLI command that reads or writes `duration_minutes` must be migrated to
`end_time`, including the overlap and cancellation-window business rules
from Workload Milestone 2, which must keep working unchanged in behavior
(just computed from `end_time` instead of `start_time + duration_minutes`).

Requirements:
- `POST /bookings` and the CLI create command accept `end_time` instead of
  `duration_minutes`; requests still sending `duration_minutes` get `400`.
- `GET`/list responses no longer include `duration_minutes`; they include
  `end_time`.
- All WM2 business rules (double-booking overlap, cancellation window,
  ownership, auth) must continue to hold under the new shape.
- This is a deliberate shape break: do not keep `duration_minutes` for
  backward compatibility.

Entry contract (must hold for every workload milestone in this benchmark):
the app must run as `python -m app` serving HTTP on `$PORT`.
