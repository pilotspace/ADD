"""WM3 FROZEN requirement checklist — the end_time shape break.

Rows for wm3/PROMPT.md's NEW/CHANGED requirements: end_time replaces
duration_minutes, requests still sending duration_minutes are 400, list omits
duration_minutes, and the WM2 rules keep holding under the new shape. Auth-carrying,
self-contained (base, workspace) probes. NO LLM.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call

_ALICE = {"Authorization": "Bearer test-token-alice"}


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _mk(base, **over):
    start = over.pop("start_time", _future(48))
    body = {"title": "T", "start_time": start, "end_time": _future(49)}
    body.update(over)
    return http_call("POST", f"{base}/bookings", body, headers=_ALICE)


def _p_end_time_shape(base, ws):
    status, created = _mk(base)
    if status not in (200, 201):
        return False
    bid = created.get("id")
    got, body = http_call("GET", f"{base}/bookings/{bid}", headers=_ALICE)
    return got == 200 and "end_time" in body


def _p_duration_rejected_400(base, ws):
    body = {"title": "T", "start_time": _future(48), "duration_minutes": 30}
    status, _ = http_call("POST", f"{base}/bookings", body, headers=_ALICE)
    return status == 400


def _p_list_no_duration(base, ws):
    _mk(base)
    status, body = http_call("GET", f"{base}/bookings", headers=_ALICE)
    if status != 200 or not isinstance(body, list) or not body:
        return False
    return all("duration_minutes" not in b and "end_time" in b for b in body)


def _p_wm2_overlap_holds(base, ws):
    s, e = _future(72), _future(73)
    st1, _ = _mk(base, start_time=s, end_time=e)
    if st1 not in (200, 201):
        return False
    st2, resp = _mk(base, start_time=s, end_time=e)
    return st2 == 409 and isinstance(resp, dict) and "conflict_booking_id" in resp


REQUIREMENTS = [
    {"id": "R-end-time-shape", "description": "POST/GET use end_time instead of duration_minutes", "probe": _p_end_time_shape},
    {"id": "R-duration-rejected-400", "description": "a request still sending duration_minutes returns 400", "probe": _p_duration_rejected_400},
    {"id": "R-list-no-duration", "description": "list responses omit duration_minutes and include end_time", "probe": _p_list_no_duration},
    {"id": "R-wm2-overlap-holds", "description": "the WM2 double-booking rule still holds under the end_time shape", "probe": _p_wm2_overlap_holds},
]
