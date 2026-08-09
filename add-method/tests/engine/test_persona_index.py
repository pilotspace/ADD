"""The persona roster is discoverable in the compiled index (A4, task 1).

A Persona carries a machine-readable `use-when:`; the compiled `index.md` gains a `## Personas`
section listing each lens with it. The row detail is the `use-when:` FRONTMATTER — not a hand-authored
index tail the generic branch would preserve.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _fm(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def test_new_persona_scaffolds_use_when(tmp_path):
    """covers: M1 — a freshly created Persona carries a `use-when:` frontmatter key."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Persona", "backend-systems", title="backend lens")
    assert re.search(r"^use-when:", _fm((tmp_path / cid.lstrip("/")).read_text(encoding="utf-8")), re.M)


def test_index_lists_personas_with_use_when(tmp_path):
    """covers: M2 — the rebuilt index has a `## Personas` section showing the persona's use-when."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Persona", "sec-rev", title="security lens", **{"use-when": "auth or crypto in scope"})
    add.doctor_sync(tmp_path)
    body = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "## Personas" in body, body
    assert "auth or crypto in scope" in body, body


def test_persona_row_renders_frontmatter_not_tail(tmp_path):
    """covers: R:USEWHENAUTHORED — the row detail is the use-when value, not a stale authored tail."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Persona", "sec-rev", title="security lens", **{"use-when": "the-frontmatter-value"})
    # Pre-seed the index with a stale hand-authored tail for that persona row.
    idx = tmp_path / "index.md"
    raw, _ = add.split(idx.read_text(encoding="utf-8"))
    idx.write_text(f"---\n{raw}\n---\n\n## Personas\n\n- [security lens](personas/sec-rev.md) — STALE-AUTHORED-TAIL\n",
                   encoding="utf-8")
    add.doctor_sync(tmp_path)
    body = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "the-frontmatter-value" in body, body
    assert "STALE-AUTHORED-TAIL" not in body, "the persona row must render use-when, not the preserved tail"
