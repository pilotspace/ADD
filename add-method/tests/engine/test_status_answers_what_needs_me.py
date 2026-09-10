"""Red suite for `status-answers-what-needs-me` — orientation answers one question.

On a nearly-finished bundle `add status` printed three rows — `PROJECT`, `index`, and an
ARCHIVED milestone — while withholding 112 nodes, and ended in `next: add new task <slug>`,
which is not a command anyone can run. Running `--all` printed `… 112 more of 132 (`--all` for
done nodes)`: a hint advising the flag already in force, with no other way to those rows.

It was tuned for a bundle mid-flight and degraded at both ends. The question a reader actually
brings — human or agent, resuming cold — is `what needs me?`.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

WIDTH = 100
SLOT = re.compile(r"<[^>]+>")


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Board")
    return tmp_path


def _set(root, cid, **fields):
    path = Path(root) / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = n["raw"]
    for k, v in fields.items():
        raw = add.set_key(raw, k, v)
    add.write(path, f"---\n{raw}\n---\n{n['body']}")
    return cid


def _rows(out):
    return [l for l in out.splitlines() if l.lstrip().startswith("· ")]


def _slugs(out):
    return [l.split("·", 1)[1].split()[0] for l in _rows(out)]


def test_the_board_shows_only_what_needs_a_decision(bundle):
    """covers: M1, R:DEADROW, A2, A4, E2, E3, E4 — a row is work, or it is not a row."""
    # E4: a fresh bundle has vocabulary and no work. The answer is a sentence, not an empty list.
    fresh = add.status(bundle)
    assert not _rows(fresh), f"a fresh bundle printed work rows:\n{fresh}"
    assert "nothing needs you" in fresh.lower(), \
        f"A4/E4 — an empty board is indistinguishable from a broken read:\n{fresh}"

    add.new(bundle, "Task", "t-open", title="Open work")
    _set(bundle, add.new(bundle, "Task", "t-done", title="Finished")[0], status="done")
    _set(bundle, add.new(bundle, "Milestone", "m-old", title="Retired")[0], status="archived")
    _set(bundle, add.new(bundle, "Task", "t-odd", title="Odd")[0], status="mid-review")

    out = add.status(bundle)
    shown = _slugs(out)
    assert "t-open" in shown, f"open work is missing from the board:\n{out}"
    assert "t-odd" in shown, f"E3 — an unrecognised status vanished instead of printing:\n{out}"
    for gone in ("t-done", "m-old"):
        assert gone not in shown, f"an answered node printed as a row ({gone}):\n{out}"
    for dead in ("PROJECT", "index"):
        assert dead not in shown, \
            f"R:DEADROW — `{dead}` carries no state and still printed a row:\n{out}"


def test_rows_are_ordered_by_attention(bundle):
    """covers: M2, A5, A10, E1 — closest to needing a human, first."""
    add.new(bundle, "Milestone", "m-live", title="Live")
    # A node at the DIRECTION beat is one that was authored and not yet frozen — setting
    # `status: direction` on a scaffold does not make it one; it is still adrift, correctly.
    for slug, st in (("z-verify", "verify"), ("y-build", "build")):
        _set(bundle, add.new(bundle, "Task", slug, title=slug)[0], status=st)
    _author(bundle, add.new(bundle, "Task", "x-direction", title="x-direction")[0])
    add.new(bundle, "Task", "w-queued", title="queued", milestone="m-live")
    add.new(bundle, "Task", "v-adrift", title="adrift")

    shown = [s for s in _slugs(add.status(bundle)) if s != "m-live"]
    want = ["z-verify", "y-build", "x-direction", "w-queued", "v-adrift"]
    assert shown == want, (
        "rows are not ordered by how close the work is to needing a human — an archived "
        f"milestone used to outrank every open task because the sort was by node TYPE:\n"
        f"  got  {shown}\n  want {want}")

    # A10/E1: `--all` is a superset in the SAME order, never a re-sort.
    everything = [s for s in _slugs(add.status(bundle, all=True)) if s in want]
    assert everything == want, f"`--all` re-ordered the board:\n  {everything}"

    # A5: ties inside one beat break by slug, so two reads never disagree.
    for slug in ("b-tie", "a-tie"):
        _set(bundle, add.new(bundle, "Task", slug, title=slug)[0], status="build")
    ties = [s for s in _slugs(add.status(bundle)) if s.endswith("-tie")]
    assert ties == sorted(ties), f"A5 — ties do not break by slug: {ties}"


def test_every_hint_names_something_that_runs(bundle):
    """covers: M3, M4, R:DEADHINT, R:PLACEHOLDER_NEXT, R:NOWAYIN, A3, A7, A8 — driven, not read."""
    add.new(bundle, "Milestone", "m", title="M")
    for i in range(add.MAX_LINES + 12):
        _set(bundle, add.new(bundle, "Task", f"t{i:03d}", title=f"task {i}")[0], status="build")

    bare = add.status(bundle)
    nxt = next(l for l in bare.splitlines() if l.startswith("next:"))
    # A notary cannot invent a project's test command before it has ever seen one, so the build
    # hint is a template exactly until the first run — and never after. Drive one and re-read.
    assert "<test cmd>" in nxt, "fixture: the slot is already gone, so this proves nothing"
    add.run(bundle, "/tasks/t000.md", ["python3", "-c", "print('ok')"])
    nxt = next(l for l in add.status(bundle).splitlines() if l.startswith("next:"))
    assert not SLOT.search(nxt), (
        f"R:PLACEHOLDER_NEXT — the next line still hands back a slot after a real run "
        f"recorded the command: {nxt!r}")

    everything = add.status(bundle, all=True)
    for line in everything.splitlines():
        assert "`--all`" not in line and "--all for" not in line, (
            f"R:DEADHINT — `--all` advised the flag already in force:\n  {line}")

    # R:NOWAYIN: the bare report withheld rows. Whatever command it names must actually
    # produce them — driven, never taken on the hint's word.
    withheld = set(_slugs(everything)) - set(_slugs(bare))
    assert withheld, "fixture: the cap did not withhold anything, so this proves nothing"
    hint = "\n".join(l for l in bare.splitlines() if l.lstrip().startswith("…"))
    assert hint, f"rows were withheld with no hint at all:\n{bare}"
    assert "add status --all" in hint, (
        f"R:NOWAYIN — the bare report withheld {len(withheld)} row(s) and names no command "
        f"that reaches them:\n  {hint}")
    assert withheld <= set(_slugs(everything)), "the named command does not produce the withheld rows"

    # A11: a reader who asked for everything is told how much everything is.
    assert str(len(_slugs(everything))) in everything.splitlines()[0], \
        f"`--all` does not say how many rows are coming:\n{everything.splitlines()[0]}"


def test_the_report_says_where_you_left_off(bundle):
    """covers: M6, E6 — a resume point that omits the last session is not a resume point."""
    # E6: no stamps anywhere — absent, never a guessed date.
    assert "last:" not in add.status(bundle).lower(), \
        "a bundle with no recorded act still claimed a last one"

    cid, _ = add.new(bundle, "Task", "t-acted", title="Acted on")
    add.drop(bundle, cid, "so there is exactly one recorded act")
    out = add.status(bundle)
    line = next((l for l in out.splitlines() if l.lstrip().lower().startswith("last")), "")
    assert line, f"M6 — the report does not say where the reader left off:\n{out}"
    assert "t-acted" in line and "drop" in line, \
        f"the last act names neither the node nor the act: {line!r}"


def test_no_row_wraps_or_misaligns(bundle):
    """covers: M7, A1, A6, A9, E5 — one row, one line, at 100 columns."""
    long_title = ("A deliberately overlong title that keeps going well past any sensible column "
                  "budget and would wrap a terminal twice over")
    add.new(bundle, "Task", "s" * 40, title=long_title)
    _set(bundle, add.new(bundle, "Task", "t-second", title=long_title)[0], status="verify")

    for out, label in ((add.status(bundle), "bare"), (add.status(bundle, all=True), "--all")):
        for line in out.splitlines():
            assert len(line) <= WIDTH, (
                f"M7 — a {label} line is {len(line)} columns and will wrap:\n  {line!r}")
        for row in _rows(out):
            if row.endswith("…"):
                assert not row[:-1].endswith(" "), f"A6 — truncated mid-space: {row!r}"
                assert " " in row[:-1].rstrip(), f"A6 — truncation ate the whole value: {row!r}"

    # A9: `--all` on an empty board answers the same way the bare report does.
    empty = add.init(bundle / "sub", "code", "Empty") and add.status(bundle / "sub", all=True)
    assert "nothing needs you" in empty.lower(), f"A9 — `--all` on an empty board:\n{empty}"


AUTHORED_BODY = """## CARD
goal: a real authored goal
beat: direction

## RULES
<must>
- M1 the thing holds
</must>
<reject>
- R:BAD the bad thing never happens -> "BAD"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · one caller, this repo
- A2 [which] n/a · one case
- A3 [when] n/a · no boundary
- A4 [absent] n/a · no optional value
- A5 [order] n/a · one item
- A6 [experience] n/a · no human reads it

## PLAN
contract: S1 a surface

## CHECKS
- test_one · covers: M1 · proves it
red-first: every check MUST fail first.
"""


def _author(root, cid):
    """A node authored far enough to reach the DIRECTION beat — not merely stamped as one."""
    path = Path(root) / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = add.set_key(n["raw"], "gives", ["S1 a surface other code calls"])
    add.write(path, f"---\n{raw}\n---\n{AUTHORED_BODY}")
    return cid
