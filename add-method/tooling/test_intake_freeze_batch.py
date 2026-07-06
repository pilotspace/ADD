"""intake-freeze-batch (method-ergonomics): N same-gate decisions render as ONE report.

CONTRACT (prose-only, presentation not policy — no gate added, none removed):
  intake.md documents **Batched intake** — N same-bucket items arriving together classify
  as ONE proposal with one human confirm covering the batch, never N sequential asks
  (mixed buckets stay `split_required`).
  report-template.md gains the **Batch, don't serialize** hard rule — N same-gate
  decisions ready together render as one report; each item carries its own flag; any item
  can be held back by name.
  Both absorbed under their frozen pools (core · reference); 3 trees each stay identical.
Run: python3 -m unittest test_intake_freeze_batch -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
SKILL = ADD_METHOD / "skill" / "add"


def _trees(name: str):
    return (SKILL / name,
            REPO / ".claude" / "skills" / "add" / name,
            ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / name)


class IntakeFreezeBatchTest(unittest.TestCase):
    def test_intake_documents_batched_intake(self):            # scenario 1
        text = _trees("intake.md")[0].read_text(encoding="utf-8")
        self.assertIn("Batched intake", text)
        sec = text.split("Batched intake", 1)[1][:500]
        self.assertIn("ONE proposal", sec)
        self.assertIn("never N sequential", sec)

    def test_batch_never_mixes_buckets(self):                  # scenario 2
        text = _trees("intake.md")[0].read_text(encoding="utf-8")
        sec = text.split("Batched intake", 1)[1][:500]
        self.assertIn("split_required", sec,
                      "mixed buckets must stay split_required, not batch-merged")

    def test_report_template_batch_rule(self):                 # scenario 3
        text = _trees("report-template.md")[0].read_text(encoding="utf-8")
        self.assertIn("Batch, don't serialize", text)
        sec = text.split("Batch, don't serialize", 1)[1][:400]
        self.assertIn("held back by name", sec,
                      "a batched approval must let the human hold back any single item")

    def test_batch_keeps_per_item_flag(self):                  # scenario 4
        text = _trees("report-template.md")[0].read_text(encoding="utf-8")
        sec = text.split("Batch, don't serialize", 1)[1][:400]
        self.assertIn("flag", sec, "each batched item must carry its own least-sure flag")

    def test_tree_parity(self):                                # scenario 5
        for name in ("intake.md", "report-template.md"):
            digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in _trees(name)}
            self.assertEqual(len(digests), 1, f"{name} trees diverged")

    def test_pools_absorbed(self):                             # scenario 6 — net ≤0B per pool
        # ceilings from test_skill_lean (baseline × ratio) — duplicated so a bust names this task
        core = sum((SKILL / g).stat().st_size for g in ("SKILL.md", "intake.md"))
        self.assertLessEqual(core, int(20666 * 0.88), "core pool must absorb the intake addition")
        ref = ["scope.md", "deltas.md", "fold.md", "release.md", "report-template.md",
               "graduate.md", "soul.md", "setup-review.md", "adopt.md", "confidence.md",
               "compact-foundation.md", "phases/fast-lane.md", "components.md", "sensitivity.md"]
        total = sum((SKILL / g).stat().st_size for g in ref)
        self.assertLessEqual(total, 51885, "reference pool must absorb the report-template addition")


if __name__ == "__main__":
    unittest.main()
