#!/usr/bin/env python3
"""Offline candidate-byte gate for ADD's wheel, sdist and npm tarball.

Fixture mode checks small archives and the same refusal controls without a
registry. Real mode installs the supplied package files and runs their launchers:
a fresh install with each twin (identical trees, idempotent re-run) and an upgrade
over a project the previous (3.x) package installed. The candidate itself has no
runtime dependencies; the caller must cache the PREVIOUS npm tarball's (3.x shipped
@clack/prompts) so the offline install of it succeeds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

# What a 4.0 install lays down — compared byte-for-byte between the pip and npm twins.
MANAGED = (".claude/skills/add", ".add/personas-teacher", ".add/personas-index",
           ".add/personas", ".add/PROJECT.md", ".add/.gitignore", "CLAUDE.md", "AGENTS.md")
SHARED_ARCHIVE_ROOTS = ("skill/add/", "personas/", "personas-index/", "personas-teacher/")
REQUIRED = ("skill/add/SKILL.md", "skill/add/references/format.md",
            "personas-index/use-when.md")
REQUIRED_TREES = ("personas/", "personas-teacher/")
PREVIOUS_REQUIRED = ("skill/add/SKILL.md",)
RETIRED_ROOTS = ("tooling/", "agents/")     # 4.0 ships no engine and no agent roster
RETIRED_AGENTS = (".claude/agents/add-worker.md", ".claude/agents/add-advisor.md")


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
                raise Refusal("MISSING_PAYLOAD", "archive", str(path), "sdist has no bundled payload")
            prefix = candidates[0] + "src/add_method/_bundled/"
    return {n[len(prefix):]: data for n, data in raw.items() if n.startswith(prefix)}


def hashes(payload: dict[str, bytes]) -> dict[str, str]:
    return {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}


def package_version(path: Path, kind: str) -> str:
    if kind == "npm":
        with tarfile.open(path, "r:*") as archive:
            member = archive.extractfile("package/package.json")
            if member is None:
                raise Refusal("MISSING_PAYLOAD", "archive", "package/package.json")
            return str(json.loads(member.read())["version"])
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise Refusal("MISSING_PAYLOAD", "archive", str(path), "wheel has no unique metadata")
        metadata = archive.read(names[0]).decode("utf-8")
    match = re.search(r"(?m)^Version: (\S+)$", metadata)
    if not match:
        raise Refusal("MISSING_PAYLOAD", "archive", names[0], "wheel has no version")
    return match.group(1)


def verify_archives(files: dict, fixture: bool) -> dict:
    payload = {kind: entries(Path(files["candidate"][kind]["path"]), kind)
               for kind in ("wheel", "sdist", "npm")}
    previous_payload = {kind: entries(Path(files["previous"][kind]["path"]), kind)
                        for kind in ("wheel", "npm")}
    for kind in ("wheel", "sdist", "npm"):
        for name in REQUIRED:
            if name not in payload[kind]:
                raise Refusal("MISSING_PAYLOAD", "archive", name, f"{kind} lacks {name}")
        for root in REQUIRED_TREES:
            if not any(name.startswith(root) for name in payload[kind]):
                raise Refusal("MISSING_PAYLOAD", "archive", root, f"{kind} lacks {root}")
        for name in sorted(payload[kind]):
            if name.startswith(RETIRED_ROOTS):
                raise Refusal("ENGINE_SHIPPED", "archive", name, f"{kind} still ships {name}")
    for kind in ("wheel", "npm"):
        for name in PREVIOUS_REQUIRED:
            if name not in previous_payload[kind]:
                raise Refusal("MISSING_PAYLOAD", "archive", name,
                              f"previous {kind} has no upgradeable {name}")
    # An archive must never claim ownership of user-state paths during upgrade.
    for kind in ("wheel", "npm"):
        for name in payload[kind]:
            if name.startswith(".add/") or name.startswith("../"):
                raise Refusal("STATELOSS", "upgrade", name, "candidate includes user-owned state")
    for other in ("npm", "sdist"):
        common = {name for name in set(payload["wheel"]) | set(payload[other])
                  if name.startswith(SHARED_ARCHIVE_ROOTS)}
        for name in sorted(common):
            if payload["wheel"].get(name) != payload[other].get(name):
                raise Refusal("PACKAGE_DIVERGENCE", "archive", name,
                              f"wheel and {other} shared payload bytes differ")
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
        files = [base] if base.is_file() else sorted(base.rglob("*")) if base.is_dir() else []
        for file in files:
            if file.is_file():
                result[file.relative_to(project).as_posix()] = digest(file)
    return result


def compare_installed(pip_project: Path, npm_project: Path, stage: str) -> None:
    pip, npm = snapshot(pip_project), snapshot(npm_project)
    for name in sorted(set(pip) | set(npm)):
        if pip.get(name) != npm.get(name):
            raise Refusal("PACKAGE_DIVERGENCE", stage, name,
                          "installed npm and pip files differ")


def check_skill(project: Path, payload: dict, stage: str) -> None:
    """The installed skill is exactly the candidate's skill, and a project card exists."""
    base = project / ".claude" / "skills" / "add"
    installed = ({f.relative_to(base).as_posix(): f.read_bytes()
                  for f in base.rglob("*") if f.is_file()} if base.is_dir() else {})
    shipped = {n[len("skill/add/"):]: data for n, data in payload.items()
               if n.startswith("skill/add/")}
    for name in sorted(set(installed) | set(shipped)):
        if installed.get(name) != shipped.get(name):
            raise Refusal("SMOKE_FAILED", stage, ".claude/skills/add/" + name,
                          "installed skill differs from the candidate payload")
    if not (project / ".add" / "PROJECT.md").is_file():
        raise Refusal("SMOKE_FAILED", stage, ".add/PROJECT.md", "no project card")


def installed_npm(root: Path, tarball: Path, report: dict, stage: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.json").write_text('{"private":true,"name":"add-artifact-smoke","version":"0.0.0"}\n')
    run(["npm", "install", "--offline", "--ignore-scripts", "--no-audit",
         "--no-fund", "--no-save", str(tarball)], cwd=root, stage=stage,
        path=str(tarball), report=report)
    launcher = root / "node_modules" / "@pilotspace" / "add" / "bin" / "cli.js"
    if not launcher.is_file():
        raise Refusal("MISSING_PAYLOAD", stage, str(launcher), "npm install omitted launcher")
    return launcher


def installed_pip(root: Path, wheel: Path, report: dict, stage: str) -> Path:
    run([sys.executable, "-m", "venv", str(root)], stage=stage,
        path=str(wheel), report=report)
    python = root / "bin" / "python"
    launcher = root / "bin" / "pilotspace-add"
    run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        stage=stage, path=str(wheel), report=report)
    if not launcher.is_file():
        raise Refusal("MISSING_PAYLOAD", stage, str(launcher), "wheel omitted console launcher")
    return launcher


def user_state(project: Path) -> dict[str, str]:
    """Every file under .add/ the installer does not own — it must survive byte-for-byte."""
    owned = ("tooling", "personas-teacher", "personas-index", ".gitignore")
    base = project / ".add"
    return {f.relative_to(project).as_posix(): digest(f) for f in sorted(base.rglob("*"))
            if f.is_file() and f.relative_to(base).parts[0] not in owned}


def preserve(project: Path, manifest: dict) -> dict[str, bytes]:
    """Write the manifest's user-owned text; `file#outside-managed-block` appends to that file."""
    expected = {}
    for name, text in manifest.get("preserve", {}).items():
        path = project / name.split("#", 1)[0]
        path.parent.mkdir(parents=True, exist_ok=True)
        data = text.encode()
        if path.exists():
            path.write_bytes(path.read_bytes() + b"\n" + data + b"\n")
        else:
            path.write_bytes(data)
        expected[name] = data if "#" in name else path.read_bytes()
    return expected


def ensure_preserved(project: Path, expected: dict[str, bytes]) -> None:
    for name, data in expected.items():
        path = project / name.split("#", 1)[0]
        if not path.is_file():
            raise Refusal("STATELOSS", "upgrade", name, "user-owned file removed")
        current = path.read_bytes()
        if "#" in name:                     # text the user wrote OUTSIDE the managed block
            text = current.decode("utf-8")
            begin, end = text.rfind("<!-- ADD:BEGIN"), text.rfind("<!-- ADD:END -->")
            outside = text[:begin] + text[end:] if -1 < begin < end else text
            if data.decode() not in outside:
                raise Refusal("STATELOSS", "upgrade", name, "user text outside the block lost")
        elif current != data:
            raise Refusal("STATELOSS", "upgrade", name, "user-owned bytes changed")


def real_smoke(manifest: dict, report: dict, tmp: Path, payload: dict) -> None:
    candidate, previous = manifest["candidate"], manifest["previous"]
    versions = {"pip": package_version(Path(candidate["wheel"]["path"]), "wheel"),
                "npm": package_version(Path(candidate["npm"]["path"]), "npm")}
    if versions["pip"] != versions["npm"]:
        raise Refusal("PACKAGE_DIVERGENCE", "archive", "version",
                      "wheel and npm tarball declare different versions")
    shipped = {"pip": payload["wheel"], "npm": payload["npm"]}
    new = {"pip": [str(installed_pip(tmp / "candidate-venv", Path(candidate["wheel"]["path"]),
                                     report, "fresh_install"))],
           "npm": ["node", str(installed_npm(tmp / "candidate-npm", Path(candidate["npm"]["path"]),
                                             report, "fresh_install"))]}
    fresh = {}
    for channel, command in new.items():
        project = tmp / "fresh" / channel / "project"   # same folder name: same PROJECT.md title
        project.mkdir(parents=True)
        said = run(command + ["--version"], stage="fresh_install", path=command[-1], report=report)
        if said.strip() != versions[channel]:
            raise Refusal("SMOKE_FAILED", "fresh_install", command[-1],
                          "the launcher reports a different version than its metadata")
        run(command + ["init", str(project)], stage="fresh_install", path=command[-1], report=report)
        check_skill(project, shipped[channel], "fresh_install")
        before = snapshot(project)
        run(command + ["update", str(project)], stage="fresh_install", path=command[-1], report=report)
        if snapshot(project) != before:
            raise Refusal("SMOKE_FAILED", "fresh_install", str(project), "a re-run changed the install")
        fresh[channel] = {"installed": "PASS", "idempotent": "PASS", "version": versions[channel]}
    compare_installed(tmp / "fresh" / "pip" / "project", tmp / "fresh" / "npm" / "project", "fresh_install")
    report["fresh_install"] = fresh

    old = {"pip": [str(installed_pip(tmp / "previous-venv", Path(previous["wheel"]["path"]),
                                     report, "upgrade"))],
           "npm": ["node", str(installed_npm(tmp / "previous-npm", Path(previous["npm"]["path"]),
                                             report, "upgrade"))]}
    upgrades = {}
    for channel in ("pip", "npm"):
        project = tmp / "upgrade" / channel / "project"
        project.mkdir(parents=True)
        run(old[channel] + ["init", str(project), "--yes"], stage="upgrade",
            path=old[channel][-1], report=report)
        engine = project / ".add" / "tooling" / "cli.py"
        if engine.is_file():                # a 3.x package: let its engine lay down real 3.x state
            run([sys.executable, str(engine), "init"], cwd=project, stage="upgrade",
                path=str(engine), report=report)
        state = user_state(project)
        owned = preserve(project, manifest)
        run(new[channel] + ["update", str(project)], stage="upgrade",
            path=new[channel][-1], report=report)
        ensure_preserved(project, owned)
        for name, sha in state.items():
            if not (project / name).is_file() or digest(project / name) != sha:
                raise Refusal("STATELOSS", "upgrade", name, "3.x project state changed")
        for leftover in (".add/tooling",) + RETIRED_AGENTS:
            if (project / leftover).exists():
                raise Refusal("SMOKE_FAILED", "upgrade", leftover, "a 3.x leftover survived")
        check_skill(project, shipped[channel], "upgrade")
        upgrades[channel] = {"state_preserved": "PASS", "engine_removed": "PASS",
                             "candidate_version": versions[channel]}
    compare_installed(tmp / "upgrade" / "pip" / "project", tmp / "upgrade" / "npm" / "project", "upgrade")
    report["upgrade"] = upgrades


def fixture_smoke(manifest: dict, report: dict, payload: dict) -> None:
    # Fixture archives are intentionally synthetic: verify package content and
    # upgrade boundaries, then label actual install/update observations NOT_RUN.
    report["archive_controls"] = {
        "required_payload": "PASS", "shared_payload": "PASS", "no_engine": "PASS",
        "previous_payload": "PASS", "candidate_user_state_guard": "PASS"}
    report["fresh_install"] = {
        kind: {"installed": "NOT_RUN", "mode": "fixture archive"}
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
            real_smoke(manifest, report, Path(directory), payload)
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
