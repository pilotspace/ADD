"""HV3 oracle — API keys + per-key token-bucket rate limiting. Not arm-visible.

Black-box, deterministic. The discriminating checks are that a limit exists,
that buckets are PER KEY (no global limiter), that a throttled key refills, that
reads stay open, and that carry-forward behavior still holds under a valid key.
Red on an empty workspace.
"""
import os
import time

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

CAPACITY = 120
_ALICE = {"X-API-Key": "bench-key-alice"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _burst(base, key, n):
    hdr = {"X-API-Key": key}
    ok = throttled = 0
    for _ in range(n):
        status, _b = http_call("POST", f"{base}/accounts", {"name": "a"}, headers=hdr)
        if status in (200, 201):
            ok += 1
        elif status == 429:
            throttled += 1
    return ok, throttled


def _account(base):
    status, body = http_call("POST", f"{base}/accounts", {"name": "a"}, headers=_ALICE)
    assert status in (200, 201), body
    return body["id"]


def _credit(base, aid, cents):
    http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents}, headers=_ALICE)


def test_mutation_requires_valid_key():
    with running_app(_workspace()) as base:
        assert http_call("POST", f"{base}/accounts", {"name": "a"})[0] == 401  # no key
        assert http_call("POST", f"{base}/accounts", {"name": "a"}, headers={"X-API-Key": "nope"})[0] == 401
        assert http_call("POST", f"{base}/accounts", {"name": "a"}, headers=_ALICE)[0] in (200, 201)


def test_reads_are_open_without_a_key():
    with running_app(_workspace()) as base:
        status, body = http_call("GET", f"{base}/accounts")
        assert status == 200 and isinstance(body, list)


def test_a_limit_exists_and_bounds_a_burst():
    with running_app(_workspace()) as base:
        ok, throttled = _burst(base, "bench-key-burst", 3 * CAPACITY)
        assert throttled >= 1, "no rate limit at all"
        assert ok <= 2 * CAPACITY, f"burst not bounded near capacity: {ok} succeeded"


def test_buckets_are_per_key():
    with running_app(_workspace()) as base:
        _burst(base, "bench-key-a", CAPACITY + 80)  # exhaust A
        # B is a different key -> its own full bucket -> not throttled
        status, _ = http_call("POST", f"{base}/accounts", {"name": "a"}, headers={"X-API-Key": "bench-key-b"})
        assert status in (200, 201)


def test_a_throttled_key_refills_after_waiting():
    with running_app(_workspace()) as base:
        _burst(base, "bench-key-refill", CAPACITY + 80)
        time.sleep(1.1)  # ~22 tokens back at 20/s
        status, _ = http_call("POST", f"{base}/accounts", {"name": "a"}, headers={"X-API-Key": "bench-key-refill"})
        assert status in (200, 201)


def test_reads_stay_open_when_a_key_is_exhausted():
    with running_app(_workspace()) as base:
        _burst(base, "bench-key-reads", CAPACITY + 80)
        status, body = http_call("GET", f"{base}/accounts")
        assert status == 200 and isinstance(body, list)


def test_keyed_transfer_still_reconciles():
    with running_app(_workspace()) as base:
        src = _account(base)
        _credit(base, src, 100)
        payees = [_account(base) for _ in range(3)]
        status, b = http_call("POST", f"{base}/transfers",
                              {"source_id": src, "amount_cents": 100,
                               "payees": [{"account_id": p, "weight": 1} for p in payees]}, headers=_ALICE)
        assert status in (200, 201), b
        assert sum(s["amount_cents"] for s in b["splits"]) == 100


def test_keyed_invoice_still_settles():
    with running_app(_workspace()) as base:
        cust, merch = _account(base), _account(base)
        _credit(base, cust, 1152)
        status, b = http_call("POST", f"{base}/invoices",
                              {"customer_account_id": cust, "merchant_account_id": merch,
                               "line_items": [{"sku": "x", "unit_price_cents": 600, "qty": 1}], "coupons": []}, headers=_ALICE)
        assert status in (200, 201), b
        assert b["total_cents"] == 1152 and b["transfer_id"]
