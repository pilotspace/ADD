"""B4 Direction checks: implementation repair versus changed or unknown intent."""
import re
import subprocess
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


def _receipt_paths(root, cid):
    slug = cid.rsplit("/", 1)[-1][:-3]
    return sorted((root / "tasks" / f"{slug}.d" / "runs").glob("*.md"))


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


def test_direction_return_outranks_an_old_run_for_the_current_beat(tmp_path):
    root, cid, _path = _frozen(tmp_path)
    result = add.run(root, cid, [sys.executable, "-c", "pass"], cwd=tmp_path)
    assert result["receipt"]["exit"] == 0, result["note"]
    assert add._beat_of(add.scan(root)[cid]) == "verify"

    node, note = add.repair(root, cid, kind="unknown",
                            cause="the frozen rule does not define the retry boundary")
    assert node, note
    assert add._beat_of(add.scan(root)[cid]) == "direction", (
        "a run recorded before the Direction return must not keep controlling the beat")


def test_direction_return_blocks_brief_run_and_gate_without_execution_or_receipt(tmp_path):
    root, cid, _path = _frozen(tmp_path)
    first = add.run(root, cid, [sys.executable, "-c", "pass"], cwd=tmp_path)
    assert first["receipt"]["exit"] == 0, first["note"]
    before_receipts = _receipt_paths(root, cid)

    node, note = add.repair(root, cid, kind="unknown",
                            cause="the contract is silent about expired credentials")
    assert node, note

    digest, message = add.brief_stamp(root, cid, by="plan:fixture")
    assert digest is None and "R:OLDSEAL" in message

    marker = tmp_path / "must-not-run"
    result = add.run(root, cid,
                     [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"],
                     cwd=tmp_path)
    assert result["receipt"]["exit"] != 0 and "R:OLDSEAL" in result["note"]
    assert not marker.exists(), "a run behind an invalidated seal executed its command"
    assert _receipt_paths(root, cid) == before_receipts, (
        "a refused run behind an invalidated seal wrote a receipt")

    gated, message = add.gate(root, cid, "PASS", by="plan:fixture", authority="plan")
    assert gated is None and "R:OLDSEAL" in message


def test_refreeze_after_direction_return_restores_build_entry(tmp_path):
    root, cid, _path = _frozen(tmp_path)
    node, note = add.repair(root, cid, kind="unknown",
                            cause="the timeout meaning needs an explicit decision")
    assert node, note
    assert add._beat_of(add.scan(root)[cid]) == "direction"

    node, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
    assert node, note
    assert add._beat_of(add.scan(root)[cid]) == "build"
    digest, message = add.brief_stamp(root, cid, by="plan:fixture")
    assert digest, message


def test_repair_refuses_wrong_node_states(tmp_path):
    root = tmp_path / ".add"
    add.init(root, "code", "wrong nodes")

    unfrozen, _ = add.new(root, "Task", "unfrozen", title="unfrozen",
                          scope=["src/unfrozen.py"])
    refused, message = add.repair(root, unfrozen, kind="implementation", cause="code defect")
    assert refused is None and "R:WRONGNODE" in message

    _, done, done_path = _frozen(tmp_path, slug="done")
    node = add.read(done_path, "T2")
    add.write(done_path, f"---\n{add.set_key(node['raw'], 'status', 'done')}\n---\n{node['body']}")
    refused, message = add.repair(root, done, kind="implementation", cause="late defect")
    assert refused is None and "R:WRONGNODE" in message

    _, returned, returned_path = _frozen(tmp_path, slug="returned")
    node, note = add.repair(root, returned, kind="unknown", cause="meaning still open")
    assert node, note
    before = returned_path.read_bytes()
    refused, message = add.repair(root, returned, kind="implementation", cause="code defect")
    assert refused is None and "R:WRONGNODE" in message
    assert returned_path.read_bytes() == before

    milestone, _ = add.new(root, "Milestone", "milestone", title="milestone")
    milestone_path = root / milestone.lstrip("/")
    node = add.read(milestone_path, "T2")
    raw = node["raw"].replace(
        "verified: []",
        'verified:\n  - { by: "human:fixture", at: 2026-09-24, act: freeze, authority: human }')
    add.write(milestone_path, f"---\n{raw}\n---\n{node['body']}")
    refused, message = add.repair(root, milestone, kind="implementation", cause="code defect")
    assert refused is None and "R:WRONGNODE" in message


def test_legacy_and_malformed_scope_seals_are_uncertain_not_clean(tmp_path):
    for malformed in (False, True):
        root, cid, path = _frozen(tmp_path, slug="malformed" if malformed else "legacy")
        text = path.read_text()
        if malformed:
            text = re.sub(r'scope: "sha256:[0-9a-f]+"', 'scope: malformed', text, count=1)
        else:
            text = re.sub(r', scope: "sha256:[0-9a-f]+"', '', text, count=1)
        path.write_text(text)

        refused, message = add.repair(root, cid, kind="implementation",
                                      cause="implementation rejects a valid input")
        assert refused is None and "R:SEAL_TOUCH" in message
        node, note = add.repair(root, cid, kind="unknown",
                                cause="the approved scope cannot be verified")
        assert node, note
        assert add._beat_of(add.scan(root)[cid]) == "direction"


def test_semantic_change_without_text_edit_returns_direction(tmp_path):
    root, cid, path = _frozen(tmp_path)
    sealed = _stamps(path)[-1]["direction"]
    node, note = add.repair(root, cid, kind="change",
                            cause="the product owner changed the retry semantics")
    assert node, note
    assert add.direction_digest(add.read(path, "T2")) == sealed, (
        "control: this is a declared semantic change, not observed text drift")
    assert add._beat_of(add.scan(root)[cid]) == "direction"


def test_repair_cli_and_stamp_contract(tmp_path):
    root, cid, path = _frozen(tmp_path)
    cli = REPO / "tooling" / "cli.py"
    command = [sys.executable, str(cli), "--root", str(root), "repair", cid]
    before = path.read_bytes()
    bad = subprocess.run(command + ["--kind", "other", "--cause", "code defect"],
                         capture_output=True, text=True)
    assert bad.returncode == 2 and path.read_bytes() == before
    good = subprocess.run(command + ["--kind", "implementation", "--cause",
                                     "valid input is rejected", "--by", "plan:fixture"],
                          capture_output=True, text=True)
    assert good.returncode == 0, good.stdout + good.stderr
    stamp = _stamps(path)[-1]
    assert stamp["act"] == "repair"
    assert stamp["kind"] == "implementation"
    assert stamp["cause"] == "valid input is rejected"
    assert stamp["to"] == "build"
    assert stamp["authority"] == "process"
    assert stamp["by"] == "plan:fixture"


def test_carry_mapping_drift_is_not_an_implementation_repair(tmp_path):
    root, _, _ = _frozen(tmp_path, slug="original")
    _, cid, path = _frozen(tmp_path, slug="destination")
    edge = "/tasks/original.md#RULES:M1 -> /tasks/destination.md#RULES:M1"
    path.write_text(path.read_text().replace(
        "verified:\n", f'carries:\n  - "{edge}"\nverified:\n', 1).replace(
        "## PLAN\n", "## PLAN\nregression: none · isolated carry fixture\n", 1))
    frozen, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
    assert frozen, note
    path.write_text(path.read_text().replace(f'carries:\n  - "{edge}"\n', ""))
    before = path.read_bytes()
    refused, message = add.repair(root, cid, kind="implementation",
                                  cause="code rejects valid input")
    assert refused is None and "R:SEAL_TOUCH" in message
    assert path.read_bytes() == before


def test_direction_return_blocks_risk_accepted_and_direct_done(tmp_path):
    root, cid, path = _frozen(tmp_path)
    node = add.read(path, "T2")
    gate = '{ by: "plan:fixture", at: 2026-09-24, act: gate, authority: plan, outcome: PASS }'
    add.write(path, f"---\n{add.append_item(node['raw'], 'verified', gate)}\n---\n{node['body']}")
    assert add.repair(root, cid, kind="unknown", cause="meaning must be clarified")[0]
    before = path.read_bytes()
    refused, message = add.gate(root, cid, "RISK-ACCEPTED", by="plan:fixture",
                                reason="old result cannot decide this")
    assert refused is None and "R:OLDSEAL" in message
    refused, _, message = add.done(root, cid)
    assert refused is None and "R:OLDSEAL" in message
    assert path.read_bytes() == before


def test_refreeze_does_not_reuse_a_pre_return_receipt_for_risk_accepted(tmp_path):
    root, cid, path = _frozen(tmp_path)
    assert add.brief_stamp(root, cid, by="plan:fixture")[0]
    old = add.run(root, cid, [sys.executable, "-c", "pass"], cwd=tmp_path)
    assert old["receipt"]["exit"] == 0
    assert add.repair(root, cid, kind="unknown", cause="the retry contract is open")[0]
    assert add.freeze(root, cid, by="plan:fixture", authority="plan")[0]
    before = path.read_bytes()
    refused, message = add.gate(root, cid, "RISK-ACCEPTED", by="plan:fixture",
                                reason="an open risk remains")
    assert refused is None and "R:OLDSEAL" in message
    assert path.read_bytes() == before, "an old receipt entitled a closing gate after refreeze"


def test_reopened_direction_needs_a_new_freeze(tmp_path):
    root, cid, path = _frozen(tmp_path)
    node = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(node['raw'], 'status', 'done')}\n---\n{node['body']}")
    assert add.reopen(root, cid, to="direction", reason="new decision required")[0]
    assert add._beat_of(add.scan(root)[cid]) == "direction"
    digest, message = add.brief_stamp(root, cid)
    assert digest is None and "R:OLDSEAL" in message
    assert add.freeze(root, cid, by="plan:fixture", authority="plan")[0]
    assert add._beat_of(add.scan(root)[cid]) == "build"


def test_repair_cause_is_a_readable_one_line_stamp(tmp_path):
    root, cid, path = _frozen(tmp_path)
    old_count = len(_stamps(path))
    node, note = add.repair(root, cid, kind="implementation",
                            cause='token } "quoted"\nfailed')
    assert node, note
    stamps = _stamps(path)
    assert len(stamps) == old_count + 1
    assert stamps[-1]["act"] == "repair"
    assert "quoted" in stamps[-1]["cause"] and "failed" in stamps[-1]["cause"]
