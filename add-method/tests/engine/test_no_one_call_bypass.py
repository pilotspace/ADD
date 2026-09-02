"""No ONE engine call may span the human seam — created here, closed here, nobody asked.

`add.quick()` did exactly that: `new` → `freeze(by=by)` (no authority, so `process`) → `run` →
`gate PASS`, in one call, and wrote a body with no `## RULES` at all so there was nothing left
to bind. It was wired to no CLI verb and named in no shipped doc, yet four assertions in
`test_gate_verb.py` kept it green and its docstring advertised it as a supported lane. A tested
bypass is one refactor away from being reachable.

This guard is a CENSUS, not a name check. Deleting `quick` and pinning `not hasattr(add, "quick")`
would prove only that one function is gone; the rule is about the SHAPE, so the check enumerates
every public function in the engine and asks whether any single one of them opens a node and
closes it. Re-add the lane under any name and this goes red.
"""
import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

ENGINE = REPO / "tooling" / "add.py"

OPENS = {"new"}
CLOSES = {"done", "gate"}


def _calls_in(fn: ast.FunctionDef) -> set:
    """Bare names called directly in this function's body — `new(...)`, not `x.new(...)`."""
    return {n.func.id for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def _public_functions():
    tree = ast.parse(ENGINE.read_text(encoding="utf-8"))
    return [n for n in tree.body
            if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]


def test_no_public_function_both_opens_and_closes_a_node():
    """covers: M1 — the ONE human approval sits between `new` and `done`; nothing may straddle it."""
    straddling = []
    for fn in _public_functions():
        called = _calls_in(fn)
        if called & OPENS and called & CLOSES:
            straddling.append(f"{fn.name} (line {fn.lineno}) calls "
                              f"{sorted(called & OPENS)} and {sorted(called & CLOSES)}")
    assert not straddling, (
        "an engine call walks a node from creation to closed in one step, so the ONE human "
        "approval ADD asks for can be skipped entirely:\n  " + "\n  ".join(straddling))


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN, tracked by /tasks/wire-or-delete-checks-sync.md: `checks_sync` compiles a node's "
    "CHECKS from the suite, carries 9 tests and its own R:SILENTFIX refusal — whose `next:` line "
    "promises `add checks <slug> --verify`, a verb that does not exist. It is wired to nothing. "
    "Deleting a working feature is the wrong repair, and wiring a 25th verb is outside this "
    "milestone's frozen scope, so the gap is recorded here rather than accommodated by weakening "
    "the census. strict=True: when the task lands, this xfail must be REMOVED, not left passing.")) 
def test_every_public_function_is_reachable_or_a_library_read():
    """covers: M2 — an unwired, tested writer is a bypass nobody is watching.

    A writer the CLI cannot reach is not covered by any refusal the CLI enforces. Two exemptions,
    both real: reads are out of scope (`add.py` is a library, its readers serve tests and `cli.py`
    alike), and so is a writer another engine function calls — `render_card` and `checks_sync` are
    internal steps of verbs that ARE reachable, not lanes of their own. What is left is a writer
    nothing calls and no operator can run: reachable only from a test.
    """
    cli = (REPO / "tooling" / "cli.py").read_text(encoding="utf-8")
    functions = _public_functions()
    called_by_engine = set()
    for fn in functions:
        called_by_engine |= _calls_in(fn) - {fn.name}
    writers = []
    for fn in functions:
        called = _calls_in(fn)
        if not (called & (OPENS | CLOSES | {"freeze", "write", "put", "_transition"})):
            continue                      # a read, or a pure computation
        if f"add.{fn.name}(" in cli or f"add.{fn.name} " in cli:
            continue
        if fn.name in called_by_engine:
            continue                      # an internal step of a verb that IS reachable
        writers.append(f"{fn.name} (line {fn.lineno})")
    assert not writers, (
        "these engine functions WRITE to a node but no CLI verb reaches them — an operator "
        "cannot run them, so no refusal they skip is ever observed:\n  " + "\n  ".join(writers))


def test_the_deleted_lane_is_gone():
    """covers: M1 — the specific function measured, pinned so it cannot quietly return."""
    assert not hasattr(add, "quick"), (
        "add.quick() is back — it walked new -> freeze(process) -> run -> gate PASS in one call")
