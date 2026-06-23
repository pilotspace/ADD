#!/usr/bin/env python3
"""Red/green tests for the contract-fill gate (milestone flow-enforcement, task contract-fill-gate).

v2 — OPTED-IN ONLY: `milestone-confirm` enforces that the MILESTONE.md
`## Shared / risky contracts` section is FILLED, but ONLY for a milestone that opted into
`--await-confirm` (its state record carries a `confirmed` key). A grandfathered no-key
milestone keeps the plain stamp (census-safe). "confirmed:true" now MEANS the cross-task
contracts were present at confirm time. Shared pure predicate `_section_unfilled` is reused
by the sibling task `build-expectations-gate` for §6.

Run: python3 -m unittest test_contract_fill_gate -v
"""
import contextlib
import io
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

import add

CONTRACTS_HEADER = "## Shared / risky contracts"


class ContractFillGateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-contractfill-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ── helpers ──────────────────────────────────────────────────────────────────────────
    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _ms(self, slug="mvp"):
        return self._state()["milestones"][slug]

    def _ms_path(self, slug="mvp"):
        return Path(self.tmp) / ".add" / "milestones" / slug / "MILESTONE.md"

    def _make(self, slug="mvp", await_confirm=True):
        argv = ["new-milestone", slug, "--goal", "g", "--stage", "mvp"]
        if await_confirm:
            argv.append("--await-confirm")
        add.main(argv)

    def _fill_contracts(self, slug="mvp"):
        p = self._ms_path(slug)
        t = p.read_text()
        # replace the scaffold placeholder bullet with a real, <…>-free contract line
        t = t.replace("- <contract name> -> owning task <slug>",
                      "- real worker-contract shape -> owning task alpha")
        p.write_text(t, encoding="utf-8")

    def _empty_contracts(self, slug="mvp"):
        """Keep the header, drop every bullet under it (section present but empty)."""
        p = self._ms_path(slug)
        lines = p.read_text().splitlines(keepends=True)
        out, in_sec = [], False
        for ln in lines:
            if ln.startswith(CONTRACTS_HEADER):
                in_sec = True
                out.append(ln)
                continue
            if in_sec:
                if ln.startswith("## "):       # next section ends ours
                    in_sec = False
                    out.append(ln)
                continue                        # drop bullets/blank inside the section
            out.append(ln)
        p.write_text("".join(out), encoding="utf-8")

    def _strip_section(self, slug="mvp"):
        """Remove the whole '## Shared / risky contracts' heading + body (legacy MILESTONE.md)."""
        p = self._ms_path(slug)
        t = p.read_text()
        t = re.sub(r"## Shared / risky contracts.*?(?=\n## )", "", t, flags=re.DOTALL)
        p.write_text(t, encoding="utf-8")

    @staticmethod
    def _die_stderr(argv):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                add.main(argv)
            except SystemExit as e:
                return e.code, err.getvalue()
        raise AssertionError(f"expected SystemExit from {argv}")

    def _confirm_ok(self, slug="mvp"):
        with contextlib.redirect_stdout(io.StringIO()):
            add.main(["milestone-confirm", slug])

    # ── opted-in: filled contracts confirm ───────────────────────────────────────────────
    def test_optedin_filled_contracts_confirm(self):
        self._make(await_confirm=True)
        self._fill_contracts()
        self._confirm_ok()
        self.assertIs(self._ms().get("confirmed"), True)

    # ── opted-in: placeholder contracts refuse ───────────────────────────────────────────
    def test_optedin_placeholder_refuse(self):
        self._make(await_confirm=True)            # scaffold placeholder left untouched
        before = self._ms_path().read_text()
        state_before = (Path(self.tmp) / ".add" / "state.json").read_text()
        code, err = self._die_stderr(["milestone-confirm", "mvp"])
        self.assertEqual(code, 1)
        self.assertIn("milestone_contracts_unfilled", err)
        self.assertIs(self._ms().get("confirmed"), False, "refused confirm must leave confirmed:false")
        self.assertEqual((Path(self.tmp) / ".add" / "state.json").read_text(), state_before,
                         "validate-then-write: a refused confirm mutates no state")
        self.assertEqual(self._ms_path().read_text(), before)

    # ── opted-in: empty section refuse ───────────────────────────────────────────────────
    def test_optedin_empty_section_refuse(self):
        self._make(await_confirm=True)
        self._empty_contracts()
        code, err = self._die_stderr(["milestone-confirm", "mvp"])
        self.assertEqual(code, 1)
        self.assertIn("milestone_contracts_unfilled", err)
        self.assertIs(self._ms().get("confirmed"), False)

    # ── NOT opted-in: never content-gated (census-safe) ──────────────────────────────────
    def test_no_key_milestone_not_gated(self):
        self._make(await_confirm=False)           # no confirmed key, scaffold placeholder
        self.assertNotIn("confirmed", self._ms())
        self._confirm_ok()                         # plain stamp — gate skipped despite placeholder
        self.assertIs(self._ms().get("confirmed"), True)

    # ── opted-in legacy: section absent → grandfather ────────────────────────────────────
    def test_optedin_legacy_no_section_grandfathered(self):
        self._make(await_confirm=True)
        self._strip_section()
        self.assertNotIn(CONTRACTS_HEADER, self._ms_path().read_text())
        self._confirm_ok()
        self.assertIs(self._ms().get("confirmed"), True)

    # ── unknown slug still refuses FIRST ─────────────────────────────────────────────────
    def test_unknown_slug_still_first(self):
        code, err = self._die_stderr(["milestone-confirm", "ghost"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_milestone", err)

    # ── the pure predicate ───────────────────────────────────────────────────────────────
    def test_section_unfilled_predicate(self):
        H = CONTRACTS_HEADER
        placeholder = f"{H}\n- <contract name> -> owning task <slug>\n\n## Next\n"
        filled = f"{H}\n- a real contract -> owning task alpha\n\n## Next\n"
        empty = f"{H}\n\n## Next\n"
        absent = "## Scope\n- something\n\n## Next\n"
        self.assertTrue(add._section_unfilled(placeholder, H), "placeholder -> unfilled")
        self.assertTrue(add._section_unfilled(empty, H), "empty -> unfilled")
        self.assertFalse(add._section_unfilled(filled, H), "filled -> filled")
        self.assertFalse(add._section_unfilled(absent, H), "absent -> grandfather (not unfilled)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
