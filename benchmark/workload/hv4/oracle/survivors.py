"""HV4 must-survive invariants — the resilient-settlement LAWS (re-run only if a
later hv milestone is ever added). KEY-CARRYING, few calls, LAW-TOLERANT: a
healthy payout settles idempotently, and a payout never double-pays. Never
visible to the arm.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

_K = {"X-API-Key": "bench-key-alice"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _transfer(base, amount=50):
    _s, src = http_call("POST", f"{base}/accounts", {"name": "src"}, headers=_K)
    http_call("POST", f"{base}/accounts/{src['id']}/credit", {"amount_cents": amount + 50}, headers=_K)
    _s, p = http_call("POST", f"{base}/accounts", {"name": "p"}, headers=_K)
    s, b = http_call("POST", f"{base}/transfers",
                     {"source_id": src["id"], "amount_cents": amount, "payees": [{"account_id": p["id"], "weight": 1}]}, headers=_K)
    assert s in (200, 201), b
    return b["id"]


def test_healthy_payout_settles_and_applies_once():
    with running_app(_workspace()) as base:
        http_call("PUT", f"{base}/admin/payout-backend", {"fail_next": 0, "mode": "error"}, headers=_K)
        s, b = http_call("POST", f"{base}/payouts", {"transfer_id": _transfer(base)}, headers=_K)
        assert s in (200, 201), b
        assert b["status"] == "settled" and b["provider_applied"] == 1


def test_exhausted_payout_does_not_apply():
    with running_app(_workspace()) as base:
        http_call("PUT", f"{base}/admin/payout-backend", {"fail_next": 99, "mode": "error"}, headers=_K)
        _s, b = http_call("POST", f"{base}/payouts", {"transfer_id": _transfer(base)}, headers=_K)
        assert b["status"] == "failed" and b["provider_applied"] == 0
