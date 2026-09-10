"""Red suite for `one-budget-one-guard` — one budget, one guard.

SKILL.md went one line over its 176-line pin and FOURTEEN checks across seven files reported it.
Fourteen failures for one fact. Worse, re-pinning meant finding eight separate literals, so the
first re-pin that finds only seven leaves two live numbers and no error (R:SILENTPIN).

The budgets now live in `skill_budget.py`, each asserted by exactly one named guard. Other checks
may READ a constant to build a message; asserting one outside its owner is what this refuses.
"""

import ast
import re
import pytest
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

import skill_budget  # noqa: E402

OWNERS = {
    "LINE_BUDGET": ("tests/skill/test_surface.py", "test_router_within_line_budget"),
    "BYTE_BUDGET": ("tests/skill/test_surface.py", "test_skill_byte_budget_holds"),
    "SURFACE_BUDGET": ("tests/skill/test_surface.py", "test_total_surface_within_budget"),
}
VALUES = {"LINE_BUDGET": 176, "BYTE_BUDGET": 13258, "SURFACE_BUDGET": 1500}


def _ints_in(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, int) \
                and not isinstance(sub.value, bool):
            yield sub.value


def _asserted_numbers(path):
    """Every numeric literal that appears inside an `assert` in this module: (line, value)."""
    return [(n.lineno, v) for n in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
            if isinstance(n, ast.Assert) for v in _ints_in(n.test)]


def _budget_uses(path):
    """Every place a budget VALUE is asserted or re-declared: (line, how, value).

    An assert holding the literal is the obvious scatter. The one that hid was a module-level
    `LINE_PIN = 176`, whose assertion carries no literal at all — four modules held their own
    copy that way, and three then pinned each other's SOURCE TEXT so the number could only be
    re-pinned everywhere at once, or nowhere.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Assert):
            out += [(n.lineno, "asserts", v) for v in _ints_in(n.test)]
        elif isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None:
            out += [(n.lineno, "re-declares", v) for v in _ints_in(n.value)]
    return out


def test_one_module_owns_the_budgets():
    """covers: M1, M4, E4, A2 — three literals, one home, each carrying why it is that number."""
    for name, expected in VALUES.items():
        assert getattr(skill_budget, name) == expected, \
            f"{name} moved without a re-pin — the module is the single source now"
    src = (REPO / "tests" / "skill" / "skill_budget.py").read_text(encoding="utf-8")
    assert "re-pinned from 150 at 3.1.0" in src, \
        "M4 — the line budget's human-call rationale did not travel with the literal"
    assert "ratchet" in src, "M4 — the byte budget's ratchet rationale did not travel"
    for name, (owner_file, owner_test) in OWNERS.items():
        assert owner_test in src, f"M4 — {name} does not name the guard that owns it"
        owner = (REPO / owner_file).read_text(encoding="utf-8")
        assert f"def {owner_test}(" in owner, \
            f"A5 — {name}'s named owner {owner_file}::{owner_test} does not exist"


def test_only_one_guard_asserts_the_line_budget():
    """covers: M2, M5, R:SCATTERED, A5, E2, E3 — the number, asserted in exactly one place."""
    scattered = []
    for f in sorted((REPO / "tests").rglob("test_*.py")):
        if f.name == Path(__file__).name:
            continue                                   # E3: this module names them to report them
        rel = f.relative_to(REPO).as_posix()
        for line, how, value in _budget_uses(f):
            for name, budget in VALUES.items():
                if value != budget:
                    continue
                owner_file, _ = OWNERS[name]
                if rel != owner_file:
                    scattered.append(f"  {rel}:{line} — {how} {name} ({budget}); "
                                     f"the owner is {owner_file}")
    assert not scattered, (
        "R:SCATTERED — a budget is asserted or re-declared outside the guard that owns it, so "
        "one overrun reports once per module and a re-pin has to find every copy:\n" + "\n".join(scattered)
        + "\n\nImport the constant from skill_budget and drop the assertion — keep this check's "
          "own subject. Reading a constant to build a message is fine; asserting it is not.")


def test_an_overrun_reports_once_and_says_how_to_fix_it():
    """covers: M2, A6, R:SILENTPIN — one failure, and it says what to do about it."""
    import inspect

    import test_surface

    fn = inspect.getsource(test_surface.test_router_within_line_budget)
    assert "LINE_BUDGET" in fn, \
        "the owning guard still holds its own literal — a re-pin would leave two live numbers"
    assert "176" not in fn, "R:SILENTPIN — the literal survived beside the constant"
    for cue in ("compress", "budget"):
        assert cue in fn.lower(), (
            f"A6 — the one surviving message dropped the guidance the fourteen carried "
            f"between them: no mention of '{cue}'")


def test_the_other_checks_keep_their_own_subject():
    """covers: M3, E1, A4 — a stripped check still proves what it was written for."""
    import test_surface

    src = (REPO / "tests" / "skill" / "test_surface.py").read_text(encoding="utf-8")
    fn = __import__("inspect").getsource(test_surface.test_line_pin_survives_unreplaced_by_this_task)
    assert "LINE_BUDGET" in fn, \
        "E1 — the self-pin still pins the string `n <= 176`, a line that no longer exists"
    assert "re-pinned from 150 at 3.1.0" in fn or "skill_budget" in fn, \
        "E1 — the self-pin lost its grip on the human-call rationale it was written to hold"
    assert "def test_router_within_line_budget" in src, "the line-pin owner was removed"

    # A4 as REPLANNED: sourcing the constant was not enough — `n == LINE_BUDGET` still asserts
    # the budget, so an overrun would report twice. The check keeps its unique subject, the
    # three-tree MIRROR claim, in a unit the budget cannot move.
    parity = (REPO / "tests" / "test_front_door_claim_truth.py").read_text(encoding="utf-8")
    assert "def test_the_skill_trees_agree_on_their_length(" in parity, \
        "the mirror claim was deleted with the duplicate budget assertion"
    assert "len(set(counts.values())) == 1" in parity, \
        "A4 — the parity check no longer asserts that the three trees agree with each other"
    # The literal may still appear in PROSE explaining why it left (E3); what must be gone is
    # the ASSERTION of it.
    asserted = [v for _, v in _asserted_numbers(REPO / "tests" / "test_front_door_claim_truth.py")]
    assert 176 not in asserted, \
        "R:SILENTPIN — the budget literal is still asserted in the parity check"


# The prose pins joined this module's charge at `one-home-for-the-prose-pin`. They are the same
# defect in a different type: a sha256 held as a literal in `test_surface.py` while
# `test_skill_reads_the_graph.py` recovered it by REGEXING that file's source — three modules
# pinning each other's source text is exactly what `skill_budget.py` exists to end (R:SILENTPIN).
_HEX64 = re.compile(r"[0-9a-f]{64}")


def test_one_module_owns_the_prose_pins():
    """covers: M1, M2, A1, A2, R:SOURCESCRAPE — one home, and nobody scrapes for it."""
    assert getattr(skill_budget, "PROSE_PINS", None), \
        "PROSE_PINS is not in skill_budget.py — the prose pins have no single home"
    for name in ("SKILL.md", "intake.md"):
        assert name in skill_budget.PROSE_PINS, f"{name}'s prose pin did not move to the one home"

    scattered, scraping = [], []
    for f in sorted((REPO / "tests").rglob("test_*.py")):
        if f.name == Path(__file__).name:
            continue
        text = f.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if any(h in line for h in skill_budget.PROSE_PINS.values()):
                scattered.append(f"  {f.relative_to(REPO).as_posix()}:{i}")
        # R:SOURCESCRAPE — reading another CHECK's source to recover a value it holds.
        if "test_surface.py" in text and _HEX64.search(text.split("test_surface.py")[1][:400]):
            scraping.append(f"  {f.relative_to(REPO).as_posix()}")
    assert not scattered, (
        "R:SILENTPIN — a prose pin's hash is written outside skill_budget.py, so a re-aim has to "
        "find every copy:\n" + "\n".join(scattered))
    assert not scraping, (
        "R:SOURCESCRAPE — these modules recover a pin by reading another check's source text. "
        "Import `skill_budget.PROSE_PINS` instead:\n" + "\n".join(scraping))


def test_the_prose_pins_kept_their_record():
    """covers: M3, R:LOSTRECORD, A4, A5, A6 — a hash with no reason is a number nobody can audit."""
    src = (REPO / "tests" / "skill" / "skill_budget.py").read_text(encoding="utf-8")
    for name, digest in skill_budget.PROSE_PINS.items():
        line = next((l for l in src.splitlines() if digest in l), "")
        assert line, f"{name}'s pin is not written as a literal in its own home — it cannot carry a record"
        record = line.split("#", 1)[1] if "#" in line else ""
        assert "aimed @" in record, \
            f"R:LOSTRECORD — {name}'s pin names no task that aimed it: {line.strip()[:90]}"
        assert len(record.split("aimed @", 1)[1].strip()) > 40, \
            f"R:LOSTRECORD — {name}'s pin names a task but no reason: {record.strip()[:90]}"


def test_the_prose_claims_are_unchanged(tmp_path, monkeypatch):
    """covers: M4 — moving the value is not relaxing the claim.

    Drives the OWNING guard, not a re-implementation of it: point its `SKILL` at a tree whose
    SKILL.md is one byte different and it must still raise. A check that only asserted the
    constant exists would pass on a guard that had quietly stopped comparing.
    """
    import test_surface

    for name in skill_budget.PROSE_PINS:
        (tmp_path / name).write_bytes(
            (test_surface.SKILL / name).read_bytes() + b"\n<!-- edited -->\n")
    monkeypatch.setattr(test_surface, "SKILL", tmp_path)
    with pytest.raises(AssertionError, match="R:PROSE_FIX"):
        test_surface.test_skill_tree_prose_unedited_by_this_task()

    # And it is not raising on everything: the real tree still passes.
    monkeypatch.undo()
    test_surface.test_skill_tree_prose_unedited_by_this_task()
