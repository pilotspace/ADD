"""HV3 FROZEN requirement checklist — API keys + per-key token-bucket limiting.

Boots the app once, runs each probe; coverage = covered / total. Rate-limit
probes use DEDICATED keys (each key its own bucket) so they never starve the
functional carry-forward probes, which run on `bench-key-alice`. Deterministic:
buckets are capacity 120 / refill 20 per second, so a burst of 200 always
exhausts and a 1.1s wait always refills. The discriminating checks are that a
limit exists at all, that buckets are PER KEY (no global limiter), that a
throttled key refills, and that reads stay open.
"""
from __future__ import annotations

import time

from benchmark.workload._oracle_lib import http_call

_ALICE = {"X-API-Key": "bench-key-alice"}
CAPACITY = 120


def _post_account(base, headers):
    return http_call("POST", f"{base}/accounts", {"name": "a"}, headers=headers)


def _burst(base, key, n):
    """Fire n keyed POSTs; return (count_200, count_429)."""
    hdr = {"X-API-Key": key}
    ok = throttled = 0
    for _ in range(n):
        status, _b = _post_account(base, hdr)
        if status in (200, 201):
            ok += 1
        elif status == 429:
            throttled += 1
    return ok, throttled


def _account(base, name="a"):
    status, body = _post_account(base, _ALICE)
    return body.get("id") if status in (200, 201) and isinstance(body, dict) else None


def _credit(base, aid, cents):
    http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents}, headers=_ALICE)


def _p_key_required_on_mutation(base, ws):
    status, _ = http_call("POST", f"{base}/accounts", {"name": "a"})  # no key
    return status == 401


def _p_bad_key_401(base, ws):
    status, _ = _post_account(base, {"X-API-Key": "nope"})  # not bench-key-*
    return status == 401


def _p_valid_key_works(base, ws):
    status, _ = _post_account(base, _ALICE)
    return status in (200, 201)


def _p_reads_open_without_key(base, ws):
    status, body = http_call("GET", f"{base}/accounts")  # no key
    return status == 200 and isinstance(body, list)


def _p_rate_limit_exists(base, ws):
    _ok, throttled = _burst(base, "bench-key-exists", CAPACITY + 80)
    return throttled >= 1


def _p_per_key_isolation(base, ws):
    _burst(base, "bench-key-iso-a", CAPACITY + 80)  # exhaust A
    status, _ = _post_account(base, {"X-API-Key": "bench-key-iso-b"})  # B is fresh
    return status in (200, 201)


def _p_refill_after_wait(base, ws):
    _burst(base, "bench-key-refill", CAPACITY + 80)  # exhaust
    time.sleep(1.1)  # ~22 tokens refill at 20/s
    status, _ = _post_account(base, {"X-API-Key": "bench-key-refill"})
    return status in (200, 201)


def _p_reads_not_rate_limited(base, ws):
    _burst(base, "bench-key-reads", CAPACITY + 80)  # exhaust the mutating bucket
    status, body = http_call("GET", f"{base}/accounts")  # reads unaffected
    return status == 200 and isinstance(body, list)


def _p_carryforward_transfer(base, ws):
    src = _account(base)
    _credit(base, src, 100)
    payees = [_account(base) for _ in range(3)]
    if not src or any(p is None for p in payees):
        return False
    status, b = http_call("POST", f"{base}/transfers",
                          {"source_id": src, "amount_cents": 100,
                           "payees": [{"account_id": p, "weight": 1} for p in payees]}, headers=_ALICE)
    return status in (200, 201) and isinstance(b, dict) and sum(s["amount_cents"] for s in b.get("splits", [])) == 100


def _p_carryforward_invoice(base, ws):
    cust, merch = _account(base), _account(base)
    _credit(base, cust, 1152)
    status, b = http_call("POST", f"{base}/invoices",
                          {"customer_account_id": cust, "merchant_account_id": merch,
                           "line_items": [{"sku": "x", "unit_price_cents": 600, "qty": 1}], "coupons": []}, headers=_ALICE)
    return status in (200, 201) and isinstance(b, dict) and b.get("total_cents") == 1152 and bool(b.get("transfer_id"))


def _p_integer_money(base, ws):
    aid = _account(base)
    status, body = http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": 100}, headers=_ALICE)
    return status in (200, 201) and isinstance(body.get("balance_cents"), int) and not isinstance(body.get("balance_cents"), bool)


def _p_entry_contract(base, ws):
    status, _ = http_call("GET", f"{base}/accounts")
    return status == 200


REQUIREMENTS = [
    {"id": "R-key-required", "description": "a mutation without a valid API key is 401", "probe": _p_key_required_on_mutation},
    {"id": "R-bad-key-401", "description": "a key not beginning with bench-key- is 401", "probe": _p_bad_key_401},
    {"id": "R-valid-key-works", "description": "a mutation with a valid key under the limit succeeds", "probe": _p_valid_key_works},
    {"id": "R-reads-open", "description": "GET is open without an API key", "probe": _p_reads_open_without_key},
    {"id": "R-rate-limit-exists", "description": "a burst on one key is eventually 429'd (a limit exists)", "probe": _p_rate_limit_exists},
    {"id": "R-per-key-isolation", "description": "exhausting one key does not throttle another key", "probe": _p_per_key_isolation},
    {"id": "R-refill-after-wait", "description": "a throttled key refills after waiting", "probe": _p_refill_after_wait},
    {"id": "R-reads-not-limited", "description": "reads stay available when a key's mutating bucket is exhausted", "probe": _p_reads_not_rate_limited},
    {"id": "R-carryforward-transfer", "description": "a keyed split transfer still reconciles to the cent", "probe": _p_carryforward_transfer},
    {"id": "R-carryforward-invoice", "description": "a keyed invoice still prices and settles", "probe": _p_carryforward_invoice},
    {"id": "R-integer-money", "description": "balances stay integer cents", "probe": _p_integer_money},
    {"id": "R-entry-contract", "description": "the app still runs as `python -m app` on $PORT", "probe": _p_entry_contract},
]
