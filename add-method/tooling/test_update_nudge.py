#!/usr/bin/env python3
"""Behavioral proof of the agent-agnostic update nudge (prototype: agent-update-nudge).

ADD is agent-agnostic: ANY agent (Claude Code · Gemini CLI · Codex) is told by the
guideline block to run `add.py status`/`guide` FIRST, every session. That makes the
engine the universal chokepoint to tell the agent its tooling is stale — a plain line
on STDERR the agent reads and acts on (run update, then resume the user's task).

CONTRACT (frozen @ v1):
  - On `status`/`guide` ONLY, when a launcher install stamp (.add-version) is present
    and the registry's latest > the project's version, the engine writes an ACTION-
    REQUIRED nudge to STDERR naming the update command. stdout stays clean (--json safe).
  - Bounded + fail-open: no stamp -> inert (covers every engine-only test project, so the
    offline suite never touches the network); offline / fetch error / ADD_NO_UPDATE_CHECK
    -> silent no-op; the registry is hit at most once / TTL (cached in .update-cache.json).
  - It is advisory: it NEVER changes the command's exit code or stdout.

Run: python3 -m unittest test_update_nudge -v
"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class UpdateNudgeTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-nudge-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.add_dir = add.find_root()
        self._orig_fetch = add._fetch_latest_version
        os.environ.pop("ADD_NO_UPDATE_CHECK", None)

    def tearDown(self):
        add._fetch_latest_version = self._orig_fetch
        os.environ.pop("ADD_NO_UPDATE_CHECK", None)
        os.chdir(self._cwd)

    def _stamp(self, version, channel="npm"):
        (self.add_dir / ".add-version").write_text(
            json.dumps({"version": version, "channel": channel}) + "\n")

    def _fetch_returns(self, version):
        add._fetch_latest_version = lambda *a, **k: version

    def _fetch_must_not_run(self):
        def boom(*a, **k):
            raise AssertionError("network fetch must not run")
        add._fetch_latest_version = boom

    # --- the core behaviour --------------------------------------------------
    def test_nudge_on_status_when_behind(self):
        self._stamp("1.0.0")
        self._fetch_returns("2.0.0")
        code, out, err = _run(["status"])
        self.assertEqual(code, 0, "the nudge is advisory — status still succeeds")
        self.assertIn("out of date", err.lower())
        self.assertIn("2.0.0", err)
        self.assertIn("update", err.lower())

    def test_channel_picks_the_right_command(self):
        self._stamp("1.0.0", channel="pip")
        self._fetch_returns("2.0.0")
        _, _, err = _run(["guide"])
        self.assertIn("pipx run pilotspace-add update", err)

    def test_no_nudge_when_current(self):
        self._stamp("2.0.0")
        self._fetch_returns("1.0.0")          # latest < current -> nothing
        _, _, err = _run(["status"])
        self.assertNotIn("out of date", err.lower())

    # --- bounded + fail-open -------------------------------------------------
    def test_inert_without_a_launcher_stamp(self):
        # no .add-version -> the network is never touched (keeps the offline suite clean)
        self._fetch_must_not_run()
        code, _, err = _run(["status"])
        self.assertEqual(code, 0)
        self.assertNotIn("out of date", err.lower())

    def test_fail_open_when_offline(self):
        self._stamp("1.0.0")
        def offline(*a, **k):
            raise OSError("no network")
        add._fetch_latest_version = offline
        code, _, err = _run(["status"])
        self.assertEqual(code, 0)             # a nudge must NEVER break a command
        self.assertNotIn("out of date", err.lower())

    def test_opt_out_env(self):
        self._stamp("1.0.0")
        self._fetch_must_not_run()
        os.environ["ADD_NO_UPDATE_CHECK"] = "1"
        _, _, err = _run(["status"])
        self.assertNotIn("out of date", err.lower())

    def test_throttle_serves_from_cache(self):
        self._stamp("1.0.0")
        (self.add_dir / ".update-cache.json").write_text(json.dumps({
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "latest": "3.0.0",
        }) + "\n")
        self._fetch_must_not_run()            # fresh cache -> no network
        _, _, err = _run(["status"])
        self.assertIn("3.0.0", err)

    # --- only the orientation commands, and never stdout ---------------------
    def test_no_nudge_on_non_orientation_commands(self):
        self._stamp("1.0.0")
        self._fetch_returns("2.0.0")
        _, _, err = _run(["check"])           # not status/guide
        self.assertNotIn("out of date", err.lower())

    def test_json_stdout_stays_clean(self):
        self._stamp("1.0.0")
        self._fetch_returns("2.0.0")
        _, out, err = _run(["status", "--json"])
        json.loads(out)                       # stdout must remain valid JSON
        self.assertIn("out of date", err.lower())   # nudge went to stderr


if __name__ == "__main__":
    unittest.main()
