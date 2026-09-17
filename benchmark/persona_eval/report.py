"""Complete-denominator, bounded-claim persona evaluation reports."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from benchmark.schema.trial_record import TrialRecord, validate_trial_record

from ._common import refuse
from .allocation import (
    TrialCell,
    assert_condition_balance,
    validate_allocation_authority,
)
from .corpus import Corpus
from .protocol import Protocol
from .runner import StopRecord, _validate_runner_attestation, validate_stop_record


_TASK_OUTCOMES = frozenset({"passed", "failed", "timed_out", "ungraded"})


@dataclass(frozen=True, slots=True)
class CellResult:
    cell_id: str
    task_id: str
    repetition: int
    condition: str
    status: str
    task_outcome: str | None
    severe_misses: int | None
    false_blockers: int | None
    repair_rounds: int | None
    cost_usd: float | None


@dataclass(frozen=True, slots=True)
class TaskResult:
    """All repeated paired conditions for one independent task."""

    task_id: str
    cells: tuple[CellResult, ...]


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """A descriptive report that carries no significance or governance claim."""

    claim_label: str
    task_count: int
    repetition_count: int
    cells: tuple[CellResult, ...]
    tasks: tuple[TaskResult, ...]
    significance_declared: bool = False
    governance_recommendation: None = None


def _record_dict(value: TrialRecord | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, TrialRecord):
        return value.to_dict()
    if not isinstance(value, dict):
        refuse("PROVENANCE_DRIFT", "records must be TrialRecord values or dictionaries")
    return validate_trial_record(value).to_dict()


def _verify_record(cell: TrialCell, record: dict[str, Any]) -> str:
    from .allocation import validate_trial_cell

    validate_trial_cell(cell)
    _validate_runner_attestation(record)
    if (
        record["layer"] != "mechanism"
        or record["claim_scope"] != "implementation_semantics"
    ):
        refuse(
            "CLAIM_ESCALATION",
            "model-effectiveness evidence requires a separately attested live evaluator",
        )
    if record["trial_id"] != cell.cell_id:
        refuse("PROVENANCE_DRIFT", "record trial_id does not match its allocated cell")
    checks = (
        (record["repository"]["revision"], cell.repository_revision, "repository revision"),
        (record["add"]["version"], cell.add_version, "ADD version"),
        (record["add"]["revision"], cell.add_revision, "ADD revision"),
        (record["task"]["corpus_version"], cell.corpus_version, "corpus version"),
        (record["task"]["id"], cell.task_id, "task id"),
        (record["actor"]["role"], "builder", "actor role"),
        (record["actor"]["model"], None, "model attribution"),
        (record["actor"]["persona"], None, "persona attribution"),
        (record["prompt"]["digest"], cell.effective_prompt_digest, "prompt digest"),
        (record["prompt"]["brief_digest"], cell.case_prompt_digest, "brief digest"),
        (record["environment"]["digest"], cell.environment_digest, "environment digest"),
    )
    for actual, expected, field in checks:
        if actual != expected:
            refuse("PROVENANCE_DRIFT", f"record {field} differs from the allocation")

    if record["participant"] is not None:
        refuse("CLAIM_ESCALATION", "fixture trials cannot become governance records")
    pin_artifacts = [
        artifact
        for artifact in record["evidence"]["artifacts"]
        if artifact.startswith("pin-manifest:")
    ]
    if pin_artifacts != [f"pin-manifest:{cell.pin_manifest_digest}"]:
        refuse("PROVENANCE_DRIFT", "record does not carry the exact allocated pin manifest")
    campaign_artifacts = [
        artifact
        for artifact in record["evidence"]["artifacts"]
        if artifact.startswith("campaign-manifest:")
    ]
    if campaign_artifacts != [f"campaign-manifest:{cell.campaign_manifest_digest}"]:
        refuse("PROVENANCE_DRIFT", "record does not carry the frozen campaign manifest")
    protocol_artifacts = [
        artifact
        for artifact in record["evidence"]["artifacts"]
        if artifact.startswith("protocol-manifest:")
    ]
    if protocol_artifacts != [f"protocol-manifest:{cell.protocol_manifest_digest}"]:
        refuse("PROVENANCE_DRIFT", "record does not carry the full frozen protocol manifest")
    if (
        record["cost"]["cost_usd"] > cell.per_cell_cost_ceiling_usd + 1e-12
        or record["cost"]["turns"] > cell.turn_ceiling
        or record["cost"]["tokens"] > cell.token_ceiling
        or record["cost"]["wall_time_seconds"] > cell.wall_time_ceiling_seconds + 1e-12
    ):
        refuse("CAP_EXCEEDED", "recorded usage exceeds a frozen cell ceiling")
    if record["outcome"]["task"] not in _TASK_OUTCOMES:
        refuse("CLAIM_ESCALATION", "record task outcome is outside the frozen vocabulary")
    if record["outcome"]["task"] == "passed":
        receipts = record["evidence"]["test_receipts"]
        artifacts = record["evidence"]["artifacts"]
        held_out = any(
            receipt.startswith("held-out:") and receipt.removeprefix("held-out:").strip()
            for receipt in receipts
        )
        final_workspace = any(
            artifact.startswith("final-workspace:")
            and artifact.removeprefix("final-workspace:").strip()
            for artifact in artifacts
        )
        if not held_out and not final_workspace:
            refuse(
                "PROVENANCE_DRIFT",
                "passed fixture record lacks held-out or final-workspace evidence",
            )
    runner = record["environment"]["runner"]
    if runner != "fixture":
        refuse("CLAIM_ESCALATION", "local records must remain fixture evidence")
    if record["independence"] != "fresh_session":
        refuse("PROVENANCE_DRIFT", "fixture record lacks fresh-session evidence")
    return runner


def _status(task_outcome: str) -> str:
    if task_outcome == "timed_out":
        return "timed_out"
    if task_outcome == "passed":
        return "completed"
    return "failed"


def summarize(
    protocol: Protocol,
    corpus: Corpus,
    cells: list[TrialCell] | tuple[TrialCell, ...],
    records: list[TrialRecord | dict[str, Any]] | tuple[TrialRecord | dict[str, Any], ...],
    *,
    stop_records: Sequence[StopRecord] = (),
) -> EvaluationReport:
    """Join every planned cell and retain missing/stopped outcomes in the denominator."""

    if not isinstance(protocol, Protocol):
        refuse("INVALID_PROTOCOL", "summarize requires a validated Protocol")
    if not isinstance(corpus, Corpus):
        refuse("INVALID_CORPUS", "summarize requires a validated Corpus")
    cells_tuple = tuple(cells)
    assert_condition_balance(cells_tuple)
    validate_allocation_authority(protocol, corpus, cells_tuple)

    cell_by_id = {cell.cell_id: cell for cell in cells_tuple}
    record_by_id: dict[str, dict[str, Any]] = {}
    runner_kinds: set[str] = set()
    for raw_record in records:
        record = _record_dict(raw_record)
        trial_id = record["trial_id"]
        if trial_id in record_by_id:
            refuse("DENOMINATOR_DRIFT", f"duplicate record for {trial_id!r}")
        cell = cell_by_id.get(trial_id)
        if cell is None:
            refuse("PROVENANCE_DRIFT", f"record {trial_id!r} is not in the frozen allocation")
        runner_kinds.add(_verify_record(cell, record))
        record_by_id[trial_id] = record

    stopped_by_id: dict[str, StopRecord] = {}
    for stop in stop_records:
        validate_stop_record(stop)
        cell = cell_by_id.get(stop.cell_id)
        if cell is None:
            refuse("PROVENANCE_DRIFT", "stop is not in the frozen allocation")
        if stop.campaign_manifest_digest != cell.campaign_manifest_digest:
            refuse("PROVENANCE_DRIFT", "stop belongs to another frozen campaign")
        if stop.protocol_manifest_digest != cell.protocol_manifest_digest:
            refuse("PROVENANCE_DRIFT", "stop belongs to another frozen protocol")
        if stop.cell_id in stopped_by_id or stop.cell_id in record_by_id:
            refuse("DENOMINATOR_DRIFT", "cell has duplicate or conflicting terminal evidence")
        if stop.code not in {"CAP_EXCEEDED", "PROVENANCE_DRIFT", "ORACLE_LEAK", "CLAIM_ESCALATION"}:
            refuse("PROVENANCE_DRIFT", "stop has an unsupported reason code")
        stopped_by_id[stop.cell_id] = stop

    if runner_kinds - {"fixture"}:
        refuse("CLAIM_ESCALATION", "this harness reports fixture evidence only")
    claim_label = "fixture_only"

    total_cost = sum(
        float(record["cost"]["cost_usd"]) for record in record_by_id.values()
    )
    if total_cost > protocol.aggregate_cost_cap_usd + 1e-12:
        refuse("CAP_EXCEEDED", "recorded campaign cost exceeds the frozen aggregate cap")

    rows: list[CellResult] = []
    for cell in cells_tuple:
        record = record_by_id.get(cell.cell_id)
        if record is None:
            stopped = stopped_by_id.get(cell.cell_id)
            rows.append(
                CellResult(
                    cell_id=cell.cell_id,
                    task_id=cell.task_id,
                    repetition=cell.repetition,
                    condition=cell.condition,
                    status="stopped" if stopped is not None else "missing",
                    task_outcome="stopped" if stopped is not None else None,
                    severe_misses=None,
                    false_blockers=None,
                    repair_rounds=None,
                    cost_usd=None,
                )
            )
            continue
        rows.append(
            CellResult(
                cell_id=cell.cell_id,
                task_id=cell.task_id,
                repetition=cell.repetition,
                condition=cell.condition,
                status=_status(record["outcome"]["task"]),
                task_outcome=record["outcome"]["task"],
                severe_misses=record["repair"]["severe_misses"],
                false_blockers=record["repair"]["false_blockers"],
                repair_rounds=record["repair"]["rounds"],
                cost_usd=float(record["cost"]["cost_usd"]),
            )
        )

    task_ids = sorted({cell.task_id for cell in cells_tuple})
    tasks = tuple(
        TaskResult(task_id=task_id, cells=tuple(row for row in rows if row.task_id == task_id))
        for task_id in task_ids
    )
    return EvaluationReport(
        claim_label=claim_label,
        task_count=len(task_ids),
        repetition_count=protocol.repetitions,
        cells=tuple(rows),
        tasks=tasks,
    )
