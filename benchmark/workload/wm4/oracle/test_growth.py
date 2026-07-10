"""WM4 oracle — filtering, pagination, recurring. Never visible to the arm."""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

TOKEN_A = "test-token-alice"


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _mk(base, title, start, end, token=TOKEN_A):
    status, body = http_call(
        "POST", f"{base}/bookings",
        {"title": title, "start_time": start, "end_time": end}, _auth(token))
    assert status in (200, 201), (title, status, body)
    return body


def test_status_filter():
    with running_app(_workspace()) as base:
        _mk(base, "F1", "2026-09-01T09:00:00Z", "2026-09-01T10:00:00Z")
        status, listing = http_call("GET", f"{base}/bookings?status=pending", headers=_auth(TOKEN_A))
        assert status == 200
        items = listing if isinstance(listing, list) else listing.get("bookings", listing.get("items", []))
        assert all(b["status"] == "pending" for b in items)
        assert any(b["title"] == "F1" for b in items)


def test_time_window_filter():
    with running_app(_workspace()) as base:
        _mk(base, "InWindow", "2026-09-10T09:00:00Z", "2026-09-10T10:00:00Z")
        _mk(base, "OutWindow", "2026-11-20T09:00:00Z", "2026-11-20T10:00:00Z")
        status, listing = http_call(
            "GET", f"{base}/bookings?from=2026-09-01T00:00:00Z&to=2026-09-30T23:59:59Z",
            headers=_auth(TOKEN_A))
        assert status == 200
        items = listing if isinstance(listing, list) else listing.get("bookings", listing.get("items", []))
        titles = [b["title"] for b in items]
        assert "InWindow" in titles and "OutWindow" not in titles


def test_pagination_limit_offset():
    with running_app(_workspace()) as base:
        for i in range(4):
            _mk(base, f"P{i}", f"2026-09-0{i+1}T09:00:00Z", f"2026-09-0{i+1}T10:00:00Z")
        status, page = http_call("GET", f"{base}/bookings?limit=2&offset=1", headers=_auth(TOKEN_A))
        assert status == 200
        items = page if isinstance(page, list) else page.get("bookings", page.get("items", []))
        assert len(items) == 2
        assert items[0]["title"] == "P1"  # stable start_time order, offset applied


def test_invalid_pagination_rejected():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings?limit=-1", headers=_auth(TOKEN_A))
        assert status == 400


def test_recurring_creates_weekly_instances():
    with running_app(_workspace()) as base:
        status, body = http_call(
            "POST", f"{base}/bookings/recurring",
            {"title": "Standup", "start_time": "2026-09-07T09:00:00Z",
             "end_time": "2026-09-07T09:15:00Z", "repeats": 3}, _auth(TOKEN_A))
        assert status in (200, 201), body
        status, listing = http_call("GET", f"{base}/bookings?limit=50", headers=_auth(TOKEN_A))
        items = listing if isinstance(listing, list) else listing.get("bookings", listing.get("items", []))
        standups = sorted(b["start_time"] for b in items if b["title"] == "Standup")
        assert len(standups) == 3
        assert standups[1].startswith("2026-09-14") and standups[2].startswith("2026-09-21")


def test_recurring_all_or_nothing_on_conflict():
    with running_app(_workspace()) as base:
        # block the SECOND weekly slot
        _mk(base, "Blocker", "2026-10-12T09:00:00Z", "2026-10-12T09:30:00Z")
        status, _ = http_call(
            "POST", f"{base}/bookings/recurring",
            {"title": "Clash", "start_time": "2026-10-05T09:00:00Z",
             "end_time": "2026-10-05T09:15:00Z", "repeats": 3}, _auth(TOKEN_A))
        assert status == 409
        status, listing = http_call("GET", f"{base}/bookings?limit=50", headers=_auth(TOKEN_A))
        items = listing if isinstance(listing, list) else listing.get("bookings", listing.get("items", []))
        assert not any(b["title"] == "Clash" for b in items), "all-or-nothing violated"
