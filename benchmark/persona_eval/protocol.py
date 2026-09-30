"""Validation for a prospectively frozen persona evaluation protocol."""
from __future__ import annotations

import json
from typing import Any

from ._common import (
    canonical_sha256,
    canonical_json,
    exact_mapping,
    finite_number,
    integer,
    nonblank,
    refuse,
    string_list,
)


SCHEMA = "add.persona-eval-protocol/1"

_KEYS = frozenset(
    {
        "schema",
        "campaign_id",
        "repository_revision",
        "add_version",
        "add_revision",
        "corpus_version",
        "corpus_digest",
        "model_id",
        "model_family",
        "effort",
        "runner_digest",
        "environment_digest",
        "tool_allowlist",
        "prompt_template_digest",
        "token_ceiling",
        "turn_ceiling",
        "wall_time_ceiling_seconds",
        "per_cell_cost_ceiling_usd",
        "aggregate_cost_cap_usd",
        "repetitions",
        "allocation_seed",
        "live_enabled",
        "stop_policy",
    }
)
_STRING_KEYS = _KEYS - {
    "tool_allowlist",
    "token_ceiling",
    "turn_ceiling",
    "wall_time_ceiling_seconds",
    "per_cell_cost_ceiling_usd",
    "aggregate_cost_cap_usd",
    "repetitions",
    "allocation_seed",
    "live_enabled",
}
_DIGEST_KEYS = frozenset(
    {
        "corpus_digest",
        "runner_digest",
        "environment_digest",
        "prompt_template_digest",
    }
)
_VALIDATED = object()


class Protocol(tuple):
    """An immutable protocol backed by a detached strict-JSON snapshot."""

    __slots__ = ()

    def __new__(
        cls, payload_json: str, *, _construction_token: object | None = None
    ) -> "Protocol":
        if _construction_token is not _VALIDATED:
            refuse("INVALID_PROTOCOL", "Protocol must be created by validate_protocol")
        return tuple.__new__(cls, (payload_json,))

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Protocol is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Protocol is immutable")

    def __getattr__(self, name: str) -> Any:
        if name in _KEYS:
            value = self.to_dict()[name]
            return tuple(value) if name == "tool_allowlist" else value
        raise AttributeError(name)

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self[0])


def validate_protocol(payload: dict[str, Any]) -> Protocol:
    """Validate and detach one exact ``add.persona-eval-protocol/1`` value."""

    data = exact_mapping(payload, "protocol", _KEYS, "INVALID_PROTOCOL")
    if data["schema"] != SCHEMA:
        refuse("INVALID_PROTOCOL", f"schema must be {SCHEMA!r}")

    for key in _STRING_KEYS:
        nonblank(data[key], key, "INVALID_PROTOCOL")
    for key in _DIGEST_KEYS:
        canonical_sha256(data[key], key, "INVALID_PROTOCOL")
    if data["stop_policy"] != "before_next_cell":
        refuse("INVALID_PROTOCOL", "stop_policy must be 'before_next_cell'")

    string_list(
        data["tool_allowlist"],
        "tool_allowlist",
        "INVALID_PROTOCOL",
        nonempty=True,
    )
    integer(data["token_ceiling"], "token_ceiling", "INVALID_PROTOCOL", minimum=1)
    integer(data["turn_ceiling"], "turn_ceiling", "INVALID_PROTOCOL", minimum=1)
    finite_number(
        data["wall_time_ceiling_seconds"],
        "wall_time_ceiling_seconds",
        "INVALID_PROTOCOL",
        strictly_positive=True,
    )
    per_cell = finite_number(
        data["per_cell_cost_ceiling_usd"],
        "per_cell_cost_ceiling_usd",
        "INVALID_PROTOCOL",
        minimum=0,
    )
    aggregate = finite_number(
        data["aggregate_cost_cap_usd"],
        "aggregate_cost_cap_usd",
        "INVALID_PROTOCOL",
        minimum=0,
    )
    if aggregate < per_cell:
        refuse(
            "INVALID_PROTOCOL",
            "aggregate_cost_cap_usd cannot reserve one worst-case cell",
        )
    integer(data["repetitions"], "repetitions", "INVALID_PROTOCOL", minimum=1)
    integer(
        data["allocation_seed"],
        "allocation_seed",
        "INVALID_PROTOCOL",
        minimum=0,
    )
    if type(data["live_enabled"]) is not bool:
        refuse("INVALID_PROTOCOL", "live_enabled must be an explicit boolean")

    return Protocol(canonical_json(data, "INVALID_PROTOCOL"), _construction_token=_VALIDATED)
