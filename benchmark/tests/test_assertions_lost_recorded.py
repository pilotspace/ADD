"""`assertions_lost` must land in the record beside `tests_weakened`.

A metric computed only by a post-hoc script is a metric nobody will recompute
consistently. `tests_weakened` is written at score time from the snapshot pair;
its rename-immune companion is written from the same pair, under the same
guards, or the two numbers drift apart the first time someone scores a run
without remembering the extra step.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.schema.run_record import OPTIONAL_METRICS

_SUITE = """\
class T:
    def test_create(self):
        self.assertEqual(status, 201)
        self.assertTrue(body["id"])
"""


def test_assertions_lost_is_an_accepted_optional_metric():
    assert "assertions_lost" in OPTIONAL_METRICS


def _score(tmp_path, wm1: str, wm2: str) -> dict:
    from benchmark import score

    root = tmp_path / "runs"
    for wm, body in ((1, wm1), (2, wm2)):
        path = root / "add" / "snapshots" / f"wm{wm}" / "tests" / "test_suite.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    metrics: dict = {}
    score._add_tamper_metrics(metrics, root, "add", 2, "wm")
    return metrics


def test_both_counts_are_written_from_the_same_snapshot_pair(tmp_path):
    # A rename: tests_weakened sees a removed function, assertions_lost sees
    # nothing lost. Both numbers present, and they DISAGREE — which is the
    # whole reason for carrying two.
    renamed = _SUITE.replace("def test_create", "def test_create_with_owner")
    metrics = _score(tmp_path, _SUITE, renamed)
    assert metrics["tests_weakened"] == 1.0
    assert metrics["assertions_lost"] == 0.0


def test_a_real_drop_moves_both(tmp_path):
    thinner = _SUITE.replace('        self.assertTrue(body["id"])\n', "")
    metrics = _score(tmp_path, _SUITE, thinner)
    assert metrics["tests_weakened"] == 1.0
    assert metrics["assertions_lost"] == 1.0


def test_first_milestone_is_zero_for_both(tmp_path):
    from benchmark import score

    root = tmp_path / "runs"
    snap = root / "add" / "snapshots" / "wm1" / "tests"
    snap.mkdir(parents=True)
    (snap / "test_suite.py").write_text(_SUITE, encoding="utf-8")
    metrics: dict = {}
    score._add_tamper_metrics(metrics, root, "add", 1, "wm")
    assert metrics["tests_weakened"] == 0.0
    assert metrics["assertions_lost"] == 0.0


def test_no_snapshots_means_neither_key_rather_than_a_zero(tmp_path):
    # Fail closed: a missing snapshot pair must not be reported as "lost 0".
    from benchmark import score

    metrics: dict = {}
    score._add_tamper_metrics(metrics, tmp_path / "runs", "add", 2, "wm")
    assert "tests_weakened" not in metrics
    assert "assertions_lost" not in metrics
