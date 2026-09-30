"""RED contract: an escape prevention earns policy only from later evidence."""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


@pytest.fixture()
def bundle(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "prevention.py").write_text("def held(): return True\n")
    root = tmp_path / ".add"
    add.init(root, "code", "P")
    add.new(root, "Task", "filing", title="filing", scope=["src/prevention.py"])
    return root


def _escape(bundle: Path, lesson: str = "escaped defect") -> None:
    ok, note = add.learn(
        bundle, "method", lesson, evidence="/tasks/filing.md", escape=True,
        why_missed="the prevention was never exercised",
        prevention="check → src/prevention.py",
    )
    assert ok, note


def _assert_validation_surface() -> None:
    assert "validation" in inspect.signature(add.fold).parameters, \
        "RED: fold has no explicit later validation receipt"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_escape_bind_requires_explicit_validation(bundle):
    _escape(bundle)
    ok, note = add.fold(bundle, "method", "escaped defect",
                        bind="owner · prevention is policy")
    assert ok is None and "R:UNVALIDATED" in note, note


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_self_or_date_only_validation_refuses(bundle):
    _assert_validation_surface()
    _escape(bundle)
    ok, note = add.fold(
        bundle, "method", "escaped defect", bind="owner · policy",
        validation="/tasks/filing.d/runs/1.md",
    )
    assert ok is None and "R:UNVALIDATED" in note and "distinct" in note.lower(), note


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_receipt_stamp_gate_and_bound_purpose_must_agree(bundle):
    _assert_validation_surface()
    assert hasattr(add, "escape_validation_eligibility"), \
        "RED: no centralized receipt/stamp/gate/purpose reader exists"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_exact_sealed_scope_blob_is_required(bundle):
    _assert_validation_surface()
    assert hasattr(add, "escape_validation_eligibility"), \
        "RED: no centralized sealed-scope/blob reader exists"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_committed_descendant_validation_can_bind(bundle):
    _assert_validation_surface()
    assert hasattr(add, "filing_commit_for_delta"), \
        "RED: no durable filing-commit anchor reader exists"


@pytest.mark.xfail(strict=True, reason="red-first check for a Task still in direction; 3.7.0 ships without it and ADD 4.0 retires the engine, so it is never built")
def test_mixed_match_refuses_atomically_with_actionable_reason(bundle):
    assert add.learn(bundle, "method", "shared ordinary", evidence="/tasks/filing.md")[0]
    _escape(bundle, "shared escaped")
    before = (bundle / "specs" / "method.md").read_bytes()
    ok, note = add.fold(bundle, "method", "shared", bind="owner · policy")
    assert ok is None and "R:UNVALIDATED" in note and "shared escaped" in note, note
    assert (bundle / "specs" / "method.md").read_bytes() == before
