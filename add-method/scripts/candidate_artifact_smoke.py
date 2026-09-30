#!/usr/bin/env python3
"""Offline candidate-byte gate for ADD's wheel, sdist and npm tarball.

Fixture mode checks small archives and the same refusal controls without a
registry. Real mode installs the supplied package files and runs their launchers;
the caller must first cache the npm tarballs' declared runtime dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

MANAGED = (".add/tooling", ".claude/skills/add", ".claude/agents",
           ".add/personas-index", ".add/personas-teacher")
SHARED_ARCHIVE_ROOTS = ("tooling/", "skill/add/", "agents/",
                        "personas-index/", "personas-teacher/")
REQUIRED = ("tooling/cli.py", "tooling/add.py", "skill/add/SKILL.md",
            "personas-index/use-when.md")


def tool_versions() -> dict[str, str]:
    versions = {"python": sys.version.split()[0]}
    for name, command in (("pip", [sys.executable, "-m", "pip", "--version"]),
                          ("node", ["node", "--version"]),
                          ("npm", ["npm", "--version"]),
                          ("build", [sys.executable, "-m", "build", "--version"])):
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            versions[name] = (result.stdout or result.stderr).strip() if result.returncode == 0 else "unavailable"
        except (OSError, subprocess.TimeoutExpired):
            versions[name] = "unavailable"
    return versions


class Refusal(Exception):
    def __init__(self, reason: str, stage: str, path: str, detail: str = ""):
        super().__init__(detail or reason)
        self.reason, self.stage, self.path, self.detail = reason, stage, path, detail


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def entries(path: Path, kind: str) -> dict[str, bytes]:
    """Read payload bytes from a package without trusting archive paths."""
    if kind == "wheel":
        with zipfile.ZipFile(path) as archive:
            raw = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
        prefix = "add_method/_bundled/"
    else:
        with tarfile.open(path, "r:*") as archive:
            raw = {m.name: archive.extractfile(m).read() for m in archive
                   if m.isfile() and archive.extractfile(m) is not None}
        if kind == "npm":
            prefix = "package/"
        else:
            candidates = [n.split("src/add_method/_bundled/", 1)[0]
                          for n in raw if "src/add_method/_bundled/" in n]
            if not candidates:
                raise Refusal("HEADLESS", "archive", str(path), "sdist has no bundled payload")
            prefix = candidates[0] + "src/add_method/_bundled/"
    return {n[len(prefix):]: data for n, data in raw.items() if n.startswith(prefix)}


def hashes(payload: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}


def package_version(path: Path, kind: str) -> str:
    if kind == "npm":
        with tarfile.open(path, "r:*") as archive:
            member = archive.extractfile("package/package.json")
            if member is None:
                raise Refusal("HEADLESS", "archive", "package/package.json")
            return str(json.loads(member.read())["version"])
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise Refusal("HEADLESS", "archive", str(path), "wheel has no unique metadata")
        metadata = archive.read(names[0]).decode("utf-8")
    match = re.search(r"(?m)^Version: (\S+)$", metadata)
    if not match:
        raise Refusal("HEADLESS", "archive", names[0], "wheel has no version")
    return match.group(1)


def verify_archives(files: dict, fixture: bool) -> dict:
    payload = {kind: entries(Path(files["candidate"][kind]["path"]), kind)
               for kind in ("wheel", "sdist", "npm")}
    previous_payload = {kind: entries(Path(files["previous"][kind]["path"]), kind)
                        for kind in ("wheel", "npm")}
    for kind in ("wheel", "npm"):
        for name in REQUIRED:
            if name not in payload[kind]:
                raise Refusal("HEADLESS", "archive", name, f"{kind} lacks {name}")
    for name in REQUIRED:
        if name not in payload["sdist"]:
            raise Refusal("HEADLESS", "archive", name, f"sdist lacks {name}")
    for kind in ("wheel", "sdist", "npm"):
        if not any(name.startswith("personas-teacher/") for name in payload[kind]):
            raise Refusal("HEADLESS", "archive", "personas-teacher/",
                          f"{kind} lacks the representative teacher corpus")
    for kind in ("wheel", "npm"):
        for name in REQUIRED:
            if name not in previous_payload[kind]:
                raise Refusal("HEADLESS", "archive", name,
                              f"previous {kind} has no upgradeable {name}")
        if not any(name.startswith("personas-teacher/") for name in previous_payload[kind]):
            raise Refusal("HEADLESS", "archive", "personas-teacher/",
                          f"previous {kind} lacks an upgradeable teacher corpus")
    # An archive must never claim ownership of user-state paths during upgrade.
    for kind in ("wheel", "npm"):
        for name in payload[kind]:
            if name.startswith(".add/") or name.startswith("../"):
                raise Refusal("STATELOSS", "upgrade", name, "candidate includes user-owned state")
    common = {name for name in set(payload["wheel"]) | set(payload["npm"])
              if name.startswith(SHARED_ARCHIVE_ROOTS)}
    for name in sorted(common):
        if name not in payload["wheel"] or name not in payload["npm"] or payload["wheel"][name] != payload["npm"][name]:
            raise Refusal("PACKAGE_DIVERGENCE", "archive", name,
                          "wheel and npm shared managed bytes differ")
    source_common = {name for name in set(payload["wheel"]) | set(payload["sdist"])
                     if name.startswith(SHARED_ARCHIVE_ROOTS)}
    for name in sorted(source_common):
        if payload["wheel"].get(name) != payload["sdist"].get(name):
            raise Refusal("PACKAGE_DIVERGENCE", "archive", name,
                          "sdist and wheel shared managed bytes differ")
    return payload


def run(argv: list[str], *, cwd: Path | None = None, env: dict | None = None,
        stage: str, path: str, report: dict) -> str:
    proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=90)
    report.setdefault("commands", []).append({
        "stage": stage, "argv": argv, "returncode": proc.returncode,
        "stdout": proc.stdout[-1200:], "stderr": proc.stderr[-1200:]})
    if proc.returncode != 0:
        raise Refusal("SMOKE_FAILED", stage, path, proc.stderr[-500:] or proc.stdout[-500:])
    return proc.stdout


def snapshot(project: Path) -> dict[str, str]:
    result = {}
    for root in MANAGED:
        base = project / root
        if not base.is_dir():
            continue
        for file in base.rglob("*"):
            # Importing the dropped Python engine may generate interpreter-local
            # bytecode. It is runtime cache, not managed package payload.
            if file.is_file() and "__pycache__" not in file.parts and file.suffix not in (".pyc", ".pyo"):
                result[str(file.relative_to(project))] = digest(file)
    return result


def compare_installed(pip_project: Path, npm_project: Path) -> None:
    pip, npm = snapshot(pip_project), snapshot(npm_project)
    for name in sorted(set(pip) | set(npm)):
        if pip.get(name) != npm.get(name):
            raise Refusal("PACKAGE_DIVERGENCE", "fresh_install", name,
                          "installed npm and pip managed files differ")


def stamp(project: Path) -> dict:
    file = project / ".add" / ".add-version"
    try:
        value = json.loads(file.read_text(encoding="utf-8"))
        if isinstance(value, dict) and "version" in value:
            return value
    except (OSError, ValueError):
        pass
    raise Refusal("SMOKE_FAILED", "fresh_install", str(project / ".add"),
                  "installed project has no version stamp")


def status(project: Path, python: Path, report: dict, stage: str,
           initialize: bool = True) -> None:
    cli = project / ".add" / "tooling" / "cli.py"
    if not cli.is_file():
        raise Refusal("HEADLESS", stage, ".add/tooling/cli.py")
    if initialize:
        run([str(python), str(cli), "init"], cwd=project, stage=stage,
            path=str(cli), report=report)
    run([str(python), str(cli), "status"], cwd=project, stage=stage,
        path=str(cli), report=report)


def installed_npm(root: Path, tarball: Path, report: dict, stage: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.json").write_text('{"private":true,"name":"add-artifact-smoke","version":"0.0.0"}\n')
    run(["npm", "install", "--offline", "--ignore-scripts", "--no-audit",
         "--no-fund", "--no-save", str(tarball)], cwd=root, stage=stage,
        path=str(tarball), report=report)
    launcher = root / "node_modules" / "@pilotspace" / "add" / "bin" / "cli.js"
    if not launcher.is_file():
        raise Refusal("HEADLESS", stage, str(launcher), "npm install omitted launcher")
    return launcher


def installed_pip(root: Path, wheel: Path, report: dict, stage: str) -> tuple[Path, Path]:
    run([sys.executable, "-m", "venv", str(root)], stage=stage,
        path=str(wheel), report=report)
    python = root / "bin" / "python"
    launcher = root / "bin" / "pilotspace-add"
    run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        stage=stage, path=str(wheel), report=report)
    if not launcher.is_file():
        raise Refusal("HEADLESS", stage, str(launcher), "wheel omitted console launcher")
    return launcher, python


def preserve(project: Path, manifest: dict) -> dict[str, bytes]:
    expected = {}
    for name, text in manifest.get("preserve", {}).items():
        if "#" in name:
            name = name.split("#", 1)[0]
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            original = path.read_bytes()
            path.write_bytes(original + b"\n" + text.encode())
            expected[name] = original + b"\n" + text.encode()
        else:
            path.write_text(text, encoding="utf-8")
            expected[name] = text.encode()
    return expected


def ensure_preserved(project: Path, expected: dict[str, bytes]) -> None:
    for name, data in expected.items():
        path = project / name
        if not path.is_file() or path.read_bytes() != data:
            raise Refusal("STATELOSS", "upgrade", name, "user-owned bytes changed")


def real_smoke(manifest: dict, report: dict, tmp: Path) -> None:
    candidate = manifest["candidate"]
    previous = manifest["previous"]
    candidate_versions = {
        "pip": package_version(Path(candidate["wheel"]["path"]), "wheel"),
        "npm": package_version(Path(candidate["npm"]["path"]), "npm")}
    if candidate_versions["pip"] != candidate_versions["npm"]:
        raise Refusal("PACKAGE_DIVERGENCE", "archive", "version",
                      "wheel and npm tarball declare different versions")
    new_pip, python = installed_pip(tmp / "candidate-venv",
                                    Path(candidate["wheel"]["path"]), report, "fresh_install")
    new_npm = installed_npm(tmp / "candidate-npm", Path(candidate["npm"]["path"]),
                            report, "fresh_install")
    fresh = {}
    for channel, launcher in (("pip", new_pip), ("npm", new_npm)):
        project = tmp / f"fresh-{channel}"
        project.mkdir()
        command = ([str(launcher)] if channel == "pip" else ["node", str(launcher)])
        run(command + ["init", str(project), "--yes"], stage="fresh_install",
            path=str(launcher), report=report)
        # Installer init drops files only; the version stamp is written by
        # update, so stamp the freshly materialized managed layer explicitly.
        run(command + ["update", str(project)], stage="fresh_install",
            path=str(launcher), report=report)
        status(project, python, report, "fresh_install")
        version = stamp(project)["version"]
        if version != candidate_versions[channel]:
            raise Refusal("SMOKE_FAILED", "fresh_install", ".add/.add-version",
                          "project stamp differs from installed artifact metadata")
        fresh[channel] = {"dropped_cli": "PASS", "version": version}
    compare_installed(tmp / "fresh-pip", tmp / "fresh-npm")
    report["fresh_install"] = fresh

    old_pip, _old_python = installed_pip(tmp / "previous-venv",
                                         Path(previous["wheel"]["path"]), report, "upgrade")
    old_npm = installed_npm(tmp / "previous-npm", Path(previous["npm"]["path"]),
                            report, "upgrade")
    upgrades = {}
    for channel, old, new in (("pip", old_pip, new_pip), ("npm", old_npm, new_npm)):
        project = tmp / f"upgrade-{channel}"
        project.mkdir()
        old_cmd = [str(old)] if channel == "pip" else ["node", str(old)]
        new_cmd = [str(new)] if channel == "pip" else ["node", str(new)]
        run(old_cmd + ["init", str(project), "--yes"], stage="upgrade",
            path=str(old), report=report)
        run(old_cmd + ["update", str(project)], stage="upgrade",
            path=str(old), report=report)
        status(project, python, report, "upgrade")
        old_stamp = stamp(project)["version"]
        before = snapshot(project)
        owned = preserve(project, manifest)
        drift = run(new_cmd + ["update", str(project), "--check"], stage="upgrade",
                    path=str(new), report=report)
        if "update available" not in drift and "unstamped" not in drift:
            raise Refusal("SMOKE_FAILED", "upgrade", str(project), "candidate did not report drift")
        run(new_cmd + ["update", str(project)], stage="upgrade",
            path=str(new), report=report)
        current = run(new_cmd + ["update", str(project), "--check"], stage="upgrade",
                      path=str(new), report=report)
        if "is current" not in current:
            raise Refusal("SMOKE_FAILED", "upgrade", str(project), "candidate did not report current")
        ensure_preserved(project, owned)
        status(project, python, report, "upgrade", initialize=False)
        new_stamp = stamp(project)["version"]
        after = snapshot(project)
        if new_stamp == old_stamp or before.get(".add/tooling/add.py") == after.get(".add/tooling/add.py"):
            raise Refusal("SMOKE_FAILED", "upgrade", ".add/tooling/add.py",
                          "candidate version or engine did not advance")
        upgrades[channel] = {"state_preserved": "PASS", "previous_version": old_stamp,
                             "candidate_version": new_stamp}
    compare_installed(tmp / "upgrade-pip", tmp / "upgrade-npm")
    report["upgrade"] = upgrades


def fixture_smoke(manifest: dict, report: dict, payload: dict) -> None:
    # Fixture archives are intentionally synthetic: verify package content and
    # upgrade boundaries, then label actual install/update observations NOT_RUN.
    report["archive_controls"] = {
        "required_payload": "PASS", "shared_payload": "PASS",
        "previous_payload": "PASS", "candidate_user_state_guard": "PASS"}
    report["fresh_install"] = {
        kind: {"dropped_cli": "NOT_RUN", "mode": "fixture archive"}
        for kind in ("pip", "npm")}
    report["upgrade"] = {
        kind: {"state_preserved": "NOT_RUN", "mode": "fixture archive"}
        for kind in ("pip", "npm")}
    report["fixture_payload_digest"] = hashes(payload["wheel"])


def process(manifest: dict, fixture: bool, report: dict) -> None:
    report["tool_versions"] = tool_versions()
    for group, kinds in (("candidate", ("wheel", "sdist", "npm")),
                         ("previous", ("wheel", "npm"))):
        for kind in kinds:
            spec = manifest.get(group, {}).get(kind)
            if not isinstance(spec, dict) or not spec.get("path"):
                raise Refusal("MISSING_ARTIFACT", "input", f"{group}.{kind}")
            path = Path(spec["path"])
            if not path.is_file():
                raise Refusal("MISSING_ARTIFACT", "input", str(path))
            measured = digest(path)
            if not re.fullmatch(r"[0-9a-f]{64}", str(spec.get("sha256") or "")) or measured != spec["sha256"]:
                raise Refusal("HASHMISMATCH", "hash", str(path), f"measured {measured}")
            report.setdefault("artifacts", {}).setdefault(group, {})[kind] = {
                "path": str(path), "sha256": measured}
    # Flatten candidate artifact data for stable consumer access.
    report["artifacts"].update(report["artifacts"].pop("candidate"))
    report["tag_commit"] = manifest.get("tag_commit")
    report["tag_tree"] = manifest.get("tag_tree")
    payload = verify_archives(manifest, fixture)
    if fixture:
        fixture_smoke(manifest, report, payload)
    else:
        with tempfile.TemporaryDirectory(prefix="add-candidate-") as directory:
            real_smoke(manifest, report, Path(directory))
        # Rehash after installing to detect modified or swapped inputs.
        for group, kinds in (("candidate", ("wheel", "sdist", "npm")),
                             ("previous", ("wheel", "npm"))):
            for kind in kinds:
                spec = manifest[group][kind]
                if digest(Path(spec["path"])) != spec["sha256"]:
                    raise Refusal("HASHMISMATCH", "post_install_hash", spec["path"])
    report["evidence_boundary"] = "local candidate artifact bytes"
    report["registry_verified"] = False
    report["attestation_verified"] = False
    report["outcome"] = "PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--manifest", type=Path)
    mode.add_argument("--fixture-manifest", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = args.fixture_manifest or args.manifest
    report: dict = {"outcome": "REFUSED", "evidence_boundary": "local candidate artifact bytes",
                    "registry_verified": False, "attestation_verified": False}
    try:
        manifest = json.loads(source.read_text(encoding="utf-8"))
        process(manifest, args.fixture_manifest is not None, report)
    except Refusal as err:
        report.update(outcome="REFUSED", reason=err.reason, stage=err.stage,
                      path=err.path, detail=err.detail)
    except (OSError, ValueError, KeyError, tarfile.TarError, zipfile.BadZipFile,
            subprocess.TimeoutExpired) as err:
        report.update(outcome="REFUSED", reason="SMOKE_FAILED", stage="input",
                      path=str(source), detail=str(err))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if report["outcome"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
