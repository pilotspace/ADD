"""Red suite for `observes-slot` — a rule names the runtime signal that would show it broken.

loop.md says the CHECKS have a second life as monitors, and no slot held WHICH signal. `## PLAN`
now accepts `- O<n> covers: <M ids> · signal <text> · window <text> · threshold <text> · action
alert|rollback`; `observes(node)` reads them, `brief` renders an `<observes>` block, `doctor` names
a malformed line, and a human-floor `freeze` notices a node with none. No gate reads one: whether a
monitor fired is production's evidence, not the bundle's (R:OBSERVEASGATE).

Driven as `.add/tasks/observes-slot.md` under milestone `loop-that-closes`.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

from conftest import DRAFTED_ASSUMPTIONS, DRAFTED_CHECKS, DRAFTED_RULES, draft_direction  # noqa: E402

TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")

GOOD = "- O1 covers: M1 · signal 5xx rate on /list · window 5m · threshold > 1% · action alert"
BAD = "- O2 covers: M1 · signal x · action page"


def _plan(bundle, cid, *lines):
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    body = n["body"].replace("## PLAN", "## PLAN\nregression: none · fixture", 1)
    if lines:
        body = body.replace("regression: none · fixture",
                            "regression: none · fixture\n" + "\n".join(lines), 1)
    add.write(p, f"---\n{n['raw']}\n---\n{body}")
    return p


@pytest.fixture
def task(tmp_path):
    b = tmp_path / ".add"
    add.init(b, "code", "P")
    cid, _ = add.new(b, "Task", "t", title="t")
    draft_direction(b, cid, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    return b, cid


def test_observes_reads_the_grammar(task):
    """covers: M1, A2, A5, E1 — six fields, each free text, round-tripped as written: the engine
    names a slot, it never judges a metric."""
    bundle, cid = task
    _plan(bundle, cid, GOOD)
    obs = add.observes(add.read(bundle / cid.lstrip("/"), "T2"))
    assert len(obs) == 1, obs
    o = obs[0]
    assert o["id"] == "O1" and o["covers"] == ["M1"] and o["action"] == "alert", o
    assert o["signal"] == "5xx rate on /list" and o["window"] == "5m" and o["threshold"] == "> 1%", o


def test_malformed_lines_are_named_not_read(task):
    """covers: M1, E2 — a line missing a field, carrying a placeholder, or naming an action outside
    the two is NOT an observe: `doctor` names it `observe_malformed` (info) and `observes` skips it.
    A line nobody reads and nobody names is the slot silently not working."""
    bundle, cid = task
    _plan(bundle, cid, GOOD, BAD,
          "- O3 covers: M1 · signal <the metric> · window 5m · threshold > 1% · action alert",
          "- O4 covers: M1 · signal x · window 5m · threshold > 1% · action rollback",
          # well-formed in every field but the ACTION: the one axis an enum decides, swept on its
          # own so the enum is not proved by a line that was malformed for three other reasons
          "- O5 covers: M1 · signal x · window 5m · threshold > 1% · action page",
          "- O6 covers: M1 · signal x · window 5m · threshold > 1% · action Alert")
    obs = add.observes(add.read(bundle / cid.lstrip("/"), "T2"))
    assert [o["id"] for o in obs] == ["O1", "O4"], obs
    finds = [f for f in add.doctor(bundle) if f["code"] == "observe_malformed"]
    assert {f["severity"] for f in finds} == {"info"}, finds
    named = " ".join(f["detail"] for f in finds)
    for bad in ("O2", "O3", "O5", "O6"):
        assert bad in named, f"{bad} was neither read nor named: {named}"
    assert "O1:" not in named and " O4 " not in named, named


def test_brief_renders_the_block(task):
    """covers: M2, E1 — the block and one element per line; a node with none renders no block."""
    bundle, cid = task
    _plan(bundle, cid)
    assert "<observes>" not in add.brief(bundle, cid)["text"], "an empty slot rendered a block"
    _plan(bundle, cid, GOOD)
    xml = add.brief(bundle, cid)["text"]
    assert "<observes>" in xml and "</observes>" in xml, xml
    assert '<o id="O1" covers="M1" action="alert">5xx rate on /list · 5m · > 1%</o>' in xml, xml


def test_freeze_notices_only_at_human(task):
    """covers: M3, R:OBSERVEASREFUSAL, A3, E3 — the notice rides the ONE beat where a human reads
    the whole node, and a freeze is never refused for a missing monitor."""
    bundle, _ = task
    sec, _ = add.new(bundle, "Task", "s", title="s", sensitivity="security")
    draft_direction(bundle, sec, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    _plan(bundle, sec)
    node = add.read(bundle / sec.lstrip("/"), "T2")
    add.interview(bundle, sec, {d["id"]: "confirm" for d in add._open_decisions(node)}, by="human:x")
    ok, note = add.freeze(bundle, sec, "human:x", "human")
    assert ok, f"a freeze was refused for a missing observe: {note!r}"
    assert "no observes:" in note and "O<n>" in note, note

    _plan(bundle, sec, GOOD)
    node = add.read(bundle / sec.lstrip("/"), "T2")
    add.interview(bundle, sec, {d["id"]: "confirm" for d in add._open_decisions(node)}, by="human:x")
    ok, note = add.freeze(bundle, sec, "human:x", "human")
    assert ok and "no observes:" not in note, f"a node WITH an observe was noticed: {note!r}"

    dat, _ = add.new(bundle, "Task", "d", title="d", sensitivity="data")
    draft_direction(bundle, dat, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    _plan(bundle, dat)
    ok, note = add.freeze(bundle, dat, "plan:m", "plan")
    assert ok and "no observes:" not in note, f"a plan floor was noticed: {note!r}"


def test_no_gate_reads_an_observe(tmp_path):
    """covers: M4, R:OBSERVEASGATE, A8, E4 — two copies of one rung-bound node, one with observes
    and one without, briefed, run, refuted and gated: the verdicts AND the `next:` hints are
    identical. An observe that moves any outcome makes production's evidence the bundle's."""
    outs = []
    for lines in ((), (GOOD,)):
        b = tmp_path / ("with" if lines else "without") / ".add"
        add.init(b, "code", "P")
        cid, _ = add.new(b, "Task", "t", title="t", sensitivity="architecture")
        draft_direction(b, cid, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
        _plan(b, cid, *lines)
        seen = [add.freeze(b, cid, "plan:m", "plan")[1], add.brief(b, cid)["text"].count("<"),
                add._next_verb(add.scan(b), cid, add.scan(b)[cid]["fm"]) if hasattr(add, "_next_verb") else "",
                add.todo(b)[1] if hasattr(add, "todo") else "",
                str([f["code"] for f in add.doctor(b) if f["code"] != "observe_malformed"])]
        outs.append([str(x).replace(str(b), "") for x in seen])
    assert outs[0][0] == outs[1][0], f"the freeze note moved under an observe:\n{outs[0][0]}\n{outs[1][0]}"
    assert outs[0][2:] == outs[1][2:], f"a verdict-bearing reader moved: {outs[0][2:]} vs {outs[1][2:]}"


def test_scaffold_and_docs_carry_the_slot(tmp_path):
    """covers: M5, A11 — a slot with no prompt is a slot nobody fills: `new`'s PLAN carries the
    line, direction.md names it, and the three trees are identical and line-neutral."""
    b = tmp_path / ".add"
    add.init(b, "code", "P")
    cid, _ = add.new(b, "Task", "t", title="t")
    body = add.read(b / cid.lstrip("/"), "T2")["body"]
    assert "- O<n> covers:" in add._section(body, "plan"), add._section(body, "plan")
    d = (REPO / "skill" / "add" / "phases" / "direction.md").read_text(encoding="utf-8")
    assert "O<n>" in d and "observes" in d, "direction.md does not name the observes slot"
    for tree in TREES[1:]:
        assert (tree / "phases" / "direction.md").read_bytes() == \
            (REPO / "skill" / "add" / "phases" / "direction.md").read_bytes(), tree
    # TRIPWIRE: the working tree against `HEAD`, so `git commit` satisfies it — it fires while the
    # skill edit is uncommitted, which is exactly when the line-neutral rule is decided, and is
    # inert once committed; nobody may read a green CI as this claim holding permanently.
    head = subprocess.run(["git", "show", "HEAD:add-method/skill/add/phases/direction.md"],
                          cwd=REPO.parent, capture_output=True, text=True, check=True).stdout
    assert len(d.splitlines()) == len(head.splitlines()), "direction.md is not line-neutral vs HEAD"
