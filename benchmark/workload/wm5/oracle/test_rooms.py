"""WM5 oracle — rooms: per-room overlap, schedule endpoint. Never visible to the arm."""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

TOKEN_A = "test-token-alice"
TOKEN_B = "test-token-bob"


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _mk(base, title, start, end, room, token=TOKEN_A):
    return http_call(
        "POST", f"{base}/bookings",
        {"title": title, "start_time": start, "end_time": end, "room_id": room},
        _auth(token))


def test_room_id_required():
    with running_app(_workspace()) as base:
        status, _ = http_call(
            "POST", f"{base}/bookings",
            {"title": "NoRoom", "start_time": "2026-12-01T09:00:00Z",
             "end_time": "2026-12-01T10:00:00Z"}, _auth(TOKEN_A))
        assert status == 400


def test_room_id_returned():
    with running_app(_workspace()) as base:
        status, body = _mk(base, "R1", "2026-12-01T09:00:00Z", "2026-12-01T10:00:00Z", "room-1")
        assert status in (200, 201), body
        assert body["room_id"] == "room-1"


def test_same_room_cross_user_overlap_rejected():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "A", "2026-12-02T09:00:00Z", "2026-12-02T10:00:00Z", "room-1", TOKEN_A)
        assert status in (200, 201)
        status, _ = _mk(base, "B", "2026-12-02T09:30:00Z", "2026-12-02T10:30:00Z", "room-1", TOKEN_B)
        assert status == 409, "same room, different users, overlapping — must conflict"


def test_different_rooms_never_conflict():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "A", "2026-12-03T09:00:00Z", "2026-12-03T10:00:00Z", "room-1", TOKEN_A)
        assert status in (200, 201)
        status, _ = _mk(base, "B", "2026-12-03T09:00:00Z", "2026-12-03T10:00:00Z", "room-2", TOKEN_B)
        assert status in (200, 201), "different rooms at the same time must not conflict"


def test_room_schedule_ordered_and_shaped():
    with running_app(_workspace()) as base:
        _mk(base, "Late", "2026-12-04T14:00:00Z", "2026-12-04T15:00:00Z", "room-9", TOKEN_A)
        _mk(base, "Early", "2026-12-04T09:00:00Z", "2026-12-04T10:00:00Z", "room-9", TOKEN_B)
        status, sched = http_call("GET", f"{base}/rooms/room-9/schedule", headers=_auth(TOKEN_A))
        assert status == 200
        items = sched if isinstance(sched, list) else sched.get("schedule", sched.get("bookings", []))
        titles = [b["title"] for b in items]
        assert titles == ["Early", "Late"], f"must be start_time-ordered, got {titles}"
        for b in items:
            for key in ("id", "title", "start_time", "end_time", "owner"):
                assert key in b, f"schedule entry missing {key}"


def test_schedule_requires_auth():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/rooms/room-1/schedule")
        assert status == 401
