#!/usr/bin/env python3
"""Red/green tests for rule-file mode (ccsk-style guideline relocation).

For ccsk projects (a `.ccsk/` dir) or an explicit `--rule-file`, the CLAUDE.md block is
relocated to `.claude/rules/add-workflows.md` and CLAUDE.md keeps only a reference bullet
under a Workflows/Rules heading. This is CLAUDE-only — AGENTS.md keeps the inline block.
The mode is re-derived from disk each phase (no persisted state). Idempotent; migrates a
prior inline block out of CLAUDE.md.

Run: python3 -m unittest test_rule_file_mode -v
"""
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class RuleFileModeTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------

    def _fresh_project(self) -> Path:
        """A valid .add/ project with the auto-synced guideline files stripped."""
        d = Path(tempfile.mkdtemp(prefix="add-rule-")).resolve()
        os.chdir(d)
        add.main(["init", "--name", "demo"])
        for name in ("AGENTS.md", "CLAUDE.md", "AGENTS.md.bak", "CLAUDE.md.bak"):
            (d / name).unlink(missing_ok=True)
        return d

    def _sync(self, *flags) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(["sync-guidelines", *flags])
        return buf.getvalue()

    @property
    def _rules_path(self) -> Path:
        return Path(add.RULES_FILE_REL)

    # --- detection -----------------------------------------------------------

    def test_mode_off_by_default(self):
        d = self._fresh_project()
        self.assertFalse(add._rule_file_mode(d), "plain project must NOT be rule-file mode")

    def test_mode_on_ccsk(self):
        d = self._fresh_project()
        (d / ".ccsk").mkdir()
        self.assertTrue(add._rule_file_mode(d), ".ccsk/ dir must trigger rule-file mode")

    def test_mode_on_flag(self):
        d = self._fresh_project()
        self.assertTrue(add._rule_file_mode(d, True), "explicit flag must trigger rule-file mode")

    def test_mode_on_existing_rule_file(self):
        d = self._fresh_project()
        (d / add.RULES_FILE_REL).parent.mkdir(parents=True)
        (d / add.RULES_FILE_REL).write_text("x", encoding="utf-8")
        self.assertTrue(add._rule_file_mode(d),
                        "a prior rule file must keep the project in rule-file mode")

    # --- the relocation ------------------------------------------------------

    def test_flag_relocates_claude_keeps_agents_inline(self):
        d = self._fresh_project()
        self._sync("--rule-file")
        rules = d / add.RULES_FILE_REL
        self.assertTrue(rules.exists(), "rule file must be created")
        self.assertIn(add._GUIDE_BEGIN, _read(rules), "rule file holds the full marked block")
        claude = _read(d / "CLAUDE.md")
        self.assertIn("add-workflows.md", claude, "CLAUDE.md must reference the rule file")
        self.assertNotIn(add._GUIDE_BEGIN, claude, "CLAUDE.md must NOT hold the inline block")
        self.assertIn("## Workflows", claude, "a Workflows section must be created")
        # AGENTS.md stays inline
        agents = _read(d / "AGENTS.md")
        self.assertIn(add._GUIDE_BEGIN, agents, "AGENTS.md must keep the inline block")

    def test_ccsk_autodetect_at_sync(self):
        d = self._fresh_project()
        (d / ".ccsk").mkdir()
        self._sync()                                   # no flag — ccsk alone drives it
        self.assertTrue((d / add.RULES_FILE_REL).exists(),
                        "ccsk project must auto-relocate without the flag")
        self.assertNotIn(add._GUIDE_BEGIN, _read(d / "CLAUDE.md"))

    def test_init_autodetect_ccsk(self):
        d = Path(tempfile.mkdtemp(prefix="add-rule-init-")).resolve()
        os.chdir(d)
        (d / ".ccsk").mkdir()
        add.main(["init", "--name", "demo"])
        self.assertTrue((d / add.RULES_FILE_REL).exists(),
                        "init in a ccsk project must land in rule-file mode")
        self.assertIn("add-workflows.md", _read(d / "CLAUDE.md"))

    # --- find-or-create heading ---------------------------------------------

    def test_inserts_under_existing_heading(self):
        d = self._fresh_project()
        (d / "CLAUDE.md").write_text(
            "# Proj\n\n## Rules\n\n- a: ./.claude/rules/a.md\n\n## Tail\n\nx\n",
            encoding="utf-8")
        self._sync("--rule-file")
        out = _read(d / "CLAUDE.md")
        self.assertEqual(out.count("## Workflows"), 0,
                         "must reuse the existing Rules heading, not add a Workflows one")
        # bullet sits inside the Rules section, before ## Tail
        self.assertLess(out.index("add-workflows.md"), out.index("## Tail"),
                        "reference must be inserted within the matched section")

    def test_creates_workflows_when_no_section(self):
        d = self._fresh_project()
        (d / "CLAUDE.md").write_text("# Proj\n\nintro only\n", encoding="utf-8")
        self._sync("--rule-file")
        out = _read(d / "CLAUDE.md")
        self.assertIn("## Workflows", out, "must append a Workflows section when none exists")
        self.assertIn("intro only", out, "existing content must be preserved")

    # --- migration -----------------------------------------------------------

    def test_migrates_inline_block_out(self):
        d = self._fresh_project()
        inline = (f"# Proj\n\nhead\n\n{add._GUIDE_BEGIN}\n## ADD\nOLD INLINE\n{add._GUIDE_END}\n"
                  "\n## Other\n\ntail\n")
        (d / "CLAUDE.md").write_text(inline, encoding="utf-8")
        self._sync("--rule-file")
        out = _read(d / "CLAUDE.md")
        self.assertNotIn(add._GUIDE_BEGIN, out, "inline block must be removed from CLAUDE.md")
        self.assertNotIn("OLD INLINE", out, "inline body must be gone")
        self.assertIn("head", out, "content before the block survives")
        self.assertIn("## Other", out, "content after the block survives")
        self.assertIn("add-workflows.md", out, "reference must be added")
        self.assertIn(add._GUIDE_BEGIN, _read(d / add.RULES_FILE_REL),
                      "the full block must now live in the rule file")

    # --- idempotency ---------------------------------------------------------

    def test_idempotent_no_dupes_no_bak(self):
        d = self._fresh_project()
        (d / ".ccsk").mkdir()
        self._sync()
        out = self._sync()
        self.assertIn("unchanged", out, "second sync must report unchanged")
        claude = _read(d / "CLAUDE.md")
        self.assertEqual(claude.count("add-workflows.md"), 1, "no duplicate reference bullet")
        # a no-op second run leaves no fresh backups
        self.assertFalse((d / "CLAUDE.md.bak").exists() and
                         _read(d / "CLAUDE.md.bak") == claude,
                         "no-op sync must not churn CLAUDE.md.bak")


if __name__ == "__main__":
    unittest.main()
