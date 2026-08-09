"""coverage-doctor severity agrees with the gate floor (A2, task 2).

Task 1 makes a security-without-lens a HARD gate refusal (R:NOCOVERAGE). So `doctor` reports the
same gap at `warn` for a security task, while the softer data/architecture floors stay `info` nudges.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _finding(root):
    return next(f for f in add.doctor(root) if f["code"] == "unadvised_sensitive")


def _bundle(tmp_path, sensitivity):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "a", title="a", milestone="m", sensitivity=sensitivity, scope=["a.py"])


def test_security_unadvised_is_warn(tmp_path):
    """covers: M1 — an unadvised security task's finding is severity `warn`."""
    _bundle(tmp_path, "security")
    assert _finding(tmp_path)["severity"] == "warn"


def test_architecture_unadvised_stays_info(tmp_path):
    """covers: M2, R:OVERESCALATE — an unadvised architecture task stays severity `info`."""
    _bundle(tmp_path, "architecture")
    assert _finding(tmp_path)["severity"] == "info"
