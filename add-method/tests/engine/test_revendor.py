"""`add doctor --sync` re-vendors a stale engine — detection now has a one-command fix.

`tooling_drift` warns when the vendored `.add/tooling/` engine no longer matches the running one, but
its old advice ("re-run add init") was a dead end: init's put() skips existing files, so it never
refreshed. `doctor_sync` now overwrites the stale copy and re-stamps `tooling_engine`, clearing the drift.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli  # noqa: E402


def _set_tooling_engine(root, value):
    path = root / "index.md"
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'tooling_engine', value)}\n---\n{n['body']}")


def test_doctor_sync_revendors_a_stale_engine(tmp_path):
    """covers: M2 — after a drift, doctor_sync refreshes tooling and clears tooling_drift."""
    add.init(tmp_path, "code", "T")
    # Simulate drift: an old recorded version + a corrupted vendored engine file.
    _set_tooling_engine(tmp_path, "add/2.0.0")
    (tmp_path / "tooling" / "add.py").write_text("# STALE ENGINE\n", encoding="utf-8")
    assert add.tooling_drift(tmp_path) is not None, "precondition: the bundle is drifted"

    changed, _ = add.doctor_sync(tmp_path)
    assert changed is True
    assert add.tooling_drift(tmp_path) is None, "doctor_sync must clear the drift"
    assert (tmp_path / "tooling" / "add.py").read_bytes() == (add.TOOLING_SRC / "add.py").read_bytes(), \
        "the stale vendored engine must be overwritten with the running engine"


def test_init_tooling_stays_idempotent(tmp_path):
    """covers: M1, R:CLOBBER — the shared helper keeps init non-clobbering."""
    add.init(tmp_path, "code", "T")
    (tmp_path / "tooling" / "add.py").write_text("# a human edited this\n", encoding="utf-8")
    add.init(tmp_path, "code", "T")  # re-run
    assert (tmp_path / "tooling" / "add.py").read_text(encoding="utf-8") == "# a human edited this\n", \
        "init (overwrite=False) must never clobber an existing vendored file"


def test_doctor_sync_is_cli_reachable(tmp_path):
    """covers: M3 — `add doctor --sync` returns 0 on a real bundle."""
    add.init(tmp_path, "code", "T")
    assert cli.main(["--root", str(tmp_path), "doctor", "--sync"]) == 0


def test_doctor_lists_findings(tmp_path):
    """covers: M3 — `add doctor` returns 0 and reports."""
    add.init(tmp_path, "code", "T")
    assert cli.main(["--root", str(tmp_path), "doctor"]) == 0


def test_drift_message_points_at_doctor_sync(tmp_path):
    """covers: M4 — the warning names the working fix, not the dead-end init."""
    add.init(tmp_path, "code", "T")
    _set_tooling_engine(tmp_path, "add/2.0.0")
    msg = add.tooling_drift(tmp_path)
    assert "doctor --sync" in msg, f"the drift warning must point at the working fix: {msg!r}"
    assert "add init" not in msg, "re-running init never refreshes — do not advise it"
