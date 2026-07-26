"""PAY2 oracle — pricing & checkout on the ledger. Never visible to the arm.

Scores against $BENCH_WORKSPACE. Black-box, deterministic; the discriminating
checks are discount precedence, tax-on-discounted, half-even rounding, the
floor-at-zero, and conserving settlement. Red on an empty workspace.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _account(base, name="acct"):
    status, body = http_call("POST", f"{base}/accounts", {"name": name})
    assert status in (200, 201), body
    return body["id"]


def _credit(base, aid, cents):
    http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents})


def _coupon(base, code, kind, value, once=False):
    status, _ = http_call("POST", f"{base}/coupons",
                          {"code": code, "kind": kind, "value": value, "once_per_customer": once})
    assert status in (200, 201)
    return code


def _invoice(base, cust, merch, items, coupons=None):
    return http_call("POST", f"{base}/invoices", {
        "customer_account_id": cust, "merchant_account_id": merch,
        "line_items": items, "coupons": coupons or [],
    })


def test_full_price_composition():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 2000)
        status, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert status in (200, 201), b
        assert b["subtotal_cents"] == 600 and b["tax_cents"] == 52
        assert b["shipping_cents"] == 500 and b["total_cents"] == 1152


def test_discount_precedence_percent_before_fixed():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 5000)
        _coupon(base, "P10", "percent", 10)
        _coupon(base, "F300", "fixed", 300)
        _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], ["P10", "F300"])
        assert b["discount_cents"] == 400  # 1000 -> 900 -> 600
        assert b["total_cents"] == 1152


def test_tax_is_on_discounted_subtotal():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 5000)
        _coupon(base, "P10b", "percent", 10)
        _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], ["P10b"])
        assert b["tax_cents"] == 79  # on 900, not 88 on 1000


def test_tax_rounds_half_to_even():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 2000)
        _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert b["tax_cents"] == 52  # 52.5 -> even 52, not 53


def test_discount_floors_at_zero():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 5000)
        _coupon(base, "BIG", "fixed", 1000)
        _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 500, "qty": 1}], ["BIG"])
        assert b["discount_cents"] == 500 and b["total_cents"] == 500  # never negative


def test_free_shipping_threshold():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 10000)
        _, over = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 5000, "qty": 1}])
        assert over["shipping_cents"] == 0
        c2 = _account(base, "c2")
        _credit(base, c2, 2000)
        _, under = _invoice(base, c2, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert under["shipping_cents"] == 500


def test_invoice_settles_conserving_transfer():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 1152)
        _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert b["transfer_id"]
        _, cust = http_call("GET", f"{base}/accounts/{c}")
        _, merch = http_call("GET", f"{base}/accounts/{m}")
        assert cust["balance_cents"] == 0 and merch["balance_cents"] == 1152


def test_insufficient_customer_is_409_no_invoice():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 100)
        status, _ = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
        assert status == 409
        _, cust = http_call("GET", f"{base}/accounts/{c}")
        assert cust["balance_cents"] == 100


def test_once_per_customer_coupon_exhausts():
    with running_app(_workspace()) as base:
        m = _account(base, "m")
        a, b = _account(base, "a"), _account(base, "b")
        _credit(base, a, 10000)
        _credit(base, b, 10000)
        _coupon(base, "ONCE", "fixed", 100, once=True)
        items = [{"sku": "x", "unit_price_cents": 1000, "qty": 1}]
        assert _invoice(base, a, m, items, ["ONCE"])[0] in (200, 201)
        assert _invoice(base, a, m, items, ["ONCE"])[0] == 400  # A reuse
        assert _invoice(base, b, m, items, ["ONCE"])[0] in (200, 201)  # B ok


def test_bad_input_is_4xx_not_500():
    with running_app(_workspace()) as base:
        c, m = _account(base, "c"), _account(base, "m")
        _credit(base, c, 5000)
        assert _invoice(base, c, m, [])[0] == 400
        assert _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 0, "qty": 1}])[0] == 400
        assert _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 100, "qty": 1}], ["NOPE"])[0] == 400
