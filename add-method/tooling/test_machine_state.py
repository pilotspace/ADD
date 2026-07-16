#!/usr/bin/env python3
"""Behavioral proof of machine-readable engine state (task: machine-state-json, v4-1).

The CONTRACT (frozen @ v1): a `--json` flag on guide/status/check/ready, each printing
ONE compact JSON object to stdout (and nothing else); an `owner`/`stop` derived from the
phase via a single map; fail-closed (`no_state` / `unmapped_phase` -> stderr + exit 1 +
EMPTY stdout, never partial JSON); text mode unchanged; JSON built from State only (no
docs/ read). One test per SCENARIO. Run: python3 -m unittest test_machine_state -v
"""
import contextlib
import io
import json
import os
import pathlib
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _run(argv):
    """Run add.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class MachineStateTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-machine-state-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------
    def _freeze(self, slug: str):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _task_at(self, phase, slug="t"):
        """Create task `slug` and move it to `phase` (via explicit `phase` set)."""
        root = add.find_root()
        is_new = slug not in (add.load_state(root).get("tasks") or {})
        if is_new:
            add.main(["new-task", slug, "--title", "Feature"])
            self._freeze(slug)
        add.main(["phase", phase, slug])

    def _json_only(self, stdout):
        """Assert stdout is exactly ONE json object and return it."""
        self.assertTrue(stdout.strip(), "stdout was empty")
        obj = json.loads(stdout)             # raises if not valid / has trailing junk
        self.assertIsInstance(obj, dict)
        return obj

    def _set_updated(self, kind: str, slug: str, ts: str):
        """Directly stamp `updated` on a milestone/task record (kind: 'milestones'|'tasks')."""
        sp = Path(self.tmp) / ".add" / "state.json"
        state = json.loads(sp.read_text(encoding="utf-8"))
        state[kind][slug]["updated"] = ts
        sp.write_text(json.dumps(state), encoding="utf-8")

    # --- scenarios -----------------------------------------------------------
    def test_guide_json_active_task_carries_owner_stop(self):
        self._task_at("build")
        code, out, _ = _run(["guide", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertEqual(d["owner"], "ai")
        self.assertFalse(d["stop"])
        for k in ("task", "phase", "next_step", "chapter", "gate"):
            self.assertIn(k, d)
        self.assertEqual(d["task"], "t")
        self.assertEqual(d["phase"], "build")

    def test_owner_map_stops_at_human_and_seam(self):
        # phase-collapse-3: the whole front span collapsed into ONE `direction` phase —
        # it stays the seam owner.
        expect = {
            "direction": ("seam", True),
            "build": ("ai", False), "verify": ("human", True),
            "done": ("human", True),
        }
        for phase, (owner, stop) in expect.items():
            self._task_at(phase)
            code, out, _ = _run(["guide", "--json"])
            self.assertEqual(code, 0, f"guide --json failed at phase {phase}")
            d = self._json_only(out)
            self.assertEqual(d["owner"], owner, f"owner wrong at {phase}")
            self.assertEqual(d["stop"], stop, f"stop wrong at {phase}")

    def test_status_json_describes_project(self):
        add.main(["new-milestone", "m", "--goal", "g"])
        add.main(["new-task", "t", "--title", "Feature"])
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        for k in ("project", "stage", "active_task", "milestones", "tasks"):
            self.assertIn(k, d)
        self.assertTrue(all({"slug", "status", "done", "total"} <= set(m) for m in d["milestones"]))
        self.assertTrue(all({"slug", "phase", "gate", "milestone"} <= set(t) for t in d["tasks"]))

    def test_status_json_task_filter_returns_one_object(self):
        add.main(["new-milestone", "m", "--goal", "g"])
        add.main(["new-task", "t", "--title", "Feature"])
        code, out, _ = _run(["status", "--json", "--task", "t"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        # phase-bundles: additive "bundle" key (direction -> DIRECTION); every other key
        # unchanged. phase-collapse-3: new-task now seeds `direction` (was `specify`).
        self.assertEqual(d, {"slug": "t", "phase": "direction", "gate": "none",
                              "milestone": "m", "owner": None, "assignee": None,
                              "bundle": "DIRECTION"})

    def test_status_json_task_filter_unknown_slug_dies_unknown_task(self):
        code, out, err = _run(["status", "--json", "--task", "does-not-exist"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("unknown_task", err)

    def test_status_json_milestones_sorted_by_updated_desc(self):
        for slug in ("m-old", "m-mid", "m-new"):
            add.main(["new-milestone", slug, "--goal", "g"])
        self._set_updated("milestones", "m-old", "2026-01-01T00:00:00+00:00")
        self._set_updated("milestones", "m-mid", "2026-06-01T00:00:00+00:00")
        self._set_updated("milestones", "m-new", "2026-07-01T00:00:00+00:00")
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertEqual([m["slug"] for m in d["milestones"]], ["m-new", "m-mid", "m-old"])

    def test_status_json_tasks_sorted_by_updated_desc(self):
        for slug in ("t-old", "t-mid", "t-new"):
            add.main(["new-task", slug, "--title", "Feature"])
        self._set_updated("tasks", "t-old", "2026-01-01T00:00:00+00:00")
        self._set_updated("tasks", "t-mid", "2026-06-01T00:00:00+00:00")
        self._set_updated("tasks", "t-new", "2026-07-01T00:00:00+00:00")
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertEqual([t["slug"] for t in d["tasks"]], ["t-new", "t-mid", "t-old"])

    def test_status_json_caps_to_10_with_total_fields(self):
        for i in range(12):
            slug = f"t{i:02d}"
            add.main(["new-task", slug, "--title", "Feature"])
            self._set_updated("tasks", slug, f"2026-01-{i+1:02d}T00:00:00+00:00")
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertEqual(len(d["tasks"]), 10)
        self.assertEqual(d["tasks_total"], 12)
        self.assertEqual([t["slug"] for t in d["tasks"]],
                          ["t11", "t10", "t09", "t08", "t07", "t06", "t05", "t04", "t03", "t02"])

    def test_status_json_all_flag_returns_uncapped(self):
        for i in range(12):
            slug = f"t{i:02d}"
            add.main(["new-task", slug, "--title", "Feature"])
            self._set_updated("tasks", slug, f"2026-01-{i+1:02d}T00:00:00+00:00")
        code, out, _ = _run(["status", "--json", "--all"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertEqual(len(d["tasks"]), 12)
        self.assertEqual(d["tasks_total"], 12)
        self.assertEqual(d["tasks"][0]["slug"], "t11")
        self.assertEqual(d["tasks"][-1]["slug"], "t00")

    def test_status_text_mode_shows_truncation_note(self):
        for i in range(12):
            slug = f"t{i:02d}"
            add.main(["new-task", slug, "--title", "Feature"])
            self._set_updated("tasks", slug, f"2026-01-{i+1:02d}T00:00:00+00:00")
        # status-lean-default: the task ROWS (and thus the pagination "… N more" note)
        # now gate behind --all; bare status shows a `tasks : <N> (status --all)` count line.
        _, out, _ = _run(["status"])
        self.assertIn("tasks   : 12 (status --all)", out)

    def test_status_text_mode_all_flag_shows_everything(self):
        for i in range(12):
            slug = f"t{i:02d}"
            add.main(["new-task", slug, "--title", "Feature"])
            self._set_updated("tasks", slug, f"2026-01-{i+1:02d}T00:00:00+00:00")
        _, out, _ = _run(["status", "--all"])
        self.assertNotIn("more (see status --all)", out)
        for i in range(12):
            self.assertIn(f"t{i:02d}", out)

    def test_check_json_reports_result(self):
        code, out, _ = _run(["check", "--json"])
        d = self._json_only(out)
        self.assertIn("passed", d)
        self.assertIn("failed", d)
        self.assertTrue(all({"ok", "name", "reason"} <= set(c) for c in d["checks"]))
        self.assertEqual(code, 0 if d["failed"] == 0 else 1)

    def test_ready_json_lists_ready_and_blocked(self):
        add.main(["new-task", "a", "--title", "A"])
        add.main(["new-task", "b", "--title", "B", "--depends-on", "a"])
        code, out, _ = _run(["ready", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertIn("a", d["ready"])
        blocked = {x["slug"]: x["waiting_on"] for x in d["blocked"]}
        self.assertIn("b", blocked)
        self.assertIn("a", blocked["b"])

    def test_json_output_is_machine_clean(self):
        self._task_at("build")
        for argv in (["guide", "--json"], ["status", "--json"],
                     ["check", "--json"], ["ready", "--json"]):
            _, out, _ = _run(argv)
            self._json_only(out)   # parses whole stdout -> no human prose mixed in

    def test_text_mode_is_unchanged(self):
        self._task_at("build")
        _, g, _ = _run(["guide"])
        self.assertFalse(g.lstrip().startswith("{"), "text guide leaked JSON")
        self.assertIn("next   :", g)
        _, s, _ = _run(["status"])
        self.assertIn("project :", s)

    def test_minimal_pillar_holds_for_json(self):
        # the v2 Minimal pillar: no --json command may read a docs/ chapter.
        self._task_at("build")
        orig = pathlib.Path.read_text
        reads = []

        def spy(self, *a, **k):
            reads.append(str(self))
            return orig(self, *a, **k)

        pathlib.Path.read_text = spy
        try:
            for argv in (["guide", "--json"], ["status", "--json"],
                         ["check", "--json"], ["ready", "--json"]):
                _run(argv)
        finally:
            pathlib.Path.read_text = orig
        story = [p for p in reads if "docs" in Path(p).parts]
        self.assertEqual(story, [], f"a --json command read the Story: {story}")
        self.assertTrue(reads, "spy observed no reads")

    def test_guide_json_no_active_task_is_parseable(self):
        # fresh init -> no active task; guide --json must NOT crash.
        code, out, _ = _run(["guide", "--json"])
        self.assertEqual(code, 0)
        d = self._json_only(out)
        self.assertIsNone(d["task"])
        self.assertTrue(d["stop"])
        # contract conformance (amended @ v1.1): when there is no task, phase and gate
        # are null — not a fabricated string. A consumer typing them must allow null.
        self.assertIsNone(d["phase"])
        self.assertIsNone(d["gate"])
        self.assertEqual(d["owner"], "human")

    def test_status_json_fails_closed_on_bad_state(self):
        (Path(self.tmp) / ".add" / "state.json").write_text("{not valid json",
                                                            encoding="utf-8")
        code, out, err = _run(["status", "--json"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "", "stdout must be EMPTY on failure (no partial JSON)")
        self.assertIn("no_state", err)

    def test_guide_json_unmapped_phase_fails_closed(self):
        # corrupt the active task's phase to something outside the owner map.
        sp = Path(self.tmp) / ".add" / "state.json"
        add.main(["new-task", "t", "--title", "Feature"])
        state = json.loads(sp.read_text(encoding="utf-8"))
        state["tasks"]["t"]["phase"] = "bogus"
        state["active_task"] = "t"
        sp.write_text(json.dumps(state), encoding="utf-8")
        code, out, err = _run(["guide", "--json"])
        self.assertEqual(code, 1)
        self.assertEqual(out, "", "stdout must be EMPTY on failure")
        self.assertIn("unmapped_phase", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
