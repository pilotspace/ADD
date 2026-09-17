"""RED contract fixtures for complete task-level, bounded-claim reports."""
from __future__ import annotations

import sys

import pytest


def _command() -> list[str]:
    return [sys.executable, "-c", "pass"]


def _grade() -> dict:
    return {
        "task": "passed",
        "severe_misses": 0,
        "false_blockers": 0,
        "rounds": 0,
        "contract_edits_after_first_freeze": 0,
        "test_receipts": ["held-out:report-fixture"],
        "artifacts": [],
    }


def test_report_preserves_missing_timeout_and_task_denominator():
    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.fixtures import example_campaign, example_observed_provenance
    from benchmark.persona_eval.protocol import validate_protocol
    from benchmark.persona_eval.report import summarize
    from benchmark.persona_eval.runner import run_cell
    protocol, corpus, cells, records = example_campaign(missing_one=True, timeout_one=True)
    report = summarize(protocol, corpus, cells, records)
    assert report.task_count == len({c.task_id for c in cells})
    assert report.repetition_count == protocol.to_dict()["repetitions"]
    assert {row.status for row in report.cells} >= {"missing", "timed_out"}

    cap_payload = protocol.to_dict()
    cap_payload["aggregate_cost_cap_usd"] = 1.0
    cap_payload["per_cell_cost_ceiling_usd"] = 1.0
    cap_protocol = validate_protocol(cap_payload)
    cap_cells = allocate(cap_protocol, corpus)
    records = [
        run_cell(
            cell,
            agent_cmd=_command(),
            observed_usage={"turns": 1, "tool_calls": 0, "tokens": 1, "cost_usd": 1.0},
            grader=lambda _: _grade(),
            **example_observed_provenance(cell),
        ).to_dict()
        for cell in cap_cells
    ]
    with pytest.raises(Exception, match="CAP_EXCEEDED"):
        summarize(cap_protocol, corpus, cap_cells, records)


def test_report_rejects_record_provenance_drift():
    import copy

    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.corpus import validate_corpus
    from benchmark.persona_eval.fixtures import example_campaign, example_observed_provenance
    from benchmark.persona_eval.protocol import validate_protocol
    from benchmark.persona_eval.report import summarize
    from benchmark.persona_eval.runner import CampaignBudget, run_cell
    protocol, corpus, cells, records = example_campaign()
    records[0]["prompt"]["digest"] = "sha256:" + "0" * 64
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, records)

    protocol, corpus, _, records = example_campaign()
    changed_protocol_payload = protocol.to_dict()
    changed_protocol_payload.update(
        effort="high", runner_digest="sha256:" + "1" * 64, tool_allowlist=["other-tool"]
    )
    changed_protocol = validate_protocol(changed_protocol_payload)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(changed_protocol, corpus, allocate(changed_protocol, corpus), records)

    changed_corpus_payload = corpus.to_dict()
    changed_corpus_payload["cases"][0].update(
        workspace_digest="sha256:" + "2" * 64,
        oracle_digest="sha256:" + "3" * 64,
        rubric_digest="sha256:" + "4" * 64,
    )
    changed_corpus = validate_corpus(changed_corpus_payload)
    changed_protocol_payload = protocol.to_dict()
    changed_protocol_payload["corpus_digest"] = changed_corpus.digest
    changed_protocol = validate_protocol(changed_protocol_payload)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(changed_protocol, changed_corpus, allocate(changed_protocol, changed_corpus), records)

    protocol, corpus, cells, records = example_campaign()
    expanded_payload = protocol.to_dict()
    expanded_payload["repetitions"] += 1
    expanded = validate_protocol(expanded_payload)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT|UNBALANCED_MATRIX"):
        summarize(expanded, corpus, allocate(expanded, corpus), records)

    reseeded_payload = protocol.to_dict()
    reseeded_payload["allocation_seed"] += 1
    reseeded = validate_protocol(reseeded_payload)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(reseeded, corpus, allocate(reseeded, corpus), records)

    stop_payload = protocol.to_dict()
    stop_payload["aggregate_cost_cap_usd"] = 1.0
    stop_payload["per_cell_cost_ceiling_usd"] = 1.0
    stop_protocol = validate_protocol(stop_payload)
    stop_cells = allocate(stop_protocol, corpus)
    ledger = CampaignBudget(stop_protocol, corpus, stop_cells)
    run_cell(
        stop_cells[0],
        agent_cmd=_command(),
        observed_usage={"turns": 1, "tool_calls": 0, "tokens": 1, "cost_usd": 1.0},
        grader=lambda _: _grade(),
        budget_ledger=ledger,
        **example_observed_provenance(stop_cells[0]),
    )
    with pytest.raises(Exception, match="CAP_EXCEEDED"):
        run_cell(
            stop_cells[1],
            agent_cmd=_command(),
            budget_ledger=ledger,
            **example_observed_provenance(stop_cells[1]),
        )
    reseeded_stop_payload = stop_protocol.to_dict()
    reseeded_stop_payload["allocation_seed"] += 1
    reseeded_stop = validate_protocol(reseeded_stop_payload)
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(
            reseeded_stop,
            corpus,
            allocate(reseeded_stop, corpus),
            [],
            stop_records=ledger.stop_records,
        )

    tampered = copy.deepcopy(records)
    target = next(cell for cell in cells if cell.cell_id == tampered[0]["trial_id"])
    tampered[0]["cost"]["turns"] = target.turn_ceiling + 1
    tampered[0]["cost"]["tokens"] = target.token_ceiling + 1
    tampered[0]["cost"]["wall_time_seconds"] = target.wall_time_ceiling_seconds + 1
    with pytest.raises(Exception, match="CAP_EXCEEDED|PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, tampered)

    protocol, corpus, cells, records = example_campaign()
    assert any(
        artifact.startswith("runner-attestation:hmac-sha256:")
        for artifact in records[0]["evidence"]["artifacts"]
    )
    mutated = copy.deepcopy(records)
    mutated[0]["repair"]["severe_misses"] += 1
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, mutated)

    fabricated = copy.deepcopy(records)
    fabricated[0]["evidence"]["artifacts"] = [
        artifact
        for artifact in fabricated[0]["evidence"]["artifacts"]
        if not artifact.startswith("runner-attestation:")
    ]
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, fabricated)

    evidence_stripped = copy.deepcopy(records)
    evidence_stripped[0]["evidence"]["test_receipts"] = []
    evidence_stripped[0]["evidence"]["artifacts"] = [
        artifact
        for artifact in evidence_stripped[0]["evidence"]["artifacts"]
        if not artifact.startswith("final-workspace:")
    ]
    with pytest.raises(Exception, match="PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, evidence_stripped)


def test_report_labels_fixtures_and_refuses_mixed_or_governance_claims():
    from benchmark.persona_eval.fixtures import example_campaign
    from benchmark.persona_eval.report import summarize
    protocol, corpus, cells, records = example_campaign(runner_kind="fixture")
    assert summarize(protocol, corpus, cells, records).claim_label == "fixture_only"
    records[-1]["environment"]["runner"] = "live"
    with pytest.raises(Exception, match="CLAIM_ESCALATION|PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, records)

    live_payload = protocol.to_dict()
    live_payload["live_enabled"] = True
    from benchmark.persona_eval.protocol import validate_protocol
    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.runner import run_cell
    from benchmark.persona_eval.fixtures import example_observed_provenance
    live_protocol = validate_protocol(live_payload)
    live_cells = allocate(live_protocol, corpus)
    with pytest.raises(Exception, match="CLAIM_ESCALATION"):
        run_cell(
            live_cells[0],
            agent_cmd=_command(),
            grader=lambda _: _grade(),
            runner_kind="live",
            **example_observed_provenance(live_cells[0]),
        )

    protocol, corpus, cells, records = example_campaign()
    records[0]["outcome"]["task"] = "routing rollout approved; permission granted"
    with pytest.raises(Exception, match="CLAIM_ESCALATION|PROVENANCE_DRIFT"):
        summarize(protocol, corpus, cells, records)
