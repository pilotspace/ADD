"""Red/green suite for the site-scaffold task (docs-site milestone).

Pins the FROZEN §3 contract: a MkDocs-Material site over the canonical book in
`add-method/docs/`, with README.md as the home, deps build-time only, and `site/`
ignored. Runs RED until mkdocs.yml / requirements-docs.txt / .gitignore exist.

Stdlib `unittest` (the project's test framework; CI runs `unittest discover`).
PyYAML is used to parse mkdocs.yml — it ships transitively with mkdocs-material,
so it is present wherever the site can be built; tests skip cleanly if absent.

Repo root is 4 parents above this file:
  tests/ -> site-scaffold/ -> tasks/ -> .add/ -> <repo root>
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DOCS = REPO / "add-method" / "docs"
MKDOCS = REPO / "mkdocs.yml"
REQS = REPO / "requirements-docs.txt"
GITIGNORE = REPO / ".gitignore"

CHAPTERS = [
    "00-introduction.md", "01-principles.md", "02-the-flow.md",
    "03-step-1-specify.md", "04-step-2-scenarios.md", "05-step-3-contract.md",
    "06-step-4-tests.md", "07-step-5-build.md", "08-step-6-verify.md",
    "09-the-loop.md", "10-setup-and-stages.md", "11-governance.md",
    "12-roles.md", "13-adoption.md", "14-foundation.md",
    "15-foundations-and-lineage.md", "16-releasing.md",
]
APPENDICES = [
    "appendix-a-templates.md", "appendix-b-prompts.md", "appendix-c-glossary.md",
    "appendix-d-worked-example.md", "appendix-e-checklists.md",
    "appendix-f-requirements-matrix.md", "appendix-g-references.md",
]
PNGS = [
    "add-competencies.png", "add-flow.png",
    "add-foundation.png", "add-hierarchy.png",
]
# the full book .md set that must stay byte-stable (README + chapters + appendices)
BOOK_MD = ["README.md", *CHAPTERS, *APPENDICES]


def _load_mkdocs() -> dict:
    """Parse mkdocs.yml tolerantly — ignore any `!!python/...`/`!` custom tags so a
    Material config with emoji/icon tags still loads under SafeLoader."""
    import yaml

    class _Tolerant(yaml.SafeLoader):
        pass

    _Tolerant.add_multi_constructor("tag:yaml.org,2002:python/", lambda *_: None)
    _Tolerant.add_multi_constructor("!", lambda *_: None)
    return yaml.load(MKDOCS.read_text(encoding="utf-8"), Loader=_Tolerant)


def _nav_files(nav) -> list[str]:
    """Flatten nav (list of {label: target} / nested) to the ordered target paths."""
    out: list[str] = []

    def walk(node):
        if isinstance(node, str):
            out.append(node)
        elif isinstance(node, list):
            for it in node:
                walk(it)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    walk(nav)
    return out


def _require_yaml(tc: unittest.TestCase):
    try:
        import yaml  # noqa: F401
    except Exception:
        tc.skipTest("PyYAML not installed — ships with mkdocs-material; asserted where the site builds")


class TestMkdocsConfig(unittest.TestCase):
    def test_mkdocs_config_keys(self):
        self.assertTrue(MKDOCS.is_file(), "mkdocs.yml must exist at repo root")
        _require_yaml(self)
        cfg = _load_mkdocs()
        self.assertTrue(cfg.get("site_name"), "site_name must be set")
        self.assertEqual(cfg.get("docs_dir"), "add-method/docs")
        self.assertEqual((cfg.get("theme") or {}).get("name"), "material")

    def test_search_and_palette_present(self):
        self.assertTrue(MKDOCS.is_file(), "mkdocs.yml must exist")
        _require_yaml(self)
        cfg = _load_mkdocs()
        plugins = cfg.get("plugins") or []
        names = [p if isinstance(p, str) else next(iter(p)) for p in plugins]
        self.assertIn("search", names, "search plugin must be enabled")
        palette = (cfg.get("theme") or {}).get("palette")
        self.assertIsInstance(palette, list)
        self.assertGreaterEqual(len(palette), 2, "palette must define >=2 schemes (dark/light)")
        schemes = {(p or {}).get("scheme") for p in palette}
        self.assertTrue({"default", "slate"} <= schemes,
                        "palette must include default (light) and slate (dark)")


class TestNavAndHome(unittest.TestCase):
    def test_nav_is_full_book_in_order(self):
        self.assertTrue(MKDOCS.is_file(), "mkdocs.yml must exist")
        _require_yaml(self)
        files = _nav_files(_load_mkdocs().get("nav"))
        self.assertEqual(files, ["README.md", *CHAPTERS, *APPENDICES],
                         "nav must be Home(README.md) then 00..16 then appendices A..G, in order")
        for f in files:
            self.assertTrue((DOCS / f).is_file(),
                            f"nav target {f} must exist in docs_dir (no nav_target_missing)")

    def test_readme_is_home_book_unchanged(self):
        self.assertTrue(MKDOCS.is_file(), "mkdocs.yml must exist")
        _require_yaml(self)
        files = _nav_files(_load_mkdocs().get("nav"))
        self.assertTrue(files and files[0] == "README.md",
                        "the home (first nav entry) must be README.md")
        self.assertFalse((DOCS / "index.md").exists(),
                         "no index.md may be added to the book (keep the home out of the book)")
        on_disk = sorted(p.name for p in DOCS.glob("*.md"))
        self.assertEqual(on_disk, sorted(BOOK_MD),
                         "book .md set must be exactly README + 17 chapters + 7 appendices (byte-unchanged)")


class TestDepsAndIgnore(unittest.TestCase):
    def test_docs_dep_build_time_only(self):
        self.assertTrue(REQS.is_file(), "requirements-docs.txt must exist")
        self.assertRegex(REQS.read_text(encoding="utf-8"), r"(?m)^\s*mkdocs-material\b",
                         "requirements-docs.txt must pin mkdocs-material")
        pyproject = (REPO / "add-method" / "pyproject.toml").read_text(encoding="utf-8")
        m = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)\]", pyproject)
        self.assertIsNotNone(m, "pyproject [project].dependencies must be present")
        self.assertNotIn("mkdocs", m.group(1).lower(),
                         "mkdocs must not be a published pyproject dependency (runtime_dep_leak)")
        pkg = json.loads((REPO / "add-method" / "package.json").read_text(encoding="utf-8"))
        deps = " ".join((pkg.get("dependencies") or {}).keys()).lower()
        self.assertNotIn("mkdocs", deps, "mkdocs must not be a package.json dependency")

    def test_site_gitignored(self):
        self.assertTrue(GITIGNORE.is_file())
        lines = [ln.strip() for ln in GITIGNORE.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(ln in ("site/", "/site/", "site") for ln in lines),
                        ".gitignore must ignore the MkDocs build output site/")


class TestStrictBuild(unittest.TestCase):
    def test_strict_build_produces_site(self):
        if not MKDOCS.is_file():
            self.fail("mkdocs.yml must exist before a strict build")
        try:
            import mkdocs  # noqa: F401
        except Exception:
            if shutil.which("mkdocs") is None:
                self.skipTest("mkdocs not installed — strict build asserted in CI (pages-deploy)")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "site"
            proc = subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(out)],
                cwd=str(REPO), capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0,
                             f"`mkdocs build --strict` must exit 0:\n{proc.stderr}")
            self.assertTrue((out / "index.html").is_file(),
                            "site/index.html (from README) must be produced")
            for f in [*CHAPTERS, *APPENDICES]:
                stem = f[:-3]
                self.assertTrue((out / stem / "index.html").is_file() or (out / f"{stem}.html").is_file(),
                                f"a page for {f} must be in the built site")
            for png in PNGS:
                self.assertTrue((out / png).is_file(), f"diagram {png} must be copied into the site")
            self.assertTrue((out / "search" / "search_index.json").is_file(),
                            "search index must be built")


if __name__ == "__main__":
    unittest.main()
