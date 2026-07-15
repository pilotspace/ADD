"""HV3 must-survive invariants — the auth/rate-limit LAWS that outlive hv4.

Re-run against the hv4 workspace (resilient settlement + input hardening).
KEY-CARRYING and kept to a handful of calls, well under the bucket. LAW-TOLERANT:
probe only invariants that never change — a mutation needs a valid key, reads are
open, and a keyed transfer still reconciles. Never visible to the arm.
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


def _account(base):
    status, body = http_call("POST", f"{base}/accounts", {"name": "a"}, headers=_KEY)
    assert status in (200, 201), body
    return body["id"]


def test_mutation_requires_a_valid_key():
    with running_app(_workspace()) as base:
        assert http_call("POST", f"{base}/accounts", {"name": "a"})[0] == 401


def test_reads_stay_open():
    with running_app(_workspace()) as base:
        status, body = http_call("GET", f"{base}/accounts")
        assert status == 200 and isinstance(body, list)


def test_keyed_transfer_reconciles():
    with running_app(_workspace()) as base:
        src = _account(base)
        http_call("POST", f"{base}/accounts/{src}/credit", {"amount_cents": 100}, headers=_KEY)
        a, b = _account(base), _account(base)
        status, body = http_call("POST", f"{base}/transfers",
                                 {"source_id": src, "amount_cents": 100,
                                  "payees": [{"account_id": a, "weight": 1}, {"account_id": b, "weight": 1}]}, headers=_KEY)
        assert status in (200, 201), body
        assert sum(s["amount_cents"] for s in body["splits"]) == 100
