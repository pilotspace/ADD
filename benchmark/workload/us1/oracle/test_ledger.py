"""US1 oracle — UNDER-SPECIFIED split-payment ledger. Not arm-visible.

Probes ONLY objectively-correct invariants (the rules are hidden in the prompt):
a split reconciles to the cent, money is conserved, and no sub-cent leaks. Red
on an empty workspace.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def _account(base, name="a"):
    s, b = http_call("POST", f"{base}/accounts", {"name": name})
    assert s in (200, 201), b
    return b["id"]


def _credit(base, aid, cents):
    http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents})


def _transfer(base, src, amount, payees):
    return http_call("POST", f"{base}/transfers",
                     {"source_id": src, "amount_cents": amount, "payees": payees})


def _total(base):
    _s, accts = http_call("GET", f"{base}/accounts")
    return sum(a["balance_cents"] for a in accts)


def test_account_lifecycle():
    with running_app(_workspace()) as base:
        aid = _account(base)
        _s, acct = http_call("GET", f"{base}/accounts/{aid}")
        assert acct["balance_cents"] == 0
        _credit(base, aid, 500)
        _s, acct = http_call("GET", f"{base}/accounts/{aid}")
        assert acct["balance_cents"] == 500


def test_split_reconciles_to_the_cent():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        payees = [_account(base, f"p{i}") for i in range(3)]
        s, b = _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
        assert s in (200, 201), b
        shares = [x["amount_cents"] for x in b["splits"]]
        assert all(isinstance(x, int) for x in shares), shares
        assert sum(shares) == 100, shares  # no cent lost, even though the rule was unstated


def test_transfer_conserves_money():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        payees = [_account(base, f"p{i}") for i in range(3)]
        before = _total(base)
        _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
        assert _total(base) == before  # nothing created or destroyed


def test_source_debited_and_payees_credited_exactly():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        payees = [_account(base, f"p{i}") for i in range(3)]
        _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
        _s, s_acct = http_call("GET", f"{base}/accounts/{src}")
        assert s_acct["balance_cents"] == 0
        credited = 0
        for p in payees:
            _s, acct = http_call("GET", f"{base}/accounts/{p}")
            credited += acct["balance_cents"]
        assert credited == 100


def test_no_fractional_cent_leak():
    with running_app(_workspace()) as base:
        src = _account(base, "src")
        _credit(base, src, 100)
        payees = [_account(base, f"p{i}") for i in range(3)]
        _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
        for p in payees:
            _s, acct = http_call("GET", f"{base}/accounts/{p}")
            assert isinstance(acct["balance_cents"], int)
