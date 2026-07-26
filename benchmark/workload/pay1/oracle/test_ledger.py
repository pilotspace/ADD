"""PAY1 oracle — split-payment ledger core. Never visible to the arm under test.

Scores against $BENCH_WORKSPACE (an arm's built app). Must collect and fail
against an empty workspace (red for the right reason). Every probe is black-box
over HTTP and deterministic; the discriminating checks are exact-cent
reconciliation, idempotent replay, and conservation.
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
    status, body = http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents})
    assert status in (200, 201), body
    return body


def _transfer(base, source_id, amount, payees, headers=None):
    return http_call(
        "POST", f"{base}/transfers",
        {"source_id": source_id, "amount_cents": amount, "payees": payees},
        headers=headers,
    )


def test_account_lifecycle():
    with running_app(_workspace()) as base:
        aid = _account(base, "alice")
        status, acct = http_call("GET", f"{base}/accounts/{aid}")
        assert status == 200
        assert acct["balance_cents"] == 0
        assert _credit(base, aid, 250)["balance_cents"] == 250


def test_split_reconciles_to_the_cent():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        payees = [_account(base, f"p{i}") for i in range(3)]
        status, body = _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
        assert status in (200, 201), body
        shares = [s["amount_cents"] for s in body["splits"]]
        assert sum(shares) == 100, shares
        assert shares == [34, 33, 33], shares  # tie -> lowest index wins the extra cent


def test_split_proportional_to_weights():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        a, b = _account(base, "a"), _account(base, "b")
        status, body = _transfer(base, src, 100, [{"account_id": a, "weight": 2}, {"account_id": b, "weight": 1}])
        assert status in (200, 201), body
        assert [s["amount_cents"] for s in body["splits"]] == [67, 33]


def test_balances_move_and_conserve():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        payees = [_account(base, f"p{i}") for i in range(3)]
        _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
        _, accts = http_call("GET", f"{base}/accounts")
        assert sum(a["balance_cents"] for a in accts) == 100  # nothing created/destroyed
        _, src_acct = http_call("GET", f"{base}/accounts/{src}")
        assert src_acct["balance_cents"] == 0


def test_insufficient_funds_is_409_no_partial_debit():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 50)
        p = _account(base, "p")
        status, _ = _transfer(base, src, 100, [{"account_id": p, "weight": 1}])
        assert status == 409
        _, src_acct = http_call("GET", f"{base}/accounts/{src}")
        assert src_acct["balance_cents"] == 50  # untouched


def test_idempotent_replay_debits_once():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        p = _account(base, "p")
        body = {"source_id": src, "amount_cents": 40, "payees": [{"account_id": p, "weight": 1}]}
        hdr = {"Idempotency-Key": "key-1"}
        s1, b1 = http_call("POST", f"{base}/transfers", body, headers=hdr)
        s2, b2 = http_call("POST", f"{base}/transfers", body, headers=hdr)
        assert s1 in (200, 201) and s2 in (200, 201)
        assert b1["id"] == b2["id"]
        _, src_acct = http_call("GET", f"{base}/accounts/{src}")
        assert src_acct["balance_cents"] == 60  # 40 debited exactly once


def test_idempotency_key_reuse_with_different_body_is_409():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        p = _account(base, "p")
        hdr = {"Idempotency-Key": "key-2"}
        http_call("POST", f"{base}/transfers",
                  {"source_id": src, "amount_cents": 40, "payees": [{"account_id": p, "weight": 1}]}, headers=hdr)
        status, _ = http_call("POST", f"{base}/transfers",
                              {"source_id": src, "amount_cents": 41, "payees": [{"account_id": p, "weight": 1}]}, headers=hdr)
        assert status == 409


def test_unknown_source_is_404():
    with running_app(_workspace()) as base:
        p = _account(base, "p")
        status, _ = _transfer(base, "nope", 10, [{"account_id": p, "weight": 1}])
        assert status == 404


def test_bad_amount_and_empty_payees_are_400_not_500():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        p = _account(base, "p")
        for amount in (0, -5, "10"):
            status, _ = _transfer(base, src, amount, [{"account_id": p, "weight": 1}])
            assert status == 400, amount
        status, _ = _transfer(base, src, 10, [])
        assert status == 400


def test_money_is_integer_never_float():
    with running_app(_workspace()) as base:
        aid = _account(base, "a")
        acct = _credit(base, aid, 100)
        assert isinstance(acct["balance_cents"], int)
        assert not isinstance(acct["balance_cents"], bool)
