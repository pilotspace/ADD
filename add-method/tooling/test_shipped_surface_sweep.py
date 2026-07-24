#!/usr/bin/env python3
"""shipped-surface-sweep: nothing that SHIPS may reference a book chapter that doesn't.

The scenarios-into-tests fold deleted `04-step-2-scenarios` from the book. Its sweep
covered add-method/docs/ and mkdocs.yml, so a link in GETTING-STARTED.md survived and
rode into the published v2.3.0 npm and PyPI tarballs as a live 404 — through a
milestone close and a release cut, with nothing objecting.

The fix for the CLASS is this sweep. Its surface set is DERIVED from the packaging
manifests (package.json `files`, MANIFEST.in) rather than hand-written here, because a
hand-written list is one more thing that drifts — the exact failure being guarded. Add
a path to either manifest and it comes under the sweep automatically.
"""

import json
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG = TOOLING.parent                      # add-method/
DOCS = PKG / "docs"
PACKAGE_JSON = PKG / "package.json"
MANIFEST_IN = PKG / "MANIFEST.in"

# Text that can hold a link. Binaries and lockfiles are skipped, not "shipped prose".
PROSE_SUFFIXES = {".md", ".tmpl", ".txt", ".json", ".js", ".py", ".yml", ".yaml", ".css", ".html"}
SKIP_NAMES = {"package-lock.json", "uv.lock"}

# A guard that silently sweeps almost nothing would pass forever. 693 files resolved
# when this was written (npm 'files' + MANIFEST.in + the docs site); the floor catches
# a derivation that quietly collapses, with headroom for normal churn.
MIN_SWEPT_FILES = 600

CHAPTER_REF = re.compile(r"(?:docs/|ADD/)(\d{2}-[a-z0-9-]+?)(?:\.md|/)")


def _npm_paths():
    """Entries from package.json `files`, minus negations (`!…`)."""
    files = json.loads(PACKAGE_JSON.read_text(encoding="utf-8")).get("files", [])
    return [e for e in files if not e.startswith("!")]


def _sdist_paths():
    """`include X` / `graft DIR` from MANIFEST.in; global-exclude is not a path."""
    out = []
    for raw in MANIFEST_IN.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        head, _, rest = line.partition(" ")
        if head in ("include", "graft") and rest.strip():
            out.append(rest.strip())
    return out


def _site_paths():
    """The book ships too — via GitHub Pages (.github/workflows/pages.yml), not the
    tarballs. A dead cross-reference BETWEEN chapters is a 404 on the published site,
    so docs/ is a shipped surface on its own channel."""
    return ["docs"] if (PKG.parent / "mkdocs.yml").is_file() else []


def shipped_surfaces():
    """Every shipped file that could hold a chapter reference — derived, not declared."""
    seen, out = set(), []
    for entry in _npm_paths() + _sdist_paths() + _site_paths():
        target = PKG / entry
        if target.is_file():
            candidates = [target]
        elif target.is_dir():
            candidates = [p for p in target.rglob("*") if p.is_file()]
        else:
            continue                       # a manifest entry with nothing on disk
        for p in candidates:
            if p.suffix.lower() not in PROSE_SUFFIXES or p.name in SKIP_NAMES:
                continue
            if "__pycache__" in p.parts:
                continue
            rp = p.resolve()
            if rp not in seen:
                seen.add(rp)
                out.append(p)
    return out


def _chapters():
    return {p.stem for p in DOCS.glob("*.md")}


def dead_refs_in(text, chapters):
    return sorted({s for s in CHAPTER_REF.findall(text) if s not in chapters})


class ShippedSurfaceSet(unittest.TestCase):
    def test_surface_set_derives_from_packaging(self):                  # M2
        self.assertTrue(PACKAGE_JSON.is_file(), "package.json defines the npm surface")
        self.assertTrue(MANIFEST_IN.is_file(), "MANIFEST.in defines the sdist surface")

        surfaces = shipped_surfaces()
        self.assertGreaterEqual(
            len(surfaces), MIN_SWEPT_FILES,
            f"only {len(surfaces)} shipped files resolved (floor {MIN_SWEPT_FILES}) — the "
            "derivation collapsed; a sweep that covers nothing passes for the wrong reason")

    def test_known_shipped_files_are_covered(self):                     # M2
        swept = {p.resolve() for p in shipped_surfaces()}
        # The surface that actually shipped the v2.3.0 404, plus the trees the fold touched.
        for rel in ("GETTING-STARTED.md", "README.md",
                    "skill/add/SKILL.md", "tooling/templates/PLAN.md.tmpl"):
            f = (PKG / rel).resolve()
            if f.is_file():
                self.assertIn(f, swept, f"{rel} ships but is not swept")


class ShippedChapterRefs(unittest.TestCase):
    def test_every_shipped_chapter_ref_resolves(self):                  # M1
        chapters = _chapters()
        self.assertGreater(len(chapters), 10, "sanity: the book should have chapters")

        dead = []
        for f in shipped_surfaces():
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for slug in dead_refs_in(text, chapters):
                dead.append(f"{f.relative_to(PKG)} -> {slug}")
        self.assertEqual(dead, [], "shipped files reference missing chapters: " + "; ".join(dead))


class GuardFailsLoudly(unittest.TestCase):
    def test_failure_message_names_file_and_ref(self):                  # M4
        """The guard's own failure path, exercised permanently rather than once by hand."""
        chapters = _chapters()
        self.assertNotIn("04-step-2-scenarios", chapters,
                         "sanity: the retired chapter really is gone")

        text = "see https://pilotspace.github.io/ADD/04-step-2-scenarios/ for scenarios"
        self.assertEqual(dead_refs_in(text, chapters), ["04-step-2-scenarios"],
                         "the detector must name the dead slug it found")

        # And a live chapter must NOT be reported — otherwise the guard cries wolf.
        live = sorted(chapters)[0]
        self.assertEqual(dead_refs_in(f"see docs/{live}.md", chapters), [])


if __name__ == "__main__":
    unittest.main()
