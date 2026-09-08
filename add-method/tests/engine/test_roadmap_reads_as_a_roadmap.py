"""Red suite for `a-roadmap-reads-as-a-roadmap` — a queued plan says what it queues.

A real 40-task roadmap shipped for review with 38 nodes still scaffold. Every engine surface
reported it — `doctor` warned 38 times, every `status` row read `[scaffold]`, `todo` said
`38 open task(s)` — and the reviewer still concluded the tool had failed, because the ONE field
those 40 nodes had authored was their `title:`, and no orientation verb rendered it. Reading the
roadmap meant opening forty files.

And the planner that wrote those titles had nowhere to put the one-line goal it also held:
`add new` has no `--goal`, while the library accepts `goal=` and writes it into FRONTMATTER,
leaving one authored goal and one scaffold goal in the same node.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

LONG = "Live sources stream results instead of accumulating them in an unbounded list forever"


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Roadmap")
    return tmp_path


def _row(note, slug):
    return next((l for l in note.splitlines() if f" {slug} " in l or l.strip().startswith(f"· {slug}")), "")


def test_status_rows_carry_their_title(bundle):
    """covers: M1, A1, A3, A12, E1 — the one authored field, on every listed node."""
    add.new(bundle, "Milestone", "m-one", title="Trust the ship")
    add.new(bundle, "Task", "t-one", title="Bounded CLI memory")
    out = add.status(bundle)
    assert "Trust the ship" in _row(out, "m-one"), f"a Milestone row carried no title:\n{out}"
    assert "Bounded CLI memory" in _row(out, "t-one"), f"a Task row carried no title:\n{out}"
    # A12: the existing columns keep their positions — a guard reading the prefix still reads it.
    assert "[scaffold] Task" in _row(out, "t-one"), _row(out, "t-one")


def test_a_slot_title_is_not_a_title(bundle):
    """covers: M6, A8, E1 — render nothing, never a placeholder."""
    add.new(bundle, "Task", "t-real", title="A real title")
    add.new(bundle, "Task", "t-slot", title="<the surface this publishes>")
    out = add.status(bundle)
    # Arm it: "no placeholder was rendered" is free while NOTHING is rendered.
    assert "A real title" in _row(out, "t-real"), "no title renders at all, so this proves nothing"
    row = _row(out, "t-slot")
    assert "<" not in row, f"a template slot was rendered as a title: {row}"


def test_status_headline_names_the_scaffold_count(bundle):
    """covers: M3, A4, A9, E3 — the headline and `doctor` can never disagree."""
    head = add.status(bundle).splitlines()[0]
    assert "scaffold" not in head, f"A9 — a zero count was shown: {head}"   # E3

    for n in range(3):
        add.new(bundle, "Task", f"t-{n}", title=f"Queued task {n}")
    head = add.status(bundle).splitlines()[0]
    assert "3 scaffold" in head, f"the headline named no scaffold count: {head}"
    doctored = len([f for f in add.doctor(bundle) if f["code"] == "unauthored_node"])
    assert doctored == 3, f"the fixture is not what this guard assumes: {doctored}"


def test_orientation_stays_t0_and_bounded(bundle, monkeypatch):
    """covers: R:T2SCAN, R:ROWBLOAT, A6, A14, E2 — free, and still one line per node."""
    for n in range(3):
        add.new(bundle, "Task", f"t-{n}", title=LONG + f" number {n}")
    real, leaks = add.read, []

    def spy(path, tier="T0"):
        if tier != "T0":
            leaks.append((str(path), tier))
        return real(path, tier)

    monkeypatch.setattr(add, "read", spy)
    out = add.status(bundle)
    monkeypatch.undo()
    assert "Live sources stream" in out, "no title was produced, so no tier was tested"
    assert leaks == [], f"R:T2SCAN — orientation read past T0: {leaks}"
    over = [l for l in out.splitlines() if len(l) > 100]
    assert not over, f"R:ROWBLOAT — a row wrapped:\n" + "\n".join(over)


def test_show_header_carries_the_title(bundle):
    """covers: M2 — `show` named the cid, the beat and the type, and never the title."""
    add.new(bundle, "Task", "t-show", title="Bounded CLI memory")
    header = add.show(bundle, "/tasks/t-show.md")[1].splitlines()[0]
    assert "Bounded CLI memory" in header, f"the show header carried no title: {header}"


def test_new_goal_writes_the_card(bundle):
    """covers: M4, R:TWOGOALS, A2, A7, A10, E4 — one goal, in the place every reader looks."""
    add.new(bundle, "Task", "t-goal", title="Bounded CLI memory",
            goal="live sources stream results instead of accumulating them")
    body = (Path(bundle) / "tasks" / "t-goal.md").read_text()
    goals = [l for l in body.splitlines() if l.startswith("goal:")]
    assert len(goals) == 1, f"R:TWOGOALS — the node carries {len(goals)} goal lines: {goals}"
    assert "live sources stream" in goals[0], goals
    assert goals[0] in add.card_of(body.split("---", 2)[2]), \
        "the goal was written to frontmatter, not to the CARD where every guard looks"

    add.new(bundle, "Task", "t-bare", title="No goal passed")   # A10
    assert "goal: <one line>" in (Path(bundle) / "tasks" / "t-bare.md").read_text()


def test_the_front_door_takes_the_goal(bundle):
    """covers: M4 — the planner types `add new --goal`; `add.new(goal=)` is not a front door.

    The library is not the entry point: `add.py` prints nothing and nobody invokes it. A Must
    about what `add new` accepts is only met when `cli.py` accepts it, so this check goes through
    the CLI the way a planner does — argv, exit code, and the file that lands.
    """
    out = subprocess.run(
        [sys.executable, str(REPO / "tooling" / "cli.py"), "--root", str(bundle),
         "new", "Task", "t-cli", "--title", "T", "--goal", "the seeded line"],
        capture_output=True, text=True)
    assert out.returncode == 0, f"`add new --goal` refused at the front door:\n{out.stderr}"
    body = (Path(bundle) / "tasks" / "t-cli.md").read_text()
    assert "goal: the seeded line" in add.card_of(body.split("---", 2)[2]), body


def test_new_refuses_a_field_it_does_not_know(bundle):
    """covers: M5, R:GHOSTFIELD, A5, A15, E5 — no ghost data in frontmatter."""
    node, note = add.new(bundle, "Task", "t-ghost", title="T", owner="someone")
    assert node is None, "an unrecognised field was accepted"
    assert not (Path(bundle) / "tasks" / "t-ghost.md").exists(), "a refused create wrote a file"
    assert "owner" in note, note
    for legal in ("title", "goal", "depth", "sensitivity", "milestone", "scope"):
        assert legal in note, f"A15 — the refusal did not enumerate the accepted set:\n{note}"
