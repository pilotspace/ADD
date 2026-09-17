"""Strict evaluator-only corpus snapshots for persona trials."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from ._common import (
    canonical_sha256,
    canonical_json,
    exact_mapping,
    nonblank,
    refuse,
    sha256_json,
    string_list,
)


SCHEMA = "add.persona-eval-corpus/1"
_TOP_KEYS = frozenset({"schema", "version", "cases"})
_CASE_KEYS = frozenset(
    {
        "id",
        "prompt_digest",
        "workspace_digest",
        "oracle_digest",
        "rubric_digest",
        "acceptable_personas",
        "plausible_wrong_persona",
        "no_fit",
        "agent_visible_paths",
    }
)
_VALIDATED = object()


@dataclass(frozen=True, slots=True)
class CorpusCase:
    id: str
    prompt_digest: str
    workspace_digest: str
    oracle_digest: str
    rubric_digest: str
    acceptable_personas: tuple[str, ...]
    plausible_wrong_persona: str
    no_fit: bool
    agent_visible_paths: tuple[str, ...]


def _case_from_dict(value: dict[str, Any]) -> CorpusCase:
    return CorpusCase(
        id=value["id"],
        prompt_digest=value["prompt_digest"],
        workspace_digest=value["workspace_digest"],
        oracle_digest=value["oracle_digest"],
        rubric_digest=value["rubric_digest"],
        acceptable_personas=tuple(value["acceptable_personas"]),
        plausible_wrong_persona=value["plausible_wrong_persona"],
        no_fit=value["no_fit"],
        agent_visible_paths=tuple(value["agent_visible_paths"]),
    )


class Corpus(tuple):
    """An immutable, detached persona-evaluation corpus."""

    __slots__ = ()

    def __new__(
        cls, payload_json: str, *, _construction_token: object | None = None
    ) -> "Corpus":
        if _construction_token is not _VALIDATED:
            refuse("INVALID_CORPUS", "Corpus must be created by validate_corpus")
        return tuple.__new__(cls, (payload_json,))

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Corpus is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("Corpus is immutable")

    @property
    def schema(self) -> str:
        return self.to_dict()["schema"]

    @property
    def version(self) -> str:
        return self.to_dict()["version"]

    @property
    def cases(self) -> tuple[CorpusCase, ...]:
        return tuple(_case_from_dict(case) for case in self.to_dict()["cases"])

    @property
    def digest(self) -> str:
        return sha256_json(self.to_dict(), "INVALID_CORPUS")

    def case(self, case_id: str) -> CorpusCase:
        for case in self.cases:
            if case.id == case_id:
                return case
        raise KeyError(case_id)

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self[0])


def _path_exposes_evaluator_material(path: str) -> bool:
    parts = PurePosixPath(path.replace("\\", "/")).parts
    return any(
        "oracle" in part.casefold() or "rubric" in part.casefold()
        for part in parts
    )


def validate_corpus(payload: dict[str, Any]) -> Corpus:
    """Validate acceptable/wrong persona labels without exposing evaluator data."""

    data = exact_mapping(payload, "corpus", _TOP_KEYS, "INVALID_CORPUS")
    if data["schema"] != SCHEMA:
        refuse("INVALID_CORPUS", f"schema must be {SCHEMA!r}")
    nonblank(data["version"], "version", "INVALID_CORPUS")
    cases_value = data["cases"]
    if not isinstance(cases_value, list) or not cases_value:
        refuse("INVALID_CORPUS", "cases must be a non-empty list")

    seen_ids: set[str] = set()
    normalized_cases: list[dict[str, Any]] = []
    for index, raw_case in enumerate(cases_value):
        field = f"cases[{index}]"
        case = exact_mapping(raw_case, field, _CASE_KEYS, "INVALID_CORPUS")
        case_id = nonblank(case["id"], f"{field}.id", "INVALID_CORPUS")
        if case_id in seen_ids:
            refuse("INVALID_CORPUS", f"duplicate case id {case_id!r}")
        seen_ids.add(case_id)

        for key in (
            "prompt_digest",
            "workspace_digest",
            "oracle_digest",
            "rubric_digest",
        ):
            canonical_sha256(case[key], f"{field}.{key}", "INVALID_CORPUS")
        nonblank(
            case["plausible_wrong_persona"],
            f"{field}.plausible_wrong_persona",
            "INVALID_CORPUS",
        )
        acceptable = string_list(
            case["acceptable_personas"],
            f"{field}.acceptable_personas",
            "INVALID_CORPUS",
        )
        paths = string_list(
            case["agent_visible_paths"],
            f"{field}.agent_visible_paths",
            "INVALID_CORPUS",
            nonempty=True,
        )
        if type(case["no_fit"]) is not bool:
            refuse("INVALID_CORPUS", f"{field}.no_fit must be an explicit boolean")
        if case["no_fit"] and acceptable:
            refuse("INVALID_CORPUS", "a no-fit case must have an empty acceptable set")
        if not case["no_fit"] and not acceptable:
            refuse("INVALID_CORPUS", "a fitted case needs an acceptable persona")
        if case["plausible_wrong_persona"] in acceptable:
            refuse(
                "INVALID_CORPUS",
                "plausible_wrong_persona must be outside the acceptable set",
            )
        if any(_path_exposes_evaluator_material(path) for path in paths):
            refuse("ORACLE_LEAK", "an evaluator-only path is agent-visible")
        evaluator_digests = {case["oracle_digest"], case["rubric_digest"]}
        if case["prompt_digest"] in evaluator_digests or case["workspace_digest"] in evaluator_digests:
            refuse(
                "ORACLE_LEAK",
                "an agent-visible prompt or workspace digest matches evaluator material",
            )

        normalized = dict(case)
        # The contract calls this a set.  Canonicalize it so neither routing
        # nor the corpus digest depends on incidental authoring order.
        normalized["acceptable_personas"] = sorted(acceptable)
        normalized["agent_visible_paths"] = list(paths)
        normalized_cases.append(normalized)

    snapshot = {"schema": data["schema"], "version": data["version"], "cases": normalized_cases}
    return Corpus(canonical_json(snapshot, "INVALID_CORPUS"), _construction_token=_VALIDATED)
