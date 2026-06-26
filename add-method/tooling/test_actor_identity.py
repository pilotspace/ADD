#!/usr/bin/env python3
"""Red/green tests for the git-native actor resolver (user-identity 1/3):
_git_config (fail-soft, bounded) · _whoami (override→git→os) · the whoami command.
Run: python3 -m unittest test_actor_identity -v
"""
import hashlib
import io
import json
import os
import subprocess
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import add
from add_engine import identity
from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class WhoamiResolverTest(unittest.TestCase):
    def test_resolves_from_git(self):
        with mock.patch.object(identity, "_git_config",
                               side_effect=lambda k: {"user.name": "Ada", "user.email": "ada@x.io"}[k]):
            who = add._whoami({})
        self.assertEqual(who, {"name": "Ada", "email": "ada@x.io", "source": "git"})

    def test_falls_back_to_os(self):
        with mock.patch.object(identity, "_git_config", return_value=None), \
             mock.patch.object(add.getpass, "getuser", return_value="osuser"):
            who = add._whoami({})
        self.assertEqual(who, {"name": "osuser", "email": None, "source": "os"})

    def test_override_wins(self):
        st = {"actor_override": {"name": "Bob", "email": "bob@y.io"}}
        with mock.patch.object(identity, "_git_config", return_value="SomeoneElse"):
            who = add._whoami(st)
        self.assertEqual(who, {"name": "Bob", "email": "bob@y.io", "source": "override"})

    def test_blank_override_ignored(self):
        # an override with a blank name is NOT a valid identity -> fall through to git/os
        st = {"actor_override": {"name": "   ", "email": None}}
        with mock.patch.object(identity, "_git_config", return_value=None), \
             mock.patch.object(add.getpass, "getuser", return_value="osuser"):
            who = add._whoami(st)
        self.assertEqual(who["source"], "os")

    def test_os_floor_total_when_getuser_raises(self):
        # the TOTAL invariant: in a bare container getpass.getuser() raises KeyError
        # (no passwd entry + no LOGNAME/USER env). _whoami must NOT crash — it floors
        # to the "unknown" sentinel so it always returns a non-empty name.
        with mock.patch.object(identity, "_git_config", return_value=None), \
             mock.patch.object(add.getpass, "getuser", side_effect=KeyError("getpwuid(): uid not found")):
            who = add._whoami({})
        self.assertEqual(who, {"name": "unknown", "email": None, "source": "os"})


class GitConfigFailSoftTest(unittest.TestCase):
    def test_failsoft_no_git(self):
        with mock.patch.object(add.shutil, "which", return_value=None):
            self.assertIsNone(add._git_config("user.name"))

    def test_failsoft_timeout(self):
        with mock.patch.object(add.shutil, "which", return_value="/usr/bin/git"), \
             mock.patch.object(add.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired(cmd="git", timeout=2)):
            self.assertIsNone(add._git_config("user.name"))

    def test_failsoft_empty_stdout(self):
        with mock.patch.object(add.shutil, "which", return_value="/usr/bin/git"), \
             mock.patch.object(add.subprocess, "run",
                               return_value=mock.Mock(stdout="\n")):
            self.assertIsNone(add._git_config("user.email"))

    def test_failsoft_nonutf8_value(self):
        # text=True decoding of a latin-1 legacy config value raises UnicodeDecodeError
        # (a ValueError subclass, NOT OSError/SubprocessError) — must still fail soft.
        boom = UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
        with mock.patch.object(add.shutil, "which", return_value="/usr/bin/git"), \
             mock.patch.object(add.subprocess, "run", side_effect=boom):
            self.assertIsNone(add._git_config("user.name"))

    def test_uses_fixed_argv_no_shell(self):
        captured = {}
        def fake_run(argv, **kw):
            captured["argv"] = argv
            captured["kw"] = kw
            return mock.Mock(stdout="Ada\n")
        with mock.patch.object(add.shutil, "which", return_value="/usr/bin/git"), \
             mock.patch.object(add.subprocess, "run", side_effect=fake_run):
            add._git_config("user.name")
        self.assertEqual(captured["argv"], ["git", "config", "--get", "user.name"])
        self.assertNotIn("shell", captured["kw"])  # never shell=True
        self.assertIn("timeout", captured["kw"])    # bounded


class WhoamiCommandTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-actor-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            add.main(list(argv))
        return buf.getvalue()

    def _run(self, *argv):
        buf = io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def test_whoami_set_stores_override(self):
        self._silent("whoami", "--name", "Cleo", "--email", "cleo@z.io")
        self.assertEqual(self._state()["actor_override"], {"name": "Cleo", "email": "cleo@z.io"})
        out = json.loads(self._silent("whoami", "--json"))
        self.assertEqual(out, {"name": "Cleo", "email": "cleo@z.io", "source": "override"})

    def test_whoami_unset_clears(self):
        self._silent("whoami", "--name", "Cleo")
        self._silent("whoami", "--unset")
        self.assertNotIn("actor_override", self._state())

    def test_unset_without_override_rejected(self):
        before = self._state()
        _, code = self._run("whoami", "--unset")
        self.assertNotEqual(code, 0)
        self.assertEqual(self._state(), before)

    def test_set_blank_name_rejected(self):
        before = self._state()
        _, code = self._run("whoami", "--name", "")
        self.assertNotEqual(code, 0)
        self.assertEqual(self._state(), before)

    def test_set_empty_email_normalized_to_none(self):
        # --email "" is no email at all -> stored as None, not the empty string
        self._silent("whoami", "--name", "Cleo", "--email", "")
        self.assertEqual(self._state()["actor_override"], {"name": "Cleo", "email": None})

    def test_name_and_unset_mutually_exclusive(self):
        # contradictory flags must be rejected (argparse exit 2) before any state write
        before = self._state()
        _, code = self._run("whoami", "--unset", "--name", "Foo")
        self.assertNotEqual(code, 0)
        self.assertEqual(self._state(), before)


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
