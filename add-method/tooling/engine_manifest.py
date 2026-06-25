#!/usr/bin/env python3
"""engine_manifest — the package digest over the add_engine/ modules.

The engine is add.py (the entry) + add_engine/*.py (the modules). engine_pin.py
holds TWO literal pins: ENGINE_MD5 = md5(add.py) and ENGINE_PKG_MD5 = the package
digest below. This helper is kept SEPARATE from engine_pin.py on purpose: the pin
home must never hash or read files (the vacuous-pin guard), so the COMPUTATION the
parity tests use to compare against ENGINE_PKG_MD5 lives here, not in the pin.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def package_files(tooling_dir) -> list:
    """add_engine/*.py under tooling_dir, sorted by filename (deterministic)."""
    pkg = Path(tooling_dir) / "add_engine"
    return sorted(pkg.glob("*.py"), key=lambda p: p.name) if pkg.is_dir() else []


def package_digest(tooling_dir) -> str:
    """md5 over the sorted manifest of {filename: md5(bytes)} for the package modules."""
    h = hashlib.md5()
    for f in package_files(tooling_dir):
        h.update(f"{f.name}:{hashlib.md5(f.read_bytes()).hexdigest()}\n".encode())
    return h.hexdigest()
