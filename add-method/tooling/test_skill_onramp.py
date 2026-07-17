#!/usr/bin/env python3
"""Tests for the zero-command on-ramp (v15 skill-onramp).

The centerpiece is a PROTOCOL WALK: from a tmp dir holding only what the
installers lay down, the walker — standing in for the agent — issues every
add.py call itself (status → init parsed from 0-setup §1 → status → lock
parsed from 0-setup §4 → new-task → advance ×5 → gate PASS), running the
INSTALLED add.py. It pins the journey v15's exit criterion 3 names, not a
proxy. The prose tests close the one typed-command gap: the lock is run by
the AGENT on the human's recorded confirmation.
Run: python3 -m unittest test_skill_onramp -v
"""
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent
SETUP_CANONICAL = PKG_ROOT / "skill" / "add" / "phases" / "direction.md"
SETUP_TRIPLET = (
    SETUP_CANONICAL,
    REPO_ROOT / ".claude" / "skills" / "add" / "phases" / "direction.md",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "direction.md",
)

from engine_pin import ENGINE_MD5
ENGINE_PATHS = (
    PKG_ROOT / "tooling" / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)

# anchors the cospecify suite already pins — the §4 reword must not disturb them
COSPECIFY_ANCHORS = (
    # skill-loop-fold: the onward specify-guide pointer is retired — the specify
    # depth now lives in this same file (the Rules/scenarios co-specification span)
    "co-specify at foundation level",
    "Domain (DDD)", "Spec (SDD)", "Users (UDD)",
    "co-specification",
)


def _setup_text() -> str:
    return SETUP_CANONICAL.read_text(encoding="utf-8")


def _section4(text: str) -> str:
    """0-setup.md §4 (the lock-down) BODY, up to the next ## heading — the
    heading line itself is excluded so a future heading carrying a trigger
    phrase cannot satisfy a body assertion (v2 strengthening)."""
    m = re.search(r"^## 4 ·.*\n", text, re.M)
    if m is None:
        raise AssertionError("0-setup.md has no '## 4 ·' lock-down section")
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def _fenced(text: str) -> str:
    """Only the bodies of ``` code fences — prose is excluded."""
    return "\n".join(re.findall(r"^```[^\n]*\n(.*?)^```", text, re.S | re.M))


def _fence_command(section: str, subcommand: str) -> str:
    """The `python3 .add/tooling/add.py <subcommand> ...` line inside a REAL
    code fence — a column-0 command in plain prose does not count (v2)."""
    m = re.search(rf"^python3 \.add/tooling/add\.py {subcommand}[^\n]*$",
                  _fenced(section), re.M)
    if m is None:
        raise AssertionError(f"no fenced `add.py {subcommand}` command found")
    return m.group(0)


def _install(tmp: Path) -> None:
    """Lay down exactly what the installers lay down: skill tree + runtime
    tooling (tests stripped) — and NO state.json (drop-files-only rule)."""
    shutil.copytree(PKG_ROOT / "skill" / "add", tmp / ".claude" / "skills" / "add")
    tooling = tmp / ".add" / "tooling"
    tooling.mkdir(parents=True)
    shutil.copy2(PKG_ROOT / "tooling" / "add.py", tooling / "add.py")
    # the engine is a package now: add.py imports add_engine.constants — copy it too
    shutil.copytree(PKG_ROOT / "tooling" / "add_engine", tooling / "add_engine",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(PKG_ROOT / "tooling" / "templates", tooling / "templates")


def _run(tmp: Path, argv: list[str]):
    return subprocess.run([sys.executable, str(tmp / ".add" / "tooling" / "add.py"),
                           *argv], cwd=tmp, capture_output=True, text=True, timeout=120)


class ProtocolWalkTest(unittest.TestCase):
    """The journey itself — every command issued by the walker (the agent)."""

    @staticmethod
    def _freeze(tmp: Path, slug: str) -> None:
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = tmp / ".add" / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def test_protocol_walk_zero_typed_commands(self):
        text = _setup_text()
        with tempfile.TemporaryDirectory(prefix="add-onramp-") as td:
            tmp = Path(td)
            _install(tmp)

            # 1 · orient on nothing: the installed tree has no project yet
            res = _run(tmp, ["status"])
            self.assertNotEqual(res.returncode, 0, "status must fail pre-init")
            self.assertIn("no .add/ project found", res.stdout + res.stderr)

            # 2 · the agent runs init ITSELF — the command comes from the
            #     guide's own fence (placeholders are the agent's judgment)
            init_line = _fence_command(text, "init")
            self.assertIn("--await-lock", init_line,
                          "the guide's init must arm the lock-down gate")
            init_line = re.sub(r'"<[^>]+>"', '"demo"', init_line)
            init_line = re.sub(r"<[^>]+>", "mvp", init_line)
            argv = shlex.split(init_line)[2:]          # drop `python3 …/add.py`
            res = _run(tmp, argv)
            self.assertEqual(res.returncode, 0, f"init failed:\n{res.stderr}")

            # 3 · the pre-lock window is real: status names the lock next
            res = _run(tmp, ["status"])
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("lock", res.stdout.lower(),
                          "the unlocked window must name the lock as the next step")

            # 4 · the human confirms in chat; the AGENT runs the lock —
            #     command sourced from §4's fence, their name substituted
            lock_line = _fence_command(_section4(text), "lock")
            lock_line = lock_line.replace('"<name>"', '"Tin"')
            res = _run(tmp, shlex.split(lock_line)[2:])
            self.assertEqual(res.returncode, 0, f"lock failed:\n{res.stderr}")

            # 5 · first feature, driven to the gate — all agent-issued
            res = _run(tmp, ["new-task", "walk", "--title", "Protocol walk"])
            self.assertEqual(res.returncode, 0, res.stderr)
            self._freeze(tmp, "walk")                   # freeze-gate-universal sweep
            for _ in range(6):                          # ground → verify
                res = _run(tmp, ["advance"])
                self.assertEqual(res.returncode, 0, res.stderr)
            res = _run(tmp, ["gate", "PASS"])
            self.assertEqual(res.returncode, 0, res.stderr)

            state = json.loads((tmp / ".add" / "state.json").read_text())
            self.assertEqual(state["tasks"]["walk"]["phase"], "done")
            self.assertEqual(state["tasks"]["walk"]["gate"], "PASS")

    def test_prelock_window_names_the_lock(self):
        # focused pin of step 3's promise (one next move at the lost moment)
        with tempfile.TemporaryDirectory(prefix="add-onramp-") as td:
            tmp = Path(td)
            _install(tmp)
            _run(tmp, ["init", "--name", "demo", "--await-lock"])
            out = _run(tmp, ["status"]).stdout.lower()
            self.assertIn("lock", out)
            self.assertIn("setup-review", out,
                          "the window points at the review the human signs")


class LockProseTest(unittest.TestCase):
    """The one typed-command gap: §4 must make the lock agent-run."""

    def test_lock_step_is_agent_run(self):
        sec = _section4(_setup_text()).lower()
        self.assertIn("you run", sec,
                      "§4 must instruct the AGENT to run the lock — the human "
                      "decides; the agent types")
        self.assertTrue(
            re.search(r"(they confirm|the human confirms|their recorded|"
                      r"recorded confirmation)", sec),
            "§4 must anchor the lock to the human's recorded confirmation")
        self.assertIn("explicit yes", sec,
                      "§4 must demand an EXPLICIT yes to the lock-down itself — "
                      "ambient mid-stream agreement is not consent (v2)")

    def test_lock_escape_hatch_kept(self):
        sec = _section4(_setup_text()).lower()
        self.assertIn("escape hatch", sec,
                      "§4 must keep self-typing the lock as the named escape hatch")


class CompanionGuidesTest(unittest.TestCase):
    """v2: every OTHER shipped guide carrying the lock fence is agent-run too —
    the adversarial verify found the same human-types gap in both of these."""

    COMPANIONS = ("setup-review.md", "adopt.md")

    def _text(self, name: str) -> str:
        return (PKG_ROOT / "skill" / "add" / name).read_text(encoding="utf-8")

    def test_companion_guides_lock_is_agent_run(self):
        for name in self.COMPANIONS:
            low = self._text(name).lower()
            self.assertIsNotNone(
                re.search(r"^python3 \.add/tooling/add\.py lock", _fenced(low), re.M),
                f"{name} lost its lock fence — the guide must still show the command")
            self.assertNotRegex(low, r"(they sign|and signs)\s*(\*\*once\*\*|once)?\s*:",
                                f"{name} still hands the lock command to the human")
            self.assertIn("you run", low,
                          f"{name}: the lock must be agent-run on the human's word")

    def test_sign_row_is_chat_confirm(self):
        low = self._text("setup-review.md").lower()
        self.assertNotIn("sign: reviewed the above →", low,
                         "the Sign: template row must not present the command "
                         "as the human's action item")
        self.assertIn("confirm in chat", low,
                      "the Sign: row anchors the signature in conversation")

    def test_companion_guides_ship_x3(self):
        for name in self.COMPANIONS:
            twins = (PKG_ROOT / "skill" / "add" / name,
                     REPO_ROOT / ".claude" / "skills" / "add" / name,
                     PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add" / name)
            digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in twins}
            self.assertEqual(len(digests), 1, f"{name} drifted across the trees")


class ShipShapeTest(unittest.TestCase):
    def test_three_tree_parity(self):
        digests = {p: hashlib.md5(p.read_bytes()).hexdigest() for p in SETUP_TRIPLET}
        self.assertEqual(len(set(digests.values())), 1,
                         f"0-setup.md drifted across trees: {digests}")
        text = _setup_text()
        for anchor in COSPECIFY_ANCHORS:
            self.assertIn(anchor, text,
                          f"cospecify anchor lost in the reword: {anchor!r}")

    def test_engine_untouched(self):
        for p in ENGINE_PATHS:
            digest = hashlib.md5(p.read_bytes()).hexdigest()
            self.assertEqual(digest, ENGINE_MD5,
                             f"{p} changed — this prose-only task must not touch the engine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
