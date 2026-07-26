"""US1 must-survive invariants (structural — only re-run if a us2+ is added).
Money conservation is the law that never changes. Never visible to the arm.
"""
import os

import pytest

from benchmark.workload._oracle_lib import http_call, running_app


def _workspace() -> str:
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    return ws


def test_split_reconciles():
    with running_app(_workspace()) as base:
        _s, src = http_call("POST", f"{base}/accounts", {"name": "src"})
        src = src["id"]
        http_call("POST", f"{base}/accounts/{src}/credit", {"amount_cents": 100})
        payees = []
        for i in range(3):
            _s, a = http_call("POST", f"{base}/accounts", {"name": f"p{i}"})
            payees.append(a["id"])
        s, b = http_call("POST", f"{base}/transfers",
                         {"source_id": src, "amount_cents": 100,
                          "payees": [{"account_id": p, "weight": 1} for p in payees]})
        assert s in (200, 201), b
        assert sum(x["amount_cents"] for x in b["splits"]) == 100
