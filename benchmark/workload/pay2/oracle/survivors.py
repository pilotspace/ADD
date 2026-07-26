"""PAY2 must-survive invariants — the pricing LAWS that outlive later evolution.

Re-run against every later PAY workspace (pay3 rate limit, pay4 resilient
settlement). KEY-CARRYING (X-API-Key bench-key-alice, pinned in pay3) and kept to
a handful of calls, well under the pay3 bucket. LAW-TOLERANT: probe only pricing
invariants that never change — percent-before-fixed precedence, tax on the
discounted subtotal, and conserving settlement. Never visible to the arm.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

_KEY = {"X-API-Key": "bench-key-alice"}


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _account(base, name="acct"):
    status, body = http_call("POST", f"{base}/accounts", {"name": name}, headers=_KEY)
    assert status in (200, 201), body
    return body["id"]


def _credit(base, aid, cents):
    http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents}, headers=_KEY)


def _invoice(base, cust, merch, items, coupons=None):
    return http_call("POST", f"{base}/invoices", {
        "customer_account_id": cust, "merchant_account_id": merch,
        "line_items": items, "coupons": coupons or [],
    }, headers=_KEY)


def test_precedence_and_tax_law_hold():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 5000)
        http_call("POST", f"{base}/coupons",
                  {"code": "SVP10", "kind": "percent", "value": 10, "once_per_customer": False}, headers=_KEY)
        http_call("POST", f"{base}/coupons",
                  {"code": "SVF300", "kind": "fixed", "value": 300, "once_per_customer": False}, headers=_KEY)
        status, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], ["SVP10", "SVF300"])
        assert status in (200, 201), b
        assert b["discount_cents"] == 400 and b["total_cents"] == 1152


def test_invoice_settles_a_conserving_transfer():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 1152)
        status, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert status in (200, 201), b
        assert b["transfer_id"]
        _, cust = http_call("GET", f"{base}/accounts/{c}", headers=_KEY)
        _, merch = http_call("GET", f"{base}/accounts/{m}", headers=_KEY)
        assert cust["balance_cents"] == 0 and merch["balance_cents"] == 1152


def test_customer_who_cannot_pay_is_409():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 100)
        status, _ = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert status == 409
