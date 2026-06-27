"""test_advisor_strategy — guards skill/add/advisor.md, the advisor subagent-spawn strategy.

The advisor is TOOL-AGNOSTIC: the engine never spawns; the orchestrating agent chooses to
spawn a single subagent to follow its plan, and the subagent only PROPOSES (the orchestrator
records). This suite asserts the doc states that, carries the when/when-not decision, a fenced
plan-following prompt template, the vendor-neutral tier pick, the confidence-self-score link,
and that the frozen-vocab guard COVERS the doc (advisor.md ∈ ENGINE_FILES) while the template's
fenced worker tags stay exempt.

Owning task: advisor-strategy (milestone advisor-context). RED until advisor.md exists + is
registered; GREEN after.
"""
from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_DOC = _TOOLING.parent / "skill" / "add" / "advisor.md"
_STREAMS = _TOOLING.parent / "skill" / "add" / "streams.md"   # the canonical worker-contract HOME (spawn-fold, Design C)

_spec = importlib.util.spec_from_file_location(
    "xmlconv_for_advisor", _TOOLING / "test_xml_convention.py")
_xmlconv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_xmlconv)  # type: ignore[union-attr]

# the worker-contract tags the fenced template reuses (mirrors test_xml_convention.WORKER_CONTRACT_TAGS).
# spawn-fold (Design C′) keeps advisor's advisory template; only the tier MAPPING folds to streams.md.
_TEMPLATE_TAGS = {"objective", "persona", "return"}


class TestAdvisorStrategy(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert _DOC.exists(), f"advisor.md missing: {_DOC}"
        assert _STREAMS.exists(), f"streams.md (worker-contract home) missing: {_STREAMS}"
        cls.text = _DOC.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()
        cls.stripped = _xmlconv._strip_code_fences(cls.text)
        cls.streams = _STREAMS.read_text(encoding="utf-8")
        cls.streams_lower = cls.streams.lower()

    def test_intro_names_advisor_and_plan(self) -> None:
        self.assertIn("advisor", self.lower, "intro must name the advisor strategy")
        self.assertIn("plan", self.lower, "the subagent follows the orchestrator's plan")

    def test_when_and_when_not(self) -> None:
        self.assertTrue(("when to spawn" in self.lower) or ("spawn when" in self.lower),
                        "must state WHEN to spawn")
        self.assertTrue(("when not" in self.lower) or ("in-context" in self.lower)
                        or ("in context" in self.lower) or ("do not spawn" in self.lower),
                        "must state the in-context default (when NOT to spawn)")

    def test_template_is_fenced(self) -> None:
        # advisor KEEPS its advisory template (spawn-fold C′ folds only the tier mapping). raw text
        # carries the worker tags; after fence-strip they are gone (⇒ they live in a code fence).
        raw_tags = _xmlconv._paired_tags(self.text)
        self.assertTrue(_TEMPLATE_TAGS <= raw_tags,
                        f"plan-following template missing tags: {sorted(_TEMPLATE_TAGS - raw_tags)}")
        leaked = _TEMPLATE_TAGS & _xmlconv._paired_tags(self.stripped)
        self.assertEqual(leaked, set(),
                         f"template tags {sorted(leaked)} leaked OUTSIDE a code fence — must stay fenced/exempt")

    def test_tier_pick_reuses_streams(self) -> None:
        # spawn-fold C′: the tier vocabulary lives at the home (streams.md); advisor references it
        # rather than repeating the sonnet/opus mapping — a pointer, not a 2nd copy.
        for token in ("mid", "top", "sonnet", "opus"):
            self.assertIn(token, self.streams_lower, f"streams.md (the home) missing tier vocabulary: {token}")
        self.assertIn("streams.md", self.lower, "tier pick must point at streams.md (one vocabulary)")

    def test_subagent_self_scores_and_proposes(self) -> None:
        self.assertIn("confidence.md", self.lower, "the spawned subagent must self-score via confidence.md")
        self.assertTrue(("propose" in self.lower) or ("records" in self.lower),
                        "subagent PROPOSES, orchestrator RECORDS")

    def test_engine_never_spawns_constraints(self) -> None:
        block = re.search(r"<constraints>(.*?)</constraints>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "missing the tool-agnostic <constraints> block")
        body = block.group(1).lower()
        self.assertIn("engine never spawns", body,
                      "the <constraints> block must state the engine never spawns")
        self.assertIn("propose", body, "the <constraints> block must state the subagent only proposes")

    def test_vocab_subset_outside_fence(self) -> None:
        tags = _xmlconv._paired_tags(self.stripped)
        self.assertTrue(tags, "advisor.md carries no outside-fence paired tag (not converted)")
        offenders = tags - {"constraints"}
        self.assertFalse(offenders, f"out-of-subset outside-fence tags {sorted(offenders)} (engine doc: only constraints)")

    def test_registered_in_engine_files(self) -> None:
        self.assertIn("advisor.md", _xmlconv.ENGINE_FILES,
                      "advisor.md not registered in test_xml_convention.ENGINE_FILES")
        self.assertEqual(_xmlconv.ENGINE_FILES["advisor.md"]["tags"], {"constraints"},
                         "advisor.md must register tags={'constraints'}")

    def test_strategy_block_fenced_and_points_at_section5(self) -> None:
        # build-strategy-solutions ADD-3: the fenced template gains a <strategy> element that
        # mirrors the task's §5 (Strategy + Known-problem fixes). It must stay INSIDE the fence
        # (present raw, gone after fence-strip) so the outside-fence vocab stays {constraints}.
        self.assertIn("strategy", _xmlconv._paired_tags(self.text),
                      "fenced plan-following template missing the <strategy> element")
        self.assertNotIn("strategy", _xmlconv._paired_tags(self.stripped),
                         "<strategy> leaked OUTSIDE the code fence — must stay fenced/exempt")
        block = re.search(r"<strategy>(.*?)</strategy>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "no <strategy>…</strategy> block")
        self.assertIn("§5", block.group(1), "the <strategy> block must point at the task's §5")


if __name__ == "__main__":
    unittest.main()
