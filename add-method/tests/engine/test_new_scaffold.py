"""`add new` must ship a usable scaffold — no unexpanded placeholder in the CARD.

Surfaced by the skill cold-drive (2026-08-06): a created task carried
`next: add freeze {slug}` literally, because the BODIES template's `{slug}` marker was never
substituted with the node's own slug.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_new_task_card_has_no_unexpanded_slug_marker(tmp_path):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "mul-fn", title="Add mul")
    text = (tmp_path / cid.lstrip("/")).read_text(encoding="utf-8")
    assert "{slug}" not in text, "the CARD scaffold leaked an unexpanded {slug} marker"
    assert "mul-fn" in text, "the CARD `next:` affordance does not name the real slug"


def test_new_scaffold_pins_the_corrected_affordance(tmp_path):
    """covers: M6 — RE-AIMED, not deleted. The scaffold's `next:` stays a pinned interface;
    it was the VALUE that was wrong, not the pinning.

    A freshly created node carries nothing but placeholders, and `freeze` is structurally
    guaranteed to refuse it (add.py:1394) — so the one string the CARD must not carry is the
    verb that refusal names.
    """
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "mul-fn", title="Add mul")
    card = next(ln for ln in (tmp_path / cid.lstrip("/"))
                .read_text(encoding="utf-8").splitlines() if ln.startswith("beat:"))
    assert not card.strip().startswith("beat: direction"), card
    assert "author" in card.lower() and "mul-fn" in card, card
