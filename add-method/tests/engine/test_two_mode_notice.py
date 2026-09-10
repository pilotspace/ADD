"""Red suite for `/tasks/two-mode-notice.md` — the freeze names the plan-floor Musts still on one
evidence mode. A notice, never a refusal.

dogfood-and-measure F1: the session that wrote "at a plan floor a Must carries two checks of
different mode" froze 0 of 10 such Musts one task later. Prose nobody follows binds nothing; a
refusal would grow ceremony back on the mechanical lane. So: one line on the freeze note and one
count in `todo`, armed exactly where the refute rung arms, judging nothing.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

HEAD = """## CARD
goal: a task with modes to count
beat: direction · next: add freeze

## RULES
<must>
- M1 the first rule
- M2 the second rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who; taking anyone -> cost
- A2 [which] covers: S1 · n/a · fixture
- A3 [when] covers: S1 · n/a · fixture
- A4 [absent] covers: S1 · n/a · fixture
- A5 [order] covers: S1 · n/a · fixture
- A6 [experience] covers: S1 · n/a · fixture

## PLAN
contract: S1
budget: ~5 tool calls

## CHECKS
"""
TAIL = """red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
"""

# E2's shape: M1 two modes, M2 one mode (twice), the Reject one mode
CHECKS_E2 = """- test_a · covers: M1 · acceptance · through the port
- test_b · covers: M1 · contract · the consumer's pact
- test_c · covers: M2 · acceptance · first example
- test_d · covers: M2 · acceptance · second example
- test_e · covers: R:BAD · acceptance · the reject
"""
# E1's shape: M1 one acceptance + one mode-less; M2 two modes
CHECKS_E1 = """- test_a · covers: M1 · acceptance · through the port
- test_b · covers: M1 · what it proves, no mode word
- test_c · covers: M2 · property · an invariant
- test_d · covers: M2 · acceptance · an example
- test_e · covers: R:BAD · acceptance · the reject
"""
CHECKS_ALL_TWO = """- test_a · covers: M1 · acceptance · through the port
- test_b · covers: M1 · static · an import rule
- test_c · covers: M2 · property · an invariant
- test_d · covers: M2 · acceptance · an example
- test_e · covers: R:BAD · acceptance · the reject
"""


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _bundle(tmp_path, checks, slug="modes", *, depth="standard", sensitivity="data", kind=None):
    if not (tmp_path / ".git").exists():
        git("init", "-q", cwd=tmp_path)
        git("config", "user.email", "t@example.com", cwd=tmp_path)
        git("config", "user.name", "T", cwd=tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")
        add.init(tmp_path / ".add", "code", "Modes")
    root = tmp_path / ".add"
    cid, _ = add.new(root, "Task", slug, title=f"{slug} task", depth=depth, sensitivity=sensitivity,
                     scope=["src/service.py"], kind=kind)
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = n["raw"].replace("  - S1 <the surface this publishes — an endpoint, function, or section>", "  - S1 book()")
    body = HEAD + checks + TAIL
    if kind == "explore":
        body = body.replace("## CHECKS", "## FINDINGS\n- F1 (answers M1) · holds · (evidence: src/service.py:1)\n\n## CHECKS")
    add.write(path, f"---\n{raw}\n---\n{body}")
    return cid


def _node(tmp_path, cid):
    return add.scan(tmp_path / ".add")[cid]


# --- M1 / A2: the mode word --------------------------------------------------------------------

def test_check_modes_reads_the_closed_set(tmp_path):
    """covers: M1, A2 — seven words parse, case folds, `acceptance-ish` and a two-segment line are None."""
    checks = "".join(f"- t_{w} · covers: M1 · {w} · proves it\n"
                     for w in ("acceptance", "property", "contract", "static", "unit", "e2e", "manual"))
    checks += ("- t_case · covers: M1 · Acceptance · case folds\n"
               "- t_tick · covers: M1 · `property` · direction.md's own typography\n"
               "- t_paren · covers: M1 · (contract) · parenthesised\n"
               "- t_ish · covers: M1 · acceptance-ish · not a mode\n"
               "- t_none · covers: M1 · what it proves with no mode word\n"
               "- t_two · covers: M1\n")
    cid = _bundle(tmp_path, checks)
    modes = add.check_modes(_node(tmp_path, cid))
    for w in ("acceptance", "property", "contract", "static", "unit", "e2e", "manual"):
        assert modes[f"t_{w}"] == w, modes
    assert modes["t_case"] == "acceptance", modes
    assert modes["t_tick"] == "property" and modes["t_paren"] == "contract", modes
    assert modes["t_ish"] is None and modes["t_none"] is None, modes
    assert "t_two" not in modes or modes["t_two"] is None


# --- M2 / R:NOTAMUST / E1 / E2 -------------------------------------------------------------------

def test_single_mode_musts_lists_one_known_mode_only(tmp_path):
    """covers: M2, R:NOTAMUST, E1, E2 — one known mode → listed; two → not; none known → not; never a Reject."""
    cid = _bundle(tmp_path, CHECKS_E2)
    assert add.single_mode_musts(_node(tmp_path, cid)) == [("M2", "acceptance")]
    cid = _bundle(tmp_path, CHECKS_E1, slug="edge1")
    assert add.single_mode_musts(_node(tmp_path, cid)) == [("M1", "acceptance")]
    cid = _bundle(tmp_path, "- test_a · covers: M1 · no mode here\n- test_b · covers: M2 · nor here\n- test_c · covers: R:BAD · manual · x\n",
                  slug="nomode")
    assert add.single_mode_musts(_node(tmp_path, cid)) == []


# --- M3 / R:REFUSED / R:NOISE -------------------------------------------------------------------

def test_freeze_notice_at_plan_floor_still_stamps(tmp_path):
    """covers: M3, R:REFUSED, E2 — the note names M2 (acceptance), not M1; the stamp is written."""
    cid = _bundle(tmp_path, CHECKS_E2)
    ok, note = add.freeze(tmp_path / ".add", cid, "plan:test")
    assert ok, note
    assert re.search(r"^notice: M2 \(acceptance\) carries one evidence mode", note, re.M), note
    assert "M1" not in note.split("notice:", 1)[1].split("\n", 1)[0], note
    assert "direction.md" in note and "next: add brief modes" in note, note
    stamps = (add.read(tmp_path / ".add/tasks/modes.md", "T0")["fm"] or {}).get("verified") or []
    assert any(s.get("act") == "freeze" for s in stamps if isinstance(s, dict))
    # every Must single-mode → still a freeze, never a refusal
    cid = _bundle(tmp_path, "- test_a · covers: M1 · acceptance · x\n- test_b · covers: M2 · unit · y\n- test_c · covers: R:BAD · acceptance · z\n",
                  slug="allone")
    ok, note = add.freeze(tmp_path / ".add", cid, "plan:test")
    assert ok, note
    assert "notice: M1 (acceptance), M2 (unit) carry one evidence mode" in note, note


def test_freeze_silent_when_unarmed_or_two_modes(tmp_path):
    """covers: M3, R:NOISE — quick · process floor · explore print nothing; two modes everywhere prints nothing."""
    for slug, kw in (("q", dict(depth="quick")), ("p", dict(sensitivity=None)), ("x", dict(kind="explore"))):
        cid = _bundle(tmp_path, CHECKS_E2, slug=slug, **kw)
        ok, note = add.freeze(tmp_path / ".add", cid, "plan:test")
        assert ok, (slug, note)
        assert "notice:" not in note, (slug, note)
    cid = _bundle(tmp_path, CHECKS_ALL_TWO, slug="two")
    ok, note = add.freeze(tmp_path / ".add", cid, "plan:test")
    assert ok, note
    assert "notice:" not in note, note


# --- M4 -----------------------------------------------------------------------------------------

def test_todo_hint_counts_single_mode_musts(tmp_path):
    """covers: M4, R:NOISE — `1 single-mode Must` on a plan-floor direction task; nothing on a quick one."""
    _bundle(tmp_path, CHECKS_E2, slug="plan")
    _bundle(tmp_path, CHECKS_E2, slug="quick", depth="quick")
    items, note = add.todo(tmp_path / ".add")
    plan_line = next(l for l in note.splitlines() if "plan " in l and "→" in l)
    quick_line = next(l for l in note.splitlines() if "quick " in l and "→" in l)
    assert "1 single-mode Must" in plan_line, plan_line
    assert "single-mode" not in quick_line, quick_line


# --- M3 at the front door -------------------------------------------------------------------------

def test_freeze_notice_reaches_the_cli(tmp_path):
    """covers: M3 — `cli.py freeze` prints the notice line and exits 0."""
    _bundle(tmp_path, CHECKS_E2)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    r = subprocess.run([sys.executable, str(tmp_path / ".add/tooling/cli.py"), "freeze", "modes",
                        "--by", "plan:test", "--authority", "plan"],
                       cwd=str(tmp_path), capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "notice: M2 (acceptance) carries one evidence mode" in r.stdout, r.stdout


# --- M5 -----------------------------------------------------------------------------------------

def test_prose_states_the_notice():
    """covers: M5 — FORMAT §6.2 · docs 03 · direction.md ×3, byte-identical."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    assert "### §6.2" in fmt, "FORMAT has no §6.2"
    sec = fmt.split("### §6.2", 1)[1].split("\n## ", 1)[0]
    assert "notice" in sec and re.search(r"never refuses|not a refusal", sec), sec
    assert "single" in sec and "mode" in sec
    # the documented example must be a shape the engine emits — the second T2 refute found §6.2
    # carrying the pre-refreeze rendering, and a keyword grep could not see it
    example = re.search(r"^notice: .*$", sec, re.M)
    assert example, "§6.2 shows no notice example"
    assert re.fullmatch(r"notice: (M\d+ \(\w+\), )*M\d+ \(\w+\) carr(y|ies) one evidence mode — a plan-floor Must carries two \(direction\.md § router\)",
                        example.group(0)), example.group(0)
    d03 = (REPO / "docs" / "03-direction.md").read_text(encoding="utf-8")
    assert re.search(r"freeze[^\n]*notice[^\n]*one (evidence )?mode|one (evidence )?mode[^\n]*notice", d03, re.I), \
        "docs 03 does not say the freeze names single-mode Musts"
    trees = [REPO / "skill/add/phases/direction.md",
             ROOT / ".claude/skills/add/phases/direction.md",
             REPO / "src/add_method/_bundled/skill/add/phases/direction.md"]
    texts = [p.read_bytes() for p in trees]
    assert texts[0] == texts[1] == texts[2], "direction.md twins differ"
    t = texts[0].decode("utf-8")
    assert re.search(r"freeze[^\n]*(names|notice)[^\n]*one mode", t, re.I), "direction.md does not name the notice"


# --- E3: the probe that graduated ---------------------------------------------------------------

def test_duplicate_check_id_keeps_each_lines_mode(tmp_path):
    """covers: M2, E3 — two lines sharing one id: the first line's mode still counts for its Must."""
    checks = ("- test_a · covers: M1 · acceptance · the M1 example\n"
              "- test_b · covers: M1 · contract · the consumer pact for M1\n"
              "- test_b · covers: M2 · acceptance · the same test also shows M2\n"
              "- test_c · covers: M2 · property · an invariant\n"
              "- test_d · covers: R:BAD · acceptance · the reject\n")
    cid = _bundle(tmp_path, checks, slug="dup")
    assert add.single_mode_musts(_node(tmp_path, cid)) == [], "M1 meets the rule (acceptance + contract)"
    ok, note = add.freeze(tmp_path / ".add", cid, "plan:test")
    assert ok and "notice:" not in note, note


# --- E4: the third refute's probe, graduated ----------------------------------------------------

def test_duplicate_must_id_is_named_once(tmp_path):
    """covers: M2, M4, E4 — `M1` declared on two RULES lines: named once in the notice, counted once in todo."""
    checks = ("- test_a · covers: M1 · acceptance · the M1 example\n"
              "- test_c · covers: M2 · unit · the M2 unit\n"
              "- test_e · covers: R:BAD · acceptance · the reject\n")
    cid = _bundle(tmp_path, checks, slug="twice")
    path = tmp_path / ".add" / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n" + n["body"].replace("- M1 the first rule\n", "- M1 the first rule\n- M1 the first rule again (copy-paste)\n"))
    assert add.single_mode_musts(_node(tmp_path, cid)) == [("M1", "acceptance"), ("M2", "unit")]
    _, note = add.todo(tmp_path / ".add")
    assert "2 single-mode Musts" in note, note
    ok, note = add.freeze(tmp_path / ".add", cid, "plan:test")
    assert ok and "notice: M1 (acceptance), M2 (unit) carry one evidence mode" in note, note
