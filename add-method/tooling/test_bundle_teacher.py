#!/usr/bin/env python3
"""Ship-truth tests for bundle-teacher (persona-teacher-bundle 2/4). CONTRACT frozen @ v1.

The vendored teacher snapshot (add-method/personas-teacher/, owned by vendor-teacher-snapshot)
must SHIP in both distributions and MATERIALIZE on install:
  - npm:  package.json files allowlist carries personas-teacher/ + THIRD_PARTY_NOTICES.md
          (the tarball-level assertion lives in test_packaging.NpmTarballTest)
  - pip:  prepare_bundle copies it to _bundled/personas-teacher/ (shipped via package-data;
          the wheel-level assertion lives in test_packaging.PyWheelTest)
  - both installers (cli.js MANAGED + _installer.py MANAGED) clean-replace it into
          .add/personas-teacher/ on init/update, never touching user data.
  - the MIT THIRD_PARTY_NOTICES.md ships as a parity-guarded twin in BOTH package roots.
  - engine stays hands-off: ENGINE_MD5 unchanged; no engine module references update_teacher.

Run: python3 -m unittest test_bundle_teacher -v
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent                 # add-method/
_REPO_ROOT = _ADD_METHOD.parent               # repo root
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

CANON_TEACHER = _ADD_METHOD / "personas-teacher"
BUNDLE_TEACHER = _SRC / "add_method" / "_bundled" / "personas-teacher"
NOTICES_CANON = _REPO_ROOT / "THIRD_PARTY_NOTICES.md"
NOTICES_NPM = _ADD_METHOD / "THIRD_PARTY_NOTICES.md"
NOTICES_BUNDLE = _SRC / "add_method" / "_bundled" / "THIRD_PARTY_NOTICES.md"

PKG_JSON = _ADD_METHOD / "package.json"
CLI_JS = _ADD_METHOD / "bin" / "cli.js"
INSTALLER_PY = _SRC / "add_method" / "_installer.py"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _rel_files(root: Path) -> dict:
    return {p.relative_to(root): _md5(p) for p in root.rglob("*") if p.is_file()}


class NpmAllowlistTest(unittest.TestCase):
    """No npm needed — reads package.json directly. The tarball-content assertion is
    in test_packaging.NpmTarballTest; this pins the allowlist so the dir can't silently
    drop (the 1.11.0 trap)."""

    def test_files_allowlist_carries_teacher_and_notices(self):
        pkg = json.loads(PKG_JSON.read_text(encoding="utf-8"))
        files = pkg.get("files", [])
        self.assertTrue(any("personas-teacher" in f for f in files),
                        "package.json files[] must list personas-teacher/ (teacher_absent_from_npm)")
        self.assertIn("THIRD_PARTY_NOTICES.md", files,
                      "package.json files[] must ship THIRD_PARTY_NOTICES.md (attribution_missing)")


class ManagedParityTest(unittest.TestCase):
    """Both installers must declare the teacher as a ship-controlled MANAGED tree."""

    def test_cli_js_manages_teacher(self):
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertIn("personas-teacher", src,
                      "cli.js MANAGED must materialize personas-teacher -> .add/personas-teacher")

    def test_installer_py_manages_teacher(self):
        src = INSTALLER_PY.read_text(encoding="utf-8")
        self.assertIn("personas-teacher", src,
                      "_installer.py MANAGED must materialize personas-teacher -> .add/personas-teacher")
        self.assertIn(".add/personas-teacher", src,
                      "_installer.py must target .add/personas-teacher")


class AttributionShipsBothTest(unittest.TestCase):
    """THIRD_PARTY_NOTICES.md ships as a byte-identical twin in both package roots."""

    def test_notices_present_and_identical(self):
        for p in (NOTICES_CANON, NOTICES_NPM, NOTICES_BUNDLE):
            self.assertTrue(p.is_file(), f"THIRD_PARTY_NOTICES.md must ship at {p} (attribution_missing)")
            self.assertIn("MIT", p.read_text(encoding="utf-8"), f"{p} must carry the MIT notice")
        self.assertEqual(_md5(NOTICES_CANON), _md5(NOTICES_NPM),
                         "npm THIRD_PARTY_NOTICES.md drifted from the repo-root canonical (bundle_drift)")
        self.assertEqual(_md5(NOTICES_CANON), _md5(NOTICES_BUNDLE),
                         "bundle THIRD_PARTY_NOTICES.md drifted from the repo-root canonical (bundle_drift)")


class BundleTeacherParityTest(unittest.TestCase):
    """_bundled/personas-teacher/ must be byte-identical to the canonical snapshot."""

    def test_bundle_teacher_byte_identical(self):
        self.assertTrue(BUNDLE_TEACHER.is_dir(),
                        "_bundled/personas-teacher/ missing — run scripts/prepare_bundle.py (teacher_absent_from_wheel)")
        canon = _rel_files(CANON_TEACHER)
        bundle = _rel_files(BUNDLE_TEACHER)
        self.assertEqual(sorted(map(str, canon)), sorted(map(str, bundle)),
                         "teacher file sets differ between canonical and bundle (bundle_drift)")
        mismatched = [str(rel) for rel in canon if canon[rel] != bundle[rel]]
        self.assertEqual(mismatched, [], f"teacher file(s) differ canonical vs bundle: {mismatched}")


class InitMaterializesTeacherTest(unittest.TestCase):
    """Pip init (hermetic, synthetic bundle) populates .add/personas-teacher/, leaving
    user data untouched. The npm twin is covered by test_heal_reconcile's MANAGED loop."""

    def setUp(self):
        from add_method import _installer       # noqa: E402
        self._installer = _installer
        self.tmp = Path(tempfile.mkdtemp(prefix="bundle-teacher-"))
        self.bundled = self.tmp / "pkg"
        # minimal synthetic bundle mirroring the MANAGED trees
        (self.bundled / "skill" / "add").mkdir(parents=True)
        (self.bundled / "skill" / "add" / "SKILL.md").write_text("skill\n")
        (self.bundled / "tooling" / "templates").mkdir(parents=True)
        (self.bundled / "tooling" / "add.py").write_text("# add tool\n")
        (self.bundled / "docs").mkdir(parents=True)
        (self.bundled / "docs" / "00.md").write_text("doc\n")
        (self.bundled / "personas-teacher" / "engineering").mkdir(parents=True)
        (self.bundled / "personas-teacher" / "engineering" / "agent.md").write_text("agent\n")
        (self.bundled / "personas-teacher" / "LICENSE").write_text("MIT License\n")
        self.proj = self.tmp / "proj"
        self.proj.mkdir()
        (self.proj / ".add").mkdir()
        (self.proj / ".add" / "state.json").write_text(json.dumps({"project": "demo"}) + "\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_materializes_teacher_keeps_user_data(self):
        code = self._installer.install(target=str(self.proj), bundled=str(self.bundled),
                                       non_interactive=True)
        self.assertEqual(code, 0, "install must succeed")
        teacher = self.proj / ".add" / "personas-teacher"
        self.assertTrue(teacher.is_dir(), ".add/personas-teacher/ must be materialized on init")
        self.assertTrue((teacher / "engineering" / "agent.md").is_file(),
                        "the teacher agent defs must be copied into the project")
        self.assertTrue((teacher / "LICENSE").is_file(), "the MIT LICENSE must travel with the snapshot")
        # user data untouched
        self.assertEqual(json.loads((self.proj / ".add" / "state.json").read_text())["project"], "demo",
                         "init must not touch user data (state.json)")


class EngineHandsOffTest(unittest.TestCase):
    def test_engine_unchanged_and_handsoff(self):
        import engine_pin
        live = hashlib.md5((_TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(live, engine_pin.ENGINE_MD5,
                         "bundle-teacher touches no engine code — ENGINE_MD5 must equal the pin")
        engine_src = (_TOOLING / "add.py").read_text(encoding="utf-8")
        for f in (_TOOLING / "add_engine").glob("*.py"):
            engine_src += f.read_text(encoding="utf-8")
        self.assertNotIn("update_teacher", engine_src,
                         "the engine must never reference update_teacher (engine stays hands-off)")
        self.assertNotIn("personas-teacher", engine_src,
                         "the engine must not read the teacher on any path (engine stays hands-off)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
