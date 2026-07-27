"""`compute_assertions_lost` — the rename-immune companion to
`compute_tests_weakened`.

`compute_tests_weakened` keys test identity as `<relpath>::<fn name>`, so a
RENAME reads as a removed test. Auditing spec-kit's largest recorded count
(runs-persist wm1->wm2 = 4) found three of the four were renames or
resemanticized tests, not lost coverage:

    test_create_returns_201_with_id -> test_create_returns_201_with_id_and_owner
    test_list_returns_all_bookings  -> test_list_returns_only_own_bookings
    test_list_returns_created_...   -> test_list_returns_only_owner_bookings

An arm that renames its tests as the domain shifts is punished for
housekeeping. Since `compute_tests_weakened`'s definition is frozen in its
§3 contract, this is a NEW metric rather than an edit to that one:

    assertions_lost = |prior fingerprints - current fingerprints|
                      over the WHOLE snapshot, not per function

An assertion that survived under a different test name, in a different class,
or in a different file is not lost. Only an assertion the suite NO LONGER
MAKES counts. Both numbers get reported; they answer different questions.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest

from benchmark.schema.run_record import BenchError
from benchmark.tamper import compute_assertions_lost


def _seed(root: pathlib.Path, wm1: dict[str, str], wm2: dict[str, str]) -> pathlib.Path:
    arm = root / "runs" / "arm"
    for wm, files in ((1, wm1), (2, wm2)):
        for rel, body in files.items():
            path = arm / "snapshots" / f"wm{wm}" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
    return arm


_SUITE = """\
class T:
    def test_create_returns_201(self):
        self.assertEqual(status, 201)
        self.assertTrue(body["id"])

    def test_list(self):
        self.assertEqual(len(body), 2)
"""


class TestRenamesAreNotLosses:
    def test_renaming_a_test_loses_nothing(self, tmp_path):
        renamed = _SUITE.replace("test_create_returns_201", "test_create_returns_201_with_owner")
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": renamed}), 2) == 0

    def test_moving_an_assertion_to_another_test_loses_nothing(self, tmp_path):
        moved = """\
class T:
    def test_create_returns_201(self):
        self.assertEqual(status, 201)

    def test_id_is_assigned(self):
        self.assertTrue(body["id"])

    def test_list(self):
        self.assertEqual(len(body), 2)
"""
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": moved}), 2) == 0

    def test_moving_an_assertion_to_another_file_loses_nothing(self, tmp_path):
        split_a = "class T:\n    def test_list(self):\n        self.assertEqual(len(body), 2)\n"
        split_b = ("class U:\n    def test_create_returns_201(self):\n"
                   "        self.assertEqual(status, 201)\n"
                   '        self.assertTrue(body["id"])\n')
        arm = _seed(tmp_path, {"test_suite.py": _SUITE},
                    {"test_a.py": split_a, "test_b.py": split_b})
        assert compute_assertions_lost(arm, 2) == 0


class TestRealLossesStillCount:
    def test_dropping_an_assertion_counts(self, tmp_path):
        thinner = _SUITE.replace('        self.assertTrue(body["id"])\n', "")
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": thinner}), 2) == 1

    def test_deleting_a_whole_test_counts_each_of_its_assertions(self, tmp_path):
        # Unlike tests_weakened (1 per removed fn), the loss is measured in
        # assertions — deleting a 2-assert test loses 2.
        remaining = "class T:\n    def test_list(self):\n        self.assertEqual(len(body), 2)\n"
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": remaining}), 2) == 2

    def test_weakening_an_expected_status_counts(self, tmp_path):
        weakened = _SUITE.replace("self.assertEqual(status, 201)", "self.assertEqual(status, 200)")
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": weakened}), 2) == 1

    def test_neutering_to_trivia_counts(self, tmp_path):
        weakened = _SUITE.replace("self.assertEqual(status, 201)", "self.assertTrue(True)")
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": weakened}), 2) == 1

    def test_duplicate_assertions_are_a_multiset_not_a_set(self, tmp_path):
        # Two tests both assert 201; dropping ONE of them is a real loss.
        both = _SUITE + "\n    def test_create_again(self):\n        self.assertEqual(status, 201)\n"
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": both}, {"test_suite.py": _SUITE}), 2) == 1

    def test_an_unchanged_suite_loses_nothing(self, tmp_path):
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": _SUITE}), 2) == 0

    def test_added_assertions_do_not_offset_a_loss(self, tmp_path):
        grown = (_SUITE.replace('        self.assertTrue(body["id"])\n', "")
                 + "\n    def test_new(self):\n        self.assertEqual(x, y)\n")
        assert compute_assertions_lost(_seed(tmp_path, {"test_suite.py": _SUITE}, {"test_suite.py": grown}), 2) == 1


class TestContract:
    def test_wm1_is_zero_by_definition(self, tmp_path):
        assert compute_assertions_lost(tmp_path / "runs" / "arm", 1) == 0

    def test_missing_snapshot_raises_rather_than_reporting_zero(self, tmp_path):
        arm = tmp_path / "runs" / "arm"
        (arm / "snapshots" / "wm2").mkdir(parents=True)
        with pytest.raises(BenchError, match="^missing_test_snapshot"):
            compute_assertions_lost(arm, 2)
