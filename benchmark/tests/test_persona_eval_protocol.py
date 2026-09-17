"""RED contract fixtures for the prospective persona-evaluation protocol."""
from __future__ import annotations

import math

import pytest


def _payload() -> dict:
    digest = lambda label: "sha256:" + label.encode("utf-8").hex().ljust(64, "0")[:64]
    return {
        "schema": "add.persona-eval-protocol/1", "campaign_id": "pilot-1",
        "repository_revision": "git:repo", "add_version": "3.6.0",
        "add_revision": "git:add", "corpus_version": "persona-corpus/1",
        "corpus_digest": digest("corpus"), "model_id": "gpt-5.6",
        "model_family": "gpt-5", "effort": "medium",
        "runner_digest": digest("runner"), "environment_digest": digest("environment"),
        "tool_allowlist": ["shell"], "prompt_template_digest": digest("prompt"),
        "token_ceiling": 1000, "turn_ceiling": 8, "wall_time_ceiling_seconds": 300,
        "per_cell_cost_ceiling_usd": 1.0, "aggregate_cost_cap_usd": 24.0,
        "repetitions": 2, "allocation_seed": 7391, "live_enabled": False,
        "stop_policy": "before_next_cell",
    }


def test_protocol_is_strict_immutable_and_dry_run_first():
    from benchmark.persona_eval.protocol import validate_protocol
    payload = _payload()
    protocol = validate_protocol(payload)
    payload["model_id"] = "mutated"
    assert protocol.to_dict()["model_id"] == "gpt-5.6"
    assert protocol.to_dict()["live_enabled"] is False
    with pytest.raises(Exception, match="INVALID_PROTOCOL"):
        validate_protocol({**_payload(), "unknown": True})
    with pytest.raises(Exception, match="INVALID_PROTOCOL"):
        validate_protocol({**_payload(), "aggregate_cost_cap_usd": math.inf})
    for invalid_digest in (
        "sha256:short",
        "sha256:" + "A" * 64,
        "sha256:" + "g" * 64,
        "SHA256:" + "0" * 64,
    ):
        with pytest.raises(Exception, match="INVALID_PROTOCOL"):
            validate_protocol({**_payload(), "runner_digest": invalid_digest})


def test_protocol_rejects_live_default_and_incoherent_cap(tmp_path):
    import sys

    from benchmark.persona_eval.allocation import allocate
    from benchmark.persona_eval.fixtures import example_corpus, example_observed_provenance
    from benchmark.persona_eval.protocol import validate_protocol
    from benchmark.persona_eval.runner import CampaignBudget, run_cell
    live = {**_payload(), "live_enabled": True}
    del live["stop_policy"]
    with pytest.raises(Exception, match="INVALID_PROTOCOL"):
        validate_protocol(live)
    with pytest.raises(Exception, match="INVALID_PROTOCOL"):
        validate_protocol({**_payload(), "aggregate_cost_cap_usd": 0.5})

    live_protocol = validate_protocol({**_payload(), "live_enabled": True})
    corpus = example_corpus()
    rebound = live_protocol.to_dict()
    rebound["corpus_version"] = corpus.version
    rebound["corpus_digest"] = corpus.digest
    live_protocol = validate_protocol(rebound)
    cells = allocate(live_protocol, corpus)
    marker = tmp_path / "local-command-ran"
    with pytest.raises(Exception, match="CLAIM_ESCALATION"):
        run_cell(
            cells[0],
            agent_cmd=[
                sys.executable,
                "-c",
                "from pathlib import Path; Path('local-command-ran').write_text('yes')",
            ],
            workspace=tmp_path,
            runner_kind="live",
            budget_ledger=CampaignBudget(live_protocol, corpus, cells),
            observed_usage={"turns": 1, "tool_calls": 0, "tokens": 1, "cost_usd": 0.0},
            **example_observed_provenance(cells[0]),
        )
    assert not marker.exists()

    fixture_record = run_cell(
        cells[0],
        agent_cmd=[sys.executable, "-c", "pass"],
        grader=lambda _: {
            "task": "passed",
            "severe_misses": 0,
            "false_blockers": 0,
            "rounds": 0,
            "contract_edits_after_first_freeze": 0,
            "test_receipts": ["held-out:protocol-fixture"],
            "artifacts": [],
        },
        **example_observed_provenance(cells[0]),
    )
    assert fixture_record.to_dict()["layer"] == "mechanism"
    assert fixture_record.to_dict()["claim_scope"] == "implementation_semantics"
