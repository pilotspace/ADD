"""Rounds 7–8 and the SWE-bench Lite pilot (.add/tasks/lean-bounded-fixes.md): what the isolated
measurements say to keep, cut and correct."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
SKILL = PKG / "skill" / "add"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _section(text: str, start: str) -> str:
    return text.split(start, 1)[1].split("\n## ", 1)[0] if start in text else ""


def test_floor_is_shape_change_not_touch():
    """Every SWE-bench fix touches a public API; only one that changes its shape breaks a consumer."""
    flat = _flat(SKILL / "SKILL.md")
    assert "changes the shape of a surface other code consumes" in flat
    assert "restores" in flat and "without changing its shape" in flat


def test_quick_commit_carries_its_lane_and_evidence():
    flat = _flat(SKILL / "SKILL.md")
    assert "lane: quick —" in flat and "red→green:" in flat, "Quick names no commit artifact"


def test_assumptions_hold_only_real_silences():
    flat = _flat(SKILL / "SKILL.md")
    assert "a dimension the request settles gets no line" in flat
    assert "`- none — <why>`" in flat


def test_persona_index_path_resolves():
    for name in ("SKILL.md", "references/personas.md"):
        text = (SKILL / name).read_text(encoding="utf-8")
        assert "`.add/personas-index/use-when.md`" in text, f"{name} lacks the installed path"
        assert " `personas-index/use-when.md`" not in text, f"{name} still has the bare path"


def test_readmes_state_the_isolated_price():
    for path in (ROOT / "README.md", PKG / "README.md"):
        flat = _flat(path)
        assert "4.0–5.1× the minutes" not in flat, f"{path}: the contaminated minutes survive"
        assert "1.3–1.9× the dollars" in flat and "1.8–2.4× the minutes" in flat, path
        assert "--effort low" in flat, f"{path}: no effort recommendation"
        assert "security-guidance" in flat, f"{path}: the contamination is not named"
        assert "0.83 vs 0.19" not in flat, f"{path}: round 8's single-round mutation gap overstates it"
        assert "0.81 vs 0.43" in flat, f"{path}: the pooled rounds 8–9 mutation gap is missing"
