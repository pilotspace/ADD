"""e18 · D-12 fires — three status flags are withdrawn, not erased.

The red suite for `cut-status-flags`. A deletion's red is the mirror of a feature's: every
check here asserts an ABSENCE, so each one fails while the code is still present and passes
once it is gone. That inversion is the whole reason this file exists — a cut with no suite
is indistinguishable from a cut that forgot something, and the thing it forgot is usually
the collateral (R:COLLATERAL).

Three of these flags are `build-orient`'s M1, M3 and M4, and that node carries a human gate.
`test_gated_node_untouched` is the one that matters most: the record of what was accepted
must survive the withdrawal of what it accepted (§3.6, R:ERASE).
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    """A small bundle with a milestone and two tasks — enough for `status` to have work to do."""
    add.init(tmp_path, "code", "Cut")
    add.new(tmp_path, "Milestone", "m-one", title="Milestone One")
    add.new(tmp_path, "Task", "alpha-task", title="Alpha", milestone="/milestones/m-one.md")
    add.new(tmp_path, "Task", "beta-task", title="Beta confirmation",
            milestone="/milestones/m-one.md")
    return tmp_path


# ------------------------------------------------------------------ M1 · the three are gone


@pytest.mark.parametrize("name", ["locate", "graph_lines", "since"])
def test_the_withdrawn_functions_are_gone(name):
    """covers: M1, R:SILENTCUT · D-12's first three steps, spent."""
    assert not hasattr(add, name), \
        f"`{name}` still exists — D-12's cut was recorded but not made"


def test_status_no_longer_takes_the_three_parameters():
    """covers: M1 · the branches go with the functions, not just the functions."""
    import inspect
    params = set(inspect.signature(add.status).parameters)
    assert not (params & {"locate_term", "milestone", "since_date"}), \
        f"status still accepts a withdrawn flag: {sorted(params)}"


# ------------------------------------------------- M2 · the gate's record survives the cut


def test_gated_node_untouched():
    """covers: M2, R:ERASE · e6 keeps its M1/M3/M4 exactly as the human gate accepted them.

    The rules were true when gated. A gate records what was ACCEPTED, never what still ships,
    so rewriting them to match the cut would erase the accepted claim rather than supersede it.
    """
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", ".add/tasks/build-orient.md"],
                         cwd=REPO, capture_output=True, text=True, timeout=30)
    assert not out.stdout.strip(), "build-orient.md was edited to match the cut (R:ERASE)"


@pytest.mark.skip(reason="dogfood: asserts add-skill's own cut record ('1921 -> 1865') in its dev bundle; not portable")
def test_the_withdrawal_is_recorded_somewhere():
    """covers: M3, R:SILENTCUT · a removed feature that leaves no trace is a feature that lied."""
    node = (REPO / ".add" / "tasks" / "cut-status-flags.md").read_text(encoding="utf-8")
    assert "## RETIRED" in node, "the four withdrawn checks were deleted with no record"
    for name in ("test_locate_by_slug_fragment", "test_locate_by_title_fragment",
                 "test_graph_is_per_milestone", "test_since_uses_stamps_not_mtime"):
        assert name in node, f"{name} vanished from the suite with no record of why"


# ------------------------------------------------------------- M4 · nothing else moved


@pytest.mark.skip(reason="dogfood: asserts add-skill's own measured saving in its dev bundle; not portable")
def test_the_saving_is_measured_not_estimated():
    """covers: M5 · a cut fired on an estimate must leave behind the number it should have been.

    F21 found A3's estimate for these same three flags was wrong by 5-7x. D-12's remaining step
    is still an estimate, so this node's measured figure is the only calibration it has.
    """
    node = (REPO / ".add" / "tasks" / "cut-status-flags.md").read_text(encoding="utf-8")
    assert "1921 → 1865" in node, "the actual saving was never written down"
    assert "247" in node, "the measurement was recorded without the estimate it corrects"


def test_status_still_orients(bundle):
    """covers: M4, R:COLLATERAL · the surface the cut was NOT supposed to touch."""
    out = add.status(bundle)
    assert "alpha-task" in out
    assert "next:" in out, "a verb stopped ending in a runnable next step"


def test_status_stays_within_its_line_budget(bundle):
    """covers: M4, R:COLLATERAL, A12 · the 20-line orientation budget is unchanged."""
    for i in range(30):
        add.new(bundle, "Task", f"filler-{i}", title=f"Filler {i}",
                milestone="/milestones/m-one.md")
    assert len(add.status(bundle).splitlines()) <= 25, "the orientation budget grew"


def test_card_drift_survives(bundle):
    """covers: M4, R:COLLATERAL · e6's M5 is NOT part of the cut and must still work."""
    assert hasattr(add, "card_drift"), "the cut took a function it was not meant to take"
    assert isinstance(add.card_drift(add.scan(bundle)), list)
