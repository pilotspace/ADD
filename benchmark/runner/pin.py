"""resolve_pin — frozen per TASK.md bench-runner §3.

The `add` arm's `pin` field in add.toml is a repo-path comment, not a
reproducible ref (bench-scaffold spec delta). This resolves it to a concrete,
re-derivable git SHA at execution time; every other arm's pin passes through
unchanged (already reproducible: an npm/pip/git ref string).
"""
from __future__ import annotations

import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def resolve_pin(raw_pin: str, arm_name: str, *, repo_path: pathlib.Path | None = None) -> str:
    """Return a concrete, re-derivable reference for `raw_pin`.

    Only the `add` arm's pin is a repo-path comment needing resolution
    (bench-scaffold spec delta); every other arm's pin is already a
    reproducible ref (npm/pip/git version string) and passes through as-is.
    """
    if arm_name != "add":
        return raw_pin

    path = repo_path or REPO_ROOT
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(path),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
