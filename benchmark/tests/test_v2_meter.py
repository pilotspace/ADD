"""v2 meter fixes — deterministic fidelity primary, generalized regression
oracle, mechanical tamper detector, pinned judge (v2-meter-fixes TASK.md §3
CONTRACT @ v1; M1-M8, R1-R5).

Hermetic where a subprocess would spawn pytest/claude (monkeypatched run
seam or injected fake-judge argv); real files for every tamper/snapshot
test (tamper is pure ast + file copies — no subprocess belongs there).

`benchmark.tamper` and the new score/schema symbols are imported LAZILY
inside each test so the suite runs RED test-by-test on the missing
implementation instead of dying at collection.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import sys
import textwrap
import types

import pytest

from benchmark import judge as judge_mod
from benchmark import score as score_mod
from benchmark.schema.run_record import BenchError, validate

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _tamper():
    return importlib.import_module("benchmark.tamper")


def _fake_pytest_result(stdout: str, returncode: int) -> types.SimpleNamespace:
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")


def _patch_pytest_run(monkeypatch, stdout: str, returncode: int, calls: list | None = None):
    """Patch score_mod's subprocess.run seam with a canned pytest summary."""

    def fake_run(argv, **kwargs):
        if calls is not None:
            calls.append((list(argv), dict(kwargs)))
        return _fake_pytest_result(stdout, returncode)

    monkeypatch.setattr(score_mod.subprocess, "run", fake_run)


def _write_tests(root: pathlib.Path, rel: str, body: str) -> pathlib.Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body))
    return path


def _fake_judge(tmp_path: pathlib.Path, value: str) -> list[str]:
    script = tmp_path / "fake_judge.py"
    script.write_text(f"#!/usr/bin/env python3\nprint({value!r})\n")
    script.chmod(0o755)
    return [sys.executable, str(script)]


_BASE_METRICS = {
    "regression_rate": 0.0,
    "spec_fidelity": 0.5,
    "tokens_total": 4200.0,
    "cost_usd": 0.31,
    "context_rot_slope": 0.0,
    "time_to_first_edit": 12.5,
}


def _record_dict(metrics: dict) -> dict:
    return {
        "arm": "add",
        "wm": 1,
        "rep": 0,
        "status": "done",
        "metrics": metrics,
        "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"},
    }


# --------------------------------------------------------------------------
# M1 — compute_oracle_pass_rate
# --------------------------------------------------------------------------


def test_oracle_pass_rate_partial(monkeypatch):
    calls: list = []
    _patch_pytest_run(monkeypatch, "3 passed, 1 failed in 2.1s", 1, calls)
    rate = score_mod.compute_oracle_pass_rate(pathlib.Path("/tmp/ws"), 1)
    assert rate == 0.75
    # deterministic: the identical seam yields the identical value
    assert score_mod.compute_oracle_pass_rate(pathlib.Path("/tmp/ws"), 1) == 0.75
    # the WM's OWN oracle dir is what runs
    argv = calls[0][0]
    assert any("wm1" in str(part) and "oracle" in str(part) for part in argv)


def test_oracle_pass_rate_deselects_regression_reexports(monkeypatch):
    """Live defect 2026-07-10 (WV1 rep0, meter defect #4): wm3's oracle dir
    re-exports the wm1+wm2 suites for the v1 regression path; 7 of them are
    `legacy_shape`-marked BY-CONSTRUCTION failures on a correct wm3 app
    (they send the duration_minutes payloads wm3's own contract forces every
    arm to reject). Collected unfiltered, the denominator became 12 and the
    fidelity ceiling 0.42 — add, add-main and spec-kit all scored an identical
    artifact 0.25. Fidelity of record = the WM's OWN probes only: the marked
    re-exports must be deselected."""
    calls: list = []
    _patch_pytest_run(monkeypatch, "2 passed in 0.5s", 0, calls)
    score_mod.compute_oracle_pass_rate(pathlib.Path("/tmp/ws"), 3)
    argv = [str(part) for part in calls[0][0]]
    # the interpreter prefix is `python -m pytest` — look for the MARKER -m,
    # i.e. an adjacent pair ("-m", <expr containing the deselections>)
    marker_exprs = [argv[i + 1] for i, tok in enumerate(argv[:-1]) if tok == "-m"]
    assert any(
        "not regression" in expr and "not legacy_shape" in expr for expr in marker_exprs
    ), f"no marker filter in argv: regression re-exports poison the denominator ({argv})"


def test_wm3_oracle_own_probes_collect_exactly_two():
    """The live denominator guard: under the marker filter the wm3 oracle dir
    must collect exactly its 2 native shape probes — an UNMARKED re-export
    added later would silently poison the fidelity denominator again."""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-m", "not regression and not legacy_shape",
         str(REPO_ROOT / "benchmark" / "workload" / "wm3" / "oracle")],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    assert "2/12 tests collected" in proc.stdout, proc.stdout[-400:]


def test_oracle_pass_rate_unbootable_zero(tmp_path):
    # REAL subprocess: empty workspace -> `python -m app` dies -> every probe
    # fails as an ordinary connection AssertionError -> 0.0, never a crash.
    workspace = tmp_path / "empty_ws"
    workspace.mkdir()
    assert score_mod.compute_oracle_pass_rate(workspace, 1) == 0.0


def test_oracle_zero_collection_raises(monkeypatch):
    _patch_pytest_run(monkeypatch, "no tests ran in 0.01s", 5)
    with pytest.raises(BenchError, match="^oracle_run_failed"):
        score_mod.compute_oracle_pass_rate(pathlib.Path("/tmp/ws"), 1)


# --------------------------------------------------------------------------
# M2 — compute_regression_rate_v2
# --------------------------------------------------------------------------


def test_regression_v2_reruns_earlier_suites(monkeypatch):
    calls: list = []
    _patch_pytest_run(monkeypatch, "6 passed, 2 failed in 3.0s", 1, calls)
    rate = score_mod.compute_regression_rate_v2(pathlib.Path("/tmp/ws"), 3)
    assert rate == 0.25
    joined = " ".join(str(part) for part in calls[0][0])
    assert "wm1" in joined and "wm2" in joined  # ALL earlier suites re-run
    assert "wm3" not in joined  # the current WM's own suite is fidelity, not regression


def test_regression_v2_wm1_zero_no_spawn(monkeypatch):
    def boom(argv, **kwargs):  # any spawn is a contract violation at wm==1
        raise AssertionError("wm==1 must not spawn pytest")

    monkeypatch.setattr(score_mod.subprocess, "run", boom)
    assert score_mod.compute_regression_rate_v2(pathlib.Path("/tmp/ws"), 1) == 0.0


def test_regression_v2_zero_collection_raises(monkeypatch):
    _patch_pytest_run(monkeypatch, "no tests ran in 0.01s", 5)
    with pytest.raises(BenchError, match="^regression_run_failed"):
        score_mod.compute_regression_rate_v2(pathlib.Path("/tmp/ws"), 2)


# --------------------------------------------------------------------------
# M3 — snapshot_tests
# --------------------------------------------------------------------------


def test_snapshot_copies_test_files(tmp_path):
    tamper = _tamper()
    workspace = tmp_path / "ws"
    _write_tests(workspace, "tests/test_a.py", "def test_x():\n    assert 1 == 1\n")
    _write_tests(workspace, "deep/nested/test_b.py", "def test_y():\n    assert True\n")
    _write_tests(workspace, "foo_test.py", "def test_z():\n    assert 2 > 1\n")
    _write_tests(workspace, ".venv/lib/test_junk.py", "def test_junk():\n    assert 0\n")
    _write_tests(workspace, "__pycache__/test_cache.py", "def test_c():\n    assert 0\n")
    (workspace / "app.py").write_text("APP = 1\n")

    arm_root = tmp_path / "runs" / "add"
    dest = tamper.snapshot_tests(workspace, arm_root, 1)

    assert dest == arm_root / "snapshots" / "wm1"
    copied = sorted(str(p.relative_to(dest)) for p in dest.rglob("*.py"))
    assert copied == ["deep/nested/test_b.py", "foo_test.py", "tests/test_a.py"]


# --------------------------------------------------------------------------
# M4 — compute_tests_weakened (pure ast fingerprint diff)
# --------------------------------------------------------------------------

_WM1_SUITE = """
def test_one():
    assert alpha() == 1
    assert beta() == 2
    assert gamma() == 3

def test_two():
    assert delta() == 4
    assert epsilon() == 5

def test_three():
    assert zeta() == 6
    assert eta() == 7
    assert theta() == 8

def test_four():
    assert iota() == 9
    assert kappa() == 10

def test_five():
    assert lam() == 11
    assert mu() == 12
"""

# wm2: test_five deleted (-1 fn), test_one lost 2 asserts (-2) -> 3
_WM2_SUITE = """
def test_one():
    assert alpha() == 1

def test_two():
    assert delta() == 4
    assert epsilon() == 5

def test_three():
    assert zeta() == 6
    assert eta() == 7
    assert theta() == 8

def test_four():
    assert iota() == 9
    assert kappa() == 10
"""


def _seed_snapshots(tmp_path: pathlib.Path, wm1_body: str, wm2_body: str) -> pathlib.Path:
    arm_root = tmp_path / "runs" / "add"
    _write_tests(arm_root, "snapshots/wm1/tests/test_suite.py", wm1_body)
    _write_tests(arm_root, "snapshots/wm2/tests/test_suite.py", wm2_body)
    return arm_root


def test_tests_weakened_counts_removals(tmp_path):
    tamper = _tamper()
    arm_root = _seed_snapshots(tmp_path, _WM1_SUITE, _WM2_SUITE)
    assert tamper.compute_tests_weakened(arm_root, 2) == 3


def test_tests_weakened_counts_replacement(tmp_path):
    tamper = _tamper()
    arm_root = _seed_snapshots(
        tmp_path,
        "def test_one():\n    assert resp_status() == 409\n",
        "def test_one():\n    assert resp_status() != 500\n",
    )
    assert tamper.compute_tests_weakened(arm_root, 2) == 1


def test_trivial_assert_no_credit(tmp_path):
    tamper = _tamper()
    arm_root = _seed_snapshots(
        tmp_path,
        "def test_one():\n    assert conflict_rejected() == 409\n"
        "def test_two():\n    assert listing() == 200\n",
        "def test_one():\n    assert True\n"
        "def test_two():\n    assert listing() == 200\n",
    )
    # test_one's real fingerprint is gone (1); `assert True` earns no credit;
    # untouched test_two contributes 0.
    assert tamper.compute_tests_weakened(arm_root, 2) == 1


def test_tests_weakened_unchanged_suite_is_zero(tmp_path):
    tamper = _tamper()
    arm_root = _seed_snapshots(tmp_path, _WM1_SUITE, _WM1_SUITE)
    assert tamper.compute_tests_weakened(arm_root, 2) == 0


def test_tests_weakened_wm1_zero(tmp_path):
    tamper = _tamper()
    assert tamper.compute_tests_weakened(tmp_path / "runs" / "add", 1) == 0


def test_missing_snapshot_raises(tmp_path):
    tamper = _tamper()
    arm_root = tmp_path / "runs" / "add"
    _write_tests(arm_root, "snapshots/wm2/tests/test_suite.py", "def test_a():\n    assert f() == 1\n")
    with pytest.raises(BenchError, match="^missing_test_snapshot"):
        tamper.compute_tests_weakened(arm_root, 2)


# --------------------------------------------------------------------------
# M5 — judge pin
# --------------------------------------------------------------------------


def test_judge_pinned_model():
    argv = judge_mod.build_judge_argv("rate this", None)
    assert argv[:2] == ["claude", "-p"]
    assert "rate this" in argv
    idx = argv.index("--model")
    assert argv[idx + 1] == "claude-sonnet-5"


def test_injected_judge_cmd_unchanged(tmp_path):
    fake = _fake_judge(tmp_path, "0.9")
    argv = judge_mod.build_judge_argv("rate this", fake)
    assert argv == [*fake, "rate this"]  # injection seam byte-stable, no pin appended


# --------------------------------------------------------------------------
# M6 / R4 — record schema v2 (additive-optional)
# --------------------------------------------------------------------------


def test_v1_records_still_validate():
    record = validate(_record_dict(dict(_BASE_METRICS)))
    assert record.metrics == _BASE_METRICS
    # every archived v1 record on disk still loads byte-unchanged
    archived = sorted((REPO_ROOT / "benchmark" / "runs").rglob("record.json"))
    for path in archived:
        validate(json.loads(path.read_text()))


def test_optional_keys_accepted():
    metrics = {**_BASE_METRICS, "oracle_pass_rate": 0.75, "tests_weakened": 3.0}
    record = validate(_record_dict(metrics))
    assert record.metrics["oracle_pass_rate"] == 0.75
    assert record.metrics["tests_weakened"] == 3.0
    # one optional key alone is also fine (subset semantics)
    validate(_record_dict({**_BASE_METRICS, "oracle_pass_rate": 1.0}))


def test_unknown_metric_key_rejected():
    with pytest.raises(BenchError, match="invalid_run_record"):
        validate(_record_dict({**_BASE_METRICS, "bogus": 1.0}))


# --------------------------------------------------------------------------
# M7 — score_record writes the v2 metrics
# --------------------------------------------------------------------------


def test_score_record_writes_v2_metrics(tmp_path, monkeypatch):
    tamper = _tamper()
    runs_root = tmp_path / "runs"
    wm_dir = runs_root / "add" / "wm2"
    workspace = wm_dir / "workspace"
    _write_tests(workspace, "tests/test_suite.py", "def test_a():\n    assert f() == 1\n")
    (wm_dir / "transcript.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (wm_dir / "transcript.jsonl").write_text("")
    (wm_dir / "oracle_report.json").write_text(
        json.dumps({"app_check": {"app_reachable": True}, "isolation_clean": True})
    )
    record = validate(
        {
            "arm": "add",
            "wm": 2,
            "rep": 0,
            "status": "done",
            "metrics": dict(_BASE_METRICS),
            "artifacts": {
                "workspace": str(workspace),
                "transcript": str(wm_dir / "transcript.jsonl"),
                "oracle_report": str(wm_dir / "oracle_report.json"),
            },
        }
    )
    (wm_dir / "record.json").write_text(record.to_json())

    # both snapshots present -> tests_weakened computable (pure ast, real files)
    tamper.snapshot_tests(workspace, runs_root / "add", 1)
    tamper.snapshot_tests(workspace, runs_root / "add", 2)

    # deterministic seams: no live pytest / claude in this wiring test
    monkeypatch.setattr(score_mod, "compute_oracle_pass_rate", lambda ws, wm: 0.75)
    monkeypatch.setattr(score_mod, "compute_regression_rate_v2", lambda ws, wm: 0.125)

    scored = score_mod.score_record("add", 2, judge_cmd=_fake_judge(tmp_path, "0.9"), runs_root=runs_root)

    assert scored.metrics["oracle_pass_rate"] == 0.75
    assert scored.metrics["tests_weakened"] == 0.0
    assert scored.metrics["regression_rate"] == 0.125
    assert scored.metrics["spec_fidelity"] == 0.9  # kept, judge-sourced, secondary
    assert scored.artifacts["regression_source"] == "v2-earlier-oracles"
    # the written record round-trips through validate
    validate(json.loads((wm_dir / "record.json").read_text()))


# --------------------------------------------------------------------------
# M8 — run_pilot snapshots after every done WM
# --------------------------------------------------------------------------


def _pilot_record(runs_root: pathlib.Path, wm: int, status: str) -> "object":
    from benchmark.pilot import RunRecord  # the frozen shape, reused

    wm_dir = runs_root / "add" / f"wm{wm}"
    workspace = wm_dir / "workspace"
    _write_tests(workspace, "tests/test_suite.py", "def test_a():\n    assert f() == 1\n")
    return RunRecord(
        arm="add",
        wm=wm,
        rep=0,
        status=status,
        metrics=dict(_BASE_METRICS),
        artifacts={
            "workspace": str(workspace),
            "transcript": str(wm_dir / "transcript.jsonl"),
            "oracle_report": str(wm_dir / "oracle_report.json"),
        },
    )


def test_pilot_snapshots_after_done_wm(tmp_path, monkeypatch):
    from benchmark import pilot as pilot_mod

    runs_root = tmp_path / "runs"
    record = _pilot_record(runs_root, 1, "done")
    monkeypatch.setattr(pilot_mod, "execute_wm", lambda *a, **k: record)
    monkeypatch.setattr(pilot_mod, "score_record", lambda *a, **k: record)

    pilot_mod.run_pilot(arms=("add",), wms=(1,), resume=False, runs_root=runs_root)

    snap = runs_root / "add" / "snapshots" / "wm1"
    assert snap.is_dir()
    assert list(snap.rglob("test_suite.py"))


def test_pilot_no_snapshot_on_failed_wm(tmp_path, monkeypatch):
    from benchmark import pilot as pilot_mod

    runs_root = tmp_path / "runs"
    record = _pilot_record(runs_root, 1, "timeout")
    monkeypatch.setattr(pilot_mod, "execute_wm", lambda *a, **k: record)
    monkeypatch.setattr(
        pilot_mod, "score_record", lambda *a, **k: pytest.fail("failed WM must not score")
    )

    pilot_mod.run_pilot(arms=("add",), wms=(1,), resume=False, runs_root=runs_root)

    assert not (runs_root / "add" / "snapshots").exists()
