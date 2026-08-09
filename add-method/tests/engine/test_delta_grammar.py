"""learn() must emit the frozen delta grammar (deltas.md §grammar), open by default.

    - [<COMPETENCY> · open] <learning> (evidence: <pointer>)

Before this, learn() wrote an untagged `- <lesson> — evidence: …` line, so `deltas` (list open) and
`fold` (retag open→folded) had no status to act on. The competency derives from the lens, so the
method vocabulary the skill teaches lands as the tag the grammar requires.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _spec(root, name):
    return (root / "specs" / f"{name}.md").read_text(encoding="utf-8")


def test_learn_writes_open_tagged_grammar(tmp_path):
    """covers: M1 — a delta matches the frozen [COMP · open] grammar, evidence closing it."""
    add.init(tmp_path, "code", "T")
    ok, _ = add.learn(tmp_path, "method", "budgets need a unit", evidence="/runs/1.md")
    assert ok is True
    assert re.search(r"^- \[ADD · open\] budgets need a unit \(evidence: /runs/1\.md\)\s*$",
                     _spec(tmp_path, "method"), re.M), _spec(tmp_path, "method")


def test_competency_derives_from_lens(tmp_path):
    """covers: M1 — domain→DDD, quality→TDD (the lens names the competency tag)."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "domain", "d-lesson", evidence="e")
    add.learn(tmp_path, "quality", "q-lesson", evidence="e")
    assert re.search(r"^- \[DDD · open\] d-lesson ", _spec(tmp_path, "domain"), re.M)
    assert re.search(r"^- \[TDD · open\] q-lesson ", _spec(tmp_path, "quality"), re.M)


def test_no_evidence_still_refused(tmp_path):
    """covers: R:NOEVIDENCE — an evidence-less lesson writes nothing."""
    add.init(tmp_path, "code", "T")
    ok, _ = add.learn(tmp_path, "method", "an opinion", evidence=None)
    assert ok is False
    assert "an opinion" not in _spec(tmp_path, "method")


def test_unknown_lens_refused(tmp_path):
    """covers: R:UNKNOWNLENS — a lens naming no spec file is refused."""
    add.init(tmp_path, "code", "T")
    ok, note = add.learn(tmp_path, "nonesuch", "x", evidence="e")
    assert ok is False and "lens" in note.lower()
