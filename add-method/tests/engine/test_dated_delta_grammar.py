"""A delta is an addressable concept with a validity interval — id + valid-from, closed on fold.

The frozen grammar carried a competency tag and a status and nothing else, so a lesson had no
address a relation could point at and no way to answer "was this true in August". The head opens
to four fields:

    - [ADD · M12 · open · 2026-08-11] the lesson (evidence: /tasks/x.md)
    - [ADD · M12 · folded · 2026-08-11→2026-09-03] the lesson (evidence: /tasks/x.md)

and the LEGACY two-field head stays readable forever, because ADD ships on npm and PyPI and every
existing bundle is full of them. Deprecation has no landing: a legacy head carries no date, and a
user's install has nowhere to recover one — leaving only "make their lessons malformed" or "invent
a date", and R:INVENTEDDATE forbids the second. `learn` only ever WRITES the four-field head.

Dispatch is on the COUNT of `·`-separated fields inside the brackets, never on their shape: shape
dispatch would make a four-field head with a broken id fall out as `unparsed`, and `bad_id` would
become a code no producer can emit — a check with nothing to prove.

covers the node `.add/tasks/dated-addressable-deltas.md`.
"""
import inspect
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DATED_HEAD = re.compile(
    r"^- \[(?P<comp>[A-Z]+) · (?P<id>[A-Za-z][A-Za-z0-9_-]*) · (?P<status>\w+) · (?P<iv>[\d\-→]+)\] ")


def _spec(root, lens):
    return (root / "specs" / f"{lens}.md").read_text(encoding="utf-8")


def _delta_lines(root, lens):
    return [ln for ln in _spec(root, lens).splitlines() if ln.lstrip().startswith("- [")]


def _append(root, lens, *lines):
    p = root / "specs" / f"{lens}.md"
    p.write_text(p.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(lines) + "\n",
                 encoding="utf-8")


# ---------------------------------------------------------------- M1 · learn writes the dated head

def test_learn_writes_an_id_and_a_valid_from_date(tmp_path):
    """covers: M1 — the written head carries four fields, and the date is the engine's own clock."""
    add.init(tmp_path, "code", "T")
    ok, _ = add.learn(tmp_path, "method", "budgets need a unit", evidence="/runs/1.md")
    assert ok is True
    lines = [ln for ln in _delta_lines(tmp_path, "method") if "budgets need a unit" in ln]
    assert len(lines) == 1, f"learn wrote {len(lines)} matching lines: {lines}"
    m = DATED_HEAD.match(lines[0])
    assert m, f"learn did not write the dated four-field head:\n{lines[0]}"
    assert m.group("status") == "open"
    assert m.group("iv") == add._today(), (
        f"valid-from must be the engine's own clock, got {m.group('iv')!r}")
    assert "(evidence: /runs/1.md)" in lines[0]
    # and structurally: there is no parameter through which a caller could supply that date.
    params = set(inspect.signature(add.learn).parameters)
    assert {"lens", "lesson", "evidence"} <= params, (
        f"the guard is aimed at the wrong callable: {sorted(params)}")
    leaked = {q for q in params if "date" in q or q in ("at", "when", "valid_from", "today")}
    assert not leaked, f"learn exposes a caller-supplied clock: {sorted(leaked)}"


# ---------------------------------------------------------------- M2 · the id and its high-water

def test_a_minted_id_is_the_lens_letter_and_the_next_integer(tmp_path):
    """covers: M2 — two learns mint 1 then 2 on TWO lenses, so a hardcoded letter cannot pass."""
    add.init(tmp_path, "code", "T")
    for lens, letter in (("method", "M"), ("quality", "Q")):
        add.learn(tmp_path, lens, f"first {lens} lesson", evidence="e1")
        add.learn(tmp_path, lens, f"second {lens} lesson", evidence="e2")
        ids = [m.group("id") for ln in _delta_lines(tmp_path, lens)
               for m in [DATED_HEAD.match(ln)] if m]
        assert set(ids) == {f"{letter}1", f"{letter}2"}, f"{lens} minted {sorted(ids)}"
        fm = add.read(tmp_path / "specs" / f"{lens}.md", "T2")["raw"]
        assert re.search(r"^delta_seq:\s*2\s*$", fm, re.M), (
            f"the high-water mark must be written back to {lens}'s frontmatter:\n{fm}")


def test_learn_touches_only_the_delta_seq_key(tmp_path):
    """covers: M2 — writing back a counter must not re-emit the frontmatter and lose a byte."""
    add.init(tmp_path, "code", "T")
    before = add.read(tmp_path / "specs" / "method.md", "T2")["raw"]
    assert "type: Spec" in before, "the fixture frontmatter is not what this guard assumes"
    add.learn(tmp_path, "method", "a lesson", evidence="e")
    after = add.read(tmp_path / "specs" / "method.md", "T2")["raw"]
    moved = [ln for ln in after.splitlines() if ln not in before.splitlines()]
    assert moved == ["delta_seq: 1"], f"learn changed frontmatter beyond delta_seq: {moved}"
    dropped = [ln for ln in before.splitlines() if ln not in after.splitlines()]
    assert not dropped, f"learn dropped frontmatter lines: {dropped}"


def test_a_deleted_top_delta_does_not_free_its_id(tmp_path):
    """covers: R:REUSEDID — an address must never be reused, so the counter cannot walk backwards."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "method", "first lesson", evidence="e1")
    add.learn(tmp_path, "method", "second lesson", evidence="e2")
    p = tmp_path / "specs" / "method.md"
    kept = [ln for ln in p.read_text(encoding="utf-8").splitlines() if "second lesson" not in ln]
    assert any("first lesson" in ln for ln in kept), "the fixture deleted the wrong line"
    assert any("delta_seq" in ln for ln in kept), "the fixture must leave delta_seq in place"
    p.write_text("\n".join(kept) + "\n", encoding="utf-8")
    assert "M2" not in p.read_text(encoding="utf-8"), "M2 must be gone before the re-mint"

    add.learn(tmp_path, "method", "third lesson", evidence="e3")
    m = DATED_HEAD.match([ln for ln in _delta_lines(tmp_path, "method") if "third lesson" in ln][0])
    assert m and m.group("id") == "M3", (
        f"the deleted M2 was handed out again — an id must never be reused: {m and m.group('id')}")


def test_join_cannot_mint_a_duplicate_id(tmp_path):
    """covers: R:REUSEDID — join is the SECOND delta writer.

    `_union_into_deltas` appends a stream's delta lines verbatim while writing back MAIN's
    frontmatter, so the stream's counter is discarded. Two streams off one base each mint the
    same id for a different lesson; the merge must not leave two deltas sharing an address.
    """
    main = tmp_path / "main"
    add.init(main, "code", "T")
    add.new(main, "Milestone", "m", title="m")
    add.new(main, "Task", "sa", title="sa", milestone="m", scope=["a.py"])
    add.new(main, "Task", "sb", title="sb", milestone="m", scope=["b.py"])

    def _pass_stream(name, slug):
        d = tmp_path / name
        shutil.copytree(main, d)
        runs = d / "tasks" / f"{slug}.d" / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (runs / "1.md").write_text("# receipt\n", encoding="utf-8")
        add._transition(d, f"/tasks/{slug}.md", sets={"status": "done"}, appends=[("verified",
            f'{{ by: "x", at: {add._today()}, act: gate, authority: process, '
            f'outcome: PASS, receipt: /tasks/{slug}.d/runs/1.md }}')])
        return d

    sA, sB = _pass_stream("sA", "sa"), _pass_stream("sB", "sb")
    add.learn(sA, "quality", "stream A's own lesson", evidence="a")
    add.learn(sB, "quality", "stream B's own lesson", evidence="b")
    ida = DATED_HEAD.match(_delta_lines(sA, "quality")[0]).group("id")
    idb = DATED_HEAD.match(_delta_lines(sB, "quality")[0]).group("id")
    assert ida == idb, f"the fixture must produce colliding ids off one base, got {ida} and {idb}"

    add.join(main, [sA, sB])
    merged = [DATED_HEAD.match(ln) for ln in _delta_lines(main, "quality")]
    ids = [m.group("id") for m in merged if m]
    assert len(ids) == 2, f"join must carry both lessons: {_delta_lines(main, 'quality')}"
    assert len(set(ids)) == 2, f"join left two deltas sharing one address: {ids}"


def test_a_hand_written_higher_id_is_never_clobbered(tmp_path):
    """covers: M2 — the body floors the counter, so a hand-numbered delta cannot be shadowed."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "method", "engine minted", evidence="e1")
    _append(tmp_path, "method", "- [ADD · M40 · open · 2026-08-11] a hand numbered one (evidence: e)")
    add.learn(tmp_path, "method", "after the hand edit", evidence="e2")
    m = DATED_HEAD.match([ln for ln in _delta_lines(tmp_path, "method")
                          if "after the hand edit" in ln][0])
    assert m and int(m.group("id")[1:]) > 40, (
        f"the mint must clear the hand-written high-water M40, got {m and m.group('id')}")


def test_an_empty_spec_mints_its_first_id_as_one(tmp_path):
    """covers: E2 — a spec holding no deltas is the cold-start case; it must not crash or skip 1."""
    add.init(tmp_path, "code", "T")
    assert not [ln for ln in _delta_lines(tmp_path, "domain")], "the fixture spec already has deltas"
    ok, _ = add.learn(tmp_path, "domain", "the very first lesson", evidence="e")
    assert ok is True
    m = DATED_HEAD.match(_delta_lines(tmp_path, "domain")[0])
    assert m and m.group("id") == "D1", f"cold start minted {m and m.group('id')}, expected D1"


def test_the_minted_id_is_fragment_safe(tmp_path):
    """covers: M9 — the id becomes a `#fragment`, so it may hold no space, dot or punctuation."""
    add.init(tmp_path, "code", "T")
    for i in range(3):
        add.learn(tmp_path, "method", f"lesson number {i}", evidence="e")
    ids = [m.group("id") for ln in _delta_lines(tmp_path, "method")
           for m in [DATED_HEAD.match(ln)] if m]
    assert len(ids) == 3, f"the fixture must mint three ids, got {ids}"
    for did in ids:
        assert re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", did), f"{did!r} is not fragment-safe"
    assert len(set(ids)) == 3, f"two deltas in one file share an id: {ids}"


# ---------------------------------------------------------------- M3 · the item carries the interval

def test_delta_items_expose_the_interval_and_still_unpack_as_three(tmp_path):
    """covers: M3 — the interval rides as attributes so every existing 3-tuple unpack survives."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "method", "an interval bearing lesson", evidence="e")
    items, _ = add.deltas(tmp_path)
    assert len(items) == 1, items
    spec, comp, text = items[0]                      # the shape cli.py and 3 suites already read
    assert (spec, comp) == ("method", "ADD") and "an interval bearing lesson" in text
    item = items[0]
    assert item.id == "M1", f"the item must carry its address: {item.id!r}"
    assert item.valid_from == add._today(), f"valid_from missing: {item.valid_from!r}"
    assert item.valid_to is None, f"an open delta has no close: {item.valid_to!r}"


def test_delta_equality_stays_the_three_tuple(tmp_path):
    """covers: M3 — the id is metadata, not identity: no existing comparison changes meaning."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "method", "a lesson", evidence="e")
    items, _ = add.deltas(tmp_path)
    item = items[0]
    plain = (item[0], item[1], item[2])
    assert item == plain, "a Delta must still compare equal to the plain three-tuple"
    assert len({item, plain}) == 1, "hash diverged from the three-tuple"
    assert item.id and item.id in repr(item), (
        f"the repr hides the id and every debug print lies by omission: {item!r}")


# ---------------------------------------------------------------- M4/M5 · closing the interval

def test_fold_closes_the_validity_interval(tmp_path):
    """covers: M4 — folding stamps the close, so the window a lesson was carried is on the record."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M7 · open · 2026-08-11] a lesson that will be folded (evidence: e)")
    ok, _ = add.fold(tmp_path, "method", "will be folded")
    assert ok is True
    line = [ln for ln in _delta_lines(tmp_path, "method") if "will be folded" in ln][0]
    assert f"[ADD · M7 · folded · 2026-08-11→{add._today()}]" in line, (
        f"fold did not close the interval:\n{line}")
    items, _ = add.deltas(tmp_path, "folded")
    assert len(items) == 1 and items[0].valid_from == "2026-08-11", items
    assert items[0].valid_to == add._today(), items[0].valid_to


def test_a_rejected_delta_parses_with_both_endpoints(tmp_path):
    """covers: M5 — no engine writer emits `rejected`; the PARSER must still read its interval."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M8 · rejected · 2026-08-11→2026-08-20] a rejected one (evidence: e)")
    items, note = add.deltas(tmp_path, "rejected")
    assert len(items) == 1, f"a rejected delta with an interval must parse:\n{note}"
    assert (items[0].valid_from, items[0].valid_to) == ("2026-08-11", "2026-08-20"), items[0]
    assert "malformed" not in note.lower(), note


def test_a_terminal_head_with_one_date_is_tolerated(tmp_path):
    """An unknown close is unknown, not malformed — the shape this node's own migration emits
    when a fold's filing commit is recoverable but its closing one is not (A6/A11)."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method", "- [ADD · M9 · folded · 2026-08-11] an unclosed fold (evidence: e)")
    items, note = add.deltas(tmp_path, "folded")
    assert [t for _, _, t in items if "unclosed fold" in t], (
        f"a terminal delta whose close is unknown must still be carried:\n{note}")
    assert items[0].valid_from == "2026-08-11" and items[0].valid_to is None, items[0]
    assert "malformed" not in note.lower(), note


def test_a_legacy_two_part_head_is_still_a_lesson(tmp_path):
    """covers: M6 — an undated line from an older bundle lists normally AND reports nothing."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method", "- [ADD · open] a lesson from an older bundle (evidence: /runs/1.md)")
    items, note = add.deltas(tmp_path)
    carried = [i for i in items if "older bundle" in i[2]]
    assert carried, f"a legacy delta must still be carried:\n{note}"      # half one: present
    assert (carried[0].id, carried[0].valid_from, carried[0].valid_to) == (None, None, None), \
        carried[0]
    assert "malformed" not in note.lower(), (                             # half two: unreported
        f"a legacy line is not malformed:\n{note}")


def test_fold_on_a_legacy_head_invents_no_date(tmp_path):
    """covers: E1 — one fold over a mixed file: the dated line gets a close, the legacy one does not."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M3 · open · 2026-08-11] a dated lesson to close (evidence: e)",
            "- [ADD · open] an undated legacy lesson to close (evidence: e)")
    ok, _ = add.fold(tmp_path, "method", "lesson to close")
    assert ok is True
    dated = [ln for ln in _delta_lines(tmp_path, "method") if "a dated lesson" in ln][0]
    legacy = [ln for ln in _delta_lines(tmp_path, "method") if "legacy lesson" in ln][0]
    assert f"[ADD · M3 · folded · 2026-08-11→{add._today()}]" in dated, (
        f"the dated line must have its interval closed:\n{dated}")
    assert "[ADD · folded]" in legacy, f"the legacy head must stay two-field:\n{legacy}"
    assert add._today() not in legacy and "→" not in legacy, (
        f"fold invented a date on a line whose start it does not know:\n{legacy}")


def test_folding_never_renumbers_a_survivor(tmp_path):
    """covers: R:RENUMBER — ids retire in place; a renumber re-points every relation silently."""
    add.init(tmp_path, "code", "T")
    for i in range(3):
        add.learn(tmp_path, "method", f"lesson number {i}", evidence="e")

    def ids_by_text():
        out = {}
        for ln in _delta_lines(tmp_path, "method"):
            m = DATED_HEAD.match(ln)
            if m:
                out[ln[m.end():].split(" (evidence:")[0]] = m.group("id")
        return out

    before = ids_by_text()
    assert len(before) == 3, before
    ok, _ = add.fold(tmp_path, "method", "lesson number 1")
    assert ok is True
    after = ids_by_text()
    assert len(after) == 3, f"folding removed a line: {after}"
    assert after == before, f"a fold renumbered a survivor: {before} -> {after}"


# ---------------------------------------------------------------- the reject codes

def test_a_bad_id_field_is_reported_not_read(tmp_path):
    """covers: R:BADID — an unaddressable address is worse than none; it must be named."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · open] a control line that must survive (evidence: e)",
            "- [ADD · 12M · open · 2026-08-11] a broken address (evidence: e)")
    items, note = add.deltas(tmp_path)
    assert [t for _, _, t in items if "control line" in t], f"the control line vanished:\n{note}"
    assert "bad_id" in note and "broken address" in note, (
        f"a malformed id must be reported as bad_id:\n{note}")
    assert not [i for i in items if "broken address" in i[2]], (
        "a line with a broken address must not be read as a lesson id")


def test_a_dotted_id_is_not_fragment_safe(tmp_path):
    """covers: R:BADID — an id carrying punctuation would not survive as a `#fragment`."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M1 · open · 2026-08-11] a control line that must survive (evidence: e)",
            "- [ADD · M.12 · open · 2026-08-11] a dotted address (evidence: e)")
    items, note = add.deltas(tmp_path)
    assert [t for _, _, t in items if "control line" in t], f"the control line vanished:\n{note}"
    assert "bad_id" in note and "dotted address" in note, note


def test_a_bad_date_is_reported_by_its_own_code(tmp_path):
    """covers: R:BADDATE — the code IS the whole message the author gets; this fix is the format."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M1 · open · 2026-08-11] a control line that must survive (evidence: e)",
            "- [ADD · M2 · open · not-a-date] an unparsable endpoint (evidence: e)")
    items, note = add.deltas(tmp_path)
    assert [t for _, _, t in items if "control line" in t], f"the control line vanished:\n{note}"
    assert "bad_date" in note and "unparsable endpoint" in note, (
        f"an unparsable date needs its own actionable code:\n{note}")
    assert not [i for i in items if "unparsable endpoint" in i[2]], note


def test_a_reversed_or_early_closed_interval_is_reported(tmp_path):
    """covers: R:BADINTERVAL — two different faults, two different fixes, two different codes."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M1 · open · 2026-08-11] a control line that must survive (evidence: e)",
            "- [ADD · M3 · open · 2026-08-11→2026-09-03] an open head with a close (evidence: e)",
            "- [ADD · M4 · folded · 2026-09-03→2026-08-11] a reversed interval (evidence: e)")
    items, note = add.deltas(tmp_path)
    assert [t for _, _, t in items if "control line" in t], f"the control line vanished:\n{note}"
    assert "open_carries_close" in note and "open head with a close" in note, note
    assert "bad_interval" in note and "reversed interval" in note, note
    for phrase in ("open head with a close", "reversed interval"):
        assert not [i for i in items if phrase in i[2]], f"{phrase!r} was read as a lesson"


def test_every_malformed_shape_is_reported_by_name(tmp_path):
    """covers: R:SILENTDROP — the rule quantifies over EVERY unplaceable line, so the check does
    too: one row per failure the parser can reach, each proving its own text reached the report."""
    add.init(tmp_path, "code", "T")
    table = [
        ("one field",      "- [ADD] a one field head (evidence: e)"),
        ("three fields",   "- [ADD · M1 · open] a three field head (evidence: e)"),
        ("five fields",    "- [ADD · M2 · open · 2026-08-11 · x] a five field head (evidence: e)"),
        ("unknown status", "- [ADD · M3 · opne · 2026-08-11] a typoed status (evidence: e)"),
        ("unknown comp",   "- [XYZ · M4 · open · 2026-08-11] a bogus competency (evidence: e)"),
        ("no evidence",    "- [ADD · M5 · open · 2026-08-11] a claim with no proof"),
        ("bad id",         "- [ADD · 9 · open · 2026-08-11] a numeric address (evidence: e)"),
        ("bad date",       "- [ADD · M6 · open · yesterday] a worded date (evidence: e)"),
        ("bad interval",   "- [ADD · M7 · folded · 2026-09-03→2026-08-11] a backwards window (evidence: e)"),
        ("open close",     "- [ADD · M8 · open · 2026-08-11→2026-09-03] an open with a close (evidence: e)"),
    ]
    _append(tmp_path, "method",
            "- [ADD · M99 · open · 2026-08-11] a control line that must survive (evidence: e)",
            *[line for _, line in table])
    items, note = add.deltas(tmp_path)
    assert [t for _, _, t in items if "control line" in t], f"the control line vanished:\n{note}"
    assert len(items) == 1, f"only the control line is well formed, got {items}"
    for label, line in table:
        marker = line.split("] ", 1)[1].split(" (evidence:")[0]
        assert marker in note, f"{label}: this line vanished from the inventory entirely:\n{note}"


def test_a_second_trailing_clause_leaves_the_delta_readable(tmp_path):
    """covers: M10 — a later typed-relation clause must not empty the inventory the loop reads."""
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "method",
            "- [ADD · M5 · open · 2026-08-11] a lesson with a relation "
            "(evidence: /tasks/x.md) (refines: /specs/method.md#M2)")
    items, note = add.deltas(tmp_path)
    carried = [i for i in items if "with a relation" in i[2]]
    assert carried, f"a trailing relation clause dropped the delta from the inventory:\n{note}"
    assert "malformed" not in note.lower(), f"a trailing clause must not read as malformed:\n{note}"
    assert carried[0].id == "M5" and carried[0].valid_from == "2026-08-11", carried[0]
    assert "(refines: /specs/method.md#M2)" in carried[0][2], (
        "the tail must survive intact for the relation parser downstream")


def test_the_persona_hint_rides_the_tail_not_the_head(tmp_path):
    """covers: M11 — personas.md's live persona-delta claim keeps working with ONE head shape.

    The documented form put the hint INSIDE the brackets, which is four fields and would now
    parse as a dated head and report bad_id on `open`. Moving it to the open tail keeps the
    claim and keeps the head unambiguous.
    """
    add.init(tmp_path, "code", "T")
    _append(tmp_path, "experience",
            "- [UDD · X4 · open · 2026-08-11] 4.5:1 contrast · persona:ui-designer · "
            "success-metric (evidence: audit)")
    items, note = add.deltas(tmp_path)
    carried = [i for i in items if "4.5:1 contrast" in i[2]]
    assert carried, f"the documented persona-delta form must parse:\n{note}"
    assert "malformed" not in note.lower(), note
    assert carried[0].id == "X4", carried[0]
    assert "persona:ui-designer" in carried[0][2] and "success-metric" in carried[0][2], (
        "the persona hint must survive in the tail for the persona loop to read")


def test_the_interval_arrow_survives_the_round_trip(tmp_path):
    """covers: E3, A4 — the arrow is byte-identical after write/read/write, and the close is inclusive."""
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "method", "an arrow round trip", evidence="e")
    add.fold(tmp_path, "method", "arrow round trip")
    raw = (tmp_path / "specs" / "method.md").read_bytes()
    assert "→".encode("utf-8") in raw, "the U+2192 separator did not survive as UTF-8"
    add.learn(tmp_path, "method", "a second lesson after the fold", evidence="e")
    assert "→".encode("utf-8") in (tmp_path / "specs" / "method.md").read_bytes(), \
        "a later write mangled the arrow"
    items, note = add.deltas(tmp_path, "folded")
    assert len(items) == 1 and items[0].valid_to == add._today(), (items, note)
    # A4's probe, asked of the path that SHIPS. These three assertions used to run against
    # `delta_carried_on`, a predicate no engine or CLI path ever called, whose docstring claimed
    # `--as-of` was wired to it and whose interval was CLOSED-CLOSED. `--as-of` is half-open, so
    # on the close date the two disagreed — and the dead one was the one under test. It is gone
    # (source-dead-code); the questions it asked are asked here of `deltas --as-of`.
    # This fixture files and folds on the SAME day, so it cannot tell the two endpoints apart —
    # the open endpoint's inclusivity is asked in test_source_dead_code.py, where the dates
    # differ. What it can still ask is the right endpoint and the far side.
    assert items[0].id in [i.id for i in add.deltas(tmp_path, "folded", as_of=add._today())[0]], \
        "on its close date the lesson reads FOLDED — the interval is half-open on the right"
    assert add.deltas(tmp_path, "open", as_of="2000-01-01")[0] == [], \
        "a date before valid_from is outside the interval"
