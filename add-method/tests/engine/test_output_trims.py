"""Three verbs stop spending a reader's context on rows that reader cannot act on.

Measured 2026-09-04 on the live 258-node bundle, CLI only:

    add status      13 rows, 9 of them `[—]` Spec/Persona rows that never change   -> 53% noise
    add locate add-method/tooling/add.py
                    52 lines, 50 owners, 48 of them `[done]`                       -> 93% noise
    add brief <any> five `<ref>` blocks whose whole body is the shipped placeholder
                    `- <the first decision that constrains the rest>`              -> filed as D1

Each trim here is a LOSS as well as a saving, so every check below asks the same two
questions: did the byte go away, and can the reader get it back? A collapse that cannot be
expanded is R:NOWAYBACK, and a row describing something a reader must act on is R:HIDDENSTATE
however cheap it would be to drop.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _constant(root, type_, slug):
    """A Spec or Persona the way `init` seeds them: no `status:` at all."""
    p = Path(root) / (type_.lower() + "s") / (slug + ".md")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\ntype: {type_}\ntitle: {slug}\n---\n## CARD\ngoal: g\n", encoding="utf-8")
    return p


def test_every_collapse_names_its_way_back():
    """covers: R:NOWAYBACK, M4, A10 — a summary line that does not name its flag is a loss."""
    root_lines = []
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = _bundle(Path(td))
        for i in range(4):
            _constant(root, "Spec", f"s{i}")
        root_lines.append(add.status(root))
        add.new(root, "Task", "open", title="open", scope="f.py")
        add.new(root, "Task", "shut", title="shut", scope="f.py")
        add.set_status(root, "/tasks/shut.md", "done") if hasattr(add, "set_status") else None
        p = Path(root) / "tasks" / "shut.md"
        p.write_text(p.read_text().replace("status: direction", "status: done"), encoding="utf-8")
        root_lines.append(add.locate(root, "f.py")[1])
    for text in root_lines:
        summary = [l for l in text.splitlines() if "not listed" in l or "more" in l or "hidden" in l]
        assert summary, f"no collapse summary line in:\n{text}"
        for line in summary:
            assert "--all" in line, f"a collapse that does not name its way back: {line!r}"


def test_status_summarises_only_constant_rows(tmp_path):
    """covers: M1, A2, R:HIDDENSTATE — a node carrying a status is never summarised away."""
    root = _bundle(tmp_path)
    for i in range(3):
        _constant(root, "Spec", f"quiet{i}")
    live = Path(root) / "specs" / "loud.md"
    live.write_text("---\ntype: Spec\ntitle: loud\nstatus: build\n---\n## CARD\ngoal: g\n",
                    encoding="utf-8")
    out = add.status(root)
    assert "loud" in out, "a Spec carrying a real status was summarised away -> R:HIDDENSTATE"
    for i in range(3):
        assert f"quiet{i}" not in out, f"quiet{i} is a constant row and is still listed"


def test_status_all_is_unchanged(tmp_path):
    """covers: M2, E5 — `--all` lists every row it lists today."""
    root = _bundle(tmp_path)
    for i in range(3):
        _constant(root, "Persona", f"p{i}")
    out = add.status(root, all=True)
    for i in range(3):
        assert f"p{i}" in out, f"--all dropped p{i}"


def test_locate_shows_open_owners_in_full(tmp_path):
    """covers: M3, A3 — every open owner appears; closed ones are counted, not listed."""
    root = _bundle(tmp_path)
    add.new(root, "Task", "still-open", title="o", scope="shared.py")
    for i in range(3):
        add.new(root, "Task", f"shut{i}", title="s", scope="shared.py")
        p = Path(root) / "tasks" / f"shut{i}.md"
        p.write_text(p.read_text().replace("status: direction", "status: done"), encoding="utf-8")
    hits, note = add.locate(root, "shared.py")
    assert len(hits) == 4, f"fixture did not build four owners: {hits}"
    assert "still-open" in note, "the open owner — the answer to who owns this — is missing"
    for i in range(3):
        assert f"shut{i}" not in note, f"shut{i} is closed and is still listed in full"
    assert "3" in note, "the closed owners were dropped without being counted"


def _ref_node(root, slug, body):
    """A Task whose `needs:` points at a section with `body` as its whole content."""
    src = Path(root) / "specs" / f"{slug}src.md"
    src.write_text(f"---\ntype: Spec\ntitle: {slug}\n---\n## GIVES\n{body}\n",
                   encoding="utf-8")
    cid, _ = add.new(root, "Task", slug, title=slug, scope="f.py")
    p = Path(root) / "tasks" / f"{slug}.md"
    p.write_text(p.read_text().replace(
        "status: direction", f"status: direction\nneeds: [/specs/{slug}src.md#gives]"),
        encoding="utf-8")
    return cid


def _spec_binds(root, slug, body):
    """A Spec carrying `body` as its whole `Decisions that bind` — the D1 path a brief compiles."""
    (Path(root) / "specs" / f"{slug}.md").write_text(
        f"---\ntype: Spec\ntitle: {slug}\n---\n## Decisions that bind\n{body}\n",
        encoding="utf-8")


PLACEHOLDER_BODY = "- <the first decision that constrains the rest>"
REAL_BODY = "- the first decision that constrains the rest!!"


def test_brief_omits_only_placeholder_blocks(tmp_path):
    """covers: M5, R:PLACEHOLDERLOSS, E3, E4, A4 — a real block survives, a placeholder does not."""
    root = _bundle(tmp_path)
    for p in (Path(root) / "specs").glob("*.md"):
        p.unlink()
    _spec_binds(root, "ghost", PLACEHOLDER_BODY)
    _spec_binds(root, "solid", "- the queue is at-least-once, so every handler is idempotent")
    cid, _ = add.new(root, "Task", "t", title="t", scope="f.py")

    text = add.brief(root, cid)["text"]
    assert "specs/ghost#decisions-that-bind" in text, \
        "the omitted section is no longer NAMED -> R:NOWAYBACK"
    assert "the first decision that constrains" not in text, \
        "the placeholder body is still compiled into every brief"
    assert "every handler is idempotent" in text, \
        "a section with real content was dropped -> R:PLACEHOLDERLOSS"


def test_nothing_to_collapse_prints_no_line(tmp_path):
    """covers: E1, E2, A7 — a bundle with nothing to hide grows no line reporting zero."""
    root = _bundle(tmp_path)
    for d in ("specs", "personas"):
        for p in (Path(root) / d).glob("*.md"):
            p.unlink()
    out = add.status(root)
    assert "not listed" not in out, f"a summary line about hiding nothing:\n{out}"
    add.new(root, "Task", "solo", title="s", scope="only.py")
    _, note = add.locate(root, "only.py")
    assert "not listed" not in note, f"a count line about zero closed owners:\n{note}"


def test_order_is_unchanged(tmp_path):
    """covers: A9 — the rows that survive keep the order they had."""
    root = _bundle(tmp_path)
    add.new(root, "Milestone", "mm", title="m")
    add.new(root, "Task", "aa", title="a", milestone="mm")
    add.new(root, "Task", "zz", title="z", milestone="mm")
    rows = [l for l in add.status(root).splitlines() if l.startswith("  · ")]
    names = [l.split()[1] for l in rows]
    assert {"mm", "aa", "zz"} <= set(names), f"fixture rows missing: {names}"
    assert names.index("mm") < names.index("aa") < names.index("zz"), \
        f"a trim re-ranked the surviving rows: {names}"


def test_the_trims_are_measured(tmp_path):
    """covers: M6, A5 — each trim is strictly smaller than the untrimmed rendering."""
    root = _bundle(tmp_path)
    for i in range(6):
        _constant(root, "Spec", f"c{i}")
    assert len(add.status(root)) < len(add.status(root, all=True)), \
        "status: the bare report is not smaller than --all"

    add.new(root, "Task", "live", title="l", scope="m.py")
    for i in range(6):
        add.new(root, "Task", f"gone{i}", title="g", scope="m.py")
        p = Path(root) / "tasks" / f"gone{i}.md"
        p.write_text(p.read_text().replace("status: direction", "status: done"), encoding="utf-8")
    assert len(add.locate(root, "m.py")[1]) < len(add.locate(root, "m.py", all=True)[1]), \
        "locate: the collapsed note is not smaller than the full one"

    _spec_binds(root, "phantom", PLACEHOLDER_BODY)
    assert len(PLACEHOLDER_BODY) == len(REAL_BODY), \
        "the two bodies must be the same length for this to measure"
    c, _ = add.new(root, "Task", "measured", title="m", scope="m.py")
    small = len(add.brief(root, c)["text"])
    _spec_binds(root, "phantom", REAL_BODY)
    assert small < len(add.brief(root, c)["text"]), \
        "brief: omitting the placeholder block saved nothing"


def test_no_actionable_state_went_silent(tmp_path):
    """covers: M7 — the trims removed rows, never a state a reader has to act on.

    M7 is the whole risk of this task stated once: three verbs got quieter, and the way that
    goes wrong is not a byte count, it is an open task, a finding or a refusal that stops
    arriving. So this asks all three, through the trimmed renderings.
    """
    root = _bundle(tmp_path)
    add.new(root, "Milestone", "m", title="m")
    add.new(root, "Task", "needs-you", title="n", milestone="m", scope="live.py")

    out = add.status(root)
    # ROWS only. `needs-you` also appears in the trailing `next:` hint, so a substring test over
    # the whole report passes with the row gone — the same false green Q15 filed.
    rows = [l.split()[1] for l in out.splitlines() if l.startswith("  \u00b7 ")]
    assert "needs-you" in rows, f"an OPEN task fell out of the bare report: {rows}"
    assert out.rstrip().splitlines()[-1].startswith("next: "), "the runnable next: line went silent"

    findings = add.doctor(root)[0]
    assert findings, "fixture: an unauthored node should produce a finding"

    _, note = add.locate(root, "live.py")
    assert "needs-you" in note, "the open owner fell out of locate"
    assert "no node scopes" in add.locate(root, "nowhere.py")[1], \
        "locate's no-hit answer went silent"

    # The CID, not the slug: `freeze` answers a bare slug with "no such node", which is a
    # refusal about the FIXTURE, not about the scaffold this means to provoke (Q18).
    ok, refusal = add.freeze(root, "/tasks/needs-you.md", by="x", authority="human")
    assert not ok and "placeholder" in refusal, f"fixture did not provoke the scaffold refusal: {refusal!r}"
    assert "next:" in refusal, "a refusal stopped naming its fix"
