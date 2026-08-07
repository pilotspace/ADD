"""book-part2 — Part II (the three-beat loop) teaches only the shipped ADD 3.0 engine.

Chapters: 02 loop · 03 Direction (merge of old specify+contract+tests) · 04 Build · 05 Verify · 06 loop.
Vocab gate + the OKF §-numbered file model must be gone; durable pedagogy stays.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import book_lint  # noqa: E402

DOCS = REPO / "docs"
PART2 = ["02-the-flow.md", "03-direction.md", "04-build.md", "05-verify.md", "06-the-loop.md"]
# OKF constructs specific to the method chapters: the §-numbered file model + old artifact names.
EXTRA_BANNED = ["§1", "§3", "§4", "§5", "§6", "§7", "PLAN.md", "SPEC.md", "contracts/",
                "specification bundle", "autonomy", "generate-behind-gate", "waves view"]


def test_part2_no_banned_okf_tokens():
    """covers: M1 — no shared or Part-II OKF token appears in any Part-II chapter."""
    hits = {}
    for fn in PART2:
        text = (DOCS / fn).read_text(encoding="utf-8")
        found = book_lint.banned_hits(text) + [t for t in EXTRA_BANNED if t in text]
        if found:
            hits[fn] = sorted(set(found))
    assert not hits, f"OKF vocabulary still taught in Part II: {hits}"


def test_part2_uses_add_surface():
    """covers: M2 — every command invokes the real `add <verb>` surface."""
    offenders = []
    for fn in PART2:
        for ln in (DOCS / fn).read_text(encoding="utf-8").splitlines():
            if "add.py" in ln or "new-task" in ln or "freeze --cross" in ln:
                offenders.append((fn, ln.strip()[:80]))
    assert not offenders, f"non-3.0 command surface in Part II: {offenders}"


def test_part2_direction_teaches_the_three_movements():
    """covers: M3 — the merged ch 03 teaches RULES, PLAN, and CHECKS (the Direction beat's shape)."""
    text = (DOCS / "03-direction.md").read_text(encoding="utf-8")
    for token in ("RULES", "PLAN", "CHECKS"):
        assert token in text, f"03 Direction no longer teaches {token}"


def test_part2_beats_are_named():
    """covers: M4 — chapter 02 names the three beats (direction · build · verify)."""
    text = (DOCS / "02-the-flow.md").read_text(encoding="utf-8").lower()
    assert "direction" in text and "build" in text and "verify" in text, \
        "chapter 02 must name the three beats"


def test_part2_verify_keeps_residue_lenses():
    """covers: E2 — ch 05 keeps the three residue lenses with security as a HARD-STOP."""
    text = (DOCS / "05-verify.md").read_text(encoding="utf-8").lower()
    for lens in ("security", "concurrency", "architecture"):
        assert lens in text, f"05 Verify dropped the {lens} residue lens"
    assert "hard-stop" in text or "hard stop" in text, "05 Verify must keep security as a HARD-STOP"
