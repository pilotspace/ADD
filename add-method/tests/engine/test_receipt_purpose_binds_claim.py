"""RED contract checks: a receipt's purpose limits the claim it may authorize."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from conftest import draft_direction, git  # noqa: E402


@pytest.fixture
def project(tmp_path):
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src.py").write_text("value = 1\n")
    git("add", "src.py", cwd=tmp_path)
    git("commit", "-q", "-m", "initial", cwd=tmp_path)
    bundle = tmp_path / ".add"
    add.init(bundle, "code", "T")
    return tmp_path, bundle


def _task(project, slug="claim", *, kind="feature", sensitivity="mechanical"):
    work, bundle = project
    cid, _ = add.new(bundle, "Task", slug, title=slug, depth="standard",
                     kind=kind, sensitivity=sensitivity, scope=["src.py"])
    draft_direction(bundle, cid)
    if kind == "explore":
        path = bundle / cid.lstrip("/")
        text = path.read_text().replace("contract: <the shape this publishes>",
                                        "contract: answers\nbudget: 8 tool calls")
        text = text.replace("## EVIDENCE", "## FINDINGS\n- F1 (answers M1) · observed source "
                            "· (evidence: /tasks/claim.d/runs/1.md)\n\n## EVIDENCE")
        path.write_text(text)
    return work, bundle, cid


def _run(work, bundle, cid, *, purpose="bound", floor=False):
    command = [sys.executable, "-c", "pass"]
    return add.run(bundle, cid, command, cwd=work, purpose=purpose, floor=floor)


def _stamp(bundle, cid, receipt_path):
    fm = add.read(bundle / cid.lstrip("/"), "T0")["fm"] or {}
    path = "/" + str(Path(receipt_path).relative_to(bundle))
    return next(s for s in (fm.get("verified") or []) if s.get("act") == "run"
                and s.get("receipt") == path)


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_run_stamps_bound_support_and_floor_purpose(project):
    """M1/M4: the receipt and run stamp agree; --floor keeps its legacy marker."""
    work, bundle, cid = _task(project)
    for purpose, floor in (("bound", False), ("support", False), ("floor", True)):
        result = _run(work, bundle, cid, purpose=purpose, floor=floor)
        assert result["receipt"]["purpose"] == purpose
        assert _stamp(bundle, cid, result["path"])["purpose"] == purpose
        if floor:
            assert result["receipt"]["floor"] == "regression"


def test_legacy_purpose_normalization_and_conflict(project):
    """M2: missing purpose keeps old bound/floor meanings; contradiction never promotes."""
    work, bundle, cid = _task(project)
    bound = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=work)
    floor = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=work, floor=True)
    assert add.latest_receipt(bundle, cid)[1] == "/" + str(Path(bound["path"]).relative_to(bundle))
    assert add.latest_floor_receipt(bundle, cid)[1] == "/" + str(Path(floor["path"]).relative_to(bundle))
    p = Path(floor["path"])
    p.write_text(p.read_text().replace("  floor: regression", "  purpose: bound\n  floor: regression"))
    assert add.latest_receipt(bundle, cid)[1] != "/" + str(p.relative_to(bundle))


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_support_only_cannot_enter_code_gate_or_build_beat(project):
    """M3/E1: even a green support command cannot fulfill code proof."""
    work, bundle, cid = _task(project)
    result = _run(work, bundle, cid, purpose="support")
    assert result["receipt"]["exit"] == 0
    assert add.latest_receipt(bundle, cid) == (None, None)
    graph = add.scan(bundle)
    assert add._beat_of(graph[cid], None, graph) == "build"
    ok, note = add.gate(bundle, cid, "PASS", by="fixture")
    assert ok is None and "bound" in note.lower(), note


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_newer_support_does_not_displace_bound_refute_or_hint(project):
    """M3/E2: purpose filters before newest-run selection in every reader."""
    work, bundle, cid = _task(project)
    bound = _run(work, bundle, cid, purpose="bound")
    _run(work, bundle, cid, purpose="support")
    expected = "/" + str(Path(bound["path"]).relative_to(bundle))
    assert add.latest_receipt(bundle, cid)[1] == expected
    stamps = (add.read(bundle / cid.lstrip("/"), "T0")["fm"] or {})["verified"]
    assert add._latest_run_cid(stamps) == expected
    assert (add.refute(bundle, cid, by="fixture", held=True)[0] or {}).get("receipt") == expected


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_floor_selector_ignores_support_and_bound(project):
    """M4/E2: later diagnostics cannot displace the regression receipt."""
    work, bundle, cid = _task(project)
    floor = _run(work, bundle, cid, purpose="floor", floor=True)
    _run(work, bundle, cid, purpose="bound")
    _run(work, bundle, cid, purpose="support")
    expected = "/" + str(Path(floor["path"]).relative_to(bundle))
    assert add.latest_floor_receipt(bundle, cid)[1] == expected


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_explore_support_preserves_sources_gate(project):
    """M5/E3: support in FINDINGS cannot switch to code receipt semantics."""
    work, bundle, cid = _task(project, kind="explore")
    _run(work, bundle, cid, purpose="support")
    assert add.latest_receipt(bundle, cid) == (None, None)
    # The Explore source lane requires a frozen budget and questions. This RED check
    # limits itself to its receipt selection, without recording a human approval.
    assert add.latest_support_receipt(bundle, cid)[0]["purpose"] == "support"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_local_holdout_refuses_before_execution(project):
    """M6/E5: a local command cannot self-attest protected origin."""
    work, bundle, cid = _task(project)
    marker = work / "executed.txt"
    result = add.run(bundle, cid, [sys.executable, "-c",
                                   f"open({str(marker)!r}, 'w').write('ran')"],
                     cwd=work, purpose="holdout")
    assert result["path"] is None and not marker.exists()
    assert add.latest_receipt(bundle, cid) == (None, None)


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_security_floor_stays_human_with_support(project):
    """M7: a support purpose cannot lower the computed human floor."""
    work, bundle, cid = _task(project, slug="secure", sensitivity="security")
    _run(work, bundle, cid, purpose="support")
    assert add.authority_for(add.scan(bundle), cid) == "human"
    ok, note = add.gate(bundle, cid, "PASS", by="fixture")
    assert ok is None and ("lens" in note.lower() or "bound" in note.lower()), note
