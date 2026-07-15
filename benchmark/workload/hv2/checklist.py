"""HV2 FROZEN requirement checklist — pricing & checkout on the ledger.

One row per enumerated requirement in hv2/PROMPT.md. Boots the built app once,
runs each probe; coverage = covered / total. Every expected cent value is
hardcoded from the pinned pipeline (8.75% tax round-half-even, $50 free-ship
threshold, $5 flat shipping), so the score is deterministic and NO LLM is in the
path. The discriminating checks are discount precedence (percent before fixed),
tax on the DISCOUNTED subtotal, half-even rounding, the floor-at-zero, and that
the invoice actually settles a conserving ledger transfer.
"""
from __future__ import annotations

import itertools

from benchmark.workload._oracle_lib import http_call

_codes = itertools.count(1)


def _account(base, name="acct"):
    status, body = http_call("POST", f"{base}/accounts", {"name": name})
    return body.get("id") if status in (200, 201) and isinstance(body, dict) else None


def _credit(base, aid, cents):
    return http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents})


def _coupon(base, kind, value, once=False):
    code = f"C{next(_codes)}"
    status, _ = http_call("POST", f"{base}/coupons",
                          {"code": code, "kind": kind, "value": value, "once_per_customer": once})
    return code if status in (200, 201) else None


def _invoice(base, cust, merch, items, coupons=None):
    return http_call("POST", f"{base}/invoices", {
        "customer_account_id": cust, "merchant_account_id": merch,
        "line_items": items, "coupons": coupons or [],
    })


def _pair(base):
    return _account(base, "cust"), _account(base, "merch")


def _p_subtotal_and_composition(base, ws):
    """600c goods, no coupon → subtotal 600, tax 52, ship 500, total 1152; and
    total == (subtotal - discount) + tax + shipping."""
    c, m = _pair(base)
    _credit(base, c, 2000)
    status, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
    if status not in (200, 201) or not isinstance(b, dict):
        return False
    ok_vals = (b.get("subtotal_cents") == 600 and b.get("tax_cents") == 52
               and b.get("shipping_cents") == 500 and b.get("total_cents") == 1152)
    ok_comp = b.get("total_cents") == (b.get("subtotal_cents", 0) - b.get("discount_cents", 0)
                                       + b.get("tax_cents", 0) + b.get("shipping_cents", 0))
    return ok_vals and ok_comp


def _p_percent_discount(base, ws):
    c, m = _pair(base)
    _credit(base, c, 5000)
    code = _coupon(base, "percent", 10)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], [code])
    return isinstance(b, dict) and b.get("discount_cents") == 100 and b.get("total_cents") == 1479


def _p_fixed_discount(base, ws):
    c, m = _pair(base)
    _credit(base, c, 5000)
    code = _coupon(base, "fixed", 300)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], [code])
    return isinstance(b, dict) and b.get("discount_cents") == 300 and b.get("total_cents") == 1261


def _p_discount_precedence(base, ws):
    """percent BEFORE fixed: 1000 -> 900 -> 600 (discount 400). Wrong order
    (fixed first) yields discounted 630 — a different total."""
    c, m = _pair(base)
    _credit(base, c, 5000)
    pct = _coupon(base, "percent", 10)
    fix = _coupon(base, "fixed", 300)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], [pct, fix])
    return isinstance(b, dict) and b.get("discount_cents") == 400 and b.get("total_cents") == 1152


def _p_discount_floor_zero(base, ws):
    """A fixed discount larger than the goods can NEVER go negative: 500 - 1000
    floors to 0 (discount capped at 500), total is shipping only."""
    c, m = _pair(base)
    _credit(base, c, 5000)
    fix = _coupon(base, "fixed", 1000)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 500, "qty": 1}], [fix])
    return isinstance(b, dict) and b.get("discount_cents") == 500 and b.get("total_cents") == 500


def _p_tax_on_discounted(base, ws):
    """Tax is on the DISCOUNTED subtotal: 10% off 1000 -> 900 -> tax 79, not the
    88 you get taxing the gross 1000."""
    c, m = _pair(base)
    _credit(base, c, 5000)
    pct = _coupon(base, "percent", 10)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], [pct])
    return isinstance(b, dict) and b.get("tax_cents") == 79


def _p_tax_round_half_even(base, ws):
    """600 * 8.75% = 52.5 -> round-half-to-even -> 52 (not 53)."""
    c, m = _pair(base)
    _credit(base, c, 2000)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
    return isinstance(b, dict) and b.get("tax_cents") == 52


def _p_free_shipping_at_threshold(base, ws):
    c, m = _pair(base)
    _credit(base, c, 10000)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 5000, "qty": 1}])
    return isinstance(b, dict) and b.get("shipping_cents") == 0


def _p_shipping_below_threshold(base, ws):
    c, m = _pair(base)
    _credit(base, c, 2000)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
    return isinstance(b, dict) and b.get("shipping_cents") == 500


def _p_settles_ledger_transfer(base, ws):
    """The invoice settles a conserving transfer: customer debited total,
    merchant credited total, and a transfer_id is returned."""
    c, m = _pair(base)
    _credit(base, c, 1152)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
    if not isinstance(b, dict) or not b.get("transfer_id"):
        return False
    _, cust = http_call("GET", f"{base}/accounts/{c}")
    _, merch = http_call("GET", f"{base}/accounts/{m}")
    return cust.get("balance_cents") == 0 and merch.get("balance_cents") == 1152


def _p_insufficient_409(base, ws):
    c, m = _pair(base)
    _credit(base, c, 100)  # can't afford total 1152
    status, _ = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
    if status != 409:
        return False
    _, cust = http_call("GET", f"{base}/accounts/{c}")
    return cust.get("balance_cents") == 100  # no debit


def _p_coupon_once_per_customer(base, ws):
    a, m = _pair(base)
    b_cust = _account(base, "cust-b")
    for acct in (a, b_cust):
        _credit(base, acct, 10000)
    code = _coupon(base, "fixed", 100, once=True)
    items = [{"sku": "x", "unit_price_cents": 1000, "qty": 1}]
    s1, _ = _invoice(base, a, m, items, [code])
    s2, _ = _invoice(base, a, m, items, [code])  # A reuses -> 400
    s3, _ = _invoice(base, b_cust, m, items, [code])  # B first use -> ok
    return s1 in (200, 201) and s2 == 400 and s3 in (200, 201)


def _p_unknown_coupon_400(base, ws):
    c, m = _pair(base)
    _credit(base, c, 5000)
    status, _ = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 1000, "qty": 1}], ["NOPE"])
    return status == 400


def _p_empty_lineitems_400(base, ws):
    c, m = _pair(base)
    status, _ = _invoice(base, c, m, [])
    return status == 400


def _p_bad_price_qty_400(base, ws):
    c, m = _pair(base)
    _credit(base, c, 5000)
    zero_price, _ = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 0, "qty": 1}])
    zero_qty, _ = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 100, "qty": 0}])
    return zero_price == 400 and zero_qty == 400


def _p_integer_money(base, ws):
    c, m = _pair(base)
    _credit(base, c, 2000)
    _, b = _invoice(base, c, m, [{"sku": "x", "unit_price_cents": 600, "qty": 1}])
    return isinstance(b, dict) and isinstance(b.get("total_cents"), int) and not isinstance(b.get("total_cents"), bool)


def _p_entry_contract(base, ws):
    status, _ = http_call("GET", f"{base}/accounts")
    return status == 200


REQUIREMENTS = [
    {"id": "R-subtotal-composition", "description": "subtotal + tax + shipping compose the total (600c -> 1152)", "probe": _p_subtotal_and_composition},
    {"id": "R-percent-discount", "description": "a percent coupon takes value% off", "probe": _p_percent_discount},
    {"id": "R-fixed-discount", "description": "a fixed coupon takes value cents off", "probe": _p_fixed_discount},
    {"id": "R-discount-precedence", "description": "percent coupons apply before fixed coupons", "probe": _p_discount_precedence},
    {"id": "R-discount-floor-zero", "description": "a discount never drives the goods amount below zero", "probe": _p_discount_floor_zero},
    {"id": "R-tax-on-discounted", "description": "tax is computed on the discounted subtotal, not the gross", "probe": _p_tax_on_discounted},
    {"id": "R-tax-round-half-even", "description": "tax rounds half-to-even (52.5 -> 52)", "probe": _p_tax_round_half_even},
    {"id": "R-free-shipping-threshold", "description": "discounted subtotal >= $50 ships free", "probe": _p_free_shipping_at_threshold},
    {"id": "R-shipping-below-threshold", "description": "below the threshold a $5 flat shipping applies", "probe": _p_shipping_below_threshold},
    {"id": "R-settles-transfer", "description": "the invoice settles a conserving customer->merchant ledger transfer", "probe": _p_settles_ledger_transfer},
    {"id": "R-insufficient-409", "description": "a customer who cannot afford the total gets 409, no invoice", "probe": _p_insufficient_409},
    {"id": "R-coupon-once-per-customer", "description": "a once-per-customer coupon is exhausted after one use per customer", "probe": _p_coupon_once_per_customer},
    {"id": "R-unknown-coupon-400", "description": "an unknown coupon code is 400", "probe": _p_unknown_coupon_400},
    {"id": "R-empty-lineitems-400", "description": "an empty line_items array is 400", "probe": _p_empty_lineitems_400},
    {"id": "R-bad-price-qty-400", "description": "non-positive unit_price_cents or qty is 400", "probe": _p_bad_price_qty_400},
    {"id": "R-integer-money", "description": "invoice totals are integer cents", "probe": _p_integer_money},
    {"id": "R-entry-contract", "description": "the app still runs as `python -m app` on $PORT", "probe": _p_entry_contract},
]
