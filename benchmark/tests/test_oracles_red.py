"""Scenarios: oracle red on empty workspace / WM3 covers regression (M2)."""
import pathlib
import subprocess
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _oracle_dir(wm: int, family: str = "wm") -> pathlib.Path:
    return ROOT / "workload" / f"{family}{wm}" / "oracle"


# (family, index) — the wm longitudinal track plus the hv hard cross-domain track.
@pytest.mark.parametrize(
    "family,wm",
    [("wm", 1), ("wm", 2), ("wm", 3), ("hv", 1), ("hv", 2), ("hv", 3), ("hv", 4)],
)
def test_oracles_red_on_empty_workspace(family, wm):
    oracle_dir = _oracle_dir(wm, family)
    if not oracle_dir.exists():
        pytest.fail(f"missing oracle dir {oracle_dir}")
    with tempfile.TemporaryDirectory() as empty_ws:
        env = {**__import__("os").environ, "BENCH_WORKSPACE": empty_ws}
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(oracle_dir), "-q", "--no-header"],
            capture_output=True,
            text=True,
            env=env,
        )
        # Collection must succeed (no collection ERRORS section) and every test must fail.
        assert "errors during collection" not in proc.stdout.lower(), proc.stdout
        assert proc.returncode != 0, f"expected red run against empty workspace, got:\n{proc.stdout}"
        assert " passed" not in proc.stdout, proc.stdout
        assert "failed" in proc.stdout, proc.stdout


def test_wm3_oracle_includes_regression_reexports():
    oracle_dir = _oracle_dir(3)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(oracle_dir), "--collect-only", "-q"],
        capture_output=True,
        text=True,
    )
    collected = proc.stdout
    assert "wm1" in collected.lower(), collected
    assert "wm2" in collected.lower(), collected
    assert "regression" in collected.lower(), collected
