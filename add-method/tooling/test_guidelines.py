#!/usr/bin/env python3
"""Red/green tests for dynamic-by-reference guideline injection (Q7).

`sync-guidelines` writes one stable, marker-delimited ADD block into the project
root's AGENTS.md + CLAUDE.md. The block points the agent at `add.py status` /
PROJECT.md — it NEVER embeds live state (anti-context-rot). `init` runs the same
injection automatically. Run: python3 -m unittest test_guidelines -v
"""
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class GuidelineInjectTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------

    def _fresh_project(self) -> Path:
        """A valid .add/ project with NO guideline files yet.

        init auto-syncs once the feature exists, so strip the guideline files
        afterwards to exercise sync-guidelines from a clean starting state.
        """
        d = Path(tempfile.mkdtemp(prefix="add-guide-")).resolve()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(d)
        add.main(["init", "--name", "demo"])
        for name in ("AGENTS.md", "CLAUDE.md", "AGENTS.md.bak", "CLAUDE.md.bak"):
            (d / name).unlink(missing_ok=True)
        return d

    def _sync(self) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["sync-guidelines"])
        return buf.getvalue()

    # --- scenarios -----------------------------------------------------------

    def test_sync_creates_block_fresh(self):
        d = self._fresh_project()
        self._sync()
        for name in ("AGENTS.md", "CLAUDE.md"):
            f = d / name
            self.assertTrue(f.exists(), f"sync must create {name}")
            text = _read(f)
            self.assertIn(add._GUIDE_BEGIN, text, f"{name} missing begin marker")
            self.assertIn(add._GUIDE_END, text, f"{name} missing end marker")
            self.assertIn("add.py status", text,
                          f"{name} block must point at `add.py status`")

    def test_sync_idempotent_no_bak(self):
        d = self._fresh_project()
        self._sync()
        first = {n: _read(d / n) for n in ("AGENTS.md", "CLAUDE.md")}
        self._sync()
        for n, body in first.items():
            self.assertEqual(_read(d / n), body,
                             f"second sync must leave {n} byte-identical")
        baks = list(d.glob("*.bak"))
        self.assertEqual(baks, [], f"no-op sync must not create backups, got {baks}")

    def test_preserve_outside_restore_inside(self):
        d = self._fresh_project()
        agents = d / "AGENTS.md"
        agents.write_text("# My Project\n\nhand-written user body\n", encoding="utf-8")
        self._sync()                                   # appends the block
        tampered = _read(agents).replace("how to work in this repo", "TAMPERED")
        agents.write_text(tampered, encoding="utf-8")  # edit inside the markers
        self._sync()                                   # must restore the block body
        out = _read(agents)
        self.assertIn("hand-written user body", out, "user text outside markers lost")
        self.assertNotIn("TAMPERED", out, "tampered block body was not restored")
        self.assertIn("how to work in this repo", out, "canonical block not restored")

    def test_backup_on_change(self):
        d = self._fresh_project()
        agents = d / "AGENTS.md"
        agents.write_text("USER CONTENT\n", encoding="utf-8")
        self._sync()
        bak = d / "AGENTS.md.bak"
        self.assertTrue(bak.exists(), "changing an existing file must write a .bak")
        self.assertEqual(_read(bak), "USER CONTENT\n",
                         ".bak must hold the original (pre-block) content")
        self.assertIn("USER CONTENT", _read(agents), "user content must survive")
        self.assertIn(add._GUIDE_BEGIN, _read(agents), "block must be added")

    def test_block_no_live_state(self):
        d = self._fresh_project()
        add.main(["new-task", "secret-slug-xyz", "--title", "Secret"])
        self._sync()
        text = _read(d / "AGENTS.md")
        self.assertNotIn("secret-slug-xyz", text,
                         "block must NOT embed the live task slug (anti-context-rot)")
        self.assertIn("PROJECT.md", text, "block must point at the foundation doc")
        self.assertIn("add.py status", text, "block must point at the resume command")

    def test_symlink_targets_dedup(self):
        d = self._fresh_project()
        os.symlink("AGENTS.md", str(d / "CLAUDE.md"))   # CLAUDE.md -> AGENTS.md
        self._sync()
        agents = _read(d / "AGENTS.md")
        self.assertEqual(agents.count(add._GUIDE_BEGIN), 1,
                         "symlinked targets must be injected exactly once")
        self.assertTrue((d / "CLAUDE.md").is_symlink(),
                        "the symlink must NOT be replaced by a regular file")

    def test_init_auto_syncs(self):
        d = Path(tempfile.mkdtemp(prefix="add-guide-init-")).resolve()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(d)
        add.main(["init", "--name", "demo"])
        for name in ("AGENTS.md", "CLAUDE.md"):
            f = d / name
            self.assertTrue(f.exists(), f"init must auto-create {name}")
            self.assertIn(add._GUIDE_BEGIN, _read(f),
                          f"init must inject the ADD block into {name}")

    def test_unwritable_target_skips(self):
        d = self._fresh_project()
        orig = add._atomic_write

        def fake(path, text):
            if str(path).endswith("AGENTS.md"):
                raise OSError("simulated read-only filesystem")
            return orig(path, text)

        add._atomic_write = fake
        try:
            self._sync()                                # must NOT raise
        finally:
            add._atomic_write = orig
        self.assertIn(add._GUIDE_BEGIN, _read(d / "CLAUDE.md"),
                      "a failed target must not stop the other from syncing")

    def test_non_utf8_existing_file_skips(self):
        # A pre-existing CLAUDE.md/AGENTS.md saved as UTF-16 (common from Windows
        # editors) is not valid UTF-8 -> read_text raises UnicodeDecodeError, NOT
        # OSError. It must be caught (warn+skip), never crash init or the other target.
        d = self._fresh_project()
        raw = "héllo from a windows editor\n".encode("utf-16")
        (d / "AGENTS.md").write_bytes(raw)
        buf = io.StringIO()
        with redirect_stderr(buf):
            self._sync()                                # must NOT raise
        self.assertEqual((d / "AGENTS.md").read_bytes(), raw,
                         "an undecodable target must be left untouched")
        self.assertIn(add._GUIDE_BEGIN, _read(d / "CLAUDE.md"),
                      "a non-UTF-8 target must not stop the other from syncing")
        self.assertIn("skipped", buf.getvalue(), "the skip must be reported on stderr")

    def test_begin_without_end_warns_and_recovers(self):
        # A hand-typed BEGIN with no END is corrupt input: warn, append a fresh
        # complete block, and converge to a single valid block (no perpetual append).
        d = self._fresh_project()
        agents = d / "AGENTS.md"
        agents.write_text(f"# Notes\n{add._GUIDE_BEGIN}\nstray\nuser tail\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stderr(buf):
            self._sync()
        self.assertIn("no ADD:END", buf.getvalue(), "corrupt block must be warned about")
        out = _read(agents)
        self.assertIn(add._GUIDE_END, out, "a complete block must now exist")
        self._sync()                                    # second run must converge
        self.assertEqual(_read(agents).count(add._GUIDE_BEGIN), 1,
                         "repeated syncs must collapse to exactly one block")


if __name__ == "__main__":
    unittest.main(verbosity=2)
