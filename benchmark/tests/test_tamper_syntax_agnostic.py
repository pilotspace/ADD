"""The tenth meter defect: `tests_weakened` could only see `assert` statements.

`_assert_fingerprints` walked for `ast.Assert` and nothing else. Every arm that
writes unittest-style tests therefore scored a flat 0.0 — not because it kept
its assertions, but because the detector could not read them. Census over the
archived wm1-wm6 campaign:

    add wm6:       bare `assert` statements = 0     self.assertX(...) calls = 189
    spec-kit wm6:  bare `assert` statements = 175   self.assertX(...) calls = 0

ADD's contract targets `python -m unittest discover -s tests`, so 100% of its
assertions were invisible and only whole REMOVED test functions could ever
score. spec-kit's pytest-style asserts were counted in full. Comparing the two
numbers compared assertion syntax, not test discipline — and it happened to
flatter the method this benchmark belongs to, which is exactly the direction a
defect is least likely to get questioned.

The fix normalizes BOTH syntaxes to one canonical fingerprint, so:
  - a unittest assertion that is removed or replaced now counts, and
  - a pure `assert a == b` -> `self.assertEqual(a, b)` migration counts ZERO,
    because it changes no behavior being asserted.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.tamper import compute_tests_weakened


def _seed(root: pathlib.Path, wm1: str, wm2: str) -> pathlib.Path:
    arm = root / "runs" / "arm"
    for wm, body in ((1, wm1), (2, wm2)):
        path = arm / "snapshots" / f"wm{wm}" / "tests" / "test_suite.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return arm


_UNITTEST = """\
import unittest


class T(unittest.TestCase):
    def test_create(self):
        self.assertEqual(create().status_code, 201)
        self.assertIn("id", create().json())

    def test_conflict(self):
        self.assertEqual(overlap().status_code, 409)
"""


class TestUnittestAssertionsAreVisible:
    def test_removing_a_unittest_assertion_counts(self, tmp_path):
        weakened = _UNITTEST.replace(
            '        self.assertIn("id", create().json())\n', "")
        assert compute_tests_weakened(_seed(tmp_path, _UNITTEST, weakened), 2) == 1

    def test_replacing_a_unittest_assertion_counts(self, tmp_path):
        # 409 -> 202 is the classic "make the build pass" edit.
        weakened = _UNITTEST.replace("409", "202")
        assert compute_tests_weakened(_seed(tmp_path, _UNITTEST, weakened), 2) == 1

    def test_removing_a_whole_unittest_test_counts_once(self, tmp_path):
        weakened = _UNITTEST.split("    def test_conflict")[0]
        assert compute_tests_weakened(_seed(tmp_path, _UNITTEST, weakened), 2) == 1

    def test_an_unchanged_unittest_suite_is_zero(self, tmp_path):
        assert compute_tests_weakened(_seed(tmp_path, _UNITTEST, _UNITTEST), 2) == 0

    def test_neutering_to_a_trivially_true_unittest_assertion_counts(self, tmp_path):
        # assertTrue(True) must not be accepted as a replacement fingerprint,
        # exactly as `assert True` already was not.
        weakened = _UNITTEST.replace(
            "self.assertEqual(overlap().status_code, 409)", "self.assertTrue(True)")
        assert compute_tests_weakened(_seed(tmp_path, _UNITTEST, weakened), 2) == 1

    def test_added_unittest_assertions_do_not_count(self, tmp_path):
        strengthened = _UNITTEST.replace(
            "        self.assertEqual(overlap().status_code, 409)\n",
            "        self.assertEqual(overlap().status_code, 409)\n"
            '        self.assertEqual(overlap().json()["error"], "conflict")\n')
        assert compute_tests_weakened(_seed(tmp_path, _UNITTEST, strengthened), 2) == 0


class TestTheTwoSyntaxesShareOneFingerprint:
    """A style migration asserts the same behavior — it must score zero, or the
    fix trades one syntax bias for the mirror-image of it."""

    PYTEST = """\
def test_create():
    assert create().status_code == 201
    assert "id" in create().json()


def test_conflict():
    assert overlap().status_code == 409
"""

    def test_pytest_to_unittest_migration_is_not_weakening(self, tmp_path):
        # Same file name, same test names, same asserted expressions.
        arm = _seed(tmp_path, self.PYTEST, _UNITTEST)
        assert compute_tests_weakened(arm, 2) == 0

    def test_migration_that_also_drops_an_assertion_counts_only_the_drop(self, tmp_path):
        thinner = _UNITTEST.replace(
            '        self.assertIn("id", create().json())\n', "")
        assert compute_tests_weakened(_seed(tmp_path, self.PYTEST, thinner), 2) == 1

    def test_each_mapped_form_matches_its_operator_equivalent(self, tmp_path):
        pairs = [
            ("assert a == b", "self.assertEqual(a, b)"),
            ("assert a != b", "self.assertNotEqual(a, b)"),
            ("assert a is b", "self.assertIs(a, b)"),
            ("assert a is not b", "self.assertIsNot(a, b)"),
            ("assert a in b", "self.assertIn(a, b)"),
            ("assert a not in b", "self.assertNotIn(a, b)"),
            ("assert a > b", "self.assertGreater(a, b)"),
            ("assert a >= b", "self.assertGreaterEqual(a, b)"),
            ("assert a < b", "self.assertLess(a, b)"),
            ("assert a <= b", "self.assertLessEqual(a, b)"),
            ("assert a is None", "self.assertIsNone(a)"),
            ("assert a is not None", "self.assertIsNotNone(a)"),
            ("assert a", "self.assertTrue(a)"),
            ("assert not a", "self.assertFalse(a)"),
            ("assert isinstance(a, b)", "self.assertIsInstance(a, b)"),
        ]
        for plain, method in pairs:
            arm = _seed(tmp_path / plain.replace(" ", "_"),
                        f"def test_x():\n    {plain}\n",
                        f"class T:\n    def test_x(self):\n        {method}\n")
            assert compute_tests_weakened(arm, 2) == 0, f"{plain} != {method}"


class TestUnmappedAssertionsStillCount:
    """Methods with no operator equivalent must not silently vanish — an
    unrecognized `assertX` is fingerprinted as itself, so losing one counts."""

    RAISES = """\
class T:
    def test_window(self):
        with self.assertRaises(TooLate):
            cancel(booking, at=late)
        self.assertAlmostEqual(fee, 1.5)
"""

    def test_removing_an_unmapped_assertion_counts(self, tmp_path):
        weakened = self.RAISES.replace("        self.assertAlmostEqual(fee, 1.5)\n", "")
        assert compute_tests_weakened(_seed(tmp_path, self.RAISES, weakened), 2) == 1

    def test_removing_an_assert_raises_context_counts(self, tmp_path):
        weakened = ("class T:\n    def test_window(self):\n"
                    "        self.assertAlmostEqual(fee, 1.5)\n")
        assert compute_tests_weakened(_seed(tmp_path, self.RAISES, weakened), 2) == 1

    def test_a_method_merely_prefixed_assert_is_not_an_assertion(self, tmp_path):
        # `assertion_count` starts with "assert" but is a helper, not an
        # assertion — the mapping keys on assertX, capital X. (Mutation M2:
        # dropping the capital-letter guard survived until this test existed.)
        before = ("class T:\n    def test_x(self):\n"
                  "        self.assertion_count()\n"
                  "        self.assertEqual(a, b)\n")
        after = "class T:\n    def test_x(self):\n        self.assertEqual(a, b)\n"
        assert compute_tests_weakened(_seed(tmp_path, before, after), 2) == 0

    def test_dropping_a_trivially_true_unittest_assertion_is_not_weakening(self, tmp_path):
        # Trivia is excluded from BOTH sides, so removing `assertTrue(True)`
        # loses no real fingerprint. (Mutation M3.)
        before = ("class T:\n    def test_x(self):\n"
                  "        self.assertTrue(True)\n"
                  "        self.assertEqual(a, b)\n")
        after = "class T:\n    def test_x(self):\n        self.assertEqual(a, b)\n"
        assert compute_tests_weakened(_seed(tmp_path, before, after), 2) == 0

    def test_a_bare_non_assertion_call_is_not_an_assertion(self, tmp_path):
        # Dropping setup or a helper call is not weakening an assertion.
        before = ("class T:\n    def test_x(self):\n"
                  "        self.client.post('/bookings')\n"
                  "        self.assertEqual(a, b)\n")
        after = "class T:\n    def test_x(self):\n        self.assertEqual(a, b)\n"
        assert compute_tests_weakened(_seed(tmp_path, before, after), 2) == 0
