"""What "dead source" in add.py actually amounts to, measured rather than surveyed.

read-cost was planned on a survey claiming ~101 removable lines (1.75% of add.py). Re-measured
2026-09-04 by parsing the AST and searching all four corpora that can reach a name — add.py
itself, cli.py, scripts/validate_bundle.py, and the whole test tree:

    unreferenced module-level definitions   1 line    RESERVED_FILES
    functions no engine or CLI path calls   16 lines  delta_carried_on
    commented-out code                      3 lines
    duplicated "load a node or refuse"      9 sites, THREE return conventions — left alone

~22 lines, 0.37%. The bytes are not the finding. `delta_carried_on` documented the validity
interval as CLOSED-CLOSED and claimed `--as-of` was wired to it; `--as-of` is not wired to it
and implements HALF-OPEN. On a lesson's close date the live filter reports it `folded` and the
dead predicate reported it still carried — two definitions of one boundary, disagreeing on the
boundary day, with three passing assertions holding the dead one in place.
"""
import ast
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

REMOVED = ("RESERVED_FILES", "delta_carried_on")
TWINS = ("add-method/tooling/add.py", "add-method/.add/tooling/add.py",
         "add-method/src/add_method/_bundled/tooling/add.py", ".add/tooling/add.py")
PINS = ("add-method/tooling/engine_pin.py", "add-method/.add/tooling/engine_pin.py",
        ".add/tooling/engine_pin.py")


def _delta_bundle(tmp_path, line):
    add.init(tmp_path, "code", "T")
    p = Path(tmp_path) / "specs" / "method.md"
    p.write_text(p.read_text().replace("## Deltas\n", "## Deltas\n" + line + "\n", 1),
                 encoding="utf-8")
    assert "X1" in p.read_text(), "fixture: the delta line never landed in the spec"
    return tmp_path


CLOSED = "- [ADD · X1 · folded · 2026-01-01→2026-06-01] a closed lesson (evidence: /x.md)"


def _present(paths, floor, what):
    """The paths this checkout actually carries, with a floor sized to the CLAIM being made.

    Two of the four add.py twins are gitignored and so are two of the three pins: a fresh clone
    carries two twins and ONE pin, while the machine that built them has all seven. Reading them
    unconditionally passed here and failed in CI. An exists-skip is right, but the floor is not
    one number — the twins claim PARITY, which needs two to mean anything, and a pin claims it
    ATTESTS THE ENGINE ON DISK, which one pin can do alone. A single floor of 2 red the pins on
    a fresh checkout; a single floor of 1 would let the parity claim pass on one file.
    """
    have = [p for p in paths if (ROOT / p).is_file()]
    assert len(have) >= floor, f"only {len(have)} {what} present; the claim would be vacuous"
    return have


def test_the_removed_names_are_gone_everywhere():
    """covers: M1, R:BLINDCUT, A2 — neither name survives in any twin this checkout carries."""
    for twin in _present(TWINS, 2, "twin(s)"):
        text = (ROOT / twin).read_text(encoding="utf-8")
        assert len(text.splitlines()) > 5000, f"{twin}: not the engine — the search would be vacuous"
        for name in REMOVED:
            assert not re.search(r"\b" + name + r"\b", text), f"{twin} still defines {name}"


def test_one_boundary_definition_survives(tmp_path):
    """covers: M3, A3, E2 — the close date reads folded, and no rival predicate says otherwise."""
    root = _delta_bundle(tmp_path, CLOSED)
    on_close = [i.id for i in add.deltas(root, status="folded", as_of="2026-06-01")[0]]
    still_open = [i.id for i in add.deltas(root, status="open", as_of="2026-06-01")[0]]
    assert on_close == ["X1"], f"the live boundary moved: folded on the close date gave {on_close}"
    assert still_open == [], f"the interval is half-open; open on the close date gave {still_open}"
    assert not hasattr(add, "delta_carried_on"), \
        "a second, CLOSED-CLOSED definition of the boundary is still importable"


def test_the_boundary_claim_survived_the_removal(tmp_path):
    """covers: M4, R:COVERLOSS, A5 — the three assertions still run, against the live path.

    The removed predicate was pinned by three assertions: carried today, carried on the opening
    date, not carried long before it. Each one is asked here of `deltas --as-of`, which is what
    ships. The middle one is where the two definitions never disagreed; the close date is where
    they did, and that is `test_one_boundary_definition_survives`.
    """
    root = _delta_bundle(tmp_path, CLOSED)
    assert [i.id for i in add.deltas(root, status="open", as_of="2026-01-01")[0]] == ["X1"], \
        "carried on its OPENING date — the interval is closed on the left"
    assert [i.id for i in add.deltas(root, status="open", as_of="2026-05-31")[0]] == ["X1"], \
        "carried the day before it closed"
    assert [i.id for i in add.deltas(root, status="open", as_of="2000-01-01")[0]] == [], \
        "not carried before it was ever filed"


def test_all_four_twins_and_both_pins_agree():
    """covers: M2, A7, E3 — the four twins are byte-identical and both pins verify."""
    digests = {hashlib.md5((ROOT / t).read_bytes()).hexdigest() for t in _present(TWINS, 2, "twin(s)")}
    assert len(digests) == 1, f"the add.py twins have drifted: {digests}"
    engine = digests.pop()
    cli = hashlib.md5((ROOT / "add-method/tooling/cli.py").read_bytes()).hexdigest()
    for pin in _present(PINS, 1, "pin(s)"):
        text = (ROOT / pin).read_text(encoding="utf-8")
        assert f'"{engine}"' in text, f"{pin}: ENGINE_MD5 does not attest the engine on disk"
        assert f'"{cli}"' in text, f"{pin}: ENGINE_PKG_MD5 does not attest cli.py on disk"


def test_engine_surface_was_not_removed():
    """covers: E1 — a name only the tests call is engine SURFACE, and stays."""
    for name in ("neighborhood", "read_payload", "delta_address", "bind_sections"):
        assert hasattr(add, name), f"{name} was removed; a test-only caller is not a dead caller"


def test_the_inventory_is_recorded():
    """covers: M5, R:CHURN, A6, A8 — the node records what was removable and what was left."""
    card = (ROOT / ".add/tasks/source-dead-code.md").read_text(encoding="utf-8")
    why = card.split("why:", 1)[1].split("\n", 1)[0]
    assert len(why) > 400, "the why: does not carry an inventory"
    for token in ("101", "RESERVED_FILES", "delta_carried_on", "0.37%"):
        assert token in why, f"the inventory does not record `{token}`"
    assert "three different conventions" in why or "THREE" in why or "three" in why, \
        "the duplication that was deliberately NOT extracted is unrecorded -> R:CHURN"
