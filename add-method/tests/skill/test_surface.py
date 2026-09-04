"""The skill surface: valid frontmatter, within budget, and every command it names is real.

The last test is the load-bearing one — it makes the "dispatch gap" seam impossible to ship
silently. If SKILL.md tells an agent to run `add <verb>` and no dispatch verb exists, this fails.
"""
import hashlib
import inspect
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
sys.path.insert(0, str(REPO / "tooling"))

import argparse  # noqa: E402
import cli  # noqa: E402  — the real ABF-1 CLI; the skill must stay honest to its verb set


def _cli_verbs():
    sub = [a for a in cli.build_parser()._actions if isinstance(a, argparse._SubParsersAction)][0]
    return set(sub.choices)


def _frontmatter(text: str) -> str:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def test_router_frontmatter_is_valid():
    fm = _frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    assert re.search(r"^name:\s*add\s*$", fm, re.M), "name: add missing"
    assert "description:" in fm, "description missing"
    assert re.search(r"^user-invocable:\s*true\s*$", fm, re.M), "user-invocable: true missing (needed for /add)"


def test_router_within_line_budget():
    n = len((SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines())
    assert n <= 176, f"SKILL.md is {n} lines (budget 176 — the only always-loaded cost; re-pinned from 150 at 3.1.0, human call)"


# Newline count is a PROXY for the always-loaded cost, not the cost itself. A reflow — same
# content, restructured into fewer, longer lines — makes the pin above go greener while the
# real cost (what actually loads into context) rises. That happened for real, this session:
# SKILL.md held at 176/176 lines while it grew 189 bytes. BYTE_BUDGET closes that hole; it does
# NOT replace the line pin above, which stays in its own unit because it is a recorded HUMAN
# call (task budget-pin-measures-cost).
BYTE_BUDGET = 13258  # ratchet: pinned to the measured byte count of skill/add/SKILL.md at authoring time — never raise without funding it elsewhere


def _assert_within_byte_budget(nbytes, budget=BYTE_BUDGET):
    """The guard a pure reflow cannot dodge.

    Two pins exist on SKILL.md on purpose — this one is NOT redundant with
    `test_router_within_line_budget` above. That pin holds a human-set number (176) in its
    own unit (lines) for its own reason (re-pinned from 150 at 3.1.0, a human call). THIS
    pin measures the real always-loaded cost (bytes) so a reflow — same content, fewer
    lines, more bytes — cannot pass by moving the metric instead of moving the cost.
    Delete this pin as "redundant" and that hole reopens.
    """
    assert nbytes <= budget, (
        f"SKILL.md is {nbytes} bytes — over the {budget}-byte pin (R:BUDGET_BUMP). "
        f"This is a SEPARATE pin from the line-count budget above, not a duplicate of it: "
        f"it measures the real always-loaded cost so a reflow (same content, fewer lines, "
        f"more bytes) cannot pass by moving the metric instead of the cost. Fund any growth "
        f"by compressing elsewhere in SKILL.md — never by raising this number."
    )


def test_skill_byte_budget_holds():
    nbytes = len((SKILL / "SKILL.md").read_bytes())
    _assert_within_byte_budget(nbytes)


def _reflow_merge_pairs(text):
    """A pure reflow fixture: identical content, roughly HALF the newlines, but MORE bytes —
    the exact shape of move that got 189 bytes of growth past the line-only pin this session
    while SKILL.md held at 176/176 lines. Joins consecutive lines with a separator wider
    than the single-byte newline it replaces, so line count drops while byte count rises.
    """
    lines = text.splitlines()
    sep = "  <>  "  # 6 bytes, replacing the 1-byte "\n" it stands in for -> +5 bytes/merge
    merged = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines):
            merged.append(lines[i] + sep + lines[i + 1])
            i += 2
        else:
            merged.append(lines[i])
            i += 1
    return "\n".join(merged) + "\n"


def test_byte_pin_catches_a_pure_reflow_the_line_pin_would_miss():
    """Prove the reflow hole is closed. Built on a FIXTURE derived from the real SKILL.md —
    the reflow never lands on disk, no skill-tree file is edited.

    covers: the crux of task budget-pin-measures-cost — a budget check must fail on a
    reflow that cuts newlines while growing bytes, not merely on a raw size increase.
    """
    original = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    reflowed = _reflow_merge_pairs(original)

    original_lines = len(original.splitlines())
    reflowed_lines = len(reflowed.splitlines())
    reflowed_bytes = len(reflowed.encode("utf-8"))

    assert reflowed_lines < original_lines, "fixture setup: the reflow must actually cut lines"
    assert reflowed_lines <= 176, (
        "fixture setup: the reflow must still pass the line-ONLY pin — that PASS is exactly "
        "the vulnerability this task closes, so the byte pin below has to be what stops it"
    )
    assert reflowed_bytes > BYTE_BUDGET, (
        "fixture setup: the reflow must actually grow bytes past the pin, or this proves nothing"
    )

    with pytest.raises(AssertionError, match="byte pin"):
        _assert_within_byte_budget(reflowed_bytes)


def test_line_pin_survives_unreplaced_by_this_task():
    """covers: M2, R:SILENT_REPIN. The byte pin is an ADDITION, not a re-cast of the human's
    176-line call into a different unit. Proves `test_router_within_line_budget` — name,
    literal 176, and its "human call" rationale — is still exactly present in this file,
    never edited or dropped in favour of the new byte pin."""
    src = Path(__file__).read_text(encoding="utf-8")
    assert "def test_router_within_line_budget" in src, "the line-pin test was removed"
    fn_src = inspect.getsource(test_router_within_line_budget)
    assert "n <= 176" in fn_src, "the 176-line literal was changed or removed"
    assert "re-pinned from 150 at 3.1.0, human call" in fn_src, (
        "the line pin's human-call rationale was reworded or dropped — a floor sentence "
        "decaying through \"clarification\" is a floor that is already gone"
    )


def test_byte_pin_scoped_to_source_tree_only():
    """covers: A2. The byte pin measures the SOURCE skill tree only, the same scope the
    line pin already has — the two mirror trees stay bound by the pre-existing
    byte-identical parity test (`test_quick_lane_size_gate.py::test_three_skill_trees_identical`),
    never duplicated here."""
    fn_src = inspect.getsource(test_skill_byte_budget_holds)
    assert "TREES" not in fn_src, "the byte pin must not iterate the three-tree TREES tuple"
    assert 'SKILL / "SKILL.md"' in fn_src, "the byte pin must read the source tree's SKILL.md directly"


def test_skill_tree_prose_unedited_by_this_task():
    """covers: M5, R:PROSE_FIX. A new pin that comes up red against shipped content is a
    finding to report, never prose to fix. Pins SKILL.md and intake.md to their sha256 as
    measured when this task was authored — proof this task's own tests never touched them."""
    pinned = {
        "SKILL.md": "be921c453bf10344b9b0ac60ef0802def6561fb3e5070e74adff16633bd4370a",   # re-aimed @ 3.5.0: metadata version bump only, no prose edit. prior: d3170f4b…
        "intake.md": "ee78c0816e09eba20be82535b7e8729c42a715589743508c2dcd5f4155e95e41",   # re-aimed @ skill-reads-the-graph: the loop reads the graph before it plans. prior: db288507…
    }
    for name, want in pinned.items():
        got = hashlib.sha256((SKILL / name).read_bytes()).hexdigest()
        assert got == want, f"{name}: sha256 changed — skill-tree prose was edited (R:PROSE_FIX)"


def test_no_single_ref_over_split_threshold():
    for path in SKILL.rglob("*.md"):
        if path.name == "SKILL.md":
            continue
        n = len(path.read_text(encoding="utf-8").splitlines())
        assert n <= 350, f"{path.relative_to(SKILL)} is {n} lines — split it (T3 rule)"


def _own_docs():
    """The `add` skill's own docs. `persona-author/` is a NESTED sub-skill with its own SKILL.md and
    its own budget — it is loaded on its own terms, not as part of this router's disclosure cost, so
    it is not counted here (the add-skill-2 tree this came from has no nested sub-skill at all)."""
    return [p for p in SKILL.rglob("*.md") if "persona-author" not in p.relative_to(SKILL).parts]


def test_total_surface_within_budget():
    total = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in _own_docs())
    assert total <= 1500, f"skill surface is {total} lines (budget 1500; 2.5 was 2031)"


def test_every_wired_verb_is_documented():
    """The other direction of the anti-seam: a verb the engine ships that no doc names.

    The phantom direction (a doc naming a verb the CLI lacks) was already guarded. The orphan
    direction was not, so a shipped verb could be invisible to the only thing an agent reads —
    which is how `advise` (the sequential remedy R:NOCOVERAGE's refusal asks for), `doctor`,
    `locate` and `todo` came to be documented nowhere.
    """
    documented = set()
    for path in _own_docs():
        text = path.read_text(encoding="utf-8")
        documented |= {m.group(1) for m in re.finditer(r"`?add\s+([a-z][a-z-]{1,22})\b", text)}
    orphans = _cli_verbs() - documented
    assert not orphans, f"engine ships verbs no skill doc names: {sorted(orphans)}"


def test_router_commands_are_real_dispatch_verbs():
    """Every `add <verb>` in SKILL.md's bash cookbook maps to a real spike_cli verb."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
    assert blocks, "SKILL.md has no ```bash cookbook block"
    verbs = {m.group(1) for b in blocks for line in b.splitlines()
             if (m := re.match(r"add\s+([a-z-]+)", line.strip()))}
    assert verbs, "no `add <verb>` command lines found in the cookbook"
    unknown = verbs - _cli_verbs()
    assert not unknown, f"SKILL.md names commands with no dispatch verb: {sorted(unknown)}"
