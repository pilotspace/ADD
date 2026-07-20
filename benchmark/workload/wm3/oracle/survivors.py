"""WM3 must-survive invariants (long-horizon extension, 2026-07-18).

Re-run against every LATER WM's workspace (WM4+). Auth-carrying (pinned
token from wm2's PROMPT) and ROOM-ADAPTIVE: WM5 makes `room_id` required
and re-scopes overlap per-room, so `_create` sends the plain end_time
payload first and adds `room_id` ONLY on a 400 shape rejection — business
statuses (401/403/409) pass through untouched (meter defect #5). The
overlap probe hands BOTH creates the SAME room so the conflict expectation
holds under the per-owner era (WM3/WM4, same owner) AND the per-room era
(WM5+). Windows genuinely overlap — never boundary-touch — so WM6's
half-open [start, end) semantics keep them conflicting. Each probe books
its OWN 2028 calendar day (probe-state pollution, twice proven). Never
visible to the arm under test.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

_AUTH = {"Authorization": "Bearer test-token-alice"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _create(base: str, token: str, title: str, start: str, end: str, room: str):
    """Room-adaptive end_time create: plain payload first; on a 400 shape
    rejection ONLY, retry with the caller's room_id added."""
    payload = {"title": title, "start_time": start, "end_time": end}
    status, body = http_call(
        "POST", f"{base}/bookings", dict(payload),
        headers={"Authorization": f"Bearer {token}"},
    )
    if status != 400:
        return status, body
    payload["room_id"] = room
    return http_call(
        "POST", f"{base}/bookings", payload,
        headers={"Authorization": f"Bearer {token}"},
    )


def test_end_time_create_and_echo():
    with running_app(_workspace()) as base:
        status, created = _create(
            base, "test-token-alice", "sv3-echo",
            "2028-06-05T10:00:00Z", "2028-06-05T11:00:00Z", "sv3-echo-room",
        )
        assert status in (200, 201), created
        status, body = http_call("GET", f"{base}/bookings/{created['id']}", headers=_AUTH)
        assert status == 200
        assert "end_time" in body


def test_duration_minutes_rejected():
    # the WM3 shape break must hold forever: a duration_minutes payload is 400
    # in every later era (WM5 also lacks room_id — still 400; WM6 hardening: 400)
    with running_app(_workspace()) as base:
        status, _ = http_call(
            "POST", f"{base}/bookings",
            {"title": "sv3-dur", "start_time": "2028-06-14T10:00:00Z", "duration_minutes": 30},
            headers=_AUTH,
        )
        assert status == 400


def test_overlap_conflicts_under_end_time_shape():
    with running_app(_workspace()) as base:
        status, first = _create(
            base, "test-token-alice", "sv3-ov-a",
            "2028-07-12T10:00:00Z", "2028-07-12T11:00:00Z", "sv3-ov-room",
        )
        assert status in (200, 201), first
        status, second = _create(
            base, "test-token-alice", "sv3-ov-b",
            "2028-07-12T10:30:00Z", "2028-07-12T11:30:00Z", "sv3-ov-room",
        )
        assert status == 409, second
