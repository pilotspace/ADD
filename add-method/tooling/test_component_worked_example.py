#!/usr/bin/env python3
"""Red/green tests for `component-worked-example` (milestone component-polish, the
capstone task).

A DOCS task — no engine change. It (a) adds a multi-component BE->FE worked example to
Appendix D, and (b) absorbs the milestone's open doc-deltas: the four new fail-loud codes
shipped by federation-harden / cross-component-recency / component-registry-fill, plus the
per-component `verify`-command surfacing, documented in ch.17, the glossary, and the skill
component beat.

The guards:
  - WORKED EXAMPLE — Appendix D carries a "Multi-component" section naming the pillar's
    moving parts (components.toml, produces:/consumes:, federate), with the existing
    single-component example preserved.
  - DOC-TRUTH — every code the docs newly name is a real literal in add.py (no drift of
    the `green-bar`-vs-`green_bar` class).
  - CODES DOCUMENTED — the four new codes appear in ch.17, the glossary, and the skill beat.
  - VERIFY-SURFACING — ch.17 / the skill beat state the component `verify` command is
    surfaced at the gate (NO-EXEC).
  - PARITY — the touched book files are byte-identical across their 4 trees; the skill file
    across its 3 trees (this task's scoped echo of test_book_parity / the skill parity).

    python3 -m unittest test_component_worked_example -v
"""
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent              # add-method/tooling
ADD_METHOD = HERE.parent                            # add-method
REPO = ADD_METHOD.parent                            # repo root
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

ADD_PY = HERE / "add.py"

# --- the four new codes this milestone shipped (the doc-deltas being absorbed) ---
NEW_CODES = (
    "federation_source_escapes",      # federation-harden
    "producer_contract_stale",        # cross-component-recency
    "contract_producer_stale",        # cross-component-recency (check WARN)
    "contract_snapshot_hashless",     # cross-component-recency (R1 WARN)
)

# --- book files this task edits, each across 4 trees (canon · root · dogfood · bundle) ---
BOOK_FILES = ("appendix-d-worked-example.md", "17-components.md", "appendix-c-glossary.md")


def _book_trees(name: str):
    return (
        ADD_METHOD / "docs" / name,
        REPO / name,                              # the repo-root mirror (test_book_parity)
        REPO / ".add" / "docs" / name,            # the dogfood mirror
        BUNDLE / "docs" / name,                   # the package bundle
    )


SKILL_TREES = (
    ADD_METHOD / "skill" / "add" / "components.md",
    REPO / ".claude" / "skills" / "add" / "components.md",
    BUNDLE / "skill" / "add" / "components.md",
)

APPENDIX_D = ADD_METHOD / "docs" / "appendix-d-worked-example.md"
CH17 = ADD_METHOD / "docs" / "17-components.md"
GLOSSARY = ADD_METHOD / "docs" / "appendix-c-glossary.md"
SKILL_BEAT = ADD_METHOD / "skill" / "add" / "components.md"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class WorkedExample(unittest.TestCase):
    """Appendix D gains the multi-component BE->FE transcript."""

    def setUp(self):
        self.text = APPENDIX_D.read_text(encoding="utf-8")

    def test_multicomponent_section_present(self):
        # a new section heading mentioning multi-component
        self.assertRegex(self.text, r"(?im)^#{2,3} .*multi-?component")

    def test_names_the_pillar_moving_parts(self):
        for token in ("components.toml", "produces:", "consumes:", "federate"):
            self.assertIn(token, self.text, f"worked example missing {token!r}")

    def test_be_to_fe_slice_named(self):
        # the producer/consumer/contract identities the transcript walks
        for token in ("gateway", "web", "orders"):
            self.assertIn(token, self.text, f"worked example missing component id {token!r}")

    def test_single_component_example_preserved(self):
        # the original money-transfer transcript stays — its anchor headings remain
        self.assertIn("Step 1 — Specify", self.text)
        self.assertIn("transfer", self.text)


class DocTruth(unittest.TestCase):
    """Every code the docs newly name is a real literal in the engine."""

    def test_new_codes_are_real_engine_literals(self):
        engine = ADD_PY.read_text(encoding="utf-8")
        for code in NEW_CODES:
            self.assertIn(code, engine, f"doc-truth: {code} is not a literal in add.py")


class CodesDocumented(unittest.TestCase):
    """The four new codes land in ch.17, the glossary, and the skill beat."""

    def test_codes_in_chapter_17(self):
        text = CH17.read_text(encoding="utf-8")
        # ch.17 must name the two operator-facing HARD-STOP/WARN codes at least
        for code in ("federation_source_escapes", "producer_contract_stale"):
            self.assertIn(code, text, f"ch.17 missing {code}")

    def test_codes_in_glossary(self):
        text = GLOSSARY.read_text(encoding="utf-8")
        for code in NEW_CODES:
            self.assertIn(code, text, f"glossary missing {code}")

    def test_codes_in_skill_beat(self):
        text = SKILL_BEAT.read_text(encoding="utf-8")
        for code in ("federation_source_escapes", "producer_contract_stale"):
            self.assertIn(code, text, f"skill beat missing {code}")


class VerifySurfacing(unittest.TestCase):
    """The per-component verify-command surfacing (NO-EXEC) is documented."""

    def test_chapter_17_documents_verify_surfacing(self):
        text = CH17.read_text(encoding="utf-8").lower()
        self.assertIn("verify", text)
        self.assertIn("surface", text)


class Parity(unittest.TestCase):
    """The touched files stay byte-identical across their trees."""

    def test_book_files_byte_identical_across_four_trees(self):
        for name in BOOK_FILES:
            trees = _book_trees(name)
            present = [p for p in trees if p.is_file()]
            self.assertEqual(
                len(present), len(trees),
                f"{name}: missing tree(s): "
                + ", ".join(str(p) for p in trees if not p.is_file()),
            )
            digests = {_md5(p) for p in trees}
            self.assertEqual(len(digests), 1, f"{name}: diverged across its 4 book trees")

    def test_skill_beat_byte_identical_across_three_trees(self):
        present = [p for p in SKILL_TREES if p.is_file()]
        self.assertEqual(
            len(present), len(SKILL_TREES),
            "skill components.md missing tree(s): "
            + ", ".join(str(p) for p in SKILL_TREES if not p.is_file()),
        )
        digests = {_md5(p) for p in SKILL_TREES}
        self.assertEqual(len(digests), 1, "skill components.md diverged across its 3 trees")


if __name__ == "__main__":
    unittest.main(verbosity=2)
