"""Red→green guard for suggestion-block §3 (FROZEN @ v1).

The decision-suggestion convention in report-template.md: the DECISION block presents a highlighted
recommended pick + 1–3 described alternatives at every HUMAN gate. Presentation-only — the engine is
untouched (a convention-guided seam). report-template.md stays byte-identical across the 3 skill homes.

unittest (repo convention). RED before build: the convention tokens (T1–T6) are absent from
report-template.md today; this guard fails until the build adds them to all 3 homes.

Maps to TASK.md: M1–M8 (Must) + the 3 reject codes (convention_absent · home_drift · tag_or_block_added).
"""
import hashlib
import os
import re
import sys
import unittest

# tests → suggestion-block → tasks → .add → repo root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_HOMES = [
    "add-method/skill/add/report-template.md",
    "add-method/src/add_method/_bundled/skill/add/report-template.md",
    ".claude/skills/add/report-template.md",
]
_CANONICAL = _HOMES[0]

# Closed v16 XML vocab — report-template.md may carry NO tag outside this set (M8 / tag_or_block_added).
_CLOSED_TAGS = {"prompt", "exit_gate", "constraints", "reject_codes", "output_format"}

# The frozen five-block list — exactly these labels, no 6th (M4 / tag_or_block_added).
_FIVE_BLOCKS = ["SUMMARY", "DECISION", "⚠ FLAGS", "EVIDENCE", "NEXT"]

# The required convention tokens the §3 contract freezes (T1–T6 → M1–M3, M5–M7).
# Each (label, token) must be present in the canonical report-template.md after build.
_REQUIRED_TOKENS = [
    ("M1 marker glyph", "▶"),
    ("M1 term", "recommended pick"),
    ("M1 single-rule", "exactly one"),
    ("M1 never-two", "never two"),
    ("M2 count", "1–3"),
    ("M2 degenerate case", "single recommended step"),
    ("M3 per-option description", "one-line description"),
    ("M5 AskUserQuestion", "AskUserQuestion"),
    ("M5 recommended label", "(Recommended)"),
    ("M5 tool-agnostic fallback", "numbered"),
    ("M6 human-gate scope", "[human gate]"),
    ("M6 autonomous exclusion", "[you drive]"),
    ("M7 confidence source", "confidence.md"),
    ("M7 human override", "override"),
]


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


class DecisionSuggestionConvention(unittest.TestCase):
    def setUp(self):
        self.text = _read(_CANONICAL)

    # ── M1–M3, M5–M7: the convention tokens (RED before build) ──────────────────────────────────
    def test_required_tokens_present(self):
        missing = [f"{label}: {tok!r}" for label, tok in _REQUIRED_TOKENS if tok not in self.text]
        self.assertEqual(missing, [], f"convention_absent — missing tokens: {missing}")

    # ── M4: refines block 2 only — the five-block list + show-before-ask survive ─────────────────
    def test_five_block_list_present(self):
        for label in _FIVE_BLOCKS:
            self.assertIn(label, self.text, f"five-block label dropped: {label}")

    def test_show_before_ask_preserved(self):
        self.assertIn("show-before-ask", self.text)
        self.assertIn("after EVIDENCE", self.text,
                       "the described choice must be the ASK, rendered after EVIDENCE (M4)")

    # ── M8: the binding rule is pinned INSIDE the <constraints> Hard rules block ─────────────────
    def test_recommended_pick_pinned_in_constraints(self):
        m = re.search(r"<constraints>(.*?)</constraints>", self.text, re.DOTALL)
        self.assertIsNotNone(m, "no <constraints> Hard rules block")
        block = m.group(1)
        self.assertIn("recommended pick", block,
                       "the recommended-pick rule must be pinned in the <constraints> Hard rules (M8)")
        self.assertIn("[human gate]", block,
                       "the human-gate-only scope must be pinned in the <constraints> Hard rules (M8)")

    # ── M8 / tag_or_block_added: no XML tag outside the closed vocab ─────────────────────────────
    def test_no_tag_outside_closed_vocab(self):
        tags = set(re.findall(r"</?([a-z_]+)>", self.text))
        offenders = tags - _CLOSED_TAGS
        self.assertEqual(offenders, set(),
                         f"tag_or_block_added — out-of-vocab tag(s): {sorted(offenders)}")

    # ── tag_or_block_added: exactly the five blocks in the fenced list, no 6th ───────────────────
    def test_no_sixth_block(self):
        # the block-list fence is the first ``` block that contains all five labels
        fences = re.findall(r"```\n(.*?)```", self.text, re.DOTALL)
        listing = next((f for f in fences if all(b in f for b in _FIVE_BLOCKS)), None)
        self.assertIsNotNone(listing, "five-block listing fence not found")
        labels = [ln.split()[0] if not ln.startswith("⚠") else "⚠"
                  for ln in listing.splitlines() if ln.strip()]
        self.assertEqual(len(labels), 5, f"five-block list must have exactly 5 entries, got {labels}")

    # ── home_drift: the 3 homes are byte-identical ──────────────────────────────────────────────
    def test_homes_byte_identical(self):
        digests = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in _HOMES}
        self.assertEqual(len(set(digests.values())), 1,
                         f"home_drift — homes differ: {digests}")


if __name__ == "__main__":
    unittest.main()
