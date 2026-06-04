#!/usr/bin/env python3
"""Proofs that the ch02 flow DIAGRAM does not contradict the method (task:
flow-diagram-refresh, milestone v2). The picture must say what the words say:
the forward spine is solid (forward-skip forbidden) and backward correction is
drawn (principle 4 — "any phase may send you back to an earlier one").

Text surfaces (mermaid + CHECKLIST) are machine-proved here. The rendered
add-flow.png is a HUMAN visual gate at VERIFY — image models garble labels, so
the raster is reviewed against CHECKLIST by a person, never asserted in code.
Run: python3 -m unittest test_flow_diagram -v
"""
import hashlib
import re
import unittest
from pathlib import Path

import add

ROOT = Path(__file__).resolve().parents[2]          # tooling -> add-method -> repo root
FLOW_TREES = [
    ROOT / "02-the-flow.md",                         # repo-root book (flat)
    ROOT / "add-method" / "docs" / "02-the-flow.md", # shipped npm copy
    ROOT / ".add" / "docs" / "02-the-flow.md",       # dogfood install (gitignored)
]
CHAPTER = ROOT / "add-method" / "docs" / "02-the-flow.md"   # the tested content source
CHECKLIST = ROOT / "add-method" / "diagrams" / "CHECKLIST.md"  # the reusable pipeline

# Phases the FLOW depicts = PHASES minus the terminal bookkeeping state "done".
# ch02 is "seven steps" (six build the feature, Observe is the seventh); "done" is an
# engine state, not a step — so the FLOW depicts every phase except the terminal "done".
FLOW_PHASES = [p for p in add.PHASES if p != "done"]


def _mermaid_block(text: str) -> str:
    m = re.search(r"```mermaid\n(.*?)```", text, re.DOTALL)
    assert m, "no mermaid block in 02-the-flow.md"
    return m.group(1)


def _backward_edges(mermaid: str) -> list[tuple[str, str]]:
    """Mid-flow backward-correction edges, by phase order. The Observe->Specify
    wrap is the big loop, NOT a correction, so it is excluded. Resolves node ids
    to phase indices and reports edges that point upstream — deliberately tolerant
    of arrow syntax (solid/dashed/labelled), so it pins the CLAIM, not the markup."""
    nodes = dict(re.findall(r'(\w+)\["([^"]*)"\]', mermaid))

    def idx_of(node_id: str):
        label = nodes.get(node_id, "").lower()
        for i, p in enumerate(FLOW_PHASES):
            if p in label:
                return i
        return None

    clean = re.sub(r'\[[^\]]*\]', '', mermaid)   # node-label brackets
    clean = re.sub(r'"[^"]*"', '', clean)        # inline edge-label quotes
    clean = re.sub(r'\|[^|]*\|', '', clean)      # |pipe| edge labels
    edges = re.findall(r'(\w+)\s*-[-.\s]*>\s*(\w+)', clean)

    out = []
    for src, dst in edges:
        si, di = idx_of(src), idx_of(dst)
        if si is None or di is None or si <= di:
            continue
        if FLOW_PHASES[si] == "observe" and FLOW_PHASES[di] == "specify":
            continue                              # the wrap loop, not a correction
        out.append((FLOW_PHASES[si], FLOW_PHASES[di]))
    return out


class FlowDiagramProofTest(unittest.TestCase):
    # --- Story <-> State: every engine phase label appears in the diagram -----
    def test_every_phase_label_in_mermaid_and_checklist(self):
        mermaid = _mermaid_block(CHAPTER.read_text(encoding="utf-8")).lower()
        checklist = CHECKLIST.read_text(encoding="utf-8").lower()
        for p in FLOW_PHASES:
            self.assertIn(p, mermaid, f"phase '{p}' missing from ch02 mermaid")
            self.assertIn(p, checklist, f"phase '{p}' missing from CHECKLIST")

    # --- Story <-> Story: the loopback rule is both WRITTEN and DRAWN ----------
    def test_loopback_claim_and_drawing_coexist(self):
        text = CHAPTER.read_text(encoding="utf-8")
        self.assertIn("any phase may send you back to an earlier one", text.lower(),
                      "the principle-4 loopback rule is no longer written in ch02")
        backward = _backward_edges(_mermaid_block(text))
        self.assertTrue(backward,
                        "ch02 prose claims any-phase loopback but the mermaid draws no "
                        "mid-flow backward-correction edge (loopback_not_drawn)")

    # --- no surface drifts: the doc trees agree byte-for-byte -----------------
    def test_flow_chapter_identical_across_trees(self):
        present = [p for p in FLOW_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2, "expected at least root + shipped copy")
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in present}
        self.assertEqual(
            len(digests), 1,
            "02-the-flow.md differs across trees: "
            + ", ".join(f"{p.name}@{p.parent.name}={hashlib.md5(p.read_bytes()).hexdigest()[:8]}"
                        for p in present))


if __name__ == "__main__":
    unittest.main(verbosity=2)
