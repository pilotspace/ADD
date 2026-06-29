#!/usr/bin/env python3
"""Red→green suite for v21 foundations-chapter (.add/tasks/foundations-chapter/TASK.md §3 FROZEN @ v1).

Pins the FROZEN contract: 15-foundations-and-lineage.md is a NARRATIVE lineage chapter that
NAMES the RSI closing-the-loop framing, the spec-kit↔ADD divergence triad, and the evidence chain,
and whose EVERY inline [Author Year] citation RESOLVES to an appendix-g entry key (the resolution
backbone). Inserting it between ch.14 and Appendix A repairs the sequential nav chain. Mirrored ×4
byte-identical, wired into the book TOC.

Every check PARSES the shipped artifact (asserts behaviour, never an internal): a build that ships
a dangling cite, drops a required anchor, forgets a copy, or breaks the nav chain turns one red.

RED until BUILD writes the chapter + repairs nav + wires the TOC: the chapter file is missing, so
the asserts fail for the RIGHT reason (no implementation yet), not a broken harness.

Run: python3 -m unittest test_foundations_chapter -v
"""
import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CHAPTER = "15-foundations-and-lineage.md"
APPENDIX_G = "appendix-g-references.md"
CH14 = "14-foundation.md"
APPENDIX_A = "appendix-a-templates.md"
README = "README.md"


def _copies_of(filename: str) -> dict[str, Path]:
    """The 4 book copies of a doc: root ./ · canonical · bundle · dogfood (.add/docs, gitignored)."""
    return {
        "root":      _REPO / filename,
        "canonical": _ADD_METHOD / "docs" / filename,
        "bundle":    _ADD_METHOD / "src" / "add_method" / "_bundled" / "docs" / filename,
        "dogfood":   _REPO / ".add" / "docs" / filename,
    }


CHAPTER_COPIES = _copies_of(CHAPTER)
CANONICAL = CHAPTER_COPIES["canonical"]
CANON_APPENDIX_G = _copies_of(APPENDIX_G)["canonical"]

# inline citation form [Author Year] / [Org 2026a] / [Surname et al. 2023] — year-anchored so it does
# NOT match nav/markdown links like [Contents](./README.md) or [Appendix A] (no year token).
_INLINE_CITE_RE = re.compile(r"\[([^\[\]]*\b(?:19|20)\d{2}[a-z]?)\]")
# the entry-lead key inside appendix-g: "- **Title** (Author Year) — …" → first (… Year) parenthetical.
_ENTRY_PREFIX = "- **"
_KEY_RE = re.compile(r"\(([^)]*\b(?:19|20)\d{2}[a-z]?)\)")

# the required core cite-set — one anchor per current + the evidence pair + the math anchor (§3).
REQUIRED_KEYS = (
    "Favaro & Clark 2026",       # RSI / framing / evidence
    "Anthropic 2026a",           # Automated Alignment Researchers (evidence chain)
    "Schluntz & Zhang 2024",     # agentic current
    "GitHub 2025",               # spec-kit
    "GSD 2025",                  # closest peer / divergence
    "Schmidhuber 2003",          # RSI math anchor
)
TESTS_FIRST_ANY = ("Mathews & Nagappan 2024", "Jimenez et al. 2023")  # ≥1 required


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _nav_line(text: str) -> str | None:
    """The prev/Contents/Next nav line — the one carrying the Contents back-link."""
    for ln in text.splitlines():
        if "](./README.md)" in ln and ("Next:" in ln or "←" in ln):
            return ln
    return None


def _appendix_g_keys() -> set[str]:
    """The valid cite-key set = the lead (Author Year) of every appendix-g entry line."""
    assert CANON_APPENDIX_G.exists(), f"appendix-g missing at {CANON_APPENDIX_G} (references-appendix not built?)"
    keys: set[str] = set()
    for ln in _read(CANON_APPENDIX_G).splitlines():
        if ln.startswith(_ENTRY_PREFIX):
            m = _KEY_RE.search(ln)          # FIRST year-parenthetical = the entry's cite-key
            if m:
                keys.add(m.group(1).strip())
    return keys


class FoundationsChapterTest(unittest.TestCase):
    def _chapter(self) -> str:
        self.assertTrue(CANONICAL.exists(),
                        f"missing {CANONICAL} — BUILD has not written the chapter yet")
        return _read(CANONICAL)

    # 1 — exists in all copies, byte-identical (mirror_drift)
    def test_chapter_exists_in_copies_byte_identical(self):
        required = {k: CHAPTER_COPIES[k] for k in ("root", "canonical", "bundle")}
        missing = [name for name, p in required.items() if not p.exists()]
        self.assertEqual(missing, [], f"required chapter copies missing: {missing}")
        present = {name: p for name, p in CHAPTER_COPIES.items() if p.exists()}  # dogfood iff present
        digests = {name: _md5(p) for name, p in present.items()}
        self.assertEqual(len(set(digests.values())), 1,
                         f"chapter copies not byte-identical (mirror_drift): {digests}")

    # 2 — RSI closing-the-loop framing named
    def test_closing_the_loop_framing_named(self):
        low = self._chapter().lower()
        self.assertIn("closing the loop", low, "the RSI 'closing the loop' framing is not named")
        self.assertTrue("human-gated" in low or "evidence-trusted" in low,
                        "ADD is not cast as the human-gated / evidence-trusted instance")
        self.assertTrue(re.search(r"recursive self-improvement|\brsi\b", low),
                        "recursive self-improvement is not named")

    # 3 — divergence triad named in full (divergence_incomplete)
    def test_divergence_triad_named(self):
        text = self._chapter()
        low = text.lower()
        self.assertTrue(re.search(r"tests?-first|failing.?test", low),
                        "divergence triad omits the failing-tests-first gate")
        self.assertIn("fold", low, "divergence triad omits observe→fold")
        self.assertTrue(re.search(r"dynamic.{0,12}loop|goal.?loop|hold.{0,8}reopen", low),
                        "divergence triad omits the dynamic goal-loop")

    # 4 — evidence chain present (evidence_chain_absent)
    def test_evidence_chain_present(self):
        low = self._chapter().lower()
        self.assertTrue(re.search(r"time.?horizon", low),
                        "evidence chain omits the task time-horizon")
        self.assertTrue("80%" in low or "claude-authored" in low or "claude authored" in low,
                        "evidence chain omits the >80%-Claude-authored figure")
        self.assertTrue(re.search(r"automated alignment researcher", low),
                        "evidence chain omits the Automated Alignment Researchers result")

    # 5 — THE RESOLUTION BACKBONE: every inline cite resolves to an appendix-g key (dangling_citation)
    def test_every_inline_cite_resolves(self):
        text = self._chapter()
        keys = _appendix_g_keys()
        self.assertTrue(keys, "appendix-g produced no cite-keys — extraction or appendix is broken")
        cites = {m.group(1).strip() for m in _INLINE_CITE_RE.finditer(text)}
        self.assertTrue(cites, "the chapter carries no inline [Author Year] citation")
        dangling = sorted(cites - keys)
        self.assertEqual(dangling, [],
                         f"inline cites resolve to no appendix-g entry (dangling_citation): {dangling}")

    # 6 — required core cite-set present AND resolving
    def test_required_core_cites_present(self):
        text = self._chapter()
        keys = _appendix_g_keys()
        cites = {m.group(1).strip() for m in _INLINE_CITE_RE.finditer(text)}
        for key in REQUIRED_KEYS:
            self.assertIn(key, cites, f"required anchor not cited in the chapter: [{key}]")
            self.assertIn(key, keys, f"required anchor does not resolve to appendix-g: [{key}]")
        self.assertTrue(any(k in cites for k in TESTS_FIRST_ANY),
                        f"no tests-first anchor cited (need ≥1 of {TESTS_FIRST_ANY})")

    # 7 — wired into the book TOC (orphan_chapter)
    def test_chapter_in_toc(self):
        # The book's own index (docs/README.md) is the chapter TOC, mirrored across the tracked
        # book trees (canonical + bundle). The repo-root README is a marketing landing page, not a
        # chapter index, so it is no longer a TOC surface here; the gitignored dogfood copy is
        # checked opportunistically when present.
        toc_copies = {k: p for k, p in _copies_of(README).items()
                      if k in ("canonical", "bundle", "dogfood")}
        checked = 0
        for name, p in toc_copies.items():
            if name in ("canonical", "bundle"):
                self.assertTrue(p.exists(), f"TOC index missing: {p}")
            if not p.exists():
                continue
            self.assertIn(CHAPTER, _read(p),
                          f"chapter not linked in TOC {name} (orphan_chapter): {p}")
            checked += 1
        self.assertGreaterEqual(checked, 2, "fewer than the 2 required TOC indexes checked")

    # 8 — sequential nav chain intact across the ch.14 → ch.15 → Appendix A boundary
    def test_nav_chain_intact(self):
        # ch.15: sits between 14 and Appendix A
        ch15_nav = _nav_line(self._chapter())
        self.assertIsNotNone(ch15_nav, "ch.15 has no nav line")
        self.assertIn(CH14, ch15_nav, "ch.15 prev does not point to ch.14")
        self.assertIn(APPENDIX_A, ch15_nav, "ch.15 Next does not point to Appendix A")
        # ch.14: Next re-points to ch.15 (not Appendix A) — checked in every copy present
        for name, p in _copies_of(CH14).items():
            if not p.exists():
                continue
            nav = _nav_line(_read(p))
            self.assertIsNotNone(nav, f"ch.14 ({name}) has no nav line")
            self.assertIn(CHAPTER, nav, f"ch.14 ({name}) Next not re-pointed to ch.15: {nav}")
            self.assertNotIn(APPENDIX_A, nav,
                             f"ch.14 ({name}) Next still points at Appendix A (stale nav): {nav}")
        # Appendix A: back-pointer re-points to ch.15 (corrects the pre-existing 13-skip)
        for name, p in _copies_of(APPENDIX_A).items():
            if not p.exists():
                continue
            nav = _nav_line(_read(p))
            self.assertIsNotNone(nav, f"Appendix A ({name}) has no nav line")
            self.assertIn(CHAPTER, nav, f"Appendix A ({name}) back-pointer not re-pointed to ch.15: {nav}")

    # 9 — no unverified marker shipped
    def test_no_unverified_token(self):
        self.assertNotIn("unverified", self._chapter().lower(),
                         "an [UNVERIFIED] / 'unverified' marker shipped in the chapter")


if __name__ == "__main__":
    unittest.main(verbosity=2)
