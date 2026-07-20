#!/usr/bin/env python3
"""Red/green tests for SURFACING owner/assignee (ownership-assignment 2/2):
the recorded owner/assignee (ownership-model's assign) made visible in `report`
(per-task + milestone), `status` (active task), and `status --json` (per-task).
Read-only; an unassigned record renders no owner/assignee. Run:
  python3 -m unittest test_ownership_surface -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ownsurface-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", "t", "--title", "Feature")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _own(self, slug, owner=None, assignee=None):
        """kernel-trim (ADD 2.0 M5): the `assign` setter died; the owner/assignee READ
        surface survives — write the actor dicts directly (the shape _parse_actor_arg made)."""
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text())
        rec = st["tasks"].get(slug) or st["milestones"][slug]
        if owner:
            rec["owner"] = owner
        if assignee:
            rec["assignee"] = assignee
        sp.write_text(json.dumps(st, indent=2))

    def _report_data(self):
        root = add.find_root()
        return add.report_data(root, add.load_state(root), "m")


class ReportSurfaceTest(_Harness):
    def test_report_surfaces_task_owner_assignee(self):
        self._own("t", owner={"name": "Bob", "email": "bob@y.io", "source": "assigned"}, assignee={"name": "Cy", "email": None, "source": "assigned"})
        d = self._report_data()
        row = next(r for r in d["tasks"] if r["slug"] == "t")
        self.assertEqual(row["owner"]["name"], "Bob")
        self.assertEqual(row["assignee"]["name"], "Cy")
        out = self._silent("report", "m")
        self.assertIn("OWNED BY", out)
        self.assertIn("Bob", out)
        self.assertIn("Cy", out)

    def test_report_surfaces_milestone_owner(self):
        self._own("m", owner={"name": "Bob", "email": "bob@y.io", "source": "assigned"})
        d = self._report_data()
        self.assertEqual(d["milestone"]["owner"]["name"], "Bob")
        out = self._silent("report", "m")
        self.assertIn("owned by", out)
        self.assertIn("Bob", out)

    def test_report_omits_unassigned(self):
        out = self._silent("report", "m")
        self.assertNotIn("OWNED BY", out)
        self.assertNotIn("owned by", out)
        self.assertIn("VERDICT", out)   # an existing line is still present


class StatusSurfaceTest(_Harness):
    def test_status_shows_active_owned_line(self):
        self._own("t", owner={"name": "Bob", "email": "bob@y.io", "source": "assigned"}, assignee={"name": "Cy", "email": None, "source": "assigned"})
        out = self._silent("status")
        owned = [l for l in out.splitlines() if l.startswith("owned   :")]
        self.assertEqual(len(owned), 1, "one owned line for the active assigned task")
        self.assertIn("Bob", owned[0])
        self.assertIn("Cy", owned[0])

    def test_status_omits_owned_when_unassigned(self):
        out = self._silent("status")
        self.assertEqual([l for l in out.splitlines() if l.startswith("owned   :")], [])

    def test_status_json_per_task_ownership(self):
        self._own("t", owner={"name": "Bob", "email": "bob@y.io", "source": "assigned"})
        out = self._silent("status", "--json")
        obj = json.loads(out)
        entry = next(e for e in obj["tasks"] if e["slug"] == "t")
        self.assertEqual(entry["owner"]["name"], "Bob")
        self.assertIsNone(entry["assignee"])
        for base in ("project", "stage", "actor", "milestones", "tasks"):
            self.assertIn(base, obj)   # top-level surface intact


if __name__ == "__main__":
    unittest.main(verbosity=2)
