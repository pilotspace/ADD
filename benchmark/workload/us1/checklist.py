"""US1 FROZEN checklist — UNDER-SPECIFIED split-payment ledger.

The prompt fixes the API shape but HIDES the semantic rules (exact
reconciliation, integer-cent rounding, leftover distribution, idempotency,
validation). So this checklist probes ONLY objectively-correct invariants that
any real payments ledger must satisfy and a sloppy one violates — money is
conserved, a split reconciles to the cent, and no sub-cent leaks. The bet: a
careful method reconciles even when unprompted; a speed-first `amount // n` per
payee silently loses cents. NO LLM in the path — deterministic.
"""
from __future__ import annotations

from benchmark.workload._oracle_lib import http_call, records


def _account(base, name="a"):
    s, b = http_call("POST", f"{base}/accounts", {"name": name})
    return b.get("id") if s in (200, 201) and isinstance(b, dict) else None


def _credit(base, aid, cents):
    return http_call("POST", f"{base}/accounts/{aid}/credit", {"amount_cents": cents})


def _transfer(base, src, amount, payees):
    return http_call("POST", f"{base}/transfers",
                     {"source_id": src, "amount_cents": amount, "payees": payees})


def _total_balance(base):
    s, accts = http_call("GET", f"{base}/accounts")
    accts = records(accts)
    if s != 200 or accts is None:
        return None
    return sum(a.get("balance_cents", 0) for a in accts if isinstance(a, dict))


def _funded(base, cents):
    src = _account(base, "src")
    if src:
        _credit(base, src, cents)
    return src


def _p_account_create(base, ws):
    s, b = http_call("POST", f"{base}/accounts", {"name": "a"})
    return s in (200, 201) and isinstance(b, dict) and bool(b.get("id"))


def _p_account_get(base, ws):
    aid = _account(base)
    s, b = http_call("GET", f"{base}/accounts/{aid}")
    return s == 200 and isinstance(b, dict) and b.get("id") == aid


def _p_account_list(base, ws):
    _account(base)
    s, b = http_call("GET", f"{base}/accounts")
    return s == 200 and records(b) is not None


def _p_account_credit(base, ws):
    aid = _account(base)
    s, b = _credit(base, aid, 500)
    return s in (200, 201) and isinstance(b, dict) and b.get("balance_cents") == 500


def _p_transfer_reconciles(base, ws):
    """THE hidden trap: 100 across three equal payees must sum back to 100 — no
    cent lost. A naive `amount // n` per payee (99) fails this."""
    src = _funded(base, 100)
    payees = [_account(base, f"p{i}") for i in range(3)]
    if not src or any(p is None for p in payees):
        return False
    s, b = _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    if s not in (200, 201) or not isinstance(b, dict):
        return False
    shares = [x.get("amount_cents") for x in b.get("splits", [])]
    return all(isinstance(x, int) for x in shares) and sum(shares) == 100


def _p_transfer_conserves(base, ws):
    """Money is neither created nor destroyed by a transfer (delta check)."""
    src = _funded(base, 100)
    payees = [_account(base, f"q{i}") for i in range(3)]
    if not src or any(p is None for p in payees):
        return False
    before = _total_balance(base)
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    after = _total_balance(base)
    return before is not None and after is not None and before == after


def _p_source_debited_exactly(base, ws):
    src = _funded(base, 100)
    payees = [_account(base, f"r{i}") for i in range(3)]
    if not src or any(p is None for p in payees):
        return False
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    _, acct = http_call("GET", f"{base}/accounts/{src}")
    return isinstance(acct, dict) and acct.get("balance_cents") == 0


def _p_payees_credited_sum_to_amount(base, ws):
    """What leaves the source equals what reaches the payees — no money created
    or lost in the move itself."""
    src = _funded(base, 100)
    payees = [_account(base, f"s{i}") for i in range(3)]
    if not src or any(p is None for p in payees):
        return False
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    credited = 0
    for p in payees:
        _, acct = http_call("GET", f"{base}/accounts/{p}")
        credited += acct.get("balance_cents", 0) if isinstance(acct, dict) else 0
    return credited == 100


def _p_clean_integer_money(base, ws):
    """Balances are whole cents — no fractional-cent leak from float division."""
    src = _funded(base, 100)
    payees = [_account(base, f"t{i}") for i in range(3)]
    if not src or any(p is None for p in payees):
        return False
    _transfer(base, src, 100, [{"account_id": p, "weight": 1} for p in payees])
    for p in payees:
        _, acct = http_call("GET", f"{base}/accounts/{p}")
        bal = acct.get("balance_cents") if isinstance(acct, dict) else None
        if not isinstance(bal, int) or isinstance(bal, bool):
            return False
    return True


def _p_entry_contract(base, ws):
    s, _ = http_call("GET", f"{base}/accounts")
    return s == 200


REQUIREMENTS = [
    {"id": "R-account-create", "description": "POST /accounts creates an account", "probe": _p_account_create},
    {"id": "R-account-get", "description": "GET /accounts/{id} fetches one account", "probe": _p_account_get},
    {"id": "R-account-list", "description": "GET /accounts lists accounts", "probe": _p_account_list},
    {"id": "R-account-credit", "description": "POST /accounts/{id}/credit funds an account", "probe": _p_account_credit},
    {"id": "R-transfer-reconciles", "description": "a split reconciles to the cent (no cent lost when unprompted)", "probe": _p_transfer_reconciles},
    {"id": "R-transfer-conserves", "description": "a transfer creates/destroys no money (conservation)", "probe": _p_transfer_conserves},
    {"id": "R-source-debited", "description": "the source is debited by exactly the amount", "probe": _p_source_debited_exactly},
    {"id": "R-payees-sum", "description": "payees collectively receive exactly the amount", "probe": _p_payees_credited_sum_to_amount},
    {"id": "R-clean-money", "description": "balances stay whole cents (no fractional-cent leak)", "probe": _p_clean_integer_money},
    {"id": "R-entry-contract", "description": "the app runs as `python -m app` on $PORT", "probe": _p_entry_contract},
]
