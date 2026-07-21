#!/usr/bin/env python3
"""Red/green tests for persona-setup (persona-learning-loop 1/7; persona-skill refit).

Personas are project requirements personas living under `.add/personas/`, AUTHORED via the
persona-author skill (persona-skill: the static `_template.md` scaffold is retired). The engine:
(a) creates the empty `.add/personas/` dir at cmd_init so authored personas have a home,
(b) validates personas presence-based (measure-not-block), (c) stays NO-EXEC (no network/spawn).
The persona-author skill (skill/add/persona-author/) carries the schema + judgment layer.
One test per scenario. Run: python3 -m unittest test_persona_setup -v
"""
import inspect
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

ENGINE_TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)
SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)
PERSONA_AUTHOR_REL = "persona-author"  # skill dir under each skill/add tree (persona-skill)
REQUIRED_SECTIONS = ("## Identity", "## Critical Rules", "## Default Requirement", "## Success Metrics")
FRONTMATTER_KEYS = ("name", "vibe")
# network/spawn tokens a NO-EXEC path must never contain (os.system built to dodge lint scanners)
FORBIDDEN_EXEC = ("socket", "urllib", "requests", "subprocess", "Popen", "os." + "system", "spawn")


def _conformant_persona() -> str:
    return (
        "---\nname: Frontend Engineer\nvibe: ships accessible, fast UI\n---\n"
        "## Identity\nA frontend specialist.\n\n"
        "## Critical Rules\n- accessibility first\n\n"
        "## Default Requirement\nWCAG AA in every screen.\n\n"
        "## Success Metrics\n- 4.5:1 contrast · 44px targets\n"
    )


class SeedTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-persona-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _personas(self) -> Path:
        return Path(self.tmp) / ".add" / "personas"

    # scenario: init creates the empty personas dir (no template) — personas are authored via the skill
    def test_init_creates_empty_personas_dir(self):
        d = self._personas()
        self.assertTrue(d.is_dir(), "init must create the .add/personas/ directory")
        self.assertFalse((d / "_template.md").exists(),
                         "no template is seeded — personas are authored via the persona-author skill")
        self.assertEqual(list(d.glob("*.md")), [], "the personas dir starts empty (unseeded → nudge fires)")

    # scenario: the skill's worked examples are schema-conformant (what an author imitates)
    def test_skill_examples_are_conformant(self):
        assets = PKG_ROOT / "skill" / "add" / PERSONA_AUTHOR_REL / "assets"
        for ex in ("example-persona.md", "example-design-persona.md"):
            text = (assets / ex).read_text(encoding="utf-8")
            self.assertEqual(add._persona_missing(text), [],
                             f"the skill example {ex} must be schema-conformant")

    # scenario: the skill documents the recommended flow frontmatter + the Abilities section, so the
    # design/build/advisor/verify surfaces can actually pick a persona up and use it
    def test_skill_documents_flow_and_abilities(self):
        base = PKG_ROOT / "skill" / "add" / PERSONA_AUTHOR_REL
        contract = (base / "references" / "contract.md").read_text(encoding="utf-8")
        self.assertRegex(contract, r"(?m)^flow:", "contract must document the 'flow' frontmatter")
        self.assertIn("Abilities", (base / "SKILL.md").read_text(encoding="utf-8"),
                      "the skill must cover the Abilities section")

    # scenario: re-init never clobbers an authored persona (survivor)
    def test_reinit_never_clobbers_authored_persona(self):
        f = self._personas() / "frontend.md"
        f.write_text(_conformant_persona(), encoding="utf-8")
        before = f.read_bytes()
        add.main(["init", "--force"])
        self.assertEqual(f.read_bytes(), before,
                         "init --force must not clobber an authored persona (survivor)")

    # scenario: init succeeds offline (fail-safe, no network)
    def test_seed_offline_failsafe(self):
        # Seed a FRESH project under a dead network: any socket the engine opens on the init path
        # raises. A NO-EXEC fail-safe init must (a) attempt NO socket and (b) still create the
        # personas dir (personas are authored later via the skill — nothing is fetched).
        import socket
        fresh = tempfile.mkdtemp(prefix="add-persona-offline-")
        self.addCleanup(shutil.rmtree, fresh, ignore_errors=True)
        os.chdir(fresh)
        attempts = []
        orig = socket.socket

        def _boom(*a, **k):
            attempts.append((a, k))
            raise OSError("network access attempted on a NO-EXEC seed path")

        socket.socket = _boom
        try:
            add.main(["init", "--name", "offline"])  # FRESH init — must NOT raise
        finally:
            socket.socket = orig
        self.assertEqual(attempts, [],
                         "the engine must attempt no network on the init path (NO-EXEC)")
        self.assertTrue((Path(fresh) / ".add" / "personas").is_dir(),
                        "a fresh init must create the personas dir with the network down (fail-safe)")

    # scenario: a persona missing a required section is flagged (measure-not-block via check)
    def test_check_census_warns_not_blocks(self):
        (self._personas() / "broken.md").write_text(
            "---\nname: X\nvibe: y\n---\n## Identity\n## Critical Rules\n## Default Requirement\n",
            encoding="utf-8")  # missing ## Success Metrics
        # capture the EXIT CODE explicitly — the measure-not-block contract (§3) is that a persona
        # warning surfaces but check still exits 0; a swallowed SystemExit would hide a regression.
        buf = io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf):
                add.main(["check"])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        out = buf.getvalue()
        self.assertIn("persona_schema_incomplete", out, "check must surface the incomplete persona")
        self.assertIn("broken", out, "check must name the offending persona slug")
        self.assertEqual(code, 0,
                         "a persona schema warning must NOT block check (measure-not-block, exit 0)")


class PredicateTest(unittest.TestCase):
    # scenario: a persona missing a required section yields the named error from the predicate
    def test_validator_flags_missing_section(self):
        text = _conformant_persona().replace("## Success Metrics\n- 4.5:1 contrast · 44px targets\n", "")
        self.assertIn("## Success Metrics", add._persona_missing(text),
                      "_persona_missing must report the absent section")

    def test_validator_conformant_returns_empty(self):
        self.assertEqual(add._persona_missing(_conformant_persona()), [],
                         "a conformant persona has nothing missing")

    # scenario: an invalid persona slug is rejected
    def test_persona_slug_invalid(self):
        self.assertFalse(add._persona_slug_valid("bad name!"), "spaces/punctuation slug is invalid")
        self.assertTrue(add._persona_slug_valid("frontend_dev-2"), "alnum + -/_ slug is valid")

    # scenario: the engine never fetches the teacher or spawns on the seed/validate path
    def test_engine_no_exec_on_persona_paths(self):
        # §3 scopes BOTH paths: validate (_persona_missing/_persona_slug_valid) AND seed
        # (cmd_init -> SETUP_FILES loop -> _render_template -> _atomic_write). Scan all of them.
        import add_engine.io_state as io_state
        symbols = (add._persona_missing, add._persona_slug_valid,        # validate
                   add.cmd_init, add._render_template, io_state._atomic_write)  # seed
        src = "".join(inspect.getsource(fn) for fn in symbols)
        for forbidden in FORBIDDEN_EXEC:
            self.assertNotIn(forbidden, src,
                             f"persona seed/validate path must stay NO-EXEC (found {forbidden!r})")


class ParityAndDocTest(unittest.TestCase):
    # scenario: the seed change is byte-identical across all three engine/template trees

    def test_persona_author_skill_ships_not_template(self):
        # persona-skill: the static template is retired from SETUP_FILES; the persona-author skill
        # ships in every skill tree instead (SKILL.md + the contract/patterns references).
        import add_engine.constants as c
        self.assertNotIn("personas/_template.md", c.SETUP_FILES,
                         "the persona template is retired — SETUP_FILES must not seed it")
        for tree in SKILL_TREES:
            base = tree / "persona-author"
            self.assertTrue((base / "SKILL.md").exists(), f"persona-author SKILL.md must ship in {tree}")
            self.assertTrue((base / "references" / "contract.md").exists(),
                            f"persona-author contract.md must ship in {tree}")

    # scenario: the first-run authoring step is documented and baseline-approval-covered
    def test_setup_guide_documents_authoring(self):
        # Assert the AUTHORING STEP content, not a one-word mention: the AI authors personas
        # from PROJECT.md + the LOCAL vendored teacher library (.add/personas-teacher/),
        # covered by the baseline approval. (de-branded — the upstream is vendored locally.)
        for tree in SKILL_TREES:
            txt = (tree / "phases" / "direction.md").read_text(encoding="utf-8").lower()
            self.assertIn("persona", txt, f"0-setup.md in {tree} must document persona authoring")
            self.assertIn("author", txt,
                          f"0-setup.md in {tree} must describe AUTHORING personas (not just mention them)")
            self.assertIn("teacher", txt,
                          f"0-setup.md in {tree} must name the teacher source for authoring")
            self.assertIn("personas-teacher", txt,
                          f"0-setup.md in {tree} must point at the local teacher library (.add/personas-teacher)")
            self.assertIn("baseline approval", txt,
                          f"0-setup.md in {tree} must state the seeded set is baseline-approval-covered")


if __name__ == "__main__":
    unittest.main(verbosity=2)
