#!/usr/bin/env python3
"""Red/green tests for structured task/milestone Relations (relations-surface, plan-legibility).

Three relation types — `depends_on` (existing, BLOCKING) · `extends` · `relates_to` (both new,
NON-BLOCKING) — declared per task (new-task flags → state) and per milestone (MILESTONE.md
header lines). Surfaced at `status`; an ADVISORY guard (`_relations_health` + `cmd_check`) flags
a dangling / stale / self relation. Relations are DECLARED, never inferred. The wave schedule
stays a PURE depends_on DAG (extends/relates_to must not enter `_edges_fingerprint`).

Asserts behavior via state/stdout, never internals beyond the two documented readers. Run:
    python3 -m unittest test_relations -v
"""
import io
import os
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class RelationsTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-rel-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "m1", "--title", "M1", "--goal", "relate"])
        add.main(["milestone-confirm", "m1"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _run(self, *args):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(args))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _mk(self, slug, extends=None, relates=None, deps=None):
        argv = ["new-task", slug, "--title", slug, "--milestone", "m1"]
        if extends:
            argv += ["--extends", extends]
        if relates:
            argv += ["--relates-to", relates]
        if deps:
            argv += ["--depends-on", deps]
        add.main(argv)

    # ---- M1: task declares extends + relates_to ---------------------------
    def test_new_task_records_relations(self):
        self._mk("alpha")
        self._mk("gamma")
        self._mk("beta", extends="alpha", relates="gamma")
        t = self._state()["tasks"]["beta"]
        self.assertEqual(t["extends"], ["alpha"])
        self.assertEqual(t["relates_to"], ["gamma"])

    def test_relations_reader_migration_tolerant(self):
        """R3: a task created before this change (no keys) reads [] — never a KeyError."""
        self._mk("alpha")
        legacy = {"phase": "specify", "gate": "none", "milestone": "m1"}   # no relation keys
        rel = add._task_relations(legacy)
        self.assertEqual(rel, {"depends_on": [], "extends": [], "relates_to": []})
        # and a real task's reader agrees
        self._mk("beta", extends="alpha")
        self.assertEqual(add._task_relations(self._state()["tasks"]["beta"])["extends"], ["alpha"])

    # ---- M3: status surfaces relations ------------------------------------
    def test_status_shows_task_relations(self):
        self._mk("alpha")
        self._mk("beta", extends="alpha", relates="alpha")
        out, _, code = self._run("status", "--all")   # task rows gate behind --all
        self.assertEqual(code, 0)
        # beta's row names its extends/relates-to
        beta_line = next(l for l in out.splitlines() if l.strip().startswith(("*", " ")) and "beta" in l)
        self.assertIn("alpha", beta_line)
        self.assertTrue("ext" in beta_line or "extends" in beta_line)

    def test_status_silent_when_no_relations(self):
        self._mk("alpha")
        out, _, _ = self._run("status")
        alpha_line = next(l for l in out.splitlines() if "alpha" in l and "phase=" in l)
        self.assertNotIn("ext=", alpha_line)
        self.assertNotIn("rel=", alpha_line)

    # ---- M4 / R1 / R2: the advisory guard ---------------------------------
    def test_check_flags_dangling_extends(self):
        self._mk("beta", extends="ghost")   # ghost is not a task
        out, err, _ = self._run("check")
        blob = out + err
        self.assertIn("ghost", blob)
        self.assertIn("beta", blob)

    def test_check_flags_self_relation(self):
        self._mk("beta")
        st = self._state()
        st["tasks"]["beta"]["extends"] = ["beta"]         # a self-edge
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")
        findings = add._relations_health(self._root(), self._state())
        kinds = {f["kind"] for f in findings}
        self.assertIn("self_relation", kinds)

    def test_relations_health_dangling_finding(self):
        self._mk("beta", relates="ghost")
        findings = add._relations_health(self._root(), self._state())
        self.assertTrue(any(f["kind"] == "dangling" and f["target"] == "ghost"
                            and f["slug"] == "beta" for f in findings))

    def test_relations_health_archived_still_resolves(self):
        """M4: an archived (PASS-done) target is NOT dangling — mirrors depends_on."""
        self._mk("alpha")
        add.main(["phase", "verify", "alpha"])
        add.main(["gate", "PASS", "alpha"])
        self._mk("beta", extends="alpha")
        # archive alpha out of active tasks (the real archive path: an `archived` record whose
        # task_slugs list is read by _archived_task_slugs) — health must still resolve it.
        st = self._state()
        st["tasks"].pop("alpha")
        st.setdefault("archived", []).append({"milestone": "m0", "task_slugs": ["alpha"]})
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")
        findings = add._relations_health(self._root(), self._state())
        self.assertFalse(any(f["slug"] == "beta" and f["target"] == "alpha" for f in findings))

    def test_guard_writes_nothing(self):
        """R4/purity: the health guard is PURE — it validates, never invents/persists an edge."""
        self._mk("beta", extends="ghost")
        before = (self._root() / "state.json").read_bytes()
        add._relations_health(self._root(), self._state())
        self.assertEqual((self._root() / "state.json").read_bytes(), before)

    # ---- M2: milestone-altitude relations (MILESTONE.md header) -----------
    def test_milestone_relations_parse_header(self):
        md = self._root() / "milestones" / "m1" / "MILESTONE.md"
        txt = md.read_text(encoding="utf-8")
        txt = txt.replace("relations: ",
                          "extends: prior-ms\nrelates-to: other-ms\nrelations: ")
        md.write_text(txt, encoding="utf-8")
        rel = add._milestone_relations(self._root(), "m1")
        self.assertEqual(rel["extends"], ["prior-ms"])
        self.assertEqual(rel["relates_to"], ["other-ms"])

    def test_milestone_relations_migration_tolerant(self):
        """R3: an OLD MILESTONE.md with no relation lines reads empty — no crash."""
        rel = add._milestone_relations(self._root(), "m1")
        self.assertEqual(rel, {"depends_on": [], "extends": [], "relates_to": []})
        # a missing milestone is fail-safe too
        self.assertEqual(add._milestone_relations(self._root(), "no-such"),
                         {"depends_on": [], "extends": [], "relates_to": []})

    def test_milestone_header_deps_not_confused_with_task_rows(self):
        """The header parser reads only the pre-`##` region, never a per-task `depends-on:` row."""
        md = self._root() / "milestones" / "m1" / "MILESTONE.md"
        txt = md.read_text(encoding="utf-8")
        # a task-row style depends-on lives AFTER the first ## — must not be read as a ms relation
        txt += "\n## Tasks\n- [ ] sometask depends-on: otherts\n"
        md.write_text(txt, encoding="utf-8")
        rel = add._milestone_relations(self._root(), "m1")
        self.assertEqual(rel["depends_on"], [])


    # ---- M5: vocabulary + where-declared, on the shipped surface ---------
    def test_glossary_names_relation_vocab(self):
        tmpl = Path(add.__file__).resolve().parent / "templates" / "GLOSSARY.md.tmpl"
        txt = tmpl.read_text(encoding="utf-8")
        for term in ("depends-on:", "extends:", "relates-to:"):
            self.assertIn(term, txt)
        self.assertIn("non-blocking", txt.lower())

    def test_templates_name_where_relations_declared(self):
        tdir = Path(add.__file__).resolve().parent / "templates"
        task_t = (tdir / "TASK.md.tmpl").read_text(encoding="utf-8")
        ms_t = (tdir / "MILESTONE.md.tmpl").read_text(encoding="utf-8")
        self.assertIn("--extends", task_t)        # task relations declared via new-task flags
        self.assertIn("relations:", ms_t)         # milestone relations declared in the header


if __name__ == "__main__":
    unittest.main()
