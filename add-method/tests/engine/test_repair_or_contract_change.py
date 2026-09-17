"""B4 Direction checks: implementation repair versus changed or unknown intent."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from conftest import draft_direction  # noqa: E402


def _frozen(tmp_path, slug="repair", *, scope=None):
    root = tmp_path / ".add"
    add.init(root, "code", slug)
    cid, _ = add.new(root, "Task", slug, title=slug, scope=scope or ["src/service.py"])
    path = draft_direction(root, cid)
    node, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
    assert node, note
    return root, cid, path


def _stamps(path):
    return add.read(path, "T2")["fm"]["verified"]


def test_same_contract_defect_records_cause_and_stays_build(tmp_path):
    root, cid, path = _frozen(tmp_path)
    old = _stamps(path)[:]
    node, note = add.repair(root, cid, kind="implementation",
                            cause="valid token is rejected by the implementation")
    assert node, note
    assert add._beat_of(add.scan(root)[cid]) == "build"
    stamps = _stamps(path)
    assert stamps[:len(old)] == old
    assert stamps[-1]["cause"] == "valid token is rejected by the implementation"
    assert stamps[-1]["kind"] == "implementation"
    before = path.read_bytes()
    refused, message = add.repair(root, cid, kind="implementation", cause=" ")
    assert refused is None and "R:CAUSELESS" in message
    assert path.read_bytes() == before


def test_drift_cannot_be_called_implementation_and_returns_direction(tmp_path):
    root, cid, path = _frozen(tmp_path)
    old = _stamps(path)[:]
    text = path.read_text().replace("the admit path is atomic", "the admit path may retry")
    path.write_text(text)
    node, note = add.repair(root, cid, kind="implementation",
                            cause="retry is now required for the build")
    assert node is None and "R:SEAL_TOUCH" in note
    assert _stamps(path) == old
    node, note = add.repair(root, cid, kind="change", cause="retry requirement supersedes atomic admission")
    assert node, note
    assert add.read(path, "T2")["fm"]["status"] == "direction"
    assert _stamps(path)[-1]["cause"] == "retry requirement supersedes atomic admission"
    assert _stamps(path)[-1]["to"] == "direction"
    assert _stamps(path)[:len(old)] == old


def test_scope_move_returns_direction_and_recomputes_authority(tmp_path):
    root, cid, path = _frozen(tmp_path)
    index = add.read(root / "index.md", "T2")
    add.write(root / "index.md", "---\n" + add.set_key(index["raw"], "sensitive_paths", "[src/auth/**]")
              + "\n---\n" + index["body"])
    path.write_text(path.read_text().replace("src/service.py", "src/auth/token.py"))
    node, note = add.repair(root, cid, kind="implementation", cause="token path moved")
    assert node is None and "R:SEAL_TOUCH" in note
    node, note = add.repair(root, cid, kind="change", cause="token path is now security-sensitive")
    assert node, note
    assert add.read(path, "T2")["fm"]["status"] == "direction"
    rejected, message = add.freeze(root, cid, by="plan:fixture", authority="process")
    assert rejected is None, message
    assert "floor" in message.lower() or "human" in message.lower()


def test_unknown_requirement_returns_direction_and_old_seal_cannot_run(tmp_path):
    root, cid, path = _frozen(tmp_path)
    old = _stamps(path)[:]
    node, note = add.repair(root, cid, kind="unknown",
                            cause="the rule never says what an expired token means")
    assert node, note
    assert add.read(path, "T2")["fm"]["status"] == "direction"
    assert _stamps(path)[:len(old)] == old
    assert _stamps(path)[-1]["cause"] == "the rule never says what an expired token means"
    rejected, message = add.brief_stamp(root, cid, by="plan:fixture")
    assert rejected is None and "R:OLDSEAL" in message


def test_existing_replan_preserves_seal_as_steering_control(tmp_path):
    root, cid, path = _frozen(tmp_path)
    old = _stamps(path)[:]
    node, note = add.replan(root, cid, note="run the narrower test first")
    assert node, note
    assert _stamps(path)[:len(old)] == old
    assert _stamps(path)[-1]["act"] == "replan"
    assert add.sealed_direction(add.read(path, "T2")["fm"]) == old[-1]["direction"]
