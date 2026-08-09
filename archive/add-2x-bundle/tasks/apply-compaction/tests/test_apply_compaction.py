"""Red→green guard for apply-compaction §3 (FROZEN @ v1).

Dogfoods foundation compaction on the LIVE specs: reverse all 3 append-only sequences
newest-first, then roll the approved v1–v20 tail into ONE settled line per spec — proving
no record is lost (collapse = summarize + point to git), order is newest-first, and every
OPEN residue stays live.

Records + the roll boundary come from the SHARED parser (`compaction_lib`) so the test and
the transform classify identically. The baseline is the frozen `snapshot_before.json`.

RED drivers (fail until the transform runs): test_reverse_then_roll_order ·
  test_settled_line_at_tail · test_visibly_shorter · test_git_pointer_survives.
DISCLOSED green-at-red regression guards (a preservation guard cannot RED by doing nothing —
  doing nothing loses nothing): test_no_residue_lost · test_open_residues_live ·
  test_glossary_model_registry_unchanged.

unittest (repo convention). Run: python3 -m unittest discover -s tests
"""
import hashlib
import json
import os
import re
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_TASK = os.path.dirname(_HERE)
_ROOT = os.path.abspath(os.path.join(_TASK, "..", "..", ".."))
sys.path.insert(0, _TASK)
import compaction_lib as cl  # noqa: E402

_PROJECT = os.path.join(_ROOT, ".add", "PROJECT.md")
_CONVENTIONS = os.path.join(_ROOT, ".add", "CONVENTIONS.md")
_GLOSSARY = os.path.join(_ROOT, ".add", "GLOSSARY.md")
_MODEL = os.path.join(_ROOT, ".add", "MODEL_REGISTRY.md")
_SNAP = os.path.join(_TASK, "snapshot_before.json")


def _read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _ident(seq_name, rec):
    """A stable identity for a record (the row line / bullet block)."""
    return rec["line"].strip() if seq_name == "key_decisions" else rec["block"].strip()


@unittest.skip(
    "ONE-SHOT: apply-compaction shipped 2026-06-15 (verified EARNED at its verify gate). "
    "This suite proved the reverse+roll transform lost no record AT BUILD TIME against the "
    "frozen snapshot_before.json. The live specs have since legitimately evolved (foundation "
    "fv31 fold prepended new records), so the exact-list assertions no longer match — that is "
    "expected, not a regression. The pre-transform records remain recoverable from git "
    "(commit db98f9a). snapshot_before.json is now a gitignored transient; the reusable parser "
    "compaction_lib.py + apply_compaction.py stay for the NEXT compaction."
)
class ApplyCompactionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snap = json.loads(_read(_SNAP))
        proj, conv = _read(_PROJECT), _read(_CONVENTIONS)
        cls.live = cl.sequences(proj, conv)
        # reconstruct the ORIGINAL records from the frozen snapshot
        s = cls.snap
        cls.orig = {
            "key_decisions": [{"line": ln, "date": d, "settled": False}
                              for ln, d in zip(s["key_decisions"]["rows"], s["key_decisions"]["dates"])],
            "spec": [{"block": b, "maxfv": m, "settled": False}
                     for b, m in zip(s["spec"]["blocks"], s["spec"]["maxfv"])],
            "method_learnings": [{"block": b, "maxfv": m, "settled": False}
                                 for b, m in zip(s["method_learnings"]["blocks"], s["method_learnings"]["maxfv"])],
        }

    def _live_split(self, name):
        recs = self.live[name]
        kept = [r for r in recs if not r.get("settled")]
        settled = [r for r in recs if r.get("settled")]
        return kept, settled

    # ---- RED drivers --------------------------------------------------------
    def test_reverse_then_roll_order(self):
        """Each sequence reads newest-first: live kept records == the snapshot's kept run REVERSED."""
        for name in ("key_decisions", "spec", "method_learnings"):
            _, kept_orig = cl.split(name, self.orig[name])
            expected = [_ident(name, r) for r in reversed(kept_orig)]
            live_kept, _ = self._live_split(name)
            got = [_ident(name, r) for r in live_kept]
            self.assertEqual(got, expected,
                             f"{name}: kept records are not the original kept run reversed (newest-first)")
        # the very first key-decision row is the most-recent date
        live_kd, _ = self._live_split("key_decisions")
        self.assertTrue(live_kd and live_kd[0]["date"] == max(d for d in self.snap["key_decisions"]["dates"] if d),
                        "key_decisions head is not the most-recent dated row")

    def test_settled_line_at_tail(self):
        """Each sequence ends in EXACTLY ONE settled line; KD/method declare the rolled count."""
        for name in ("key_decisions", "spec", "method_learnings"):
            recs = self.live[name]
            settled = [r for r in recs if r.get("settled")]
            self.assertEqual(len(settled), 1, f"{name}: expected exactly one settled line, got {len(settled)}")
            self.assertTrue(recs[-1].get("settled"), f"{name}: the settled line is not at the tail")
        rolled_kd, _ = cl.split("key_decisions", self.orig["key_decisions"])
        rolled_ml, _ = cl.split("method_learnings", self.orig["method_learnings"])
        kd_line = [r for r in self.live["key_decisions"] if r.get("settled")][0]["line"]
        ml_block = [r for r in self.live["method_learnings"] if r.get("settled")][0]["block"]
        self.assertEqual(int(cl.SETTLED_KD.match(kd_line.strip()).group(3)), len(rolled_kd),
                         "§Key-Decisions settled row declares the wrong rolled count")
        self.assertEqual(int(cl.SETTLED_ML.match(ml_block.strip()).group(1)), len(rolled_ml),
                         "§Method-learnings settled line declares the wrong rolled count")

    def test_visibly_shorter(self):
        """§Spec and §Method-learnings are shorter than the pre-transform snapshot."""
        proj = _read(_PROJECT)
        spec_lines = proj.count("\n", proj.index("## Spec"), proj.index("## Key Decisions"))
        self.assertLess(spec_lines, self.snap["project_spec_section_lines"],
                        "§Spec did not get shorter")
        self.assertLess(_read(_CONVENTIONS).count("\n") + 1, self.snap["conventions_total_lines"],
                        "CONVENTIONS.md did not get shorter")

    def test_git_pointer_survives(self):
        """Every settled line carries a 'see git' pointer (else trail-loss)."""
        for name in ("key_decisions", "spec", "method_learnings"):
            for r in self.live[name]:
                if r.get("settled"):
                    text = r.get("line") or r.get("block")
                    self.assertIn("see git", text, f"{name}: settled line dropped the git pointer")

    # ---- DISCLOSED green-at-red regression guards ---------------------------
    def test_no_residue_lost(self):
        """Nothing is dropped EXCEPT records inside the approved rolled run (preservation)."""
        for name in ("key_decisions", "spec", "method_learnings"):
            originals = {_ident(name, r) for r in self.orig[name]}
            rolled, _ = cl.split(name, self.orig[name])
            rolled_ids = {_ident(name, r) for r in rolled}
            live_kept, _ = self._live_split(name)
            live_ids = {_ident(name, r) for r in live_kept}
            self.assertTrue(live_ids <= originals, f"{name}: a kept record was fabricated (not in the snapshot)")
            dropped = originals - live_ids
            self.assertTrue(dropped <= rolled_ids,
                            f"{name}: {len(dropped - rolled_ids)} record(s) vanished that were NOT eligible to roll")

    def test_open_residues_live(self):
        """fv29–30 era + dates >= 2026-06-09 stay EXPANDED (never inside a rolled run)."""
        live_kd, _ = self._live_split("key_decisions")
        recent_dates = {d for d in self.snap["key_decisions"]["dates"] if d and d >= "2026-06-09"}
        live_kd_dates = {r["date"] for r in live_kd}
        self.assertTrue(recent_dates <= live_kd_dates, "a recent (>=06-09) key-decision was rolled away")
        for name in ("spec", "method_learnings"):
            live_kept, _ = self._live_split(name)
            live_fv = {r["maxfv"] for r in live_kept}
            for fv in (29, 30):
                if fv in (m for m in self.snap[name]["maxfv"]):
                    self.assertIn(fv, live_fv, f"{name}: fv{fv} (recent) was rolled away")

    def test_glossary_model_registry_unchanged(self):
        self.assertEqual(_md5(_GLOSSARY), self.snap["glossary_md5"], "GLOSSARY.md changed (should be untouched)")
        self.assertEqual(_md5(_MODEL), self.snap["model_registry_md5"], "MODEL_REGISTRY.md changed (should be untouched)")


if __name__ == "__main__":
    unittest.main()
