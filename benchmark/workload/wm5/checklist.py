"""WM5 FROZEN requirement checklist — rooms + per-room overlap.

Rows for wm5/PROMPT.md: required room_id, per-room (not per-owner) overlap,
the room schedule endpoint. Auth-carrying, self-contained probes. NO LLM.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call, records

_ALICE = {"Authorization": "Bearer test-token-alice"}
_BOB = {"Authorization": "Bearer test-token-bob"}


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _mk(base, headers=_ALICE, **over):
    body = {"title": "T", "start_time": _future(48), "end_time": _future(49), "room_id": "r1"}
    body.update(over)
    return http_call("POST", f"{base}/bookings", body, headers=headers)


def _p_room_required_400(base, ws):
    body = {"title": "T", "start_time": _future(48), "end_time": _future(49)}  # no room_id
    status, _ = http_call("POST", f"{base}/bookings", body, headers=_ALICE)
    return status == 400


def _p_per_room_overlap_409(base, ws):
    s, e = _future(72), _future(73)
    st1, _ = _mk(base, headers=_ALICE, start_time=s, end_time=e, room_id="rX")
    if st1 not in (200, 201):
        return False
    # DIFFERENT owner, SAME room, overlapping -> conflict (per-room, cross-owner)
    st2, resp = _mk(base, headers=_BOB, start_time=s, end_time=e, room_id="rX")
    return st2 == 409


def _p_different_rooms_no_conflict(base, ws):
    s, e = _future(96), _future(97)
    st1, _ = _mk(base, start_time=s, end_time=e, room_id="rA")
    st2, _ = _mk(base, start_time=s, end_time=e, room_id="rB")  # same time, other room
    return st1 in (200, 201) and st2 in (200, 201)


def _p_room_schedule_endpoint(base, ws):
    _mk(base, room_id="rSched", start_time=_future(120), end_time=_future(121))
    status, body = http_call("GET", f"{base}/rooms/rSched/schedule", headers=_ALICE)
    return status == 200 and records(body) is not None


REQUIREMENTS = [
    {"id": "R-room-required-400", "description": "a create/update missing room_id returns 400", "probe": _p_room_required_400},
    {"id": "R-per-room-overlap-409", "description": "two bookings in the same room overlap-conflict regardless of owner (409)", "probe": _p_per_room_overlap_409},
    {"id": "R-different-rooms-no-conflict", "description": "same-time bookings in different rooms do not conflict", "probe": _p_different_rooms_no_conflict},
    {"id": "R-room-schedule", "description": "GET /rooms/{id}/schedule returns that room's bookings", "probe": _p_room_schedule_endpoint},
]
