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
import subprocess
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
BUNDLED_GITIGNORE_TMPL = (_ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" /
                          "templates" / "gitignore.tmpl")

# the 3 installer-managed vendor trees (task: installer-gitignore-mirrors) — regenerable/
# vendored copies the installer drops in, never project-authored, so never committed.
# Split by WHERE the pattern is allowed to live: .add/tooling/ and .add/docs/ are safe in
# the shared engine template/constant; .add/personas-teacher/ must stay OUT of the engine
# (test_engine_unchanged_and_handsoff) and is added by the installer twins only.
ENGINE_MANAGED_TREE_PATTERNS = (".add/tooling/", ".add/docs/")
ALL_MANAGED_TREE_PATTERNS = ENGINE_MANAGED_TREE_PATTERNS + (".add/personas-teacher/",)


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

    def test_init_gitignore_lists_managed_trees(self):     # M1, R:gitignore_source_drift
        cwd = Path.cwd()
        tmp = tempfile.mkdtemp(prefix="gi-managed-")
        os.chdir(tmp)
        try:
            add.main(["init", "--name", "demo", "--stage", "mvp"])
            body = (Path(tmp) / ".add" / ".gitignore").read_text(encoding="utf-8")
            for pattern in ENGINE_MANAGED_TREE_PATTERNS:
                self.assertIn(pattern, body,
                              f"the init seed must ignore the managed vendor tree {pattern!r}")
            # direct `add.py init` uses the engine's OWN _GITIGNORE_BODY fallback, which must
            # stay hands-off of the teacher tree — that pattern is seeded only via the
            # installer twins (cli.js / _installer.py), not this direct-engine path.
            self.assertNotIn(".add/personas-teacher/", body,
                              "direct add.py init must not seed the personas-teacher pattern "
                              "(engine hands-off boundary — see the installer twins instead)")
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_engine_gitignore_body_excludes_personas_teacher(self):   # hands-off invariant
        # belt-and-suspenders alongside test_bundle_teacher.py::test_engine_unchanged_and_
        # handsoff: the engine's shared template/constant must never name the teacher tree.
        self.assertNotIn("personas-teacher", GITIGNORE_TMPL.read_text(encoding="utf-8"))
        self.assertNotIn("personas-teacher", add._GITIGNORE_BODY)

    def test_bundled_template_matches_canonical(self):     # M3, R:gitignore_source_drift
        self.assertTrue(BUNDLED_GITIGNORE_TMPL.exists(),
                        "the bundled tooling/templates/gitignore.tmpl copy must exist")
        self.assertEqual(GITIGNORE_TMPL.read_text(encoding="utf-8"),
                         BUNDLED_GITIGNORE_TMPL.read_text(encoding="utf-8"),
                         "the bundled template copy must be byte-identical to the canonical one")


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

    def test_seed_appends_managed_trees_preserves_custom_lines(self):   # M1/M2, R:gitignore_append_destructive
        # against the REAL canonical template (not the synthetic fixture above) — proves
        # production content, not just the generic append mechanism.
        self._gi().write_text("scope-snapshot.json\nmy-secret.local\n", encoding="utf-8")
        _installer._seed_gitignore(self.proj, _ADD_METHOD)
        body = self._gi().read_text(encoding="utf-8")
        for pattern in ALL_MANAGED_TREE_PATTERNS:
            self.assertIn(pattern, body, f"managed tree pattern {pattern!r} must be appended")
        self.assertIn("my-secret.local", body, "user-added line preserved")

    def test_personas_teacher_entry_unconditional_even_when_absent(self):   # M1, R:gitignore_entry_conditional
        # self.proj never has a .add/personas-teacher/ tree on disk in this fixture —
        # the pattern must still be seeded/appended, with no error.
        self.assertFalse((self.proj / ".add" / "personas-teacher").exists())
        try:
            _installer._seed_gitignore(self.proj, _ADD_METHOD)
        except Exception as e:  # noqa: BLE001
            self.fail(f"seeding must not require the tree to exist, raised {e!r}")
        body = self._gi().read_text(encoding="utf-8")
        self.assertIn(".add/personas-teacher/", body,
                      "the personas-teacher pattern must be present even when the tree is absent")


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

    def test_cli_js_seed_lists_managed_trees_on_init(self):   # M1, M4
        # a real node execution against the REAL PKG_ROOT (cli.js resolves it relative to
        # its own __dirname, independent of cwd) — proves the npm twin against production
        # content, not just a text-invariant regex.
        if not shutil.which("node"):
            self.skipTest("node not available")
        tmp = tempfile.mkdtemp(prefix="gi-npm-")
        try:
            r = subprocess.run(["node", str(CLI_JS), "init", tmp, "--yes"],
                               capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, f"npm init failed: {r.stdout}{r.stderr}")
            body = (Path(tmp) / ".add" / ".gitignore").read_text(encoding="utf-8")
            for pattern in ALL_MANAGED_TREE_PATTERNS:
                self.assertIn(pattern, body,
                              f"cli.js init must seed the managed tree pattern {pattern!r}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
