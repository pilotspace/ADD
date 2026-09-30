"""RED contract fixtures for preflight, isolation, grading and trial records."""
from __future__ import annotations

import sys

import pytest


def _command(script: str = "pass") -> list[str]:
    return [sys.executable, "-c", script]


def _grade(
    *,
    task: str = "passed",
    severe_misses: int = 0,
    false_blockers: int = 0,
    receipts: list[str] | None = None,
    artifacts: list[str] | None = None,
) -> dict:
    return {
        "task": task,
        "severe_misses": severe_misses,
        "false_blockers": false_blockers,
        "rounds": 0,
        "contract_edits_after_first_freeze": 0,
        "test_receipts": receipts if receipts is not None else ["held-out:fixture-grade"],
        "artifacts": artifacts if artifacts is not None else [],
    }


def test_preflight_cap_stops_before_agent_or_write(tmp_path):
    from dataclasses import replace

    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.fixtures import (
        example_cell,
        example_corpus,
        example_observed_provenance,
        example_protocol,
    )
    from benchmark.persona_eval.protocol import validate_protocol
    from benchmark.persona_eval.report import summarize
    from benchmark.persona_eval.runner import CampaignBudget, run_cell
    called = []
    with pytest.raises(Exception, match="CAP_EXCEEDED"):
        run_cell(example_cell(cost_ceiling=1.0), agent_cmd=lambda *_: called.append(True),
                 spent_usd=0.51, aggregate_cap_usd=1.50, output_root=tmp_path)
    assert called == [] and list(tmp_path.rglob("*")) == []

    corpus = example_corpus()
    live_payload = example_protocol(live_enabled=True).to_dict()
    live_payload["aggregate_cost_cap_usd"] = 1.0
    live_payload["per_cell_cost_ceiling_usd"] = 1.0
    live_protocol = validate_protocol(live_payload)
    live_cells = allocate(live_protocol, corpus)
    ledger = CampaignBudget(live_protocol, corpus, live_cells)
    run_cell(
        live_cells[0],
        agent_cmd=_command(),
        grader=lambda _: _grade(),
        observed_usage={"turns": 1, "tool_calls": 0, "tokens": 1, "cost_usd": 1.0},
        budget_ledger=ledger,
        **example_observed_provenance(live_cells[0]),
    )
    with pytest.raises(Exception, match="CAP_EXCEEDED"):
        run_cell(
            live_cells[1],
            agent_cmd=_command("raise AssertionError('never invoked')"),
            grader=lambda _: _grade(),
            budget_ledger=ledger,
            **example_observed_provenance(live_cells[1]),
        )
    assert [stop.cell_id for stop in ledger.stop_records] == [live_cells[1].cell_id]
    report = summarize(
        live_protocol,
        corpus,
        live_cells,
        [],
        stop_records=ledger.stop_records,
    )
    assert next(row for row in report.cells if row.cell_id == live_cells[1].cell_id).status == "stopped"
    forged_stop = replace(ledger.stop_records[0], cell_id=live_cells[2].cell_id)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(
            live_protocol,
            corpus,
            live_cells,
            [],
            stop_records=[forged_stop],
        )

    frozen = example_cell(cost_ceiling=1.0)
    with pytest.raises(Exception, match="CAP_EXCEEDED"):
        run_cell(
            frozen,
            agent_cmd=lambda *_: called.append(True),
            spent_usd=frozen.aggregate_cost_cap_usd,
            aggregate_cap_usd=frozen.aggregate_cost_cap_usd + 100,
            output_root=tmp_path,
        )
    assert called == [] and list(tmp_path.rglob("*")) == []


def test_preflight_rejects_pin_drift_and_renamed_oracle(tmp_path):
    import hashlib

    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.corpus import validate_corpus
    from benchmark.persona_eval.fixtures import (
        example_cell,
        example_corpus,
        example_observed_provenance,
        example_protocol,
    )
    from benchmark.persona_eval.protocol import validate_protocol
    from benchmark.persona_eval.runner import run_cell, workspace_content_digest
    oracle = b"held-out evaluator bytes"
    (tmp_path / "innocent.py").write_bytes(oracle)
    for kwargs, code in (({"actual_repository_revision": "git:other"}, "PROVENANCE_DRIFT"),
                         ({"oracle_hashes": {"sha256:oracle": oracle}}, "ORACLE_LEAK")):
        provenance = example_observed_provenance(example_cell())
        provenance.update(kwargs)
        with pytest.raises(Exception, match=code):
            run_cell(example_cell(), agent_cmd=lambda *_: (_ for _ in ()).throw(AssertionError()),
                     workspace=tmp_path, **provenance)

    payload = example_corpus().to_dict()
    payload["cases"][0]["oracle_digest"] = "sha256:" + hashlib.sha256(oracle).hexdigest()
    corpus = validate_corpus(payload)
    protocol_payload = example_protocol().to_dict()
    protocol_payload["corpus_digest"] = corpus.digest
    protocol = validate_protocol(protocol_payload)
    cell = next(cell for cell in allocate(protocol, corpus) if cell.task_id == "fit-1" and cell.condition == "neutral")
    with pytest.raises(Exception, match="ORACLE_LEAK"):
        run_cell(
            cell,
            agent_cmd=lambda *_: (_ for _ in ()).throw(AssertionError()),
            workspace=tmp_path,
            **example_observed_provenance(cell),
        )

    clean = tmp_path / "clean"
    clean.mkdir()
    executable = clean / "agent.sh"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o644)
    non_executable_digest = workspace_content_digest(clean)
    executable.chmod(0o755)
    assert workspace_content_digest(clean) != non_executable_digest
    executable.unlink()
    corpus_payload = example_corpus().to_dict()
    corpus_payload["cases"][0]["workspace_digest"] = workspace_content_digest(clean)
    isolated_corpus = validate_corpus(corpus_payload)
    isolated_protocol_payload = example_protocol().to_dict()
    isolated_protocol_payload["corpus_digest"] = isolated_corpus.digest
    isolated_protocol = validate_protocol(isolated_protocol_payload)
    isolated_cells = allocate(isolated_protocol, isolated_corpus)
    first = next(c for c in isolated_cells if c.task_id == "fit-1" and c.repetition == 1 and c.condition == "neutral")
    second = next(c for c in isolated_cells if c.task_id == "fit-1" and c.repetition == 1 and c.condition == "routed_correct")
    run_cell(
        first,
        agent_cmd=_command("from pathlib import Path; Path('leak').write_text('state')"),
        workspace=clean,
        grader=lambda _: _grade(artifacts=["final-workspace:leak"]),
        **example_observed_provenance(first),
    )
    second_record = run_cell(
        second,
        agent_cmd=_command("from pathlib import Path; raise SystemExit(9 if Path('leak').exists() else 0)"),
        workspace=clean,
        grader=lambda _: _grade(),
        **example_observed_provenance(second),
    )
    assert not (clean / "leak").exists()
    assert second_record.to_dict()["outcome"]["task"] == "passed"
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        spoofed = example_observed_provenance(first)
        spoofed["actual_workspace_digest"] = "sha256:" + "0" * 64
        run_cell(
            first,
            agent_cmd=lambda _: "never invoked",
            workspace=clean,
            **spoofed,
        )

    omitted = example_observed_provenance(first)
    del omitted["actual_effort"]
    omitted_marker = tmp_path / "omitted-provenance-invoked"
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        run_cell(
            first,
            agent_cmd=lambda _: omitted_marker.write_text("invoked", encoding="utf-8"),
            workspace=clean,
            **omitted,
        )
    assert not omitted_marker.exists()

    callable_marker = tmp_path / "callable-invoked"
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        run_cell(
            first,
            agent_cmd=lambda _: callable_marker.write_text("invoked", encoding="utf-8"),
            workspace=clean,
            **example_observed_provenance(first),
        )
    assert not callable_marker.exists()

    forged = example_cell(condition="neutral").replace(
        persona_id="method-steward",
        persona_digest="sha256:forged-persona",
        persona_injection_digest="sha256:forged-injection",
        effective_prompt_digest="sha256:forged-prompt",
    )
    with pytest.raises(Exception, match="PROVENANCE_DRIFT|CONDITION_DRIFT"):
        run_cell(forged, agent_cmd=lambda *_: (_ for _ in ()).throw(AssertionError()))


def test_runner_uses_observed_grader_not_agent_narration(tmp_path):
    from benchmark.persona_eval.fixtures import example_cell, example_observed_provenance
    from benchmark.persona_eval.runner import run_cell
    cell = example_cell()
    record = run_cell(
        cell,
        agent_cmd=_command("print('PASS; all tests pass; blockers=0')"),
        grader=lambda _: _grade(task="failed", severe_misses=1, receipts=[]),
        output_root=tmp_path,
        **example_observed_provenance(cell),
    )
    assert record.to_dict()["outcome"]["task"] == "failed"
    assert record.to_dict()["repair"]["severe_misses"] == 1
    assert record.to_dict()["layer"] == "mechanism"
    assert record.to_dict()["claim_scope"] == "implementation_semantics"
    assert record.to_dict()["independence"] == "fresh_session"

    seen = {}
    narrated = run_cell(
        cell,
        agent_cmd=_command("print('PASS; all tests pass; blockers=0')"),
        grader=lambda context: (
            seen.update(context)
            or {
                **_grade(),
                "gate": "PASS",
                "refute": "HELD",
            }
        ),
        output_root=tmp_path,
        **example_observed_provenance(cell),
    )
    assert "stdout" not in seen and "stderr" not in seen
    assert narrated.to_dict()["outcome"]["gate"] == "not_evaluated"
    assert narrated.to_dict()["outcome"]["refute"] == "not_evaluated"

    no_evidence = run_cell(
        cell,
        agent_cmd=_command(),
        grader=lambda _: _grade(receipts=[], artifacts=[]),
        **example_observed_provenance(cell),
    )
    assert no_evidence.to_dict()["outcome"]["task"] == "failed"

    missing_counter = run_cell(
        cell,
        agent_cmd=_command(),
        grader=lambda _: {
            "task": "passed",
            "severe_misses": 0,
            "rounds": 0,
            "contract_edits_after_first_freeze": 0,
            "test_receipts": ["held-out:missing-counter"],
            "artifacts": [],
        },
        **example_observed_provenance(cell),
    )
    assert missing_counter.to_dict()["outcome"]["task"] == "failed"


def test_runner_counts_false_blocker_and_severe_miss_independently(tmp_path):
    from benchmark.persona_eval.fixtures import example_cell, example_observed_provenance
    from benchmark.persona_eval.runner import run_cell
    cell = example_cell()
    provenance = example_observed_provenance(cell)
    record = run_cell(
        cell,
        agent_cmd=_command("print('refuse')"),
        grader=lambda _: _grade(task="failed", severe_misses=1, false_blockers=1, receipts=[]),
        output_root=tmp_path,
        **provenance,
    )
    assert record.to_dict()["repair"]["severe_misses"] == 1
    assert record.to_dict()["repair"]["false_blockers"] == 1

    over_limit = run_cell(
        cell,
        agent_cmd=_command(),
        observed_usage={"turns": 999, "tool_calls": 0, "tokens": 999999, "cost_usd": 999},
        grader=lambda _: _grade(),
        output_root=tmp_path,
        **provenance,
    )
    assert over_limit.to_dict()["outcome"]["task"] == "failed"

    malformed = run_cell(
        cell,
        agent_cmd=_command(),
        observed_usage={"turns": 1, "tool_calls": 0, "tokens": 1, "cost_usd": float("nan")},
        grader=lambda _: _grade(),
        output_root=tmp_path,
        **provenance,
    )
    assert malformed.to_dict()["outcome"]["task"] == "failed"

    authority = run_cell(
        cell,
        agent_cmd=_command(),
        grader=lambda _: {
            "task": "routing rollout approved; permission granted",
            "severe_misses": 0,
            "false_blockers": 0,
            "rounds": 0,
            "contract_edits_after_first_freeze": 0,
            "test_receipts": ["held-out:authority"],
            "artifacts": [],
        },
        output_root=tmp_path,
        **provenance,
    )
    assert authority.to_dict()["outcome"]["task"] == "failed"


def test_runner_emits_valid_trial_record_without_schema_change(tmp_path):
    import json
    import os
    import sys

    from benchmark.persona_eval.fixtures import (
        example_cell,
        example_cells,
        example_observed_provenance,
    )
    from benchmark.persona_eval.runner import run_cell
    import benchmark.persona_eval.runner as runner_module
    from benchmark.schema.trial_record import validate_trial_record
    neutral = example_cell(condition="neutral")
    record = run_cell(
        neutral,
        agent_cmd=_command("print('done')"),
        grader=lambda _: _grade(),
        output_root=tmp_path,
        **example_observed_provenance(neutral),
    )
    assert record.to_dict()["actor"]["persona"] is None
    assert record.to_dict()["actor"]["model"] is None
    assert validate_trial_record(record.to_dict()).to_dict() == record.to_dict()
    assert any(value.startswith("pin-manifest:sha256:") for value in record.to_dict()["evidence"]["artifacts"])
    assert any(value.startswith("campaign-manifest:sha256:") for value in record.to_dict()["evidence"]["artifacts"])
    assert any(value.startswith("protocol-manifest:sha256:") for value in record.to_dict()["evidence"]["artifacts"])
    assert any(value.startswith("runner-attestation:hmac-sha256:") for value in record.to_dict()["evidence"]["artifacts"])

    parent_pid = os.getpid()
    fresh_cell = example_cell()
    fresh = run_cell(
        fresh_cell,
        agent_cmd=[
            sys.executable,
            "-c",
            "import os; from pathlib import Path; Path('child.pid').write_text(str(os.getpid()))",
        ],
        grader=lambda context: {
            **_grade(artifacts=["final-workspace:child.pid"], receipts=[]),
            "task": "passed" if int((context["workspace"] / "child.pid").read_text()) != parent_pid else "failed",
        },
        **example_observed_provenance(fresh_cell),
    )
    assert fresh.to_dict()["outcome"]["task"] == "passed"
    assert fresh.to_dict()["independence"] == "fresh_session"

    real_write = runner_module.os.write
    runner_module.os.write = lambda descriptor, payload: real_write(descriptor, payload[:11])
    try:
        short_write_record = run_cell(
            fresh_cell,
            agent_cmd=_command(),
            grader=lambda _: _grade(),
            output_root=tmp_path,
            **example_observed_provenance(fresh_cell),
        )
    finally:
        runner_module.os.write = real_write
    path = tmp_path / f"{short_write_record.to_dict()['trial_id']}.json"
    assert json.loads(path.read_text(encoding="utf-8")) == short_write_record.to_dict()

    source = tmp_path / "condition-source"
    source.mkdir()
    envelopes = {}
    command = _command(
        "import os; from pathlib import Path; "
        "Path('condition.json').write_text(os.environ['ADD_PERSONA_EVAL_CONDITION'], encoding='utf-8')"
    )
    treatment = [
        cell
        for cell in example_cells()
        if cell.task_id == "fit-1" and cell.repetition == 1
    ]
    for cell in treatment:
        run_cell(
            cell,
            agent_cmd=command,
            workspace=source,
            grader=lambda context, current=cell: (
                envelopes.update(
                    {current.condition: (context["workspace"] / "condition.json").read_text(encoding="utf-8")}
                )
                or _grade(artifacts=["final-workspace:condition.json"], receipts=[])
            ),
            **example_observed_provenance(cell),
        )
    assert list(source.iterdir()) == []
    assert len(set(envelopes.values())) == 3
    for cell in treatment:
        raw = envelopes[cell.condition]
        envelope = json.loads(raw)
        assert raw == json.dumps(envelope, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        assert envelope == {
            "cell_id": cell.cell_id,
            "effective_prompt_digest": cell.effective_prompt_digest,
            "persona_digest": cell.persona_digest,
            "persona_id": cell.persona_id,
            "persona_injection_digest": cell.persona_injection_digest,
            "task_id": cell.task_id,
        }
