"""add_engine.version — the npm/PyPI update-nudge version helpers (engine-modularization 13/N).

Safe JSON read, semantic-ish version compare, and a fail-soft registry fetch (timeout-bounded,
never raises into the nudge path). A closed cluster: the three functions don't call each other.
The cluster-private _REGISTRY_LATEST (the npm 'latest' URL) lives here. Deps: stdlib only.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

_REGISTRY_LATEST = "https://registry.npmjs.org/@pilotspace/add/latest"


def _read_json_safe(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

def _version_gt(a: str, b: str) -> bool:
    """True if version a is newer than b (dotted numeric; prerelease suffix dropped)."""
    def key(v: str):
        out = []
        for part in str(v).split("."):
            part = part.split("-", 1)[0]
            out.append((0, int(part)) if part.isdigit() else (1, part))
        return out
    try:
        return key(a) > key(b)
    except Exception:
        return False

def _fetch_latest_version(timeout: float = 1.5):
    """GET the registry's latest version. Returns a string, or None on ANY failure
    (offline, timeout, bad payload) — the caller treats None as 'unknown, skip'."""
    try:
        req = urllib.request.Request(_REGISTRY_LATEST, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        v = data.get("version")
        return v if isinstance(v, str) and v else None
    except Exception:
        return None
