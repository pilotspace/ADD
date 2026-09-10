"""Red suite for `persona-loads-on-every-path` — the lens loads by fit, not by spawn.

Measured over this bundle at direction: 15 of 190 lifecycle nodes carry a lens, and 3 of 40
milestones — the one lane `intake.md` already says must load one. The mandate is not missing; it
is well written and lives in `agents/add-worker.md` §2 ("Become the persona FIRST"), a file loaded
ONLY when a subagent is spawned. The three beat guides mentioned a persona zero, zero and once,
and that once is the security `R:NOCOVERAGE` paragraph.

So the lens was a function of whether the human spawned an agent. These checks pin the selector
onto the path that does not spawn, and pin the four copies of it to agree.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
sys.path.insert(0, str(Path(__file__).parent))

# The three EXECUTION beats. `explore.md` is deliberately absent (A2): an explore node's
# deliverable is cited findings and its lens question is the advisor's, which `intake.md` owns.
BEAT_GUIDES = ("direction.md", "build.md", "verify.md")

# The two frontmatter keys the roster's selector reads. `personas.md` states the contract; every
# copy of the SELECTOR must route on exactly these, or two agents route the same node differently.
SELECTOR_KEYS = ("flow:", "task-kinds:")

# Tier 1 is the project's own roster, tier 2 the vendored teacher index. Both `add-worker.md` §2
# and `add-advisor.md` §2 already state this order; a guide that inverts it is R:DRIFTCOPY.
TIER1 = ".add/personas/"
TIER2 = "personas-index/use-when.md"


def _guide(name):
    return (SKILL / "phases" / name).read_text(encoding="utf-8")


def _worker_selector():
    """`add-worker.md` §2 — the copy that has always been right, and the one the others match."""
    body = (REPO / "agents" / "add-worker.md").read_text(encoding="utf-8")
    start = body.index("## 2 · Become the persona")
    end = body.index("\n## ", start + 1)
    return body[start:end]


def _surface_lines(read):
    """Total lines over every .md the router can reach, `persona-author/` excluded (its own budget).

    `read` takes a path relative to the GIT ROOT — the repo is a parent of `add-method/` — so the
    SAME measurement runs over the working tree and over `HEAD`, which is what makes "funded" a
    comparison rather than a literal this module would hold (and `test_one_budget_one_guard.py`
    would then refuse it).
    """
    total = 0
    for f in sorted(SKILL.rglob("*.md")):
        if "persona-author" in f.parts:
            continue
        text = read(f.relative_to(REPO.parent).as_posix())
        if text is not None:
            total += len(text.splitlines())
    return total


def _at_head(rel):
    out = subprocess.run(["git", "show", f"HEAD:{rel}"],
                         cwd=REPO.parent, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def test_every_execution_beat_guide_selects_a_lens():
    """covers: M1, A1, A3 — the roster, the verb, and the load placed BEFORE the beat's work."""
    for name in BEAT_GUIDES:
        text = _guide(name)
        assert TIER1 in text, (
            f"phases/{name} never names the roster an agent working this beat should read. The "
            f"rule exists in agents/add-worker.md §2 and loads only on a spawn — that is the bug.")
        assert "add advise" in text, \
            f"phases/{name} names no way to RECORD the pick, so the lens cannot reach a brief"


def test_the_four_copies_state_one_selector():
    """covers: M2, M3, R:DRIFTCOPY, A5 — enumerated, on both keys, in one tier order.

    ENUMERATED on purpose: the selector is now written in four places, and four copies of a rule
    is four things that drift. This names all four so a fifth cannot appear quietly stating a
    different rule, and so no copy can be edited alone.
    """
    copies = {f"phases/{n}": _guide(n) for n in BEAT_GUIDES}
    copies["agents/add-worker.md §2"] = _worker_selector()
    for where, text in copies.items():
        for key in SELECTOR_KEYS:
            assert key in text, \
                f"{where} routes on something other than `{key}` — two agents will pick differently"
        assert TIER1 in text and TIER2 in text, \
            f"{where} names only one tier; the fallback is half the selector"
        assert text.index(TIER1) < text.index(TIER2), (
            f"R:DRIFTCOPY — {where} puts the teacher corpus before the project's own roster. A "
            f"project persona was authored for THIS bundle; a teacher entry never was.")


def test_the_roster_is_optional_and_the_load_is_not():
    """covers: M4, A4, R:MANDATORYROSTER — what is opt-in is the roster, never the load."""
    router = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "persona is opt-in" not in router, (
        "SKILL.md still calls the LOAD opt-in. `opt-in` is true of the ROSTER (a bundle may have "
        "none) and false of the load (if a persona fits, it loads) — and the router is the one "
        "file always in context, so its word is the one that governs.")
    for name in BEAT_GUIDES:
        text = _guide(name)
        assert "none" in text.lower().split("add advise")[0].rsplit(TIER1, 1)[-1] \
            or "neither" in text.lower(), (
            f"R:MANDATORYROSTER — phases/{name} names no exit for a bundle whose roster has no "
            f"fit, so a roster-less bundle is told at every beat that it is missing something.")


def test_only_the_execution_beats_gained_it():
    """covers: A2 — the instruction landed where it was aimed, and nowhere else."""
    explore = (SKILL / "phases" / "explore.md").read_text(encoding="utf-8")
    assert TIER1 not in explore, (
        "phases/explore.md gained the selector. An explore node's lens question belongs to the "
        "advisor flow, which intake.md already owns — and the surface budget pays for every line.")


def test_the_addition_was_funded():
    """covers: M5, A6, R:PINBUMP — compressed to pay for itself; no budget literal moved."""
    before = _surface_lines(_at_head)
    after = _surface_lines(lambda rel: (REPO.parent / rel).read_text(encoding="utf-8"))
    assert before, "nothing resolved at HEAD, so this comparison proves nothing"
    assert after <= before, (
        f"the skill surface grew {after - before} line(s) ({before} -> {after}). The budgets are "
        f"ceilings, not baselines: fund the addition by compressing, or it is not designed yet.")

    rel = "add-method/tests/skill/skill_budget.py"
    head = _at_head(rel)
    assert head is not None, "skill_budget.py did not resolve at HEAD"
    assert head == (REPO / "tests" / "skill" / "skill_budget.py").read_text(encoding="utf-8"), \
        "R:PINBUMP — a budget literal moved. A ceiling raised to fit an addition is not a ceiling."
