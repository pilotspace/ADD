"""Prune guards (prune-benchmark-deadweight §3 @ v1; hv track RE-FUNDED 2026-07-15).

History: the hv slot was first a one-shot WV2 hostile experiment whose
hypothesis failed at n=1 (human-decided prune 2026-07-10). On 2026-07-15 the
human re-funded the hv slot with a DIFFERENT purpose — a longitudinal, hard
cross-domain track (a split-payment ledger: money-split -> pricing -> rate
limit -> resilient settlement) to POSITION ADD vs spec-kit vs gsd. So the hv
workload DATA is now present by design; what stays pruned is (a) the v1
compute_regression_rate (superseded by _v2, zero callers) and (b) the OLD
WV2-specific dead symbols (`_HV3`, `hv_base_pair`). The generic `family` seam
always survived.
"""
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BENCH = REPO_ROOT / "benchmark"
GUARD = pathlib.Path(__file__).resolve()


def test_hv_track_present_and_real():
    # the re-funded hv longitudinal track — hv1 is the ledger core. Each present
    # milestone must be a REAL workload (prompt + checklist + oracle), never an
    # empty stub, so scoring resolves exactly like the wm track.
    hv1 = BENCH / "workload" / "hv1"
    assert hv1.exists(), "workload/hv1 missing — the hv track was re-funded 2026-07-15"
    assert (hv1 / "PROMPT.md").exists(), "hv1 PROMPT.md missing"
    assert (hv1 / "checklist.py").exists(), "hv1 checklist.py missing"
    assert (hv1 / "oracle" / "survivors.py").exists(), "hv1 survivors.py missing"
    oracle_tests = list((hv1 / "oracle").glob("test_*.py"))
    assert oracle_tests, "hv1 oracle has no test_*.py suite"


def test_v1_regression_fn_absent_v2_present():
    from benchmark import score

    assert not hasattr(score, "compute_regression_rate"), (
        "v1 compute_regression_rate resurfaced — it was pruned as a zero-caller "
        "superseded path; regression scoring is compute_regression_rate_v2"
    )
    assert callable(getattr(score, "compute_regression_rate_v2", None)), (
        "compute_regression_rate_v2 must survive the prune untouched"
    )


def test_old_wv2_dead_symbols_stay_gone():
    # the REVIVED track reuses the generic `hv` family, but the OLD WV2-specific
    # dead symbols (`_HV3`, `hv_base_pair`) must never resurface.
    offenders = []
    for py in BENCH.rglob("*.py"):
        if py == GUARD:
            continue
        text = py.read_text(errors="ignore")
        if re.search(r"_HV3|hv_base_pair", text):
            offenders.append(str(py.relative_to(REPO_ROOT)))
    assert not offenders, f"dead WV2 hv symbols resurfaced: {offenders}"
