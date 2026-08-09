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


def test_installers_carry_no_2x_ceremony():
    """covers: M6 — neither twin ships 2.x installer furniture the 3.0 method retired.

    All three were present in `cli.js` AND `_installer.py` alike (parity held; they were stale
    together, which is why a twin-vs-twin diff could never surface it):

    - the brand loop was `Specify · Plan · Tests · Build · Verify`, the 2.x five-step model; ADD 3.0
      is three beats (Direction → Build → Verify), which is what the book and skill teach.
    - both seeded `.add/SOUL.md` from `tooling/templates/SOUL.md.tmpl`; 3.0 retired SOUL.md as dead.
    - both accepted `--stage`, the graduation ceremony the three lanes replaced. It was already
      INERT — `install()` took the parameter and never read it.
    """
    srcs = (("cli.js", _js()),
            ("_cli.py", (PKG / "src" / "add_method" / "_cli.py").read_text(encoding="utf-8")),
            ("_installer.py", (PKG / "src" / "add_method" / "_installer.py").read_text(encoding="utf-8")))
    for name, src in srcs:
        assert "Specify" not in src, f"{name} still brands the retired 5-step loop"
        assert "SOUL" not in src, f"{name} still references the retired SOUL.md"
        # `--stage` may only appear where it is REFUSED or explained, never where it is bound to a
        # value — `add_argument("--stage"` (pip) or an assignment out of the parse loop (npm).
        assert 'add_argument("--stage"' not in src, f"{name} still accepts the retired --stage"
        assert "args.stage" not in src, f"{name} still binds a value for the retired --stage"
    assert not (PKG / "tooling" / "templates" / "SOUL.md.tmpl").exists(), \
        "the SOUL.md template still ships — nothing seeds it any more"


def test_retired_stage_flag_is_refused_not_silently_dropped():
    """covers: M8, R:STAGESHIFT — `--stage` must FAIL on both twins, never fall through.

    npm's parser ends in `else if (a.startsWith("--")) warn("ignoring unknown flag")`, which drops
    the flag but leaves its VALUE on the positional list — where the target directory is read from.
    `init --stage mvp` would then install into ./mvp if that directory happened to exist. So the
    retired flag needs an EXPLICIT refusal, matching the pip twin's argparse hard error.
    """
    js = _js()
    m = re.search(r'else if \(a === "--stage"\) \{\s*\n\s*fail\(', js)
    assert m, "cli.js must refuse --stage explicitly, before the unknown-flag fallback"
    assert js.index(m.group(0)) < js.index('else if (a.startsWith("--")) warn('), \
        "the --stage refusal must come BEFORE the generic unknown-flag warning, or it never fires"


def test_brand_loop_is_the_three_beats():
    """covers: M7 — both twins brand the SAME loop, and it is the one the engine implements."""
    js_loop = re.search(r'const BRAND_LOOP = \[(.*?)\];', _js()).group(1)
    py_loop = re.search(r'^_LOOP = \((.*?)\)',
                        (PKG / "src" / "add_method" / "_installer.py").read_text(encoding="utf-8"), re.M).group(1)
    beats = lambda raw: [t.strip().strip('"\'') for t in raw.split(",") if t.strip()]
    assert beats(js_loop) == beats(py_loop), f"twins brand different loops: {beats(js_loop)} vs {beats(py_loop)}"
    assert beats(js_loop) == ["Direction", "Build", "Verify"], f"not the three beats: {beats(js_loop)}"


def test_npm_publishes_the_whole_flat_engine():
    """covers: M9, R:HEADLESS — the published tarball must carry the dispatch ENTRY, not just the lib.

    `package.json`'s `files` whitelist survived the 3.0 graft unedited: it listed `tooling/add.py`
    and the retired `tooling/add_engine/`, but never `tooling/cli.py`. `npm pack` confirmed the
    omission — a published package installed an engine with no entry point, so every
    `python3 .add/tooling/cli.py status` the skill, the book and the installer pointer tell a user
    to run would fail. Asserted on the whitelist (deterministic, no npm required).
    """
    files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
    for needed in ("tooling/add.py", "tooling/cli.py"):
        assert needed in files, f"package.json `files` omits {needed} — npm would ship a broken engine"
    retired = [f for f in files if "add_engine" in f]
    assert not retired, f"package.json `files` still whitelists the retired engine: {retired}"


def test_both_artifacts_ship_the_same_tooling_payload():
    """covers: M10 — the pip bundle and the npm whitelist agree on what lands in `.add/tooling/`.

    pip installs from the GENERATED `_bundled/` tree (prepare_bundle.py filters it); npm installs
    from `tooling/` as narrowed by the `files` whitelist. The two are independent definitions of the
    same payload, so they can drift silently — `cli.py` going missing from one of them is exactly
    how the npm package came to ship a headless engine. Pin both to the same set.

    NOTE this is the PUBLISHED payload. Running `node bin/cli.js` from a source checkout copies the
    live `tooling/` directory unfiltered, so a dev run also drops repo-only helpers (engine_pin.py,
    spike_cli.py, gate_fixtures.py, …). Those are excluded from the tarball by this whitelist and
    never reach a real user; pip has no such gap because `_bundled/` is filtered at generation.
    """
    bundled = PKG / "src" / "add_method" / "_bundled" / "tooling"
    top = {p.name for p in bundled.iterdir()}
    assert top == {"add.py", "cli.py", "templates"}, \
        f"_bundled/tooling/ ships something unexpected: {sorted(top)}"
    files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
    tooling_rules = {f for f in files if f.startswith("tooling/")}
    assert tooling_rules == {"tooling/add.py", "tooling/cli.py", "tooling/templates/"}, \
        f"npm whitelists a different tooling payload than pip bundles: {sorted(tooling_rules)}"


def test_both_installers_manage_the_same_payload_trees():
    """covers: M11 — the pip and npm MANAGED tables name the same destinations.

    Same drift shape as the tooling payload above, one layer up: `MANAGED` in `_installer.py` and
    its twin in `cli.js` are independent lists of what a real install materializes. A tree added to
    one and not the other installs for half the users — which is what would have happened to
    `personas-index/`, whose whole purpose is to reach the bundle beside the corpus it routes into.
    """
    py_trees = {sub for sub, _dest, _strip in _installer.MANAGED}
    js = _js()
    js_table = js[js.index("const MANAGED = ["):js.index("];", js.index("const MANAGED = ["))]
    # first field of each entry only — the later strings are destination path SEGMENTS
    # ([".claude", "skills", "add"]), not tree names.
    js_trees = set(re.findall(r'^\s*\["([^"]+)"', js_table, re.M))
    assert py_trees == js_trees, \
        f"installer twins disagree on managed trees: pip-only {py_trees - js_trees}, npm-only {js_trees - py_trees}"


def test_the_persona_routing_index_ships_in_both_artifacts():
    """covers: M12 — the corpus and its routing index travel together.

    A bundle with the teacher corpus but no index can read personas and cannot route to one. pip
    ships it via the generated `_bundled/` tree; npm ships it via the `files` whitelist — the two
    independent definitions again, so both are pinned here.
    """
    bundled = PKG / "src" / "add_method" / "_bundled" / "personas-index"
    assert (bundled / "use-when.md").is_file(), \
        "the pip bundle has no persona routing index — run scripts/prepare_bundle.py"
    files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
    assert "personas-index/" in files, "the npm whitelist drops the persona routing index"
    assert not list((PKG / "personas-teacher").rglob("use-when.md")), \
        "the index is inside the verbatim vendor tree — update_teacher.py would erase it"


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
