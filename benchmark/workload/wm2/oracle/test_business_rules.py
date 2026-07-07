"""WM2 oracle — business rules + auth. Never visible to the arm under test."""
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


def test_unauthenticated_request_rejected():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings")
        assert status == 401


def test_no_double_booking_for_same_owner():
    with running_app(_workspace()) as base:
        payload = {"title": "First", "start_time": "2026-08-01T09:00:00Z", "duration_minutes": 60}
        status, first = http_call("POST", f"{base}/bookings", payload, _auth(TOKEN_A))
        assert status in (200, 201), first

        overlap = {"title": "Overlap", "start_time": "2026-08-01T09:30:00Z", "duration_minutes": 30}
        status, body = http_call("POST", f"{base}/bookings", overlap, _auth(TOKEN_A))
        assert status == 409, body
        assert body and body.get("conflict_booking_id") == first["id"]


def test_ownership_forbids_cross_user_edit():
    with running_app(_workspace()) as base:
        payload = {"title": "Owned", "start_time": "2026-08-02T09:00:00Z", "duration_minutes": 30}
        _, created = http_call("POST", f"{base}/bookings", payload, _auth(TOKEN_A))
        status, _ = http_call(
            "PATCH", f"{base}/bookings/{created['id']}", {"status": "confirmed"}, _auth(TOKEN_B)
        )
        assert status == 403


def test_cancellation_window_enforced():
    with running_app(_workspace()) as base:
        # start_time in the past / within the hour -> cancellation must be rejected.
        payload = {"title": "Soon", "start_time": "2026-01-01T00:00:00Z", "duration_minutes": 30}
        _, created = http_call("POST", f"{base}/bookings", payload, _auth(TOKEN_A))
        status, _ = http_call(
            "PATCH", f"{base}/bookings/{created['id']}", {"status": "cancelled"}, _auth(TOKEN_A)
        )
        assert status == 422


def test_list_scoped_to_caller():
    with running_app(_workspace()) as base:
        http_call(
            "POST",
            f"{base}/bookings",
            {"title": "Alice's", "start_time": "2026-08-03T09:00:00Z", "duration_minutes": 30},
            _auth(TOKEN_A),
        )
        status, body = http_call("GET", f"{base}/bookings", headers=_auth(TOKEN_B))
        assert status == 200
        assert all(b.get("owner_id") != "alice" for b in (body or []))
