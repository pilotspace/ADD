"""RunRecord: the frozen per-run shape written by the benchmark harness.

Frozen by .add/tasks/bench-scaffold/TASK.md §3 CONTRACT @ v1. Stdlib only,
fail-loud: a malformed record raises BenchError("invalid_run_record: ...")
rather than writing anything.
"""
from __future__ import annotations

import dataclasses
import json
from typing import Any

# Exactly these 5 metric names — no more, no fewer (frozen in MILESTONE.md).
REQUIRED_METRICS = frozenset(
    {
        "regression_rate",
        "spec_fidelity",
        "tokens_total",
        "cost_usd",
        "context_rot_slope",
        "time_to_first_edit",
    }
)

REQUIRED_ARTIFACTS = frozenset({"workspace", "transcript", "oracle_report"})

VALID_STATUSES = frozenset({"done", "timeout", "failed"})

REQUIRED_TOP_LEVEL = frozenset({"arm", "wm", "rep", "status", "metrics", "artifacts"})


class BenchError(Exception):
    """Raised for any invalid benchmark shape. Message is prefixed with the
    frozen error code (e.g. "invalid_run_record", "invalid_arm_recipe")."""


@dataclasses.dataclass(frozen=True)
class RunRecord:
    arm: str
    wm: int
    rep: int
    status: str
    metrics: dict[str, float]
    artifacts: dict[str, str]

    def to_json(self) -> str:
        return json.dumps(
            {
                "arm": self.arm,
                "wm": self.wm,
                "rep": self.rep,
                "status": self.status,
                "metrics": dict(self.metrics),
                "artifacts": dict(self.artifacts),
            },
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str) -> "RunRecord":
        data = json.loads(payload)
        return validate(data)


def validate(d: dict[str, Any]) -> RunRecord:
    """Validate a raw dict into a RunRecord, or raise BenchError("invalid_run_record: ...").

    Never partially writes anything — pure validation.
    """
    if not isinstance(d, dict):
        raise BenchError("invalid_run_record: not a mapping")

    missing_top = REQUIRED_TOP_LEVEL - d.keys()
    if missing_top:
        raise BenchError(f"invalid_run_record: missing field(s) {sorted(missing_top)}")

    if d["status"] not in VALID_STATUSES:
        raise BenchError(f"invalid_run_record: invalid status {d['status']!r}")

    metrics = d["metrics"]
    if not isinstance(metrics, dict):
        raise BenchError("invalid_run_record: metrics must be a mapping")
    metric_keys = set(metrics.keys())
    if metric_keys != set(REQUIRED_METRICS):
        extra = metric_keys - REQUIRED_METRICS
        missing = REQUIRED_METRICS - metric_keys
        raise BenchError(
            f"invalid_run_record: metrics keys must be exactly {sorted(REQUIRED_METRICS)} "
            f"(extra={sorted(extra)}, missing={sorted(missing)})"
        )

    artifacts = d["artifacts"]
    if not isinstance(artifacts, dict):
        raise BenchError("invalid_run_record: artifacts must be a mapping")
    missing_artifacts = REQUIRED_ARTIFACTS - artifacts.keys()
    if missing_artifacts:
        raise BenchError(f"invalid_run_record: artifacts missing key(s) {sorted(missing_artifacts)}")

    try:
        wm = int(d["wm"])
        rep = int(d["rep"])
    except (TypeError, ValueError) as exc:
        raise BenchError("invalid_run_record: wm/rep must be int-convertible") from exc

    return RunRecord(
        arm=str(d["arm"]),
        wm=wm,
        rep=rep,
        status=str(d["status"]),
        metrics=dict(metrics),
        artifacts=dict(artifacts),
    )
