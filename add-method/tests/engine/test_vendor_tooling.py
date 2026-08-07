"""`add init` vendors its own tooling so the bundle runs standalone — engine + corpus, version-stamped.

The skill calls the engine at an in-repo path (`add/scripts/cli.py`); a project created elsewhere has
no such path. So `init` copies the engine (`add.py` + `cli.py`) and the seed persona corpus into
`.add/tooling/`, and records the engine version in `index.md` as `tooling_engine:`. A missing source
degrades (a note), never crashes; a re-run never clobbers a vendored file (idempotent).
"""
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_init_vendors_the_engine(tmp_path):
    """covers: M1 — the engine lands in .add/tooling/."""
    add.init(tmp_path, "code", "T")
    assert (tmp_path / "tooling" / "add.py").is_file(), "add.py must be vendored"
    assert (tmp_path / "tooling" / "cli.py").is_file(), "cli.py must be vendored"


def test_vendored_engine_imports(tmp_path):
    """covers: M1 — the vendored engine is complete: cli.py imports and exposes build_parser."""
    add.init(tmp_path, "code", "T")
    tooling = tmp_path / "tooling"
    sys.path.insert(0, str(tooling))
    try:
        spec = importlib.util.spec_from_file_location("vendored_cli", tooling / "cli.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "build_parser"), "the vendored cli.py must expose build_parser"
    finally:
        sys.path.remove(str(tooling))
        sys.modules.pop("vendored_cli", None)


def test_init_vendors_the_corpus(tmp_path):
    """covers: M2 — the seed persona archetypes are vendored.

    Graft note: the corpus dest moved from `tooling/personas-teacher/` (flat) to the
    bundle-root `personas-teacher/` (nested by division). Proof is unchanged — the seed
    corpus lands vendored — but the dest is the new root tree and the archetypes are nested,
    so we recurse.
    """
    add.init(tmp_path, "code", "T")
    corpus = tmp_path / "personas-teacher"
    assert corpus.is_dir(), "the teacher corpus dir must be vendored at the bundle root"
    assert list(corpus.rglob("*.md")), "at least one seed persona archetype must be vendored (nested)"


def test_vendored_corpus_is_not_scanned_as_nodes(tmp_path):
    """covers: M2 — vendored tooling is engine material, not project graph (seed personas ≠ live nodes).

    Graft note: the seed corpus moved from `tooling/personas-teacher/` to the bundle-root
    `personas-teacher/`. `scan()`'s own docstring says the vendored corpus is "never project
    graph, never a stray" — so this proof is unchanged, only its target path moves. Both the
    vendored engine copy (`tooling/`) AND the vendored seed corpus (`personas-teacher/`) must
    stay out of the graph and out of the stray list.
    """
    add.init(tmp_path, "code", "T")
    graph = add.scan(tmp_path)
    assert not any("/tooling/" in cid for cid in graph), \
        "the vendored engine copy must not appear as bundle nodes"
    assert not any("/personas-teacher/" in cid or cid.startswith("/personas-teacher/") for cid in graph), \
        "the vendored seed corpus must not appear as bundle nodes"
    strays = []
    add.scan(tmp_path, strays=strays)
    assert not any(s.startswith("tooling/") for s in strays), \
        "vendored engine material must not be flagged as a stray either"
    assert not any(s.startswith("personas-teacher/") for s in strays), \
        "vendored seed corpus must not be flagged as a stray either"


def test_init_stamps_tooling_engine(tmp_path):
    """covers: M3, M4 — index.md records the engine version, equal to the ENGINE constant."""
    add.init(tmp_path, "code", "T")
    fm = add.read(tmp_path / "index.md", "T0")["fm"] or {}
    assert fm.get("tooling_engine") == add.ENGINE, "tooling_engine must equal the single ENGINE constant"


def test_init_degrades_on_missing_source(tmp_path, monkeypatch):
    """covers: R:MISSINGSRC — a missing engine source is a note, never an exception."""
    monkeypatch.setattr(add, "TOOLING_SRC", tmp_path / "no-such-engine-dir")
    monkeypatch.setattr(add, "CORPUS_SRC", tmp_path / "no-such-corpus-dir")
    _graph, _created, note = add.init(tmp_path, "code", "T")  # must not raise
    assert not (tmp_path / "tooling" / "add.py").exists(), "nothing to copy → nothing vendored"
    assert "vendor" in note.lower(), "the degrade must be reported in the note"


def test_init_is_idempotent_for_tooling(tmp_path):
    """covers: R:CLOBBER — a second init never overwrites a vendored file."""
    add.init(tmp_path, "code", "T")
    vendored = tmp_path / "tooling" / "add.py"
    vendored.write_text("# a human edited the vendored engine\n", encoding="utf-8")
    add.init(tmp_path, "code", "T")  # re-run
    assert vendored.read_text(encoding="utf-8") == "# a human edited the vendored engine\n", \
        "re-running init must not clobber an existing vendored file"
