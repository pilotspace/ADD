"""The repository's actual orientation must lead to observable ADD state."""
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))
sys.path.insert(0, str(PKG / "tooling"))
import add
from add_method import _installer


def test_repo_orientation_uses_current_cli():
    text = (PKG.parent / "AGENTS.md").read_text()
    block = text[text.index("ADD:BEGIN"):text.index("ADD:END")]
    assert "python3 .add/tooling/cli.py status" in block
    assert "add.py status" not in block
    assert "add.py guide" not in block


def test_orientation_status_produces_resume_output(tmp_path):
    add.init(tmp_path / ".add", "code", "Orientation proof")
    proc = subprocess.run(
        [sys.executable, str(PKG / "tooling/cli.py"), "status"],
        cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    assert "Orientation proof" in proc.stdout and "next:" in proc.stdout


def test_pointer_refresh_preserves_user_content(tmp_path):
    profile = next(p for p in _installer.AGENT_PROFILES if p["id"] == "codex")
    path = tmp_path / "AGENTS.md"
    path.write_text("before\n" + _installer._GUIDE_BEGIN + "\nold\n"
                    + _installer._GUIDE_END + "\nafter\n")
    assert _installer._write_agent_pointer(tmp_path, profile) == "updated"
    assert path.read_text().startswith("before\n")
    assert path.read_text().endswith("\nafter\n")
