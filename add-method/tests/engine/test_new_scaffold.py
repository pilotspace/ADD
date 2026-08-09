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
    assert "next: add freeze mul-fn" in text, "the CARD `next:` affordance does not name the real slug"
