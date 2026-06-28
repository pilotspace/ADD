#!/usr/bin/env python3
"""Red/green tests for the components reader/validator + check-time schema lint
(task components-validator, milestone component-polish).

`add.py components` reads .add/components.toml, prints the parsed registry, and
validates it — the existing RED integrity findings then the NEW schema-lint WARNs
(component_unknown_key · component_type_mismatch · component_unknown_table). It
exits 1 IFF a RED integrity finding exists; exit 0 when clean, WARN-only, or
opted-out (no components.toml). The SAME schema-lint WARNs surface at `add.py
check` as never-red warnings (measure-not-block) — caught early without failing
the build or breaking older-engine/newer-file forward-compat.

Contract FROZEN @ v1: typos are WARN, never a RED check-fail. The lint is
PURE · DEGRADE-SAFE · NO-EXEC (never runs `verify`).

Run: cd add-method/tooling && python3 -m unittest test_components_validator -v
"""
import contextlib
import io
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

try:
    import tomllib  # the component pillar requires tomllib (stdlib, Python 3.11+)
    _HAS_TOMLLIB = True
except ModuleNotFoundError:
    _HAS_TOMLLIB = False


def setUpModule():
    # Python < 3.11 has no tomllib, so components.toml cannot be parsed and the pillar is
    # unavailable. The feature's behavior can only be exercised where it exists; 3.12+ runs all.
    if not _HAS_TOMLLIB:
        raise unittest.SkipTest("component pillar requires tomllib (Python 3.11+)")


# ── a well-formed multi-component registry (the print-valid fixture) ──────────────────
_VALID = (
    '[component.gateway]\n'
    'root = "apps/gateway"\n'
    'verify = "pytest -q"\n'
    'green_bar = "tests + pyright"\n'
    'language = "python"\n'
    '[component.web]\n'
    'root = "apps/web"\n'
    'green_bar = "vitest"\n'
    '[contract.orders]\n'
    'producer = "gateway"\n'
    'consumers = ["web"]\n'
    '[federation.shared]\n'
    'source = "../producer/.add/contracts/shared.json"\n'
    'pin = "v1"\n'
)


class _Board(unittest.TestCase):
    """A real init-ed project (so find_root + state + check work), with
    components.toml written per test. cwd is the tmp project root, which lives
    under the OS tmp dir — outside this repo — so find_root never escapes upward
    to the repo's own .add/."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-cv-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self.addp = self.tmp / ".add"

    def tearDown(self):
        os.chdir(self._cwd)

    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _toml(self, body: str):
        (self.addp / "components.toml").write_text(body, encoding="utf-8")
        for name in ("gateway", "web", "api"):          # give roots something on disk
            (self.tmp / "apps" / name).mkdir(parents=True, exist_ok=True)

    def _run(self, argv):
        """Run a command; return (combined stdout+stderr, exit_code). exit_code 0
        when no SystemExit is raised (a clean exit)."""
        out, errb = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errb):
                add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + errb.getvalue(), code


# ── unit: the new lint helper _component_schema_findings(root) ────────────────────────
class SchemaFindings(_Board):
    def _findings(self):
        return add._component_schema_findings(self.addp)

    def test_clean_registry_has_no_schema_findings(self):
        self._toml(_VALID)
        self.assertEqual(self._findings(), [])

    def test_absent_registry_is_empty(self):
        # opt-in: no components.toml -> [] (byte-identical opt-out)
        self.assertEqual(self._findings(), [])

    def test_malformed_toml_is_empty(self):
        # the malformed-ness is _component_findings' RED job; the schema-lint cannot
        # parse it, so it stays silent (no double-report, never raises).
        self._toml('[component.gateway\nroot = "apps/gateway"\n')   # missing closing ]
        self.assertEqual(self._findings(), [])

    def test_unknown_key_flagged(self):
        self._toml('[component.web]\nroot = "apps/web"\ngreen-bar = "vitest"\n')  # hyphen typo
        codes = [c for c, _ in self._findings()]
        self.assertIn("component_unknown_key", codes)
        # the detail names the offending key + entry
        detail = next(d for c, d in self._findings() if c == "component_unknown_key")
        self.assertIn("green-bar", detail)
        self.assertIn("web", detail)

    def test_unknown_key_on_contract_and_federation(self):
        self._toml('[component.gateway]\nroot = "apps/gateway"\n'
                   '[contract.orders]\nproducer = "gateway"\nconsumer = "web"\n'   # singular typo
                   '[federation.shared]\nsource = "../x"\nprovenance = "y"\n')      # unknown key
        codes = [c for c, _ in self._findings()]
        self.assertEqual(codes.count("component_unknown_key"), 2)

    def test_type_mismatch_flagged(self):
        self._toml('[component.gateway]\nroot = "apps/gateway"\n'
                   '[contract.orders]\nproducer = "gateway"\nconsumers = "web"\n')  # str, not list
        found = [(c, d) for c, d in self._findings()]
        self.assertTrue(any(c == "component_type_mismatch" and "consumers" in d for c, d in found),
                        f"expected a consumers type-mismatch, got {found}")

    def test_type_mismatch_on_optional_component_keys(self):
        self._toml('[component.gateway]\nroot = "apps/gateway"\nverify = 7\n')   # int, not str
        self.assertTrue(any(c == "component_type_mismatch" and "verify" in d
                            for c, d in self._findings()))

    def test_root_not_double_reported(self):
        # a missing/non-str root is already RED `components_malformed`; the schema-lint
        # must NOT also emit a type_mismatch for root (no double-report).
        self._toml('[component.api]\nroot = 5\n')
        self.assertFalse(any(c == "component_type_mismatch" and "root" in d
                             for c, d in self._findings()))

    def test_unknown_table_flagged(self):
        self._toml('[componnt.api]\nroot = "apps/api"\n')   # typo of [component.*]
        found = [(c, d) for c, d in self._findings()]
        self.assertTrue(any(c == "component_unknown_table" and "componnt" in d for c, d in found),
                        f"expected an unknown-table finding, got {found}")

    def test_never_raises_on_bad_inputs(self):
        # degrade-safe: a directory where the file is expected -> no read -> []
        (self.addp / "components.toml").mkdir()
        self.assertEqual(self._findings(), [])


# ── command: add.py components ────────────────────────────────────────────────────────
class ComponentsCommand(_Board):
    def test_print_valid_registry(self):
        self._toml(_VALID)
        out, code = self._run(["components"])
        self.assertEqual(code, 0, out)
        for needle in ("gateway", "apps/gateway", "web", "orders", "producer=gateway",
                       "shared", "source="):
            self.assertIn(needle, out)
        self.assertIn("valid", out.lower())

    def test_no_registry_is_friendly_noop(self):
        out, code = self._run(["components"])
        self.assertEqual(code, 0, out)
        self.assertIn("single-component project", out)

    def test_red_integrity_finding_fails_command(self):
        self._toml('[component.gateway]\nroot = "apps/gateway"\n'
                   '[component.api]\nverify = "x"\n')      # api has no root -> RED
        out, code = self._run(["components"])
        self.assertEqual(code, 1, out)
        self.assertIn("components_malformed", out)
        self.assertIn("gateway", out)                      # the well-formed entry still prints

    def test_unknown_key_is_warn_not_failure(self):
        self._toml('[component.web]\nroot = "apps/web"\ngreen-bar = "vitest"\n')
        out, code = self._run(["components"])
        self.assertEqual(code, 0, out)                     # WARN never fails
        self.assertIn("component_unknown_key", out)
        self.assertIn("apps/web", out)                     # the entry's known keys still print

    def test_wrong_type_is_warn(self):
        self._toml('[component.gateway]\nroot = "apps/gateway"\n'
                   '[contract.orders]\nproducer = "gateway"\nconsumers = "web"\n')
        out, code = self._run(["components"])
        self.assertEqual(code, 0, out)
        self.assertIn("component_type_mismatch", out)

    def test_unknown_table_is_warn(self):
        self._toml('[componnt.api]\nroot = "apps/api"\n')
        out, code = self._run(["components"])
        self.assertEqual(code, 0, out)
        self.assertIn("component_unknown_table", out)

    def test_malformed_degrades_no_raise(self):
        self._toml('[component.gateway\nroot = "apps/gateway"\n')   # invalid TOML
        out, code = self._run(["components"])
        self.assertEqual(code, 1, out)
        self.assertIn("components_malformed", out)

    def test_verify_is_never_executed(self):
        # NO-EXEC: a `verify` that would touch a sentinel must be parsed as data only.
        sentinel = self.tmp / "PWNED"
        self._toml(f'[component.gateway]\nroot = "apps/gateway"\n'
                   f'verify = "touch {sentinel}"\n')
        out, code = self._run(["components"])
        self.assertEqual(code, 0, out)
        self.assertIn("gateway", out)          # the command actually ran (not a vacuous pass) ...
        self.assertFalse(sentinel.exists(), "verify was executed — NO-EXEC violated")  # ... and never exec'd verify

    def test_no_project_dies(self):
        bare = Path(tempfile.mkdtemp(prefix="add-cv-bare-")).resolve()
        self.addCleanup(shutil.rmtree, bare, ignore_errors=True)
        os.chdir(bare)                                     # no .add/ here, no .add ancestor in /tmp
        out, code = self._run(["components"])
        self.assertNotEqual(code, 0)
        self.assertIn("no_project", out)


# ── integration: the same lint surfaces at add.py check (never red) ───────────────────
class CheckIntegration(_Board):
    def test_schema_warn_surfaces_at_check_never_red(self):
        self._toml('[component.web]\nroot = "apps/web"\ngreen-bar = "vitest"\n')   # typo only
        out, code = self._run(["check"])
        self.assertEqual(code, 0, out)                     # measure-not-block: never fails
        self.assertIn("WARN", out)
        self.assertIn("component_unknown_key", out)
        self.assertIn("warning", out.lower())              # summary gained "(N warnings)"
        self.assertNotIn("FAIL  component", out)           # no component FAIL line

    def test_integrity_break_stays_red_at_check(self):
        self._toml('[component.api]\nverify = "x"\n')       # api missing root -> RED
        out, code = self._run(["check"])
        self.assertEqual(code, 1, out)
        self.assertIn("components_malformed", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
