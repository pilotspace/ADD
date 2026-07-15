"""WM2 FROZEN requirement checklist — auth + business rules over WM1 CRUD.

One row per NEW requirement introduced in wm2/PROMPT.md (auth, ownership,
no-double-booking, cancellation window, tenant isolation). Carried WM1 CRUD is
covered by the regression path; this checklist probes what WM2 adds. Probes are
self-contained (base, workspace) callables and auth-carrying. NO LLM.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call

_ALICE = {"Authorization": "Bearer test-token-alice"}
_BOB = {"Authorization": "Bearer test-token-bob"}


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _mk(base, headers=_ALICE, **over):
    body = {"title": "T", "start_time": _future(48), "duration_minutes": 30}
    body.update(over)
    return http_call("POST", f"{base}/bookings", body, headers=headers)


def _p_auth_401(base, ws):
    status, _ = http_call("GET", f"{base}/bookings")  # no token
    return status == 401


def _p_ownership_403(base, ws):
    status, created = _mk(base, headers=_ALICE)
    if status not in (200, 201):
        return False
    bid = created.get("id")
    denied, _ = http_call("PATCH", f"{base}/bookings/{bid}", {"status": "confirmed"}, headers=_BOB)
    return denied == 403


def _p_double_booking_409(base, ws):
    s = _future(72)
    st1, _ = _mk(base, start_time=s, duration_minutes=60)
    if st1 not in (200, 201):
        return False
    st2, body = _mk(base, start_time=s, duration_minutes=60)  # exact overlap
    return st2 == 409 and isinstance(body, dict) and "conflict_booking_id" in body


def _p_cancellation_window_422(base, ws):
    status, created = _mk(base, start_time=_future(0))  # starts ~now, <1h away
    if status not in (200, 201):
        return False
    bid = created.get("id")
    blocked, _ = http_call("PATCH", f"{base}/bookings/{bid}", {"status": "cancelled"}, headers=_ALICE)
    return blocked == 422


def _p_tenant_isolation(base, ws):
    _mk(base, headers=_ALICE, start_time=_future(96))
    status, body = http_call("GET", f"{base}/bookings", headers=_BOB)
    if status != 200 or not isinstance(body, list):
        return False
    return all(b.get("owner_id", "bob") == "bob" for b in body)  # bob sees only bob's


REQUIREMENTS = [
    {"id": "R-auth-401", "description": "a request without a valid token returns 401", "probe": _p_auth_401},
    {"id": "R-ownership-403", "description": "a non-owner PATCH/DELETE returns 403", "probe": _p_ownership_403},
    {"id": "R-double-booking-409", "description": "an overlapping booking for the same owner returns 409 with conflict_booking_id", "probe": _p_double_booking_409},
    {"id": "R-cancellation-window-422", "description": "cancelling a booking starting within 1h returns 422", "probe": _p_cancellation_window_422},
    {"id": "R-tenant-isolation", "description": "GET /bookings returns only the caller's own bookings", "probe": _p_tenant_isolation},
]
