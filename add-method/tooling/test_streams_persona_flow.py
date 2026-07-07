#!/usr/bin/env python3
"""Red/green tests for the worker-contract flow-preference line (task streams-persona-flow,
milestone delta-drain, contract FROZEN @ v1).

streams.md's `<persona>` block gains ONE sentence: select by frontmatter flow first,
matched to the worker's step (build worker -> flow: build · verify refute-read ->
flow: verify), then use-when. Invariants held: the `<strategy>` block stays
byte-identical between streams.md and advisor.md (the pin-locked floor), the
orchestration dedup pool stays <= 41300 B (paid by in-file compression), 3 skill
trees stay md5-lockstep, and no new XML tag joins the frozen vocabulary.

Run: python3 -m unittest test_streams_persona_flow -v
"""
import hashlib
import re
import unittest
from pathlib import Path

import test_skill_lean

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

STREAMS_TREES = (ADD_METHOD / "skill" / "add" / "streams.md",
                 REPO / ".claude" / "skills" / "add" / "streams.md",
                 BUNDLE / "skill" / "add" / "streams.md")
ADVISOR = ADD_METHOD / "skill" / "add" / "advisor.md"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _block(text: str, tag: str) -> str:
    # line-start-anchored: a guide may MENTION `<strategy>` in prose before the real
    # block (the persona-flow-routing lesson) — only a tag alone on its line opens one
    m = re.search(rf"(?ms)^<{tag}>$(.*?)^</{tag}>$", text)
    return m.group(1) if m else ""


class StreamsPersonaFlowTest(unittest.TestCase):
    # ── M1 + Accept: the flow-preference sentence sits INSIDE <persona> ───────────
    def test_persona_block_teaches_flow_first(self):
        persona = _block(STREAMS_TREES[0].read_text(encoding="utf-8"), "persona")
        self.assertTrue(persona, "worker-contract <persona> block missing")
        for token in ("flow", "flow: build", "flow: verify", "use-when"):
            self.assertIn(token, persona,
                          f"<persona> block must teach flow-first selection ({token})")

    # ── M2: the <strategy> pin floor is untouched ─────────────────────────────────
    def test_strategy_block_byte_identical(self):
        s = _block(STREAMS_TREES[0].read_text(encoding="utf-8"), "strategy")
        a = _block(ADVISOR.read_text(encoding="utf-8"), "strategy")
        self.assertTrue(s and a, "a <strategy> block went missing")
        self.assertEqual(s, a, "<strategy> must stay byte-identical streams.md == advisor.md")

    # ── M3: the binding dedup floor holds ─────────────────────────────────────────
    def test_orchestration_dedup_floor_held(self):
        pool = next(p for p in test_skill_lean.POOLS if p["name"] == "orchestration")
        self.assertLessEqual(test_skill_lean._pool_bytes(pool), 41300,
                             "the 41300 dedup RECLAIM floor must hold — compress in-file")

    # ── M4: 3 skill trees lockstep ────────────────────────────────────────────────
    def test_skill_trees_lockstep(self):
        self.assertEqual(len({_md5(p) for p in STREAMS_TREES}), 1, "streams.md trees diverged")

    # ── R: no new XML tag joins the frozen vocabulary (exact census, non-vacuous) ─
    def test_no_new_xml_tag(self):
        tags = sorted(set(re.findall(r"</?([a-z_]+)>",
                                     STREAMS_TREES[0].read_text(encoding="utf-8"))))
        self.assertEqual(tags, ["agent", "constraints", "context_files", "date", "dur",
                                "expertise", "id", "m", "n", "objective", "outcome",
                                "persona", "return", "slug", "strategy", "time", "tools",
                                "touch_boundary", "worktree", "wt"],
                         "streams.md tag census changed — the flow sentence must add no tag")


if __name__ == "__main__":
    unittest.main()
