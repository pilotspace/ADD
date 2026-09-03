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
    writers, candidates = [], 0
    for fn in functions:
        called = _calls_in(fn)
        if not (called & (OPENS | CLOSES | {"freeze", "write", "put", "_transition"})):
            continue                      # a read, or a pure computation
        candidates += 1
        if f"add.{fn.name}(" in cli or f"add.{fn.name} " in cli:
            continue
        if fn.name in called_by_engine:
            continue                      # an internal step of a verb that IS reachable
        writers.append(f"{fn.name} (line {fn.lineno})")
    assert not writers, (
        "these engine functions WRITE to a node but no CLI verb reaches them — an operator "
        "cannot run them, so no refusal they skip is ever observed:\n  " + "\n  ".join(writers))
    # `assert not writers` is also satisfied when the CENSUS finds nobody to judge — a rename of
    # the write primitives, or a change to `_public_functions`, would empty the candidate pool and
    # leave this green while auditing nothing. Pin that it still has a population.
    assert candidates >= 10, (
        f"only {candidates} writer candidate(s) were examined — the reachability census is not "
        f"finding the engine's writers, so its verdict means nothing")


def test_the_deleted_lane_is_gone():
    """covers: M1 — the specific function measured, pinned so it cannot quietly return."""
    assert not hasattr(add, "quick"), (
        "add.quick() is back — it walked new -> freeze(process) -> run -> gate PASS in one call")


def test_both_type_oracles_agree_on_the_census():
    """covers: M3 — a type the engine EMITS that one oracle does not know is a self-inflicted finding.

    `ABF_TYPES` lives in two places on purpose: `add.py` compiles the graph and
    `scripts/validate_bundle.py` is the independent M0 oracle that must never be able to agree
    with the engine by construction. Independent is not the same as out of sync — adding
    `Interview` to one and not the other made `doctor` and the validator disagree about the
    FORMAT, which is the one disagreement the parity test exists to forbid.
    """
    import re
    validator = (REPO / "scripts" / "validate_bundle.py").read_text(encoding="utf-8")
    m = re.search(r"ABF_TYPES = \{([^}]*)\}", validator, re.S)
    assert m, "the validator no longer declares ABF_TYPES — this guard is stale"
    theirs = set(re.findall(r'"([A-Za-z]+)"', m.group(1)))
    assert theirs == set(add.ABF_TYPES), (
        f"the two type censuses disagree — only engine: {set(add.ABF_TYPES) - theirs}; "
        f"only validator: {theirs - set(add.ABF_TYPES)}")
