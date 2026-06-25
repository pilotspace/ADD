#!/usr/bin/env python3
"""Red/green tests for per-component verify (milestone component-aware-add, task 2).

A component-BOUND task (a `component: <name>` header binding a registered component
with a non-empty green_bar) is held to that bar at the gate — SURFACE + SOFT-GATE,
the engine still never executing a suite:
  - a completing gate (PASS/RISK-ACCEPTED) is refused `component_green_bar_uncited`
    unless the §6 body cites the component's green_bar phrase;
  - the expected-bar line is stamped into the §6 GATE RECORD;
  - a bound component with NO green_bar is a no-op (+ a `check` WARN);
  - HARD-STOP is never blocked; an UNBOUND task / no-registry gate is byte-identical.

Run: cd add-method/tooling && python3 -m unittest test_per_component_verify -v
"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

import add

try:
    import tomllib  # the component pillar requires tomllib (stdlib, Python 3.11+)
    _HAS_TOMLLIB = True
except ModuleNotFoundError:
    _HAS_TOMLLIB = False


def setUpModule():
    # Python < 3.11 has no tomllib, so components.toml cannot be parsed and the component
    # pillar is unavailable (the engine fails loud with components_malformed). The feature's
    # behavior can only be exercised where it exists; 3.12+ runs the full suite.
    if not _HAS_TOMLLIB:
        raise unittest.SkipTest("component pillar requires tomllib (Python 3.11+)")


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-pcv-")).resolve()
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])
        self.addp = self.tmp / ".add"

    def tearDown(self):
        os.chdir(self._cwd)

    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _registry(self, *, green_bar='"vitest + a11y"', name="dashboard"):
        body = f'[component.{name}]\nroot = "apps/{name}"\n'
        if green_bar:
            body += f"green_bar = {green_bar}\n"
        (self.addp / "components.toml").write_text(body, encoding="utf-8")
        (self.tmp / "apps" / name).mkdir(parents=True, exist_ok=True)

    def _task_path(self, slug):
        return self.addp / "tasks" / slug / "TASK.md"

    def _bind(self, slug, name="dashboard"):
        p = self._task_path(slug)
        t = p.read_text(encoding="utf-8")
        t = t.replace("phase: ground", f"component: {name}\nphase: ground", 1)
        p.write_text(t, encoding="utf-8")

    def _cite_in_six(self, slug, phrase):
        """Put `phrase` into the §6 body (replace the first build-expectations placeholder)."""
        p = self._task_path(slug)
        t = p.read_text(encoding="utf-8")
        t = t.replace("- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>",
                      f"- [x] met the bar {phrase} — confirmed by the green suite", 1)
        p.write_text(t, encoding="utf-8")

    def _to_verify(self, slug):
        for _ in range(6):    # ground->specify->scenarios->contract->tests->build->verify
            self._quiet(["advance", slug])

    def _gate(self, slug, outcome):
        """Run `gate <outcome>`; return (stdout, stderr-on-refusal-or-None). A refusal is a
        `_die` -> SystemExit(1) with the reason on STDERR (not the exit code)."""
        out, errbuf = io.StringIO(), io.StringIO()
        err = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["gate", outcome, slug])
        except SystemExit:
            err = errbuf.getvalue()        # the `add: error: <code> …` message lives here
        return out.getvalue(), err

    def _phase(self, slug):
        return json.loads((self.addp / "state.json").read_text())["tasks"][slug]["phase"]


class TaskGreenBar(_Board):
    def test_bound_returns_bar(self):
        self._registry()
        self._quiet(["new-task", "t"])
        self._bind("t")
        self.assertEqual(add._task_green_bar(self.addp, "t"), "vitest + a11y")

    def test_unbound_returns_none(self):
        self._registry()
        self._quiet(["new-task", "t"])           # no component: line
        self.assertIsNone(add._task_green_bar(self.addp, "t"))

    def test_bound_but_no_green_bar_returns_none(self):
        self._registry(green_bar="")
        self._quiet(["new-task", "t"])
        self._bind("t")
        self.assertIsNone(add._task_green_bar(self.addp, "t"))


class CiteGate(_Board):
    def test_uncited_completing_gate_refused(self):
        self._registry()
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._to_verify("t")
        out, err = self._gate("t", "PASS")
        self.assertIsNotNone(err)
        self.assertIn("component_green_bar_uncited", err or "")
        self.assertEqual(self._phase("t"), "verify", "a refused gate must not mark the task done")

    def test_cited_gate_passes_and_stamps(self):
        self._registry()
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._cite_in_six("t", "vitest + a11y")
        self._to_verify("t")
        out, err = self._gate("t", "PASS")
        self.assertIsNone(err, f"cited gate should pass, got {err!r}")
        self.assertEqual(self._phase("t"), "done")
        self.assertIn("vitest + a11y", out, "the expected bar is surfaced at the gate")
        six = self._task_path("t").read_text(encoding="utf-8")
        self.assertIn("expected green-bar: vitest + a11y", six,
                      "the expected-bar line is stamped into §6")

    def test_no_green_bar_does_not_block(self):
        self._registry(green_bar="")
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._to_verify("t")
        out, err = self._gate("t", "PASS")
        self.assertIsNone(err, "a bound component with no green_bar must not block")
        self.assertEqual(self._phase("t"), "done")

    def test_hard_stop_never_blocked(self):
        self._registry()
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._to_verify("t")
        out, err = self._gate("t", "HARD-STOP")
        self.assertIsNone(err, "HARD-STOP must never be blocked by the soft gate")

    def test_hard_stop_then_pass_still_refused(self):
        # refute-read BLOCKER: HARD-STOP stamps "expected green-bar: <bar>" into §6; a later
        # PASS must NOT be satisfied by the engine's OWN stamp — only user evidence counts.
        self._registry()
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._to_verify("t")
        self._gate("t", "HARD-STOP")             # stamps the bar phrase into §6
        out, err = self._gate("t", "PASS")       # must STILL be refused
        self.assertIsNotNone(err, "the engine's own stamp must not satisfy the cite-gate")
        self.assertIn("component_green_bar_uncited", err or "")
        self.assertEqual(self._phase("t"), "verify")

    def test_generic_bar_colliding_with_boilerplate_does_not_self_pass(self):
        # refute-read Finding 2 (v2): a green_bar that is a substring of §6 BOILERPLATE — the
        # fixed checklist "all tests pass", or the "Outcome: <PASS|…>" placeholder — must NOT
        # self-satisfy the cite-gate. The search is scoped to the Build-expectations block.
        self._registry(green_bar='"all tests pass"')
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._to_verify("t")
        out, err = self._gate("t", "PASS")
        self.assertIsNotNone(err, "a boilerplate-colliding bar must not silently pass the gate")
        self.assertIn("component_green_bar_uncited", err or "")
        self.assertEqual(self._phase("t"), "verify")

    def test_generic_bar_passes_when_cited_in_evidence(self):
        # the same generic bar PASSES once the user cites it in the Build-expectations evidence block.
        self._registry(green_bar='"all tests pass"')
        self._quiet(["new-task", "t"])
        self._bind("t")
        self._cite_in_six("t", "all tests pass")
        self._to_verify("t")
        out, err = self._gate("t", "PASS")
        self.assertIsNone(err, f"a cited generic bar should pass, got {err!r}")
        self.assertEqual(self._phase("t"), "done")

    def test_unbound_gate_byte_identical(self):
        # no components.toml at all -> the gate path is exactly today's
        self._quiet(["new-task", "t"])
        self._to_verify("t")
        out, err = self._gate("t", "PASS")
        self.assertIsNone(err)
        self.assertEqual(self._phase("t"), "done")
        self.assertNotIn("expected green-bar", out)


class CiteRegion(unittest.TestCase):
    """Pure unit tests for `_cite_region` (v3) — the user-authored Build-expectations evidence
    region, stamp-stripped, across BOTH template shapes + the self-satisfy edge."""

    STD = (
        "## 6 · VERIFY\n"
        "- [x] all tests pass — full engine suite green\n"   # top checklist boilerplate (EXCLUDED)
        "### Build expectations\n"
        "- [x] met the bar vitest + a11y — confirmed by the green suite\n"   # user evidence (INCLUDED)
        "### Deep checks\n"
        "- [x] WIRING ok\n"
        "### GATE RECORD\n"
        "Outcome: PASS\n"
        "component: dashboard · expected green-bar: vitest + a11y\n"          # engine stamp (EXCLUDED)
        "Reviewed by: x · date: y\n"
    )
    FAST = (
        "## 6 · VERIFY — evidence + gate\n"
        "Build expectations (from §1 Accept + §3 CONTRACT): met the bar vitest + a11y — confirmed by the suite\n"
        "### GATE RECORD\n"
        "Outcome: PASS\n"
        "component: dashboard · expected green-bar: vitest + a11y\n"
        "Reviewed by: x · date: y\n"
    )

    def test_standard_region_is_user_evidence_only(self):
        region = add._cite_region(self.STD)
        self.assertIn("met the bar vitest + a11y", region)          # user evidence kept
        self.assertNotIn("- [x] all tests pass", region)            # top checklist excluded
        self.assertNotIn("expected green-bar", region)              # engine stamp stripped

    def test_fast_lane_bare_marker_region(self):
        region = add._cite_region(self.FAST)
        self.assertIn("met the bar vitest + a11y", region)          # the bare-line evidence is captured
        self.assertNotIn("expected green-bar", region)              # stamp (in GATE RECORD) stripped

    def test_stamp_inside_expectations_is_stripped(self):
        # Finding 1: an Outcome:<…> authored inside the block let the stamp land inside the region.
        poisoned = self.STD.replace(
            "### Build expectations\n",
            "### Build expectations\nOutcome: PASS\ncomponent: dashboard · expected green-bar: vitest + a11y\n")
        region = add._cite_region(poisoned)
        self.assertNotIn("expected green-bar", region,
                         "a stamp that landed inside the block must still be stripped")

    def test_no_marker_yields_empty_region(self):
        self.assertEqual(add._cite_region("## 6\n### GATE RECORD\nOutcome: PASS\n"), "")


class CheckWarn(_Board):
    def test_bound_no_green_bar_warns(self):
        self._registry(green_bar="")
        self._quiet(["new-task", "t"])
        self._bind("t")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            with contextlib.suppress(SystemExit):
                add.main(["check"])
        self.assertIn("component_green_bar_unset", out.getvalue())


if __name__ == "__main__":
    unittest.main()
