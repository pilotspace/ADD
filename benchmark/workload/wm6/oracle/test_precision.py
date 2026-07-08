"""WM6 oracle — precision scheduling semantics. Never visible to the arm.

Every probe targets a failure mode that survives casual review: string
datetime comparison, closed-interval overlap, missing idempotency state,
unhandled parse errors.
"""
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


def _mk(base, title, start, end, room="room-p", token=TOKEN_A, extra=None, headers=None):
    payload = {"title": title, "start_time": start, "end_time": end, "room_id": room}
    if extra:
        payload.update(extra)
    h = dict(_auth(token))
    if headers:
        h.update(headers)
    return http_call("POST", f"{base}/bookings", payload, h)


# --- 1 · timezone-correct overlap ------------------------------------------------

def test_same_instant_different_offset_conflicts():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "UTC", "2026-12-10T08:00:00Z", "2026-12-10T09:00:00Z", "room-tz")
        assert status in (200, 201)
        # 10:00+02:00 == 08:00Z — the SAME instant, must conflict
        status, _ = _mk(base, "Offset", "2026-12-10T10:00:00+02:00", "2026-12-10T11:00:00+02:00", "room-tz", TOKEN_B)
        assert status == 409, "same absolute instant in a different offset must conflict"


def test_different_instant_same_wallclock_no_conflict():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "UTC", "2026-12-11T08:00:00Z", "2026-12-11T09:00:00Z", "room-tz2")
        assert status in (200, 201)
        # 08:00+07:00 is 01:00Z — same wall-clock string prefix, DIFFERENT instant
        status, _ = _mk(base, "Bangkok", "2026-12-11T08:00:00+07:00", "2026-12-11T09:00:00+07:00", "room-tz2", TOKEN_B)
        assert status in (200, 201), "same wall-clock in a different offset is a different instant"


def test_offset_aware_cancellation_window():
    with running_app(_workspace()) as base:
        # window rule must not crash or misjudge on offset-carrying times
        status, body = _mk(base, "WinProbe", "2027-06-01T10:00:00+05:30", "2027-06-01T11:00:00+05:30", "room-win")
        assert status in (200, 201), body


# --- 2 · boundary exactness (half-open intervals) --------------------------------

def test_touching_intervals_do_not_conflict():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "First", "2026-12-12T09:00:00Z", "2026-12-12T10:00:00Z", "room-adj")
        assert status in (200, 201)
        # adjacent booking starts exactly when the first ends — touching, no overlap
        status, _ = _mk(base, "Second", "2026-12-12T10:00:00Z", "2026-12-12T11:00:00Z", "room-adj", TOKEN_B)
        assert status in (200, 201), "touching [start,end) intervals must not conflict"


def test_zero_length_booking_rejected():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "Zero", "2026-12-13T09:00:00Z", "2026-12-13T09:00:00Z", "room-z")
        assert status == 400


# --- 3 · idempotent create --------------------------------------------------------

def test_idempotency_key_replay_returns_same_booking():
    with running_app(_workspace()) as base:
        h = {"Idempotency-Key": "idem-1"}
        s1, b1 = _mk(base, "Idem", "2026-12-14T09:00:00Z", "2026-12-14T10:00:00Z", "room-i", headers=h)
        assert s1 in (200, 201), b1
        s2, b2 = _mk(base, "Idem", "2026-12-14T09:00:00Z", "2026-12-14T10:00:00Z", "room-i", headers=h)
        assert s2 in (200, 201), "replay must succeed, not conflict"
        assert b2["id"] == b1["id"], "replay must return the ORIGINAL booking"
        status, listing = http_call("GET", f"{base}/bookings?limit=50", headers=_auth(TOKEN_A))
        items = listing if isinstance(listing, list) else listing.get("bookings", listing.get("items", []))
        assert sum(1 for b in items if b["title"] == "Idem") == 1, "no duplicate created"


def test_idempotency_key_different_payload_conflicts():
    with running_app(_workspace()) as base:
        h = {"Idempotency-Key": "idem-2"}
        s1, _ = _mk(base, "IdemA", "2026-12-15T09:00:00Z", "2026-12-15T10:00:00Z", "room-i2", headers=h)
        assert s1 in (200, 201)
        s2, _ = _mk(base, "IdemB", "2026-12-15T11:00:00Z", "2026-12-15T12:00:00Z", "room-i2", headers=h)
        assert s2 == 409, "same key + different payload must be 409"


# --- 4 · input hardening ----------------------------------------------------------

def test_malformed_datetime_is_400_not_500():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "Bad", "not-a-datetime", "2026-12-16T10:00:00Z", "room-h")
        assert status == 400, "malformed datetime must be a clean 400, never a 500"


def test_end_before_start_rejected():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "Backwards", "2026-12-17T10:00:00Z", "2026-12-17T09:00:00Z", "room-h")
        assert status == 400


def test_unknown_status_value_rejected():
    with running_app(_workspace()) as base:
        status, _ = _mk(base, "BadStatus", "2026-12-18T09:00:00Z", "2026-12-18T10:00:00Z", "room-h",
                        extra={"status": "definitely-not-a-status"})
        assert status == 400


def test_non_integer_pagination_is_400():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings?limit=abc", headers=_auth(TOKEN_A))
        assert status == 400


# --- carry-over: earlier behavior still works under the new semantics -------------

def test_carryover_room_scoping_still_holds():
    with running_app(_workspace()) as base:
        s1, _ = _mk(base, "RoomA", "2026-12-19T09:00:00Z", "2026-12-19T10:00:00Z", "room-x")
        assert s1 in (200, 201)
        s2, _ = _mk(base, "RoomB", "2026-12-19T09:00:00Z", "2026-12-19T10:00:00Z", "room-y", TOKEN_B)
        assert s2 in (200, 201), "different rooms still never conflict"
