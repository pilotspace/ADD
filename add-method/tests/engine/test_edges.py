"""Enumerated edge cases are first-class covers referents (C7, task 1).

A `## EDGES` section declares concrete edge cases as `- E<n> <the case>`. Each real (non-placeholder)
edge is a legal `covers:` referent the gate enforces exactly as a Must: an uncovered edge refuses PASS,
a covered edge passes, a placeholder edge is no obligation, and a node with no EDGES is unchanged.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
sys.path.insert(0, str(REPO / "scripts"))
import add  # noqa: E402


BODY = """## CARD
goal: a task with an enumerated edge
beat: build · next: add run

## RULES
<must>
- M1 the rule
</must>

## EDGES
{edges}

## CHECKS
{checks}
red-first: every check MUST fail first.
"""


def _git(*a, cwd):
    subprocess.run(["git", *a], cwd=str(cwd), capture_output=True, text=True)


def _node(tmp_path, edges, checks, report=("test_m1",)):
    _git("init", "-q", cwd=tmp_path)
    _git("config", "user.email", "t@e.com", cwd=tmp_path)
    _git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "s.py").write_text("x = 1\n")
    root = tmp_path / ".add"
    add.init(root, "code", "E")
    cid, _ = add.new(root, "Task", "t", title="t", depth="standard", sensitivity="mechanical", scope=["src/s.py"])
    path = root / cid.lstrip("/")
    raw = add.read(path, "T2")["raw"]
    add.write(path, f"---\n{add.set_key(raw, 'status', 'build')}\n---\n" + BODY.format(edges=edges, checks=checks))
    # The seal, then the brief entry — `gate` refuses a PASS on a node that was never
    # frozen (R:UNSEALED), so a fixture that skips the one approval tests no real path.
    add.freeze(root, cid, "human:t")
    add.brief_stamp(root, cid)
    _git("add", "-A", cwd=tmp_path)
    _git("commit", "-q", "-m", "i", cwd=tmp_path)
    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in report)
    # The command writes the report, so both halves of the receipt come from the same
    # process — a file dropped beside the run no longer earns `kind: test-ids`.
    doc = f"<testsuites><testsuite>{cases}</testsuite></testsuites>"
    add.run(root, cid, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
            cwd=tmp_path, junit=xml)
    return root, cid


M1_CHECK = "- test_m1 · covers: M1 · proves the rule"


def test_uncovered_edge_refuses_gate(tmp_path):
    """covers: R:UNCOVEREDEDGE, M3 — a real edge with no covering check refuses PASS."""
    root, cid = _node(tmp_path, edges="- E1 empty input list", checks=M1_CHECK, report=("test_m1",))
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is False, "an uncovered declared edge must refuse PASS"
    assert "E1" in note, note


def test_covered_edge_passes_gate(tmp_path):
    """covers: M3 — the same node with a passing `covers: E1` check gates PASS."""
    root, cid = _node(tmp_path, edges="- E1 empty input list",
                      checks=M1_CHECK + "\n- test_empty · covers: E1 · proves the edge",
                      report=("test_m1", "test_empty"))
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, note


def test_placeholder_edge_is_no_obligation(tmp_path):
    """covers: M2, E1 — a `## EDGES` entry still carrying `<...>` is not an obligation."""
    root, cid = _node(tmp_path, edges="- E1 <the edge case>", checks=M1_CHECK, report=("test_m1",))
    node = add.read((root / cid.lstrip("/")), "T2")
    assert "E1" not in add.edges_of(node), "a placeholder edge must not be a declared edge"
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, f"a placeholder edge must not block the gate: {note}"


def test_no_edges_section_unchanged(tmp_path):
    """covers: M3 — a node with no `## EDGES` gates exactly as before."""
    root, cid = _node(tmp_path, edges="", checks=M1_CHECK, report=("test_m1",))
    # strip the empty EDGES heading to model a node that never had one
    path = root / cid.lstrip("/")
    text = path.read_text(encoding="utf-8").replace("## EDGES\n\n\n", "")
    path.write_text(text, encoding="utf-8")
    _git("add", "-A", cwd=tmp_path)
    _git("commit", "-q", "-m", "noedges", cwd=tmp_path)
    xml = tmp_path / "r.xml"
    doc = '<testsuites><testsuite><testcase classname="c" name="test_m1"/></testsuite></testsuites>'
    add.run(root, cid, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
            cwd=tmp_path, junit=xml)
    ok, note = add.gate(root, cid, "PASS", by="human:t")
    assert ok is True, note


def test_grammar_admits_edge_id_in_all_oracles(tmp_path):
    """covers: M1, R:DRIFT — the engine and the validator (the package's two oracles) accept `E1`.

    The source repo also holds FORMAT.md §6.1 as a third oracle held equal by a parity test; the
    published package ships the engine + validator, so agreement here is the R:DRIFT guard that
    travels with it."""
    import re
    import validate_bundle  # noqa: E402
    assert validate_bundle.COVERS_RULE.match("E1"), "validator COVERS_RULE must admit E1"
    inner = re.search(r"\(([^)]+)\)", add.RULE_ID.pattern).group(1)
    assert re.compile(rf"\A({inner})\Z").match("E1"), "engine RULE_ID must admit E1"
