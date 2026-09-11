"""Red suite for `/tasks/t2-refute-default.md` — at floor ≥ plan the verify beat SPAWNS a fresh
refuter; T2 is the default the prose states, T1 a prelude.

dogfood-and-measure F2: with the tier ladder stated as a list of options, both refutes on the
milestone that shipped it were the builder's own read. The engine now records `--tier`; this
suite pins that every guide, agent and book page an agent reads at Verify tells it to spawn.
"""
import re
import subprocess
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parents[2]
REPO = ADD_METHOD.parent

VERIFY = [ADD_METHOD / "skill/add/phases/verify.md",
          REPO / ".claude/skills/add/phases/verify.md",
          ADD_METHOD / "src/add_method/_bundled/skill/add/phases/verify.md"]
SKILL = [ADD_METHOD / "skill/add/SKILL.md",
         REPO / ".claude/skills/add/SKILL.md",
         ADD_METHOD / "src/add_method/_bundled/skill/add/SKILL.md"]
WORKER = [ADD_METHOD / "agents/add-worker.md",
          REPO / ".claude/agents/add-worker.md",
          ADD_METHOD / "src/add_method/_bundled/agents/add-worker.md"]
ADVISOR = [ADD_METHOD / "agents/add-advisor.md",
           REPO / ".claude/agents/add-advisor.md",
           ADD_METHOD / "src/add_method/_bundled/agents/add-advisor.md"]
DOC05 = ADD_METHOD / "docs/05-verify.md"


def _same(paths):
    texts = [p.read_text(encoding="utf-8") for p in paths]
    assert texts[0] == texts[1] == texts[2], f"{paths[0].name}: the three trees differ"
    return texts[0]


def _tier_paragraph(text: str) -> str:
    m = re.search(r"\*\*Who refutes[^\n]*\n(?:[^\n]+\n)*", text)
    assert m, "verify.md: no `Who refutes` paragraph"
    return m.group(0)


# --- M1 / R:T1RUNG / E1 / A2 ------------------------------------------------------------------

def test_verify_guide_makes_t2_the_default():
    """covers: M1, R:T1RUNG, E1, A2 — spawn · brief before the diff · `--tier T2` · default at floor ≥ plan; T1 a prelude."""
    para = _tier_paragraph(_same(VERIFY))
    assert re.search(r"\bT2\b[^\n]*default|default[^\n]*\bT2\b", para, re.I | re.S), para
    assert re.search(r"spawn", para, re.I), "T2 is not stated as a spawn"
    assert "--tier T2" in para, "the recorded line does not carry --tier T2"
    assert re.search(r"before (it reads |reading )?the diff", para), "the brief-before-diff order is missing"
    assert "floor ≥ plan" in para
    t1 = re.search(r"T1[^·]*", para)
    assert t1 and re.search(r"prelude|optional", t1.group(0)), "T1 is not a prelude"
    assert "floor ≥ plan" not in t1.group(0), "T1 is stated at floor ≥ plan"


# --- M2 -----------------------------------------------------------------------------------------

def test_skill_loop_names_the_t2_spawn():
    """covers: M2 — the VERIFY step names add-advisor · refute · T2 before `add gate`, three trees."""
    t = _same(SKILL)
    step = re.search(r"3\. \*\*VERIFY\*\*(.*?)\n\n", t, re.S)
    assert step, "SKILL.md: no VERIFY step"
    s = step.group(1)
    assert "add-advisor" in s and "refute" in s and "T2" in s, s
    assert s.index("T2") < s.index("add gate"), "the spawn is named after the gate"


# --- M3 / E1 --------------------------------------------------------------------------------------

def test_worker_verify_spawns_and_records_t2():
    """covers: M3, E1 — the verify bullet: spawn add-advisor refute at floor ≥ plan, record `--tier T2`, own read is T1."""
    t = _same(WORKER)
    m = re.search(r"- \*\*verify\*\* — before recording a verdict[^\n]*(?:\n  [^\n]*)*", t)
    assert m, "add-worker.md: no verify bullet in §4"
    b = m.group(0)
    assert "spawn" in b.lower() and "refute" in b and "--tier T2" in b, b
    assert "floor ≥ plan" in b, b
    assert re.search(r"\bT1\b", b), "the builder's own read is not named T1"


# --- M4 -----------------------------------------------------------------------------------------

def test_advisor_return_line_carries_tier():
    """covers: M4 — the refute mode's recorded line carries --tier T2 in all three trees."""
    t = _same(ADVISOR)
    m = re.search(r"- \*\*refute\*\*(?:[^\n]*\n)+?[^\n]*never a verdict", t)
    assert m, "add-advisor.md: no refute mode block"
    assert "--tier T2" in m.group(0), m.group(0)


# --- M5 -----------------------------------------------------------------------------------------

def test_book_tier_table_says_default_and_prelude():
    """covers: M5 — docs 05: the T2 row says default and spawn, the T1 row says prelude."""
    rows = {l.split("|")[1].strip(): l for l in DOC05.read_text(encoding="utf-8").splitlines()
            if l.startswith("| T")}
    assert "T2" in rows and "T1" in rows, rows.keys()
    assert re.search(r"default", rows["T2"], re.I) and re.search(r"spawn", rows["T2"], re.I), rows["T2"]
    assert re.search(r"prelude", rows["T1"], re.I), rows["T1"]


# --- R:LADDERMOVED / R:BUDGET --------------------------------------------------------------------

def _at_head(rel: str) -> str:
    """TRIPWIRE — compares the working tree to `HEAD`, which `git commit` makes identical: it
    fires during this task's edit and is inert once committed, so a green CI is not the claim
    holding. What must hold permanently is pinned by content, never through this helper."""
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(REPO), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_ladder_ends_unmoved_and_budgets_hold():
    """covers: R:LADDERMOVED, R:BUDGET — T0/T4 verbatim; no budget literal moved; surface lines ≤ HEAD.

    TRIPWIRE: the two HEAD comparisons fire while this task's edit is uncommitted and are inert
    once `git commit` makes HEAD and the working tree identical — a green CI is not this claim
    holding. The T0/T4 fragments are pinned by content and hold permanently; the budget literals
    are pinned by their own owner (`test_surface.py`) after the commit."""
    para = _tier_paragraph(VERIFY[0].read_text(encoding="utf-8"))
    for frag in ("T0 nobody (quick depth · process floor: receipt + residue)",
                 "T4 a protected holdout the builder cannot read — a CI recipe, not shipped: a prompt is not isolation"):
        assert frag in para, f"ladder end moved: {frag!r}"
    rel = "add-method/tests/skill/skill_budget.py"
    lit = re.compile(r"^(LINE_BUDGET|BYTE_BUDGET|SURFACE_BUDGET) = (\d+)", re.M)
    assert dict(lit.findall(_at_head(rel))) == dict(lit.findall((REPO / rel).read_text(encoding="utf-8")))
    tree = ADD_METHOD / "skill/add"
    now = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in tree.rglob("*.md")
              if "persona-author" not in p.parts)
    ls = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "add-method/skill/add"],
                        cwd=str(REPO), capture_output=True, text=True).stdout.split()
    head = sum(len(_at_head(f).splitlines()) for f in ls if f.endswith(".md") and "persona-author" not in f)
    assert now <= head, f"the skill surface grew ({head} -> {now}); fund the addition by compressing"
