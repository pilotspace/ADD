"""report — renders the 5-arm x 3-WM arm-vs-arm markdown comparison from
scored record.json files alone (bench-pilot-report TASK.md §3 CONTRACT @
v1). Pure function over `benchmark/runs/` -- never raises for a missing
record (renders "not run"); re-runnable, no live agent/judge call.
"""
from __future__ import annotations

import json
import pathlib
from typing import Sequence

from benchmark.arms.loader import ARM_NAMES
from benchmark.runner.records import DEFAULT_RUNS_ROOT
from benchmark.schema.run_record import REQUIRED_METRICS, BenchError, RunRecord

# Headline metrics shown in the WM3 summary table + column order for the
# per-WM detail tables (human-decided at freeze: headline-first ordering).
METRIC_COLUMNS = (
    "requirement_coverage",
    "oracle_pass_rate",
    "regression_rate",
    "context_rot_slope",
    "tokens_total",
    "cost_usd",
    "time_to_first_edit",
)
NOT_RUN = "not run"
NA_BY_DEFINITION = "N/A (by definition)"


def _load_record(runs_root: pathlib.Path, arm: str, wm: int, family: str = "wm") -> RunRecord | None:
    path = runs_root / arm / f"{family}{wm}" / "record.json"
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

    evidence = _evidence_link(runs_root, arm, wm, record)
    return f"{value_text} — {evidence}"


EMDASH = "—"


def _diagnostics_cells(record: RunRecord | None) -> tuple[str, str, str]:
    """(coverage, uncovered, code quality) for one record — display-only, read from
    `artifacts` (never a metric). Fault-tolerant (M2/R1): a missing record, an absent
    key, or a malformed `coverage_detail` JSON degrades to em-dash, never raises."""
    if record is None:
        return EMDASH, EMDASH, EMDASH

    coverage, uncovered = EMDASH, EMDASH
    raw = record.artifacts.get("coverage_detail")
    if raw:
        try:
            rows = json.loads(raw)
            ids = [str(r["id"]) for r in rows]
            missed = [str(r["id"]) for r in rows if not r["covered"]]
            coverage = f"{len(ids) - len(missed)}/{len(ids)}"
            uncovered = ", ".join(missed) if missed else "none"
        except (ValueError, TypeError, KeyError):
            coverage, uncovered = EMDASH, EMDASH  # malformed -> degrade, never raise

    note = record.artifacts.get("code_quality_annotation") or ""
    quality = " ".join(note.split())[:60] if note else EMDASH
    return coverage, uncovered, quality


def _render_diagnostics(runs_root: pathlib.Path, wm: int, arms: Sequence[str]) -> str:
    """Per-WM DIAGNOSTICS table surfacing the two advisory artifacts
    (`coverage_detail`, `code_quality_annotation`) beside the metric tables — so a
    sub-1.0 coverage score is readable at a glance. Display-only; adds no metric."""
    header = "| arm | coverage | uncovered | code quality |"
    sep = "| --- | --- | --- | --- |"
    lines = [f"### WM{wm} diagnostics", "", header, sep]
    for arm in arms:
        coverage, uncovered, quality = _diagnostics_cells(_load_record(runs_root, arm, wm))
        lines.append(f"| {arm} | {coverage} | {uncovered} | {quality} |")
    lines.append("")
    return "\n".join(lines)


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
        sections.append(_render_diagnostics(root, wm, arms))
    return "\n".join(sections)


# --------------------------------------------------------------------------
# v2 — the trust vector + two-axis report (v2-scoring-report §3 @ v1)
# --------------------------------------------------------------------------

_WEAKENED_CAVEAT = (
    "> tests_weakened caveat: raw counts include legitimate spec-driven test "
    "evolution (renames, rule changes); the adjusted count is rename-tolerant "
    "(only fingerprints present in NO current test count). Every WV1+WV2 rep0 "
    "flag hand-diffed as evolution, zero tampering."
)


def render_trust_report(
    runs_root: pathlib.Path,
    arms: Sequence[str] = ARM_NAMES,
    steps: Sequence[int] = (1, 2, 3),
    family: str = "wm",
) -> str:
    """The two-axis report: per-arm x per-step TRUST VECTOR table (the
    trusted flag never prints without its vector) + the headline printing v1
    raw cost-per-feature BESIDE cost-per-trusted-feature. Read-only over
    records; honest-outcome line REQUIRED when all arms tie on trust."""
    from benchmark.trust import trusted

    root = pathlib.Path(runs_root)
    sections = [f"# Trust report — family {family}", "", _WEAKENED_CAVEAT, ""]

    header = ("| arm | step | trusted | pass | regression | weakened raw/adj (verdict) "
              "| own tests | own suite |")
    rule = "|---|---|---|---|---|---|---|---|"
    rows = [header, rule]
    totals: dict[str, dict] = {}
    for arm in arms:
        cost = 0.0
        trusted_steps = 0
        seen_steps = 0
        for step in steps:
            record = _load_record(root, arm, step, family)
            if record is None:
                rows.append(f"| {arm} | {family}{step} | {NOT_RUN} | - | - | - | - | - |")
                continue
            v = trusted(record, root / arm, family)
            seen_steps += 1
            cost += float(record.metrics.get("cost_usd", 0.0))
            trusted_steps += 1 if v["trusted"] else 0
            rows.append(
                f"| {arm} | {family}{step} | {'yes' if v['trusted'] else 'NO'} "
                f"| {v['pass_rate']:.2f} | {v['regression']:.2f} "
                f"| {v['weakened_raw']}/{v['weakened_adjusted']} ({v['weakened_verdict']}) "
                f"| {v['own_tests']} | {v['own_suite']} |"
            )
        totals[arm] = {"cost": cost, "trusted": trusted_steps, "seen": seen_steps}
    sections.append("\n".join(rows))
    sections.append("")

    sections.append("## Two-axis headline")
    sections.append("| arm | raw cost-per-feature (v1 axis) | cost-per-trusted-feature (v2 axis) |")
    sections.append("|---|---|---|")
    for arm, s in totals.items():
        if s["seen"] == 0:
            sections.append(f"| {arm} | {NOT_RUN} | {NOT_RUN} |")
            continue
        raw_axis = s["cost"] / s["seen"]
        trusted_axis = (f"${s['cost'] / s['trusted']:.2f}" if s["trusted"]
                        else "n/a (0 trusted steps)")
        sections.append(f"| {arm} | ${raw_axis:.2f} | {trusted_axis} |")

    ran = {arm: s for arm, s in totals.items() if s["seen"]}
    if ran and len({s["trusted"] for s in ran.values()}) == 1:
        sections.append("")
        sections.append(
            "**Honest-outcome:** every arm holds the same trusted-step count — "
            "the trust axis does not separate the arms here; separation is cost-only."
        )
    return "\n".join(sections)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="benchmark.report")
    parser.add_argument("--trust", action="store_true")
    parser.add_argument("--runs-root", default=None)
    parser.add_argument("--family", default="wm", choices=("wm", "hv", "amb", "pay", "us"))
    parser.add_argument("--arms", nargs="*", default=list(ARM_NAMES))
    parser.add_argument("--steps", nargs="*", type=int, default=[1, 2, 3])
    args = parser.parse_args(argv)
    root = pathlib.Path(args.runs_root) if args.runs_root else DEFAULT_RUNS_ROOT
    if args.trust:
        print(render_trust_report(root, arms=args.arms, steps=tuple(args.steps), family=args.family))
    else:
        print(render_report(root, arms=args.arms, wms=tuple(args.steps)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
