#!/usr/bin/env python3
"""Red/green tests for retro-artifact (v9 task 2): `milestone-done` persists the
milestone's canonical render to .add/milestones/<v>/RETRO.md at close.

The render SHAPE is frozen by report-render; this suite pins only WHERE/WHEN it is
persisted and the invariants: byte-identical to render_report(width=72, ascii=False),
the retro step is read-only on state.json, and a failed retro write FAILS THE CLOSE
(fail-closed: no done-without-retro). Run:
    python3 -m unittest test_retro -v
"""
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import add


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")


class RetroArtifactTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-retro-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state_file(self) -> Path:
        return self._root() / "state.json"

    def _state(self) -> dict:
        return json.loads(self._state_file().read_text())

    def _retro_file(self, slug) -> Path:
        return self._root() / "milestones" / slug / "RETRO.md"

    def _canonical(self, slug) -> str:
        root = add.find_root()
        return add.render_report(root, add.load_state(root), slug, width=72, ascii=False)

    def _close(self, *args):
        """Run `milestone-done` capturing stdout/stderr; return (out, err, code)."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["milestone-done", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _done_pass(self, slug):
        add.main(["phase", "verify", slug])
        add.main(["gate", "PASS", slug])

    def _make_closable(self, mslug, *tasks):
        """A milestone with >=1 member task, all done+PASS -> ready to close."""
        add.main(["new-milestone", mslug, "--title", "Awareness", "--goal", "see what happened"])
        for t in tasks:
            add.main(["new-task", t, "--title", t.title()])
            self._done_pass(t)
        _meet_exit_criteria(mslug)   # v20 goal-gate: meet criteria before close

    # ---- scenarios --------------------------------------------------------
    def test_close_writes_canonical_retro(self):
        self._make_closable("v9", "alpha")
        out, err, code = self._close("v9")
        self.assertEqual(code, 0, f"close failed: {out}{err}")
        retro = self._retro_file("v9")
        self.assertTrue(retro.exists(), "RETRO.md must be written on a successful close")
        self.assertEqual(retro.read_text(encoding="utf-8"), self._canonical("v9"))
        self.assertNotIn("\x1b[", retro.read_text(encoding="utf-8"))  # no ANSI in the doc

    def test_retro_write_is_state_pure(self):
        # the retro step itself writes exactly one doc and never touches state.json
        self._make_closable("v9", "alpha")
        root = add.find_root()
        state = add.load_state(root)
        before = self._state_file().read_bytes()
        path = add._write_retro(root, state, "v9")
        self.assertEqual(self._state_file().read_bytes(), before)  # state.json untouched
        self.assertEqual(path, self._retro_file("v9"))
        self.assertEqual(path.read_text(encoding="utf-8"),
                         add.render_report(root, state, "v9", width=72, ascii=False))

    def test_close_state_diff_is_status_only(self):
        self._make_closable("v9", "alpha")
        before = self._state()
        out, err, code = self._close("v9")
        self.assertEqual(code, 0, f"{out}{err}")
        after = self._state()
        mb, ma = before["milestones"]["v9"], after["milestones"]["v9"]
        changed = {k for k in set(mb) | set(ma) if mb.get(k) != ma.get(k)}
        # done_actor: the milestone close stamps WHO closed it (user-identity actor-stamping) —
        # a descriptive structured-actor record alongside the status flip, not a decision change.
        self.assertTrue(changed <= {"status", "updated", "done_actor"},
                        f"close mutated more than status/updated/done_actor: {changed}")
        self.assertEqual(ma["status"], "done")
        self.assertEqual(before["tasks"], after["tasks"])  # member tasks untouched

    def test_idempotent_reclose(self):
        self._make_closable("v9", "alpha")
        self._close("v9")
        first = self._retro_file("v9").read_text(encoding="utf-8")
        out, err, code = self._close("v9")            # close again
        self.assertEqual(code, 0, f"{out}{err}")
        self.assertEqual(self._retro_file("v9").read_text(encoding="utf-8"), first)
        self.assertEqual(self._retro_file("v9").read_text(encoding="utf-8"),
                         self._canonical("v9"))

    def test_incomplete_blocks_retro(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])               # stays at specify -> not done
        before = self._state_file().read_bytes()
        out, err, code = self._close("v9")
        self.assertNotEqual(code, 0)
        self.assertIn("milestone_incomplete", out + err)
        self.assertFalse(self._retro_file("v9").exists())   # no retro for a blocked close
        self.assertEqual(self._state_file().read_bytes(), before)  # state unchanged

    def test_failed_write_aborts_close(self):
        # fail-closed: if the retro write raises, the close aborts BEFORE flipping status
        self._make_closable("v9", "alpha")
        with mock.patch.object(add, "_write_retro",
                               side_effect=OSError("disk full"), create=True):
            out, err, code = self._close("v9")
        self.assertNotEqual(code, 0)
        self.assertIn("retro_write_failed", out + err)
        self.assertNotEqual(self._state()["milestones"]["v9"]["status"], "done")


if __name__ == "__main__":
    unittest.main()
