"""Acceptance checks for the local candidate artifact gate.

Fixture archives carry tiny, real ZIP/TGZ bytes. They exercise the runner's
digest, packaged-payload and upgrade controls without registries or build tools.
The release workflow must separately run the same runner in real-install mode.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "add-method" / "scripts" / "candidate_artifact_smoke.py"
PUBLISH = REPO / ".github" / "workflows" / "publish.yml"

SHARED = {
    "tooling/cli.py": b"print('candidate status')\n",
    "tooling/add.py": b"# candidate engine\n",
    "skill/add/SKILL.md": b"# candidate skill\n",
    "personas-index/use-when.md": b"# candidate index\n",
    "personas-teacher/engineering/seed.md": b"# candidate corpus\n",
}
OLD = {name: data.replace(b"candidate", b"previous")
       for name, data in SHARED.items()}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zip(path: Path, payload: dict[str, bytes], prefix: str) -> None:
    with zipfile.ZipFile(path, "w") as out:
        for name, data in sorted(payload.items()):
            out.writestr(prefix + name, data)


def _tgz(path: Path, payload: dict[str, bytes], prefix: str = "package/") -> None:
    with tarfile.open(path, "w:gz") as out:
        for name, data in sorted(payload.items()):
            info = tarfile.TarInfo(prefix + name)
            info.size = len(data)
            out.addfile(info, io.BytesIO(data))


@pytest.fixture()
def candidate(tmp_path: Path) -> tuple[Path, dict]:
    current = tmp_path / "candidate"
    previous = tmp_path / "previous"
    current.mkdir()
    previous.mkdir()
    wheel = current / "pilotspace_add-9.0.0-py3-none-any.whl"
    sdist = current / "pilotspace_add-9.0.0.tar.gz"
    npm = current / "pilotspace-add-9.0.0.tgz"
    old_wheel = previous / "pilotspace_add-8.0.0-py3-none-any.whl"
    old_npm = previous / "pilotspace-add-8.0.0.tgz"
    _zip(wheel, SHARED, "add_method/_bundled/")
    _tgz(sdist, SHARED, "pilotspace-add-9.0.0/src/add_method/_bundled/")
    _tgz(npm, SHARED)
    _zip(old_wheel, OLD, "add_method/_bundled/")
    _tgz(old_npm, OLD)
    manifest = {
        "tag_commit": "a" * 40,
        "tag_tree": "b" * 40,
        "candidate": {
            "wheel": {"path": str(wheel), "sha256": _sha(wheel)},
            "sdist": {"path": str(sdist), "sha256": _sha(sdist)},
            "npm": {"path": str(npm), "sha256": _sha(npm)},
        },
        "previous": {
            "wheel": {"path": str(old_wheel), "sha256": _sha(old_wheel)},
            "npm": {"path": str(old_npm), "sha256": _sha(old_npm)},
        },
        "preserve": {
            ".add/user-note.md": "my note survives",
            "AGENTS.md#outside-managed-block": "my instruction survives",
        },
    }
    return tmp_path, manifest


def _run(case: tuple[Path, dict]) -> tuple[subprocess.CompletedProcess[str], dict]:
    root, manifest = case
    assert RUNNER.is_file(), f"RED: candidate runner absent: {RUNNER}"
    mf = root / "manifest.json"
    report = root / "report.json"
    mf.write_text(json.dumps(manifest), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--fixture-manifest", str(mf),
         "--report", str(report)],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert report.is_file(), f"runner gave no report: {proc.stderr}"
    return proc, json.loads(report.read_text(encoding="utf-8"))


def test_fixture_candidate_pass_reports_measured_digests(candidate):
    proc, report = _run(candidate)
    assert proc.returncode == 0 and report["outcome"] == "PASS", report
    for kind in ("wheel", "sdist", "npm"):
        assert report["artifacts"][kind]["sha256"] == _sha(
            Path(candidate[1]["candidate"][kind]["path"]))
    assert report["tag_commit"] == candidate[1]["tag_commit"]
    assert report["tag_tree"] == candidate[1]["tag_tree"]
    assert report["fresh_install"]["pip"]["dropped_cli"] == "NOT_RUN"
    assert report["fresh_install"]["npm"]["dropped_cli"] == "NOT_RUN"
    assert report["upgrade"]["pip"]["state_preserved"] == "NOT_RUN"
    assert report["upgrade"]["npm"]["state_preserved"] == "NOT_RUN"
    assert report["archive_controls"]["required_payload"] == "PASS"


def test_hash_mismatch_refuses_before_install(candidate):
    candidate[1]["candidate"]["npm"]["sha256"] = "0" * 64
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["outcome"] == "REFUSED"
    assert report["reason"] == "HASHMISMATCH" and report["stage"] == "hash"
    assert report["path"] == candidate[1]["candidate"]["npm"]["path"]
    assert not report.get("fresh_install") and not report.get("upgrade")


def test_missing_dropped_cli_refuses(candidate):
    path = Path(candidate[1]["candidate"]["npm"]["path"])
    _tgz(path, {k: v for k, v in SHARED.items() if k != "tooling/cli.py"})
    candidate[1]["candidate"]["npm"]["sha256"] = _sha(path)
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["reason"] == "HEADLESS"
    assert report["stage"] in ("archive", "fresh_install")
    assert "tooling/cli.py" in report["path"]


def test_upgrade_user_state_loss_refuses(candidate):
    # A package trying to occupy user-owned state cannot count as a safe upgrade.
    path = Path(candidate[1]["candidate"]["npm"]["path"])
    _tgz(path, {**SHARED, ".add/user-note.md": b"package overwrite\n"})
    candidate[1]["candidate"]["npm"]["sha256"] = _sha(path)
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["reason"] == "STATELOSS"
    assert report["stage"] == "upgrade"
    assert ".add/user-note.md" in report["path"]


def test_installed_package_divergence_refuses(candidate):
    path = Path(candidate[1]["candidate"]["npm"]["path"])
    _tgz(path, {**SHARED, "tooling/add.py": b"# different engine\n"})
    candidate[1]["candidate"]["npm"]["sha256"] = _sha(path)
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["reason"] == "PACKAGE_DIVERGENCE"
    assert "tooling/add.py" in report["path"]


def test_missing_artifact_never_passes(candidate):
    # Run each required-file absence inside one named CHECK so the ADD receipt
    # binds the full five-file matrix rather than a parametrized name suffix.
    for group, kind in (("candidate", "wheel"), ("candidate", "sdist"),
                        ("candidate", "npm"), ("previous", "wheel"),
                        ("previous", "npm")):
        path = Path(candidate[1][group][kind]["path"])
        original = path.read_bytes()
        path.unlink()
        try:
            proc, report = _run(candidate)
            assert proc.returncode != 0 and report["outcome"] == "REFUSED", (group, kind, report)
            assert report["stage"] in ("input", "hash"), (group, kind, report)
            assert report["path"] == str(path), (group, kind, report)
        finally:
            path.write_bytes(original)


def test_unusable_previous_archive_refuses(candidate):
    for kind in ("wheel", "npm"):
        path = Path(candidate[1]["previous"][kind]["path"])
        original, expected = path.read_bytes(), candidate[1]["previous"][kind]["sha256"]
        if kind == "wheel":
            _zip(path, {"nonsense.txt": b"no older engine"}, "add_method/_bundled/")
        else:
            _tgz(path, {"nonsense.txt": b"no older engine"})
        candidate[1]["previous"][kind]["sha256"] = _sha(path)
        try:
            proc, report = _run(candidate)
            assert proc.returncode != 0 and report["outcome"] == "REFUSED", (kind, report)
            assert report["reason"] == "HEADLESS" and report["stage"] == "archive", (kind, report)
            assert "tooling/cli.py" in report["path"], (kind, report)
        finally:
            path.write_bytes(original)
            candidate[1]["previous"][kind]["sha256"] = expected


def test_local_report_does_not_claim_external_attestation(candidate):
    proc, report = _run(candidate)
    assert proc.returncode == 0, report
    assert report["evidence_boundary"] == "local candidate artifact bytes"
    assert not report.get("registry_verified") and not report.get("attestation_verified")


def test_publish_consumes_smoked_artifacts_without_rebuild():
    text = PUBLISH.read_text(encoding="utf-8")
    assert "candidate_artifact_smoke.py" in text, "release gate never runs artifact smoke"
    assert "actions/upload-artifact" in text and text.count("actions/download-artifact") >= 2
    assert "sha256sum" in text or "hashlib.sha256" in text
    assert re.search(r"npm publish\s+[^\n]*\.tgz", text), "npm publisher uses source, not tarball"
    assert "packages-dir: add-method/dist" in text
    assert text.count("python3 -m build") == 1, "publish jobs rebuild or do not build candidate"


def test_previous_tag_is_strictly_older():
    text = PUBLISH.read_text(encoding="utf-8")
    selection = next(line.strip() for line in text.splitlines()
                     if line.strip().startswith("PREVIOUS_VERSION="))
    proc = subprocess.run(
        ["bash", "-c", selection + '\nprintf "%s\\n" "$PREVIOUS_VERSION"'],
        cwd=REPO, env={**os.environ, "REF_NAME": "v3.5.0"},
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "3.4.0", proc.stdout


def test_refusal_report_is_uploaded_on_failure():
    text = PUBLISH.read_text(encoding="utf-8")
    assert re.search(r"- uses: actions/upload-artifact@v4\s+if: always\(\)", text), \
        "a refused smoke must still attach its named report"
    assert re.search(r"npm:\s+.*?needs: candidate", text, re.S)
    assert re.search(r"pypi:\s+.*?needs: candidate", text, re.S)
