"""HV3 must-survive invariants (v2-wv2-hostile-change §3 @ v1, M4).

Re-run against any LATER hv-track workspace. Auth-carrying and pinned to the
post-hostile contract: the premium bypass AND the scoped non-premium 409 are
both invariants from here on. Payload shape = the hv track's own contract
(duration_minutes, from the wm2-copied base — meter defect #6: the first
probes wrongly assumed a shape migration the track never asked for).
No shape fallback exists (meter defect #5 rule).
Disjoint far-future windows (2027-05/2027-06 days) per probe.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

TOKEN_A = "test-token-alice"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def test_premium_bypass_survives():
    with running_app(_workspace()) as base:
        status, first = http_call(
            "POST", f"{base}/bookings",
            {"title": "base", "start_time": "2027-05-03T09:00:00Z", "duration_minutes": 60},
            headers=_auth(TOKEN_A),
        )
        assert status in (200, 201), first
        status, premium = http_call(
            "POST", f"{base}/bookings",
            {"title": "vip", "start_time": "2027-05-03T09:30:00Z", "duration_minutes": 60, "tier": "premium"},
            headers=_auth(TOKEN_A),
        )
        assert status in (200, 201), premium


def test_scoped_conflict_survives():
    with running_app(_workspace()) as base:
        status, first = http_call(
            "POST", f"{base}/bookings",
            {"title": "base", "start_time": "2027-06-07T09:00:00Z", "duration_minutes": 60},
            headers=_auth(TOKEN_A),
        )
        assert status in (200, 201), first
        status, second = http_call(
            "POST", f"{base}/bookings",
            {"title": "clash", "start_time": "2027-06-07T09:30:00Z", "duration_minutes": 60},
            headers=_auth(TOKEN_A),
        )
        assert status == 409, second
