#!/usr/bin/env python3
"""Asset-truth tests for vendor-teacher-snapshot (persona-teacher-bundle 1/4). CONTRACT frozen @ v1.

A pinned RAW snapshot of the teacher corpus is vendored under add-method/personas-teacher/ — agent
definition .md files under their domain folders, copied verbatim from a recorded upstream commit,
trimmed to agent material. Its MIT LICENSE is retained and a repo-root THIRD_PARTY_NOTICES.md carries
the attribution; VENDOR.md records the pin; a standalone update_teacher.py reproduces it. No engine
code is touched (engine NO-EXEC; the refresh is never wired into add.py). Run:
python3 -m unittest test_teacher_snapshot -v
"""
import hashlib
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent        # repo root

TEACHER = PKG_ROOT / "personas-teacher"
NOTICES = REPO_ROOT / "THIRD_PARTY_NOTICES.md"
UPDATE = PKG_ROOT / "scripts" / "update_teacher.py"

# domain folders we expect to survive the trim (a representative subset)
KEPT_FOLDERS = ("engineering", "security", "design", "product", "finance")
# upstream dirs/files the trim must drop
DROPPED = (".github", "scripts", "integrations", "CONTRIBUTING.md")


class TeacherSnapshotTest(unittest.TestCase):
    def test_snapshot_present_and_pinned(self):
        self.assertTrue(TEACHER.is_dir(), "add-method/personas-teacher/ must exist")
        mds = list(TEACHER.rglob("*.md"))
        self.assertGreater(len(mds), 200,
                           f"expected >200 vendored agent-def .md, found {len(mds)}")
        vendor = TEACHER / "VENDOR.md"
        self.assertTrue(vendor.is_file(), "personas-teacher/VENDOR.md (the pin record) must exist")
        text = vendor.read_text(encoding="utf-8")
        self.assertRegex(text, r"\b[0-9a-f]{40}\b",
                         "VENDOR.md must record a 40-hex upstream commit SHA (pin_unrecorded)")

    def test_license_retained(self):
        lic = TEACHER / "LICENSE"
        self.assertTrue(lic.is_file(), "personas-teacher/LICENSE must be retained (attribution_missing)")
        self.assertIn("MIT License", lic.read_text(encoding="utf-8"),
                      "the retained LICENSE must be the upstream MIT license")
        self.assertTrue(NOTICES.is_file(),
                        "repo-root THIRD_PARTY_NOTICES.md must exist (attribution_missing)")
        ntext = NOTICES.read_text(encoding="utf-8")
        self.assertIn("personas-teacher", ntext, "NOTICES must name the vendored component path")
        self.assertIn("MIT", ntext, "NOTICES must carry the MIT notice")

    def test_trim_applied(self):
        for folder in KEPT_FOLDERS:
            self.assertTrue((TEACHER / folder).is_dir(),
                            f"kept agent-def domain folder '{folder}' must be vendored")
        for dropped in DROPPED:
            self.assertFalse((TEACHER / dropped).exists(),
                             f"upstream '{dropped}' must be trimmed out of the snapshot")

    def test_update_script_standalone(self):
        self.assertTrue(UPDATE.is_file(), "add-method/scripts/update_teacher.py must exist")
        src = UPDATE.read_text(encoding="utf-8")
        self.assertIn("clone", src, "update_teacher.py must clone upstream at a ref")
        self.assertIn("VENDOR.md", src, "update_teacher.py must rewrite the VENDOR.md pin")
        # the refresh is NEVER imported/invoked by the engine (engine NO-EXEC)
        engine_src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for f in (TOOLING / "add_engine").glob("*.py"):
            engine_src += f.read_text(encoding="utf-8")
        self.assertNotIn("update_teacher", engine_src,
                         "the engine must never reference update_teacher (fetch_in_engine_or_release)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
