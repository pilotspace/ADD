#!/usr/bin/env python3
"""`.add/.gitignore` carries pre-update-state.bak.json AND is seeded/refreshed on update
by both installers (task: gitignore-bak-seed).

The update backup `.add/pre-update-state.bak.json` (written by cli.js:cmdUpdate and the pip
update twin) was leaking into git because the ignore seed never listed it. This:
  - adds the line to the canonical body, single-sourced in tooling/templates/gitignore.tmpl,
    kept byte-identical to the engine `_GITIGNORE_BODY` constant (parity);
  - has BOTH installers seed `.add/.gitignore` if missing, ELSE append-if-absent the missing
    engine-transient pattern lines (additive-only, idempotent, fail-soft) — so an existing
    project gains the line on update without losing user-added lines.

cli.js carries no node harness, so its half is a text-invariant proof (like test_update.py).

Run: python3 -m unittest test_gitignore_bak_seed -v
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import add  # engine (canonical tooling tree)

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from add_method import _installer  # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"
GITIGNORE_TMPL = _ADD_METHOD / "tooling" / "templates" / "gitignore.tmpl"


class EngineSeedBody(unittest.TestCase):
    def test_init_gitignore_lists_pre_update_bak(self):
        cwd = Path.cwd()
        tmp = tempfile.mkdtemp(prefix="gi-init-")
        os.chdir(tmp)
        try:
            add.main(["init", "--name", "demo", "--stage", "mvp"])
            body = (Path(tmp) / ".add" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("pre-update-state.bak.json", body,
                          "the init seed must ignore the update backup")
            self.assertIn("pre-archive-state.bak.json", body, "prior entries kept")
            self.assertIn("scope-snapshot.json", body)
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_template_matches_constant(self):
        # single source of truth: the bundled template == the engine fallback constant
        self.assertTrue(GITIGNORE_TMPL.exists(), "tooling/templates/gitignore.tmpl must exist")
        self.assertEqual(GITIGNORE_TMPL.read_text(encoding="utf-8"), add._GITIGNORE_BODY,
                         "gitignore.tmpl must be byte-identical to _GITIGNORE_BODY (no drift)")


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    tdir = root / "tooling" / "templates"
    tdir.mkdir(parents=True)
    (tdir / "SOUL.md.tmpl").write_text("# SOUL\nvoice\n")
    # synthetic body: a comment + three patterns (one of which the dest will already have)
    (tdir / "gitignore.tmpl").write_text(
        "# transient artifacts\nscope-snapshot.json\npre-update-state.bak.json\n.update-cache.json\n"
    )
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


class PipSeedGitignore(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gi-pip-"))
        self.proj = self.tmp / "proj"
        (self.proj / ".add").mkdir(parents=True)
        self.bundled = _make_bundled(self.tmp / "pkg")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gi(self) -> Path:
        return self.proj / ".add" / ".gitignore"

    def test_seed_when_missing(self):
        _installer._seed_gitignore(self.proj, self.bundled)
        self.assertTrue(self._gi().exists(), "a missing .gitignore must be seeded")
        self.assertIn("pre-update-state.bak.json", self._gi().read_text(encoding="utf-8"))

    def test_append_if_absent_preserves_user_lines(self):
        # existing partial file: has one pattern + a user line, lacks pre-update-state.bak.json
        self._gi().write_text("scope-snapshot.json\nmy-secret.local\n", encoding="utf-8")
        _installer._seed_gitignore(self.proj, self.bundled)
        body = self._gi().read_text(encoding="utf-8")
        self.assertIn("pre-update-state.bak.json", body, "missing pattern appended")
        self.assertIn("my-secret.local", body, "user-added line preserved")
        self.assertNotIn("# transient artifacts", body, "comment lines are NOT appended")
        # idempotent: a second run adds no duplicate
        _installer._seed_gitignore(self.proj, self.bundled)
        self.assertEqual(self._gi().read_text(encoding="utf-8").count("pre-update-state.bak.json"), 1)

    def test_missing_template_is_fail_soft(self):
        # no gitignore.tmpl in this bundled root -> log + return, never raise
        bare = _make_bundled(self.tmp / "bare")
        (bare / "tooling" / "templates" / "gitignore.tmpl").unlink()
        try:
            _installer._seed_gitignore(self.proj, bare)
        except Exception as e:  # noqa: BLE001
            self.fail(f"_seed_gitignore must be fail-soft, raised {e!r}")


class NpmTwin(unittest.TestCase):
    def _src(self) -> str:
        return CLI_JS.read_text(encoding="utf-8")

    def test_seed_gitignore_defined(self):
        src = self._src()
        self.assertRegex(src, r"function\s+seedGitignore\s*\(",
                         "cli.js must define a seedGitignore twin")
        self.assertIn("gitignore.tmpl", src,
                      "seedGitignore must seed from tooling/templates/gitignore.tmpl")

    def test_seed_gitignore_wired_in_both_paths(self):
        import re
        src = self._src()
        for fn in ("dropFiles", "cmdUpdate"):
            m = re.search(rf"function\s+{fn}\s*\([\s\S]*?\n\}}", src)
            self.assertIsNotNone(m, f"could not locate {fn}")
            self.assertIn("seedGitignore(", m.group(0),
                          f"{fn} must call seedGitignore( (npm<->pip parity)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
