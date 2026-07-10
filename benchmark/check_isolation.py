#!/usr/bin/env python3
"""check_isolation.py — loud, fail-closed guard against oracle contamination.

Usage: python3 benchmark/check_isolation.py <workspace>

Exits 0 if the workspace contains no oracle file (matched by relative path OR
content hash, so a renamed copy is still caught). Exits 1 and prints
"oracle_leak: <path>" per leaked file otherwise. Stdlib only.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

BENCHMARK_ROOT = pathlib.Path(__file__).resolve().parent
WORKLOAD_ROOT = BENCHMARK_ROOT / "workload"


def _oracle_files() -> list[pathlib.Path]:
    return sorted(WORKLOAD_ROOT.glob("wm*/oracle/test_*.py"))


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _oracle_hashes() -> dict[str, pathlib.Path]:
    return {_sha256(p): p for p in _oracle_files()}


def _oracle_relative_paths() -> set[str]:
    return {str(p.relative_to(BENCHMARK_ROOT)) for p in _oracle_files()}


def find_leaks(workspace: pathlib.Path) -> list[pathlib.Path]:
    """Return the list of files inside `workspace` that match an oracle file
    by relative path OR by content hash (catches a renamed copy)."""
    oracle_hashes = _oracle_hashes()
    oracle_rel_paths = _oracle_relative_paths()

    leaks: list[pathlib.Path] = []
    if not workspace.exists():
        return leaks

    for candidate in workspace.rglob("*"):
        if not candidate.is_file():
            continue
        try:
            rel = str(candidate.relative_to(workspace))
        except ValueError:
            rel = ""
        if rel in oracle_rel_paths:
            leaks.append(candidate)
            continue
        try:
            digest = _sha256(candidate)
        except OSError:
            continue
        if digest in oracle_hashes:
            leaks.append(candidate)

    return leaks


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("usage: check_isolation.py <workspace>", file=sys.stderr)
        return 2

    workspace = pathlib.Path(argv[0])
    leaks = find_leaks(workspace)
    if not leaks:
        print(f"clean: {workspace}")
        return 0

    for leak in leaks:
        print(f"oracle_leak: {leak}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
