"""The loop routes through `add deltas` before it plans a Task or Milestone.

Lessons already accumulate in `.add/specs/*.md` (40 open at last count) with nothing in the
planning path that ever reads them back — a spec nothing reads is an archive, not a living
spec (task `skill-reads-deltas`, milestone `okf-graph-time`). This gate makes the routing
instruction load-bearing: it must name `add deltas` at every surface that plans (the
always-loaded router's own Intake bullets, and the fuller `intake.md` Task/Project sections),
in every shipped skill tree, and the verb it names must be real and must actually report —
never prose pointing at a phantom or a silent no-op (the `add.py status` class of bug).

Deliberately silent on the delta LINE grammar (tag, id, validity interval): a concurrent task
(`dated-addressable-deltas`) is actively reworking that shape. This file binds only the ROUTING
instruction and the stable ENVELOPE `add.deltas()` reports (an item count or "no open deltas",
plus a `next:` trailer) — never a delta line's internal shape.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]          # add-method/
ROOT = REPO.parent                                   # repo root
SKILL = REPO / "skill" / "add"
TREES = (SKILL, ROOT / ".claude" / "skills" / "add",
          REPO / "src" / "add_method" / "_bundled" / "skill" / "add")

sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402 — the engine `add.deltas` dispatches into
import cli  # noqa: E402 — the real ABF-1 CLI; the source of truth on which verbs are wired


def _cli_verbs() -> set:
    sub = next(a for a in cli.build_parser()._actions if getattr(a, "choices", None))
    return set(sub.choices)


def _skill_bullet(text: str, name: str) -> str:
    """The `- **<name>**` Intake bullet body, up to the next top-level bullet or the closing
    floor paragraph — the same lazy-match idiom test_quick_lane_size_gate.py uses."""
    m = re.search(rf"^- \*\*{re.escape(name)}\*\*.*?(?=\n- \*\*|\n\n\*\*The floor)",
                  text, re.M | re.S)
    assert m, f"SKILL.md: no `- **{name}**` intake bullet"
    return m.group(0)


def _intake_section(text: str, heading_word: str) -> str:
    m = re.search(rf"^### {re.escape(heading_word)}.*?(?=\n### |\Z)", text, re.M | re.S)
    assert m, f"intake.md: no `### {heading_word}` section"
    return m.group(0)


def test_skill_router_routes_task_and_milestone_through_deltas():
    """covers: M1 — the always-loaded router names `add deltas` in both lanes that plan,
    in every shipped skill tree, and the verb it names is real (not a phantom)."""
    assert "deltas" in _cli_verbs(), "`add deltas` is no longer a real, wired CLI verb"
    for tree in TREES:
        text = (tree / "SKILL.md").read_text(encoding="utf-8")
        task = _skill_bullet(text, "Task")
        milestone = _skill_bullet(text, "Project / milestone")
        assert re.search(r"add deltas", task), \
            f"{tree}: SKILL.md Task bullet never names `add deltas`"
        assert re.search(r"add deltas", milestone), \
            f"{tree}: SKILL.md Project/milestone bullet never names `add deltas`"


def test_intake_ref_routes_task_and_milestone_through_deltas():
    """covers: M2 — the fuller reference repeats the routing at both planning surfaces,
    in every shipped skill tree."""
    for tree in TREES:
        text = (tree / "intake.md").read_text(encoding="utf-8")
        task = _intake_section(text, "Task")
        milestone = _intake_section(text, "Project / milestone")
        assert re.search(r"add deltas", task), \
            f"{tree}: intake.md Task section never names `add deltas`"
        assert re.search(r"add deltas", milestone), \
            f"{tree}: intake.md Project/milestone section never names `add deltas`"


def test_add_deltas_actually_executes_and_reports(tmp_path):
    """covers: M3, E1 — the command the docs point at is not a silent no-op.

    Format-agnostic on purpose: only `add.deltas`'s own contract is asserted — an item count
    or "no open deltas", plus a `next:` line — never a delta line's tag/id/interval shape.
    Exercises three paths so the check discriminates rather than merely returning truthy:
    a populated bundle, an empty one, and one carrying a malformed (no-evidence) line that
    must be REPORTED, never silently dropped (the exact failure mode `deltas()` already
    guards against).
    """
    populated = tmp_path / "populated" / ".add"
    (populated / "specs").mkdir(parents=True)
    (populated / "specs" / "method.md").write_text(
        "---\ntype: Spec\ntitle: t\n---\n## Deltas\n\n"
        "- [ADD · open] a probe lesson (evidence: probe)\n"
        "- [ADD · open] a lesson missing its evidence pointer\n",
        encoding="utf-8")

    items, note = add.deltas(str(populated), status="open")
    assert len(items) == 1, f"add.deltas misread the seeded bundle: {note}"
    assert re.match(r"open deltas \(\d+\):", note), f"unexpected envelope: {note!r}"
    assert "next:" in note, f"add.deltas dropped its next: trailer: {note!r}"
    assert "no_evidence" in note or "malformed" in note, \
        f"the no-evidence line was silently dropped, not reported: {note!r}"

    empty = tmp_path / "empty" / ".add"
    (empty / "specs").mkdir(parents=True)
    items2, note2 = add.deltas(str(empty), status="open")
    assert items2 == []
    assert note2.startswith("no open deltas"), f"unexpected empty envelope: {note2!r}"


def test_skill_budget_holds_at_the_pinned_line_count():
    """covers: M4, R:BUDGET_BUMP — the addition is funded by compression, never a pin raise.

    The pin is READ from test_surface.py, never copied as a literal — the exact lesson this
    milestone's own carried deltas already record about method-steward hard-coding a stale 150.
    """
    src = (REPO / "tests" / "skill" / "test_surface.py").read_text(encoding="utf-8")
    m = re.search(r"n <= (\d+)", src)
    assert m, "test_surface.py: could not read the SKILL.md line pin"
    pin = int(m.group(1))
    for tree in TREES:
        n = len((tree / "SKILL.md").read_text(encoding="utf-8").splitlines())
        assert n <= pin, f"{tree}/SKILL.md: {n} lines — over the {pin}-line pin (R:BUDGET_BUMP)"


def test_three_skill_trees_stay_identical_after_the_routing_edit():
    """covers: R:ONE_TREE — reuses the repo's own parity oracle so this task cannot drift from
    it; the same assertion test_quick_lane_size_gate.py::test_three_skill_trees_identical makes,
    scoped here to the two files this task actually touches."""
    for rel in ("SKILL.md", "intake.md"):
        src_bytes = (SKILL / rel).read_bytes()
        for tree in TREES[1:]:
            assert (tree / rel).read_bytes() == src_bytes, \
                f"{tree}/{rel}: differs from the source tree — parity broken"
