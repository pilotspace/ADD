"""Scenarios: oracle leak is loud / run outputs never committed (M5, R:oracle_leak)."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
CHECK_ISOLATION = ROOT / "check_isolation.py"


def test_oracle_leak_detected_even_renamed(tmp_path):
    wm1_oracle_dir = ROOT / "workload" / "wm1" / "oracle"
    oracle_files = sorted(wm1_oracle_dir.glob("test_*.py"))
    assert oracle_files, "no wm1 oracle files found to leak"
    leaked = tmp_path / "totally_renamed_helper.py"
    shutil.copyfile(oracle_files[0], leaked)

    proc = subprocess.run(
        [sys.executable, str(CHECK_ISOLATION), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "oracle_leak" in (proc.stdout + proc.stderr)
    assert str(leaked) in (proc.stdout + proc.stderr) or leaked.name in (proc.stdout + proc.stderr)


def test_clean_workspace_exits_zero(tmp_path):
    (tmp_path / "app.py").write_text("# clean workspace file\n")
    proc = subprocess.run(
        [sys.executable, str(CHECK_ISOLATION), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_runs_dir_gitignored():
    runs_probe_dir = REPO_ROOT / "benchmark" / "runs"
    runs_probe_dir.mkdir(parents=True, exist_ok=True)
    probe = runs_probe_dir / "probe.tmp"
    probe.write_text("probe\n")
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "benchmark/runs"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert "probe.tmp" not in proc.stdout, proc.stdout
    finally:
        probe.unlink(missing_ok=True)
