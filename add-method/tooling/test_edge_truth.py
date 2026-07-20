#!/usr/bin/env python3
"""edge-truth red suite (task-graph-native W1).

The milestone is the scope ROOT of the task DAG; depth lives in edges, not
nesting. Measured gap: every bench board ends with deps=[] — the graph the
engine schedules (waves) and repairs from is EMPTY in practice. W1 makes it
real, deterministically, propose-not-block:

  compile  — `milestone-confirm` reads MILESTONE.md's `## Tasks` list
             (`- [ ] <slug>   depends-on: <deps>   — <line>`) into
             state.milestones[m].planned = {slug: [dep, ...]} — the figure's
             "Compilation of T0". Re-confirm RECOMPILES (the plan is living);
             placeholder/malformed lines are skipped silently.
  inherit  — `new-task <slug>` with no explicit --depends-on inherits the
             planned deps verbatim (creation order never loses an edge; a
             dangling forward edge is check's existing warn, never a block).
             An explicit --depends-on always wins.
  hint     — `freeze` prints `edge-hint:` when this task's declared §3 scope
             overlaps a DONE task's declared scope and no edge exists —
             print-only, capped, never a refusal.

Run: cd add-method/tooling && python3 -m unittest test_edge_truth -v
"""
import json
import unittest

import add
from test_freeze_command import _Harness, _DRAFT_FLAGGED

def _fill_confirm_floor(text: str, tasks_section: str) -> str:
    """Replace the scaffolded `## Shared / risky contracts` body with a real bullet
    (any bare `<...>` keeps the section unfilled for the confirm gate) and swap in
    the Tasks section under test."""
    def _swap(heading: str, body: str, t: str) -> str:
        start = t.index(heading)
        end = t.find("\n## ", start + 1)
        return t[:start] + body + (t[end:] if end != -1 else "")
    text = _swap("## Shared / risky contracts",
                 "## Shared / risky contracts\n- POST /bookings shape is shared\n", text)
    return _swap("## Tasks", tasks_section, text)


TASKS_SECTION = """## Tasks (breadth-first decomposition; detail lives in each PLAN.md)
- [ ] api-core   depends-on: none     — the base CRUD surface
- [ ] auth-rules   depends-on: api-core   — ownership + auth on top
- [ ] search   depends-on: api-core, auth-rules   — filtered listing
"""


class _EdgeHarness(_Harness):
    def _mk_confirm_milestone(self, tasks_section=TASKS_SECTION):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp",
                     "--await-confirm")
        mfile = self.tmp / ".add" / "milestones" / "m" / "MILESTONE.md"
        text = mfile.read_text(encoding="utf-8")
        text = _fill_confirm_floor(text, tasks_section)
        mfile.write_text(text, encoding="utf-8")
        self._silent("milestone-confirm", "m", "--by", "Ada")

    def _planned(self):
        return (self._state()["milestones"]["m"] or {}).get("planned")


class CompileTest(_EdgeHarness):
    def test_confirm_compiles_task_graph(self):
        self._mk_confirm_milestone()
        self.assertEqual(self._planned(), {
            "api-core": [],
            "auth-rules": ["api-core"],
            "search": ["api-core", "auth-rules"],
        })

    def test_placeholder_lines_skipped(self):
        self._mk_confirm_milestone(
            "## Tasks (breadth-first decomposition; detail lives in each PLAN.md)\n"
            "- [ ] <slug>   depends-on: none     — <one line>\n"
            "- [ ] real-task   depends-on: none   — a real one\n")
        self.assertEqual(self._planned(), {"real-task": []})

    def test_reconfirm_recompiles_the_living_plan(self):
        self._mk_confirm_milestone()
        mfile = self.tmp / ".add" / "milestones" / "m" / "MILESTONE.md"
        mfile.write_text(mfile.read_text(encoding="utf-8").replace(
            "- [ ] search   depends-on: api-core, auth-rules   — filtered listing",
            "- [ ] search   depends-on: auth-rules   — filtered listing"), encoding="utf-8")
        self._silent("milestone-confirm", "m", "--by", "Ada")   # idempotent note + recompile
        self.assertEqual(self._planned()["search"], ["auth-rules"])

    def test_confirm_prints_graph_summary(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp", "--await-confirm")
        mfile = self.tmp / ".add" / "milestones" / "m" / "MILESTONE.md"
        mfile.write_text(_fill_confirm_floor(mfile.read_text(encoding="utf-8"),
                                             TASKS_SECTION), encoding="utf-8")
        out = self._silent("milestone-confirm", "m", "--by", "Ada")
        self.assertIn("3 nodes", out)
        self.assertIn("3 edges", out)


class InheritTest(_EdgeHarness):
    def test_new_task_inherits_planned_deps(self):
        self._mk_confirm_milestone()
        self._silent("new-task", "api-core", "--title", "API")
        self._silent("new-task", "auth-rules", "--title", "Auth")
        self.assertEqual(self._state()["tasks"]["auth-rules"]["depends_on"], ["api-core"])

    def test_forward_edge_survives_creation_order(self):
        self._mk_confirm_milestone()
        self._silent("new-task", "search", "--title", "Search")   # parents not created yet
        self.assertEqual(self._state()["tasks"]["search"]["depends_on"],
                         ["api-core", "auth-rules"],
                         "the plan's truth is inherited verbatim; a dangling forward "
                         "edge is check's warn, never a lost edge")

    def test_explicit_depends_on_wins(self):
        self._mk_confirm_milestone()
        self._silent("new-task", "api-core", "--title", "API")
        self._silent("new-task", "auth-rules", "--title", "Auth", "--depends-on", "api-core")
        self.assertEqual(self._state()["tasks"]["auth-rules"]["depends_on"], ["api-core"])
        self._silent("new-task", "search", "--title", "S", "--depends-on", "api-core")
        self.assertEqual(self._state()["tasks"]["search"]["depends_on"], ["api-core"],
                         "an explicit edge declaration always beats the compiled plan")

    def test_unplanned_slug_inherits_nothing(self):
        self._mk_confirm_milestone()
        self._silent("new-task", "hotfix", "--title", "Hotfix")
        self.assertEqual(self._state()["tasks"]["hotfix"]["depends_on"], [])


class EdgeHintTest(_EdgeHarness):
    def _mk_done_with_scope(self, slug, scope_line="`src/`"):
        self._silent("new-task", slug, "--title", slug)
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        text = text.replace("Scope (may touch): `./src/`", f"Scope (may touch): {scope_line}", 1)
        p.write_text(text, encoding="utf-8")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text())
        st["tasks"][slug]["phase"] = "done"
        st["tasks"][slug]["gate"] = "PASS"
        sp.write_text(json.dumps(st, indent=2))

    def _draft_with_scope(self, slug, scope_line="`src/`"):
        self._silent("new-task", slug, "--title", slug)
        self._silent("phase", "plan", slug)
        self._set_section3(slug, _DRAFT_FLAGGED
                           + f"\nScope (may touch): {scope_line}\n")

    def test_scope_overlap_prints_hint(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._mk_done_with_scope("api-core", "`src/`")
        self._draft_with_scope("auth-rules", "`src/`")
        out = self._silent("freeze", "auth-rules", "--by", "Ada", "--cross")
        self.assertIn("edge-hint", out)
        self.assertIn("api-core", out)

    def test_no_overlap_no_hint(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._mk_done_with_scope("api-core", "`src/`")
        self._draft_with_scope("docs-task", "`docs/`")
        out = self._silent("freeze", "docs-task", "--by", "Ada", "--cross")
        self.assertNotIn("edge-hint", out)

    def test_declared_edge_silences_hint(self):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._mk_done_with_scope("api-core", "`src/`")
        self._silent("new-task", "auth-rules", "--title", "Auth", "--depends-on", "api-core")
        self._silent("phase", "plan", "auth-rules")
        self._set_section3("auth-rules", _DRAFT_FLAGGED
                           + "\nScope (may touch): `src/`\n")
        out = self._silent("freeze", "auth-rules", "--by", "Ada", "--cross")
        self.assertNotIn("edge-hint", out, "a declared edge needs no hint")

    def test_hint_never_blocks(self):
        # the hint path must not turn a clean freeze into a refusal
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._mk_done_with_scope("api-core", "`src/`")
        self._draft_with_scope("auth-rules", "`src/`")
        out, code = self._run("freeze", "auth-rules", "--by", "Ada", "--cross")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
