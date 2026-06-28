#!/usr/bin/env python3
"""Red/green tests for multi-repo federation (component-aware-add, task 5).

A consumer repo PULLS a producer repo's published, immutable contract snapshot by id:
`add.py federate pull <id>` reads the manifest `[federation.<id>].source`, validates it, and
atomically lands a byte-copy at the local `.add/contracts/<id>.json` — so the rest of ADD treats
mono + multi-repo identically. Designed-for-failure: unknown / missing / invalid / version-
mismatched sources HARD-STOP and land nothing.

Run: cd add-method/tooling && python3 -m unittest test_multirepo_federation -v
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
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fed-")).resolve()
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "consumer"])
        self.addp = self.tmp / ".add"
        # the producer repo's published snapshot lives OUTSIDE this repo (a sibling checkout)
        self.producer = (self.tmp / ".." / "producer").resolve()
        (self.producer / ".add" / "contracts").mkdir(parents=True, exist_ok=True)
        self.src = self.producer / ".add" / "contracts" / "gateway-api.json"
        self.src.write_text(json.dumps(
            {"id": "gateway-api", "producer": "gateway", "version": "v1", "hash": "h1"}),
            encoding="utf-8")

    def tearDown(self):
        os.chdir(self._cwd)
        import shutil
        shutil.rmtree(self.producer, ignore_errors=True)

    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _manifest(self, body):
        (self.addp / "components.toml").write_text(body, encoding="utf-8")

    def _federate(self, *argv):
        out, errbuf, err = io.StringIO(), io.StringIO(), None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["federate", *argv])
        except SystemExit:
            err = errbuf.getvalue()
        return out.getvalue(), err

    def _landed(self):
        return self.addp / "contracts" / "gateway-api.json"


class Pull(_Board):
    def test_pull_lands_producer_snapshot(self):
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIsNone(err, f"pull should succeed, got {err!r}")
        self.assertTrue(self._landed().exists())
        self.assertEqual(self._landed().read_bytes(), self.src.read_bytes())
        self.assertIn("v1", out)
        self.assertIn("h1", out)

    def test_pull_is_an_exact_byte_copy(self):
        # the contract promises the local snapshot BYTE-equals the producer's — so a source with
        # CRLF line endings (a Windows-written artifact) must land unchanged, NOT newline-translated.
        self.src.write_bytes(
            b'{\r\n  "id": "gateway-api",\r\n  "version": "v1",\r\n  "hash": "h1"\r\n}\r\n')
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIsNone(err, f"pull should succeed, got {err!r}")
        self.assertEqual(self._landed().read_bytes(), self.src.read_bytes(),
                         "landed snapshot must be a byte-for-byte copy (no newline translation)")

    def test_unknown_contract_refused(self):
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "nope")
        self.assertIsNotNone(err)
        self.assertIn("federation_unknown", err or "")
        # nothing landed at all — not the requested id, not the declared one
        self.assertFalse((self.addp / "contracts").exists(),
                         "a refused pull must create no contracts/ dir")

    def test_missing_source_hard_stops(self):
        self.src.unlink()
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIsNotNone(err)
        self.assertIn("federation_source_missing", err or "")
        self.assertFalse(self._landed().exists())

    def test_invalid_bad_json_hard_stops(self):
        self.src.write_text("{not json", encoding="utf-8")
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIn("federation_snapshot_invalid", err or "")
        self.assertFalse(self._landed().exists())

    def test_invalid_wrong_id_hard_stops(self):
        self.src.write_text(json.dumps({"id": "other", "version": "v1", "hash": "h1"}), encoding="utf-8")
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIn("federation_snapshot_invalid", err or "")
        self.assertFalse(self._landed().exists())

    def test_invalid_no_hash_hard_stops(self):
        self.src.write_text(json.dumps({"id": "gateway-api", "version": "v1"}), encoding="utf-8")
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIn("federation_snapshot_invalid", err or "")
        self.assertFalse(self._landed().exists())

    def test_version_mismatch_hard_stops(self):
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\npin = "v2"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIn("federation_version_mismatch", err or "")
        self.assertFalse(self._landed().exists())

    def test_pin_match_lands(self):
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\npin = "v1"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIsNone(err)
        self.assertTrue(self._landed().exists())


class Check(_Board):
    def _check(self):
        out, errbuf = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["check"])
        except SystemExit:
            pass
        return out.getvalue() + errbuf.getvalue()

    def test_check_warns_unreadable_source(self):
        self.src.unlink()
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        self.assertIn("federation_source_unreadable", self._check())

    def test_no_federation_clean(self):
        self._manifest('[component.web]\nroot = "apps/web"\n')
        self.assertNotIn("federation", self._check())


class HardenConfine(_Board):
    """federation-harden: a manifest `source` may reach a DIRECT sibling repo
    (../<repo>/…, under the workspace root.parent.parent) but an absolute path or a
    deeper `../../` escape HARD-STOPs `federate pull` BEFORE any read, and surfaces
    early at `check` as a never-red WARN. The legit sibling pattern is unchanged."""

    def _check(self):
        out, errbuf = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(errbuf):
                add.main(["check"])
        except SystemExit:
            pass
        return out.getvalue() + errbuf.getvalue()

    def test_sibling_source_still_pulls(self):
        # non-regression: the documented one-level sibling source stays allowed
        self._manifest('[federation.gateway-api]\nsource = "../producer/.add/contracts/gateway-api.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIsNone(err, f"a legit sibling source must pull, got {err!r}")
        self.assertTrue(self._landed().exists())

    def test_absolute_source_escapes(self):
        self._manifest('[federation.gateway-api]\nsource = "/etc/passwd"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIsNotNone(err)
        self.assertIn("federation_source_escapes", err or "")
        self.assertFalse((self.addp / "contracts").exists(),
                         "an escaping pull must create no contracts/ dir")

    def test_deep_traversal_escapes(self):
        # "../../x" from root.parent climbs ABOVE the workspace (root.parent.parent) -> rejected
        self._manifest('[federation.gateway-api]\nsource = "../../escape.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIn("federation_source_escapes", err or "")
        self.assertFalse(self._landed().exists())

    def test_escape_checked_before_read(self):
        # an escaping source that also does NOT exist must report escapes, not missing
        self._manifest('[federation.gateway-api]\nsource = "/nope/does/not/exist.json"\n')
        out, err = self._federate("pull", "gateway-api")
        self.assertIn("federation_source_escapes", err or "")
        self.assertNotIn("federation_source_missing", err or "")
        self.assertFalse(self._landed().exists())

    def test_confined_helper_is_pure_and_total(self):
        ok = add._federation_source_confined(self.addp, "../producer/.add/contracts/gateway-api.json")
        self.assertTrue(ok, "a direct sibling must be confined")
        for bad in ("/etc/passwd", "../../escape.json", "../../../../../../etc/x", "\x00bad"):
            self.assertFalse(add._federation_source_confined(self.addp, bad),
                             f"{bad!r} must be rejected (never raise)")

    def test_check_warns_escaping_source_never_red(self):
        self._manifest('[federation.gateway-api]\nsource = "/etc/passwd"\n')
        out = self._check()
        self.assertIn("federation_source_escapes", out)
        # measure-not-block: an escaping source never turns check red
        code = 0
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                add.main(["check"])
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        self.assertEqual(code, 0, "an escaping federation source must not fail check")


if __name__ == "__main__":
    unittest.main()
