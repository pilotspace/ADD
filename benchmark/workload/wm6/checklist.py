"""WM6 FROZEN requirement checklist — scheduling correctness hardening.

Rows for wm6/PROMPT.md: timezone-correct overlap, half-open boundary + zero-length
400, idempotent create, and input hardening (400 not 500). Auth-carrying,
self-contained probes. NO LLM.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call

_ALICE = {"Authorization": "Bearer test-token-alice"}


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _mk(base, headers=_ALICE, **over):
    body = {"title": "T", "start_time": _future(48), "end_time": _future(49), "room_id": "r1"}
    body.update(over)
    return http_call("POST", f"{base}/bookings", body, headers=headers)


def _p_timezone_correct_overlap(base, ws):
    # same instant, different offsets -> same room -> conflict
    a_start = "2026-12-01T10:00:00+02:00"
    a_end = "2026-12-01T12:00:00+02:00"
    st1, _ = _mk(base, start_time=a_start, end_time=a_end, room_id="tz")
    if st1 not in (200, 201):
        return False
    b_start = "2026-12-01T08:00:00Z"  # == 10:00+02:00, same instant
    b_end = "2026-12-01T10:00:00Z"
    st2, _ = _mk(base, start_time=b_start, end_time=b_end, room_id="tz")
    return st2 == 409


def _p_boundary_half_open(base, ws):
    # one ends exactly when the other starts -> NO conflict (half-open [start,end))
    s1, e1 = _future(200), _future(201)
    st1, _ = _mk(base, start_time=s1, end_time=e1, room_id="bnd")
    st2, _ = _mk(base, start_time=e1, end_time=_future(202), room_id="bnd")
    return st1 in (200, 201) and st2 in (200, 201)


def _p_zero_length_400(base, ws):
    s = _future(300)
    status, _ = _mk(base, start_time=s, end_time=s, room_id="zl")  # zero-length
    return status == 400


def _p_idempotent_create(base, ws):
    key = {"Idempotency-Key": "wm6-key-1", **_ALICE}
    body = {"title": "Idem", "start_time": _future(400), "end_time": _future(401), "room_id": "idem"}
    st1, b1 = http_call("POST", f"{base}/bookings", body, headers=key)
    st2, b2 = http_call("POST", f"{base}/bookings", body, headers=key)  # retry same key+payload
    return st1 in (200, 201) and st2 in (200, 201) and b1.get("id") == b2.get("id")


def _p_input_hardening_400(base, ws):
    # a malformed datetime must be 400 with JSON, never 500 / stack trace
    status, body = _mk(base, start_time="not-a-datetime", room_id="ih")
    return status == 400 and isinstance(body, dict)


REQUIREMENTS = [
    {"id": "R-timezone-correct-overlap", "description": "overlap compares absolute instants across ISO offsets", "probe": _p_timezone_correct_overlap},
    {"id": "R-boundary-half-open", "description": "abutting bookings [start,end) do not conflict", "probe": _p_boundary_half_open},
    {"id": "R-zero-length-400", "description": "a zero-length booking (end==start) returns 400", "probe": _p_zero_length_400},
    {"id": "R-idempotent-create", "description": "retrying a create with the same Idempotency-Key returns the original booking", "probe": _p_idempotent_create},
    {"id": "R-input-hardening-400", "description": "malformed input returns 400 JSON, never 500", "probe": _p_input_hardening_400},
]
