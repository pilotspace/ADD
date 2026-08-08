"""Red→green guard for compact-book-align §3 (FROZEN @ v1).

The book + glossary catch up to the shipped foundation-compaction ritual: ch9 (`09-the-loop.md`)
reconciles its append-only prose to newest-first AND gains a "Foundation compaction" passage; the
4 new terms land in all 3 glossary TYPES (appendix-c ×4 · template ×3 · dogfood ×1), each as an
OWN ENTRY in that type's native format. Engine untouched.

RED drivers (fail until the docs are edited): test_ch9_reads_newest_first ·
  test_ch9_documents_compaction · test_ch9_names_shapes_and_ordering · test_glossary_has_4_terms.
DISCLOSED green-at-red regression guards: test_doc_mirror_parity · test_no_engine_creep ·
  test_slang_clean_additions (nothing to scan until the passage exists).

unittest (repo convention). Run: python3 -m unittest discover -s tests
"""
import hashlib
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

# book is synced ×4 (root · canonical · bundle · dogfood) — matches the engine sync guards
_CH9 = ["09-the-loop.md",
        "add-method/docs/09-the-loop.md",
        "add-method/src/add_method/_bundled/docs/09-the-loop.md",
        ".add/docs/09-the-loop.md"]
_APPENDIX = ["appendix-c-glossary.md",
             "add-method/docs/appendix-c-glossary.md",
             "add-method/src/add_method/_bundled/docs/appendix-c-glossary.md",
             ".add/docs/appendix-c-glossary.md"]
# template is synced ×3 (canonical · bundle · dogfood)
_TMPL = ["add-method/tooling/templates/GLOSSARY.md.tmpl",
         "add-method/src/add_method/_bundled/tooling/templates/GLOSSARY.md.tmpl",
         ".add/tooling/templates/GLOSSARY.md.tmpl"]
_DOGFOOD = ".add/GLOSSARY.md"
_ENGINES = ["add-method/tooling/add.py", ".add/tooling/add.py"]
_TERMS = ["foundation compaction", "rolled-up settled line", "per-spec shape", "newest-first append-only"]
_BANS = {"seam": r"\bseams?\b", "fold": r"\bfold(s|ed|ing)?\b", "survivor": r"\bsurvivors?\b"}


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def _consolidation_section(text):
    m = re.search(r"## Lessons learned and the retrospective consolidation\n(.*?)(?=\n## )", text, re.S)
    return m.group(1) if m else ""


def _compaction_passage(section):
    """The 'Foundation compaction' passage within the consolidation section (lowercased)."""
    m = re.search(r"foundation compaction(.*)$", _norm(section), re.S)
    return m.group(0) if m else ""


class CompactBookAlignTest(unittest.TestCase):
    # ---- RED drivers --------------------------------------------------------
    def test_ch9_reads_newest_first(self):
        sec = _norm(_consolidation_section(_read(_CH9[0])))
        self.assertIn("prepend", sec, "ch9 consolidation prose does not say prepend (newest-first)")
        self.assertNotIn("appends one row", sec, "ch9 still says the contradictory 'appends one row'")

    def test_ch9_documents_compaction(self):
        p = _compaction_passage(_consolidation_section(_read(_CH9[0])))
        self.assertTrue(p, "ch9 has no 'Foundation compaction' passage")
        self.assertTrue(re.search(r"separate|distinct step", p), "passage must mark compaction SEPARATE from the consolidation")
        self.assertIn("ai proposes", p, "passage must say the AI PROPOSES (not decides)")  # refute-read hardening
        self.assertIn("human confirms", p, "passage must say AI proposes / human confirms")
        self.assertTrue("never delete" in p or "summarize" in p, "passage must state never-delete (summarize + point)")
        self.assertIn("see git", p, "passage must keep the git pointer")
        self.assertIn("add.py compact", p, "passage must distinguish the engine `add.py compact`")

    def test_ch9_names_shapes_and_ordering(self):
        p = _compaction_passage(_consolidation_section(_read(_CH9[0])))
        for spec in ("spec", "key", "conventions", "glossary", "model_registry"):
            self.assertIn(spec, p, f"passage does not name the {spec} per-spec shape")
        self.assertIn("newest-first", p, "passage must name newest-first ordering")
        self.assertTrue("bottom" in p or "tail" in p, "passage must place the settled line at the bottom/tail")

    def test_glossary_has_4_terms(self):
        """Each term has its OWN ENTRY in the home's native format — not a bare
        substring inside another entry's body (refute-read hardening: e.g. the
        'foundation compaction' body mentions 'rolled-up settled line', so a plain
        assertIn would green even if that term's own entry were deleted)."""
        for rel in _APPENDIX:           # book: bold em-dash `**Term** —`
            text = _read(rel)
            for term in _TERMS:
                pat = r"(?im)^\s*\*\*" + re.escape(term) + r"\*\*\s*[—-]"
                self.assertRegex(text, pat, f"{rel}: no bold own-entry for '{term}'")
        for rel in _TMPL + [_DOGFOOD]:  # template/dogfood: colon form `term: …`
            text = _read(rel)
            for term in _TERMS:
                pat = r"(?im)^\s*" + re.escape(term) + r"\s*:"
                self.assertRegex(text, pat, f"{rel}: no colon own-entry for '{term}'")

    # ---- DISCLOSED green-at-red regression guards ---------------------------
    def test_doc_mirror_parity(self):
        for group in (_CH9, _APPENDIX, _TMPL):
            d = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in group}
            self.assertEqual(len(set(d.values())), 1, f"mirror-drift across {group[0]} homes: {d}")

    def test_no_engine_creep(self):
        for eng in _ENGINES:
            src = _read(eng)
            self.assertNotIn("compact-foundation", src, f"{eng}: engine references the ritual guide")
            self.assertNotIn("rolled-up settled line", src, f"{eng}: engine encodes a compaction term")

    def test_slang_clean_additions(self):
        """The new term lines + the compaction passage carry no bare seam/fold/survivor in prose."""
        targets = [_compaction_passage(_consolidation_section(_read(_CH9[0])))]
        for rel in _APPENDIX[:1] + _TMPL[:1] + [_DOGFOOD]:
            for line in _read(rel).splitlines():
                if any(term in _norm(line) for term in _TERMS):
                    targets.append(_norm(line))
        for chunk in targets:
            prose = re.sub(r"`[^`]+`", "", chunk)  # code-spans exempt
            for slug, pat in _BANS.items():
                self.assertIsNone(re.search(pat, prose), f"banned idiom '{slug}' in an addition: {chunk[:80]}")


if __name__ == "__main__":
    unittest.main()
