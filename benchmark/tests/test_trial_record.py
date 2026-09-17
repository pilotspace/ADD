"""Contract checks for the public external evaluation-trial record."""
from __future__ import annotations

from copy import deepcopy

import pytest

from benchmark.schema import trial_record


def _model_trial() -> dict:
    return {
        "schema": "add.eval-trial/1",
        "trial_id": "model-corpus-001",
        "layer": "model",
        "claim_scope": "model_effectiveness",
        "repository": {"revision": "git:repository-revision"},
        "add": {"version": "3.6.0", "revision": "git:add-revision"},
        "task": {"corpus_version": "heldout/1", "id": "repair-scope-001"},
        "actor": {
            "role": "builder",
            "model": {"id": "model-2026-09", "family": "example-family"},
            "persona": {"id": "method-steward", "digest": "sha256:persona"},
        },
        "prompt": {"digest": "sha256:prompt", "brief_digest": "sha256:brief"},
        "independence": "fresh_session",
        "environment": {"runner": "local-harness", "digest": "sha256:environment"},
        "outcome": {"task": "passed", "gate": "PASS", "refute": "none"},
        "evidence": {
            "test_receipts": ["runs/model-001.md"],
            "artifacts": ["artifacts/model-001.json"],
        },
        "cost": {
            "turns": 8,
            "tool_calls": 21,
            "tokens": 4000,
            "wall_time_seconds": 95,
            "cost_usd": 0.42,
        },
        "repair": {
            "rounds": 1,
            "contract_edits_after_first_freeze": 0,
            "false_blockers": 0,
            "severe_misses": 0,
        },
        "participant": None,
    }


def _rejected(payload) -> None:
    with pytest.raises(trial_record.TrialRecordError, match="invalid_trial_record"):
        trial_record.validate_trial_record(payload)


def test_trial_record_round_trips_versioned_model_trial():
    payload = _model_trial()
    record = trial_record.validate_trial_record(payload)

    assert record.to_dict() == payload
    assert record.__class__.__module__ == "benchmark.schema.trial_record"
    payload["task"]["id"] = "caller-mutated"
    detached = record.to_dict()
    detached["task"]["id"] = "result-mutated"
    assert record.to_dict()["task"]["id"] == "repair-scope-001"
    assert record._payload_json.encode("utf-8")
    with pytest.raises(trial_record.TrialRecordError, match="invalid_trial_record"):
        trial_record.TrialRecord("{}")
    with pytest.raises(AttributeError, match="immutable"):
        record._payload_json = "{}"
    with pytest.raises(AttributeError, match="immutable"):
        del record._payload_json
    with pytest.raises(AttributeError):
        object.__setattr__(record, "_payload_json", "{}")
    assert record.to_dict()["task"]["id"] == "repair-scope-001"


def test_trial_record_rejects_missing_provenance():
    cases = []
    missing = _model_trial()
    del missing["add"]["revision"]
    cases.append(missing)

    for path in (
        ("repository", "revision"),
        ("actor", "role"),
        ("prompt", "digest"),
        ("environment", "runner"),
    ):
        blank = _model_trial()
        blank[path[0]][path[1]] = "   "
        cases.append(blank)
    for hostile_text in (
        "\u200b",
        "\ufeff",
        "\u2060",
        "\x00",
        "\ud800",
        "git:revision\u200b",
    ):
        category_c = _model_trial()
        category_c["repository"]["revision"] = hostile_text
        cases.append(category_c)
    blank_reference = _model_trial()
    blank_reference["evidence"] = {"test_receipts": ["  "], "artifacts": []}
    cases.append(blank_reference)
    no_model = _model_trial()
    no_model["actor"]["model"] = None
    cases.append(no_model)
    no_evidence = _model_trial()
    no_evidence["evidence"] = {"test_receipts": [], "artifacts": []}
    cases.append(no_evidence)
    for value in (float("nan"), float("inf"), float("-inf")):
        non_finite = _model_trial()
        non_finite["cost"]["cost_usd"] = value
        cases.append(non_finite)
    mixed_keys = _model_trial()
    mixed_keys[1] = "not-a-string-key"
    cases.append(mixed_keys)

    for payload in cases:
        _rejected(payload)


def test_trial_record_enforces_layer_authority_and_participant_boundary():
    mechanism_overclaim = _model_trial()
    mechanism_overclaim["layer"] = "mechanism"
    mechanism_overclaim["claim_scope"] = "model_effectiveness"
    mechanism_overclaim["actor"]["model"] = None
    mechanism_overclaim["actor"]["persona"] = None
    mechanism_overclaim["independence"] = "protected_ci"

    human_without_participant = _model_trial()
    human_without_participant["layer"] = "human_governance"
    human_without_participant["claim_scope"] = "governance_decision_quality"
    human_without_participant["actor"]["model"] = None
    human_without_participant["actor"]["persona"] = None
    human_without_participant["independence"] = "human"
    human_without_participant["participant"] = None

    identity_looking_participant = deepcopy(human_without_participant)
    identity_looking_participant["participant"] = {"pseudonym": "alice@example.com"}
    non_human_with_participant = _model_trial()
    non_human_with_participant["participant"] = {
        "pseudonym": "participant:0123456789abcdef0123456789abcdef"
    }

    attributed_non_model = []
    for layer, claim_scope in (
        ("mechanism", "implementation_semantics"),
        ("human_governance", "governance_decision_quality"),
    ):
        for actor_field in ("model", "persona"):
            payload = _model_trial()
            payload["layer"] = layer
            payload["claim_scope"] = claim_scope
            payload["actor"]["model" if actor_field == "persona" else "persona"] = None
            if layer == "human_governance":
                payload["independence"] = "human"
                payload["participant"] = {
                    "pseudonym": "participant:0123456789abcdef0123456789abcdef"
                }
            attributed_non_model.append(payload)

    for payload in (
        mechanism_overclaim,
        human_without_participant,
        identity_looking_participant,
        non_human_with_participant,
        *attributed_non_model,
    ):
        _rejected(payload)

    valid_human = deepcopy(human_without_participant)
    valid_human["participant"] = {
        "pseudonym": "participant:0123456789abcdef0123456789abcdef"
    }
    assert trial_record.validate_trial_record(valid_human).to_dict() == valid_human


def test_trial_record_rejects_runrecord_v3_and_unknown_fields():
    legacy_run_record = {
        "arm": "add",
        "wm": 1,
        "rep": 0,
        "status": "done",
        "metrics": {"tokens_total": 4000},
        "artifacts": {},
    }
    unknown_top = _model_trial()
    unknown_top["metrics"] = {"productivity": 1}
    unknown_nested = _model_trial()
    unknown_nested["actor"]["authority"] = "human"

    for payload in (legacy_run_record, unknown_top, unknown_nested):
        _rejected(payload)
    assert not hasattr(trial_record, "RunRecord")
