"""WM1 oracle — task/booking core CRUD. Never visible to the arm under test.

Scores against $BENCH_WORKSPACE (an arm's built app). Must collect and fail
against an empty workspace (red for the right reason).
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app, records


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def test_create_and_fetch_booking():
    with running_app(_workspace()) as base:
        status, body = http_call(
            "POST",
            f"{base}/bookings",
            {"title": "Standup", "start_time": "2026-08-01T09:00:00Z", "duration_minutes": 30},
        )
        assert status in (200, 201), body
        assert body and "id" in body
        booking_id = body["id"]

        status, fetched = http_call("GET", f"{base}/bookings/{booking_id}")
        assert status == 200, fetched
        assert fetched["title"] == "Standup"
        assert fetched["status"] == "pending"


def test_list_bookings():
    with running_app(_workspace()) as base:
        http_call(
            "POST",
            f"{base}/bookings",
            {"title": "A", "start_time": "2026-08-01T09:00:00Z", "duration_minutes": 15},
        )
        status, body = http_call("GET", f"{base}/bookings")
        assert status == 200, body
        assert records(body) is not None and len(records(body)) >= 1


def test_update_and_delete_booking():
    with running_app(_workspace()) as base:
        _, created = http_call(
            "POST",
            f"{base}/bookings",
            {"title": "B", "start_time": "2026-08-01T10:00:00Z", "duration_minutes": 15},
        )
        booking_id = created["id"]

        status, updated = http_call("PATCH", f"{base}/bookings/{booking_id}", {"status": "confirmed"})
        assert status == 200, updated
        assert updated["status"] == "confirmed"

        status, _ = http_call("DELETE", f"{base}/bookings/{booking_id}")
        assert status in (200, 204), status

        status, _ = http_call("GET", f"{base}/bookings/{booking_id}")
        assert status == 404


def test_missing_required_field_rejected():
    with running_app(_workspace()) as base:
        status, _ = http_call("POST", f"{base}/bookings", {"title": "no start time"})
        assert status == 400


def test_unknown_booking_is_404():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings/does-not-exist")
        assert status == 404
