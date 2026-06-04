#!/usr/bin/env python3
"""Guard: the npm and PyPI packages ship the SAME version.

The release is one tag → two registries (@pilotspace/add on npm, pilotspace-add on
PyPI). The publish workflow refuses to ship if the git tag disagrees with either
manifest — but that check only runs in CI, at tag time. This test brings the same
invariant local and into the suite: package.json `version` MUST equal pyproject.toml
`[project].version`. Drift caught here never reaches a tag.

Run: python3 -m unittest test_version_sync -v
"""
import json
import re
import unittest
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent      # add-method/
_PACKAGE_JSON = _PKG_ROOT / "package.json"
_PYPROJECT = _PKG_ROOT / "pyproject.toml"
_INIT = _PKG_ROOT / "src" / "add_method" / "__init__.py"  # runtime __version__

_SEMVER = re.compile(r"^\d+\.\d+\.\d+([.-].+)?$")


def _npm_version() -> str:
    return json.loads(_PACKAGE_JSON.read_text(encoding="utf-8"))["version"]


def _pypi_version() -> str:
    # stdlib-only on purpose: tomllib is 3.11+, but the floor is 3.10, so we parse
    # the single `version = "..."` line under [project] with a regex instead.
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', _PYPROJECT.read_text(encoding="utf-8"))
    assert m, "pyproject.toml has no `version = \"...\"` line"
    return m.group(1)


def _init_version() -> str:
    # the runtime version the PyPI package reports (add_method.__version__). It is a
    # THIRD source that can drift independently of pyproject's build version, so the
    # guard must include it — not just the two manifests.
    m = re.search(r'(?m)^__version__\s*=\s*"([^"]+)"', _INIT.read_text(encoding="utf-8"))
    assert m, "src/add_method/__init__.py has no `__version__ = \"...\"` line"
    return m.group(1)


class VersionSyncTest(unittest.TestCase):
    def test_both_manifests_exist(self):
        self.assertTrue(_PACKAGE_JSON.is_file(), "package.json missing")
        self.assertTrue(_PYPROJECT.is_file(), "pyproject.toml missing")
        self.assertTrue(_INIT.is_file(), "src/add_method/__init__.py missing")

    def test_versions_are_identical(self):
        npm, pypi, runtime = _npm_version(), _pypi_version(), _init_version()
        self.assertEqual(
            npm, pypi,
            f"version drift: package.json={npm!r} but pyproject.toml={pypi!r}. "
            f"One tag publishes both registries — they must agree.",
        )
        self.assertEqual(
            pypi, runtime,
            f"version drift: pyproject.toml={pypi!r} but add_method.__version__={runtime!r}. "
            f"The runtime version the package reports must match what it was built as.",
        )

    def test_version_is_semver(self):
        self.assertRegex(_npm_version(), _SEMVER, "package.json version is not semver")


if __name__ == "__main__":
    unittest.main()
