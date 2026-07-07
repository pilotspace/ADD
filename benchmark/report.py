"""report — renders the 5-arm x 3-WM arm-vs-arm markdown comparison from
scored record.json files alone (bench-pilot-report TASK.md §3 CONTRACT @
v1). Pure function over `benchmark/runs/` -- never raises for a missing
record (renders "not run"); re-runnable, no live agent/judge call.
"""
from __future__ import annotations

import pathlib
from typing import Sequence

from benchmark.arms.loader import ARM_NAMES
from benchmark.runner.records import DEFAULT_RUNS_ROOT
from benchmark.schema.run_record import REQUIRED_METRICS, BenchError, RunRecord

# Headline metrics shown in the WM3 summary table + column order for the
# per-WM detail tables (human-decided at freeze: headline-first ordering).
METRIC_COLUMNS = (
    "spec_fidelity",
    "regression_rate",
    "context_rot_slope",
    "tokens_total",
    "cost_usd",
)
NOT_RUN = "not run"
NA_BY_DEFINITION = "N/A (by definition)"


def _load_record(runs_root: pathlib.Path, arm: str, wm: int) -> RunRecord | None:
    path = runs_root / arm / f"wm{wm}" / "record.json"
    if not path.exists():
        return None
    try:
        return RunRecord.from_json(path.read_text())
    except BenchError:
        return None


def _evidence_link(runs_root: pathlib.Path, arm: str, wm: int, record: RunRecord) -> str:
    record_path = runs_root / arm / f"wm{wm}" / "record.json"
    transcript = record.artifacts.get("transcript", "")
    return f"[record.json]({record_path}) [transcript]({transcript})"


def _render_cell(arm: str, wm: int, metric: str, record: RunRecord | None, runs_root: pathlib.Path) -> str:
    if record is None:
        return NOT_RUN

    if metric in ("regression_rate", "context_rot_slope") and wm in (1, 2):
        value_text = NA_BY_DEFINITION
    else:
        value = record.metrics[metric]
        value_text = f"{value:.2f}"
        if metric == "spec_fidelity" and "spec_fidelity_audit" not in record.artifacts:
            value_text = f"{value_text} (unaudited)"

    evidence = _evidence_link(runs_root, arm, wm, record)
    return f"{value_text} — {evidence}"


def _render_wm_table(
    runs_root: pathlib.Path, wm: int, arms: Sequence[str]
) -> str:
    header = "| arm | " + " | ".join(METRIC_COLUMNS) + " |"
    sep = "| --- | " + " | ".join("---" for _ in METRIC_COLUMNS) + " |"
    lines = [f"## WM{wm}", "", header, sep]
    for arm in arms:
        record = _load_record(runs_root, arm, wm)
        cells = [_render_cell(arm, wm, metric, record, runs_root) for metric in METRIC_COLUMNS]
        lines.append(f"| {arm} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def _render_headline_table(runs_root: pathlib.Path, arms: Sequence[str]) -> str:
    """WM3 headline summary table (human-decided at freeze: headline FIRST,
    then the 3 detailed per-WM tables)."""
    wm = 3
    header = "| arm | " + " | ".join(METRIC_COLUMNS) + " |"
    sep = "| --- | " + " | ".join("---" for _ in METRIC_COLUMNS) + " |"
    lines = ["## Headline (WM3)", "", header, sep]
    for arm in arms:
        record = _load_record(runs_root, arm, wm)
        cells = [_render_cell(arm, wm, metric, record, runs_root) for metric in METRIC_COLUMNS]
        lines.append(f"| {arm} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_report(
    runs_root: pathlib.Path | None = None,
    arms: Sequence[str] = ARM_NAMES,
    wms: Sequence[int] = (1, 2, 3),
) -> str:
    """Pure function over on-disk record.json files: never raises for a
    missing record (renders "not run"); the CLI's exit-2 filter validation
    happens BEFORE calling this, not inside it."""
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT

    sections = ["# Arm-vs-arm pilot report", ""]
    if 3 in wms:
        sections.append(_render_headline_table(root, arms))
    for wm in wms:
        sections.append(_render_wm_table(root, wm, arms))
    return "\n".join(sections)
