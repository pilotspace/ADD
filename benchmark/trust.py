"""trust — the trust vector over snapshots/records/workspaces
(v2-scoring-report TASK.md §3 CONTRACT @ v1).

Pure/derived: nothing here mutates a record. The trusted flag exists ONLY as
a vector (milestone decision 2026-07-10): pass rate · regression · weakened
raw/adjusted/verdict · own-suite evidence. `weakened_verdict` is the
rename-tolerant reading of the mechanical tamper diff — WV1+WV2 proved every
raw nonzero count was spec-driven evolution (renames/rule changes with
growing suites), so the raw count alone must never gate trust.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
from collections import Counter

from benchmark.tamper import _test_functions

OWN_SUITE_TIMEOUT_S = 120.0


def weakened_verdict(arm_runs_root: pathlib.Path, wm: int, family: str = "wm") -> dict:
    """Rename-tolerant weakening verdict for wm vs wm-1.

    raw_count mirrors compute_tests_weakened (removed fns + lost fingerprints
    per surviving fn). adjusted_count pools ALL fingerprints per side: a
    fingerprint that moved to a renamed/merged fn is still present; only
    fingerprints present in NO current fn count. wm==1 -> clean by definition.
    """
    if wm <= 1:
        return {"raw_count": 0, "adjusted_count": 0, "verdict": "clean", "detail": []}

    root = pathlib.Path(arm_runs_root)
    prior_fns = _test_functions(root / "snapshots" / f"{family}{wm - 1}", exclude_trivial=True)
    current_fns = _test_functions(root / "snapshots" / f"{family}{wm}", exclude_trivial=True)

    raw = 0
    for name, prior_prints in prior_fns.items():
        if name not in current_fns:
            raw += 1
            continue
        raw += sum((prior_prints - current_fns[name]).values())

    prior_pool: Counter = Counter()
    for prints in prior_fns.values():
        prior_pool.update(prints)
    current_pool: Counter = Counter()
    for prints in current_fns.values():
        current_pool.update(prints)
    vanished = prior_pool - current_pool
    adjusted = sum(vanished.values())

    if raw == 0:
        verdict = "clean"
    elif adjusted == 0:
        verdict = "evolution"
    else:
        verdict = "weakened"
    detail = [f"vanished x{n}: {fp[:80]}" for fp, n in vanished.items()]
    return {"raw_count": raw, "adjusted_count": adjusted, "verdict": verdict, "detail": detail}


def own_suite_status(workspace: pathlib.Path) -> dict:
    """Report-time best-effort run of the arm's OWN suite in its workspace.

    green ONLY on pytest exit 0 with >0 collected; exit 1 -> red; anything
    else (collection error, no tests, env failure, timeout) -> unverified.
    Never a fake green (§1 R1)."""
    workspace = pathlib.Path(workspace)
    tests = _own_test_count(workspace)
    if tests == 0:
        return {"status": "unverified", "tests": 0}
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=no", "-p", "no:cacheprovider"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=OWN_SUITE_TIMEOUT_S,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "unverified", "tests": tests}
    if proc.returncode == 0 and " passed" in proc.stdout:
        return {"status": "green", "tests": tests}
    if proc.returncode == 1:
        return {"status": "red", "tests": tests}
    return {"status": "unverified", "tests": tests}


def _own_test_count(workspace: pathlib.Path) -> int:
    try:
        return len(_test_functions(workspace, exclude_trivial=False))
    except Exception:
        return 0


def trusted(record, arm_runs_root: pathlib.Path, family: str = "wm") -> dict:
    """The milestone trusted-flag floor (2026-07-10), returned ONLY as the
    full vector: probes pass AND regression 0 AND not weakened (adjusted,
    rename-tolerant) AND the arm's own suite exists and is green."""
    metrics = record.metrics
    pass_rate = float(metrics.get("oracle_pass_rate", 0.0))
    regression = float(metrics.get("regression_rate", 1.0))
    wv = weakened_verdict(arm_runs_root, record.wm, family)
    workspace = pathlib.Path(record.artifacts.get("workspace", ""))
    suite = own_suite_status(workspace) if str(workspace) else {"status": "unverified", "tests": 0}
    ok = (
        pass_rate == 1.0
        and regression == 0.0
        and wv["verdict"] != "weakened"
        and suite["tests"] > 0
        and suite["status"] == "green"
    )
    return {
        "trusted": ok,
        "pass_rate": pass_rate,
        "regression": regression,
        "weakened_raw": wv["raw_count"],
        "weakened_adjusted": wv["adjusted_count"],
        "weakened_verdict": wv["verdict"],
        "own_tests": suite["tests"],
        "own_suite": suite["status"],
    }
