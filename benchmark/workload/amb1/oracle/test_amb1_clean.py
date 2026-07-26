"""AMB1 oracle — the CLEAN SUBSET only. Never visible to the arm under test.

Mirrors checklist.py's contamination map: every behaviour asserted here is stated
unambiguously by amb1/PROMPT.md and holds under BOTH readings of all three
planted ambiguities. Nothing about waitlist membership, promotion order, or
position appears — asserting any of those would grade an arm on which reading it
picked, which is precisely what the ambiguity track measures separately and must
never fold into a pass/fail meter.

Scores against $BENCH_WORKSPACE (an arm's built app). Must collect and fail
against an empty workspace (red for the right reason).
"""
import os
from datetime import datetime, timedelta, timezone

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

_ALICE = {"Authorization": "Bearer test-token-alice"}
_BOB = {"Authorization": "Bearer test-token-bob"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _iso(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _body(**over) -> dict:
    body = {"title": "Standup", "start_time": _iso(72), "end_time": _iso(73),
            "room_id": "oracle-default"}
    body.update(over)
    return body


def test_create_and_fetch_booking():
    with running_app(_workspace()) as base:
        status, body = http_call("POST", f"{base}/bookings",
                                 _body(room_id="o-create"), headers=_ALICE)
        assert status in (200, 201), body
        assert body and "id" in body
        bid = body["id"]
        assert body.get("status") == "pending", body

        status, fetched = http_call("GET", f"{base}/bookings/{bid}", None, headers=_ALICE)
        assert status == 200, fetched
        assert fetched["id"] == bid


def test_list_returns_an_array():
    with running_app(_workspace()) as base:
        status, body = http_call("GET", f"{base}/bookings", None, headers=_ALICE)
        assert status == 200, body
        assert isinstance(body, list), body


def test_unknown_id_is_404():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings/nope", None, headers=_ALICE)
        assert status == 404


def test_missing_required_field_is_400():
    with running_app(_workspace()) as base:
        status, _ = http_call("POST", f"{base}/bookings", {"title": "no times"},
                              headers=_ALICE)
        assert status == 400


def test_optional_priority_is_accepted():
    # The FIELD is accepted. What priority MEANS for promotion order is ambiguous
    # (A-priority-vs-fifo) and is deliberately not asserted anywhere.
    with running_app(_workspace()) as base:
        status, body = http_call("POST", f"{base}/bookings",
                                 _body(room_id="o-priority", priority=5), headers=_ALICE)
        assert status in (200, 201), body
        assert body and "id" in body


def test_distinct_callers_get_distinct_bookings():
    with running_app(_workspace()) as base:
        _, a = http_call("POST", f"{base}/bookings", _body(room_id="o-auth-a"),
                         headers=_ALICE)
        _, b = http_call("POST", f"{base}/bookings", _body(room_id="o-auth-b"),
                         headers=_BOB)
        assert a and b and a["id"] != b["id"]


def test_cancel_outside_the_window_succeeds():
    with running_app(_workspace()) as base:
        _, created = http_call("POST", f"{base}/bookings", _body(room_id="o-delete"),
                               headers=_ALICE)
        assert created and "id" in created
        status, _ = http_call("DELETE", f"{base}/bookings/{created['id']}", None,
                              headers=_ALICE)
        assert status in (200, 204)


def test_cancel_inside_the_window_is_422():
    # §3, stated outright and untouched by any planted ambiguity.
    with running_app(_workspace()) as base:
        _, created = http_call("POST", f"{base}/bookings",
                               _body(room_id="o-window", start_time=_iso(2),
                                     end_time=_iso(3)), headers=_ALICE)
        assert created and "id" in created
        status, _ = http_call("DELETE", f"{base}/bookings/{created['id']}", None,
                              headers=_ALICE)
        assert status == 422
