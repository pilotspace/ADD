"""WM5 must-survive invariants (long-horizon extension, 2026-07-18).

Re-run against WM6 workspaces. From WM5 on, `room_id` is required and
conflicts are per-room, so these probes send rooms directly — no fallback
needed. Auth-carrying (both pinned tokens: the same-room conflict is
CROSS-USER, the very thing that distinguishes the per-room rule from the
old per-owner one). Conflict windows genuinely overlap — never
boundary-touch — so WM6's half-open [start, end) semantics keep them
conflicting. Each probe owns its 2029 calendar day. Never visible to the
arm under test.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

TOKEN_A = "test-token-alice"
TOKEN_B = "test-token-bob"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _create(base: str, token: str, title: str, start: str, end: str, room: str):
    return http_call(
        "POST", f"{base}/bookings",
        {"title": title, "start_time": start, "end_time": end, "room_id": room},
        headers=_auth(token),
    )


def test_room_id_required():
    with running_app(_workspace()) as base:
        status, _ = http_call(
            "POST", f"{base}/bookings",
            {"title": "sv5-noroom", "start_time": "2029-01-08T10:00:00Z",
             "end_time": "2029-01-08T11:00:00Z"},
            headers=_auth(TOKEN_A),
        )
        assert status == 400


def test_same_room_conflicts_across_users():
    with running_app(_workspace()) as base:
        status, first = _create(
            base, TOKEN_A, "sv5-conf-a",
            "2029-02-06T10:00:00Z", "2029-02-06T11:00:00Z", "sv5-conf-room",
        )
        assert status in (200, 201), first
        status, second = _create(
            base, TOKEN_B, "sv5-conf-b",
            "2029-02-06T10:30:00Z", "2029-02-06T11:30:00Z", "sv5-conf-room",
        )
        assert status == 409, second


def test_different_rooms_never_conflict():
    with running_app(_workspace()) as base:
        status, first = _create(
            base, TOKEN_A, "sv5-free-a",
            "2029-02-08T10:00:00Z", "2029-02-08T11:00:00Z", "sv5-room-x",
        )
        assert status in (200, 201), first
        status, second = _create(
            base, TOKEN_B, "sv5-free-b",
            "2029-02-08T10:00:00Z", "2029-02-08T11:00:00Z", "sv5-room-y",
        )
        assert status in (200, 201), second


def test_room_schedule_readable_by_any_caller():
    with running_app(_workspace()) as base:
        status, early = _create(
            base, TOKEN_A, "sv5-sched-early",
            "2029-03-05T09:00:00Z", "2029-03-05T10:00:00Z", "sv5-sched-room",
        )
        assert status in (200, 201), early
        status, late = _create(
            base, TOKEN_A, "sv5-sched-late",
            "2029-03-05T11:00:00Z", "2029-03-05T12:00:00Z", "sv5-sched-room",
        )
        assert status in (200, 201), late
        status, body = http_call(
            "GET", f"{base}/rooms/sv5-sched-room/schedule", headers=_auth(TOKEN_B)
        )
        assert status == 200
        assert isinstance(body, list)
        by_id = {item.get("id"): item for item in body}
        assert early["id"] in by_id and late["id"] in by_id
        for entry in (by_id[early["id"]], by_id[late["id"]]):
            for field in ("id", "title", "start_time", "end_time", "owner"):
                assert field in entry, f"schedule entries must carry {field}"
        positions = [item.get("id") for item in body]
        assert positions.index(early["id"]) < positions.index(late["id"]), \
            "schedule must be ordered by start_time"
