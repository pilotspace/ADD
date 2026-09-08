"""Red suite for `one-refusal-shape` — `freeze` answers every refusal the same way.

`freeze` has eleven returns. Ten refusals hand back `None`; one — the milestone-scaffold rung —
hands back `False`. Nothing in the message says so, and a reader who has checked either rung
writes the assertion that the other rung silently defeats. That happened twice in one branch,
in two different test files, hours apart.

The fix is one line. The guard is the point: a BEHAVIOURAL enumeration that drives each rung for
real, plus a STATIC pass over `freeze`'s own AST so a rung written tomorrow cannot reintroduce a
second shape. `[]` returns elsewhere in the engine are empty RESULTS, not refusals, and stay.
"""

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def _bundle(tmp_path, name="Shape"):
    add.init(tmp_path, "code", name)
    return tmp_path


# Each entry builds a bundle into the state that reaches exactly one refusal rung and returns the
# cid to freeze. The enumeration IS the coverage: a rung nobody can drive is a defect in this
# list, never a passing case (A4). Rungs are driven in isolation, so evaluation order cannot let
# an earlier one shadow the one under test (A5).

def _rung_no_such_node(root):
    return "/tasks/nothing.md"


def _rung_milestone_scaffold(root):
    cid, _ = add.new(root, "Milestone", "m-scaffold", title="A scaffold milestone")
    return cid


def _rung_task_scaffold(root):
    cid, _ = add.new(root, "Task", "t-scaffold", title="A scaffold task")
    return cid


# M3: the fix moves the falsy first element and NOTHING else — each rung keeps the words it said
# before, so a reader who greps for a refusal still finds it.
MESSAGES = {
    "no such node": "no such node",
    "milestone still a scaffold": "this milestone is still a scaffold",
    "task still carries placeholders": "still carries template placeholders",
}

RUNGS = {
    "no such node": _rung_no_such_node,
    "milestone still a scaffold": _rung_milestone_scaffold,
    "task still carries placeholders": _rung_task_scaffold,
}


def test_every_freeze_refusal_is_none(tmp_path):
    """covers: M1, M2, M3, A4, A5, E1, E2 — one falsy shape across every driven rung.

    NOT parametrized on purpose: JUnit reports a parametrized case as `name[param]` and the gate
    resolves a `covers:` referent by BARE name, so a parametrized check binds nothing at all.
    """
    wrong = []
    for rung in sorted(RUNGS):
        root = _bundle(tmp_path / rung.replace(" ", "-"))
        cid = RUNGS[rung](root)
        node, note = add.freeze(root, cid, "human:t")
        assert note, f"the `{rung}` rung refused without a message"
        assert MESSAGES[rung] in note, (
            f"M3 — only the falsy first element moves; the `{rung}` rung's message changed:\n{note}")
        if node is not None:
            wrong.append(f"  `{rung}` refused with {node!r} — {note.splitlines()[0]}")
    assert not wrong, (
        "R:TWOSHAPES — a caller writing `if node is None` does not see these refusals:\n"
        + "\n".join(wrong))


def test_no_freeze_return_is_a_second_falsy_shape():
    """covers: M1, R:TWOSHAPES, A6 — the static half; a new rung cannot reintroduce the shape."""
    # Parse the MODULE, then pick out `freeze` — dedenting a lifted source loses the true line
    # numbers, and the line number is the whole point of the message (A6).
    engine = REPO / "tooling" / "add.py"
    tree = ast.parse(engine.read_text())
    fn = next((n for n in tree.body
               if isinstance(n, ast.FunctionDef) and n.name == "freeze"), None)
    assert fn is not None, f"no top-level `freeze` in {engine} — the guard is aimed at nothing"
    offenders = []
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Return) and isinstance(n.value, ast.Tuple)):
            continue
        first = n.value.elts[0]
        falsy = ((isinstance(first, ast.Constant) and first.value in (False, 0, "", None))
                 or (isinstance(first, (ast.List, ast.Dict, ast.Tuple)) and not getattr(first, "elts", True)))
        if falsy and not (isinstance(first, ast.Constant) and first.value is None):
            offenders.append((n.lineno, ast.unparse(first)))
    assert not offenders, (
        "R:TWOSHAPES — `freeze` refuses with more than one falsy shape. Every refusal must return "
        "`None` so one caller test sees them all. Offending returns (line within `freeze`, value):\n"
        + "\n".join(f"  {engine.name}:{ln} — return {val}, ..." for ln, val in offenders))


def test_a_successful_freeze_is_still_truthy(tmp_path):
    """covers: E3 — the fix must not make a PASS look like a refusal."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "t-real", title="A real task", depth="quick",
                     scope=["src/x.py"])
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'gives', ['S1 a function other code calls'])}\n---\n"
                    + _AUTHORED)
    node, note = add.freeze(root, cid, "human:t")
    assert node is not None, f"the fixture could not reach a successful freeze: {note}"
    assert node, "a successful freeze returned a falsy node — indistinguishable from a refusal"


def test_an_empty_result_is_not_a_refusal(tmp_path):
    """covers: R:NOTAREFUSAL, E4 — a query that ran and matched nothing still answers `[]`."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "t-empty", title="A task")

    hits, _ = add.search(root, "a-term-no-node-contains-anywhere")
    assert hits == [], f"`search` rewrote an empty result as {hits!r}"

    rows, _ = add.neighborhood(add.scan(root), cid, 1)
    assert rows == [], f"`neighborhood` rewrote a no-edge result as {rows!r}"

    asked, _ = add.interview(root, cid)
    assert isinstance(asked, list), f"`interview` rewrote its result as {asked!r}"


_AUTHORED = """## CARD
goal: a real goal
beat: direction

## RULES
<must>
- M1 the thing holds
</must>
<reject>
- R:BAD the bad thing never happens -> "BAD"
</reject>

## ASSUMPTIONS
- A1 [who] n/a · the surface has one caller and it is this repo
- A2 [which] n/a · one case, no selection
- A3 [when] n/a · no boundary
- A4 [absent] n/a · no optional value
- A5 [order] n/a · one item, no tie
- A6 [experience] n/a · no human reads the output

## PLAN
contract: S1 a function other code calls

## CHECKS
- test_one · covers: M1 · proves the must
- test_two · covers: R:BAD · proves the reject
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
"""
