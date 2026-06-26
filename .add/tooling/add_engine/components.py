"""add_engine.components — the component-aware-add subsystem (engine-modularization 11/N).

Registry (.add/components.toml) + produced/consumed contracts + cross-repo federation +
scope confinement. A closed, unpatched cluster (transitive-closure AST = zero outbound).
Replicates add.py's degrade-safe tomllib guard so `import` stays safe on Python < 3.11
(where the registry degrades to opt-out). Opt-in: no components.toml -> every reader is
byte-identical to single-component. Deps: stdlib only (no add, no add_engine).
"""
from __future__ import annotations

import re
from pathlib import Path

try:                          # component registry parse (Python 3.11+ stdlib); degrade-safe
    import tomllib
except ModuleNotFoundError:   # < 3.11: registry unsupported -> tomllib None -> opt-out
    tomllib = None


def _confined(p: Path, rootp: Path) -> bool:
    """True only if p resolves (symlinks followed) inside rootp; errors -> False.
    The v2 confinement check — no read is attempted on a path that fails it."""
    try:
        return p.resolve().is_relative_to(rootp)
    except OSError:
        return False

def _components(root: Path) -> dict[str, dict]:
    """The registry from .add/components.toml → {name: {root, verify, green_bar,
    language}}. `root` required per entry; an entry missing it is skipped (the finding
    surface reports it). `verify` is stored OPAQUE — parsed as data, NEVER executed. PURE."""
    if tomllib is None:
        return {}
    try:
        raw = (root / "components.toml").read_bytes()
    except OSError:
        return {}
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError, ValueError):
        return {}
    out: dict[str, dict] = {}
    for name, spec in (data.get("component") or {}).items():
        # "?" is the reserved unknown-binding sentinel (_task_component) — a component
        # named "?" would collide and silently drop cover, so it never registers.
        if name == "?" or not isinstance(spec, dict) or not isinstance(spec.get("root"), str):
            continue
        out[name] = {"root": spec["root"], "verify": spec.get("verify"),
                     "green_bar": spec.get("green_bar"), "language": spec.get("language")}
    return out

def _cite_region(body: str) -> str:
    """The user-authored "Build expectations" evidence region of a §6 body, stamp-stripped —
    the only place a per-component green-bar cite counts (per-component-verify, v3). PURE.

    The marker matches BOTH template shapes: the standard "### Build expectations …" heading AND
    the fast-lane bare "Build expectations (from …):" line, running up to the GATE RECORD sub-block.
    So the top-of-§6 checklist ("- [ ] all tests pass") and the "Outcome: <PASS|…>" placeholder are
    excluded, and a component-bound FAST task is still citable. The trailing strip removes the
    engine's own "component: … · expected green-bar: …" stamp wherever it landed, so a stamp that
    fell inside the region can never self-satisfy the gate. No marker -> "" (fail-closed for a bound
    task: it must declare its evidence)."""
    m = re.search(r"(?im)^#*[ \t]*Build expectations\b.*?(?=\n#+[ \t]*GATE RECORD\b|\Z)", body, re.DOTALL)
    region = m.group(0) if m else ""
    return re.sub(r"(?m)^component:.*·.*expected green-bar:.*$", "", region)

def _contracts(root: Path) -> dict[str, dict]:
    """[contract.<id>] from .add/components.toml -> {id: {producer: str, consumers: list[str]}}.
    A malformed entry (producer not a str) is skipped (the finding surface reports it). PURE."""
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads((root / "components.toml").read_bytes().decode("utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError, ValueError):
        return {}
    out: dict[str, dict] = {}
    for cid, spec in (data.get("contract") or {}).items():
        if not isinstance(spec, dict) or not isinstance(spec.get("producer"), str):
            continue
        cons = spec.get("consumers")
        out[cid] = {"producer": spec["producer"],
                    "consumers": [c for c in cons if isinstance(c, str)] if isinstance(cons, list) else []}
    return out

def _federation(root: Path) -> dict[str, dict]:
    """[federation.<id>] from .add/components.toml -> {id: {source: str, pin: str|None}}.
    The cross-REPO join: a consumer repo names where a producer repo's published snapshot lives.
    A malformed entry (no string source) is skipped; a non-string `pin` degrades to None. Degrade-safe
    — never raises. PURE. On Python < 3.11 (no tomllib) this returns {} like the other component
    readers, so `federate` reports federation_unknown — components.toml needs a 3.11+ runtime."""
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads((root / "components.toml").read_bytes().decode("utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError, ValueError):
        return {}
    out: dict[str, dict] = {}
    for fid, spec in (data.get("federation") or {}).items():
        if not isinstance(spec, dict) or not isinstance(spec.get("source"), str):
            continue
        pin = spec.get("pin")
        out[fid] = {"source": spec["source"], "pin": pin if isinstance(pin, str) else None}
    return out

def _contract_snapshot(root: Path, cid: str) -> Path:
    return root / "contracts" / f"{cid}.json"

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
