"""The address every verb tells you to cite is an address a verb can read back.

Red-first for `/tasks/address-dereferences.md`.

`deltas` and `search` both print `/specs/method.md#M33`, and `search`'s own `next:` line says to
cite it. Measured before this task:

    add show /specs/method.md#M33   ->  R:NOSUCHNODE
    add search M33                  ->  no hit          (M33 IS in method.md)

So the only way to read one lesson in full was a 12,762-byte whole-spec read. X4 made the two
doors agree on how to WRITE the address; nothing made it resolvable. This closes that, and it
lands BEFORE `deltas` is windowed — truncating a listing whose full text costs 12.7 KB to
recover would make the tool worse.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

LESSON = ("- [ADD · Z1 · open · 2026-09-04] a lesson worth citing by its address"
          " (evidence: /tasks/t-one.md)")
TWIN = ("- [ADD · Z1 · open · 2026-09-04] a second lesson wearing the same id"
        " (evidence: /tasks/t-one.md)")


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="address fixture")
    add.new(root, "Task", "t-one", title="a task to cite")
    spec = root / "specs" / "method.md"
    spec.write_text(spec.read_text(encoding="utf-8").rstrip() + f"\n\n{LESSON}\n",
                    encoding="utf-8")
    return root


def test_the_printed_address_reads_back(bundle):
    """M1, M2, R:WHOLESPEC, E1, A10 — the exact string `deltas` emits, driven through `show`."""
    note = add.deltas(bundle, status="open")[1]
    address = next(w for ln in note.splitlines() for w in ln.split()
                   if w.startswith("/specs/") and "#" in w)
    assert address == "/specs/method.md#Z1", f"deltas printed an unexpected address: {address}"
    view, shown = add.show(bundle, address, 1)
    assert view is not None, f"the address `deltas` printed does not resolve: {shown}"
    assert "a lesson worth citing by its address" in shown, \
        f"the lesson's own text is not in the answer:\n{shown}"
    spec_body = (bundle / "specs" / "method.md").read_text(encoding="utf-8")
    assert len(shown) < len(spec_body) / 2, \
        "reading one lesson returned something the size of the whole spec (R:WHOLESPEC)"


def test_a_missing_fragment_refuses_and_names_the_file(bundle):
    """M4, R:SILENTMISS, E2, A6 — a bad id must not fall back to the file."""
    view, note = add.show(bundle, "/specs/method.md#ZZ99", 1)
    assert view is None, "a fragment naming no lesson resolved to the file (R:SILENTMISS)"
    # The FILE was found and the LESSON was not — the reader must learn which half was wrong.
    assert "ZZ99" in note and "/specs/method.md" in note, \
        f"the refusal does not name both the id and the file searched:\n{note}"
    assert "lesson" in note.lower() or "delta" in note.lower(), \
        f"the refusal reads as a missing FILE, not a missing lesson:\n{note}"
    assert "next:" in note, f"the refusal names no fix:\n{note}"


def test_two_lessons_one_id_refuse(bundle):
    """R:IDCOLLIDE, A15 — the same rule the node path already follows."""
    spec = bundle / "specs" / "method.md"
    spec.write_text(spec.read_text(encoding="utf-8").rstrip() + f"\n{TWIN}\n", encoding="utf-8")
    view, note = add.show(bundle, "/specs/method.md#Z1", 1)
    assert view is None, "a duplicated id resolved to one of the two lessons"
    assert "2" in note, f"the refusal does not say how many collided:\n{note}"


def test_an_address_without_a_fragment_is_unchanged(bundle):
    """M5, E3 — this task ADDS a reading; it changes none."""
    assert add.resolve_ref(bundle, "t-one")[0] == "/tasks/t-one.md"
    assert add.resolve_ref(bundle, "/tasks/t-one.md")[0] == "/tasks/t-one.md"
    assert add.resolve_ref(bundle, "/specs/method.md")[0] == "/specs/method.md"
    assert add.resolve_ref(bundle, "no-such-thing")[0] is None


def test_a_lesson_is_findable_by_its_id(bundle):
    """M3, E5 — a lesson is findable by the address it is cited at."""
    hits, note = add.search(bundle, "Z1")
    assert hits, f"a lesson is not findable by its own id:\n{note}"
    assert any("#Z1" in h[0] for h in hits), f"the id hit does not carry its address: {hits}"


def test_free_text_search_is_unchanged(bundle):
    """A3, E5 — the id is an ADDITIONAL field, never a replacement."""
    hits, _ = add.search(bundle, "worth citing by its address")
    assert hits, "a free-text query stopped matching delta text"


def test_a_lesson_shows_its_relations(bundle):
    """A9, E4, A7 — an unlinked lesson shows an empty related section, not an error."""
    view, note = add.show(bundle, "/specs/method.md#Z1", 1)
    assert view is not None, f"the lesson did not resolve: {note}"
    assert "related" in note.lower(), \
        f"a lesson with no relations shows no related section at all:\n{note}"


def test_format_states_the_address_resolves():
    """M6, A5, A11 — `citable` and `resolvable` are different promises."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    # §3.3 is where the concept address is defined; the promise belongs beside the grammar (A16).
    s33 = fmt.split("### §3.3")[1].split("\n### ")[0]
    assert "readable**, not merely citable" in s33, \
        "§3.3 defines the concept address without promising a reader can READ IT BACK"
    assert "never falls back to the file" in s33, \
        "§3.3 does not state that a missing fragment refuses rather than degrading"


def test_only_a_spec_delta_id_is_a_concept_fragment(bundle):
    """A2 — `#card` is a SECTION, not a concept, and must not be read as a lesson.

    `search` emits `{cid}#card` for a CARD goal hit and `{cid}#{id}` for a delta. Only the second
    names a concept; treating every fragment as a lesson id would resolve `#card` to a lesson
    that does not exist.
    """
    view, note = add.show(bundle, "/tasks/t-one.md#card", 1)
    assert view is None, "a `#card` section fragment was read as a lesson"
    assert "next:" in note, f"the refusal names no fix:\n{note}"
    # Floor: the SAME node without the fragment resolves, so the refusal is about the fragment.
    assert add.show(bundle, "/tasks/t-one.md", 1)[0] is not None, \
        "the floor failed: the node itself does not resolve, so this proves nothing"
