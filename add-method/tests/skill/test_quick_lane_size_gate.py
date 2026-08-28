"""The Quick lane is size-gated, route-and-go, and carries an inline checklist — in all three trees.

covers: task `direct-lane-size-gate` (milestone `right-sized-lane`). Before this task the lane admitted
only "behavior the specs already cover" and its whole discipline was "make the edit"; the sizing rule
lived nowhere a non-skill reader could see it. Every assertion names the file and the missing element
so the next editor fixes the text, not the guard.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]          # add-method/
ROOT = REPO.parent                                   # repo root
SKILL = REPO / "skill" / "add"
TREES = (SKILL, ROOT / ".claude" / "skills" / "add",
         REPO / "src" / "add_method" / "_bundled" / "skill" / "add")
CLAUDE_MD = ROOT / "CLAUDE.md"


def _intake():
    return (SKILL / "intake.md").read_text(encoding="utf-8")


def _quick_section():
    text = _intake()
    m = re.search(r"^### Quick.*?(?=^### )", text, re.M | re.S)
    assert m, "intake.md: no `### Quick` section"
    return m.group(0)


def _skill_quick_bullet():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^- \*\*Quick\*\*.*?(?=^- \*\*)", text, re.M | re.S)
    assert m, "SKILL.md: no `- **Quick**` intake bullet"
    return m.group(0)


def test_quick_lane_admits_by_size_with_floor_first():
    """covers: M1, A3, A9, E1, E2, R:SIZE_OVER_FLOOR."""
    q = _quick_section()
    assert re.search(r"3 (adjacent )?files", q), "intake.md §Quick: no file-count limit (≈3 adjacent files)"
    assert re.search(r"one sitting", q), "intake.md §Quick: no one-sitting diff limit"
    assert re.search(r"unknown[s]? tally.{0,20}zero|zero.{0,30}unknown", q, re.I), \
        "intake.md §Quick: no zero-unknowns limit"
    assert re.search(r"new behavior.{0,40}(admitted|allowed|fits)", q, re.I), \
        "intake.md §Quick: does not admit small new behavior"
    floor = re.search(r"security.{0,5}data.{0,5}architecture", q, re.I)
    gives = re.search(r"`gives:`", q)
    size = re.search(r"3 (adjacent )?files", q)
    assert floor and gives, "intake.md §Quick: the closed floor and the consumed-`gives:` refusal must be stated"
    assert floor.start() < size.start() and gives.start() < size.start(), \
        "intake.md §Quick: the floor and the `gives:` refusal must be listed BEFORE the size limits"


def test_quick_lane_is_route_and_go():
    """covers: M2, A1."""
    q = _quick_section()
    assert "`quick: <intent>" in q, "intake.md §Quick: no `quick: <intent> — <fit>` route line"
    assert re.search(r"veto", q, re.I) and "make it a task" in q, \
        "intake.md §Quick: no after-the-fact veto sentence (\"make it a task\")"
    emit = _intake().split("## What you emit")[1]
    assert re.search(r"Quick.{0,80}(no confirm|without confirm|route-and-go|never waits)", emit, re.I | re.S), \
        "intake.md §What you emit: Quick is not exempted from confirm-first"


def test_quick_lane_has_five_step_checklist():
    """covers: M3, A5, A11."""
    q = _quick_section()
    steps = re.findall(r"^\s*(\d)\. ", q, re.M)
    assert steps == ["1", "2", "3", "4", "5"], f"intake.md §Quick: expected exactly five numbered steps, got {steps}"
    block = q[q.find("1. "):]
    assert len(block.splitlines()) <= 12, "intake.md §Quick: checklist over 12 lines"
    card = re.search(r"card", block, re.I)
    edit = re.search(r"\bedit\b", block[card.end():] if card else "", re.I)
    assert card and edit, "intake.md §Quick: the inline card must come BEFORE the edit"
    assert re.search(r"red.{0,5}green|runs? it red", block, re.I), "intake.md §Quick: red→green not named"
    assert "invariants" in block, "intake.md §Quick: PROJECT.md `invariants:` not named"
    assert re.search(r"never (written|persisted) under `\.add/`|not under `\.add/`", block, re.I), \
        "intake.md §Quick: the card must be declared NOT written under `.add/`"


def test_quick_receipt_is_commit_plus_one_learn_line():
    """covers: M4, A7, R:SILENT_QUICK, R:PERSIST."""
    q = _quick_section()
    assert "commit" in q, "intake.md §Quick: receipt does not name the commit"
    assert re.search(r"add learn <[a-z|]+> .*--evidence <sha>", q), \
        "intake.md §Quick: no mandatory `add learn … --evidence <sha>` line"
    assert '"quick: <intent>"' in q, "intake.md §Quick: no `quick: <intent>` trace form for a lesson-less change"
    assert re.search(r"exactly one .{0,20}learn", q, re.I), "intake.md §Quick: 'exactly one learn line' not stated"
    assert re.search(r"tasks.{0,3}runs", q), "intake.md §Quick: must say nothing is written under `.add/tasks|runs`"


def test_medium_large_reuse_depth_and_milestone():
    """covers: M5, R:NEW_TIER."""
    q = _quick_section()
    assert re.search(r"medium.{0,40}--depth quick", q, re.I), "intake.md §Quick: medium → `--depth quick` mapping missing"
    assert re.search(r"large.{0,60}(standard|deep).{0,40}Milestone", q, re.I | re.S), \
        "intake.md §Quick: large → standard|deep / Milestone mapping missing"
    heads = re.findall(r"^### (\w+)", _intake(), re.M)
    assert set(heads) <= {"Quick", "Task", "Explore", "Project"}, f"intake.md: a new lane heading appeared: {heads}"


def test_skill_bullet_states_size_rule_within_budget():
    """covers: M6, A10, E3, R:BUDGET_BUMP."""
    b = _skill_quick_bullet()
    assert re.search(r"3 (adjacent )?files", b), "SKILL.md Quick bullet: no ≈3-files size rule"
    assert re.search(r"security.{0,5}data.{0,5}architecture|floor", b, re.I), "SKILL.md Quick bullet: floor not named"
    assert re.search(r"card|checklist", b, re.I), "SKILL.md Quick bullet: inline card/checklist not named"
    assert "learn" in b, "SKILL.md Quick bullet: mandatory learn line not named"
    n = len((SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines())
    assert n <= 176, f"SKILL.md is {n} lines — over the 176 pin"
    # R:BUDGET_BUMP — the pin must not be raised to fund the bullet. Two files carry the literal;
    # test_skill_profile_truth.py deliberately DERIVES it from test_surface.py, so pin the derivation.
    for t in ("test_surface.py", "test_uncertainty_routing.py"):
        src = (REPO / "tests" / "skill" / t).read_text(encoding="utf-8")
        assert re.search(r"<= ?176\b", src), f"{t}: the 176-line pin was moved (R:BUDGET_BUMP)"
    derived = (REPO / "tests" / "skill" / "test_skill_profile_truth.py").read_text(encoding="utf-8")
    assert "n <= (\\d+)" in derived, \
        "test_skill_profile_truth.py: no longer derives the line pin from test_surface.py (R:BUDGET_BUMP)"


def test_three_skill_trees_identical():
    """covers: M8, E6, R:TWO_TREE."""
    for tree in TREES:
        assert tree.is_dir(), f"skill tree missing (not a skip): {tree}"
    src_files = sorted(p.relative_to(SKILL) for p in SKILL.rglob("*.md"))
    for tree in TREES[1:]:
        for rel in src_files:
            twin = tree / rel
            assert twin.exists(), f"{tree}/{rel}: missing in this mirror"
            assert twin.read_bytes() == (SKILL / rel).read_bytes(), f"{tree}/{rel}: differs from the source tree"


def test_repo_claude_md_states_sizing_and_no_retired_verb():
    """covers: M6, M7, A2, A8, A12, E5."""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    block = text[text.find("ADD:BEGIN"):text.find("ADD:END")]
    assert "python3 .add/tooling/cli.py status" in block, "CLAUDE.md block: does not name `cli.py status`"
    assert "add.py status" not in block, "CLAUDE.md block: still names `add.py status` (add.py prints nothing)"
    assert "add.py guide" not in block, "CLAUDE.md block: still names the retired `add.py guide`"
    assert "Generated by" not in block, "CLAUDE.md block: stale 'Generated by sync-guidelines' trailer"
    assert re.search(r"3 (adjacent )?files", block), "CLAUDE.md block: sizing rule (≈3 adjacent files) absent"
    assert re.search(r"security.{0,5}data.{0,5}architecture", block, re.I), "CLAUDE.md block: floor absent from the sizing text"
    sizing = re.search(r"3 (adjacent )?files", block).start()
    loop = block.find("specification bundle")
    assert loop == -1 or sizing < loop, "CLAUDE.md block: sizing must precede the loop paragraph"


def test_guard_messages_name_their_target():
    """covers: A13 — every assert in the two guards carries a message naming its file/element."""
    for guard in (Path(__file__), REPO / "tests" / "test_agent_pointer_sizing.py"):
        src = guard.read_text(encoding="utf-8")
        bare = [ln for ln in src.splitlines() if ln.strip().startswith("assert ") and ", " not in ln and "\\" not in ln]
        assert not bare, f"{guard.name}: bare asserts with no message: {bare[:3]}"


# --- the ladder: kind x size -> route · effort+review · what persists -----------------
# A size threshold alone tells an agent WHEN to skip the node and nothing about what it still
# owes. These two guards pin the other half: every rung names its review and its residue, and
# no rung buys cheaper review with its cheaper ceremony.

KINDS = ("mechanical", "behavior", "question", "theme")


def _ladder(text, where):
    """The routing table: header naming route+persists, then its rows. Returns list[list[cell]]."""
    rows = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("|")]
    del rows[len(rows):]
    assert rows, f"{where}: no routing ladder table (a `|`-delimited table) found"
    head = rows[0].lower()
    assert "route" in head and "persist" in head, \
        f"{where}: ladder header names no `route` / `persists` column: {rows[0]!r}"
    assert "review" in head or "effort" in head, \
        f"{where}: ladder header names no effort/review column: {rows[0]!r}"
    body = [r for r in rows[1:] if not set(r) <= set("|-: ")]
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in body]
    assert len(cells) == 4, f"{where}: ladder has {len(cells)} rungs, expected exactly 4 (direct · task · explore · milestone)"
    cols = [c.strip().lower() for c in rows[0].strip("|").split("|")]
    order = ("change", "route", "review", "persist")
    for i, want in enumerate(order):
        assert want in cols[i], f"{where}: ladder column {i} is {cols[i]!r}, expected the `{want}` column"
    return cells


def test_ladder_rows_carry_route_effort_and_persistence():
    """covers: M9, S8."""
    for where, text in (("intake.md", _intake()),
                        ("CLAUDE.md block", CLAUDE_MD.read_text(encoding="utf-8"))):
        cells = _ladder(text, where)
        for row in cells:
            assert len(row) >= 4, f"{where}: ladder rung has {len(row)} columns, expected 4: {row}"
            for i, col in enumerate(("change", "route", "effort/review", "persists")):
                assert row[i], f"{where}: ladder rung {row[0]!r} has an empty `{col}` cell"
        flat = " ".join(c for row in cells for c in row).lower()
        for kind in KINDS:
            assert kind in flat, f"{where}: ladder never names the `{kind}` kind"
        assert "milestone" in flat, f"{where}: ladder has no Milestone rung"
        assert "--depth" in flat or "depth" in flat, f"{where}: ladder never maps a rung onto `--depth`"
        for row in cells:                                   # A27 — a table read at a glance
            for cell in row:
                assert len(cell.split()) <= 18, f"{where}: ladder cell is prose, not a phrase: {cell!r}"
        floor = re.search(r"security.{0,5}data.{0,5}architecture", text, re.I)
        table = text.find(rows_head := "| the change")
        assert floor and floor.start() < table, \
            f"{where}: the closed floor must be stated BEFORE the ladder, not inside or after it"
        assert re.search(r"sizes? UP to the next", text), \
            f"{where}: missing the size-up rule for a change that fits no rung"


def test_review_never_scales_down_with_ceremony():
    """covers: M10, R:CEREMONY_AS_EFFORT."""
    for where, text in (("intake.md", _intake()),
                        ("CLAUDE.md block", CLAUDE_MD.read_text(encoding="utf-8"))):
        cells = _ladder(text, where)
        direct = cells[0]
        joined = " ".join(direct).lower()
        assert re.search(r"red.{0,5}green", joined), \
            f"{where}: the direct rung does not name red→green — cheap ceremony must not buy cheap review"
        assert "invariant" in joined, f"{where}: the direct rung does not name `invariants:`"
        assert re.search(r"skipp?ed ceremony is (never|not) skipp?ed review", text, re.I), \
            f"{where}: missing the sentence 'ceremony you skipped is never review you skipped'"
        for row in cells:
            assert re.search(r"[a-z]", row[2], re.I), f"{where}: rung {row[0]!r} owes no stated review"


def test_guards_are_plain_and_unskippable():
    """covers: A4, A18, A19, A21 — the guards run anywhere, every run, and fail legibly."""
    for guard in (Path(__file__), REPO / "tests" / "test_agent_pointer_sizing.py"):
        src = guard.read_text(encoding="utf-8")
        assert guard.exists(), f"{guard}: guard missing"
        # assembled, never spelled — a literal here would make this guard trip on itself
        for marker in (".mark." + "skip", "pytest." + "skip(", "skip" + "if"):
            assert marker not in src, f"{guard.name}: carries `{marker}` — drift would land between releases"
        for line in src.splitlines():
            if line.startswith(("import ", "from ")):
                mod = line.split()[1].split(".")[0]
                assert mod in {"re", "sys", "pathlib", "add_method"}, \
                    f"{guard.name}: imports `{mod}` from outside the repo — the guard must run on any machine"


UNTOUCHED = {
    "intake.md": ("### Task — one atomic node", "### Explore — the answer IS the deliverable",
                  "## The closed floor — what always sizes up",
                  "## Change-request — touching already-frozen scope"),
    "SKILL.md": ("## The 3-beat loop (this file IS the loop; refs load on demand)",
                 "## Always start here (orient — do not skip)"),
}


def test_untouched_surfaces_kept_their_wording():
    """covers: A14, A17 — only the sizing sentences moved; every other heading stands unchanged."""
    for name, phrases in UNTOUCHED.items():
        src = (SKILL / name).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase in src, f"{name}: `{phrase}` changed or vanished — the edit reached outside its sentences"
    block = CLAUDE_MD.read_text(encoding="utf-8")
    block = block[block.find("ADD:BEGIN"):block.find("ADD:END")]
    status = block.find("cli.py status")
    table = block.find("| the change")
    loop = block.find("specification bundle")
    assert -1 not in (status, table, loop) and status < table < loop, \
        "CLAUDE.md block: order must be orient (`cli.py status`) → the ladder → the loop paragraph"
