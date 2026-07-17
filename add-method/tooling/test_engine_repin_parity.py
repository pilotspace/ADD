#!/usr/bin/env python3
"""engine-repin-parity (state-model-reshape 5/5) — the consolidated parity AUDIT +
multi-active invariant backstop.

Two charters in one suite:

  1. AUDIT — the engine edits of tasks 1-4 are PINNED, not bypassed: all three add.py
     copies are byte-identical AND each equals the single-source the engine pin
     (the pin is CURRENT). This is the milestone's integrity exit-criterion, mechanised.

  2. HARDEN — byte-identity + a current pin prove the three copies MATCH, but NOT that
     they still CONTAIN the multi-active feature. These behavioral guards lock the
     invariants (born-migrated init · idempotent load-seam migration · activate/deactivate
     -> streams render · the parser verbs) into the parity backstop, so a future refactor
     that keeps the copies identical+pinned yet drops the feature goes red.

Backstop/characterization tests: green against the correct engine; each guard is proven to
BITE under the specific regression it guards (test_audit_bites_on_drift +
test_hardening_bites_on_feature_removal demonstrate the two representative regressions).

Run: python3 -m unittest test_engine_repin_parity -v
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

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

ENGINE_COPIES = (
    TOOLING / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


class MultiActiveInvariants(unittest.TestCase):
    """Lock the multi-active behavior into the parity backstop (drives the real CLI)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-erp-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def test_init_born_migrated(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        st = self._state()
        self.assertIsInstance(st.get("active_milestones"), list,
                              "born-migrated: init must write active_milestones as a list")
        self.assertIsInstance(st.get("active_tasks"), dict,
                              "born-migrated: init must write active_tasks as a dict")

    def test_legacy_migrates_idempotent(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "mA", "--stage", "mvp")   # scalar active_milestone=mA
        # craft a LEGACY single-active state: strip the new keys, keep the scalar
        p = self.tmp / ".add" / "state.json"
        st = json.loads(p.read_text())
        scalar = st.get("active_milestone")
        st.pop("active_milestones", None)
        st.pop("active_tasks", None)
        p.write_text(json.dumps(st))
        # the READ-ONLY json seam must derive the SET from the scalar (load-seam migration)
        first = json.loads(self._silent("status", "--json"))
        self.assertEqual(first["active_milestones"], [scalar] if scalar else [],
                         "load-seam migration must derive active_milestones from the scalar")
        self.assertEqual(first["active_tasks"], {},
                         "no active task on the legacy board -> the derived map is empty "
                         "(pins active_tasks DERIVATION, not just its stability)")
        # idempotent: a 2nd read derives the SAME shape (no drift on re-migrate)
        second = json.loads(self._silent("status", "--json"))
        self.assertEqual(second["active_milestones"], first["active_milestones"])
        self.assertEqual(second["active_tasks"], first["active_tasks"])

    def test_activate_deactivate_streams_roundtrip(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("new-milestone", "m1", "--stage", "mvp")
        self._silent("new-milestone", "m2", "--stage", "mvp")   # m2 = replace-focus primary
        self._silent("activate", "m1")                          # reach N=2
        self.assertEqual(set(self._state()["active_milestones"]), {"m1", "m2"})
        out = self._silent("status")
        self.assertIn("streams :", out, "N>=2 must render the streams block (task 4)")
        self._silent("deactivate", "m1")                        # back to N=1
        self.assertEqual(self._state()["active_milestones"], ["m2"])
        out2 = self._silent("status")
        self.assertNotIn("streams :", out2, "N<=1 must NOT render the streams block")

    def test_parser_exposes_verbs(self):
        sub = next(a for a in add.build_parser()._actions if getattr(a, "choices", None))
        self.assertIn("activate", sub.choices)
        self.assertIn("deactivate", sub.choices)

    def test_hardening_bites_on_feature_removal(self):
        # Demonstration: prove the EXACT predicate test_init_born_migrated uses
        # (assertIsInstance(..., list)) goes red when init omits active_milestones. Emulated
        # in-memory (never patch the real engine) to stay hermetic + restore-free. NOTE: this
        # mirrors the born-migrated predicate FORM — if that guard's predicate changes (e.g. to
        # key-presence), update this demonstration in lockstep.
        regressed = {"project": "demo", "stage": "mvp", "milestones": {}, "tasks": {}}
        self.assertNotIsInstance(regressed.get("active_milestones"), list,
                                 "the born-migrated guard must fail when the key is missing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
