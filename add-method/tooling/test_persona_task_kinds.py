#!/usr/bin/env python3
"""Red/green tests for persona-task-kinds (ADD 2.0 M1 persona-core).

CONTRACT: personas become measurable per KIND of work. A closed task-kind
taxonomy (constants.TASK_KINDS) is the join key between a persona's routing
claim (`task-kinds:` frontmatter) and a task's declared kind (`kind:` header
line, same anchored grammar family as route:/sensitivity:). Everything is
measure-not-block: an unknown kind is a named WARN finding, never a refusal.

- constants.TASK_KINDS — the closed vocabulary, lowercase, no duplicates.
- add._task_kind(header) — PURE header reader: the declared kind, or None.
- add._persona_quality_warnings gains Finding C: a `task-kinds:` value outside
  the taxonomy is named; a valid list and an absent line stay clean.
- templates/personas/_template.md.tmpl carries a `task-kinds:` slot.

Run: python3 -m unittest test_persona_task_kinds -v
"""
from __future__ import annotations

import unittest
from pathlib import Path

import add
from add_engine import constants

TOOLING = Path(__file__).resolve().parent
TEMPLATE = TOOLING / "templates" / "personas" / "_template.md.tmpl"


def _persona(extra_fm: str = "", body_extra: str = "") -> str:
    """A conformant persona with optional extra frontmatter lines."""
    return ("---\nname: X\nvibe: y\nflow: build\n" + extra_fm + "---\n"
            "## Identity\nA specialist.\n\n## Critical Rules\n- rule\n\n"
            "## Default Requirement\nreq.\n\n## Success Metrics\n- metric\n"
            + body_extra)


class TaxonomyConstantTest(unittest.TestCase):
    # Must: the taxonomy is a closed, lowercase, duplicate-free tuple
    def test_taxonomy_exists_closed(self):
        kinds = constants.TASK_KINDS
        self.assertIsInstance(kinds, tuple, "TASK_KINDS must be a closed tuple")
        self.assertGreaterEqual(len(kinds), 8, "the taxonomy covers the work spectrum")
        self.assertEqual(len(kinds), len(set(kinds)), "no duplicate kinds")
        for k in kinds:
            self.assertEqual(k, k.lower(), f"kind '{k}' must be lowercase")
            self.assertNotIn(" ", k, f"kind '{k}' must be a single token")

    # Must: the kinds every project needs are present by name
    def test_core_kinds_present(self):
        for k in ("feature", "refactor", "test", "docs", "ui",
                  "security", "data", "infra", "release", "integration"):
            self.assertIn(k, constants.TASK_KINDS, f"'{k}' missing from TASK_KINDS")

    # Must: exported like its sibling persona constants
    def test_taxonomy_exported(self):
        self.assertIn("TASK_KINDS", constants.__all__)


class TaskKindReaderTest(unittest.TestCase):
    # Must: a declared kind is read verbatim
    def test_reads_declared_kind(self):
        hdr = "slug: t · created: x\nkind: security\nphase: direction\n"
        self.assertEqual(add._task_kind(hdr), "security")

    # Reject absence_is_conformant: no kind: line -> None, never a guess
    def test_absent_kind_is_none(self):
        hdr = "slug: t · created: x\nphase: direction\n"
        self.assertIsNone(add._task_kind(hdr))

    # Reject prose_is_not_declaration: 'kind:' mid-prose must not match
    def test_prose_kind_not_declaration(self):
        hdr = "slug: t\ntitle: what kind: of thing is this\n"
        self.assertIsNone(add._task_kind(hdr))

    # Boundary: surrounding whitespace tolerated, value normalized lowercase
    def test_whitespace_and_case(self):
        self.assertEqual(add._task_kind("kind:   Feature  \n"), "feature")


class PersonaTaskKindsWarningTest(unittest.TestCase):
    # Must: a valid comma-separated task-kinds list is clean
    def test_valid_kinds_clean(self):
        findings = add._persona_quality_warnings(
            _persona(extra_fm="task-kinds: feature, security\n"))
        self.assertEqual(findings, [])

    # Accept (Finding C): an unknown kind is NAMED in the finding
    def test_unknown_kind_named(self):
        findings = add._persona_quality_warnings(
            _persona(extra_fm="task-kinds: feature, featur\n"))
        self.assertTrue(any("featur" in f for f in findings),
                        f"the bad kind must be named: {findings}")

    # Reject absence_is_conformant: no task-kinds line -> no Finding C
    def test_absent_task_kinds_clean(self):
        self.assertEqual(add._persona_quality_warnings(_persona()), [])

    # Must: measure-not-block — a bad kind never raises, only warns
    def test_warning_never_raises(self):
        try:
            add._persona_quality_warnings(_persona(extra_fm="task-kinds: bogus\n"))
        except Exception as e:  # pragma: no cover
            self.fail(f"quality predicate must never raise: {e}")


class TemplateSlotTest(unittest.TestCase):
    # Must: the shipped persona template carries the task-kinds slot
    def test_template_has_task_kinds_slot(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("task-kinds:", text,
                      "_template.md.tmpl must carry a task-kinds: frontmatter slot")


if __name__ == "__main__":
    unittest.main()
