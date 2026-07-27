"""WM4 must-survive invariants (long-horizon extension, 2026-07-18).

Re-run against WM5+/WM6 workspaces. Auth-carrying and room-adaptive (same
400-only fallback discipline as wm3 — meter defect #5). Membership asserts,
never counts: survivors share the persistent store with each other, so a
probe may only assert about bookings IT created (except the pagination cap,
which is a <= bound by construction). The recurring atomicity probe hands
the blocker and the run the SAME room so the collision holds per-owner
(WM4) and per-room (WM5+); its windows coincide exactly, which still
overlaps under WM6's half-open [start, end). Each probe owns its 2028
calendar days. Never visible to the arm under test.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app, records

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


def _recurring(base: str, token: str, body: dict, room: str):
    """Room-adaptive recurring create with the same 400-only fallback."""
    status, resp = http_call(
        "POST", f"{base}/bookings/recurring", dict(body),
        headers={"Authorization": f"Bearer {token}"},
    )
    if status != 400:
        return status, resp
    with_room = dict(body)
    with_room["room_id"] = room
    return http_call(
        "POST", f"{base}/bookings/recurring", with_room,
        headers={"Authorization": f"Bearer {token}"},
    )


def test_window_filter_scopes_listing():
    with running_app(_workspace()) as base:
        status, in_window = _create(
            base, "test-token-alice", "sv4-filter-in",
            "2028-09-04T10:00:00Z", "2028-09-04T11:00:00Z", "sv4-f-room-a",
        )
        assert status in (200, 201), in_window
        status, out_window = _create(
            base, "test-token-alice", "sv4-filter-out",
            "2028-09-06T10:00:00Z", "2028-09-06T11:00:00Z", "sv4-f-room-b",
        )
        assert status in (200, 201), out_window
        status, body = http_call(
            "GET",
            f"{base}/bookings?from=2028-09-04T00:00:00Z&to=2028-09-05T00:00:00Z",
            headers=_AUTH,
        )
        assert status == 200
        assert records(body) is not None
        ids = {item.get("id") for item in body}
        assert in_window["id"] in ids, "the in-window booking must be returned"
        assert out_window["id"] not in ids, "the out-of-window booking must be filtered out"


def test_pagination_caps_and_rejects_invalid():
    with running_app(_workspace()) as base:
        for hour in ("09", "10", "11"):
            status, made = _create(
                base, "test-token-alice", f"sv4-page-{hour}",
                f"2028-10-10T{hour}:00:00Z", f"2028-10-10T{hour}:30:00Z", "sv4-page-room",
            )
            assert status in (200, 201), made
        status, body = http_call("GET", f"{base}/bookings?limit=2", headers=_AUTH)
        assert status == 200
        assert records(body) is not None
        assert len(body) == 2, f"limit=2 must cap the listing, got {len(body)}"
        status, _ = http_call("GET", f"{base}/bookings?limit=-1", headers=_AUTH)
        assert status == 400


def test_recurring_is_all_or_nothing():
    with running_app(_workspace()) as base:
        # blocker sits exactly on the would-be third weekly instance
        status, blocker = _create(
            base, "test-token-alice", "sv4-rec-blocker",
            "2028-11-21T09:00:00Z", "2028-11-21T10:00:00Z", "sv4-rec-room",
        )
        assert status in (200, 201), blocker
        status, resp = _recurring(
            base, "test-token-alice",
            {"title": "sv4-rec-run", "start_time": "2028-11-07T09:00:00Z",
             "end_time": "2028-11-07T10:00:00Z", "repeats": 3},
            "sv4-rec-room",
        )
        assert status == 409, resp
        status, body = http_call(
            "GET",
            f"{base}/bookings?from=2028-11-07T00:00:00Z&to=2028-11-08T00:00:00Z",
            headers=_AUTH,
        )
        assert status == 200
        titles = {item.get("title") for item in body}
        assert "sv4-rec-run" not in titles, "a rejected recurring run must create NO instances"
