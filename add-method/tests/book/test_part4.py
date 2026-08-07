"""book-part4 — Part IV (reference) teaches only the shipped ADD 3.0 engine.

Chapters: 12 .add/ format (NEW) · 13 command reference (NEW) · 14 foundation · 15 lineage · 16 releasing
· 17 components · 18 personas-in-practice. The CLI ref must list only REAL verbs (no phantom capabilities);
ch 15 (lineage) is exempt from the banned-token gate because it narrates the pre-3.0 method as HISTORY.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import book_lint  # noqa: E402

DOCS = REPO / "docs"
# 15 is exempt — it is the lineage chapter and must be free to name the old vocabulary as history.
PART4_CURRENT = ["12-bundle-format.md", "13-command-reference.md", "14-foundation.md",
                 "16-releasing.md", "17-components.md", "18-personas.md"]
EXTRA_BANNED = ["autonomy", "--stage", "stage production", "graduation", "RACI", "roster"]
# the real shipped verbs (from tooling/cli.py) — the CLI reference must cover the core, and must NOT
# advertise a verb the engine does not ship.
REAL_VERBS = ["status", "init", "new", "brief", "freeze", "run", "gate", "done", "learn",
              "milestone-done", "deltas", "fold", "reopen", "milestone-archive", "doctor",
              "wave", "join", "advise", "locate", "todo"]
PHANTOM_VERBS = ["add audit", "add heal", "add graduate", "add stage ", "add delta-append",
                 "add guide", "add migrate", "add waves", "add check "]


def test_part4_no_banned_okf_tokens():
    """covers: M1 — no OKF token in the CURRENT-method reference chapters (15 lineage is exempt)."""
    hits = {}
    for fn in PART4_CURRENT:
        text = (DOCS / fn).read_text(encoding="utf-8")
        found = book_lint.banned_hits(text) + [t for t in EXTRA_BANNED if t in text]
        if found:
            hits[fn] = sorted(set(found))
    assert not hits, f"OKF vocabulary still taught in Part IV (current chapters): {hits}"


def test_part4_cli_reference_covers_the_real_verbs():
    """covers: M2 — ch 13 documents the shipped verb surface."""
    text = (DOCS / "13-command-reference.md").read_text(encoding="utf-8")
    missing = [v for v in REAL_VERBS if f"add {v}" not in text]
    assert not missing, f"13 command reference omits real verbs: {missing}"


def test_part4_cli_reference_has_no_phantom_verbs():
    """covers: M3, R:OVERCLAIM — ch 13 must not advertise a verb the engine does not ship."""
    text = (DOCS / "13-command-reference.md").read_text(encoding="utf-8")
    phantom = [v for v in PHANTOM_VERBS if v in text]
    assert not phantom, f"13 advertises phantom verbs the engine lacks: {phantom}"


def test_part4_format_chapter_teaches_the_node_shape():
    """covers: M4 — ch 12 teaches the typed-node sections + graph.json + the five specs."""
    text = (DOCS / "12-bundle-format.md").read_text(encoding="utf-8")
    for token in ("CARD", "RULES", "PLAN", "CHECKS", "graph.json", ".add/specs"):
        assert token in text, f"12 bundle-format does not teach {token}"


def test_part4_lineage_frames_the_old_method_as_history():
    """covers: M5 — ch 15 names the lineage (AIDD → ADD) and marks the old model as superseded."""
    low = (DOCS / "15-foundations-and-lineage.md").read_text(encoding="utf-8").lower()
    assert "aidd" in low, "15 must trace the AIDD → ADD lineage"
    assert any(w in low for w in ("no longer", "replaced", "superseded", "earlier", "retired")), \
        "15 must mark the pre-3.0 model as superseded, not current"
