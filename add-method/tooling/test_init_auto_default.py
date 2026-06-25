#!/usr/bin/env python3
"""Red/green tests for the project-level autonomy default (task init-auto-default).

The autonomy posture stops being a constant buried in the TASK.md template and
becomes EXPLICIT + project-scoped + INHERITABLE:

  * init      — writes a header line `autonomy: auto` into PROJECT.md.
  * new-task  — seeds the new TASK.md `autonomy:` line from the project's DECLARED
                default (inherit), not a hardcoded constant. Fail-SAFE read:
                  declared & recognized -> that rung
                  no `autonomy:` line   -> "auto"          (v7: absent = auto)
                  garbled / unknown     -> "conservative"  (NEVER silently auto) + warn
  * status    — surfaces the project autonomy default every session.

These are the FROZEN-shape contract for init-auto-default. Run red before Build:

    cd add-method/tooling && python3 -m unittest test_init_auto_default -v
"""
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent          # add-method/tooling -> add-method -> repo root

# the three template trees kept byte-aligned (canonical · bundled · dogfood)
TEMPLATE_TREES = (
    "add-method/tooling/templates",
    "add-method/src/add_method/_bundled/tooling/templates",
    ".add/tooling/templates",
)


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-iad-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _project_md(self) -> Path:
        return self._root() / "PROJECT.md"

    def _task_header(self, slug: str) -> str:
        text = (self._root() / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")
        return text.split("\n## ", 1)[0]

    def _set_project_autonomy(self, level):
        """Rewrite PROJECT.md to declare exactly one autonomy posture (or none).

        Robust to whether `init` already wrote a line: strip every existing
        `autonomy:` line, then (if level is not None) insert one after `slug:`.
        """
        p = self._project_md()
        lines = [ln for ln in p.read_text(encoding="utf-8").splitlines()
                 if not ln.lstrip().startswith("autonomy:")]
        if level is not None:
            out = []
            for ln in lines:
                out.append(ln)
                if ln.startswith("slug:"):
                    out.append(f"autonomy: {level}")
            lines = out
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _new_task(self, slug: str):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])
        return out.getvalue(), err.getvalue()

    def _status(self) -> str:
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            add.main(["status"])
        return out.getvalue()


# ============================================================================
# init declares the project default
# ============================================================================
class InitWritesDefaultTest(_Board):

    def test_init_writes_autonomy_auto(self):
        self.assertIn("autonomy: auto", self._project_md().read_text(encoding="utf-8"),
                      "init must declare `autonomy: auto` in PROJECT.md")


# ============================================================================
# new-task inherits the declared project default
# ============================================================================
class InheritTest(_Board):

    def test_new_task_inherits_auto(self):
        # the established seed contract: a default project seeds auto
        self._new_task("fresh")
        self.assertIn("autonomy: auto", self._task_header("fresh"))

    def test_non_auto_default_inherited(self):
        # LOAD-BEARING: a declared NON-auto default must FLOW into the new task
        # (proves the PROJECT.md line is load-bearing, not cosmetic).
        self._set_project_autonomy("conservative")
        self._new_task("t2")
        hdr = self._task_header("t2")
        self.assertIn("autonomy: conservative", hdr)
        self.assertNotIn("autonomy: auto", hdr)

    def test_absent_project_autonomy_defaults_auto(self):
        # no autonomy line -> method default auto (v7: absent = auto)
        self._set_project_autonomy(None)
        self._new_task("t3")
        self.assertIn("autonomy: auto", self._task_header("t3"))

    def test_garbled_project_autonomy_failsafe_conservative(self):
        # a garbled line degrades fail-SAFE to conservative + warns; NEVER auto.
        self._set_project_autonomy("yolo")
        out, err = self._new_task("t4")
        hdr = self._task_header("t4")
        self.assertIn("autonomy: conservative", hdr, "garbled -> fail-safe conservative seed")
        self.assertNotIn("autonomy: auto", hdr, "a corrupt posture must NEVER yield auto")
        self.assertIn("garbled_project_autonomy", out + err, "garbled posture must warn")


# ============================================================================
# status surfaces the project default
# ============================================================================
class StatusSurfaceTest(_Board):

    def test_status_surfaces_project_default(self):
        out = self._status()
        self.assertRegex(out, r"(?i)project autonomy:\s*auto",
                         "status must name the project autonomy default")


# ============================================================================
# the read-path helper resolves every case (fail-SAFE)
# ============================================================================
class HelperTest(_Board):

    def test_project_autonomy_helper_resolves(self):
        root = self._root()
        self._set_project_autonomy("auto")
        self.assertEqual(add._project_autonomy(root), "auto")
        self._set_project_autonomy("conservative")
        self.assertEqual(add._project_autonomy(root), "conservative")
        self._set_project_autonomy(None)
        self.assertEqual(add._project_autonomy(root), "auto", "absent -> method default auto")
        self._set_project_autonomy("yolo")
        self.assertEqual(add._project_autonomy(root), "conservative", "garbled -> fail-safe conservative")


# ============================================================================
# template parity — all three trees carry the change
# ============================================================================
class TemplateParityTest(unittest.TestCase):

    def test_templates_carry_autonomy_3_trees(self):
        for tree in TEMPLATE_TREES:
            proj = (REPO / tree / "PROJECT.md.tmpl").read_text(encoding="utf-8")
            task = (REPO / tree / "TASK.md.tmpl").read_text(encoding="utf-8")
            self.assertIn("autonomy: auto", proj,
                          f"{tree}/PROJECT.md.tmpl must declare `autonomy: auto`")
            self.assertIn("{{autonomy}}", task,
                          f"{tree}/TASK.md.tmpl must inherit via the {{{{autonomy}}}} token")


if __name__ == "__main__":
    unittest.main()
