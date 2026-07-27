"""WM1 must-survive invariants (v2-wv1-longitudinal §3 @ v3, M7).

Regression probes re-run against EVERY LATER WM's workspace — so each probe
must hold under legitimate later evolution (WM2 adds mandatory auth; WM3
replaces duration_minutes with end_time). Two rules keep them survivable:

1. AUTH-CARRYING: every call sends the pinned token (`test-token-alice`,
   pinned in wm2's PROMPT). A WM1 app ignores the header; a WM2+ app
   requires it. Never assert unauthenticated success.
2. SHAPE-TOLERANT: no probe sends or reads `duration_minutes`/`end_time` —
   only invariants that survive the WM3 shape break (404 for unknown ids,
   400 for a missing required field, list-shaped listings).

Wholesale re-runs of the full WM1 suite scored a CORRECT WM2 auth
implementation regression=1.0 (rep0, 2026-07-10) — these survivors are the
fix. Never visible to the arm under test.
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


def test_unknown_booking_is_404():
    with running_app(_workspace()) as base:
        status, _ = http_call("GET", f"{base}/bookings/does-not-exist", headers=_AUTH)
        assert status == 404


def test_missing_required_field_rejected():
    # title-only payload carries NO time shape — invalid in every WM's schema
    with running_app(_workspace()) as base:
        status, _ = http_call("POST", f"{base}/bookings", {"title": "no start time"}, headers=_AUTH)
        assert status == 400


def test_listing_is_a_json_array():
    with running_app(_workspace()) as base:
        status, body = http_call("GET", f"{base}/bookings", headers=_AUTH)
        assert status == 200
        assert records(body) is not None
