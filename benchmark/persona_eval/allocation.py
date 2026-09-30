"""Seeded, balanced allocation of frozen persona-evaluation cells."""
from __future__ import annotations

import hashlib
import hmac
import random
import secrets
from dataclasses import dataclass, field, fields, replace as dataclass_replace
from typing import Any

from ._common import refuse, sha256_json, sha256_text
from .corpus import Corpus, CorpusCase
from .protocol import Protocol


CONDITIONS = ("neutral", "routed_correct", "plausible_wrong")
_ALLOCATION_AUTHORITY = secrets.token_bytes(32)


@dataclass(frozen=True, slots=True)
class TrialCell:
    """One immutable, fully pinned task/repetition/condition cell."""

    cell_id: str
    campaign_id: str
    corpus_version: str
    corpus_digest: str
    task_id: str
    repetition: int
    condition: str
    acceptable_personas: tuple[str, ...]
    plausible_wrong_persona: str
    no_fit: bool
    persona_id: str | None
    persona_digest: str | None
    persona_injection_digest: str
    effective_prompt_digest: str
    repository_revision: str
    add_version: str
    add_revision: str
    model_id: str
    model_family: str
    effort: str
    runner_digest: str
    environment_digest: str
    tool_allowlist: tuple[str, ...]
    prompt_template_digest: str
    token_ceiling: int
    turn_ceiling: int
    wall_time_ceiling_seconds: float
    per_cell_cost_ceiling_usd: float
    aggregate_cost_cap_usd: float
    live_enabled: bool
    stop_policy: str
    case_prompt_digest: str
    workspace_digest: str
    oracle_digest: str
    rubric_digest: str
    agent_visible_paths: tuple[str, ...]
    pin_manifest_digest: str
    _protocol_digest: str = field(repr=False, compare=False)
    _campaign_manifest_digest: str = field(repr=False, compare=False)
    _allocation_proof: str = field(repr=False, compare=False)

    def replace(self, **changes: Any) -> "TrialCell":
        """Return an immutable copy, used by drift probes and harness clients."""

        aliases = {
            "cost_ceiling": "per_cell_cost_ceiling_usd",
            "wall_time_ceiling": "wall_time_ceiling_seconds",
        }
        normalized = {aliases.get(key, key): value for key, value in changes.items()}
        return dataclass_replace(self, **normalized)

    def to_dict(self) -> dict[str, Any]:
        value = {
            item.name: getattr(self, item.name)
            for item in fields(self)
            if not item.name.startswith("_")
        }
        value["tool_allowlist"] = list(self.tool_allowlist)
        value["agent_visible_paths"] = list(self.agent_visible_paths)
        value["acceptable_personas"] = list(self.acceptable_personas)
        return value

    @property
    def campaign_manifest_digest(self) -> str:
        """Digest of the frozen protocol (except order seed) and exact matrix."""

        return self._campaign_manifest_digest

    @property
    def protocol_manifest_digest(self) -> str:
        """Digest of every frozen protocol field, including execution-order seed."""

        return self._protocol_digest


def _selected_persona(
    *,
    task_id: str,
    repetition: int,
    condition: str,
    acceptable_personas: tuple[str, ...],
    plausible_wrong_persona: str,
    no_fit: bool,
) -> str | None:
    if condition == "neutral":
        return None
    if condition == "plausible_wrong":
        return plausible_wrong_persona
    if no_fit:
        return None
    acceptable = tuple(sorted(acceptable_personas))
    selector = sha256_text(task_id, str(repetition), "routed_correct")
    index = int(selector.removeprefix("sha256:"), 16) % len(acceptable)
    return acceptable[index]


def _persona_for(case: CorpusCase, repetition: int, condition: str) -> str | None:
    return _selected_persona(
        task_id=case.id,
        repetition=repetition,
        condition=condition,
        acceptable_personas=case.acceptable_personas,
        plausible_wrong_persona=case.plausible_wrong_persona,
        no_fit=case.no_fit,
    )


def _manifest_payload(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if key not in {"cell_id", "pin_manifest_digest"} and not key.startswith("_")
    }


def _pin_manifest_digest(value: dict[str, Any]) -> str:
    return sha256_json(_manifest_payload(value), "PROVENANCE_DRIFT")


def _cell_id(pin_manifest_digest: str) -> str:
    return "cell-" + sha256_text("trial-cell", pin_manifest_digest).removeprefix("sha256:")[:24]


def _cell(protocol: Protocol, corpus: Corpus, case: CorpusCase, repetition: int, condition: str) -> TrialCell:
    persona_id = _persona_for(case, repetition, condition)
    persona_digest = sha256_text("persona", persona_id) if persona_id is not None else None
    injection_digest = (
        sha256_text("persona-injection", persona_id, persona_digest)
        if persona_id is not None
        else sha256_text("persona-injection", "none")
    )
    effective_prompt_digest = sha256_text(
        protocol.prompt_template_digest,
        case.prompt_digest,
        injection_digest,
    )
    values: dict[str, Any] = dict(
        cell_id="",
        campaign_id=protocol.campaign_id,
        corpus_version=corpus.version,
        corpus_digest=corpus.digest,
        task_id=case.id,
        repetition=repetition,
        condition=condition,
        acceptable_personas=tuple(sorted(case.acceptable_personas)),
        plausible_wrong_persona=case.plausible_wrong_persona,
        no_fit=case.no_fit,
        persona_id=persona_id,
        persona_digest=persona_digest,
        persona_injection_digest=injection_digest,
        effective_prompt_digest=effective_prompt_digest,
        repository_revision=protocol.repository_revision,
        add_version=protocol.add_version,
        add_revision=protocol.add_revision,
        model_id=protocol.model_id,
        model_family=protocol.model_family,
        effort=protocol.effort,
        runner_digest=protocol.runner_digest,
        environment_digest=protocol.environment_digest,
        tool_allowlist=protocol.tool_allowlist,
        prompt_template_digest=protocol.prompt_template_digest,
        token_ceiling=protocol.token_ceiling,
        turn_ceiling=protocol.turn_ceiling,
        wall_time_ceiling_seconds=float(protocol.wall_time_ceiling_seconds),
        per_cell_cost_ceiling_usd=float(protocol.per_cell_cost_ceiling_usd),
        aggregate_cost_cap_usd=float(protocol.aggregate_cost_cap_usd),
        live_enabled=protocol.live_enabled,
        stop_policy=protocol.stop_policy,
        case_prompt_digest=case.prompt_digest,
        workspace_digest=case.workspace_digest,
        oracle_digest=case.oracle_digest,
        rubric_digest=case.rubric_digest,
        agent_visible_paths=case.agent_visible_paths,
        pin_manifest_digest="",
        _protocol_digest="",
        _campaign_manifest_digest="",
        _allocation_proof="",
    )
    values["pin_manifest_digest"] = _pin_manifest_digest(values)
    values["cell_id"] = _cell_id(values["pin_manifest_digest"])
    return TrialCell(**values)


def _protocol_digest(protocol: Protocol) -> str:
    return sha256_json(protocol.to_dict(), "PROVENANCE_DRIFT")


def _campaign_manifest_digest(
    protocol: Protocol,
    corpus: Corpus,
    cells: list[TrialCell] | tuple[TrialCell, ...],
) -> str:
    protocol_payload = protocol.to_dict()
    protocol_payload.pop("allocation_seed")
    membership = sorted(
        (cell.cell_id, cell.pin_manifest_digest)
        for cell in cells
    )
    return sha256_json(
        {
            "protocol": protocol_payload,
            "corpus_digest": corpus.digest,
            "allocation": membership,
        },
        "PROVENANCE_DRIFT",
    )


def _allocation_proof(cell: TrialCell) -> str:
    message = sha256_json(
        {
            "cell": cell.to_dict(),
            "protocol_digest": cell._protocol_digest,
            "campaign_manifest_digest": cell._campaign_manifest_digest,
        },
        "PROVENANCE_DRIFT",
    ).encode("utf-8")
    return hmac.new(_ALLOCATION_AUTHORITY, message, hashlib.sha256).hexdigest()


def validate_trial_cell(cell: TrialCell) -> None:
    """Validate intrinsic condition semantics and every identity-bound pin."""

    if not isinstance(cell, TrialCell):
        refuse("PROVENANCE_DRIFT", "value is not an allocated TrialCell")
    if cell.condition not in CONDITIONS:
        refuse("CONDITION_DRIFT", "cell has an unsupported condition")
    if cell.repetition < 1:
        refuse("PROVENANCE_DRIFT", "cell repetition must be positive")
    if cell.no_fit != (not cell.acceptable_personas):
        refuse("CONDITION_DRIFT", "cell no-fit and acceptable-persona pins disagree")
    if cell.plausible_wrong_persona in cell.acceptable_personas:
        refuse("CONDITION_DRIFT", "wrong persona overlaps the acceptable set")
    expected_persona = _selected_persona(
        task_id=cell.task_id,
        repetition=cell.repetition,
        condition=cell.condition,
        acceptable_personas=cell.acceptable_personas,
        plausible_wrong_persona=cell.plausible_wrong_persona,
        no_fit=cell.no_fit,
    )
    if cell.persona_id != expected_persona:
        refuse("CONDITION_DRIFT", "cell persona does not match its frozen condition")
    expected_persona_digest = (
        sha256_text("persona", expected_persona) if expected_persona is not None else None
    )
    if cell.persona_digest != expected_persona_digest:
        refuse("PROVENANCE_DRIFT", "cell persona digest is inconsistent")
    expected_injection = (
        sha256_text("persona-injection", expected_persona, expected_persona_digest)
        if expected_persona is not None
        else sha256_text("persona-injection", "none")
    )
    if cell.persona_injection_digest != expected_injection:
        refuse("PROVENANCE_DRIFT", "cell persona injection digest is inconsistent")
    expected_prompt = sha256_text(
        cell.prompt_template_digest,
        cell.case_prompt_digest,
        expected_injection,
    )
    if cell.effective_prompt_digest != expected_prompt:
        refuse("PROVENANCE_DRIFT", "cell effective prompt digest is inconsistent")
    cell_dict = cell.to_dict()
    expected_manifest = _pin_manifest_digest(cell_dict)
    if cell.pin_manifest_digest != expected_manifest:
        refuse("PROVENANCE_DRIFT", "cell pin manifest differs from its frozen fields")
    if cell.cell_id != _cell_id(expected_manifest):
        refuse("PROVENANCE_DRIFT", "cell identity differs from its frozen pin manifest")
    if not cell._protocol_digest or not cell._campaign_manifest_digest:
        refuse("PROVENANCE_DRIFT", "cell lacks allocation authority")
    expected_proof = _allocation_proof(cell)
    if not hmac.compare_digest(cell._allocation_proof, expected_proof):
        refuse("PROVENANCE_DRIFT", "cell is not a member of its issued allocation")


def allocate(protocol: Protocol, corpus: Corpus) -> tuple[TrialCell, ...]:
    """Allocate the complete matrix, then permute execution order by seed."""

    if not isinstance(protocol, Protocol):
        refuse("INVALID_PROTOCOL", "allocate requires a validated Protocol")
    if not isinstance(corpus, Corpus):
        refuse("INVALID_CORPUS", "allocate requires a validated Corpus")
    if protocol.corpus_version != corpus.version or protocol.corpus_digest != corpus.digest:
        refuse("PROVENANCE_DRIFT", "protocol corpus pins do not match the corpus")

    cells = [
        _cell(protocol, corpus, case, repetition, condition)
        for case in corpus.cases
        for repetition in range(1, protocol.repetitions + 1)
        for condition in CONDITIONS
    ]
    protocol_digest = _protocol_digest(protocol)
    campaign_digest = _campaign_manifest_digest(protocol, corpus, cells)
    cells = [
        dataclass_replace(
            cell,
            _protocol_digest=protocol_digest,
            _campaign_manifest_digest=campaign_digest,
            _allocation_proof="",
        )
        for cell in cells
    ]
    cells = [
        dataclass_replace(cell, _allocation_proof=_allocation_proof(cell))
        for cell in cells
    ]
    assert_condition_balance(cells)
    random.Random(protocol.allocation_seed).shuffle(cells)
    return tuple(cells)


def validate_allocation_authority(
    protocol: Protocol,
    corpus: Corpus,
    cells: list[TrialCell] | tuple[TrialCell, ...],
) -> tuple[TrialCell, ...]:
    """Bind caller-supplied cells to the exact issued protocol and membership."""

    issued = tuple(cells)
    expected = allocate(protocol, corpus)
    if len(issued) != len(expected):
        refuse("UNBALANCED_MATRIX", "allocation size differs from the frozen campaign")
    expected_by_id = {cell.cell_id: cell for cell in expected}
    if len(expected_by_id) != len(expected):
        refuse("UNBALANCED_MATRIX", "frozen allocation contains duplicate identities")
    seen: set[str] = set()
    for cell in issued:
        validate_trial_cell(cell)
        if cell.cell_id in seen:
            refuse("UNBALANCED_MATRIX", "allocation contains a duplicate cell")
        seen.add(cell.cell_id)
        frozen = expected_by_id.get(cell.cell_id)
        if frozen is None or cell != frozen:
            refuse("UNBALANCED_MATRIX", "allocation membership differs from the frozen campaign")
        if (
            cell._protocol_digest != frozen._protocol_digest
            or cell._campaign_manifest_digest != frozen._campaign_manifest_digest
            or not hmac.compare_digest(cell._allocation_proof, frozen._allocation_proof)
        ):
            refuse("PROVENANCE_DRIFT", "allocation authority belongs to another protocol")
    return expected


_CONDITION_FIELDS = frozenset(
    {
        "cell_id",
        "condition",
        "persona_id",
        "persona_digest",
        "persona_injection_digest",
        "effective_prompt_digest",
        "pin_manifest_digest",
    }
)


def assert_condition_balance(cells: list[TrialCell] | tuple[TrialCell, ...]) -> None:
    """Refuse missing/duplicate conditions and any non-persona block drift."""

    if not cells:
        refuse("UNBALANCED_MATRIX", "the allocation is empty")
    groups: dict[tuple[str, int], list[TrialCell]] = {}
    ids: set[str] = set()
    for cell in cells:
        if not isinstance(cell, TrialCell):
            refuse("UNBALANCED_MATRIX", "allocation contains a non-TrialCell value")
        if cell.cell_id in ids:
            refuse("UNBALANCED_MATRIX", f"duplicate cell id {cell.cell_id!r}")
        ids.add(cell.cell_id)
        groups.setdefault((cell.task_id, cell.repetition), []).append(cell)

    expected = set(CONDITIONS)
    for block, block_cells in groups.items():
        if len(block_cells) != len(CONDITIONS) or {cell.condition for cell in block_cells} != expected:
            refuse("UNBALANCED_MATRIX", f"block {block!r} lacks exactly one of each condition")
        baseline = block_cells[0].to_dict()
        for cell in block_cells[1:]:
            candidate = cell.to_dict()
            for field, expected_value in baseline.items():
                if field not in _CONDITION_FIELDS and candidate[field] != expected_value:
                    refuse("CONDITION_DRIFT", f"{field} differs inside block {block!r}")
        for cell in block_cells:
            validate_trial_cell(cell)
