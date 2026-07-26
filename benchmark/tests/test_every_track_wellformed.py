"""Every workload track, enumerated — not a hand-listed subset.

`test_oracles_red.py` is parametrized over `[1, 2, 3]`, so wm4-wm6, amb1 and
the whole payments track were never checked for the defect it exists to catch:
an oracle that passes on an EMPTY workspace measures nothing, and a checklist
whose probes all return False scores every arm zero. Both failure modes look
exactly like a well-behaved suite from the outside.

This file enumerates `benchmark/workload/*` instead, so a track added later is
covered the day it lands rather than the day someone remembers to add it to a
parametrize list. That is the same gap that let the reading probes ship
vacuous and the collection-shape defect ship three times.
"""
from __future__ import annotations

import importlib
import os
import pathlib
import subprocess
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "workload"


def _tracks() -> list[str]:
    names = sorted(
        p.name for p in WORKLOAD.iterdir()
        if p.is_dir() and not p.name.startswith(("_", "."))
    )
    assert names, "no workload tracks found — this guard would pass vacuously"
    return names


TRACKS = _tracks()


@pytest.mark.parametrize("track", TRACKS)
def test_checklist_declares_requirements(track):
    module = importlib.import_module(f"benchmark.workload.{track}.checklist")
    requirements = getattr(module, "REQUIREMENTS", None)
    assert requirements, f"{track}/checklist.py declares no REQUIREMENTS"
    ids = [r[0] if isinstance(r, tuple) else r["id"] for r in requirements]
    assert len(ids) == len(set(ids)), f"{track}: duplicate requirement ids {ids}"


@pytest.mark.parametrize("track", TRACKS)
def test_oracle_collects_and_is_red_on_an_empty_workspace(track):
    oracle_dir = WORKLOAD / track / "oracle"
    if not oracle_dir.is_dir():
        pytest.skip(f"{track} has no oracle dir")
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(oracle_dir), "-q", "--no-header",
             "-p", "no:cacheprovider"],
            capture_output=True, text=True,
            env={**os.environ, "BENCH_WORKSPACE": empty},
        )
    out = proc.stdout + proc.stderr
    assert "errors during collection" not in out.lower(), f"{track} oracle: {out[-2000:]}"
    assert " passed" not in out or "failed" in out, (
        f"{track} oracle PASSED against an empty workspace — it proves nothing:\n"
        f"{out[-2000:]}")
    assert proc.returncode != 0, (
        f"{track} oracle exited 0 on an empty workspace:\n{out[-2000:]}")
