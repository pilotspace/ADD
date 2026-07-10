"""Prune guards (prune-benchmark-deadweight §3 @ v1).

The hv hostile track (one-shot WV2 workload, hypothesis failed at n=1,
human-decided prune 2026-07-10) and the v1 compute_regression_rate
(superseded by _v2, zero production callers) are GONE — and stay gone.
The generic `family` seam survives; only the workload DATA was removed.
"""
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BENCH = REPO_ROOT / "benchmark"
GUARD = pathlib.Path(__file__).resolve()


def test_hv_track_absent():
    for track in ("hv1", "hv2", "hv3"):
        assert not (BENCH / "workload" / track).exists(), (
            f"workload/{track} still present — the WV2 hostile track was pruned "
            "2026-07-10 (rebuild it from git history + the WV2 ledger if ever re-funded)"
        )


def test_v1_regression_fn_absent_v2_present():
    from benchmark import score

    assert not hasattr(score, "compute_regression_rate"), (
        "v1 compute_regression_rate resurfaced — it was pruned as a zero-caller "
        "superseded path; regression scoring is compute_regression_rate_v2"
    )
    assert callable(getattr(score, "compute_regression_rate_v2", None)), (
        "compute_regression_rate_v2 must survive the prune untouched"
    )


def test_no_dangling_hv_references():
    offenders = []
    for py in BENCH.rglob("*.py"):
        if py == GUARD:
            continue
        text = py.read_text(errors="ignore")
        if re.search(r"workload/hv|hv[123]/oracle|_HV3|hv_base_pair", text):
            offenders.append(str(py.relative_to(REPO_ROOT)))
    assert not offenders, f"dangling hv-track references: {offenders}"
