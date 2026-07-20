#!/usr/bin/env python3
"""dependency-allowlist enforcement (review finding, pre-2.0.0 tag).

`.add/dependencies.allowlist` claimed "CI rejects anything not listed" while
NOTHING read the file — an honor-system doc wearing a CI badge, under a build
exit gate ("no dependency outside the allow-list") that rested on it. This
suite IS the missing rejection: the corpus runs in CI, so a declared runtime
dependency absent from the allowlist reds the build.

Scope: RUNTIME dependencies of the shipped package (npm `dependencies`,
pyproject `[project] dependencies`) — what a consumer installs. Dev/bench
tooling (pytest, swebench, uv-provisioned extras) never ships and stays out
of scope. The allowlist grammar: one package per line, `#` comments, blanks
ignored.

Run: cd add-method/tooling && python3 -m unittest test_dependency_allowlist -v
"""
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOWLIST = REPO / ".add" / "dependencies.allowlist"


def _allowed() -> set[str]:
    lines = ALLOWLIST.read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")}


class AllowlistEnforcementTest(unittest.TestCase):
    def test_npm_runtime_deps_are_allowlisted(self):
        pkg = json.loads((REPO / "add-method" / "package.json").read_text(encoding="utf-8"))
        deps = set(pkg.get("dependencies") or {})
        self.assertLessEqual(deps, _allowed(),
                             f"npm runtime dep(s) not in .add/dependencies.allowlist: "
                             f"{sorted(deps - _allowed())} — approve there or drop the dep")

    def test_python_runtime_deps_are_allowlisted(self):
        toml = (REPO / "add-method" / "pyproject.toml").read_text(encoding="utf-8")
        m = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)\]", toml)
        self.assertIsNotNone(m, "pyproject [project] dependencies list not found")
        deps = {re.split(r"[<>=~!\[; ]", d.strip().strip("'\""))[0]
                for d in m.group(1).split(",") if d.strip().strip("'\"")}
        self.assertLessEqual(deps, _allowed(),
                             f"python runtime dep(s) not allowlisted: {sorted(deps - _allowed())}")

    def test_allowlist_prose_does_not_overclaim(self):
        # the file must not claim a zero-dep installer while package.json ships one
        text = ALLOWLIST.read_text(encoding="utf-8")
        pkg = json.loads((REPO / "add-method" / "package.json").read_text(encoding="utf-8"))
        if pkg.get("dependencies"):
            self.assertNotIn("built-in modules only", text,
                             "allowlist prose claims a zero-dep Node installer while "
                             "package.json declares runtime dependencies — keep the doc truthful")


if __name__ == "__main__":
    unittest.main(verbosity=2)
