"""Strict, immutable records for bounded external evaluation claims."""
from __future__ import annotations

import json
import math
import re
import unicodedata
from typing import Any


SCHEMA = "add.eval-trial/1"

_TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "trial_id",
        "layer",
        "claim_scope",
        "repository",
        "add",
        "task",
        "actor",
        "prompt",
        "independence",
        "environment",
        "outcome",
        "evidence",
        "cost",
        "repair",
        "participant",
    }
)
_LAYER_CLAIMS = {
    "mechanism": "implementation_semantics",
    "model": "model_effectiveness",
    "human_governance": "governance_decision_quality",
}
_ROLES = frozenset({"builder", "refuter", "advisor"})
_INDEPENDENCE = frozenset(
    {
        "same_session",
        "fresh_session",
        "different_model_family",
        "human",
        "protected_ci",
    }
)
_PARTICIPANT_TOKEN = re.compile(r"participant:[0-9a-f]{32}\Z")
_VALIDATED_CONSTRUCTION = object()


class TrialRecordError(ValueError):
    """Raised when an external evaluation-trial record is invalid."""


def _invalid(message: str) -> None:
    raise TrialRecordError(f"invalid_trial_record: {message}")


def _mapping(value: Any, field: str, expected: frozenset[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _invalid(f"{field} must be an object")

    keys = list(value.keys())
    if any(not isinstance(key, str) for key in keys):
        _invalid(f"{field} keys must be strings")

    actual = frozenset(keys)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        _invalid(f"{field} keys differ (missing={missing}, unknown={unknown})")
    return value


def _nonblank_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _invalid(f"{field} must be a nonblank string")
    if any(unicodedata.category(character).startswith("C") for character in value):
        _invalid(f"{field} must contain machine-readable UTF-8 text")
    try:
        value.encode("utf-8")
    except UnicodeError:
        _invalid(f"{field} must contain machine-readable UTF-8 text")
    return value


def _choice(value: Any, field: str, allowed: frozenset[str]) -> str:
    value = _nonblank_string(value, field)
    if value not in allowed:
        _invalid(f"{field} has an unsupported value")
    return value


def _integer_counter(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _invalid(f"{field} must be a non-negative integer")


def _numeric_counter(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _invalid(f"{field} must be a finite non-negative number")
    if isinstance(value, float) and not math.isfinite(value):
        _invalid(f"{field} must be a finite non-negative number")
    if value < 0:
        _invalid(f"{field} must be a finite non-negative number")


def _references(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        _invalid(f"{field} must be a list")
    for index, reference in enumerate(value):
        _nonblank_string(reference, f"{field}[{index}]")
    return value


def _optional_named_object(
    value: Any, field: str, expected: frozenset[str]
) -> dict[str, Any] | None:
    if value is None:
        return None
    result = _mapping(value, field, expected)
    for key in expected:
        _nonblank_string(result[key], f"{field}.{key}")
    return result


class TrialRecord(tuple):
    """An immutable trial record backed by a detached strict-JSON snapshot."""

    __slots__ = ()

    def __new__(
        cls, payload_json: str, *, _construction_token: object | None = None
    ) -> TrialRecord:
        if _construction_token is not _VALIDATED_CONSTRUCTION:
            _invalid("TrialRecord must be created by validate_trial_record")
        return tuple.__new__(cls, (payload_json,))

    @property
    def _payload_json(self) -> str:
        return self[0]

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("TrialRecord is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("TrialRecord is immutable")

    def to_dict(self) -> dict[str, Any]:
        """Return a detached representation of the validated record."""

        return json.loads(self[0])


def validate_trial_record(record: dict[str, Any]) -> TrialRecord:
    """Validate and detach one ``add.eval-trial/1`` record."""

    record = _mapping(record, "record", _TOP_LEVEL_KEYS)

    if record["schema"] != SCHEMA:
        _invalid(f"schema must be {SCHEMA!r}")
    _nonblank_string(record["trial_id"], "trial_id")

    layer = _choice(record["layer"], "layer", frozenset(_LAYER_CLAIMS))
    claim_scope = _nonblank_string(record["claim_scope"], "claim_scope")
    if claim_scope != _LAYER_CLAIMS[layer]:
        _invalid("claim_scope exceeds the declared layer")

    repository = _mapping(
        record["repository"], "repository", frozenset({"revision"})
    )
    _nonblank_string(repository["revision"], "repository.revision")

    add = _mapping(record["add"], "add", frozenset({"version", "revision"}))
    _nonblank_string(add["version"], "add.version")
    _nonblank_string(add["revision"], "add.revision")

    task = _mapping(
        record["task"], "task", frozenset({"corpus_version", "id"})
    )
    _nonblank_string(task["corpus_version"], "task.corpus_version")
    _nonblank_string(task["id"], "task.id")

    actor = _mapping(
        record["actor"], "actor", frozenset({"role", "model", "persona"})
    )
    _choice(actor["role"], "actor.role", _ROLES)
    model = _optional_named_object(
        actor["model"], "actor.model", frozenset({"id", "family"})
    )
    persona = _optional_named_object(
        actor["persona"], "actor.persona", frozenset({"id", "digest"})
    )
    if layer != "model" and (model is not None or persona is not None):
        _invalid("model and persona attribution are allowed only for model trials")

    prompt = _mapping(
        record["prompt"], "prompt", frozenset({"digest", "brief_digest"})
    )
    _nonblank_string(prompt["digest"], "prompt.digest")
    _nonblank_string(prompt["brief_digest"], "prompt.brief_digest")

    _choice(record["independence"], "independence", _INDEPENDENCE)

    environment = _mapping(
        record["environment"], "environment", frozenset({"runner", "digest"})
    )
    _nonblank_string(environment["runner"], "environment.runner")
    _nonblank_string(environment["digest"], "environment.digest")

    outcome = _mapping(
        record["outcome"], "outcome", frozenset({"task", "gate", "refute"})
    )
    for key in ("task", "gate", "refute"):
        _nonblank_string(outcome[key], f"outcome.{key}")

    evidence = _mapping(
        record["evidence"],
        "evidence",
        frozenset({"test_receipts", "artifacts"}),
    )
    test_receipts = _references(evidence["test_receipts"], "evidence.test_receipts")
    artifacts = _references(evidence["artifacts"], "evidence.artifacts")
    if layer == "model" and model is None:
        _invalid("model trials require actor.model")
    if layer == "model" and not (test_receipts or artifacts):
        _invalid("model trials require an evidence reference")

    cost = _mapping(
        record["cost"],
        "cost",
        frozenset(
            {"turns", "tool_calls", "tokens", "wall_time_seconds", "cost_usd"}
        ),
    )
    for key in ("turns", "tool_calls", "tokens"):
        _integer_counter(cost[key], f"cost.{key}")
    for key in ("wall_time_seconds", "cost_usd"):
        _numeric_counter(cost[key], f"cost.{key}")

    repair = _mapping(
        record["repair"],
        "repair",
        frozenset(
            {
                "rounds",
                "contract_edits_after_first_freeze",
                "false_blockers",
                "severe_misses",
            }
        ),
    )
    for key in (
        "rounds",
        "contract_edits_after_first_freeze",
        "false_blockers",
        "severe_misses",
    ):
        _integer_counter(repair[key], f"repair.{key}")

    participant = record["participant"]
    if layer == "human_governance":
        participant = _mapping(
            participant, "participant", frozenset({"pseudonym"})
        )
        pseudonym = _nonblank_string(
            participant["pseudonym"], "participant.pseudonym"
        )
        if _PARTICIPANT_TOKEN.fullmatch(pseudonym) is None:
            _invalid("participant.pseudonym must be a harness-issued opaque token")
    elif participant is not None:
        _invalid("participant is allowed only for human_governance trials")

    try:
        payload_json = json.dumps(
            record,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        payload_json.encode("utf-8")
    except (TypeError, ValueError, OverflowError, UnicodeError) as exc:
        _invalid(f"record is not strict JSON: {exc}")
    return TrialRecord(payload_json, _construction_token=_VALIDATED_CONSTRUCTION)
