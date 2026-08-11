"""The publish workflow is the last thing between a git tag and two live registries.

`npm publish` with no `--tag` assigns the `latest` dist-tag REGARDLESS of semver prerelease
status — npm does not infer a channel from `3.0.0-beta.1`. So publishing a beta through the bare
command would repoint every plain `npm i @pilotspace/add` at the prerelease, which is a worse
outcome than shipping the final. PyPI needs no equivalent care (pip excludes prereleases unless
`--pre` is passed), and that asymmetry is precisely what makes the npm side easy to miss.

The dist-tag must also be DERIVED, not hard-coded: `--tag beta` pinned in the workflow would send
the eventual 3.0.0 final out on the beta channel and leave `latest` stranded on 2.5.0 forever.

These tests EXECUTE the workflow's publish step against a stubbed `npm` rather than pattern-match
the YAML, so they red when the routing is wrong — not merely when the wording changes.

No pyyaml: CI installs pytest and nothing else, so a `import yaml` here would pass locally and
ImportError on the runner. The extractor below is deliberately dependency-free.
"""
from __future__ import annotations

import os
import re
import subprocess
import textwrap
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
REPO = PKG.parent
PUBLISH_YML = REPO / ".github" / "workflows" / "publish.yml"

PUBLISH_STEP = "Publish if this version is new"


def _run_block(yaml_text: str, step_name_fragment: str) -> str:
    """The `run:` body of the first step whose name contains `step_name_fragment`.

    Hand-rolled rather than pyyaml (see module docstring). Finds the named step, then takes the
    literal block scalar that follows `run: |`, ending at the first line that dedents out of it.
    """
    lines = yaml_text.splitlines()
    start = next((i for i, l in enumerate(lines)
                  if re.match(r"\s*-?\s*name:", l) and step_name_fragment in l), None)
    assert start is not None, f"no step named ~{step_name_fragment!r} in {PUBLISH_YML}"

    run_at = next((i for i in range(start, len(lines))
                   if re.match(r"\s*run:\s*\|", lines[i])), None)
    assert run_at is not None, f"step ~{step_name_fragment!r} has no `run: |` block"

    indent = len(lines[run_at + 1]) - len(lines[run_at + 1].lstrip())
    body = []
    for line in lines[run_at + 1:]:
        if line.strip() and (len(line) - len(line.lstrip())) < indent:
            break
        body.append(line[indent:] if len(line) >= indent else line)
    return "\n".join(body).rstrip() + "\n"


def _exec_publish_step(tmp_path: Path, version: str, *, already_published: bool = False) -> list[str]:
    """Run the real publish step with `npm` stubbed; return the argv it would have published with.

    `npm view` exits non-zero when the version is absent (the workflow's idempotency probe), so
    `already_published` flips that to zero to exercise the skip branch.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    argv_log = tmp_path / "argv.log"

    view_exit = 0 if already_published else 1
    (bin_dir / "npm").write_text(textwrap.dedent(f"""\
        #!/usr/bin/env bash
        if [ "$1" = "view" ]; then exit {view_exit}; fi
        printf '%s\\n' "$*" >> {argv_log}
        exit 0
        """), encoding="utf-8")
    (bin_dir / "npm").chmod(0o755)

    # `node -p "require('./package.json').version"` is how the step learns the version; stub node
    # so the assertion is about ROUTING, not about whatever the tree currently declares.
    (bin_dir / "node").write_text(
        f"#!/usr/bin/env bash\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
    (bin_dir / "node").chmod(0o755)

    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    proc = subprocess.run(["bash", "-c", _run_block(PUBLISH_YML.read_text(encoding="utf-8"),
                                                    PUBLISH_STEP)],
                          cwd=PKG, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, f"publish step failed for {version}:\n{proc.stderr}"
    return argv_log.read_text(encoding="utf-8").splitlines() if argv_log.exists() else []


def test_the_publish_workflow_exists():
    """covers: M1 — absence is a hard failure, never a vacuous skip."""
    assert PUBLISH_YML.is_file(), f"{PUBLISH_YML} is missing — the release gate is the artifact"


def test_a_prerelease_publishes_to_the_beta_channel(tmp_path):
    """covers: M2, E1 — `3.0.0-beta.1` must NOT land on `latest`."""
    published = _exec_publish_step(tmp_path, "3.0.0-beta.1")
    assert len(published) == 1, f"expected exactly one publish, got {published}"
    assert "--tag beta" in published[0], \
        f"a prerelease published without the beta dist-tag — it would become `latest`: {published[0]!r}"


def test_a_final_release_publishes_to_latest(tmp_path):
    """covers: M2, E2 — the dist-tag is derived, so the final does not strand on `beta`."""
    published = _exec_publish_step(tmp_path, "3.0.0")
    assert len(published) == 1, f"expected exactly one publish, got {published}"
    assert "--tag latest" in published[0], \
        f"a final release must claim `latest`, not inherit a hard-coded channel: {published[0]!r}"


def test_release_candidates_are_prereleases_too(tmp_path):
    """covers: E3 — the routing keys on the semver prerelease hyphen, not the literal `beta`."""
    published = _exec_publish_step(tmp_path, "3.1.0-rc.2")
    assert "--tag beta" in published[0], \
        f"any semver prerelease must stay off `latest`: {published[0]!r}"


def test_an_already_published_version_is_skipped(tmp_path):
    """covers: M3 — re-running a tag after a half-publish must not error, so the tag is reusable."""
    assert _exec_publish_step(tmp_path, "3.0.0", already_published=True) == [], \
        "a version already on the registry must be skipped, leaving the tag safe to re-run"


def test_prepublish_hook_runs_something_that_exists():
    """covers: M4, R:GREENLIE — a hook that discovers no tests reports success having run nothing.

    `prepublishOnly` pointed at `tooling/test_packaging.py`, a file 3.0 removed: `unittest discover`
    printed NO TESTS RAN and exited 0. That is the same hollow-gate failure the CI workflow had.
    """
    import json
    scripts = json.loads((PKG / "package.json").read_text(encoding="utf-8")).get("scripts", {})
    hook = scripts.get("prepublishOnly")
    if hook is None:
        return  # deleting the hook is a legitimate green — no gate beats a lying one
    for pattern in re.findall(r"-p\s+'([^']+)'", hook):
        assert list(PKG.rglob(pattern)), \
            f"prepublishOnly discovers {pattern!r}, which matches no file — it runs nothing and exits 0"
