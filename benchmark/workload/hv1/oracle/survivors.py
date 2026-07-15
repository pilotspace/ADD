"""HV1 must-survive invariants (family-local regression, mirrors the wm track).

Regression probes re-run against EVERY LATER HV workspace — so each probe must
hold under legitimate later evolution (hv2 adds a pricing/invoice layer; hv3
adds a per-key token-bucket rate limit; hv4 adds resilient settlement + input
hardening). Two rules keep them survivable:

1. KEY-CARRYING: every call sends the pinned API key (`bench-key-alice`, pinned
   in hv3's PROMPT). An hv1/hv2 app ignores the header; an hv3+ app requires it.
   Calls stay well under the hv3 bucket (capacity 60) so a later app never 429s
   these. Never assert un-keyed success.
2. LAW-TOLERANT: probe only the money-conservation LAWS that never change — a
   split reconciles to the cent, an over-transfer is 409, an unknown account is
   404, money is integer. No probe reads pricing/invoice/rate-limit specifics.

These are the split-payment analogue of the wm survivors. Never visible to the
arm under test.
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


def test_split_reconciles_exactly():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        a, b = _account(base, "a"), _account(base, "b")
        status, body = http_call(
            "POST", f"{base}/transfers",
            {"source_id": src, "amount_cents": 100,
             "payees": [{"account_id": a, "weight": 1}, {"account_id": b, "weight": 1}]},
            headers=_KEY,
        )
        assert status in (200, 201), body
        assert sum(s["amount_cents"] for s in body["splits"]) == 100


def test_over_transfer_is_409():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 30)
        p = _account(base, "p")
        status, _ = http_call(
            "POST", f"{base}/transfers",
            {"source_id": src, "amount_cents": 100, "payees": [{"account_id": p, "weight": 1}]},
            headers=_KEY,
        )
        assert status == 409


def test_unknown_account_is_404():
    with running_app(_workspace()) as base:
        p = _account(base, "p")
        status, _ = http_call(
            "POST", f"{base}/transfers",
            {"source_id": "does-not-exist", "amount_cents": 10, "payees": [{"account_id": p, "weight": 1}]},
            headers=_KEY,
        )
        assert status == 404


def test_money_stays_integer():
    with running_app(_workspace()) as base:
        aid = _account(base, "a")
        status, body = http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": 100}, headers=_KEY)
        assert status in (200, 201)
        assert isinstance(body["balance_cents"], int) and not isinstance(body["balance_cents"], bool)
