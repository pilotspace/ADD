"""Red/green suite for the pages-deploy task (docs-site milestone).

Pins the FROZEN §3 contract: a GitHub Actions workflow that builds the MkDocs site
`--strict` and deploys it to GitHub Pages, plus homepage/README links to the live
site, with package versions unchanged and book/bundle untouched.

Runs RED until .github/workflows/pages.yml exists and the link edits land.
Stdlib `unittest`; PyYAML parses the workflow (it ships with mkdocs-material).

NB: in YAML 1.1 the bare key `on:` parses as the boolean True — so the workflow's
`on:` block is read as cfg[True]; helpers below normalise that.

Repo root is 4 parents above this file.
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
WF = REPO / ".github" / "workflows" / "pages.yml"
PKG_JSON = REPO / "add-method" / "package.json"
PYPROJECT = REPO / "add-method" / "pyproject.toml"
ROOT_README = REPO / "README.md"
DOCS = REPO / "add-method" / "docs"
BUNDLE_DOCS = REPO / "add-method" / "src" / "add_method" / "_bundled" / "docs"

PAGES_URL = "https://pilotspace.github.io/ADD/"
EXPECTED_VERSION = "1.9.0"


def _load_yaml(path: Path) -> dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _on_block(cfg: dict):
    # `on:` parses to the boolean True key under YAML 1.1
    return cfg.get("on", cfg.get(True))


def _all_steps(job: dict) -> list[dict]:
    return [s for s in (job.get("steps") or []) if isinstance(s, dict)]


def _require_yaml(tc: unittest.TestCase):
    try:
        import yaml  # noqa: F401
    except Exception:
        tc.skipTest("PyYAML not installed — ships with mkdocs-material")


class TestWorkflowTriggers(unittest.TestCase):
    def test_workflow_triggers(self):
        self.assertTrue(WF.is_file(), ".github/workflows/pages.yml must exist")
        _require_yaml(self)
        on = _on_block(_load_yaml(WF))
        self.assertIsInstance(on, dict, "the workflow must have an `on:` block")
        push = on.get("push") or {}
        branches = push.get("branches") or []
        self.assertIn("main", branches, "must trigger on push to main")
        self.assertIn("workflow_dispatch", on, "must allow manual workflow_dispatch")


class TestBuildJob(unittest.TestCase):
    def test_build_job_strict_with_deps(self):
        self.assertTrue(WF.is_file())
        _require_yaml(self)
        jobs = _load_yaml(WF).get("jobs") or {}
        build = jobs.get("build") or {}
        steps = _all_steps(build)
        runs = [str(s.get("run", "")) for s in steps]
        uses = [str(s.get("uses", "")) for s in steps]
        # deps installed BEFORE mkdocs build (missing_build_dep guard)
        install_idx = next((i for i, r in enumerate(runs) if "requirements-docs.txt" in r), -1)
        build_idx = next((i for i, r in enumerate(runs) if "mkdocs build" in r and "--strict" in r), -1)
        self.assertGreaterEqual(install_idx, 0, "build must `pip install -r requirements-docs.txt`")
        self.assertGreaterEqual(build_idx, 0, "build must run `mkdocs build --strict`")
        self.assertLess(install_idx, build_idx, "deps must be installed before the strict build")
        self.assertTrue(any("upload-pages-artifact" in u for u in uses),
                        "build must upload the site via actions/upload-pages-artifact")


class TestDeployJob(unittest.TestCase):
    def test_deploy_job_permissions(self):
        self.assertTrue(WF.is_file())
        _require_yaml(self)
        cfg = _load_yaml(WF)
        perms = cfg.get("permissions") or {}
        self.assertEqual(perms.get("pages"), "write", "permissions.pages must be write")
        self.assertEqual(perms.get("id-token"), "write", "permissions.id-token must be write")
        jobs = cfg.get("jobs") or {}
        deploy = jobs.get("deploy") or {}
        uses = [str(s.get("uses", "")) for s in _all_steps(deploy)]
        self.assertTrue(any("deploy-pages" in u for u in uses),
                        "deploy must use actions/deploy-pages")
        env = deploy.get("environment")
        env_name = env if isinstance(env, str) else (env or {}).get("name")
        self.assertEqual(env_name, "github-pages", "deploy environment must be github-pages")
        conc = cfg.get("concurrency")
        grp = conc if isinstance(conc, str) else (conc or {}).get("group")
        self.assertEqual(grp, "pages", "a concurrency group `pages` must be set")


class TestLinksAndVersions(unittest.TestCase):
    def test_links_point_at_pages(self):
        pkg = json.loads(PKG_JSON.read_text(encoding="utf-8"))
        self.assertEqual(pkg.get("homepage"), PAGES_URL, "package.json homepage must be the Pages URL")
        pyproject = PYPROJECT.read_text(encoding="utf-8")
        self.assertRegex(pyproject, r"(?mi)^\s*Documentation\s*=\s*\"" + re.escape(PAGES_URL) + r"\"",
                         "pyproject [project.urls] must have a Documentation = Pages URL")
        self.assertIn(PAGES_URL, ROOT_README.read_text(encoding="utf-8"),
                      "repo-root README must link the Pages URL")

    def test_versions_unchanged(self):
        pkg = json.loads(PKG_JSON.read_text(encoding="utf-8"))
        self.assertEqual(pkg.get("version"), EXPECTED_VERSION, "package.json version must be unchanged")
        pyproject = PYPROJECT.read_text(encoding="utf-8")
        m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject)
        self.assertIsNotNone(m, "pyproject must declare a version")
        self.assertEqual(m.group(1), EXPECTED_VERSION, "pyproject version must be unchanged")


class TestBookUnchanged(unittest.TestCase):
    def test_book_and_bundle_unchanged(self):
        if shutil.which("git") is None:
            self.skipTest("git unavailable")
        out = subprocess.run(
            ["git", "status", "--porcelain", "--",
             "add-method/docs", "add-method/src/add_method/_bundled"],
            cwd=str(REPO), capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(out, "", f"book/bundle must be byte-unchanged, got:\n{out}")


class TestLocalStrictBuild(unittest.TestCase):
    def test_local_strict_build_ok(self):
        try:
            import mkdocs  # noqa: F401
        except Exception:
            if shutil.which("mkdocs") is None:
                self.skipTest("mkdocs not installed — strict build is the workflow's job (CI)")
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(Path(td) / "s")],
                cwd=str(REPO), capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0,
                             f"the workflow's `mkdocs build --strict` must pass locally:\n{proc.stderr}")


if __name__ == "__main__":
    unittest.main()
