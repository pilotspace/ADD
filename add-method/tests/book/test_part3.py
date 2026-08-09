"""book-part3 — Part III (operating the method) teaches only the shipped ADD 3.0 engine.

Chapters: 07 setup+lanes · 08 parallel work (waves) · 09 governance · 10 personas · 11 adoption.
Stages/graduation and the autonomy ladder are gone; the fixed roster/RACI becomes personas.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import book_lint  # noqa: E402

DOCS = REPO / "docs"
PART3 = ["07-setup-and-lanes.md", "08-parallel-work.md", "09-governance.md",
         "10-personas.md", "11-adoption.md"]
EXTRA_BANNED = ["autonomy", "RACI", "auto-with-evidence", "generate-behind-gate",
                "draft-and-review", "auto-ready", "roster", "Proof of Concept",
                "Prototype", "Production-Ready", "graduation-report", "stage-goal"]


def test_part3_no_banned_okf_tokens():
    """covers: M1 — no shared or Part-III OKF token (autonomy ladder, stages, RACI, roster) survives."""
    hits = {}
    for fn in PART3:
        text = (DOCS / fn).read_text(encoding="utf-8")
        found = book_lint.banned_hits(text) + [t for t in EXTRA_BANNED if t in text]
        if found:
            hits[fn] = sorted(set(found))
    assert not hits, f"OKF vocabulary still taught in Part III: {hits}"


def test_part3_uses_add_surface():
    """covers: M2 — every command invokes the real `add <verb>` surface."""
    offenders = []
    for fn in PART3:
        for ln in (DOCS / fn).read_text(encoding="utf-8").splitlines():
            if "add.py" in ln or "new-task" in ln or "freeze --cross" in ln:
                offenders.append((fn, ln.strip()[:80]))
    assert not offenders, f"non-3.0 command surface in Part III: {offenders}"


def test_part3_setup_teaches_the_three_lanes():
    """covers: M3 — ch 07 teaches the quick/task/project lanes + `add init` + the sensitivity floor."""
    text = (DOCS / "07-setup-and-lanes.md").read_text(encoding="utf-8")
    low = text.lower()
    for token in ("quick", "task", "project", "sensitivity"):
        assert token in low, f"07 does not teach the '{token}' lane/floor"
    assert "add init" in text, "07 must teach `add init`"


def test_part3_waves_teach_wave_join_worktree():
    """covers: M4 — ch 08 teaches `add wave` / `add join` over git worktrees."""
    low = (DOCS / "08-parallel-work.md").read_text(encoding="utf-8").lower()
    assert "add wave" in low and "add join" in low and "worktree" in low, \
        "08 must teach wave/join over worktrees"


def test_part3_personas_replace_roles():
    """covers: M5 — ch 10 teaches personas (seed/grow/apply, advise) — not a fixed org roster."""
    text = (DOCS / "10-personas.md").read_text(encoding="utf-8")
    low = text.lower()
    assert "persona" in low and "add advise" in low, "10 must teach personas + `add advise`"


def test_part3_governance_keeps_the_three_outcomes():
    """covers: E1 — ch 09 keeps PASS · RISK-ACCEPTED · HARD-STOP with security always HARD-STOP."""
    text = (DOCS / "09-governance.md").read_text(encoding="utf-8")
    for outcome in ("PASS", "RISK-ACCEPTED", "HARD-STOP"):
        assert outcome in text, f"09 dropped the {outcome} gate outcome"
    assert "security" in text.lower(), "09 must keep security as a HARD-STOP"


def test_part3_persona_never_lowers_a_gate():
    """covers: E2 — ch 10 states a persona never lowers a gate (security stays HARD-STOP)."""
    low = (DOCS / "10-personas.md").read_text(encoding="utf-8").lower()
    assert "never" in low and ("gate" in low) and "hard-stop" in low, \
        "10 must state a persona never lowers a gate and security stays HARD-STOP"
