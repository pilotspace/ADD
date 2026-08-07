"""A stale vendored engine is surfaced, never silent — `doctor` + `status --check` warn on drift.

`init` stamps `tooling_engine:` into index.md at the version it vendored. When a newer engine later
runs against that bundle, the recorded version no longer matches the running `ENGINE` — the vendored
copy is stale. That drift is the exact failure the version-stamp exists to catch, so it must show up
on the reachable conformance surface, not stay hidden until the stale engine does the wrong thing.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _set_tooling_engine(root, value):
    """Rewrite (or drop, if value is None) index.md's tooling_engine via the engine's own set_key."""
    path = root / "index.md"
    n = add.read(path, "T2")
    raw = n["raw"]
    if value is None:
        raw = "\n".join(l for l in raw.splitlines() if not l.startswith("tooling_engine:"))
    else:
        raw = add.set_key(raw, "tooling_engine", value)
    add.write(path, f"---\n{raw}\n---\n{n['body']}")


def test_drift_detected_when_versions_differ(tmp_path):
    """covers: M1 — an older recorded tooling_engine yields a warning."""
    add.init(tmp_path, "code", "T")
    _set_tooling_engine(tmp_path, "add/2.0.0")
    warn = add.tooling_drift(tmp_path)
    assert warn and "add/2.0.0" in warn and add.ENGINE in warn, "drift must name both versions"


def test_no_drift_when_versions_match(tmp_path):
    """covers: M1, R:NODRIFT — a fresh bundle records the running ENGINE, so no drift."""
    add.init(tmp_path, "code", "T")
    assert add.tooling_drift(tmp_path) is None, "a fresh bundle must not warn"


def test_no_drift_when_untooled(tmp_path):
    """covers: R:NODRIFT — a bundle with no tooling_engine recorded cannot drift."""
    add.init(tmp_path, "code", "T")
    _set_tooling_engine(tmp_path, None)
    assert add.tooling_drift(tmp_path) is None, "no recorded version → nothing to compare → no warning"


def test_doctor_reports_drift(tmp_path):
    """covers: M2 — doctor emits a tooling_drift finding on drift."""
    add.init(tmp_path, "code", "T")
    _set_tooling_engine(tmp_path, "add/2.0.0")
    codes = [f["code"] for f in add.doctor(tmp_path)]
    assert "tooling_drift" in codes, "doctor must report the drift"


def test_status_check_surfaces_drift(tmp_path):
    """covers: M3 — status(check=True) shows the drift; check=False stays quiet."""
    add.init(tmp_path, "code", "T")
    _set_tooling_engine(tmp_path, "add/2.0.0")
    assert "add/2.0.0" in add.status(tmp_path, check=True), "the --check surface must show drift"
    assert "add/2.0.0" not in add.status(tmp_path, check=False), "plain status stays cheap and quiet"
