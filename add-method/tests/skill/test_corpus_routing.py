"""Every persona in the vendored teacher corpus must be reachable through the routing index.

`personas-teacher/` is a byte-verbatim third-party snapshot that `update_teacher.py` replaces with
`shutil.rmtree`. So the corpus cannot be edited here — and a refresh that drops, renames or
reorganises personas would shrink what is routable without anyone noticing, because the index is
generated and nobody re-reads a generated file.

The guard is REGENERATE-AND-COMPARE: it proves in one assertion that the committed index is neither
hand-edited nor stale, and it is derived by construction rather than pinning a file list that would
rot on the very next refresh.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "personas-teacher"
INDEX = REPO / "personas-index" / "use-when.md"
GENERATOR = REPO / "scripts" / "build_persona_index.py"

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
DESCRIPTION = re.compile(r"^description:\s*(.+)$", re.M)


def _is_persona(path: Path) -> bool:
    """An agent definition carries `description:`; a playbook, runbook or example does not.

    This is the GENERATOR's own rule, applied here rather than restated as a list. The generator
    docstring anticipated three files (README, VENDOR, LICENSE); the corpus actually skips 22,
    including a whole `strategy/` playbook tree — correct, but never said out loud at that size.
    """
    m = FRONTMATTER.match(path.read_text(encoding="utf-8", errors="replace"))
    return bool(m and DESCRIPTION.search(m.group(1)))


def _corpus_files():
    files = sorted(CORPUS.rglob("*.md"))
    assert files, f"teacher corpus is empty or missing at {CORPUS} — refusing to report coverage"
    return files


def test_every_corpus_file_is_indexed_or_accounted():
    """M1 — indexed, or demonstrably not an agent definition. No third category."""
    text = INDEX.read_text(encoding="utf-8")
    unaccounted = sorted(str(p.relative_to(CORPUS)) for p in _corpus_files()
                         if _is_persona(p) and p.stem not in text)
    assert not unaccounted, (f"personas the routing index cannot reach: {unaccounted} — they carry "
                             f"a description: so they ARE agent definitions, and nothing routes to them")


def test_index_reaches_every_agent_division():
    """M2 — every division holding agent definitions is routable.

    Named explicitly because this milestone was drafted on the belief that finance and academic
    were thin. They are not, and this pins that they stay reachable across a vendor refresh.
    """
    text = INDEX.read_text(encoding="utf-8")
    divisions = {}
    for p in _corpus_files():
        rel = p.relative_to(CORPUS)
        if len(rel.parts) > 1 and _is_persona(p):
            divisions.setdefault(rel.parts[0], []).append(p.stem)
    assert divisions, "no divisions carry agent definitions — the corpus shape changed"
    for expected in ("finance", "academic"):
        assert expected in divisions, f"the corpus no longer ships a `{expected}` division"
    unreachable = sorted(d for d, members in divisions.items()
                         if not any(m in text for m in members))
    assert not unreachable, f"divisions with no routable persona at all: {unreachable}"


def test_index_is_regenerable():
    """M3 + R:HANDEDIT — the generator's own staleness check proves derivation AND no hand-edit.

    An earlier draft invented a `--stdout` mode, found it absent, and pytest.skip'd — which would
    have bound NOTHING: the engine records a skip as `skip`, never `pass`, so the gate refuses a
    referent whose only check was skipped. The generator already ships `--check` and exits
    non-zero when the committed index differs from a fresh render. No new mode, no skip.
    """
    out = subprocess.run([sys.executable, str(GENERATOR), "--check"],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, (
        f"personas-index/use-when.md is hand-edited or stale against the corpus:\n"
        f"{out.stdout}{out.stderr}\n"
        f"Regenerate with `python3 add-method/scripts/build_persona_index.py`.")


def test_empty_corpus_fails_loud():
    """E1 — zero personas must raise, never read as complete coverage."""
    global CORPUS
    real, missing = CORPUS, REPO / "personas-teacher-does-not-exist"
    try:
        CORPUS = missing
        with pytest.raises(AssertionError, match="empty or missing"):
            _corpus_files()
    finally:
        CORPUS = real


def test_check_reports_what_it_skipped():
    """M4 — the silence is the defect.

    `--check` reported "232 personas" and said nothing about the 22 corpus files it passed over.
    A persona that loses its `description:` in a vendor refresh simply stops being routable, and
    the only signal is a number that quietly gets smaller. Coverage has to be stated to be read.
    """
    out = subprocess.run([sys.executable, str(GENERATOR), "--check"],
                         capture_output=True, text=True, cwd=REPO)
    report = out.stdout + out.stderr
    skipped = [p for p in _corpus_files() if not _is_persona(p)]
    assert str(len(skipped)) in report, (
        f"--check does not say how many corpus files it skipped ({len(skipped)} today); "
        f"it reported only:\n  {report.strip()}")
    assert re.search(r"skip", report, re.I), \
        "--check never uses the word 'skipped' — the exclusion stays invisible to whoever reads it"
