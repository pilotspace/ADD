#!/usr/bin/env python3
"""Red/green tests for the intra-milestone cross-component HOLD (component-aware-add, task 4).

A `consumes: <id>` task is HELD from advancing scenarios->contract while its producer's contract
snapshot (`.add/contracts/<id>.json`, written by task 3 on the producer's freeze) does not exist
— so a BE producer and an FE consumer ship in ONE milestone, the FE ordered downstream of the
frozen endpoint. Undeclared / no-role tasks cross byte-identically.

Run: cd add-method/tooling && python3 -m unittest test_cross_component_milestone -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ccm-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])
        self.addp = self.tmp / ".add"
        self._registry()

    def tearDown(self):
        os.chdir(self._cwd)

    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _registry(self):
        (self.addp / "components.toml").write_text(
            '[component.gateway]\nroot = "apps/gateway"\n'
            '[component.dashboard]\nroot = "apps/dashboard"\n'
            '[contract.gateway-api]\nproducer = "gateway"\nconsumers = ["dashboard"]\n',
            encoding="utf-8")
        for c in ("gateway", "dashboard"):
            (self.tmp / "apps" / c).mkdir(parents=True, exist_ok=True)

    def _task_path(self, slug):
        return self.addp / "tasks" / slug / "TASK.md"

    def _at_scenarios(self, slug, role_line=None):
        self._quiet(["new-task", slug])
        if role_line:
            p = self._task_path(slug)
            p.write_text(p.read_text().replace("phase: ground", f"{role_line}\nphase: ground", 1),
                         encoding="utf-8")
        for _ in range(2):    # ground -> specify -> scenarios
            self._quiet(["advance", slug])

    def _advance(self, slug):
        out, errbuf = io.StringIO(), io.StringIO()
        err = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["advance", slug])
        except SystemExit:
            err = errbuf.getvalue()
        return out.getvalue(), err

    def _phase(self, slug):
        return json.loads((self.addp / "state.json").read_text())["tasks"][slug]["phase"]

    def _write_snapshot(self, cid="gateway-api"):
        (self.addp / "contracts").mkdir(parents=True, exist_ok=True)
        (self.addp / "contracts" / f"{cid}.json").write_text(
            json.dumps({"id": cid, "producer": "gateway", "hash": "h1"}), encoding="utf-8")


class Hold(_Board):
    def test_consumer_held_until_producer_freezes(self):
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._advance("fe")
        self.assertIsNotNone(err)
        self.assertIn("producer_contract_unfrozen", err or "")
        self.assertEqual(self._phase("fe"), "scenarios")

    def test_consumer_proceeds_once_snapshot_exists(self):
        self._write_snapshot()
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._advance("fe")
        self.assertIsNone(err, f"should proceed once the producer froze, got {err!r}")
        self.assertEqual(self._phase("fe"), "contract")

    def test_full_stack_slice_one_milestone(self):
        # BE producer drives through its freeze (task 3 writes the snapshot), THEN FE proceeds.
        self._quiet(["new-task", "be"])
        bp = self._task_path("be")
        import re
        t = bp.read_text().replace("phase: ground", "produces: gateway-api\nphase: ground", 1)
        t = t.replace("Status: DRAFT", "Status: FROZEN @ v1 — approved by T")
        t = re.sub(r"(## 3 · CONTRACT.*?)```.*?```", r"\1```\nBE SHAPE\n```", t, count=1, flags=re.DOTALL)
        bp.write_text(t, encoding="utf-8")
        for _ in range(4):    # ground -> ... -> contract -> tests (writes snapshot)
            self._quiet(["advance", "be"])
        self.assertTrue((self.addp / "contracts" / "gateway-api.json").exists())
        # now the FE can enter §3
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._advance("fe")
        self.assertIsNone(err)
        self.assertEqual(self._phase("fe"), "contract")

    def test_undeclared_contract_does_not_hold(self):
        self._at_scenarios("fe", "consumes: nope")
        out, err = self._advance("fe")
        self.assertIsNone(err, "an undeclared contract id must not hold")
        self.assertEqual(self._phase("fe"), "contract")

    def test_no_role_byte_identical(self):
        self._at_scenarios("plain")
        out, err = self._advance("plain")
        self.assertIsNone(err)
        self.assertEqual(self._phase("plain"), "contract")


class Recency(_Board):
    """cross-component-recency: snapshot EXISTENCE is necessary but not sufficient. When a LIVE
    producer task backs the contract, its current FROZEN §3 body-hash must equal the landed
    snapshot — else a consumer entering §3 (via `advance` OR the `phase contract` override) HARD-
    STOPs `producer_contract_stale`. No live producer (archived / federation) -> existence-only."""

    import re as _re

    def _make_producer(self, slug="be", cid="gateway-api", shape="BE SHAPE v1"):
        """Create a producer task, freeze §3 with `shape`, drive it ground->tests so the
        contract->tests crossing writes a REAL snapshot (hash = body-hash of `shape`)."""
        self._quiet(["new-task", slug])
        bp = self._task_path(slug)
        t = bp.read_text()
        t = t.replace("phase: ground", f"produces: {cid}\nphase: ground", 1)
        t = t.replace("Status: DRAFT", "Status: FROZEN @ v1 — approved by T")
        t = self._re.sub(r"(## 3 · CONTRACT.*?)```.*?```", rf"\1```\n{shape}\n```",
                         t, count=1, flags=self._re.DOTALL)
        bp.write_text(t, encoding="utf-8")
        for _ in range(4):    # ground -> specify -> scenarios -> contract -> tests (writes snapshot)
            self._quiet(["advance", slug])
        return bp

    def _drift_producer(self, bp, shape="DRIFTED SHAPE v2"):
        """Edit the producer's live §3 fence WITHOUT re-crossing — its live body-hash now
        differs from the snapshot still on disk (simulates a re-opened/edited producer §3)."""
        t = bp.read_text()
        t = self._re.sub(r"(## 3 · CONTRACT.*?)```.*?```", rf"\1```\n{shape}\n```",
                         t, count=1, flags=self._re.DOTALL)
        bp.write_text(t, encoding="utf-8")

    def _phase_to(self, slug, phase):
        out, errbuf, err = io.StringIO(), io.StringIO(), None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["phase", phase, slug])
        except SystemExit:
            err = errbuf.getvalue()
        return out.getvalue(), err

    def _check(self):
        out, errbuf = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["check"])
        except SystemExit:
            pass
        return out.getvalue() + errbuf.getvalue()

    # ── advance path ──────────────────────────────────────────────────────────────────
    def test_stale_leftover_blocks_at_advance(self):
        bp = self._make_producer()
        self._drift_producer(bp)                       # live §3 hash now != snapshot hash
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._advance("fe")
        self.assertIsNotNone(err)
        self.assertIn("producer_contract_stale", err or "")
        self.assertEqual(self._phase("fe"), "scenarios")   # held; nothing pinned

    def test_current_snapshot_admits_at_advance(self):
        self._make_producer()                          # snapshot hash == live producer §3 hash
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._advance("fe")
        self.assertIsNone(err, f"a current snapshot must admit, got {err!r}")
        self.assertEqual(self._phase("fe"), "contract")

    def test_no_live_producer_is_existence_only(self):
        # a hand-rolled leftover snapshot with NO backing producer task -> existence-only (a
        # cross-milestone / federation consume of an earlier-frozen contract is not blocked).
        self._write_snapshot()                         # {id,producer,hash:"h1"} — no `task`, no producer
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._advance("fe")
        self.assertIsNone(err, f"no live producer must be existence-only, got {err!r}")
        self.assertEqual(self._phase("fe"), "contract")

    # ── phase-contract override (the closed bypass) ─────────────────────────────────────
    def test_phase_contract_runs_stale_hold(self):
        bp = self._make_producer()
        self._drift_producer(bp)
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._phase_to("fe", "contract")
        self.assertIsNotNone(err, "phase contract must not bypass the recency hold")
        self.assertIn("producer_contract_stale", err or "")
        self.assertEqual(self._phase("fe"), "scenarios")

    def test_phase_contract_enforces_absent_hold(self):
        # no snapshot at all -> the override still enforces the existence hold
        self._at_scenarios("fe", "consumes: gateway-api")
        out, err = self._phase_to("fe", "contract")
        self.assertIsNotNone(err)
        self.assertIn("producer_contract_unfrozen", err or "")
        self.assertEqual(self._phase("fe"), "scenarios")

    def test_phase_contract_no_role_byte_identical(self):
        self._at_scenarios("plain")
        out, err = self._phase_to("plain", "contract")
        self.assertIsNone(err, f"a no-role task must not hold at phase contract, got {err!r}")
        self.assertEqual(self._phase("plain"), "contract")

    # ── check WARN (measure-not-block) ──────────────────────────────────────────────────
    def test_check_warns_drifted_consumer_never_red(self):
        bp = self._make_producer()
        self._drift_producer(bp)
        self._at_scenarios("fe", "consumes: gateway-api")     # fe held at scenarios, snapshot stale
        out = self._check()
        self.assertIn("contract_producer_stale", out)
        code = 0
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                add.main(["check"])
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        self.assertEqual(code, 0, "a stale producer must not turn check red")

    def test_check_warns_hashless_snapshot_never_red(self):
        # R1 close: a landed snapshot with NO `hash` key degrades the recency check to existence-
        # only (frozen behavior) — surface it (measure-not-block) so the blind spot is visible.
        (self.addp / "contracts").mkdir(parents=True, exist_ok=True)
        (self.addp / "contracts" / "gateway-api.json").write_text(
            json.dumps({"id": "gateway-api", "producer": "gateway"}), encoding="utf-8")  # no hash
        self._at_scenarios("fe", "consumes: gateway-api")
        out = self._check()
        self.assertIn("contract_snapshot_hashless", out)
        code = 0
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                add.main(["check"])
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        self.assertEqual(code, 0, "a hash-less snapshot must not turn check red")


if __name__ == "__main__":
    unittest.main()
