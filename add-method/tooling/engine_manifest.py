#!/usr/bin/env python3
"""engine_manifest — the digest helpers the pin-parity tests compare against.

ADD 3.0 (ABF-1): the engine is a FLAT two-file pair — `add.py` (the library) and
`cli.py` (the dispatch entry). There is no `add_engine/` package any more, so the
old package-digest becomes a single-file digest over `cli.py`.

engine_pin.py holds TWO literal pins: ENGINE_MD5 = md5(add.py) and ENGINE_PKG_MD5 =
md5(cli.py) (repurposed from the retired package digest). This helper is kept SEPARATE
from engine_pin.py on purpose: the pin home must never hash or read files (the
vacuous-pin guard), so the COMPUTATION the parity tests use lives here, not in the pin.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def engine_digest(tooling_dir) -> str:
    """md5 over tooling/add.py — compared against ENGINE_MD5."""
    return hashlib.md5((Path(tooling_dir) / "add.py").read_bytes()).hexdigest()


def package_digest(tooling_dir) -> str:
    """md5 over tooling/cli.py — compared against ENGINE_PKG_MD5.

    Name kept for call-site parity with the retired add_engine/ package digest; the
    flat engine's second file (the dispatch entry) is what it now pins.
    """
    return hashlib.md5((Path(tooling_dir) / "cli.py").read_bytes()).hexdigest()
