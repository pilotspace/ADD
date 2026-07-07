"""Regression-marker split (bench-regression-split fast task): `-m regression`
selects ONLY the 3 shape-independent must-survive tests; the 7 re-exports
doomed by WM3's own duration_minutes->end_time contract carry `legacy_shape`."""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REFRACTOR = REPO_ROOT / "benchmark" / "workload" / "wm3" / "oracle" / "test_refactor.py"

MUST_SURVIVE = {
    "test_regression_wm1_missing_required_field_rejected",
    "test_regression_wm1_unknown_booking_is_404",
    "test_regression_wm2_unauthenticated_request_rejected",
}
LEGACY = {
    "test_regression_wm1_create_and_fetch_booking",
    "test_regression_wm1_list_bookings",
    "test_regression_wm1_update_and_delete_booking",
    "test_regression_wm2_no_double_booking_for_same_owner",
    "test_regression_wm2_ownership_forbids_cross_user_edit",
    "test_regression_wm2_cancellation_window_enforced",
    "test_regression_wm2_list_scoped_to_caller",
}


def _collected(marker: str) -> set[str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-m", marker, "-p", "no:cacheprovider",
         "--collect-only", "-q", str(REFRACTOR)],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
    )
    names = set()
    for line in proc.stdout.splitlines():
        m = re.match(r".*::(test_\w+)", line.strip())
        if m:
            names.add(m.group(1))
    return names


def test_must_survive_census():
    assert _collected("regression") == MUST_SURVIVE


def test_legacy_shape_census():
    assert _collected("legacy_shape") == LEGACY


def test_no_double_markers():
    both = _collected("regression and legacy_shape")
    assert both == set(), f"tests carrying both markers: {both}"
