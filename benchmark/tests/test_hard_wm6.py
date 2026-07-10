"""bench-hard-wm6: the precision-semantics milestone exists and the harness runs it.

Designed to discriminate: naive implementations (string datetime comparison,
closed-interval overlap, no idempotency state, unhandled parse errors) pass
casual inspection and fail these exact checks.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

BENCH = pathlib.Path(__file__).resolve().parents[1]


class TestWm6Workload:
    def test_prompt_and_oracle_exist(self):
        assert (BENCH / "workload" / "wm6" / "PROMPT.md").exists()
        tests = list((BENCH / "workload" / "wm6" / "oracle").glob("test_*.py"))
        assert tests, "wm6 oracle missing"
        body = tests[0].read_text()
        assert body.count("def test_") >= 10, "wm6 oracle must carry >=10 probes"

    def test_prompt_names_the_four_precision_rules(self):
        text = (BENCH / "workload" / "wm6" / "PROMPT.md").read_text()
        for needle in ("offset", "absolute instant", "Idempotency-Key", "400", "python -m app"):
            assert needle in text, f"wm6 prompt missing: {needle}"

    def test_oracle_probes_tz_and_fencepost(self):
        body = next((BENCH / "workload" / "wm6" / "oracle").glob("test_*.py")).read_text()
        assert "+02:00" in body or "+07:00" in body, "must probe non-UTC offsets"
        assert "touching" in body.lower() or "fencepost" in body.lower() or "adjacent" in body.lower()

    def test_wm5_and_earlier_untouched(self):
        assert "room_id" in (BENCH / "workload" / "wm5" / "PROMPT.md").read_text()


class TestHarnessSix:
    def test_valid_wms_is_six(self):
        from benchmark.run import VALID_WMS as run_wms
        from benchmark.pilot import VALID_WMS as pilot_wms
        from benchmark.score import VALID_WMS as score_wms
        assert run_wms == pilot_wms == score_wms == (1, 2, 3, 4, 5, 6)
