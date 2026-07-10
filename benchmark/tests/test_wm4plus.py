"""bench-wm4plus-horizon: WM4/WM5 exist and the harness scores them.

The crossover hypothesis: add's per-WM cost falls (12.85→3.2→2.1M) while
spec-kit's rises (1.11→1.08→1.64M) — WM4/WM5 test whether the curves cross.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

BENCH = pathlib.Path(__file__).resolve().parents[1]


class TestWorkloadExists:
    def test_wm4_prompt_and_oracle(self):
        assert (BENCH / "workload" / "wm4" / "PROMPT.md").exists()
        oracle = BENCH / "workload" / "wm4" / "oracle"
        tests = list(oracle.glob("test_*.py"))
        assert tests, "wm4 oracle missing"
        body = tests[0].read_text()
        assert body.count("def test_") >= 5, "wm4 oracle must carry >=5 tests"

    def test_wm5_prompt_and_oracle(self):
        assert (BENCH / "workload" / "wm5" / "PROMPT.md").exists()
        oracle = BENCH / "workload" / "wm5" / "oracle"
        tests = list(oracle.glob("test_*.py"))
        assert tests, "wm5 oracle missing"
        body = tests[0].read_text()
        assert body.count("def test_") >= 5, "wm5 oracle must carry >=5 tests"

    def test_prompts_carry_entry_contract_and_inheritance(self):
        for wm in (4, 5):
            text = (BENCH / "workload" / f"wm{wm}" / "PROMPT.md").read_text()
            assert "python -m app" in text, f"wm{wm} must restate the entry contract"
            assert "end_time" in text, f"wm{wm} builds on the WM3 shape"

    def test_wm123_untouched(self):
        # frozen: the original prompts are byte-stable anchors for comparability
        assert "duration_minutes" in (BENCH / "workload" / "wm1" / "PROMPT.md").read_text()
        assert "end_time" in (BENCH / "workload" / "wm3" / "PROMPT.md").read_text()


class TestHarnessExtended:
    def test_valid_wms_is_five(self):
        from benchmark.run import VALID_WMS as run_wms
        from benchmark.pilot import VALID_WMS as pilot_wms
        from benchmark.score import VALID_WMS as score_wms
        assert run_wms == pilot_wms == score_wms == (1, 2, 3, 4, 5, 6)  # extended @ bench-hard-wm6

    def test_score_generalizes_priors(self):
        src = (BENCH / "score.py").read_text()
        assert "if wm >= 3:" in src, "priors/slope must generalize to wm>=3"
        # v2-meter-fixes M2: regression generalized from the wm3 bait to
        # re-running ALL earlier WMs' oracle suites at every WM
        assert "compute_regression_rate_v2" in src


class TestSlopeOverFullTrajectory:
    def test_four_point_slope(self):
        from benchmark.score import compute_context_rot_slope
        # perfectly linear decline of 0.01/WM over 4 points
        s = compute_context_rot_slope([0.97, 0.96, 0.95, 0.94])
        assert abs(s - (-0.01)) < 1e-9
