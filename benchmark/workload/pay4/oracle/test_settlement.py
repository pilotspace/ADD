"""PAY4 oracle — resilient outbound settlement + input hardening. Not arm-visible.

Black-box, deterministic against the pinned wrapper contract (200 ms timeout, 3
attempts, 3-failure circuit threshold, 1 s cooldown). Each test gets its own app
boot, so the circuit breaker starts closed. The discriminating checks are
retry-then-settle, idempotent (never double-pay), the breaker opening WITHOUT
calling the provider, half-open recovery, bounded timeout, and 400-not-500. Red
on an empty workspace.
"""
import os
import time

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

_K = {"X-API-Key": "bench-key-alice"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _set_backend(base, fail_next, mode="error"):
    http_call("PUT", f"{base}/admin/payout-backend", {"fail_next": fail_next, "mode": mode}, headers=_K)


def _backend(base):
    _s, b = http_call("GET", f"{base}/admin/payout-backend")
    return b if isinstance(b, dict) else {}


def _transfer(base, amount=50):
    s, src = http_call("POST", f"{base}/accounts", {"name": "src"}, headers=_K)
    src = src["id"]
    http_call("POST", f"{base}/accounts/{src}/credit", {"amount_cents": amount + 50}, headers=_K)
    _s, p = http_call("POST", f"{base}/accounts", {"name": "p"}, headers=_K)
    s, b = http_call("POST", f"{base}/transfers",
                     {"source_id": src, "amount_cents": amount, "payees": [{"account_id": p["id"], "weight": 1}]}, headers=_K)
    assert s in (200, 201), b
    return b["id"]


def _payout(base, tid):
    return http_call("POST", f"{base}/payouts", {"transfer_id": tid}, headers=_K)


def test_healthy_payout_settles():
    with running_app(_workspace()) as base:
        _set_backend(base, 0)
        s, b = _payout(base, _transfer(base))
        assert s in (200, 201), b
        assert b["status"] == "settled" and b["attempts"] == 1 and b["provider_applied"] == 1


def test_transient_failures_retry_then_settle():
    with running_app(_workspace()) as base:
        _set_backend(base, 2, "error")
        s, b = _payout(base, _transfer(base))
        assert b["status"] == "settled" and b["attempts"] == 3


def test_provider_applies_transfer_at_most_once():
    with running_app(_workspace()) as base:
        _set_backend(base, 2, "error")
        _s, b = _payout(base, _transfer(base))
        assert b["provider_applied"] == 1
        assert _backend(base)["applied"] == 1  # one distinct transfer settled despite 3 attempts


def test_exhausted_retries_fail_without_applying():
    with running_app(_workspace()) as base:
        _set_backend(base, 99, "error")
        s, b = _payout(base, _transfer(base))
        assert b["status"] == "failed" and b["attempts"] == 3 and b["provider_applied"] == 0


def test_timeout_is_bounded_never_hangs():
    with running_app(_workspace()) as base:
        _set_backend(base, 3, "timeout")
        start = time.monotonic()
        s, b = _payout(base, _transfer(base))
        elapsed = time.monotonic() - start
        assert b["status"] == "failed"
        assert elapsed < 2.5, f"payout took {elapsed:.2f}s — timeout not enforced"


def test_circuit_opens_and_skips_the_provider():
    with running_app(_workspace()) as base:
        _set_backend(base, 99, "error")
        for _ in range(3):
            _payout(base, _transfer(base))  # 3 consecutive failures -> open
        calls_before = _backend(base)["calls"]
        s, b = _payout(base, _transfer(base))
        assert b["status"] == "circuit_open"
        assert _backend(base)["calls"] == calls_before  # provider not called


def test_circuit_half_open_recovers():
    with running_app(_workspace()) as base:
        _set_backend(base, 99, "error")
        for _ in range(3):
            _payout(base, _transfer(base))  # open
        _set_backend(base, 0, "error")  # provider healthy; does NOT reset the breaker
        assert _payout(base, _transfer(base))[1]["status"] == "circuit_open"  # still open pre-cooldown
        time.sleep(1.05)
        s, b = _payout(base, _transfer(base))
        assert b["status"] == "settled"


def test_unknown_transfer_is_404():
    with running_app(_workspace()) as base:
        assert _payout(base, "nope")[0] == 404


def test_malformed_body_is_400_not_500():
    with running_app(_workspace()) as base:
        assert http_call("POST", f"{base}/accounts", "not an object", headers=_K)[0] == 400
        assert http_call("POST", f"{base}/accounts", [1, 2, 3], headers=_K)[0] == 400


def test_carryforward_still_holds():
    with running_app(_workspace()) as base:
        s, src = http_call("POST", f"{base}/accounts", {"name": "src"}, headers=_K)
        http_call("POST", f"{base}/accounts/{src['id']}/credit", {"amount_cents": 100}, headers=_K)
        payees = [http_call("POST", f"{base}/accounts", {"name": "p"}, headers=_K)[1]["id"] for _ in range(3)]
        s, b = http_call("POST", f"{base}/transfers",
                         {"source_id": src["id"], "amount_cents": 100,
                          "payees": [{"account_id": p, "weight": 1} for p in payees]}, headers=_K)
        assert sum(x["amount_cents"] for x in b["splits"]) == 100
