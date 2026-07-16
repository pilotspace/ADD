#!/usr/bin/env python3
"""Red/green tests for the cross-component contract artifact (component-aware-add, task 3).

A contract is DECLARED `[contract.<id>]` (producer + consumers) in components.toml; a task
declares `produces: <id>` / `consumes: <id>`. At the contract->tests crossing the engine WRITES
an immutable `.add/contracts/<id>.json` snapshot (producer) or PINS its hash (consumer; a missing
snapshot HARD-STOPS). `cmd_check` reports `contract_consumer_stale` (producer re-froze a changed
shape) + `contract_producer_unknown`. No contract / no role -> byte-identical to today.

Run: cd add-method/tooling && python3 -m unittest test_cross_component_contract -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ccc-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
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

    def _registry(self, *, contract=True, bad_producer=False):
        body = (
            '[component.gateway]\nroot = "apps/gateway"\n'
            '[component.dashboard]\nroot = "apps/dashboard"\n'
        )
        if contract:
            prod = "ghost" if bad_producer else "gateway"
            body += f'[contract.gateway-api]\nproducer = "{prod}"\nconsumers = ["dashboard"]\n'
        (self.addp / "components.toml").write_text(body, encoding="utf-8")
        for c in ("gateway", "dashboard"):
            (self.tmp / "apps" / c).mkdir(parents=True, exist_ok=True)

    def _task_path(self, slug):
        return self.addp / "tasks" / slug / "TASK.md"

    def _new_at_contract(self, slug, role_line, *, frozen="v1", fence="ENDPOINT shape v1"):
        self._quiet(["new-task", slug])
        p = self._task_path(slug)
        t = p.read_text(encoding="utf-8")
        t = t.replace("phase: direction", f"{role_line}\nphase: direction", 1)
        if frozen:
            t = t.replace("Status: DRAFT",
                          f"Status: FROZEN @ {frozen} — approved by T\n"
                          "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none")
        # force a deterministic fenced §3 shape for hashing — anchor to the §3 PLAN heading so
        # the fence we set is the one the engine actually hashes (NOT the §2 gherkin fence, which
        # precedes §3 in the file; the §3 PLAN Grounding sub-block carries no fence, so the FIRST
        # fence inside §3 is still the Contract sub-block's shape).
        import re
        t = re.sub(r"(## 3 · PLAN.*?)```.*?```", rf"\1```\n{fence}\n```", t, count=1, flags=re.DOTALL)
        assert f"\n{fence}\n" in t, "fence did not land in §3"
        p.write_text(t, encoding="utf-8")
        # task stays at direction — the ONE crossing (direction -> build) is the caller's _advance

    def _freeze(self, slug: str) -> None:
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = self._task_path(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _advance(self, slug):
        out, errbuf = io.StringIO(), io.StringIO()
        err = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["advance", slug])
        except SystemExit:
            err = errbuf.getvalue()
        return out.getvalue(), err

    def _snapshot(self, cid="gateway-api"):
        return json.loads((self.addp / "contracts" / f"{cid}.json").read_text(encoding="utf-8"))

    def _state(self):
        return json.loads((self.addp / "state.json").read_text())

    def _phase(self, slug):
        return self._state()["tasks"][slug]["phase"]

    def _check(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            with contextlib.suppress(SystemExit):
                add.main(["check"])
        return out.getvalue()


class Readers(_Board):
    def test_contracts_parsed(self):
        self._registry()
        c = add._contracts(self.addp)
        self.assertEqual(c["gateway-api"]["producer"], "gateway")
        self.assertEqual(c["gateway-api"]["consumers"], ["dashboard"])

    def test_no_components_toml_empty(self):
        self.assertEqual(add._contracts(self.addp), {})

    def test_produces_consumes_readers(self):
        self._registry()
        self._quiet(["new-task", "p"])
        pp = self._task_path("p")
        pp.write_text(pp.read_text().replace("phase: direction", "produces: gateway-api\nphase: direction", 1), encoding="utf-8")
        self.assertEqual(add._task_produces(self.addp, "p"), "gateway-api")
        self.assertIsNone(add._task_consumes(self.addp, "p"))

    def test_body_hash_is_shape_only_not_version(self):
        # a pure version bump (same fenced shape) must yield the SAME hash
        v1 = "## 3\n```\nSHAPE A\n```\nStatus: FROZEN @ v1 — approved by T"
        v2 = "## 3\n```\nSHAPE A\n```\nStatus: FROZEN @ v2 — approved by T"
        changed = "## 3\n```\nSHAPE B\n```\nStatus: FROZEN @ v2 — approved by T"
        self.assertEqual(add._contract_body_hash(v1), add._contract_body_hash(v2))
        self.assertNotEqual(add._contract_body_hash(v1), add._contract_body_hash(changed))


class ProducerWrite(_Board):
    def test_producer_crossing_writes_snapshot(self):
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence="ENDPOINT shape ALPHA")
        out, err = self._advance("p")
        self.assertIsNone(err)
        snap = self._snapshot()
        self.assertEqual(snap["id"], "gateway-api")
        self.assertEqual(snap["producer"], "gateway")
        self.assertEqual(snap["task"], "p")
        self.assertEqual(snap["version"], "v1")
        # the stored hash is the SHAPE hash the engine computes — proving the §3 fence drove it
        self.assertEqual(snap["hash"], add._contract_body_hash("```\nENDPOINT shape ALPHA\n```"))

    def test_different_shapes_write_different_hashes(self):
        # the §3 fence genuinely flows into the snapshot hash (closes the inert-fixture gap)
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence="SHAPE A"); self._advance("p")
        h_a = self._snapshot()["hash"]
        self._quiet(["phase", "plan", "p"])
        pp = self._task_path("p")
        import re
        pp.write_text(re.sub(r"(## 3 · PLAN.*?)```.*?```", r"\1```\nSHAPE B\n```",
                             pp.read_text(), count=1, flags=re.DOTALL), encoding="utf-8")
        self._advance("p")
        self.assertNotEqual(h_a, self._snapshot()["hash"])

    def test_producer_write_is_idempotent(self):
        self._registry()
        self._new_at_contract("p", "produces: gateway-api")
        self._advance("p")
        first = (self.addp / "contracts" / "gateway-api.json").read_text()
        # re-cross by stepping the producer back to contract and forward again
        self._quiet(["phase", "plan", "p"])
        self._advance("p")
        self.assertEqual(first, (self.addp / "contracts" / "gateway-api.json").read_text())


class ConsumerPin(_Board):
    def _seed_snapshot(self, hash_="abc123", fence="ENDPOINT shape v1"):
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence=fence)
        self._advance("p")

    def test_consumer_pins_live_hash(self):
        self._seed_snapshot()
        live = self._snapshot()["hash"]
        self._new_at_contract("c", "consumes: gateway-api")
        out, err = self._advance("c")
        self.assertIsNone(err)
        self.assertEqual(self._state()["tasks"]["c"]["contract_pin"], {"id": "gateway-api", "hash": live})

    def test_consumer_without_snapshot_hard_stops(self):
        # designed-for-failure: with hold + pin at the SAME direction->build crossing, an absent
        # snapshot is caught by the consumer HOLD (producer_contract_unfrozen) before the pin runs
        # — a consumer can never cross into build without a live producer snapshot. (A snapshot
        # that exists but carries no hash is the PIN's own hard-stop — test_null_hash_… below.)
        self._seed_snapshot()
        self._new_at_contract("c", "consumes: gateway-api")     # enters §3 (snapshot present)
        (self.addp / "contracts" / "gateway-api.json").unlink()  # producer snapshot vanishes
        out, err = self._advance("c")
        self.assertIsNotNone(err)
        self.assertIn("producer_contract_unfrozen", err or "")
        self.assertEqual(self._phase("c"), "direction")
        self.assertNotIn("contract_pin", self._state()["tasks"]["c"])


class CheckFindings(_Board):
    def test_consumer_stale_when_producer_refroze_changed_shape(self):
        # END-TO-END: a real §3 shape change flows through the engine hash to flip the consumer
        # stale — driven entirely via advance/check, no manual snapshot mutation.
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence="SHAPE A")
        self._advance("p")
        self._new_at_contract("c", "consumes: gateway-api")
        self._advance("c")
        self.assertNotIn("contract_consumer_stale", self._check())   # fresh pin: not stale
        # producer re-freezes a CHANGED §3 shape and re-crosses -> new snapshot hash
        self._quiet(["phase", "plan", "p"])
        pp = self._task_path("p")
        import re
        pp.write_text(re.sub(r"(## 3 · PLAN.*?)```.*?```", r"\1```\nSHAPE B (breaking)\n```",
                             pp.read_text(), count=1, flags=re.DOTALL), encoding="utf-8")
        self._advance("p")
        self.assertIn("contract_consumer_stale", self._check())

    def test_null_hash_snapshot_hard_stops_consumer(self):
        # fail-loud (refute Finding 2): a valid-JSON snapshot lacking a hash must HARD-STOP, not
        # pin None and advance — "never build against a guessed shape".
        self._registry()
        (self.addp / "contracts").mkdir(parents=True, exist_ok=True)
        (self.addp / "contracts" / "gateway-api.json").write_text('{"id": "gateway-api"}', encoding="utf-8")
        self._new_at_contract("c", "consumes: gateway-api")
        out, err = self._advance("c")
        self.assertIsNotNone(err)
        self.assertIn("contract_snapshot_missing", err or "")
        self.assertEqual(self._phase("c"), "direction")

    def test_corrupt_live_snapshot_is_surfaced_not_masked(self):
        # refute Finding 3: a corrupt live snapshot must surface a finding, not silently no-stale.
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence="SHAPE A"); self._advance("p")
        self._new_at_contract("c", "consumes: gateway-api"); self._advance("c")
        (self.addp / "contracts" / "gateway-api.json").write_text("{ not json", encoding="utf-8")
        self.assertIn("contract_snapshot_unreadable", self._check())

    def test_no_stale_on_pure_version_bump(self):
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence="SHAPE A")
        self._advance("p")
        self._new_at_contract("c", "consumes: gateway-api")
        self._advance("c")
        # producer re-freezes v2 with the SAME shape -> same hash -> no churn
        self._quiet(["phase", "plan", "p"])
        pp = self._task_path("p")
        pp.write_text(pp.read_text().replace("FROZEN @ v1", "FROZEN @ v2"), encoding="utf-8")
        self._advance("p")
        self.assertNotIn("contract_consumer_stale", self._check())

    def test_unknown_producer_is_red_finding(self):
        self._registry(bad_producer=True)
        self.assertIn("contract_producer_unknown", self._check())


class OptIn(_Board):
    def test_zero_contract_no_role_byte_identical(self):
        # no components.toml at all; a plain task crosses direction->build as today (once frozen —
        # the universal freeze gate sits at this crossing regardless of the contract system,
        # unrelated to the cross-component behavior under test here)
        self._quiet(["new-task", "t"])
        self._freeze("t")
        out, err = self._advance("t")
        self.assertIsNone(err)
        self.assertEqual(self._phase("t"), "build")
        self.assertFalse((self.addp / "contracts").exists())


class GateConsumerStale(_Board):
    """F5 (consumer-stale-gate): cmd_gate must REFUSE a completing outcome when the consumer's
    pinned contract hash is stale (the producer re-froze a changed shape). Today the drift is only
    a cmd_check warning — a consumer can PASS against an out-of-date contract."""

    def _consumer_to_verify(self, slug="c"):
        # _new_at_contract stamps FROZEN + the least-sure flag, so the single
        # direction->build crossing (which pins) passes the whole floor stack
        self._new_at_contract(slug, "consumes: gateway-api")   # at direction (pins on next advance)
        for _ in range(2):                                     # direction->build (pin) -> verify
            self._advance(slug)

    def _refreeze_producer(self, fence):
        self._quiet(["phase", "plan", "p"])
        pp = self._task_path("p")
        import re
        pp.write_text(re.sub(r"(## 3 · PLAN.*?)```.*?```", rf"\1```\n{fence}\n```",
                             pp.read_text(), count=1, flags=re.DOTALL), encoding="utf-8")
        self._advance("p")

    def _gate(self, *argv):
        out, errbuf = io.StringIO(), io.StringIO()
        err = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["gate", *argv])
        except SystemExit:
            err = errbuf.getvalue()
        return out.getvalue(), err

    def _arrange(self):
        self._registry()
        self._new_at_contract("p", "produces: gateway-api", fence="SHAPE A")
        self._advance("p")
        self._consumer_to_verify("c")
        self.assertEqual(self._phase("c"), "verify", "consumer must reach verify before the gate")

    def test_gate_refuses_stale_consumer_pin(self):
        self._arrange()
        self._refreeze_producer("SHAPE B (breaking)")          # c's pin now stale
        out, err = self._gate("PASS", "c")
        self.assertIsNotNone(err, "a stale pin must refuse the completing gate")
        self.assertIn("contract_consumer_stale", err)
        self.assertNotEqual(self._phase("c"), "done", "a refused gate must not mark the task done")

    def test_risk_accepted_also_refused_on_stale_pin(self):
        self._arrange()
        self._refreeze_producer("SHAPE B (breaking)")
        out, err = self._gate("RISK-ACCEPTED", "c",
                              "--owner", "T", "--ticket", "T-1", "--expires", "2099-01-01")
        self.assertIsNotNone(err)
        self.assertIn("contract_consumer_stale", err)
        self.assertNotIn("waiver", self._state()["tasks"]["c"],
                         "a stale pin is refused BEFORE the waiver write — not launderable")

    def test_gate_passes_fresh_consumer_pin(self):
        self._arrange()                                        # producer unchanged -> pin fresh
        out, err = self._gate("PASS", "c")
        self.assertIsNone(err, f"a fresh pin must complete normally; got {err}")
        self.assertEqual(self._phase("c"), "done")

    def test_gate_passes_on_pure_version_bump(self):
        self._arrange()
        self._refreeze_producer("SHAPE A")                     # same shape, re-frozen -> same hash
        out, err = self._gate("PASS", "c")
        self.assertIsNone(err, f"a pure version bump is not stale; got {err}")
        self.assertEqual(self._phase("c"), "done")

    def test_plain_task_unaffected(self):
        # a task with no consumes: carries no contract_pin -> the guard returns early (byte-identical)
        self._quiet(["new-task", "t"])
        self._freeze("t")                                      # freeze-gate-universal sweep
        for _ in range(2):                                     # direction -> build -> verify
            self._quiet(["advance", "t"])
        self.assertEqual(self._phase("t"), "verify")
        out, err = self._gate("PASS", "t")
        self.assertIsNone(err, f"a no-pin task must complete as today; got {err}")
        self.assertEqual(self._phase("t"), "done")


if __name__ == "__main__":
    unittest.main()
