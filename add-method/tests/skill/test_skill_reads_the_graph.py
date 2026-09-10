"""The always-loaded skill teaches the graph — read a node whole, query it by field.

Red-first for `/tasks/skill-reads-the-graph.md`.

Three verbs shipped this milestone and the skill named none of them: the orient branch still
told an agent to `open .add/tasks/<slug>.md` and read its CARD by hand — the exact `cat` that
`add show` exists to replace. A capability the always-loaded surface does not name is a
capability nobody uses.

The budget is the hard part and it is checked HERE rather than trusted: SKILL.md sits at its
176-line ceiling, so every added line is funded by retiring a duplicate, and a retired
sentence's claim must still be asserted somewhere in the same file (R:NEUTERED) — otherwise
the cheapest way to fit is to make the document shorter and worse.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

SKILL = REPO / "skill" / "add"
TREES = (SKILL,
         REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")



def _skill() -> str:
    return (SKILL / "SKILL.md").read_text(encoding="utf-8")


def _intake() -> str:
    return (SKILL / "intake.md").read_text(encoding="utf-8")


def _wired_verbs() -> set:
    source = (REPO / "tooling" / "cli.py").read_text(encoding="utf-8")
    return set(re.findall(r'sub\.add_parser\("([a-z-]+)"', source))


def test_orient_reads_the_node_through_the_engine():
    """covers: M1, A2 — the branch names `add show`, and no longer hand-opens the file."""
    text = _skill()
    branch = next((ln for ln in text.splitlines() if "**A task is active**" in ln), "")
    assert branch, "the orient branch for an active task is gone"
    assert "add show" in branch, f"the orient branch does not read through the engine: {branch}"
    assert ".add/tasks/" not in branch, (
        f"the branch still instructs opening the task file by hand — the `cat` that `add show` "
        f"replaces: {branch}")


def test_intake_routes_name_a_graph_read():
    """covers: M2, A4, A5 — both planning routes read before they draft, in both files."""
    skill = _skill()
    for marker in ("- **Task**", "- **Project / milestone**"):
        line = next((ln for ln in skill.splitlines() if ln.startswith(marker)), "")
        assert line, f"SKILL.md lost the {marker} route"
        assert "add show" in line or "add search" in line, \
            f"SKILL.md {marker} names no graph read: {line}"

    intake = _intake()
    assert "### Task" in intake and "### Project / milestone" in intake, \
        "intake.md lost the sections that carry the read step"
    for section in ("### Task", "### Project / milestone"):
        body = intake.split(section, 1)[1].split("\n### ", 1)[0]
        assert "add show" in body or "add search" in body, \
            f"intake.md {section} names no graph read"


def test_cookbook_shows_the_search_filters():
    """covers: M3 — the row shows the field grammar, not only the free-text one."""
    row = next((ln for ln in _skill().splitlines() if ln.startswith("add search")), "")
    assert row, "the cookbook lost its search row"
    for flag in ("--type", "--status", "--milestone"):
        assert flag in row, f"the search row does not show {flag}: {row}"


# RETIRED: test_skill_stays_within_both_pins (M4, R:BUDGET_BUMP, E1)
#
# Every line of it was a second opinion about numbers another guard owns: it re-asserted the line
# and byte budgets, held its own copies of both, and then pinned the OWNER'S SOURCE TEXT so a
# re-pin would red here too. That is what made a one-line overrun report fourteen failures and a
# re-pin a hunt for eight literals.
#
# Both budgets now live in tests/skill/skill_budget.py, asserted once each by the guards named
# there, and `test_one_budget_one_guard.py` refuses a second assertion anywhere. Funding a line by
# compression rather than by raising a pin is still the rule — it is enforced in one place.
# Retired by `one-budget-one-guard`.


def test_no_claim_was_deleted_by_compression():
    """covers: R:NEUTERED, E2 — a retired row's claim survives in the prose.

    Enumerated: every cookbook row retired to fund an addition in this milestone, paired with
    the sentence that must still carry its claim. A denylist with no surviving-claim assertion
    makes deletion the cheapest way to pass.
    """
    text = _skill()
    retired = {
        "add done": "`add done` is only for closing after a signed `RISK-ACCEPTED`",
    }
    for row, claim in retired.items():
        assert not any(ln.startswith(row + " ") for ln in text.splitlines()), \
            f"{row!r} is still a cookbook row — this guard is testing the wrong thing"
        assert claim in text, \
            f"{row!r} was retired and its claim went with it (R:NEUTERED): {claim!r}"


def test_new_prose_names_only_wired_verbs():
    """covers: R:PHANTOM, E3 — every verb the skill names is a real subcommand."""
    verbs = _wired_verbs()
    assert "show" in verbs and "search" in verbs, \
        "the CLI does not wire the verbs under test, so this guard proves nothing"
    named = set(re.findall(r"\badd ([a-z][a-z-]+)\b", _skill() + _intake()))
    prose = {"the", "a", "an", "learn", "and", "it", "them", "this", "one", "your", "new"}
    unknown = {v for v in named - verbs - prose if "-" in v or len(v) > 3}
    assert not unknown, f"the skill names verbs the CLI does not wire (R:PHANTOM): {sorted(unknown)}"


def test_three_trees_are_byte_identical():
    """covers: M5, R:DRIFT, E4 — one string, three trees."""
    for name in ("SKILL.md", "intake.md"):
        seen = {}
        for tree in TREES:
            path = tree / name
            if not path.exists():
                continue                  # a gitignored twin — exists-skip, never a false green
            seen[str(tree)] = path.read_bytes()
        assert len(seen) >= 2, f"only {len(seen)} tree(s) carry {name}; parity proves nothing"
        assert len(set(seen.values())) == 1, f"{name} diverged across trees: {sorted(seen)}"


def test_prose_pin_was_re_aimed():
    """covers: M6, E5 — the pin matches the shipped bytes and records where it came from."""
    import hashlib
    import sys
    sys.path.insert(0, str(REPO / "tests" / "skill"))
    from skill_budget import PROSE_PINS

    # RE-AIMED (one-home-for-the-prose-pin): this recovered the hash by REGEXING
    # `test_surface.py`'s source — a check pinning another check's source text, which is the
    # scatter `skill_budget.py` exists to end. The claim is unchanged; it now imports.
    pinned = PROSE_PINS["SKILL.md"]
    assert pinned == hashlib.sha256((SKILL / "SKILL.md").read_bytes()).hexdigest(), \
        "the prose pin does not match the shipped SKILL.md"
    src = (REPO / "tests" / "skill" / "skill_budget.py").read_text(encoding="utf-8")
    line = next(l for l in src.splitlines() if pinned in l)
    assert "prior:" in line, f"the re-aim records no prior hash: {line}"
