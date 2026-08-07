"""Red suite for e3 `build-init-profiles` — the `init` verb.

One test per Must / Reject of tasks/build-init-profiles. The acceptance test for M1 is the M0
conformance oracle itself: a bundle this engine creates must satisfy the validator that was
written before the engine existed, with no hand editing.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

VALIDATOR = REPO / "scripts" / "validate_bundle.py"


def validate(root: Path):
    """Run M0's oracle over a bundle. Returns (exit_code, stdout)."""
    r = subprocess.run([sys.executable, str(VALIDATOR), str(root)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


# --------------------------------------------------------- the oracle accepts it (M1)


def test_init_output_validates(tmp_path):
    """covers: M1, R:HANDFIX — the bundle validates on first run, unedited.

    This is the whole point of the verb. If it fails, `init` is producing something only it
    believes in.
    """
    add.init(tmp_path, "code", "Test project")
    code, out = validate(tmp_path)
    assert code == 0, f"a freshly created bundle failed the M0 oracle:\n{out}"
    assert "CONFORMS" in out


def test_init_creates_minimum(tmp_path):
    """covers: M1 — FORMAT §1's three-file minimum bundle."""
    add.init(tmp_path, "code", "Test project")
    for name in ("index.md", "log.md", "PROJECT.md"):
        assert (tmp_path / name).is_file(), f"{name} was not created"


# ------------------------------------------------------ init never clobbers (M2)


def test_init_is_idempotent(tmp_path):
    """covers: M2, R:CLOBBER — a second init reports and changes no byte."""
    add.init(tmp_path, "code", "Test project")
    before = {p: p.read_bytes() for p in sorted(tmp_path.rglob("*.md"))}

    graph, created, note = add.init(tmp_path, "code", "Test project")
    assert created == [], "a second init created files"
    assert note, "a no-op init said nothing"

    after = {p: p.read_bytes() for p in sorted(tmp_path.rglob("*.md"))}
    assert after == before, "a second init changed bytes on disk"


def test_init_never_overwrites_edited_node(tmp_path):
    """covers: M2, R:CLOBBER — a human's edit outranks the template, always."""
    add.init(tmp_path, "code", "Test project")
    index = tmp_path / "index.md"
    index.write_text(index.read_text() + "\nHUMAN EDIT — must survive\n")

    add.init(tmp_path, "doc", "Different title")
    assert "HUMAN EDIT — must survive" in index.read_text()


# ------------------------------------------------ profiles are data, not branches (M3)


def test_profile_selects_specs(tmp_path):
    """covers: M3 — different profiles produce different spec sets."""
    a, b = tmp_path / "a", tmp_path / "b"
    add.init(a, "code", "A")
    add.init(b, "doc", "B")
    specs_a = {p.name for p in (a / "specs").glob("*.md")}
    specs_b = {p.name for p in (b / "specs").glob("*.md")}
    assert specs_a and specs_b
    assert specs_a != specs_b, "two profiles produced identical bundles"


def test_new_profile_needs_no_engine_change(tmp_path):
    """covers: M3, R:PROFILECODE — a profile added at runtime works, with no new branch.

    If this fails, profiles are branches wearing a dict costume and goal 2's closed-lens
    claim is false.
    """
    add.PROFILES["research"] = {"method": "how enquiry proceeds", "evidence": "what counts as proof"}
    try:
        graph, created, note = add.init(tmp_path, "research", "R")
        names = {p.name for p in (tmp_path / "specs").glob("*.md")}
        assert names == {"method.md", "evidence.md"}, f"runtime profile ignored: {names}"
        assert validate(tmp_path)[0] == 0
    finally:
        del add.PROFILES["research"]


# ----------------------------------------------------------- attribution (M4) & next (M5)


def test_every_file_is_attributed(tmp_path):
    """covers: M4 — nothing in a new bundle is unattributed (OKF §10)."""
    graph, created, note = add.init(tmp_path, "code", "Test project")
    assert created, "init created nothing"
    for cid, node in graph.items():
        gen = (node["fm"] or {}).get("generated")
        assert isinstance(gen, dict), f"{cid} has no `generated` map"
        assert gen.get("by") and gen.get("at"), f"{cid} is unattributed: {gen}"


def test_init_prints_next(tmp_path):
    """covers: M5 — the engine teaches at the moment of use (law 4)."""
    graph, created, note = add.init(tmp_path, "code", "Test project")
    assert "next:" in note.lower(), f"no next: line in {note!r}"
    assert "add " in note, "the next: line does not name a runnable command"
