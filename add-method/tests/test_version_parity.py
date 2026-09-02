"""One version, eight declarations — the pip/npm twins must ship the same number.

The package declares its version in five manifests: `pyproject.toml`, `src/add_method/__init__.py`,
`package.json`, `package-lock.json`, and `.claude-plugin/plugin.json` — and once more in each of
the THREE shipped skill trees, whose `metadata: { version }` an agent reads at load. Those three
were never enumerated here and sat at `3.1.0` two minor releases after 3.1: a rule that quantifies
over a set must ENUMERATE that set, which is exactly what this gate had stopped doing. Nothing held them equal, and
`package-lock.json` silently stayed at `2.5.0` through the whole 3.0 graft — so `npm ci` would
install a tree stamped with the previous major.

This is the version half of what `tooling/test_tree_parity.py` does for the engine and bundle.
"""
import json
import re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]


def _pyproject() -> str:
    text = (PKG / "pyproject.toml").read_text(encoding="utf-8")
    return re.search(r'^version\s*=\s*"([^"]+)"', text, re.M).group(1)


def _dunder() -> str:
    text = (PKG / "src" / "add_method" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.M).group(1)


def _json_version(rel: str) -> str:
    return json.loads((PKG / rel).read_text(encoding="utf-8"))["version"]


SKILL_TREES = (PKG / "skill" / "add",
               PKG / "src" / "add_method" / "_bundled" / "skill" / "add",
               PKG.parent / ".claude" / "skills" / "add")


def _skill_versions() -> dict:
    """`metadata: { ..., version: "X.Y.Z", ... }` from each shipped SKILL.md."""
    out = {}
    for tree in SKILL_TREES:
        f = tree / "SKILL.md"
        if not f.is_file():
            continue          # a fresh checkout may not carry the host-installed tree
        m = re.search(r'metadata:.*?version:\s*"([^"]+)"', f.read_text(encoding="utf-8"))
        assert m, f"{f} declares no metadata version"
        out[str(f.relative_to(PKG.parent))] = m.group(1)
    assert out, "no shipped SKILL.md found — the enumeration is broken, not the declarations"
    return out


def test_every_declaration_agrees():
    """covers: M1 — every version declaration is the same string, skill trees included."""
    declared = {
        "pyproject.toml": _pyproject(),
        "src/add_method/__init__.py": _dunder(),
        "package.json": _json_version("package.json"),
        "package-lock.json": _json_version("package-lock.json"),
        ".claude-plugin/plugin.json": _json_version(".claude-plugin/plugin.json"),
        **_skill_versions(),
    }
    assert len(set(declared.values())) == 1, f"version declarations disagree: {declared}"


def test_no_manifest_description_hard_codes_a_stale_version():
    """covers: M3, E2 — the blurb npm and PyPI show the world must not name the previous major.

    All three descriptions still read "ADD (AI-Driven Development) 2.0" after the 3.0 graft. Those
    strings are the public copy on both registry pages, and nothing bound them to the version
    field — so they advertised 2.0 from a 3.0 artifact. The fix is to carry no version literal at
    all: the `version` field already states it, and prose that repeats it only drifts again.
    """
    stale = {}
    for rel in ("package.json", ".claude-plugin/plugin.json"):
        stale[rel] = json.loads((PKG / rel).read_text(encoding="utf-8")).get("description", "")
    stale["pyproject.toml"] = re.search(
        r'^description\s*=\s*"([^"]*)"', (PKG / "pyproject.toml").read_text(encoding="utf-8"), re.M
    ).group(1)

    for rel, text in stale.items():
        # The trailing `.` of "…Development) 2.0. The agent…" is sentence punctuation, not part of
        # the version — an over-eager lookahead here silently passed while the bug sat in the copy.
        found = re.findall(r"(?<![\w.])\d+\.\d+(?:\.\d+)*(?![\w])", text)
        assert not found, f"{rel} description hard-codes version literal(s) {found}: {text!r}"


def test_lockfile_root_package_agrees():
    """covers: M2, E1 — the lockfile's own `packages[""]` entry, not just its top-level version.

    npm writes the version twice; updating only the top-level one leaves `npm ci` reading a stale
    number out of the root package entry.
    """
    lock = json.loads((PKG / "package-lock.json").read_text(encoding="utf-8"))
    root = lock["packages"][""]
    assert root["version"] == lock["version"] == _pyproject(), \
        f'lockfile root entry {root["version"]!r} != {lock["version"]!r} != {_pyproject()!r}'
