"""add_engine.components — scope-confinement utilities.

kernel-trim (ADD 2.0 M5): the components pillar (registry · cross-component contracts ·
federation) died with its verbs; only the two GENERIC path/scope utilities every scope
read shares survive here. Deps: stdlib only (no add, no add_engine).
"""
from __future__ import annotations

from pathlib import Path


def _confined(p: Path, rootp: Path) -> bool:
    """True only if p resolves (symlinks followed) inside rootp; errors -> False.
    The v2 confinement check — no read is attempted on a path that fails it."""
    try:
        return p.resolve().is_relative_to(rootp)
    except OSError:
        return False






def _in_scope(rel: str, declared: list[str]) -> bool:
    """True when rel falls under any declared token — exact match for a file
    token, whole-subtree prefix containment for a directory token ('…/')."""
    for tok in declared:
        if tok.endswith("/"):
            if rel.startswith(tok) or rel == tok.rstrip("/"):
                return True
        elif rel == tok:
            return True
    return False
