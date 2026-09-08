"""The runner for `backlog-drain` — a non-code task, checked the same way any other is.

`add run` parses JUnit XML and does not care what produced it, so a check over the live bundle
earns exactly the same bound receipt as a pytest check over the engine. These assert facts about
`.add/specs/*.md` after the sitting, not about any Python.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2].parent
BUNDLE = REPO / ".add"
SPECS = sorted((BUNDLE / "specs").glob("*.md"))
# NOT a hardcoded list. A set frozen at planning time is exactly what let Q25 be swallowed and
# Q26 be missed — the bundle moved between the plan and the run. The deferred set is COMPUTED
# from the same window `milestone-done` refuses on, so it is right whenever this check runs.
sys.path.insert(0, str(BUNDLE / "tooling"))
import add  # noqa: E402

_MILESTONE = add.scan(BUNDLE)["/milestones/loop-that-drains.md"]
_ANCHOR = add.milestone_window_anchor(_MILESTONE["fm"])
DEFERRED = {d.id for d in add.deltas(BUNDLE, status="open")[0]
            if d.valid_from and _ANCHOR and d.valid_from >= _ANCHOR}
BEFORE = 78                                # open deltas when the sitting was planned

DELTA = re.compile(r"^- \[([A-Z]+) · (\w+) · (open|folded|rejected)")


def _lines(path):
    return [DELTA.match(l) for l in path.read_text().splitlines() if DELTA.match(l)]


def _decisions(path):
    out, inside = [], False
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            inside = line.strip().lower() == "## decisions that bind"
            continue
        if inside and line.startswith("- "):
            out.append(line)
    return out


def check_no_open_deltas_remain():
    """covers: M1, M4, A1 — every pre-existing lesson resolved, none deleted, no id reused."""
    ids, still_open = [], []
    for p in SPECS:
        for m in _lines(p):
            ids.append(f"{p.stem}:{m.group(2)}")
            if m.group(3) == "open":
                still_open.append(m.group(2))
    assert len(ids) == len(set(ids)), "an id was reused — ids retire in place (M4)"
    assert len(ids) >= BEFORE, f"delta lines were DELETED: {len(ids)} < {BEFORE} (M4)"
    leftover = set(still_open) - DEFERRED
    assert not leftover, f"pre-existing lessons left open (M1): {sorted(leftover)}"
    # A1: the verdicts are the human's. Every retagged line carries a verdict word the engine
    # only writes on an explicit call — there is no path by which one appears unasked.
    assert any(m.group(3) == "rejected" for p in SPECS for m in _lines(p)), \
        "no verdict beyond fold was recorded, so no human call is evidenced"


def check_every_spec_binds_something():
    """covers: M3, E2, A6 — a lens that retained a lesson binds; one that did not is NAMED."""
    unbound = []
    for p in SPECS:
        kept = [m for m in _lines(p) if m.group(3) == "folded"]
        decisions = [d for d in _decisions(p) if "<" not in d]
        if not kept:
            unbound.append(p.stem)
            continue
        assert decisions, f"{p.stem} retained {len(kept)} lesson(s) and bound nothing (M3)"
        assert any("(from: /specs/" in d for d in decisions), \
            f"{p.stem}'s decision cites no delta id (M3)"
    assert unbound == ["domain"], \
        f"the unbound lenses are not the one this task declared: {unbound}"
    out = subprocess.run([sys.executable, str(BUNDLE / "tooling" / "cli.py"), "brief",
                          "backlog-drain"], capture_output=True, text=True, cwd=str(REPO)).stdout
    for stem in ("method", "quality", "system", "experience"):
        assert f'id="specs/{stem}#decisions-that-bind" unauthored="true"' not in out, \
            f"{stem} still reports unauthored to every brief"


def check_false_lessons_were_rejected():
    """covers: M2, R:FALSECARRY, E1 — a stale claim is never recorded as carried truth."""
    rejected = {m.group(2) for p in SPECS for m in _lines(p) if m.group(3) == "rejected"}
    for did in ("D1", "M27"):
        assert did in rejected, f"{did} is contradicted by shipped code and was not rejected"
    assert len(rejected) == 5, f"expected the 5 verified stale claims, got {sorted(rejected)}"


def check_the_drain_was_not_a_bulk_fold():
    """covers: R:BULKFOLD, A2 — a cleared pile that wrote no decision proves nothing."""
    bound = [d for p in SPECS for d in _decisions(p) if "<" not in d]
    assert len(bound) >= 10, f"only {len(bound)} decisions written — that is a bulk fold"
    for d in bound:
        assert "(from: /specs/" in d, f"a decision cites no lesson: {d[:70]}"
        assert not d.lstrip("- ").lower().startswith(("we learned", "the ", "a lesson")), \
            f"a decision reads as narrative, not as a constraint: {d[:70]}"


def main():
    cases, failures = [], 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("check_"):
            continue
        try:
            fn()
            cases.append(f'<testcase classname="backlog_drain" name="{name}"/>')
        except AssertionError as e:
            failures += 1
            cases.append(f'<testcase classname="backlog_drain" name="{name}">'
                         f'<failure message="{str(e)[:400]}"/></testcase>')
            print(f"FAIL {name}: {e}")
        else:
            print(f"ok   {name}")
    xml = (f'<?xml version="1.0"?><testsuites><testsuite name="backlog-drain" '
           f'tests="{len(cases)}" failures="{failures}">' + "".join(cases) + "</testsuite></testsuites>")
    out = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--junitxml=")), None)
    if out:
        Path(out).write_text(xml)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
