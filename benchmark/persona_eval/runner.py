"""Fail-closed preflight and deterministic execution for one trial cell."""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import re
import shutil
import secrets
import stat
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from benchmark.schema.trial_record import TrialRecord, validate_trial_record

from ._common import (
    PersonaEvalError,
    canonical_json,
    finite_number,
    integer,
    refuse,
    sha256_json,
)
from .allocation import TrialCell, validate_allocation_authority, validate_trial_cell
from .corpus import Corpus
from .protocol import Protocol


_UNSET = object()
_PIN_ARTIFACT_PREFIX = "pin-manifest:"
_CAMPAIGN_ARTIFACT_PREFIX = "campaign-manifest:"
_PROTOCOL_ARTIFACT_PREFIX = "protocol-manifest:"
_RUNNER_ATTESTATION_PREFIX = "runner-attestation:hmac-sha256:"
_HELD_OUT_RECEIPT_PREFIX = "held-out:"
_FINAL_WORKSPACE_PREFIX = "final-workspace:"
_CONDITION_ENVIRONMENT_VARIABLE = "ADD_PERSONA_EVAL_CONDITION"
_USAGE_KEYS = frozenset({"turns", "tool_calls", "tokens", "cost_usd"})
_TASK_OUTCOMES = frozenset({"passed", "failed", "timed_out", "ungraded"})
_STOP_AUTHORITY = secrets.token_bytes(32)
_RUNNER_ATTESTATION_AUTHORITY = secrets.token_bytes(32)


@dataclass(frozen=True, slots=True)
class StopRecord:
    """A campaign-bound cell that was stopped before agent invocation."""

    cell_id: str
    campaign_manifest_digest: str
    protocol_manifest_digest: str
    code: str
    _proof: str = field(repr=False, compare=False)


def _stop_proof(
    cell_id: str,
    campaign_manifest_digest: str,
    protocol_manifest_digest: str,
    code: str,
) -> str:
    message = sha256_json(
        {
            "cell_id": cell_id,
            "campaign_manifest_digest": campaign_manifest_digest,
            "protocol_manifest_digest": protocol_manifest_digest,
            "code": code,
        },
        "PROVENANCE_DRIFT",
    ).encode("utf-8")
    return hmac.new(_STOP_AUTHORITY, message, hashlib.sha256).hexdigest()


def validate_stop_record(stop: StopRecord) -> None:
    if not isinstance(stop, StopRecord):
        refuse("DENOMINATOR_DRIFT", "stop_records must contain StopRecord values")
    expected = _stop_proof(
        stop.cell_id,
        stop.campaign_manifest_digest,
        stop.protocol_manifest_digest,
        stop.code,
    )
    if not hmac.compare_digest(stop._proof, expected):
        refuse("PROVENANCE_DRIFT", "stop record lacks campaign-ledger authority")


def workspace_content_digest(workspace: str | os.PathLike[str] | Path) -> str:
    """Hash normalized relative paths, entry kinds, and file bytes."""

    root = Path(workspace)
    if not root.exists() or not root.is_dir():
        refuse("PROVENANCE_DRIFT", "workspace must be an existing directory")
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda candidate: candidate.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            refuse("PROVENANCE_DRIFT", f"workspace symlink is not allowed: {relative}")
        mode = stat.S_IMODE(path.stat().st_mode)
        if path.is_dir():
            entries.append(
                {"path": relative, "kind": "directory", "mode": mode, "sha256": ""}
            )
            continue
        if not path.is_file():
            refuse("PROVENANCE_DRIFT", f"unsupported workspace entry: {relative}")
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            refuse("PROVENANCE_DRIFT", f"cannot inspect workspace file {relative}: {exc}")
        entries.append(
            {"path": relative, "kind": "file", "mode": mode, "sha256": digest}
        )
    return sha256_json(entries, "PROVENANCE_DRIFT")


EMPTY_WORKSPACE_DIGEST = sha256_json([], "PROVENANCE_DRIFT")


class CampaignBudget:
    """Thread-safe reservation ledger for one live frozen campaign."""

    def __init__(
        self,
        protocol: Protocol,
        corpus: Corpus,
        cells: Sequence[TrialCell],
    ) -> None:
        if not isinstance(protocol, Protocol):
            refuse("INVALID_PROTOCOL", "CampaignBudget requires a validated Protocol")
        if not isinstance(corpus, Corpus):
            refuse("INVALID_CORPUS", "CampaignBudget requires a validated Corpus")
        issued = tuple(cells)
        validate_allocation_authority(protocol, corpus, issued)
        self.campaign_id = protocol.campaign_id
        self.aggregate_cap_usd = float(protocol.aggregate_cost_cap_usd)
        self._protocol_digest = issued[0]._protocol_digest
        self._campaign_manifest_digest = issued[0].campaign_manifest_digest
        self._membership = {
            cell.cell_id: cell.pin_manifest_digest
            for cell in issued
        }
        self._spent_usd = 0.0
        self._reserved_usd = 0.0
        self._reservations: dict[object, tuple[str, float]] = {}
        self._attempted_cells: set[str] = set()
        self._stops: list[StopRecord] = []
        self._lock = threading.Lock()

    @property
    def spent_usd(self) -> float:
        with self._lock:
            return self._spent_usd

    @property
    def stop_records(self) -> tuple[StopRecord, ...]:
        with self._lock:
            return tuple(self._stops)

    def reserve(self, cell: TrialCell, runtime_cap_usd: float) -> object:
        validate_trial_cell(cell)
        if cell.campaign_id != self.campaign_id:
            refuse("PROVENANCE_DRIFT", "budget ledger belongs to another campaign")
        if (
            cell._protocol_digest != self._protocol_digest
            or cell.campaign_manifest_digest != self._campaign_manifest_digest
            or self._membership.get(cell.cell_id) != cell.pin_manifest_digest
        ):
            refuse("PROVENANCE_DRIFT", "cell is not in the ledger's frozen allocation")
        if abs(cell.aggregate_cost_cap_usd - self.aggregate_cap_usd) > 1e-12:
            refuse("PROVENANCE_DRIFT", "budget ledger cap differs from the frozen campaign")
        with self._lock:
            if cell.cell_id in self._attempted_cells:
                refuse("PROVENANCE_DRIFT", "a live cell cannot be invoked twice")
            prospective = self._spent_usd + self._reserved_usd + cell.per_cell_cost_ceiling_usd
            if prospective > runtime_cap_usd + 1e-12:
                if not any(stop.cell_id == cell.cell_id for stop in self._stops):
                    code = "CAP_EXCEEDED"
                    self._stops.append(
                        StopRecord(
                            cell_id=cell.cell_id,
                            campaign_manifest_digest=self._campaign_manifest_digest,
                            protocol_manifest_digest=self._protocol_digest,
                            code=code,
                            _proof=_stop_proof(
                                cell.cell_id,
                                self._campaign_manifest_digest,
                                self._protocol_digest,
                                code,
                            ),
                        )
                    )
                self._attempted_cells.add(cell.cell_id)
                refuse("CAP_EXCEEDED", "live reservation exceeds the remaining campaign cap")
            token = object()
            self._reservations[token] = (cell.cell_id, cell.per_cell_cost_ceiling_usd)
            self._reserved_usd += cell.per_cell_cost_ceiling_usd
            self._attempted_cells.add(cell.cell_id)
            return token

    def settle(self, token: object, cost_usd: float, *, invalid_output: bool = False) -> None:
        with self._lock:
            reservation = self._reservations.pop(token, None)
            if reservation is None:
                refuse("PROVENANCE_DRIFT", "unknown budget reservation")
            _, ceiling = reservation
            self._reserved_usd -= ceiling
            try:
                observed = finite_number(
                    cost_usd, "cost_usd", "NARRATED_OUTCOME", minimum=0
                )
            except PersonaEvalError:
                observed = ceiling
                invalid_output = True
            if observed > ceiling + 1e-12:
                invalid_output = True
            self._spent_usd += ceiling if invalid_output else observed


def _runtime_cap(
    cell: TrialCell,
    spent_usd: Any,
    aggregate_cap_usd: Any,
) -> tuple[float, float]:
    spent = finite_number(spent_usd, "spent_usd", "CAP_EXCEEDED", minimum=0)
    frozen = float(cell.aggregate_cost_cap_usd)
    if aggregate_cap_usd is None:
        runtime = frozen
    else:
        runtime = finite_number(
            aggregate_cap_usd, "aggregate_cap_usd", "CAP_EXCEEDED", minimum=0
        )
        if runtime > frozen + 1e-12:
            refuse("CAP_EXCEEDED", "runtime aggregate cap cannot raise the frozen cap")
    if spent + cell.per_cell_cost_ceiling_usd > runtime + 1e-12:
        refuse("CAP_EXCEEDED", "the next worst-case cell exceeds the remaining aggregate cap")
    return spent, runtime


def _expected_pins(cell: TrialCell) -> dict[str, Any]:
    return {
        "repository_revision": cell.repository_revision,
        "add_version": cell.add_version,
        "add_revision": cell.add_revision,
        "corpus_digest": cell.corpus_digest,
        "model_id": cell.model_id,
        "model_family": cell.model_family,
        "effort": cell.effort,
        "runner_digest": cell.runner_digest,
        "environment_digest": cell.environment_digest,
        "tool_allowlist": cell.tool_allowlist,
        "prompt_template_digest": cell.prompt_template_digest,
        "case_prompt_digest": cell.case_prompt_digest,
        "effective_prompt_digest": cell.effective_prompt_digest,
        "workspace_digest": cell.workspace_digest,
        "oracle_digest": cell.oracle_digest,
        "rubric_digest": cell.rubric_digest,
        "grader_digest": cell.rubric_digest,
        "persona_id": cell.persona_id,
        "persona_digest": cell.persona_digest,
        "pin_manifest_digest": cell.pin_manifest_digest,
    }


def _check_provenance(
    cell: TrialCell,
    actual: Mapping[str, Any],
    *,
    complete: bool,
) -> None:
    for key, expected_value in _expected_pins(cell).items():
        value = actual.get(key, _UNSET)
        if value is _UNSET:
            if complete:
                refuse("PROVENANCE_DRIFT", f"live execution omitted observed {key}")
            continue
        if key == "tool_allowlist" and value is not None:
            value = tuple(value)
        if value != expected_value:
            refuse("PROVENANCE_DRIFT", f"{key} differs from the frozen pin")


def _secret_hashes(cell: TrialCell, oracle_hashes: Mapping[str, Any] | None) -> set[str]:
    result = {cell.oracle_digest.casefold(), cell.rubric_digest.casefold()}
    for declared, material in (oracle_hashes or {}).items():
        if isinstance(declared, str):
            result.add(declared.casefold())
        if isinstance(material, (bytes, bytearray)):
            result.add("sha256:" + hashlib.sha256(bytes(material)).hexdigest())
        elif isinstance(material, str) and material.startswith("sha256:"):
            result.add(material.casefold())
    return result


def _check_workspace(
    cell: TrialCell,
    workspace: Path | None,
    oracle_hashes: Mapping[str, Any] | None,
) -> str:
    if workspace is None:
        digest = EMPTY_WORKSPACE_DIGEST
        if digest != cell.workspace_digest:
            refuse("PROVENANCE_DRIFT", "empty workspace differs from the frozen fixture")
        return digest
    secrets = _secret_hashes(cell, oracle_hashes)
    for path in workspace.rglob("*"):
        if path.is_symlink():
            refuse(
                "PROVENANCE_DRIFT",
                f"workspace symlink is not allowed: {path.relative_to(workspace)}",
            )
        if not path.is_file():
            continue
        relative = path.relative_to(workspace)
        if any(
            "oracle" in part.casefold() or "rubric" in part.casefold()
            for part in relative.parts
        ):
            refuse("ORACLE_LEAK", f"evaluator-only path is agent-visible: {relative}")
        try:
            digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            refuse("PROVENANCE_DRIFT", f"cannot inspect workspace file {relative}: {exc}")
        if digest.casefold() in secrets:
            refuse("ORACLE_LEAK", f"agent-visible file matches evaluator material: {relative}")
    digest = workspace_content_digest(workspace)
    if digest != cell.workspace_digest:
        refuse("PROVENANCE_DRIFT", "workspace content differs from the frozen fixture")
    return digest


@contextmanager
def _fresh_workspace(source: Path | None):
    with tempfile.TemporaryDirectory(prefix="persona-eval-cell-") as directory:
        target = Path(directory) / "workspace"
        if source is None:
            target.mkdir()
        else:
            shutil.copytree(source, target, symlinks=False)
        yield target


def _command_kind(agent_cmd: Any, requested_runner: str) -> str:
    if requested_runner not in {"fixture", "live"}:
        refuse("PROVENANCE_DRIFT", "runner_kind must be fixture or live")
    if requested_runner == "live":
        refuse(
            "CLAIM_ESCALATION",
            "injected local commands are fixture evidence; external live attestation is outside this harness",
        )
    if callable(agent_cmd):
        refuse(
            "PROVENANCE_DRIFT",
            "executable fixture commands must be fresh subprocess argument lists",
        )
    if (
        isinstance(agent_cmd, (str, bytes, bytearray))
        or not isinstance(agent_cmd, Sequence)
        or not agent_cmd
    ):
        refuse("PROVENANCE_DRIFT", "agent_cmd must be a non-empty argument list")
    if any(not isinstance(argument, str) or not argument for argument in agent_cmd):
        refuse("PROVENANCE_DRIFT", "agent command arguments must be nonblank strings")
    return "fixture"


def _invoke(
    cell: TrialCell,
    agent_cmd: Sequence[str],
    workspace: Path | None,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        envelope = canonical_json(
            {
                "cell_id": cell.cell_id,
                "effective_prompt_digest": cell.effective_prompt_digest,
                "persona_digest": cell.persona_digest,
                "persona_id": cell.persona_id,
                "persona_injection_digest": cell.persona_injection_digest,
                "task_id": cell.task_id,
            },
            "PROVENANCE_DRIFT",
        )
        environment = os.environ.copy()
        environment[_CONDITION_ENVIRONMENT_VARIABLE] = envelope
        completed = subprocess.run(
            list(agent_cmd),
            cwd=str(workspace) if workspace is not None else None,
            env=environment,
            capture_output=True,
            text=True,
            timeout=cell.wall_time_ceiling_seconds,
            check=False,
        )
        return {
            "status": "completed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "wall_time_seconds": time.monotonic() - started,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timed_out",
            "returncode": -1,
            "wall_time_seconds": time.monotonic() - started,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "returncode": -1,
            "wall_time_seconds": time.monotonic() - started,
            "invocation_error": type(exc).__name__,
        }


def _normalize_usage(
    cell: TrialCell,
    execution: Mapping[str, Any],
    observed_usage: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], bool]:
    supplied = observed_usage is not None
    if supplied:
        source: Any = observed_usage
    elif any(key in execution for key in _USAGE_KEYS):
        source = {key: execution.get(key, _UNSET) for key in _USAGE_KEYS}
    else:
        source = {"turns": 1, "tool_calls": 0, "tokens": 0, "cost_usd": 0.0}
    invalid = False
    try:
        if not isinstance(source, Mapping) or frozenset(source) != _USAGE_KEYS:
            raise PersonaEvalError(
                "NARRATED_OUTCOME", "usage must contain every exact observed counter"
            )
        turns = integer(source["turns"], "turns", "NARRATED_OUTCOME", minimum=0)
        tool_calls = integer(
            source["tool_calls"], "tool_calls", "NARRATED_OUTCOME", minimum=0
        )
        tokens = integer(source["tokens"], "tokens", "NARRATED_OUTCOME", minimum=0)
        cost = finite_number(
            source["cost_usd"], "cost_usd", "NARRATED_OUTCOME", minimum=0
        )
    except (PersonaEvalError, TypeError, AttributeError):
        turns = cell.turn_ceiling
        tool_calls = 0
        tokens = cell.token_ceiling
        cost = cell.per_cell_cost_ceiling_usd
        invalid = True
    wall_time = float(execution.get("wall_time_seconds", 0.0))
    if not math.isfinite(wall_time) or wall_time < 0:
        wall_time = 0.0
        invalid = True
    exceeded = (
        turns > cell.turn_ceiling
        or tokens > cell.token_ceiling
        or cost > cell.per_cell_cost_ceiling_usd + 1e-12
        or wall_time > cell.wall_time_ceiling_seconds + 1e-12
    )
    return {
        "turns": turns,
        "tool_calls": tool_calls,
        "tokens": tokens,
        "cost_usd": cost,
        "wall_time_seconds": wall_time,
        "exceeded": exceeded,
    }, invalid


def _safe_references(value: Any) -> tuple[list[str], bool]:
    if not isinstance(value, (list, tuple)):
        return [], True
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return [], True
        result.append(item)
    return result, False


def _valid_pass_evidence(
    receipts: Sequence[str],
    artifacts: Sequence[str],
    workspace: Path | None,
) -> bool:
    if any(
        receipt.startswith(_HELD_OUT_RECEIPT_PREFIX)
        and receipt.removeprefix(_HELD_OUT_RECEIPT_PREFIX).strip()
        for receipt in receipts
    ):
        return True
    if workspace is None:
        return False
    workspace_root = workspace.resolve()
    for artifact in artifacts:
        if not artifact.startswith(_FINAL_WORKSPACE_PREFIX):
            continue
        relative = artifact.removeprefix(_FINAL_WORKSPACE_PREFIX)
        if not relative.strip():
            continue
        candidate = (workspace_root / relative).resolve()
        try:
            candidate.relative_to(workspace_root)
        except ValueError:
            continue
        if candidate.is_file():
            return True
    return False


def _grade(
    cell: TrialCell,
    execution: Mapping[str, Any],
    grader: Callable[[Any], Mapping[str, Any]] | None,
    workspace: Path | None,
    usage: Mapping[str, Any],
    invalid_output: bool,
) -> dict[str, Any]:
    context = {
        "cell_id": cell.cell_id,
        "task_id": cell.task_id,
        "workspace": workspace,
        "status": execution.get("status", "failed"),
        "returncode": execution.get("returncode", -1),
    }
    grader_invalid = False
    try:
        result: Mapping[str, Any]
        if grader is None:
            result = {
                "task": "ungraded",
                "severe_misses": 0,
                "false_blockers": 0,
            }
        else:
            result = grader(context)
            if not isinstance(result, Mapping):
                raise TypeError("grader result must be a mapping")
        task = result.get("task")
        if task not in _TASK_OUTCOMES:
            raise ValueError("grader task outcome is outside the frozen vocabulary")
        required_counters = (
            "severe_misses",
            "false_blockers",
            "rounds",
            "contract_edits_after_first_freeze",
        )
        if any(key not in result for key in required_counters):
            raise ValueError("grader omitted an observed counter")
        severe = integer(
            result["severe_misses"],
            "severe_misses",
            "NARRATED_OUTCOME",
            minimum=0,
        )
        blockers = integer(
            result["false_blockers"],
            "false_blockers",
            "NARRATED_OUTCOME",
            minimum=0,
        )
        rounds = integer(
            result["rounds"], "rounds", "NARRATED_OUTCOME", minimum=0
        )
        edits = integer(
            result["contract_edits_after_first_freeze"],
            "contract_edits_after_first_freeze",
            "NARRATED_OUTCOME",
            minimum=0,
        )
        receipts, bad_receipts = _safe_references(result.get("test_receipts", []))
        artifacts, bad_artifacts = _safe_references(result.get("artifacts", []))
        grader_invalid = bad_receipts or bad_artifacts
        if task == "passed" and not _valid_pass_evidence(receipts, artifacts, workspace):
            grader_invalid = True
    except Exception:
        task, severe, blockers, rounds, edits = "failed", 1, 0, 0, 0
        receipts, artifacts = [], []
        grader_invalid = True

    status = execution.get("status", "failed")
    if status == "timed_out":
        task = "timed_out"
    elif status != "completed" or usage["exceeded"] or invalid_output or grader_invalid:
        task = "failed"
    return {
        "task": task,
        "gate": "not_evaluated",
        "refute": "not_evaluated",
        "severe_misses": severe,
        "false_blockers": blockers,
        "rounds": rounds,
        "contract_edits": edits,
        "test_receipts": receipts,
        "artifacts": artifacts,
        "invalid": grader_invalid,
    }


def _atomic_write(record: TrialRecord, output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", record.to_dict()["trial_id"])
    target = output_root / f"{safe_id}.json"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{safe_id}.", suffix=".tmp", dir=output_root
    )
    try:
        payload = json.dumps(
            record.to_dict(),
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write made no progress")
            view = view[written:]
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary_name, target)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _runner_attestation_payload(record: Mapping[str, Any]) -> dict[str, Any]:
    payload = json.loads(canonical_json(record, "PROVENANCE_DRIFT"))
    payload["evidence"]["artifacts"] = [
        artifact
        for artifact in payload["evidence"]["artifacts"]
        if not artifact.startswith(_RUNNER_ATTESTATION_PREFIX)
    ]
    return payload


def _runner_attestation(record: Mapping[str, Any]) -> str:
    message = canonical_json(
        _runner_attestation_payload(record), "PROVENANCE_DRIFT"
    ).encode("utf-8")
    digest = hmac.new(
        _RUNNER_ATTESTATION_AUTHORITY, message, hashlib.sha256
    ).hexdigest()
    return _RUNNER_ATTESTATION_PREFIX + digest


def _validate_runner_attestation(record: Mapping[str, Any]) -> None:
    """Verify that this process's runner emitted the complete fixture record."""

    try:
        attestations = [
            artifact
            for artifact in record["evidence"]["artifacts"]
            if artifact.startswith(_RUNNER_ATTESTATION_PREFIX)
        ]
    except (KeyError, TypeError):
        refuse("PROVENANCE_DRIFT", "fixture record has no runner attestation")
    if len(attestations) != 1:
        refuse("PROVENANCE_DRIFT", "fixture record must carry one runner attestation")
    expected = _runner_attestation(record)
    if not hmac.compare_digest(attestations[0], expected):
        refuse("PROVENANCE_DRIFT", "fixture record runner attestation is invalid")


def run_cell(
    cell: TrialCell,
    *,
    agent_cmd: Callable[..., Any] | Sequence[str] | None = None,
    spent_usd: float = 0.0,
    aggregate_cap_usd: float | None = None,
    output_root: str | os.PathLike[str] | None = None,
    workspace: str | os.PathLike[str] | None = None,
    grader: Callable[[Any], Mapping[str, Any]] | None = None,
    oracle_hashes: Mapping[str, Any] | None = None,
    runner_kind: str = "fixture",
    budget_ledger: CampaignBudget | None = None,
    observed_usage: Mapping[str, Any] | None = None,
    actual_repository_revision: Any = _UNSET,
    actual_add_version: Any = _UNSET,
    actual_add_revision: Any = _UNSET,
    actual_corpus_digest: Any = _UNSET,
    actual_model_id: Any = _UNSET,
    actual_model_family: Any = _UNSET,
    actual_effort: Any = _UNSET,
    actual_runner_digest: Any = _UNSET,
    actual_environment_digest: Any = _UNSET,
    actual_tool_allowlist: Any = _UNSET,
    actual_prompt_template_digest: Any = _UNSET,
    actual_case_prompt_digest: Any = _UNSET,
    actual_effective_prompt_digest: Any = _UNSET,
    actual_workspace_digest: Any = _UNSET,
    actual_oracle_digest: Any = _UNSET,
    actual_rubric_digest: Any = _UNSET,
    actual_grader_digest: Any = _UNSET,
    actual_persona_id: Any = _UNSET,
    actual_persona_digest: Any = _UNSET,
    actual_pin_manifest_digest: Any = _UNSET,
) -> TrialRecord:
    """Preflight, invoke, independently grade, validate, and atomically record."""

    validate_trial_cell(cell)
    _, runtime_cap = _runtime_cap(cell, spent_usd, aggregate_cap_usd)
    if agent_cmd is None:
        refuse("PROVENANCE_DRIFT", "dry run requires an injected deterministic command")
    workspace_path = Path(workspace) if workspace is not None else None
    computed_workspace_digest = _check_workspace(cell, workspace_path, oracle_hashes)
    if actual_workspace_digest is _UNSET:
        refuse("PROVENANCE_DRIFT", "execution omitted observed workspace_digest")
    if actual_workspace_digest != computed_workspace_digest:
        refuse(
            "PROVENANCE_DRIFT",
            "caller workspace digest differs from independently observed content",
        )
    actual = {
        "repository_revision": actual_repository_revision,
        "add_version": actual_add_version,
        "add_revision": actual_add_revision,
        "corpus_digest": actual_corpus_digest,
        "model_id": actual_model_id,
        "model_family": actual_model_family,
        "effort": actual_effort,
        "runner_digest": actual_runner_digest,
        "environment_digest": actual_environment_digest,
        "tool_allowlist": actual_tool_allowlist,
        "prompt_template_digest": actual_prompt_template_digest,
        "case_prompt_digest": actual_case_prompt_digest,
        "effective_prompt_digest": actual_effective_prompt_digest,
        "workspace_digest": actual_workspace_digest,
        "oracle_digest": actual_oracle_digest,
        "rubric_digest": actual_rubric_digest,
        "grader_digest": actual_grader_digest,
        "persona_id": actual_persona_id,
        "persona_digest": actual_persona_digest,
        "pin_manifest_digest": actual_pin_manifest_digest,
    }
    _check_provenance(cell, actual, complete=True)
    if observed_usage is not None and (
        not isinstance(observed_usage, Mapping)
        or frozenset(observed_usage) != _USAGE_KEYS
    ):
        refuse(
            "NARRATED_OUTCOME",
            "observed_usage must contain every exact observed counter",
        )
    effective_runner = _command_kind(agent_cmd, runner_kind)

    reservation = (
        budget_ledger.reserve(cell, runtime_cap)
        if budget_ledger is not None
        else None
    )
    settlement_cost = cell.per_cell_cost_ceiling_usd
    invalid_attempt = True
    try:
        with _fresh_workspace(workspace_path) as execution_workspace:
            execution = _invoke(cell, agent_cmd, execution_workspace)
            usage, invalid_usage = _normalize_usage(cell, execution, observed_usage)
            grade = _grade(
                cell,
                execution,
                grader,
                execution_workspace,
                usage,
                invalid_usage,
            )
            invalid_attempt = invalid_usage or grade["invalid"] or usage["exceeded"]
            settlement_cost = float(usage["cost_usd"])
    finally:
        if reservation is not None and budget_ledger is not None:
            budget_ledger.settle(
                reservation,
                settlement_cost,
                invalid_output=invalid_attempt,
            )

    pin_artifact = _PIN_ARTIFACT_PREFIX + cell.pin_manifest_digest
    campaign_artifact = _CAMPAIGN_ARTIFACT_PREFIX + cell.campaign_manifest_digest
    protocol_artifact = _PROTOCOL_ARTIFACT_PREFIX + cell.protocol_manifest_digest
    artifacts = [pin_artifact, campaign_artifact, protocol_artifact]
    artifacts.extend(
        artifact
        for artifact in grade["artifacts"]
        if not artifact.startswith(_PIN_ARTIFACT_PREFIX)
    )
    record_payload = {
        "schema": "add.eval-trial/1",
        "trial_id": cell.cell_id,
        "layer": "mechanism",
        "claim_scope": "implementation_semantics",
        "repository": {"revision": cell.repository_revision},
        "add": {"version": cell.add_version, "revision": cell.add_revision},
        "task": {"corpus_version": cell.corpus_version, "id": cell.task_id},
        "actor": {
            "role": "builder",
            "model": None,
            "persona": None,
        },
        "prompt": {
            "digest": cell.effective_prompt_digest,
            "brief_digest": cell.case_prompt_digest,
        },
        "independence": "fresh_session",
        "environment": {
            "runner": effective_runner,
            "digest": cell.environment_digest,
        },
        "outcome": {
            "task": grade["task"],
            "gate": grade["gate"],
            "refute": grade["refute"],
        },
        "evidence": {
            "test_receipts": grade["test_receipts"],
            "artifacts": artifacts,
        },
        "cost": {
            "turns": usage["turns"],
            "tool_calls": usage["tool_calls"],
            "tokens": usage["tokens"],
            "wall_time_seconds": usage["wall_time_seconds"],
            "cost_usd": usage["cost_usd"],
        },
        "repair": {
            "rounds": grade["rounds"],
            "contract_edits_after_first_freeze": grade["contract_edits"],
            "false_blockers": grade["false_blockers"],
            "severe_misses": grade["severe_misses"],
        },
        "participant": None,
    }
    record_payload["evidence"]["artifacts"].append(
        _runner_attestation(record_payload)
    )
    record = validate_trial_record(record_payload)
    if output_root is not None:
        _atomic_write(record, Path(output_root))
    return record
