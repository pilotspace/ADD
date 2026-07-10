"""write_record_atomic / find_resume_point — frozen per TASK.md bench-runner §3.

Pure functions over the existing frozen `RunRecord`/`validate` shape
(benchmark/schema/run_record.py) — no new persistent schema, no second
ledger file; resume state is derived entirely by re-reading record.json
files already on disk.
"""
from __future__ import annotations

import os
import pathlib
import tempfile

from benchmark.schema.run_record import BenchError, RunRecord

BENCHMARK_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RUNS_ROOT = BENCHMARK_ROOT / "runs"


def write_record_atomic(path: pathlib.Path, record: RunRecord) -> None:
    """Write `record` to `path` via temp-file + `os.replace`.

    A crash/fault between the temp-file write and the rename leaves the
    target path untouched (absent, or the prior complete record) — never a
    partial/corrupt file (R5).
    """
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".record-", suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(record.to_json())
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    finally:
        # if os.replace succeeded the temp file is gone; if a fault fired
        # before it, clean up so we never leak the temp file either.
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def find_resume_point(arm_name: str, *, runs_root: pathlib.Path | None = None) -> int | None:
    """Highest done WM + 1, or None if there is nothing to resume from
    (no record.json exists yet anywhere under runs_root/arm_name/)."""
    root = pathlib.Path(runs_root) if runs_root is not None else DEFAULT_RUNS_ROOT
    arm_dir = root / arm_name
    if not arm_dir.exists():
        return None

    record_paths = sorted(arm_dir.glob("wm*/record.json"))
    if not record_paths:
        return None

    highest_done = 0
    for record_path in record_paths:
        try:
            record = RunRecord.from_json(record_path.read_text())
        except BenchError:
            continue
        if record.status == "done" and record.wm > highest_done:
            highest_done = record.wm
    return highest_done + 1
