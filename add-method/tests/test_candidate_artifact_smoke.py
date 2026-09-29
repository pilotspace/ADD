"""Acceptance checks for the local candidate artifact gate.

Fixture archives carry tiny, real ZIP/TGZ bytes. They exercise the runner's
digest, packaged-payload and upgrade controls without registries or build tools.
The release workflow must separately run the same runner in real-install mode.

ADD 4.0 ships a skill, not an engine: the candidate must carry the skill, the
starter personas and the persona corpus, and must NOT carry `tooling/` or
`agents/`. The previous (3.x) package only has to be installable.
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
    "skill/add/SKILL.md": b"# candidate skill\n",
    "skill/add/references/format.md": b"# candidate format\n",
    "personas/task-planner.md": b"# candidate persona\n",
    "personas-index/use-when.md": b"# candidate index\n",
    "personas-teacher/engineering/seed.md": b"# candidate corpus\n",
}
OLD = {**{name: data.replace(b"candidate", b"previous") for name, data in SHARED.items()
          if not name.startswith("personas/")},
       "tooling/cli.py": b"print('previous status')\n"}


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
    assert report["fresh_install"]["pip"]["installed"] == "NOT_RUN"
    assert report["fresh_install"]["npm"]["installed"] == "NOT_RUN"
    assert report["upgrade"]["pip"]["state_preserved"] == "NOT_RUN"
    assert report["upgrade"]["npm"]["state_preserved"] == "NOT_RUN"
    assert report["archive_controls"]["required_payload"] == "PASS"
    assert report["archive_controls"]["no_engine"] == "PASS"


def test_hash_mismatch_refuses_before_install(candidate):
    candidate[1]["candidate"]["npm"]["sha256"] = "0" * 64
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["outcome"] == "REFUSED"
    assert report["reason"] == "HASHMISMATCH" and report["stage"] == "hash"
    assert report["path"] == candidate[1]["candidate"]["npm"]["path"]
    assert not report.get("fresh_install") and not report.get("upgrade")


def _repack_npm(candidate, payload):
    path = Path(candidate[1]["candidate"]["npm"]["path"])
    _tgz(path, payload)
    candidate[1]["candidate"]["npm"]["sha256"] = _sha(path)


def test_missing_skill_refuses(candidate):
    for missing in ("skill/add/SKILL.md", "personas/task-planner.md"):
        _repack_npm(candidate, {k: v for k, v in SHARED.items() if k != missing})
        proc, report = _run(candidate)
        assert proc.returncode != 0 and report["reason"] == "MISSING_PAYLOAD", (missing, report)
        assert report["stage"] == "archive" and missing.split("/")[0] in report["path"], report


def test_a_candidate_that_ships_the_engine_refuses(candidate):
    for retired in ("tooling/cli.py", "agents/add-worker.md"):
        _repack_npm(candidate, {**SHARED, retired: b"# 3.x\n"})
        proc, report = _run(candidate)
        assert proc.returncode != 0 and report["reason"] == "ENGINE_SHIPPED", (retired, report)
        assert report["path"] == retired


def test_upgrade_user_state_loss_refuses(candidate):
    # A package trying to occupy user-owned state cannot count as a safe upgrade.
    _repack_npm(candidate, {**SHARED, ".add/user-note.md": b"package overwrite\n"})
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["reason"] == "STATELOSS"
    assert report["stage"] == "upgrade"
    assert ".add/user-note.md" in report["path"]


def test_installed_package_divergence_refuses(candidate):
    _repack_npm(candidate, {**SHARED, "skill/add/SKILL.md": b"# a different skill\n"})
    proc, report = _run(candidate)
    assert proc.returncode != 0 and report["reason"] == "PACKAGE_DIVERGENCE"
    assert "skill/add/SKILL.md" in report["path"]


def test_missing_artifact_never_passes(candidate):
    # Run each required-file absence inside one named CHECK so the receipt
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
            _zip(path, {"nonsense.txt": b"no older skill"}, "add_method/_bundled/")
        else:
            _tgz(path, {"nonsense.txt": b"no older skill"})
        candidate[1]["previous"][kind]["sha256"] = _sha(path)
        try:
            proc, report = _run(candidate)
            assert proc.returncode != 0 and report["outcome"] == "REFUSED", (kind, report)
            assert report["reason"] == "MISSING_PAYLOAD" and report["stage"] == "archive", (kind, report)
            assert "skill/add/SKILL.md" in report["path"], (kind, report)
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


def test_publish_runs_no_engine():
    text = PUBLISH.read_text(encoding="utf-8")
    for retired in ("tooling/cli.py", "tooling/add.py", "clack"):
        assert retired not in text, f"publish.yml still depends on the retired {retired}"


def test_previous_tag_is_strictly_older(tmp_path):
    """CI checks out shallow with no tags, so the selection runs in a scratch repo that holds
    exactly the tags it must choose between — never the ambient clone's tag list."""
    text = PUBLISH.read_text(encoding="utf-8")
    selection = next(line.strip() for line in text.splitlines()
                     if line.strip().startswith("PREVIOUS_VERSION="))
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(tmp_path)]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "base"], check=True)
    for tag in ("v3.3.0", "v3.4.0", "v3.5.0", "v3.6.0", "v3.10.0"):
        subprocess.run([*git, "tag", tag], check=True)
    proc = subprocess.run(
        ["bash", "-c", selection + '\nprintf "%s\\n" "$PREVIOUS_VERSION"'],
        cwd=tmp_path, env={**os.environ, "REF_NAME": "v3.5.0"},
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
