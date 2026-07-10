"""WM2 must-survive invariants (v2-wv1-longitudinal §3 @ v3, M7).

Re-run against every LATER WM's workspace (WM3+). Auth-carrying (pinned
tokens from wm2's PROMPT) and shape-tolerant: `_create` adapts to whichever
time shape the app under test speaks (WM2 = duration_minutes, WM3+ =
end_time), so only the BEHAVIORAL invariants — auth floor, ownership,
overlap conflict, tenant scoping — are what can fail. Never visible to the
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


def _create(base: str, token: str, title: str, start: str, end: str, minutes: int):
    """Shape-adaptive create: try the WM3+ end_time shape; fall back to the
    WM2 duration_minutes shape ONLY on a 400 shape rejection. Any other
    status — including business-rule answers like 401/403/409 — is returned
    untouched (meter defect #5: falling back on a correct 409 turned it into
    the fallback's 400 and scored a false regression on every arm)."""
    status, body = http_call(
        "POST", f"{base}/bookings",
        {"title": title, "start_time": start, "end_time": end},
        headers=_auth(token),
    )
    if status != 400:
        return status, body
    return http_call(
        "POST", f"{base}/bookings",
        {"title": title, "start_time": start, "duration_minutes": minutes},
        headers=_auth(token),
    )


def test_unauthenticated_request_rejected():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings")
        assert status == 401


def test_ownership_forbids_cross_user_edit():
    with running_app(_workspace()) as base:
        status, created = _create(
            base, TOKEN_A, "alice-mtg", "2026-08-01T09:00:00Z", "2026-08-01T09:30:00Z", 30
        )
        assert status in (200, 201), created
        booking_id = created["id"]
        status, _ = http_call(
            "PATCH", f"{base}/bookings/{booking_id}", {"title": "hijack"}, headers=_auth(TOKEN_B)
        )
        assert status == 403


def test_same_owner_overlap_conflicts():
    with running_app(_workspace()) as base:
        status, first = _create(
            base, TOKEN_A, "first", "2026-08-02T10:00:00Z", "2026-08-02T11:00:00Z", 60
        )
        assert status in (200, 201), first
        status, second = _create(
            base, TOKEN_A, "overlap", "2026-08-02T10:30:00Z", "2026-08-02T11:30:00Z", 60
        )
        assert status == 409, second


def test_listing_scoped_to_caller():
    with running_app(_workspace()) as base:
        status, created = _create(
            base, TOKEN_A, "alice-only", "2026-08-03T09:00:00Z", "2026-08-03T09:30:00Z", 30
        )
        assert status in (200, 201), created
        alice_id = created["id"]
        status, bob_list = http_call("GET", f"{base}/bookings", headers=_auth(TOKEN_B))
        assert status == 200
        assert all(item.get("id") != alice_id for item in bob_list)
