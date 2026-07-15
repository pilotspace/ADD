"""HV4 FROZEN requirement checklist — resilient payouts + input hardening.

Boots the app once, runs each probe; coverage = covered / total. The circuit
breaker is GLOBAL app state, so every resilient probe starts with
`POST /admin/reset`; rate-limit buckets are per-key, so each probe takes a FRESH
key (its own full bucket of 120) and never starves another. Timing constants are
the pinned ones (200 ms attempt timeout, 3 attempts, 3-failure circuit threshold,
1 s cooldown), so the sequence is deterministic. The discriminating checks are
retry-then-settle, idempotent (never double-pay), the circuit opening WITHOUT
calling the provider, half-open recovery, bounded timeout, and 400-not-500.
"""
from __future__ import annotations

import itertools
import time

from benchmark.workload._oracle_lib import http_call

_keys = itertools.count(1)


def _key():
    return {"X-API-Key": f"bench-key-p{next(_keys)}"}


def _reset(base, k):
    http_call("POST", f"{base}/admin/reset", {}, headers=k)


def _set_backend(base, k, fail_next, mode="error"):
    http_call("PUT", f"{base}/admin/payout-backend", {"fail_next": fail_next, "mode": mode}, headers=k)


def _backend(base, k):
    _s, b = http_call("GET", f"{base}/admin/payout-backend")
    return b if isinstance(b, dict) else {}


def _account(base, k, name="a"):
    s, b = http_call("POST", f"{base}/accounts", {"name": name}, headers=k)
    return b.get("id") if s in (200, 201) and isinstance(b, dict) else None


def _credit(base, k, aid, cents):
    http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents}, headers=k)


def _make_transfer(base, k, amount=50):
    src = _account(base, k, "src")
    _credit(base, k, src, amount + 50)
    payee = _account(base, k, "p")
    s, b = http_call("POST", f"{base}/transfers",
                     {"source_id": src, "amount_cents": amount, "payees": [{"account_id": payee, "weight": 1}]},
                     headers=k)
    return b.get("id") if s in (200, 201) and isinstance(b, dict) else None


def _payout(base, k, transfer_id):
    return http_call("POST", f"{base}/payouts", {"transfer_id": transfer_id}, headers=k)


def _p_payout_happy(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 0)
    tid = _make_transfer(base, k)
    s, b = _payout(base, k, tid)
    return s in (200, 201) and isinstance(b, dict) and b.get("status") == "settled" and b.get("attempts") == 1 and b.get("provider_applied") == 1


def _p_payout_retry_then_settle(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 2, "error")  # first 2 attempts fail, 3rd settles
    tid = _make_transfer(base, k)
    s, b = _payout(base, k, tid)
    return s in (200, 201) and isinstance(b, dict) and b.get("status") == "settled" and b.get("attempts") == 3


def _p_payout_idempotent_provider(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 2, "error")
    tid = _make_transfer(base, k)
    _s, b = _payout(base, k, tid)
    return isinstance(b, dict) and b.get("provider_applied") == 1 and _backend(base, k).get("applied") == 1


def _p_payout_exhausts_retries(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 99, "error")
    tid = _make_transfer(base, k)
    s, b = _payout(base, k, tid)
    return s in (200, 201) and isinstance(b, dict) and b.get("status") == "failed" and b.get("attempts") == 3 and b.get("provider_applied") == 0


def _p_payout_timeout_bounded(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 3, "timeout")
    tid = _make_transfer(base, k)
    start = time.monotonic()
    s, b = _payout(base, k, tid)
    elapsed = time.monotonic() - start
    return s in (200, 201) and isinstance(b, dict) and b.get("status") == "failed" and elapsed < 2.5


def _p_circuit_opens_without_calling_provider(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 99, "error")
    for _ in range(3):  # 3 consecutive failed payouts -> open
        _payout(base, k, _make_transfer(base, k))
    calls_before = _backend(base, k).get("calls")
    s, b = _payout(base, k, _make_transfer(base, k))
    calls_after = _backend(base, k).get("calls")
    return (isinstance(b, dict) and b.get("status") == "circuit_open"
            and calls_before is not None and calls_after == calls_before)


def _p_circuit_half_open_recovers(base, ws):
    k = _key()
    _reset(base, k)
    _set_backend(base, k, 99, "error")
    for _ in range(3):
        _payout(base, k, _make_transfer(base, k))  # open
    _set_backend(base, k, 0, "error")  # provider healthy again (does NOT reset circuit)
    s_open, b_open = _payout(base, k, _make_transfer(base, k))
    if not (isinstance(b_open, dict) and b_open.get("status") == "circuit_open"):
        return False  # still open before cooldown
    time.sleep(1.05)  # cooldown -> half-open
    s, b = _payout(base, k, _make_transfer(base, k))
    return isinstance(b, dict) and b.get("status") == "settled"


def _p_payout_unknown_transfer_404(base, ws):
    k = _key()
    _reset(base, k)
    s, _ = _payout(base, k, "does-not-exist")
    return s == 404


def _p_malformed_body_400(base, ws):
    k = _key()
    s_str, _ = http_call("POST", f"{base}/accounts", "not an object", headers=k)
    s_list, _ = http_call("POST", f"{base}/accounts", [1, 2, 3], headers=k)
    return s_str == 400 and s_list == 400


def _p_wrong_type_400(base, ws):
    k = _key()
    src = _account(base, k, "src")
    _credit(base, k, src, 100)
    payee = _account(base, k, "p")
    str_amt, _ = http_call("POST", f"{base}/transfers",
                           {"source_id": src, "amount_cents": "50", "payees": [{"account_id": payee, "weight": 1}]}, headers=k)
    float_wt, _ = http_call("POST", f"{base}/transfers",
                            {"source_id": src, "amount_cents": 50, "payees": [{"account_id": payee, "weight": 1.5}]}, headers=k)
    return str_amt == 400 and float_wt == 400


def _p_carryforward_transfer(base, ws):
    k = _key()
    src = _account(base, k, "src")
    _credit(base, k, src, 100)
    payees = [_account(base, k, f"p{i}") for i in range(3)]
    s, b = http_call("POST", f"{base}/transfers",
                     {"source_id": src, "amount_cents": 100, "payees": [{"account_id": p, "weight": 1} for p in payees]}, headers=k)
    return s in (200, 201) and isinstance(b, dict) and sum(x["amount_cents"] for x in b.get("splits", [])) == 100


def _p_carryforward_invoice(base, ws):
    k = _key()
    cust, merch = _account(base, k, "c"), _account(base, k, "m")
    _credit(base, k, cust, 1152)
    s, b = http_call("POST", f"{base}/invoices",
                     {"customer_account_id": cust, "merchant_account_id": merch,
                      "line_items": [{"sku": "x", "unit_price_cents": 600, "qty": 1}], "coupons": []}, headers=k)
    return s in (200, 201) and isinstance(b, dict) and b.get("total_cents") == 1152 and bool(b.get("transfer_id"))


def _p_integer_money(base, ws):
    k = _key()
    aid = _account(base, k)
    s, b = http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": 100}, headers=k)
    return s in (200, 201) and isinstance(b.get("balance_cents"), int) and not isinstance(b.get("balance_cents"), bool)


def _p_entry_contract(base, ws):
    s, _ = http_call("GET", f"{base}/accounts")
    return s == 200


REQUIREMENTS = [
    {"id": "R-payout-happy", "description": "a healthy payout settles in one attempt, applied once", "probe": _p_payout_happy},
    {"id": "R-payout-retry-then-settle", "description": "transient provider failures are retried and then settle", "probe": _p_payout_retry_then_settle},
    {"id": "R-payout-idempotent-provider", "description": "retries never double-pay: the provider applies a transfer at most once", "probe": _p_payout_idempotent_provider},
    {"id": "R-payout-exhausts-retries", "description": "after 3 failed attempts the payout is failed, not applied", "probe": _p_payout_exhausts_retries},
    {"id": "R-payout-timeout-bounded", "description": "a timing-out provider fails within a bounded time, never hangs", "probe": _p_payout_timeout_bounded},
    {"id": "R-circuit-opens", "description": "after 3 consecutive failures the breaker opens without calling the provider", "probe": _p_circuit_opens_without_calling_provider},
    {"id": "R-circuit-half-open-recovers", "description": "after the cooldown a half-open probe recovers and closes the breaker", "probe": _p_circuit_half_open_recovers},
    {"id": "R-payout-unknown-404", "description": "a payout for an unknown transfer is 404", "probe": _p_payout_unknown_transfer_404},
    {"id": "R-malformed-body-400", "description": "a non-object JSON body is 400, never 500", "probe": _p_malformed_body_400},
    {"id": "R-wrong-type-400", "description": "wrong-typed fields (string amount, float weight) are 400", "probe": _p_wrong_type_400},
    {"id": "R-carryforward-transfer", "description": "a keyed split transfer still reconciles", "probe": _p_carryforward_transfer},
    {"id": "R-carryforward-invoice", "description": "a keyed invoice still prices and settles", "probe": _p_carryforward_invoice},
    {"id": "R-integer-money", "description": "balances stay integer cents", "probe": _p_integer_money},
    {"id": "R-entry-contract", "description": "the app still runs as `python -m app` on $PORT", "probe": _p_entry_contract},
]
