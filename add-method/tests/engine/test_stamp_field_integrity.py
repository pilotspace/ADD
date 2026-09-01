"""A stamp the notary reports written is a stamp that reads back.

`_oneline` exists because an unbalanced `{` in a `--reason` once made the parser's
list-continuation swallow the FOLLOWING stamp — two records written, one read back, from an
append-only ledger whose ordering IS the trust model. The fix was correct and was applied to
exactly one field. Seven writers interpolate `by:` raw.

Measured 2026-09-01, on the incumbent engine:

    $ add freeze t --by 'O"Brien' --authority human
    freeze recorded at authority `human`        <- reported as success
    stamp keys read back: ['by']                <- act, authority, direction all swallowed
    _is_frozen -> False · sealed_direction -> None

The seal silently does not exist while the human is told it does. It fails CLOSED — the gate
then refuses with R:UNSEALED — so nothing is let through, and that is the whole severity. But a
notary whose only job is to record faithfully must never report a record it did not write.

The trigger is an ODD number of `"`. A balanced pair round-trips, which is exactly why this
survived every real use of the engine.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DIMS = ("who", "which", "when", "absent", "order", "experience")
ODD = 'O"Brien'


def _authored(root, slug="t"):
    cid, _ = add.new(root, "Task", slug, title=slug)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>", "- S1 x")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 m\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>", '<reject>\n- R:Z x -> "Z"\n</reject>', t, flags=re.S)
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + "".join(
        f"- A{i} [{d}] covers: S1 · n; taking r -> c\n" for i, d in enumerate(DIMS, 1)
    ) + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_x · covers: M1, R:Z · p\nred-first", t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid, p


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _stamps(p):
    return [s for s in (add.read(p, "T0")["fm"].get("verified") or []) if isinstance(s, dict)]


# ------------------------------------------------------------------ M1 · the normaliser

def test_oneline_neutralises_the_double_quote():
    """covers: M1 — a scalar the notary builds must not be terminable by its own content."""
    assert '"' not in add._oneline(ODD)
    assert '"' not in add._oneline('a"b"c"d')


def test_a_value_of_only_quotes_is_not_erased():
    """covers: E3, R:LOSSY — substitute, never delete. An erased actor is its own falsehood."""
    out = add._oneline('"""')
    assert out.strip() != "", "the actor was normalised down to nothing"


def test_a_flow_map_round_trips_every_punctuation(tmp_path):
    """covers: A2 — quotes, braces, colons, commas and newlines, through a real write."""
    root = _bundle(tmp_path)
    for i, evil in enumerate(['a"b', 'a{b}', 'a}', 'a: b', 'a, b', 'a\nb', 'a"}{,b']):
        cid, p = _authored(root, f"punct{i}")
        node, note = add.freeze(root, cid, by=evil, authority="process")
        assert node, f"{evil!r}: {note}"
        st = _stamps(p)
        assert len(st) == 1, f"{evil!r} wrote {len(st)} readable stamps"
        assert st[0].get("act") == "freeze", f"{evil!r} lost `act`: {st[0]}"
        assert st[0].get("authority") == "process", f"{evil!r} lost `authority`: {st[0]}"
        assert st[0].get("direction", "").startswith("sha256:"), f"{evil!r} lost the seal: {st[0]}"


# ------------------------------------------------------------------ M2/M3 · the writers

def test_a_stamp_survives_an_odd_quote_in_by(tmp_path):
    """covers: M2, M3, R:LIE — the headline: `freeze` said yes and the seal did not exist."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "odd")
    node, note = add.freeze(root, cid, by=ODD, authority="human")
    assert node, note

    st = _stamps(p)
    assert sorted(st[0]) == ["act", "at", "authority", "by", "direction"], st[0]
    assert add._is_frozen(add.scan(root)[cid]), "the freeze was reported but the seal is absent"
    assert add.sealed_direction(add.scan(root)[cid]["fm"]), "the direction digest was swallowed"


def test_the_actor_stays_recognisable(tmp_path):
    """covers: A6, R:LOSSY — a name is a person's; refusing or erasing it teaches nothing."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "actor")
    add.freeze(root, cid, by=ODD, authority="process")
    assert _stamps(p)[0]["by"] == "O'Brien"


def test_every_stamp_writer_normalises_its_by():
    """covers: M2, A1, A8 — enumerated from the SOURCE, never from a hand list.

    A hand list is how the seventh writer gets missed, which is the defect this task exists for:
    `_oneline` was correct and applied to one field out of seven.
    """
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    raw = re.findall(r'by: "\{(?!_oneline)[^}]*\}', src)
    assert raw == [], f"{len(raw)} stamp writer(s) still interpolate `by` raw: {raw}"


def test_the_library_is_safe_without_the_cli(tmp_path):
    """covers: A5 — normalising belongs to the writer, so any caller is safe, not only cli.py."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "direct")
    add.freeze(root, cid, by=ODD, authority="process")     # the library, called directly
    assert _stamps(p)[0].get("act") == "freeze"


def test_a_full_walk_survives_an_odd_quote(tmp_path):
    """covers: M2, M3 — brief, run and gate write stamps too; the whole walk must read back."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "walk")
    add.freeze(root, cid, by=ODD, authority="process")
    add.brief_stamp(root, cid, by=ODD)
    xml = tmp_path / "r.xml"
    add.run(root, cid, [sys.executable, "-c",
                        f"open({str(xml)!r},'w').write('<testsuites><testsuite>"
                        f"<testcase classname=\"c\" name=\"test_x\"/></testsuite></testsuites>')"],
            junit=xml)
    ok, note = add.gate(root, cid, "PASS", by=ODD)
    assert ok, note
    acts = [s.get("act") for s in _stamps(p)]
    assert "freeze" in acts and "brief" in acts and "gate" in acts, acts


# ------------------------------------------------------------------ counter-guards

def test_balanced_quotes_still_round_trip(tmp_path):
    """covers: E1 — the case that always worked must keep working."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "balanced")
    add.freeze(root, cid, by='Tin "TinDang97" Dang', authority="process")
    st = _stamps(p)[0]
    assert st.get("act") == "freeze"
    assert "TinDang97" in st["by"]


def test_an_empty_by_keeps_the_writers_default(tmp_path):
    """covers: A4, E2 — normalising must not turn a default into an empty scalar."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "empty")
    add.freeze(root, cid, by="", authority="process")
    qs, _ = add.interview(root, cid)
    add.interview(root, cid, answers={q["id"]: "confirm" for q in qs}, by=None)
    by = [s.get("by") for s in _stamps(p) if s.get("act") == "interview"]
    assert by == ["unrecorded"], by


def test_no_existing_stamp_is_rewritten(tmp_path):
    """covers: A3, E4 — an append-only ledger whose past can be edited is not a ledger."""
    root = _bundle(tmp_path)
    cid, p = _authored(root, "history")
    add.freeze(root, cid, by="first", authority="process")
    before = _stamps(p)
    add.brief_stamp(root, cid, by=ODD)
    after = _stamps(p)
    # the STAMP LIST, not the file text: a later write legitimately grows the frontmatter, so
    # comparing raw text tests the wrong thing (the first cut of this check did exactly that).
    assert after[:len(before)] == before, "an earlier stamp was rewritten by a later write"
    assert len(after) == len(before) + 1, "the write was not a pure append"
