"""bench-fidelity-dip: trajectory + min artifacts at WM3.

OLS slope at n=3 is (f3-f1)/2 — the middle WM has zero weight, so a mid-run
collapse (gsd wm2 = 0.50) is invisible to context_rot_slope. These artifacts
make it visible without touching the frozen 5-metric set.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.score import _fidelity_artifacts  # noqa: E402


class TestFidelityArtifacts:
    def test_trajectory_and_min(self):
        arts = _fidelity_artifacts([0.97, 0.5], 0.95)
        assert arts["fidelity_trajectory"] == "0.97;0.5;0.95"
        assert arts["fidelity_min"] == "0.5"

    def test_flat_trajectory(self):
        arts = _fidelity_artifacts([0.95, 0.95], 0.95)
        assert arts["fidelity_trajectory"] == "0.95;0.95;0.95"
        assert arts["fidelity_min"] == "0.95"

    def test_wired_into_wm3_scoring_only(self):
        import benchmark.score as score_mod
        src = pathlib.Path(score_mod.__file__).read_text()
        wm3_branch = src.split("if wm == 3:", 2)[-1]
        assert "_fidelity_artifacts" in wm3_branch
