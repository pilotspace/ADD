"""WM4 FROZEN requirement checklist — filtering, pagination, recurring bookings.

Rows for wm4/PROMPT.md's new features over the WM3 (end_time) shape. Auth-carrying,
self-contained (base, workspace) probes. NO LLM.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call

_ALICE = {"Authorization": "Bearer test-token-alice"}


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _mk(base, **over):
    body = {"title": "T", "start_time": _future(48), "end_time": _future(49)}
    body.update(over)
    return http_call("POST", f"{base}/bookings", body, headers=_ALICE)


def _p_filter_status(base, ws):
    status, body = http_call("GET", f"{base}/bookings?status=confirmed", headers=_ALICE)
    if status != 200 or not isinstance(body, list):
        return False
    return all(b.get("status") == "confirmed" for b in body)


def _p_filter_time_window(base, ws):
    # a from..to window far in the past must return an empty (or intersecting-only) list
    status, body = http_call(
        "GET", f"{base}/bookings?from=2000-01-01T00:00:00Z&to=2000-01-02T00:00:00Z", headers=_ALICE)
    return status == 200 and isinstance(body, list) and len(body) == 0


def _p_pagination_limit_offset(base, ws):
    status, body = http_call("GET", f"{base}/bookings?limit=1&offset=0", headers=_ALICE)
    return status == 200 and isinstance(body, list) and len(body) <= 1


def _p_pagination_invalid_400(base, ws):
    status, _ = http_call("GET", f"{base}/bookings?limit=-3", headers=_ALICE)
    return status == 400


def _p_recurring_creates_n(base, ws):
    body = {"title": "R", "start_time": _future(200), "end_time": _future(201), "repeats": 3}
    status, resp = http_call("POST", f"{base}/bookings/recurring", body, headers=_ALICE)
    if status not in (200, 201):
        return False
    # response should reflect 3 created (a list of 3, or a count)
    if isinstance(resp, list):
        return len(resp) == 3
    return resp.get("created") == 3 or resp.get("count") == 3


def _p_recurring_all_or_nothing_409(base, ws):
    # a recurring set that self-overlaps (repeat interval < booking length) is rejected whole
    s = _future(400)
    e = (datetime.fromisoformat(s.replace("Z", "+00:00")) + timedelta(days=14)).isoformat()
    body = {"title": "R2", "start_time": s, "end_time": e, "repeats": 3}
    status, _ = http_call("POST", f"{base}/bookings/recurring", body, headers=_ALICE)
    return status == 409


REQUIREMENTS = [
    {"id": "R-filter-status", "description": "GET /bookings?status= filters by exact status", "probe": _p_filter_status},
    {"id": "R-filter-time-window", "description": "GET /bookings?from=&to= returns only intersecting bookings", "probe": _p_filter_time_window},
    {"id": "R-pagination-limit-offset", "description": "GET /bookings honors limit/offset after filtering", "probe": _p_pagination_limit_offset},
    {"id": "R-pagination-invalid-400", "description": "an invalid limit/offset returns 400", "probe": _p_pagination_invalid_400},
    {"id": "R-recurring-creates-n", "description": "POST /bookings/recurring with repeats:N creates N bookings", "probe": _p_recurring_creates_n},
    {"id": "R-recurring-all-or-nothing-409", "description": "a recurring set with an overlapping instance is rejected whole (409)", "probe": _p_recurring_all_or_nothing_409},
]
