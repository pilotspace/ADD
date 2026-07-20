#!/usr/bin/env python3
"""extract-identity (engine-modularization 6/N) — the 7 git-native identity/actor fns
(`_git_config` · `_os_user` · `_whoami` · `_actor_stamp` · `_render_actor_line` ·
`_parse_actor_arg` · `_actor_matches`) moved from add.py into a NEW add_engine/identity.py.

NOT a pure-move leaf: add.py commands call `_whoami` BOTH directly (5 sites) AND via
`_actor_stamp` (5 sites). A verbatim move would make `patch.object(add,"_whoami")`
dual-path, so add.py QUALIFIES its call sites to `identity._whoami(...)` and the identity
tests patch `add_engine.identity.<name>` — ONE target reaching both the direct-command
path and the `_actor_stamp`-internal path. Human (Tin) authorized this call-qualification
refactor over the safe "leave in add.py" reduce.

Run: python3 -m unittest test_engine_extract_identity -v
"""
import hashlib
import re
import unittest
from pathlib import Path
from unittest import mock

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)

MOVED = ("_git_config", "_os_user", "_whoami", "_actor_stamp",
         "_render_actor_line", "_parse_actor_arg", "_actor_matches")


class ReexportTest(unittest.TestCase):
    def test_identity_fns_live_in_module(self):
        from add_engine import identity
        for name in MOVED:
            self.assertTrue(hasattr(identity, name),
                            f"identity.py must define {name} after the extraction")

    def test_identity_reexported_for_attr_compat(self):
        import add
        from add_engine import identity
        for name in MOVED:
            self.assertTrue(hasattr(add, name),
                            f"identity_drift: add.{name} missing after the split")
            self.assertIs(getattr(add, name), getattr(identity, name),
                          f"identity_drift: add.{name} is not the identity object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src,
                             f"dead-code: add.py still defines {name} (duplicate of identity)")

    def test_identity_module_is_a_stdlib_leaf(self):
        # imports only stdlib — no add_engine edges (a leaf), no `import add`
        src = (TOOLING / "add_engine" / "identity.py").read_text(encoding="utf-8")
        for forbidden in ("from add_engine", "import add\n", "import add "):
            self.assertNotIn(forbidden, src,
                             f"identity.py must stay a stdlib leaf — found {forbidden!r}")


class SingleTargetTest(unittest.TestCase):
    """The crux: ONE patch target (add_engine.identity._whoami) must reach BOTH the
    direct-call path AND the _actor_stamp-internal path — the reason for qualification."""

    def test_no_bare_identity_call_remains_in_add_py(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        # strip the import/re-export lines, then assert no BARE `_fn(` call survives —
        # every add.py call site must be qualified to `identity._fn(`.
        body = "\n".join(
            ln for ln in src.splitlines()
            if "import" not in ln  # drop the `from add_engine.identity import (...)` block
        )
        for name in MOVED:
            # a bare call is `<name>(` NOT preceded by `identity.` (or another attr dot)
            bare = re.search(rf"(?<![\w.]){re.escape(name)}\s*\(", body)
            self.assertIsNone(
                bare,
                f"unqualified_call: add.py has a bare {name}( — qualify it to identity.{name}( "
                f"so patch('add_engine.identity.{name}') reaches it")

    def test_one_target_controls_actor_stamp_internal_path(self):
        import add
        from add_engine import identity
        sentinel = {"name": "Patched Person", "email": "p@x.io", "source": "override"}
        # patch ONLY the identity-module target; the _actor_stamp -> _whoami internal call
        # (inside identity) must observe it — proving the single target reaches that path.
        with mock.patch.object(identity, "_whoami", return_value=dict(sentinel)):
            self.assertEqual(add._actor_stamp({}), sentinel,
                             "single target must reach the _actor_stamp-internal _whoami call")
            self.assertEqual(identity._render_actor_line({}),
                             "Patched Person <p@x.io> (override)",
                             "render must flow through the same patched whoami")

    def test_one_target_controls_git_config_internal_path(self):
        from add_engine import identity
        # _whoami -> _git_config is internal to identity; patching identity._git_config
        # must steer _whoami's git branch.
        with mock.patch.object(identity, "_git_config", return_value="GitName"):
            who = identity._whoami({})
            self.assertEqual(who["name"], "GitName")
            self.assertEqual(who["source"], "git")


class BehaviorTest(unittest.TestCase):
    def test_parse_actor_arg_roundtrip(self):
        import add
        self.assertEqual(add._parse_actor_arg("Ada <ada@x.io>"),
                         {"name": "Ada", "email": "ada@x.io", "source": "assigned"})
        self.assertEqual(add._parse_actor_arg("  BareName  "),
                         {"name": "BareName", "email": None, "source": "assigned"})

    def test_actor_matches_email_first_then_name(self):
        import add
        self.assertTrue(add._actor_matches({"name": "X", "email": "a@x.io"},
                                           {"name": "Y", "email": "A@X.io"}))
        self.assertTrue(add._actor_matches({"name": "Ada"}, {"name": "ada"}))
        self.assertFalse(add._actor_matches(None, {"name": "ada"}))


class PinTest(unittest.TestCase):

    def test_pkg_digest_includes_identity_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("identity.py", names, "identity.py must join the package manifest")
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != the package digest")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src,
                             f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
