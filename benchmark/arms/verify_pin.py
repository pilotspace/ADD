#!/usr/bin/env python3
"""Arm setup step: refuse to install a pinned arm from a checkout that has left its pin.

    python3 {REPO_ROOT}/benchmark/arms/verify_pin.py <checkout> <full-sha>

A control arm installs editable from a local git checkout, so what it measures is whatever
that checkout holds at setup time. A `pin =` string in the toml is a claim; this is the
check. Exit 0 when HEAD is the pinned commit, exit 1 (loud, recorded in the transcript,
before any install or agent spend) when it is not or cannot be read.

HEAD is read from the files git keeps — `.git` as a directory, or as the `gitdir:` FILE a
linked `git worktree` has — so the check runs no git command against a checkout it does
not own. Tracked-file edits on top of the pinned HEAD are NOT detected here; see the
launch checklist for the `git status` to run before a campaign.
"""
from __future__ import annotations

import pathlib
import sys


def _gitdir(checkout: pathlib.Path) -> pathlib.Path:
    dot = checkout / ".git"
    if dot.is_dir():
        return dot
    if dot.is_file():
        text = dot.read_text().strip()
        if text.startswith("gitdir:"):
            gd = pathlib.Path(text.split(":", 1)[1].strip())
            return gd if gd.is_absolute() else (checkout / gd).resolve()
    raise ValueError(f"{checkout} is not a git checkout (no .git dir or gitdir file)")


def _commondir(gitdir: pathlib.Path) -> pathlib.Path:
    common = gitdir / "commondir"
    if common.is_file():
        p = pathlib.Path(common.read_text().strip())
        return p if p.is_absolute() else (gitdir / p).resolve()
    return gitdir


def head_sha(checkout: pathlib.Path) -> str:
    gitdir = _gitdir(checkout)
    head = (gitdir / "HEAD").read_text().strip()
    if not head.startswith("ref:"):
        return head                                   # detached HEAD holds the sha itself
    ref = head.split(":", 1)[1].strip()
    for base in (gitdir, _commondir(gitdir)):
        loose = base / ref
        if loose.is_file():
            return loose.read_text().strip()
    packed = _commondir(gitdir) / "packed-refs"
    if packed.is_file():
        for line in packed.read_text().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == ref:
                return parts[0]
    raise ValueError(f"{checkout}: HEAD names {ref}, which resolves to no commit")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_pin.py <checkout> <full-sha>", file=sys.stderr)
        return 2
    checkout, want = pathlib.Path(argv[0]), argv[1].strip().lower()
    try:
        got = head_sha(checkout).lower()
    except (OSError, ValueError) as exc:
        print(f"verify_pin: cannot read HEAD — {exc}", file=sys.stderr)
        return 1
    if got != want:
        print(f"verify_pin: pin mismatch at {checkout}: HEAD {got}, pinned {want}", file=sys.stderr)
        return 1
    print(f"verify_pin: {checkout} at pinned {want[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
