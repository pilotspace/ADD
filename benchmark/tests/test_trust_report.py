"""Trust vector + two-axis report (v2-scoring-report TASK.md §3 CONTRACT @ v1).

trust.py is pure over snapshots/records/workspaces; the report is read-only
over records; the trusted flag may never print without its vector.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import textwrap

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKLOAD = REPO_ROOT / "benchmark" / "workload"


def _trust():
    import importlib

    return importlib.import_module("benchmark.trust")


def _write(root: pathlib.Path, rel: str, body: str) -> pathlib.Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body))
    return p


def _seed_snapshots(tmp_path: pathlib.Path, prior: str, current: str, family: str = "wm") -> pathlib.Path:
    arm_root = tmp_path / "runs" / "add"
    _write(arm_root, f"snapshots/{family}1/tests/test_suite.py", prior)
    _write(arm_root, f"snapshots/{family}2/tests/test_suite.py", current)
    return arm_root


_PRIOR = """
def test_a():
    assert alpha() == 1
    assert beta() == 2
    assert gamma() == 3

def test_b():
    assert delta() == 4
"""


# --------------------------------------------------------------------------
# M1 — weakened_verdict: rename-tolerant, vanished fingerprints still count
# --------------------------------------------------------------------------


def test_pure_rename_is_evolution_not_weakening(tmp_path):
    trust = _trust()
    current = """
def test_a_scoped():
    assert alpha() == 1
    assert beta() == 2
    assert gamma() == 3

def test_b():
    assert delta() == 4
"""
    arm_root = _seed_snapshots(tmp_path, _PRIOR, current)
    v = trust.weakened_verdict(arm_root, 2)
    assert v["raw_count"] >= 1  # the mechanical diff still sees a removed fn
    assert v["adjusted_count"] == 0
    assert v["verdict"] == "evolution"


def test_rename_that_drops_a_fingerprint_stays_weakened(tmp_path):
    trust = _trust()
    current = """
def test_a_scoped():
    assert alpha() == 1
    assert beta() == 2

def test_b():
    assert delta() == 4
"""
    arm_root = _seed_snapshots(tmp_path, _PRIOR, current)
    v = trust.weakened_verdict(arm_root, 2)
    assert v["adjusted_count"] == 1  # gamma()'s fingerprint vanished
    assert v["verdict"] == "weakened"


def test_untouched_suite_is_clean(tmp_path):
    trust = _trust()
    arm_root = _seed_snapshots(tmp_path, _PRIOR, _PRIOR)
    v = trust.weakened_verdict(arm_root, 2)
    assert v == {**v, "raw_count": 0, "adjusted_count": 0, "verdict": "clean"}


# --------------------------------------------------------------------------
# M2 — own_suite_status: never a fake green
# --------------------------------------------------------------------------


def test_own_suite_unverified_on_uncollectable(tmp_path):
    trust = _trust()
    ws = tmp_path / "ws"
    _write(ws, "tests/test_x.py", "import not_a_real_dep_anywhere\n\ndef test_x():\n    assert True\n")
    s = trust.own_suite_status(ws)
    assert s["status"] == "unverified"


def test_own_suite_green_on_a_passing_suite(tmp_path):
    trust = _trust()
    ws = tmp_path / "ws"
    _write(ws, "tests/test_x.py", "def test_x():\n    assert 1 + 1 == 2\n")
    s = trust.own_suite_status(ws)
    assert s["status"] == "green"


def test_own_suite_red_on_a_failing_suite(tmp_path):
    trust = _trust()
    ws = tmp_path / "ws"
    _write(ws, "tests/test_x.py", "def test_x():\n    assert 1 + 1 == 3\n")
    s = trust.own_suite_status(ws)
    assert s["status"] == "red"


# --------------------------------------------------------------------------
# M3/M4 — the vector + the two-axis headline (fixture archive)
# --------------------------------------------------------------------------


def _fixture_archive(tmp_path: pathlib.Path) -> pathlib.Path:
    """Two arms × two steps; arm 'add' all floors held, arm 'vanilla' a
    pass_rate miss at step 2 — enough to exercise trusted + untrusted paths."""
    root = tmp_path / "rep0"
    base_metrics = {
        "requirement_coverage": 0.9, "regression_rate": 0.0, "tokens_total": 1000.0,
        "cost_usd": 2.0, "context_rot_slope": 0.0, "time_to_first_edit": 10.0,
        "oracle_pass_rate": 1.0, "tests_weakened": 0.0,
    }
    for arm in ("add", "vanilla"):
        for wm in (1, 2):
            m = dict(base_metrics)
            if arm == "vanilla" and wm == 2:
                m["oracle_pass_rate"] = 0.6
            ws = root / arm / f"wm{wm}" / "workspace"
            _write(ws, "tests/test_own.py", "def test_own():\n    assert True\n")
            record = {
                "arm": arm, "wm": wm, "rep": 0, "status": "done", "metrics": m,
                "artifacts": {"workspace": str(ws), "transcript": "t", "oracle_report": ""},
            }
            _write(root, f"{arm}/wm{wm}/record.json", json.dumps(record))
            _write(root, f"{arm}/snapshots/wm{wm}/tests/test_own.py",
                   "def test_own():\n    assert value() == 1\n")
    return root


def test_trusted_returns_the_full_vector(tmp_path):
    trust = _trust()
    root = _fixture_archive(tmp_path)
    from benchmark.schema.run_record import RunRecord

    rec = RunRecord.from_json((root / "add" / "wm2" / "record.json").read_text())
    v = trust.trusted(rec, root / "add")
    for key in ("trusted", "pass_rate", "regression", "weakened_raw",
                "weakened_adjusted", "weakened_verdict", "own_tests", "own_suite"):
        assert key in v, f"vector missing {key}"
    assert v["trusted"] is True and v["own_suite"] == "green"


def test_report_prints_vector_and_two_axis_headline(tmp_path):
    from benchmark import report as report_mod

    root = _fixture_archive(tmp_path)
    out = report_mod.render_trust_report(root, arms=("add", "vanilla"), steps=(1, 2))
    assert "cost-per-trusted-feature" in out.lower()
    assert re.search(r"cost[-/]per[- ]feature", out.lower()), "v1 raw axis must print beside it"
    # the untrusted cell exists and shows WHY (the vector, not a bare flag)
    assert "0.6" in out, "vanilla's failing pass_rate must be visible in the vector"
    # caveat wherever weakened prints
    assert "caveat" in out.lower() or "evolution" in out.lower()


def test_trusted_bool_never_prints_alone(tmp_path):
    from benchmark import report as report_mod

    root = _fixture_archive(tmp_path)
    out = report_mod.render_trust_report(root, arms=("add", "vanilla"), steps=(1, 2))
    for line in out.splitlines():
        if re.search(r"\btrusted\b", line, re.I) and re.search(r"\b(true|false|yes|no)\b", line, re.I):
            assert re.search(r"\d", line), f"bare trusted flag without vector numbers: {line!r}"


def test_report_is_read_only_over_records(tmp_path):
    from benchmark import report as report_mod

    root = _fixture_archive(tmp_path)
    hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("record.json")}
    report_mod.render_trust_report(root, arms=("add", "vanilla"), steps=(1, 2))
    after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("record.json")}
    assert hashes == after


# --------------------------------------------------------------------------
# M5 — survivors disjoint windows, semantics frozen
# --------------------------------------------------------------------------


def test_wm_survivors_use_disjoint_2028_windows():
    for wm in ("wm1", "wm2"):
        body = (WORKLOAD / wm / "oracle" / "survivors.py").read_text()
        fn_bodies = re.split(r"def test_", body)[1:]
        seen: dict[str, str] = {}
        for fn in fn_bodies:
            name = fn.split("(", 1)[0]
            days = set(re.findall(r"(202[8-9]-\d{2}-\d{2})T", fn))
            legacy = re.findall(r"(2026-\d{2}-\d{2})T", fn)
            assert not legacy, f"{wm} survivors {name} still books legacy 2026 windows"
            for d in days:
                assert d not in seen, f"{wm}: day {d} shared by {seen[d]} and {name}"
                seen[d] = name
        # semantics pins stay: tokens carried
        assert "test-token-alice" in body
