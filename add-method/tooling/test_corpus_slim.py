#!/usr/bin/env python3
"""test-corpus-slim red suite (thin-engine-loop, hygiene task).

One canonical sweep (test_tree_parity.py) owns tree parity + the engine pin;
~110 duplicated per-task copies are deleted under it. Census ceilings drive
the dedup; def-count pins protect the floors; the engine is never repinned.

Red-for-the-right-reason today: the sweep covers only 2 skill trees, 112 test
files reference ENGINE_MD5, 166 parity-named functions exist, 8 dead
PHASES_POOL constants remain. Floor pins are green today AND after.

Run: python3 -m unittest test_corpus_slim -v
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

PARITY_NAME = re.compile(
    r"def (test_\w*(?:parity|lockstep|byte_identical|identical|agree|diverged|mirrored|synced)\w*)\(")
SWEEP = HERE / "test_tree_parity.py"

# the seven floor suites — counts may only grow (floor_struck otherwise)
FLOOR_DEF_COUNTS = {
    "test_freeze_command.py": 9,
    "test_gate_audit.py": 18,
    "test_project_scope_lock.py": 31,
    "test_security_escalation_disclosure.py": 5,
    "test_advisor_gate_relax.py": 29,
    "test_ai_plan_verify_gate.py": 44,
    "test_unflagged_freeze.py": 13,
}

# ENGINE_MD5 value at this task's freeze — the engine is NOT edited here
ENGINE_MD5_AT_FREEZE = "ec9a57303adce545a2a2ba64329747c2"


def _test_files():
    return sorted(HERE.glob("test_*.py"))


class CanonicalSweepTest(unittest.TestCase):
    def setUp(self):
        self.src = SWEEP.read_text(encoding="utf-8")

    def test_sweep_covers_bundled_tree(self):
        self.assertIn("_bundled", self.src,
                      "test_tree_parity must compare the _bundled skill tree too")

    def test_sweep_covers_tooling_docs_agents(self):
        for surface in ("add_engine", "templates", "docs", "agents"):
            self.assertIn(surface, self.src,
                          f"test_tree_parity must sweep the {surface} surface")

    def test_sweep_owns_engine_pin(self):
        self.assertIn("ENGINE_MD5", self.src,
                      "the ONE engine-pin assert lives in the canonical sweep")
        self.assertIn("ENGINE_PKG_MD5", self.src)

    def test_sweep_never_vacuous(self):
        # canonical + _bundled are git-tracked and must ALWAYS be compared;
        # only the gitignored dogfood twins may exists-skip (vacuous_sweep guard)
        self.assertRegex(self.src, r"(?i)never|always|git-tracked",
                         "the sweep must state (and hold) that canonical↔bundled never skips")


class CensusCeilingsTest(unittest.TestCase):
    def test_engine_pin_census(self):
        files, fns = set(), 0
        for f in _test_files():
            t = f.read_text(encoding="utf-8")
            if "ENGINE_MD5" not in t:
                continue
            if f.name == "test_corpus_slim.py":
                continue   # this census file names the token without asserting the pin
            files.add(f.name)
            fns += len(re.findall(r"ENGINE_MD5", t))
        self.assertLessEqual(len(files), 3,
                             f"ENGINE_MD5 must live in ≤3 test files, found {len(files)}")

    def test_parity_census_ceilings(self):
        files, fns = set(), 0
        for f in _test_files():
            if f.name == "test_corpus_slim.py":
                continue
            n = len(PARITY_NAME.findall(f.read_text(encoding="utf-8")))
            if n:
                files.add(f.name)
                fns += n
        self.assertLessEqual(fns, 55,
                             f"parity-named test functions must drop to ≤55, found {fns}")
        self.assertLessEqual(len(files), 45,
                             f"their files must drop to ≤45, found {len(files)}")

    def test_no_dead_pool_constants(self):
        offenders = [f.name for f in _test_files()
                     if f.name != "test_corpus_slim.py"
                     and "PHASES_POOL = [" in f.read_text(encoding="utf-8")]
        self.assertEqual(offenders, [],
                         f"dead PHASES_POOL constants must be deleted: {offenders}")


class FloorsTest(unittest.TestCase):
    def test_floor_def_counts(self):
        for fname, count in FLOOR_DEF_COUNTS.items():
            p = HERE / fname
            self.assertTrue(p.exists(), f"floor_struck: floor suite {fname} missing")
            found = len(re.findall(r"(?m)^\s*def test_", p.read_text(encoding="utf-8")))
            self.assertGreaterEqual(
                found, count,
                f"floor_struck: {fname} dropped below its pinned {count} tests ({found})")

    def test_engine_not_repinned(self):
        import engine_pin
        self.assertEqual(engine_pin.ENGINE_MD5, ENGINE_MD5_AT_FREEZE,
                         "test-only task — the engine must not change (no repin)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
