#!/usr/bin/env python3
"""Red/green tests for the fast-lane Boundary: line (task fast-lane-boundary-line,
frozen contract v1, quality-floors lever 2): the fast template's §1 gains a
`Boundary:` line (>=1 format-variant per external input shape, or an explicit
"none"), and cmd_freeze refuses a task whose Boundary value is still the bare
template placeholder — `boundary_unfilled`, fired after unflagged_freeze in the
validate block, before any write, on BOTH freeze paths. A task with NO Boundary:
line is grandfathered (legacy fast + full lane behavior byte-identical).

Evidence class (benchmark WV1 wm2): the lean arm's red suite spoke naive
timestamps — a friendlier dialect than the spec's own Z-suffixed examples —
and shipped the aware/naive crash green. The Boundary line makes the input-
format variants an explicit, freeze-checked declaration at the fast lane's
single approval seam.

Run: python3 -m unittest test_fast_boundary_line -v
"""
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "templates"

PLACEHOLDER_BOUNDARY = ("Boundary: <one format-variant per external input shape "
                        "the tests must speak — e.g. aware vs naive timestamp "
                        '· or "none — no external input">')
REAL_BOUNDARY = "Boundary: aware (Z-suffixed) vs naive timestamp on booking.start_time"
NONE_BOUNDARY = "Boundary: none — no external input"


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board through the real CLI — the test_spec_dialect_floor idiom,
    duplicated per this repo's one-harness-per-file norm."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-boundary-line-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _write_task(self, slug: str, boundary_line: str | None, *, oneshot=False):
        spec1 = ["Feature: f", "Must:", "  - m", "Accept: Given g, When w, Then t"]
        if boundary_line is not None:
            spec1.append(boundary_line)
        header = [f"# TASK: {slug}",
                  f"slug: {slug} · created: 2026-07-11 · stage: mvp",
                  "fast: true"]
        if oneshot:
            header += ["oneshot: true", "gate_mode: ai-plan-verify"]
        sec3 = ["```", "shape: f(x) -> ok · bad -> err", "```",
                "Least-sure flag surfaced at freeze: [contract] narrow "
                "shape — cost: one re-freeze.",
                "Status: DRAFT"]
        if oneshot:
            sec3 += ["", "### AI-verify record (required when gate_mode: ai-plan-verify)",
                     "- [x] §0 GROUND anchors resolve in the current tree",
                     "- [x] §1 every Must + every Reject present, each Reject paired with an error code",
                     "- [x] §3 CONTRACT shape is concrete (no template placeholder text remains)",
                     "- [x] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)",
                     "Verified by: test-agent · at: 2026-07-11T00:00:00Z"]
        lines = [
            *header,
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance"),
            *_section(1, "SPECIFY", *spec1),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT", *sec3),
            *_section(4, "TESTS", "Tests live in: `./tests/`"),
            *_section(5, "BUILD",
                      "Scope (may touch): `src/`",
                      "Code lives in: `./src/`"),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _make_at_contract(self, slug: str, boundary_line: str | None):
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug, boundary_line)
        self._silent("phase", "contract", slug)

    def _freeze(self, slug: str, *extra):
        return self._run("freeze", slug, "--by", "Tester", *extra)


# ── M1: the fast template scaffold carries the line ─────────────────────────
class TemplateScaffoldTest(unittest.TestCase):
    def test_fast_template_carries_boundary_line_after_accept(self):
        body = (TEMPLATES / "TASK.fast.md.tmpl").read_text(encoding="utf-8")
        self.assertIn("\nBoundary: <", body, "§1 must scaffold a Boundary: line")
        acc = body.find("\nAccept: ")
        bnd = body.find("\nBoundary: ")
        self.assertGreater(bnd, acc, "Boundary: rides directly after Accept:")
        line = re.search(r"(?m)^Boundary: .*$", body).group(0)
        self.assertIn("format-variant", line)
        self.assertIn("none — no external input", line)


# ── M2: a placeholder Boundary refuses the freeze, nothing written ───────────
class PlaceholderRefusedTest(_Board):
    def test_freeze_refuses_placeholder_boundary(self):
        self._make_at_contract("t", PLACEHOLDER_BOUNDARY)
        state_before = (self._root() / "state.json").read_bytes()
        md_before = self._task_md("t").read_bytes()
        out, err, code = self._freeze("t")
        self.assertNotEqual(code, 0, "a placeholder Boundary must refuse the freeze")
        self.assertIn("boundary_unfilled", out + err)
        self.assertEqual((self._root() / "state.json").read_bytes(), state_before,
                         "validate-then-write: state.json must be untouched")
        self.assertEqual(self._task_md("t").read_bytes(), md_before,
                         "validate-then-write: §3 must stay DRAFT, zero bytes written")

    def test_empty_boundary_value_also_refused(self):
        self._make_at_contract("t", "Boundary:")
        out, err, code = self._freeze("t")
        self.assertNotEqual(code, 0)
        self.assertIn("boundary_unfilled", out + err)

    def test_ai_plan_verify_path_also_refuses(self):
        # the guard sits in the shared validate block, before the ai branch —
        # an AI freeze may not slip a placeholder Boundary past the floor
        self._silent("new-task", "t", "--title", "t")
        self._write_task("t", PLACEHOLDER_BOUNDARY, oneshot=True)
        self._silent("phase", "contract", "t")
        out, err, code = self._run("freeze", "t", "--ai-plan-verify",
                                   "--by", "test-agent")
        self.assertNotEqual(code, 0)
        self.assertIn("boundary_unfilled", out + err)

    def test_ai_plan_verify_path_freezes_real_value(self):
        self._silent("new-task", "t", "--title", "t")
        self._write_task("t", REAL_BOUNDARY, oneshot=True)
        self._silent("phase", "contract", "t")
        out, err, code = self._run("freeze", "t", "--ai-plan-verify",
                                   "--by", "test-agent")
        self.assertEqual(code, 0, f"a real value must freeze on the ai path: {out+err}")
        self.assertIn("Freeze mode: ai-plan-verify",
                      self._task_md("t").read_text(encoding="utf-8"))


# ── M3: real and explicit-none values freeze normally ────────────────────────
class RealValueFreezesTest(_Board):
    def test_real_value_freezes(self):
        self._make_at_contract("t", REAL_BOUNDARY)
        out, err, code = self._freeze("t")
        self.assertEqual(code, 0, f"a real Boundary value must freeze: {out+err}")
        self.assertIn("FROZEN @ v1", self._task_md("t").read_text(encoding="utf-8"))

    def test_explicit_none_freezes(self):
        self._make_at_contract("t", NONE_BOUNDARY)
        _, _, code = self._freeze("t")
        self.assertEqual(code, 0, "an explicit none declaration must freeze")


# ── M4: no Boundary line = grandfathered (full lane / legacy fast) ────────────
class GrandfatherTest(_Board):
    def test_absent_line_grandfathered(self):
        self._make_at_contract("t", None)
        out, err, code = self._freeze("t")
        self.assertEqual(code, 0, "a line-less task must freeze exactly as before")
        self.assertNotIn("boundary_unfilled", out + err)

    def test_boundary_mention_inside_section_3_fence_never_triggers(self):
        # the guard reads the §1 span only — a §3 code-fence line that happens
        # to start with `Boundary:` must not be mistaken for the declaration
        self._silent("new-task", "t", "--title", "t")
        self._write_task("t", None)
        md = self._task_md("t")
        md.write_text(md.read_text(encoding="utf-8").replace(
            "shape: f(x) -> ok · bad -> err",
            "shape: f(x) -> ok · bad -> err\nBoundary: <fence text, not a declaration>"),
            encoding="utf-8")
        self._silent("phase", "contract", "t")
        out, err, code = self._freeze("t")
        self.assertEqual(code, 0, f"§3 fence text must not trigger the guard: {out+err}")
        self.assertNotIn("boundary_unfilled", out + err)


if __name__ == "__main__":
    unittest.main()
