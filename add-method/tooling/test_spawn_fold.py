"""test_spawn_fold — the spawn-fold fold (milestone flow-simplification, Design C′).

Scope (resolved at v3, change-request from v2): fold ONLY the one genuine duplicate — advisor.md's
tier model-id MAPPING (`mid→sonnet / top→opus`), which copies streams.md's authoritative tier
table. advisor's `## Choosing the model` body becomes a one-line pointer at streams.md.

What this fold does NOT touch (the v2 finding): advisor's `## The plan-following prompt template`
is advisory-SPECIFIC content (the `{{PIECE}}`/verdict-only block), NOT a duplicate of streams' full
locked-task contract — it STAYS. streams.md is byte-untouched.

This suite fences Design C′:
  · streams.md is the tier-table home (mid/top/sonnet/opus present) and keeps the sonnet/opus mapping.
  · advisor's tier section references streams.md and no longer repeats the sonnet/opus mapping
    ("duplication_remains" if the mapping survives in advisor).
  · advisor STILL carries its fenced advisory template ({{PIECE}}/verdict) — "behavior_drift" (the
    v2 over-removal) if it was dropped.

Owning task: spawn-fold (milestone flow-simplification). RED until advisor's tier mapping is folded.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
_ADVISOR = _SKILL / "advisor.md"
_STREAMS = _SKILL / "streams.md"

# reuse the xml-convention helpers (one vocabulary, no drift)
_spec = importlib.util.spec_from_file_location("xmlconv_for_spawnfold", _TOOLING / "test_xml_convention.py")
_xmlconv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_xmlconv)  # type: ignore[union-attr]

# advisor's advisory template tags (a subset of the worker contract, filled advisory-specifically)
TEMPLATE_TAGS = {"objective", "persona", "context_files", "return"}
TIER_TOKENS = ("mid", "top", "sonnet", "opus")

_H_TIERS = "## Choosing the model — vendor-neutral tiers"
_H_TEMPLATE = "## The plan-following prompt template"


class TestSpawnFold(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for p in (_ADVISOR, _STREAMS):
            assert p.exists(), f"missing guide: {p}"
        cls.advisor = _ADVISOR.read_text(encoding="utf-8")
        cls.streams = _STREAMS.read_text(encoding="utf-8")

    # ── streams.md is the tier-table home (untouched) ────────────────────────────────────
    def test_streams_is_tier_home(self) -> None:
        low = self.streams.lower()
        for tok in TIER_TOKENS:
            self.assertIn(tok, low, f"streams.md (the tier home) is missing tier token: {tok}")

    def test_streams_tier_table_untouched(self) -> None:
        # the sonnet/opus model-id mapping must remain in streams.md (the fold moves it OUT of advisor, not streams)
        low = self.streams.lower()
        self.assertTrue(("sonnet" in low) and ("opus" in low),
                        "streams.md must keep the sonnet/opus tier mapping (the authoritative home)")

    # ── advisor's tier section folds to a streams pointer (the one duplicate) ─────────────
    def test_advisor_tier_section_references_streams(self) -> None:
        body = _xmlconv._section(self.advisor, _H_TIERS)
        self.assertTrue(body, f"advisor.md dropped the heading {_H_TIERS!r} (xml_convention registry expects it)")
        self.assertIn("streams.md", body,
                      f"advisor's {_H_TIERS!r} must POINT at streams.md (broken_reference)")
        low = body.lower()
        self.assertFalse(("sonnet" in low) and ("opus" in low),
                         "advisor still repeats the sonnet/opus model-id mapping — fold it to a streams "
                         "pointer (duplication_remains)")

    # ── advisor KEEPS its advisory template (behavior-preserving — the v2 finding) ────────
    def test_advisor_keeps_advisory_template(self) -> None:
        body = _xmlconv._section(self.advisor, _H_TEMPLATE)
        self.assertTrue(body, f"advisor.md dropped the heading {_H_TEMPLATE!r}")
        present = TEMPLATE_TAGS & _xmlconv._paired_tags(self.advisor)
        self.assertEqual(present, TEMPLATE_TAGS,
                         f"advisor lost advisory template tags {sorted(TEMPLATE_TAGS - present)} — "
                         f"the advisory template must stay (behavior_drift / v2 over-removal)")
        self.assertIn("{{PIECE}}", self.advisor,
                      "advisor's advisory template must keep its {{PIECE}} framing (behavior_drift)")
        self.assertIn("do not record state", self.advisor.lower(),
                      "advisor's advisory template must keep the verdict-only 'do not record state' rule")


if __name__ == "__main__":
    unittest.main(verbosity=2)
