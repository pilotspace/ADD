"""A dimension is retired more cheaply than an honest assumption can be written.

`assumption_sweep` proves the author LOOKED at every (dimension x surface) pair. A dimension can
be retired instead, and the docstring says how:

    or the dimension must be retired with `n/a` and a reason

The code checks for no reason:

    if re.match(r"^n/?a\\b", rest.strip(), re.I):
        waived.add(dim)

Six bare `n/a` lines therefore defeat the whole six-dimension sweep, and each one is cheaper to
type than a single honest assumption — which is the shape that makes a guard get routed around
rather than satisfied.

Measured 2026-09-03 across both bundles in this repo: 584 assumption lines, 4 of which actually
waive, and all 4 already state a reason. So the promise costs nothing to keep — nothing already
written is refused by making the code mean what its docstring says.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DIMS = add.SWEEP_DIMENSIONS


def _node(lines):
    """A node with one surface and the given ASSUMPTIONS lines."""
    return {"fm": {"type": "Task", "gives": ["S1 x"], "depth": "standard"},
            "body": "## ASSUMPTIONS\n" + "\n".join(lines) + "\n\n## PLAN\ncontract: c\n"}


def _swept(lines):
    """The dimensions this node has NOT left unswept."""
    return {d for d in DIMS} - {d for d, _ in add.assumption_sweep(_node(lines))}


# ------------------------------------------------------------------ M1 · the cheap escape

def test_a_bare_n_a_does_not_retire_its_dimension():
    """covers: M1, A4, E1, R:CHEAPSILENCE — the cheap total escape."""
    for bare in ("- A1 [who] n/a", "- A1 [who] n/a ", "- A1 [who] N/A", "- A1 [who] na"):
        assert "who" not in _swept([bare]), f"{bare!r} retired a dimension with no reason"


def test_six_bare_waivers_do_not_empty_the_sweep():
    """covers: M1, E3 — the measured shape of the escape: one line per dimension, all silent."""
    lines = [f"- A{i} [{d}] n/a" for i, d in enumerate(DIMS, 1)]
    assert add.assumption_sweep(_node(lines)), \
        "six bare waivers emptied the sweep — the six-dimension matrix has a six-line off switch"


# ------------------------------------------------------------------ M2 · what stays legal

def test_a_waiver_with_a_reason_still_retires():
    """covers: M2, A2, A3 — every waiver already written in this repo stays legal.

    A2: the bar is a non-empty reason, never a length or quality bar. A notary cannot judge
    whether a reason is good, and a bar it cannot judge only teaches authors to pad.
    """
    for stated in (
            "- A1 [who] n/a · no authority changes what a scaffold is",
            "- A1 [who] n/a - the claims are independent",
            "- A1 [who] n/a, out of scope for a creation guard",
            "- A1 [who] n/a · x",                      # short, honest, accepted
    ):
        assert "who" in _swept([stated]), f"{stated!r} was refused despite stating a reason"


def test_every_waiver_in_this_repo_survives():
    """covers: A3 — measured before the guard was written; the repair, if any, comes first."""
    for bundle in (REPO.parent / ".add", REPO / ".add"):
        if not (bundle / "tasks").is_dir():
            continue
        for f in sorted((bundle / "tasks").glob("*.md")):
            node = add.read(f, "T2")
            for line in add._section_of(node["body"] or "", "ASSUMPTIONS").splitlines():
                m = add.RE_ASSUMPTION_LINE.match(line.strip())
                if m and re.match(r"^n/?a\b", m.group(2).strip(), re.I):
                    assert re.match(r"^n/?a\b\s*[·,-]\s*\S", m.group(2).strip(), re.I), \
                        f"{f.name} carries a bare waiver this change would newly refuse: {line}"


# ------------------------------------------------------------------ M3/M4 · the message and the promise

def test_the_refusal_names_the_unexplained_dimension():
    """covers: M3, A6 — the fix is to write the why, so the refusal must say which dimension."""
    unswept = add.assumption_sweep(_node(["- A1 [who] n/a"]))
    assert any(d == "who" for d, _ in unswept), \
        f"the unexplained dimension is not reported as unswept: {unswept}"


def test_the_docstring_promise_is_the_behaviour():
    """covers: M4, E2 — code and prose read together, in one check.

    E2: `n/aX` is not a waiver at all — `\\b` already excludes it, and this pins that it stays
    excluded rather than becoming a reason-bearing waiver by accident.
    """
    doc = add.assumption_sweep.__doc__ or ""
    assert "and a reason" in doc, \
        "the docstring no longer promises a reason — change the promise or the code, not neither"
    assert "who" not in _swept(["- A1 [who] n/aX something"]), \
        "`n/aX` was read as a waiver"
