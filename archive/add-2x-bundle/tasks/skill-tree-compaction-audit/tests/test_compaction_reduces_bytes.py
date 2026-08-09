"""skill-tree-compaction-audit — §4 red test.

Covers M3: after the 8 frozen edits, every lean-fence pool (and the whole tree) must
measure STRICTLY FEWER bytes than at Ground SHA (7345649), while remaining <= its
UNCHANGED frozen target (no rebaseline). Everything else this task's Musts/Rejects
require (M1 no-content-loss, M2 parity, M4 full suite, M5 no-vocab-collision, R1-R4)
is already guarded by the existing suite (test_skill_lean / test_tree_parity /
test_bundle_parity / test_wording_lint / the full discover run) — this is the one
genuinely NEW assertion this task adds.

Run: python3 -m unittest test_compaction_reduces_bytes -v
"""
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "add-method" / "tooling"))

from test_skill_lean import POOLS, _CANON, _pool_bytes, TREE_BASELINE_BYTES  # noqa: E402

# Measured at Ground SHA 7345649 (this task's §0), before any of the 8 edits.
GROUND_SHA_POOL_BYTES = {
    "core": 18179,
    "orchestration": 40772,
    "phases": 32243,
    "reference": 51198,
}
GROUND_SHA_TREE_BYTES = 142392


class CompactionReducesBytesTest(unittest.TestCase):
    def test_all_pools_shrink_from_ground_sha(self):
        for pool in POOLS:
            name = pool["name"]
            ground = GROUND_SHA_POOL_BYTES[name]
            target = int(pool["baseline"] * pool["ratio"])
            now = _pool_bytes(pool)
            self.assertLess(
                now, ground,
                f"{name} pool is {now} B; expected strictly fewer than the "
                f"{ground} B measured at Ground SHA — the 8 frozen edits should have shrunk it.",
            )
            self.assertLessEqual(
                now, target,
                f"{name} pool is {now} B; still must stay <= its unchanged frozen target {target} B.",
            )

    def test_tree_shrinks_from_ground_sha(self):
        now = sum(len(p.read_bytes()) for p in _CANON.rglob("*.md"))
        self.assertLess(
            now, GROUND_SHA_TREE_BYTES,
            f"whole tree is {now} B; expected strictly fewer than the "
            f"{GROUND_SHA_TREE_BYTES} B measured at Ground SHA.",
        )
        target = int(TREE_BASELINE_BYTES * 0.75)
        self.assertLessEqual(now, target, f"whole tree is {now} B; still must stay <= {target} B.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
