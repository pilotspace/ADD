"""WM3 oracle — breaking-change refactor (regression bait).

New assertions for the `end_time` shape, PLUS the wm1+wm2 oracle suites
re-exported below (regression_rate is computed from these re-run tests).
"""
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


def test_duration_minutes_rejected():
    with running_app(_workspace()) as base:
        payload = {"title": "Old shape", "start_time": "2026-08-01T09:00:00Z", "duration_minutes": 30}
        status, _ = http_call("POST", f"{base}/bookings", payload, _auth(TOKEN_A))
        assert status == 400


def test_end_time_shape_accepted_and_returned():
    with running_app(_workspace()) as base:
        payload = {"title": "New shape", "start_time": "2026-08-01T09:00:00Z", "end_time": "2026-08-01T09:30:00Z"}
        status, body = http_call("POST", f"{base}/bookings", payload, _auth(TOKEN_A))
        assert status in (200, 201), body
        assert "end_time" in body
        assert "duration_minutes" not in body


# --- regression_rate re-exports -------------------------------------------------
# WM3's oracle re-runs the WM1 + WM2 oracle suites against the WM3 workspace;
# any of these breaking is what `regression_rate` measures.

from benchmark.workload.wm1.oracle.test_bookings import (  # noqa: E402  (regression re-export)
    test_create_and_fetch_booking as test_regression_wm1_create_and_fetch_booking,
    test_list_bookings as test_regression_wm1_list_bookings,
    test_update_and_delete_booking as test_regression_wm1_update_and_delete_booking,
    test_missing_required_field_rejected as test_regression_wm1_missing_required_field_rejected,
    test_unknown_booking_is_404 as test_regression_wm1_unknown_booking_is_404,
)
from benchmark.workload.wm2.oracle.test_business_rules import (  # noqa: E402  (regression re-export)
    test_unauthenticated_request_rejected as test_regression_wm2_unauthenticated_request_rejected,
    test_no_double_booking_for_same_owner as test_regression_wm2_no_double_booking_for_same_owner,
    test_ownership_forbids_cross_user_edit as test_regression_wm2_ownership_forbids_cross_user_edit,
    test_cancellation_window_enforced as test_regression_wm2_cancellation_window_enforced,
    test_list_scoped_to_caller as test_regression_wm2_list_scoped_to_caller,
)

# pytest needs the *_test_* names to remain callable functions with the `test_` prefix
# (already true from the import-as above) — tag each with the `regression` marker so
# regression_rate scoring can select exactly this re-exported set.
test_regression_wm1_create_and_fetch_booking = pytest.mark.regression(test_regression_wm1_create_and_fetch_booking)
test_regression_wm1_list_bookings = pytest.mark.regression(test_regression_wm1_list_bookings)
test_regression_wm1_update_and_delete_booking = pytest.mark.regression(test_regression_wm1_update_and_delete_booking)
test_regression_wm1_missing_required_field_rejected = pytest.mark.regression(
    test_regression_wm1_missing_required_field_rejected
)
test_regression_wm1_unknown_booking_is_404 = pytest.mark.regression(test_regression_wm1_unknown_booking_is_404)
test_regression_wm2_unauthenticated_request_rejected = pytest.mark.regression(
    test_regression_wm2_unauthenticated_request_rejected
)
test_regression_wm2_no_double_booking_for_same_owner = pytest.mark.regression(
    test_regression_wm2_no_double_booking_for_same_owner
)
test_regression_wm2_ownership_forbids_cross_user_edit = pytest.mark.regression(
    test_regression_wm2_ownership_forbids_cross_user_edit
)
test_regression_wm2_cancellation_window_enforced = pytest.mark.regression(
    test_regression_wm2_cancellation_window_enforced
)
test_regression_wm2_list_scoped_to_caller = pytest.mark.regression(test_regression_wm2_list_scoped_to_caller)
