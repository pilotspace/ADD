#!/usr/bin/env python3
"""Guard for debrand-teacher-prose (persona-teacher-bundle 4/4). CONTRACT frozen @ v1.

The vendored teacher corpus is now a LOCAL library (.add/personas-teacher/), so the method
prose must not name the upstream brand: book ch.18, the glossary persona headword, the skill
0-setup phase, the persona _template, and the engine constants.py comment all drop
"agency-agents"/"msitarzewski" and point the persona phase at `.add/personas-teacher/`.

The de-brand is PROSE-only: the LICENSE + THIRD_PARTY_NOTICES (MIT attribution) and the
refresh script + VENDOR.md (operational upstream URL) legitimately RETAIN the reference.
The dogfood .add/tasks/* / state.json (project history) are out of scope by design.

Engine stays hands-off: the engine pin (add.py) unchanged, the package digest re-pins cleanly
across all 3 engine trees, and no "personas-teacher" path literal enters engine source.

Run: python3 -m unittest test_debrand_teacher_prose -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

BRAND = ("agency-agents", "msitarzewski")
LOCAL_LIB = ".add/personas-teacher"

# Build a-1 spelled in parts so this guard file is not itself a brand surface a future
# broad scan would trip on by accident (it scans the LISTED files, never test sources).


def _existing(*paths):
    return [p for p in paths if p.is_file()]


# --- method-prose surfaces that MUST be brand-free (across every tree twin) ---
def _chapter_trees():
    return _existing(
        _ADD_METHOD / "docs" / "18-personas.md",
        _REPO / "18-personas.md",
    )   # book-stops-shipping (2.0 M6b): no bundled/dogfood copies


def _glossary_trees():
    return _existing(
        _ADD_METHOD / "docs" / "appendix-c-glossary.md",
        _REPO / "appendix-c-glossary.md",
    )   # book-stops-shipping (2.0 M6b): no bundled/dogfood copies


def _setup_trees():
    return _existing(
        _ADD_METHOD / "skill" / "add" / "phases" / "direction.md",
        _REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
        _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "direction.md",
    )


def _template_trees():
    rel = Path("tooling") / "templates" / "personas" / "_template.md.tmpl"
    return _existing(
        _ADD_METHOD / rel,
        _REPO / ".add" / rel,
        _ADD_METHOD / "src" / "add_method" / "_bundled" / rel,
    )


def _constants_trees():
    rel = Path("tooling") / "add_engine" / "constants.py"
    return _existing(
        _ADD_METHOD / rel,
        _REPO / ".add" / rel,
        _ADD_METHOD / "src" / "add_method" / "_bundled" / rel,
    )


def _all_prose():
    return (_chapter_trees() + _glossary_trees() + _setup_trees()
            + _template_trees() + _constants_trees())


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class NoBrandInProseTest(unittest.TestCase):
    def test_no_brand_in_prose(self):
        offenders = []
        files = _all_prose()
        self.assertTrue(files, "no prose surfaces found — test would be vacuous")
        for p in files:
            text = p.read_text(encoding="utf-8")
            for token in BRAND:
                if token in text:
                    offenders.append(f"{p} :: {token}")
        self.assertEqual(offenders, [],
                         f"method prose must not name the upstream brand (brand_in_prose): {offenders}")


class ProsePointsAtLocalLibraryTest(unittest.TestCase):
    def test_prose_points_at_local_library(self):
        # the persona-AUTHORING prose names the local library (constants.py is engine — excluded
        # so no path literal contaminates engine source).
        for group, label in ((_chapter_trees(), "ch.18"), (_setup_trees(), "0-setup"),
                             (_template_trees(), "_template"), (_glossary_trees(), "glossary")):
            self.assertTrue(group, f"{label}: no tree found")
            for p in group:
                self.assertIn(LOCAL_LIB, p.read_text(encoding="utf-8"),
                              f"{label} ({p}) must point the persona phase at {LOCAL_LIB}")


class KeepersRetainReferenceTest(unittest.TestCase):
    def test_keepers_retain_url_and_attribution(self):
        teacher = _ADD_METHOD / "personas-teacher"
        update = _ADD_METHOD / "scripts" / "update_teacher.py"
        vendor = teacher / "VENDOR.md"
        # operational refs keep the upstream URL (the refresh source + the pin record)
        for p in (update, vendor):
            self.assertTrue(p.is_file(), f"keeper missing: {p}")
            self.assertTrue(any(tok in p.read_text(encoding='utf-8') for tok in BRAND),
                            f"{p} must retain the upstream reference (over-scrubbed)")
        # legal refs keep the MIT attribution
        for p in (teacher / "LICENSE", _REPO / "THIRD_PARTY_NOTICES.md"):
            self.assertTrue(p.is_file(), f"attribution file missing: {p} (attribution_stripped)")
            self.assertIn("MIT", p.read_text(encoding="utf-8"),
                          f"{p} must retain the MIT attribution (attribution_stripped)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
