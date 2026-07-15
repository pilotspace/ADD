"""HV1 FROZEN requirement checklist — the deterministic fidelity of record.

One row per enumerated requirement in hv1/PROMPT.md. `compute_coverage_detail`
(benchmark/score.py) boots the built app once and runs each row's
`probe(base, workspace)`; coverage = covered / total. A probe returns True iff
the built app satisfies that requirement. NO LLM anywhere — identical workspace
yields the identical score.

The split-payment domain is chosen to DISCRIMINATE: a naive implementation
(float money, per-payee `round(amount/n)`, no leftover distribution, no
idempotency) boots and looks plausible but loses/creates cents and double-debits
— exactly what these probes catch and casual inspection does not.

FROZEN: adding/removing a row is a deliberate versioned change (it moves every
arm's coverage denominator). Each `id` is stable — reports key off it.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from benchmark.workload._oracle_lib import http_call


def _account(base: str, name: str = "acct") -> str | None:
    status, body = http_call("POST", f"{base}/accounts", {"name": name})
    if status not in (200, 201) or not isinstance(body, dict):
        return None
    return body.get("id")


def _credit(base: str, acct_id: str, cents: int) -> tuple[int, dict]:
    return http_call("POST", f"{base}/accounts/{acct_id}/credit", {"amount_cents": cents})


def _transfer(base: str, source_id: str, amount: int, payees: list[dict], headers=None):
    return http_call(
        "POST",
        f"{base}/transfers",
        {"source_id": source_id, "amount_cents": amount, "payees": payees},
        headers=headers,
    )


def _funded_source(base: str, cents: int) -> str | None:
    src = _account(base, "source")
    if not src:
        return None
    status, _ = _credit(base, src, cents)
    return src if status in (200, 201) else None


def _three_payees(base: str) -> list[str]:
    ids = [_account(base, f"p{i}") for i in range(3)]
    return [i for i in ids if i]


def _p_account_create(base, ws):
    status, body = http_call("POST", f"{base}/accounts", {"name": "acct"})
    return status in (200, 201) and isinstance(body, dict) and bool(body.get("id")) and body.get("balance_cents") == 0


def _p_account_get(base, ws):
    aid = _account(base)
    status, body = http_call("GET", f"{base}/accounts/{aid}")
    return status == 200 and body.get("id") == aid


def _p_account_credit(base, ws):
    aid = _account(base)
    status, body = _credit(base, aid, 500)
    return status in (200, 201) and body.get("balance_cents") == 500


def _p_transfer_reconciles(base, ws):
    """The core money-split invariant: shares sum EXACTLY to amount_cents, and
    100 across three equal-weight payees is [34, 33, 33] (payee 0 wins the tie)."""
    src = _funded_source(base, 100)
    payees = _three_payees(base)
    if not src or len(payees) != 3:
        return False
    status, body = _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    if status not in (200, 201) or not isinstance(body, dict):
        return False
    splits = body.get("splits") or []
    shares = [s.get("amount_cents") for s in splits]
    return sum(shares) == 100 and sorted(shares, reverse=True) == [34, 33, 33]


def _p_transfer_deterministic_tie(base, ws):
    """The leftover cent goes to the LOWEST-index payee on a tie: exactly
    [34, 33, 33] in payee order, not any permutation."""
    src = _funded_source(base, 100)
    payees = _three_payees(base)
    if not src or len(payees) != 3:
        return False
    status, body = _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    if status not in (200, 201):
        return False
    shares = [s.get("amount_cents") for s in (body.get("splits") or [])]
    return shares == [34, 33, 33]


def _p_transfer_proportional(base, ws):
    """Weights [2, 1] over 100 → [67, 33], summing to 100."""
    src = _funded_source(base, 100)
    payees = _three_payees(base)[:2]
    if not src or len(payees) != 2:
        return False
    status, body = _transfer(
        base, src, 100,
        [{"account_id": payees[0], "weight": 2}, {"account_id": payees[1], "weight": 1}],
    )
    if status not in (200, 201):
        return False
    shares = [s.get("amount_cents") for s in (body.get("splits") or [])]
    return shares == [67, 33]


def _p_credits_land_on_payees(base, ws):
    """Each payee's balance actually increases by its share."""
    src = _funded_source(base, 100)
    payees = _three_payees(base)
    if not src or len(payees) != 3:
        return False
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    _, first = http_call("GET", f"{base}/accounts/{payees[0]}")
    return isinstance(first, dict) and first.get("balance_cents") == 34


def _p_source_debited(base, ws):
    src = _funded_source(base, 100)
    payees = _three_payees(base)
    if not src or len(payees) != 3:
        return False
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    _, acct = http_call("GET", f"{base}/accounts/{src}")
    return isinstance(acct, dict) and acct.get("balance_cents") == 0


def _p_insufficient_409(base, ws):
    src = _funded_source(base, 50)
    payees = _three_payees(base)[:1]
    if not src or not payees:
        return False
    status, _ = _transfer(base, src, 100, [{"account_id": payees[0], "weight": 1}])
    if status != 409:
        return False
    _, acct = http_call("GET", f"{base}/accounts/{src}")  # no partial debit
    return isinstance(acct, dict) and acct.get("balance_cents") == 50


def _p_idempotent_replay(base, ws):
    src = _funded_source(base, 100)
    payees = _three_payees(base)[:1]
    if not src or not payees:
        return False
    body = {"source_id": src, "amount_cents": 40, "payees": [{"account_id": payees[0], "weight": 1}]}
    hdr = {"Idempotency-Key": "hv1-replay"}
    s1, b1 = http_call("POST", f"{base}/transfers", body, headers=hdr)
    s2, b2 = http_call("POST", f"{base}/transfers", body, headers=hdr)
    if s1 not in (200, 201) or s2 not in (200, 201):
        return False
    if not isinstance(b1, dict) or not isinstance(b2, dict) or b1.get("id") != b2.get("id"):
        return False
    _, acct = http_call("GET", f"{base}/accounts/{src}")  # debited ONCE
    return isinstance(acct, dict) and acct.get("balance_cents") == 60


def _p_idempotent_conflict(base, ws):
    src = _funded_source(base, 100)
    payees = _three_payees(base)[:1]
    if not src or not payees:
        return False
    hdr = {"Idempotency-Key": "hv1-conflict"}
    http_call("POST", f"{base}/transfers",
              {"source_id": src, "amount_cents": 40, "payees": [{"account_id": payees[0], "weight": 1}]}, headers=hdr)
    status, _ = http_call("POST", f"{base}/transfers",
                          {"source_id": src, "amount_cents": 41, "payees": [{"account_id": payees[0], "weight": 1}]}, headers=hdr)
    return status == 409


def _p_integer_money(base, ws):
    """Balances are integers, never floats — 1/3 splits must not leak a float."""
    aid = _account(base)
    _, body = _credit(base, aid, 100)
    bal = body.get("balance_cents")
    return isinstance(bal, int) and not isinstance(bal, bool)


def _p_unknown_account_404(base, ws):
    payees = _three_payees(base)[:1]
    status, _ = _transfer(base, "does-not-exist", 10, [{"account_id": payees[0], "weight": 1}] if payees else [{"account_id": "x", "weight": 1}])
    return status == 404


def _p_bad_amount_400(base, ws):
    src = _funded_source(base, 100)
    payees = _three_payees(base)[:1]
    if not src or not payees:
        return False
    zero, _ = _transfer(base, src, 0, [{"account_id": payees[0], "weight": 1}])
    neg, _ = _transfer(base, src, -5, [{"account_id": payees[0], "weight": 1}])
    return zero == 400 and neg == 400


def _p_empty_payees_400(base, ws):
    src = _funded_source(base, 100)
    if not src:
        return False
    status, _ = _transfer(base, src, 10, [])
    return status == 400


def _total_balance(base) -> int | None:
    status, accts = http_call("GET", f"{base}/accounts")
    if status != 200 or not isinstance(accts, list):
        return None
    return sum(a.get("balance_cents", 0) for a in accts if isinstance(a, dict))


def _p_conservation(base, ws):
    """No money created or destroyed: a transfer only MOVES cents, so the sum of
    all account balances is unchanged across it (a delta check — robust to the
    single shared app boot that other probes have already funded)."""
    src = _funded_source(base, 100)
    payees = _three_payees(base)
    if not src or len(payees) != 3:
        return False
    before = _total_balance(base)
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    after = _total_balance(base)
    return before is not None and after is not None and before == after


def _p_cli_parity(base, ws):
    """The PROMPT requires a CLI listing accounts via the same store. Try the
    common entry points; success = one exits 0 for a list command."""
    port = base.rsplit(":", 1)[-1]
    env = {**os.environ, "APP_BASE": base, "PORT": port}
    invocations = (
        [sys.executable, "-m", "app.cli", "list-accounts"],
        [sys.executable, "-m", "cli", "list-accounts"],
        [sys.executable, "cli.py", "list-accounts"],
        [sys.executable, "-m", "app.cli", "list"],
        [sys.executable, "-m", "app", "list-accounts"],
    )
    for argv in invocations:
        try:
            proc = subprocess.run(argv, cwd=str(ws), env=env, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            continue
        if proc.returncode == 0:
            return True
    return False


def _p_entry_contract(base, ws):
    status, _ = http_call("GET", f"{base}/accounts")
    return status == 200


REQUIREMENTS = [
    {"id": "R-account-create", "description": "POST /accounts creates an account with balance_cents 0", "probe": _p_account_create},
    {"id": "R-account-get", "description": "GET /accounts/{id} fetches one account", "probe": _p_account_get},
    {"id": "R-account-credit", "description": "POST /accounts/{id}/credit funds an account", "probe": _p_account_credit},
    {"id": "R-transfer-reconciles", "description": "a split transfer's shares sum exactly to amount_cents", "probe": _p_transfer_reconciles},
    {"id": "R-transfer-deterministic-tie", "description": "the leftover cent breaks ties to the lowest-index payee ([34,33,33])", "probe": _p_transfer_deterministic_tie},
    {"id": "R-transfer-proportional", "description": "shares are proportional to integer weights ([67,33] for [2,1])", "probe": _p_transfer_proportional},
    {"id": "R-credits-land", "description": "each payee balance increases by its share", "probe": _p_credits_land_on_payees},
    {"id": "R-source-debited", "description": "the source balance decreases by amount_cents", "probe": _p_source_debited},
    {"id": "R-insufficient-409", "description": "a transfer over the source balance is 409 with no partial debit", "probe": _p_insufficient_409},
    {"id": "R-idempotent-replay", "description": "same Idempotency-Key + body replays the original transfer, debits once", "probe": _p_idempotent_replay},
    {"id": "R-idempotent-conflict", "description": "same Idempotency-Key + different body is 409", "probe": _p_idempotent_conflict},
    {"id": "R-integer-money", "description": "balances are integer cents, never floats", "probe": _p_integer_money},
    {"id": "R-unknown-account-404", "description": "a transfer from an unknown account is 404", "probe": _p_unknown_account_404},
    {"id": "R-bad-amount-400", "description": "non-positive amount_cents is 400", "probe": _p_bad_amount_400},
    {"id": "R-empty-payees-400", "description": "an empty payees array is 400", "probe": _p_empty_payees_400},
    {"id": "R-conservation", "description": "no money is created or destroyed across credits and transfers", "probe": _p_conservation},
    {"id": "R-cli-parity", "description": "a CLI lists accounts via the same underlying logic", "probe": _p_cli_parity},
    {"id": "R-entry-contract", "description": "the app runs as `python -m app` serving HTTP on $PORT", "probe": _p_entry_contract},
]
