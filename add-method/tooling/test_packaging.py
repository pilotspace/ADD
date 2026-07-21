#!/usr/bin/env python3
"""Red/green guard for the published @pilotspace/add tarball — no dev junk ships.

`npm pack --dry-run --json` is the ground truth for what publish would include. We
parse files[].path and assert the runtime surface is present and that no compiled
bytecode (__pycache__/*.pyc), no .DS_Store, and no test_*.py source leaks in. The
npm-coupled checks SKIP cleanly when npm is absent (honest, never a false green);
the engines floor reads package.json directly so it always runs.

The PyPI side has the same risk and its own ground truth: build the wheel with the
real setuptools backend and read its namelist. _bundled/ ships only because
MANIFEST.in + [tool.setuptools.package-data] agree — a single drift and the wheel
installs but `pilotspace-add init` finds no skill/tooling to copy. PyWheelTest
catches that the same way NpmTarballTest catches an npm leak. Skips honestly when
setuptools is absent.

Run: python3 -m unittest test_packaging -v
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent      # add-method/ (holds package.json)
_PACK_TIMEOUT = 120                                    # design-for-failure: never hang the suite

_JUNK = re.compile(r"(__pycache__|\.py[co]$|(^|/)\.DS_Store$)")
_TEST_SRC = re.compile(r"(^|/)test_.*\.py$")
_RUNTIME_MUST = (
    "bin/cli.js", "tooling/add.py", "README.md", "GETTING-STARTED.md",
)


def _npm_on_path() -> bool:
    return shutil.which("npm") is not None


def _paths_from_pack_json(data) -> list[str]:
    """Normalize `npm pack --json`'s output shape to a flat files[].path list.

    npm has shipped this payload in three shapes across versions/environments, and the
    publish job's `npm@latest` inside the `prepublishOnly` hook emits a different one than
    Node 20's bundled npm in the guard job — a hard-coded `data[0]["files"]` raised
    `KeyError: 0` in CI (npm >= 11 handed back a dict, not a list), splitting a release.
    Handle every shape by keying on where the `files` array actually lives:

      1. list of pack-results        -> [ { ..., "files": [...] } ]        (npm 10, npm 11.12 local)
      2. a single pack-result dict   -> { ..., "files": [...] }
      3. a dict of pack-results      -> { "<tarball>": { ..., "files": [...] }, ... }
    """
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = [data] if "files" in data else list(data.values())
    else:
        raise RuntimeError(f"unexpected `npm pack --json` payload type: {type(data).__name__}")
    paths: list[str] = []
    for entry in entries:
        for f in entry.get("files", []):
            paths.append(f["path"])
    return paths


def _pack_paths() -> list[str]:
    """Return files[].path from `npm pack --dry-run --json`, run from the package root."""
    proc = subprocess.run(
        ["npm", "pack", "--dry-run", "--json"],
        cwd=PKG_ROOT, capture_output=True, text=True, timeout=_PACK_TIMEOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"`npm pack --dry-run` failed ({proc.returncode}):\n{proc.stderr}")
    return _paths_from_pack_json(json.loads(proc.stdout))


class PackJsonShapeTest(unittest.TestCase):
    """`npm pack --json` shape drift must never split a release again (npm>=11 KeyError:0).

    No npm needed — these feed `_paths_from_pack_json` the raw shapes directly, so they run
    everywhere (including the guard job on Node 20, catching the shape the npm job hits)."""
    _FILES = [{"path": "bin/cli.js", "size": 1, "mode": 420},
              {"path": "tooling/add.py", "size": 2, "mode": 420}]
    _EXPECTED = ["bin/cli.js", "tooling/add.py"]

    def test_list_of_results_shape(self):   # npm 10 / npm 11.12 local
        self.assertEqual(_paths_from_pack_json([{"name": "x", "files": self._FILES}]),
                         self._EXPECTED)

    def test_single_dict_result_shape(self):
        self.assertEqual(_paths_from_pack_json({"name": "x", "files": self._FILES}),
                         self._EXPECTED)

    def test_dict_of_results_shape(self):   # the CI npm>=11 shape that raised KeyError: 0
        self.assertEqual(_paths_from_pack_json({"pilotspace-add-2.0.0.tgz":
                                                {"name": "x", "files": self._FILES}}),
                         self._EXPECTED)

    def test_unexpected_scalar_raises(self):
        with self.assertRaises(RuntimeError):
            _paths_from_pack_json(42)


@unittest.skipUnless(_npm_on_path(), "npm not on PATH — tarball checks skipped (honest skip)")
class NpmTarballTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = _pack_paths()

    def test_no_bytecode_or_os_junk_ships(self):
        junk = [p for p in self.paths if _JUNK.search(p)]
        self.assertEqual(junk, [], f"compiled/OS junk must not ship: {junk}")

    def test_no_test_sources_ship(self):
        tests = [p for p in self.paths if _TEST_SRC.search(p)]
        self.assertEqual(tests, [], f"dev test sources must not ship: {tests}")

    def test_runtime_surface_ships(self):
        missing = [p for p in _RUNTIME_MUST if p not in self.paths]
        self.assertEqual(missing, [], f"runtime files must ship: {missing}")
        # the directory surfaces (templates/skill) must each contribute ≥1 file
        for prefix in ("tooling/templates/", "skill/"):
            self.assertTrue(any(p.startswith(prefix) for p in self.paths),
                            f"no file under {prefix} shipped")
        self.assertFalse(any(p.startswith("docs/") for p in self.paths),
                         "book-stops-shipping (2.0 M6b): the npm tarball must not ship docs/")

    def test_agent_roster_ships(self):
        """roster-install-drift: a missing agents/ here is the SAME files-allowlist trap
        test_teacher_corpus_and_notices_ship guards for personas-teacher/ — the dir silently
        drops from the tarball and every consumer project's guideline block cites a roster
        that can never resolve (the apple-container transcript finding)."""
        self.assertTrue(any(p.startswith("agents/") for p in self.paths),
                        "no file under agents/ shipped (roster_absent_from_npm)")
        self.assertIn("agents/add-worker.md", self.paths,
                      "the add-worker agent must ship in the npm tarball (roster_absent_from_npm)")
        self.assertIn("agents/add-advisor.md", self.paths,
                      "the add-advisor agent must ship in the npm tarball (roster_absent_from_npm)")

    def test_teacher_corpus_and_notices_ship(self):
        """The vendored teacher snapshot + its MIT attribution must ride in the tarball
        (bundle-teacher). A missing personas-teacher/ here is the 1.11.0 files-allowlist
        trap: the dir silently drops and a fresh install finds no teacher to materialize."""
        self.assertTrue(any(p.startswith("personas-teacher/") for p in self.paths),
                        "no file under personas-teacher/ shipped (teacher_absent_from_npm)")
        self.assertIn("personas-teacher/LICENSE", self.paths,
                      "the vendored MIT LICENSE must ship with the teacher (attribution_missing)")
        self.assertIn("THIRD_PARTY_NOTICES.md", self.paths,
                      "THIRD_PARTY_NOTICES.md must ship in the npm tarball (attribution_missing)")

    def test_add_engine_package_ships(self):
        """add.py imports `from add_engine.<module> import …` at load — the whole
        package MUST ship in the tarball or `bin/cli.js init` materializes an add.py
        that crashes with ModuleNotFoundError on the first `add.py status`. Pin every
        canonical module so a future split/rename can't silently drop one again."""
        shipped = {p.split("tooling/add_engine/", 1)[1]
                   for p in self.paths if "tooling/add_engine/" in p and p.endswith(".py")}
        canonical = {f.name for f in (PKG_ROOT / "tooling" / "add_engine").glob("*.py")}
        self.assertTrue(canonical, "no add_engine/*.py found on disk — test is vacuous")
        missing = sorted(canonical - shipped)
        self.assertEqual(missing, [],
                         f"the add_engine package must ship whole — missing: {missing}")


class PackageConfigTest(unittest.TestCase):
    """No npm needed — reads package.json directly."""

    def test_node_floor_is_18(self):
        pkg = json.loads((PKG_ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg.get("engines", {}).get("node"), ">=18",
                         "cli.js uses fs.cpSync (Node 16.7+); 16 is EOL — floor must be >=18")


def _setuptools_backend():
    """Return setuptools.build_meta (the PEP 517 backend) or None if unavailable.

    We drive the backend in-process rather than shelling to `python -m build`: build
    is an optional dep, but setuptools is always present in a build/test env, so this
    runs the SAME backend a real `pip install` from sdist/source would, without the
    extra dependency or a subprocess to time out."""
    if importlib.util.find_spec("setuptools") is None:
        return None
    from setuptools import build_meta
    return build_meta


_BUNDLE_PREFIXES = (
    "add_method/_bundled/skill/add/",
    "add_method/_bundled/agents/",
    "add_method/_bundled/tooling/",
    "add_method/_bundled/personas-teacher/",
)
_PKG_MODULES = (
    "add_method/__init__.py", "add_method/_cli.py", "add_method/_installer.py",
)
# the wheel members carry no "test_" prefix segment and no compiled/OS junk
_WHEEL_TEST_SRC = re.compile(r"(^|/)test_.*\.py$")


@unittest.skipUnless(_setuptools_backend() is not None,
                     "setuptools not importable — wheel build check skipped (honest skip)")
class PyWheelTest(unittest.TestCase):
    """Build the real wheel and assert _bundled/ ships intact — the PyPI analog of
    NpmTarballTest. Builds from a COPY of the sources so the repo tree stays clean
    (setuptools writes build/ + *.egg-info into the build root)."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.mkdtemp(prefix="add-pywheel-")
        srcroot = Path(cls._tmp) / "srcroot"
        outdir = Path(cls._tmp) / "out"
        srcroot.mkdir()
        outdir.mkdir()
        # minimal faithful source set for a wheel build (README/LICENSE are referenced
        # by pyproject; GETTING-STARTED silences a MANIFEST warning but isn't in the wheel)
        for fname in ("pyproject.toml", "README.md", "LICENSE", "MANIFEST.in",
                      "GETTING-STARTED.md"):
            src = PKG_ROOT / fname
            if src.exists():
                shutil.copy2(src, srcroot / fname)
        shutil.copytree(PKG_ROOT / "src", srcroot / "src")
        # strip any pre-existing build residue from the copy so it cannot mask a gap
        for junk in srcroot.glob("src/*.egg-info"):
            shutil.rmtree(junk, ignore_errors=True)
        for cache in srcroot.glob("src/**/__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)

        backend = _setuptools_backend()
        prev = os.getcwd()
        os.chdir(srcroot)
        try:
            sink = io.StringIO()
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                wheel_name = backend.build_wheel(str(outdir))
        finally:
            os.chdir(prev)
        cls.names = zipfile.ZipFile(outdir / wheel_name).namelist()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmp, ignore_errors=True)

    def test_bundled_data_ships(self):
        for prefix in _BUNDLE_PREFIXES:
            self.assertTrue(
                any(n.startswith(prefix) for n in self.names),
                f"the wheel ships NO file under {prefix} — _bundled is broken; "
                f"`pilotspace-add init` would find nothing to install",
            )
        self.assertTrue(any(n.endswith("_bundled/tooling/add.py") for n in self.names),
                        "the wheel must ship the add.py scaffolder")
        self.assertTrue(any(n.endswith("_bundled/THIRD_PARTY_NOTICES.md") for n in self.names),
                        "the wheel must ship THIRD_PARTY_NOTICES.md (attribution_missing)")

    def test_package_modules_ship(self):
        missing = [m for m in _PKG_MODULES if m not in self.names]
        self.assertEqual(missing, [], f"the importable package surface must ship: {missing}")

    def test_no_test_sources_or_junk(self):
        leaks = [n for n in self.names
                 if _WHEEL_TEST_SRC.search(n) or _JUNK.search(n)]
        self.assertEqual(leaks, [], f"no dev test source or compiled/OS junk may ship: {leaks}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
