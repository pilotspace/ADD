"""Which `brief` is pure — the function is, the verb is not, and both sides are now pinned.

Red-first for `/tasks/brief-is-not-read-only.md`.

A review agent read "`brief` is read-only" in `add.brief`'s docstring, declared the verb safe to
run during an audit, and then found `cli.py` calling `brief_stamp` on any frozen Task. The
sentence is true of the FUNCTION and false of the VERB, and it did not say which.

`docs/13-command-reference.md` already documents the stamp accurately, so the documentation was
not the defect — the docstring was, and nothing pinned the boundary either way. A check on one
side alone is satisfied by moving the write across it, so both sides are asserted here.
"""

import hashlib
import inspect
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from test_done_reads_the_verdict import _authored, _bundle  # noqa: E402


def _fingerprint(root):
    """Every file's bytes — CONTENT, not a stamp count, so a write anywhere is caught."""
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(root).rglob("*")) if p.is_file()}


def _entries(root, cid):
    return len(re.findall(r"act: brief", (Path(root) / cid.lstrip("/")).read_text(encoding="utf-8")))


@pytest.fixture
def frozen(tmp_path):
    root = _bundle(tmp_path / ".add")
    cid = _authored(root, "compiled")
    ok, note = add.freeze(root, cid, by="H", authority="human")[:2]
    assert ok, f"the fixture did not freeze, so the stamping path is not reached: {note}"
    return root, cid


def test_the_compile_writes_nothing(frozen):
    """M2, R:BYNAME, E1 — the one command that would have told the reviewer the truth."""
    root, cid = frozen
    before = _fingerprint(root)
    add.brief(root, cid)
    assert _fingerprint(root) == before, \
        "`add.brief()` changed the bundle — the pure half of the boundary is not pure"


def test_the_verb_records_one_entry(frozen):
    """M3, E2 — the stamping path is where the write lives."""
    root, cid = frozen
    assert _entries(root, cid) == 0, "the fixture already carries an entry"
    digest, _note = add.brief_stamp(root, cid, by="cli")
    assert digest, "a frozen Task recorded no brief entry"
    assert _entries(root, cid) == 1, f"expected one entry, found {_entries(root, cid)}"


def test_an_unfrozen_node_records_none(tmp_path):
    """M4, E3, A4 — before the seal there is no sealed direction for a brief to enter."""
    root = _bundle(tmp_path / ".add")
    cid = _authored(root, "unsealed")
    before = _fingerprint(root)
    digest, _note = add.brief_stamp(root, cid, by="cli")
    assert not digest, "an unfrozen node recorded a brief entry"
    assert _fingerprint(root) == before, "an unfrozen node was written to anyway"


def test_each_compile_records_its_own_entry(frozen):
    """E4, M5 — I assumed re-running was idempotent. It is not, and that is correct.

    The gate asks whether ANY `act: brief` sits after the last (re)freeze, so a per-compile
    trail records what happened without changing what the gate reads. M5 forbids changing
    behaviour to match an assumption, so the assumption is what changed.
    """
    root, cid = frozen
    add.brief_stamp(root, cid, by="cli")
    first = _entries(root, cid)
    add.brief_stamp(root, cid, by="cli")
    assert _entries(root, cid) == first + 1, "a compile stopped recording its own entry"
    assert add.brief_stamp(root, cid, by="cli")[0], "the node stopped reading as briefed"


def test_the_docstring_names_the_function():
    """M1, A2, A6, A8, A9 — the sentence must say WHICH `brief`, in the same sentence."""
    doc = inspect.getdoc(add.brief_stamp) or ""
    assert "brief()" in doc, \
        "the docstring still says `brief` without saying whether it means the function or the verb"
    assert "cli" in doc.lower(), \
        "the docstring does not say the CLI wrapper stamps, so `add brief` still reads as pure"


def test_no_write_moved():
    """M5, R:NEWWRITE, A3 — this task states and pins a boundary; it does not move one."""
    assert "_transition(" not in inspect.getsource(add.brief), \
        "a write appeared in the pure half (R:NEWWRITE)"
    assert "_transition(" in inspect.getsource(add.brief_stamp), \
        "the write left `brief_stamp` — the boundary moved instead of being pinned"
