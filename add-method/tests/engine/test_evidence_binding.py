"""Red suite for e12 `build-evidence-binding` — the covers: binding.

A15's finding was that `covers:` was a LABEL, not a binding: a task could claim a Must was
proven by a check that never ran, and nothing noticed. This suite makes the claim earn its
keep — a Must is proven only by a check ID the runner actually reported passing.

It also closes the gap e7 left open: until IDs can be extracted, `test-ids` is unreachable
and every receipt degrades to `command-exit`.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


TASK_BODY = """## CARD
goal: a task with real checks

## RULES
<must>
- M1 the first rule
- M2 the second rule
- M3 a rule nothing checks
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## CHECKS
- test_one · covers: M1 · proves the first rule
- test_two · covers: M2, R:BAD · proves the second and the reject
- test_never_ran · covers: M1 · claims the first rule but is not in any receipt
red-first: every check MUST fail first.
"""


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Binding")
    cid, _ = add.new(tmp_path, "Task", "bound", title="Bound task", depth="standard")
    path = tmp_path / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n{TASK_BODY}")
    return tmp_path


# ------------------------------------------------------------ the covers: map (M1)


def test_covers_parsed_from_checks(bundle):
    """covers: M1 — the map is built from the CHECKS section, keyed by rule."""
    covers = add.covers(add.scan(bundle)["/tasks/bound.md"])
    assert covers["M1"] == ["test_one", "test_never_ran"]
    assert covers["M2"] == ["test_two"]
    assert covers["R:BAD"] == ["test_two"]


def test_bind_requires_reported_id(bundle):
    """covers: M1, R:LABEL — a covers: naming a test that did not run proves nothing.

    This is A15's whole point. `test_never_ran` claims M1; the runner never reported it,
    so it contributes no proof.
    """
    reported = {"test_one": "pass", "test_two": "pass"}
    proven, unproven = add.bind(add.scan(bundle)["/tasks/bound.md"], reported)
    assert "M1" in proven and "M2" in proven and "R:BAD" in proven
    assert proven["M1"] == ["test_one"], "an unreported check was counted as proof"


def test_failing_check_does_not_prove(bundle):
    """covers: M1, R:LABEL — a check that RAN and FAILED proves nothing either."""
    reported = {"test_one": "fail", "test_two": "pass"}
    proven, unproven = add.bind(add.scan(bundle)["/tasks/bound.md"], reported)
    assert "M1" in unproven, "a failing check was accepted as proof"


def test_unbound_musts_reported(bundle):
    """covers: M3, R:SILENTGAP — M3 has no check at all; the gap must be visible."""
    gaps = add.unbound(add.scan(bundle)["/tasks/bound.md"], {"test_one": "pass", "test_two": "pass"})
    assert "M3" in gaps, f"a Must with no check went unreported: {gaps}"
    assert "M1" not in gaps


# ------------------------------------------------- IDs extracted from real runner output (M2)


def test_extract_ids_from_junit(tmp_path):
    """covers: M2 — junit-xml is the v1.0 format A1 scoped this to."""
    xml = tmp_path / "j.xml"
    xml.write_text(
        '<?xml version="1.0"?><testsuites><testsuite name="s" tests="2">'
        '<testcase classname="c" name="test_one"/>'
        '<testcase classname="c" name="test_two"><failure message="x"/></testcase>'
        "</testsuite></testsuites>")
    ids = add.extract_ids(xml)
    # Keys carry the classname since e16 (M1): the bare key let two same-named tests in
    # different files collide, and the failing one could be the loser. The outcomes this
    # check has always asserted are unchanged — only the id shape is.
    assert ids == {"c::test_one": "pass", "c::test_two": "fail"}


def test_extract_ids_missing_file_is_unknown(tmp_path):
    """covers: M2 — no report means `unknown`, never an invented pass."""
    assert add.extract_ids(tmp_path / "nope.xml") == {}


def test_extract_ids_corrupt_is_unknown(tmp_path):
    """covers: M2, law 3 — unparseable output reports; it does not raise."""
    bad = tmp_path / "bad.xml"
    bad.write_text("<not xml at all")
    assert add.extract_ids(bad) == {}


# ------------------------------------------- the kind becomes earnable (M2, A24, e7's gap)


def test_run_earns_test_ids_with_junit(bundle, tmp_path):
    """covers: M2 — with real IDs the receipt may finally claim `test-ids` (A24).

    e7 left this unreachable: every receipt was `command-exit` with `ids: unknown`. A kind
    that can never be earned is not a ladder, it is a label.
    """
    xml = bundle / "report.xml"
    node = add.run(bundle, "/tasks/bound.md",
                   [sys.executable, "-c",
                    f"open({str(xml)!r},'w').write('<testsuites><testsuite><testcase name=\"test_one\"/>"
                    "</testsuite></testsuites>')"],
                   cwd=bundle, junit=xml)
    assert node["receipt"]["kind"] == "test-ids", node["receipt"]
    assert node["receipt"]["ids"] != "unknown"


def test_run_without_junit_stays_command_exit(bundle):
    """covers: M2 — no report, no promotion. The degradation stays honest."""
    node = add.run(bundle, "/tasks/bound.md", [sys.executable, "-c", "pass"], cwd=bundle)
    assert node["receipt"]["kind"] == "command-exit"
    assert node["receipt"]["ids"] == "unknown"


# ------------------------------------------------------------------- the live bundle (M3)


def test_live_bundle_binding():
    """covers: M1, M3 — this repo's own gated tasks, checked for unbound Musts.

    Reports rather than asserts zero: an unbound Must is a finding to look at, and this
    project should be able to see its own.
    """
    graph = add.scan(REPO / ".add")
    gaps = {}
    for cid, node in graph.items():
        if (node["fm"] or {}).get("type") != "Task":
            continue
        missing = add.unbound(node, {})
        if missing:
            gaps[cid] = missing
    assert isinstance(gaps, dict)
    print(f"\nunbound Musts across {len(graph)} nodes: {len(gaps)} tasks")
