#!/usr/bin/env python3
"""Content + parity guard for the voice-self-improve loop (task soul-self-improve,
v13-onboarding-polish 6/6).

A new skill doc `soul.md` defines the VOICE DELTA loop — grammar, the open→confirmed
lifecycle, the human-is-only-writer rule, the routing into SOUL.md's sections, and the
reject codes — mirroring deltas.md + fold.md but folding into SOUL.md. phases/6-verify.md
emits a voice delta; SKILL.md + SOUL.md.tmpl point at the loop. Docs-only, no engine change.

Run: python3 -m unittest test_soul_self_improve -v
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parent.parent
REPO = ADD_METHOD.parent
CANONICAL = ADD_METHOD / "skill" / "add"
BUNDLED = ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = REPO / ".claude" / "skills" / "add"
TMPL = ADD_METHOD / "tooling" / "templates" / "SOUL.md.tmpl"


def _read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class SoulSelfImprove(unittest.TestCase):
    def setUp(self):
        self.soul = _read(CANONICAL, "soul.md")
        self.soul_l = self.soul.lower()

    def test_soul_md_grammar(self):
        self.assertIn("[VOICE", self.soul, "soul.md must show the [VOICE · <status>] tag form")
        self.assertIn("(evidence:", self.soul,
                      "the voice delta must be closed by a required (evidence: …) clause")

    def test_lifecycle_open_confirmed(self):
        self.assertIn("open", self.soul_l)
        self.assertIn("confirmed", self.soul_l)

    def test_human_only_writer(self):
        self.assertIn("confirm", self.soul_l)
        self.assertTrue("only writer" in self.soul_l or "never self-approve" in self.soul_l,
                        "soul.md must state the human is the only writer / the AI never self-approves")

    def test_routes_to_soul_sections(self):
        for sec in ("Tone", "Communication style", "Trust", "Voice deltas"):
            self.assertIn(sec, self.soul, f"soul.md must route to SOUL.md's '{sec}' section")
        self.assertIn("newest-first", self.soul_l)

    def test_source_wordings_flow_not_memory(self):
        self.assertIn("wordings", self.soul_l)
        self.assertIn("flow", self.soul_l)
        self.assertIn("memory", self.soul_l,
                      "soul.md must explicitly exclude the human's private memory files")

    def test_reject_codes(self):
        self.assertIn("unconfirmed_voice_rewrite", self.soul_l)
        # a no-op-when-empty code and an unroutable code (names contain these stems)
        self.assertTrue("no_open" in self.soul_l or "no_voice" in self.soul_l,
                        "soul.md must name a no-op-when-nothing-open reject code")
        self.assertIn("unroutable", self.soul_l,
                      "soul.md must name an unroutable-voice-delta reject code")

    def test_observe_emits_voice_delta(self):
        # guide-recut: the Observe duties live in 6-verify.md's post-gate block now
        obs = _read(CANONICAL, "phases/6-verify.md")
        self.assertIn("voice delta", obs.lower(),
                      "6-verify.md must carry the voice-delta emit step")
        self.assertIn("soul.md", obs, "the emit step must point at soul.md")

    def test_skill_points_at_soul_md(self):
        skill = _read(CANONICAL, "SKILL.md")
        self.assertIn("soul.md", skill, "SKILL.md must point at soul.md so the loop is discoverable")

    def test_soul_template_points_at_loop(self):
        body = TMPL.read_text(encoding="utf-8")
        i = body.find("Voice deltas")
        self.assertNotEqual(i, -1, "SOUL.md.tmpl must keep its 'Voice deltas' section")
        self.assertIn("soul.md", body[i:], "the Voice deltas section must point at soul.md")

    def test_three_trees_identical(self):
        for rel in ("soul.md", "phases/6-verify.md", "SKILL.md"):
            digests = {_md5(t / rel) for t in (CANONICAL, BUNDLED, DOGFOOD)}
            self.assertEqual(len(digests), 1, f"{rel} diverged across the 3 skill trees")


if __name__ == "__main__":
    unittest.main()
