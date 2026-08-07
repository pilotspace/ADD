"""book-part1 — Part I (00 the shift, 01 principles) teaches only the shipped ADD 3.0 engine.

Vocab gate: no OKF/2.x token survives, and the durable content (the nine principles) is not lost.
Red-first: the chapters are still the renumbered-but-OKF originals, so the banned-token check fails.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import book_lint  # noqa: E402

DOCS = REPO / "docs"
PART1 = ["00-introduction.md", "01-principles.md"]
# Part-I-specific OKF constructs beyond the shared list (bare-word bans are safe in these two files).
EXTRA_BANNED = ["autonomy:", "autonomy level", "autonomy ladder", "generate-behind-gate",
                "draft-and-review", "SETUP-REVIEW", "playbook/", "Part III", "Part IV"]


def test_part1_no_banned_okf_tokens():
    """covers: M1 — no shared or Part-I OKF token appears in 00 or 01."""
    hits = {}
    for fn in PART1:
        text = (DOCS / fn).read_text(encoding="utf-8")
        found = book_lint.banned_hits(text) + [t for t in EXTRA_BANNED if t in text]
        if found:
            hits[fn] = sorted(set(found))
    assert not hits, f"OKF vocabulary still taught in Part I: {hits}"


def test_part1_uses_add_surface():
    """covers: M2 — every fenced command line invokes the real `add <verb>` surface, never add.py."""
    offenders = []
    for fn in PART1:
        for ln in (DOCS / fn).read_text(encoding="utf-8").splitlines():
            if "add.py" in ln or "new-task" in ln or "freeze --cross" in ln:
                offenders.append((fn, ln.strip()))
    assert not offenders, f"non-3.0 command surface in Part I: {offenders}"


def test_part1_nine_principles_intact():
    """covers: M3 (regression floor) — chapter 01 still states nine numbered principles."""
    import re
    text = (DOCS / "01-principles.md").read_text(encoding="utf-8")
    principles = re.findall(r"(?m)^##\s+(\d)\.\s", text)
    assert [int(p) for p in principles] == list(range(1, 10)), \
        f"expected principles 1..9, found {principles}"
