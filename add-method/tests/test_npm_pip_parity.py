"""The npm launcher and the pip installer are twins — the invariants that must not drift apart.

`bin/cli.js` and `src/add_method/_installer.py` install the same payload into the same places by
two different routes. Nothing held them equal after the 3.0 graft: the twins were reconciled by
hand and left unguarded.

`cli.js` carries no node test harness, so — following the 2.5 pattern (`test_soul_seed_npm_parity`,
`test_update.py`) — these are TEXT-INVARIANT proofs on the JS source, paired against the real
constants imported from the pip twin. Behavioural coverage lives on the pip side.

The load-bearing one is the guidance-marker pair. `ADD:BEGIN`/`ADD:END` is an OPAQUE IDEMPOTENCY
SENTINEL: each installer finds the previous block by exact string match and replaces it in place.
If the two twins ever disagree by a single byte, a project installed with one and re-installed with
the other appends a SECOND block instead of replacing the first. (The marker still names the retired
`sync-guidelines` verb; that is deliberate — the string's job is to match, not to describe.)
"""
import json
import re
import sys

import pytest
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))

from add_method import _installer  # noqa: E402


def _js() -> str:
    return (PKG / "bin" / "cli.js").read_text(encoding="utf-8")


def _js_const(name: str) -> str:
    """The string literal a `const <name> = "...";` line binds in cli.js.

    Only JS string escapes are unwound (`\\"` and `\\\\`) — NOT a blanket `unicode_escape` decode,
    which corrupts the non-ASCII em-dash the marker actually contains.
    """
    m = re.search(rf'^const\s+{re.escape(name)}\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', _js(), re.M)
    assert m, f"cli.js defines no `const {name} = \"...\"`"
    return m.group(1).replace('\\"', '"').replace("\\\\", "\\")


def _code_lines(src: str) -> list:
    """Source lines with whole-line comments dropped — a retired name in a note is not a call."""
    return [ln for ln in src.splitlines() if not ln.strip().startswith(("#", "//", "*", "/*"))]


def test_guidance_markers_are_byte_identical():
    """covers: M1, R:DUPBLOCK — the sentinel must match across twins or re-install duplicates it."""
    assert _js_const("GUIDE_BEGIN") == _installer._GUIDE_BEGIN, (
        "ADD:BEGIN differs between cli.js and _installer.py — a cross-twin re-install would append "
        "a second guidance block instead of replacing the first")
    assert _js_const("GUIDE_END") == _installer._GUIDE_END, "ADD:END differs between the twins"


def test_npm_reads_its_version_from_package_json():
    """covers: M2 — the launcher must not carry a hard-coded version that can drift from the pin."""
    js = _js()
    assert re.search(r'require\(\s*path\.join\(\s*PKG_ROOT\s*,\s*"package\.json"\s*\)\s*\)\.version', js), \
        "cli.js must read its version from package.json, never a literal"
    declared = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["version"]
    assert not re.search(rf'"{re.escape(declared)}"', js), \
        f"cli.js hard-codes the version string {declared!r} — it must only read it from package.json"


def test_both_twins_point_at_the_flat_engine():
    """covers: M3 — 3.0 ships `tooling/{cli.py,add.py}`; the retired `add_engine/` package is gone."""
    js, py = _js(), (PKG / "src" / "add_method" / "_installer.py").read_text(encoding="utf-8")
    for name, src in (("cli.js", js), ("_installer.py", py)):
        live = [ln for ln in _code_lines(src) if "add_engine" in ln]
        assert not live, f"{name} still references the retired add_engine/ package: {live[:2]}"
    assert ".add/tooling/cli.py" in js, "cli.js must point a new project at .add/tooling/cli.py"
    assert ".add/tooling/cli.py" in py, "_installer.py must point a new project at .add/tooling/cli.py"


def test_both_twins_manage_the_corpus_the_same_way():
    """covers: M4 — the vendored corpus installs to `.add/personas-teacher/` on both routes."""
    js = _js()
    assert "personas-teacher" in js, "cli.js must handle the vendored persona corpus"
    pip_targets = {dest for _, dest, _ in _installer.MANAGED if "personas-teacher" in dest}
    assert pip_targets == {".add/personas-teacher"}, \
        f"pip installs the corpus somewhere unexpected: {pip_targets}"


@pytest.mark.skip(reason="known gap (OKF vestigial cleanup): BOTH twins still carry 2.x installer "
                         "furniture — the retired 5-step brand loop, SOUL.md seeding, and --stage. "
                         "Parity HOLDS (they are stale together); this records the shared staleness. "
                         "Un-skip when the installer ceremony is aligned to the 3.0 method.")
def test_installers_carry_no_2x_ceremony():
    """The gap this records, all present in `cli.js` AND `_installer.py` alike:

    - the brand loop is `Specify · Plan · Tests · Build · Verify` — the 2.x five-step model. ADD 3.0
      is three beats (Direction → Build → Verify), which is what the book and skill now teach.
    - both seed `.add/SOUL.md` from `tooling/templates/SOUL.md.tmpl`; 3.0 retired SOUL.md as dead.
    - both still accept `--stage`, the graduation ceremony 3.0 replaced with the three lanes.

    These are shipped user-facing installer behaviour, so removing them is a product decision, not a
    test fix — which is why this is recorded rather than made red.
    """
    js = _js()
    py = (PKG / "src" / "add_method" / "_installer.py").read_text(encoding="utf-8")
    for name, src in (("cli.js", js), ("_installer.py", py)):
        assert "Specify" not in src, f"{name} still brands the retired 5-step loop"
        assert "SOUL" not in src, f"{name} still seeds the retired SOUL.md"
        assert "--stage" not in src, f"{name} still accepts the retired --stage"


def test_retired_verbs_survive_only_inside_the_opaque_marker():
    """covers: M5, E1 — `sync-guidelines`/`migrate`/`guide` are retired.

    The marker is exempt by design (it is matched, not read), so strip the marker text before
    looking — otherwise this test would be permanently unsatisfiable.
    """
    for name, src in (("cli.js", _js()),
                      ("_installer.py", (PKG / "src" / "add_method" / "_installer.py").read_text(encoding="utf-8"))):
        stripped = src.replace(_installer._GUIDE_BEGIN, "")
        for verb in ("sync-guidelines", "add.py migrate", "add.py guide"):
            offenders = [ln for ln in stripped.splitlines()
                         if verb in ln and not ln.strip().startswith(("#", "//", "*"))]
            assert not offenders, f"{name} still offers the retired `{verb}`: {offenders[:2]}"
