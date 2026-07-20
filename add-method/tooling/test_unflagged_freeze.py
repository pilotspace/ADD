#!/usr/bin/env python3
"""Red/green tests for the flag-first freeze guard (task unflagged-freeze).

A FROZEN §3 must carry a WELL-FORMED `Least-sure flag surfaced at freeze:` unit
before its bundle may cross into build. Two enforced fire-points (the third is
CI, which runs `audit`):

  * advance  — crossing tests->build with a frozen §3 whose flag is absent or
    malformed REFUSES `unflagged_freeze` (state untouched); a well-formed flag
    passes and STAMPS `flag_verified: true` on the task.
  * audit    — enforces the flag ONLY on `flag_verified` records (the
    verified-marker discriminator): a marked record whose flag was deleted or
    corrupted post-freeze is flagged; the unmarked predecessors are skipped, so
    the existing live board is never retro-redded.

Well-formed (evidence-corrected grammar — the 3 lived flags use em-dash/prose,
never literal because/if-wrong): the label phrase + >=1 [part] tag (part in
spec/scenario/contract/test, slash-joinable like [spec/contract]) + substantive
content. A bare 'none' is refused unless it takes the honest escape
'none material — biggest risk: X'. Asserts CLI output + exit codes + state, never
parser internals. Run:
    python3 -m unittest test_unflagged_freeze -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import gate_fixtures as tga   # frozen record shapes — one source of truth (ex test_gate_audit)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"
# the freeze guide must STATE what the engine now enforces (prose ≡ enforcement)
GUIDE_ANCHOR = "The engine refuses an unflagged freeze before build"

# ---- flag fixtures (the §3 unit, appended after the FROZEN stamp) -------------
LABEL = "Least-sure flag surfaced at freeze:"
FLAG_GOOD = f"{LABEL} ⚠ [contract] open-only — a malformed delta is never caught; silent miss"
FLAG_SLASH = f"{LABEL} ⚠ [spec/contract] report skips malformed lines — over-red risk"
FLAG_MULTILINE = (f"{LABEL}\n  ⚠ [test] (A) is proven by WIRING linkage, not a live run —\n"
                  "    it reds on broken wiring but cannot prove the downstream effect")
FLAG_NONE_ESCAPE = f"{LABEL} none material — biggest risk: the regex over-reds a valid flag"
FLAG_BARE_NONE = f"{LABEL} none"
FLAG_UNTAGGED = f"{LABEL} I'm not fully sure the parser handles every edge case here"
# absent = no flag line at all


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-uff-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "PLAN.md"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _state_sha(self) -> str:
        return hashlib.sha256((self._root() / "state.json").read_bytes()).hexdigest()

    def _body(self, slug: str, flag: str, frozen: bool = True) -> str:
        """A full PLAN.md whose §3 we control: the FROZEN stamp (optional) plus
        an optional flag unit appended after it. plan-phase-core: §3 is now the
        collapsed `## 3 · PLAN` (rule 6 — fenced shape first, under `### Contract`,
        then `Status:`); the numeral (not the title) is what the engine's
        `_phase_spans` keys on, but the label is kept truthful."""
        sec3 = (tga.GOOD3 if frozen else "Status: DRAFT")
        if flag:
            sec3 = f"{sec3}\n{flag}"
        return "\n".join([
            f"# PLAN: {slug}", "",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · PLAN", "### Contract", "```\nshape\n```", "", sec3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", tga._sec6(), "",
            "## 7 · OBSERVE", "watch", "",
        ])

    def _mk_at_direction(self, slug: str, flag: str, frozen: bool = True):
        """Create a task and write a controlled §3 — a fresh task is BORN at `direction`
        (phase-collapse-3), primed for the direction->build advance under guard."""
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])
        self._task_md(slug).write_text(self._body(slug, flag, frozen), encoding="utf-8")

    def _advance(self, slug: str):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["advance", slug])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _audit_json(self):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["audit", "--json"])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return json.loads(buf.getvalue()), code

    def _codes(self, d):
        return [x["code"] for x in d["findings"]]


# ============================================================================
# Advance guard — the forward boundary (tests -> build)
# ============================================================================
class AdvanceGuardTest(_Board):

    def _assert_refused(self, slug):
        before = self._state_sha()
        out, err, code = self._advance(slug)
        self.assertNotEqual(code, 0, "a frozen+unflagged build crossing must refuse")
        self.assertIn("unflagged_freeze", out + err)
        st = self._state()
        self.assertEqual(st["tasks"][slug]["phase"], "direction",
                         "refusal must leave the phase at direction")
        self.assertNotIn("flag_verified", st["tasks"][slug],
                         "a refused crossing must not stamp the marker")
        self.assertEqual(self._state_sha(), before,
                         "refusal must be a pure no-op on state.json")

    def _assert_allowed(self, slug):
        out, err, code = self._advance(slug)
        self.assertEqual(code, 0, out + err)
        st = self._state()
        self.assertEqual(st["tasks"][slug]["phase"], "build")
        self.assertIs(st["tasks"][slug].get("flag_verified"), True,
                      "a passed crossing must stamp flag_verified: true")

    # -- refusals --
    def test_refuses_absent_flag(self):
        self._mk_at_direction("alpha", flag="")          # the 45-record failure mode
        self._assert_refused("alpha")

    def test_refuses_bare_none(self):
        self._mk_at_direction("alpha", flag=FLAG_BARE_NONE)
        self._assert_refused("alpha")

    def test_refuses_untagged(self):
        self._mk_at_direction("alpha", flag=FLAG_UNTAGGED)   # content, but no [part] tag
        self._assert_refused("alpha")

    # -- passes --
    def test_allows_wellformed(self):
        self._mk_at_direction("alpha", flag=FLAG_GOOD)
        self._assert_allowed("alpha")

    def test_allows_multiline(self):
        self._mk_at_direction("alpha", flag=FLAG_MULTILINE)
        self._assert_allowed("alpha")

    def test_allows_slash_tag(self):
        # the freeze flag's own risk: the grammar must accept [spec/contract]
        self._mk_at_direction("alpha", flag=FLAG_SLASH)
        self._assert_allowed("alpha")

    def test_allows_none_escape(self):
        self._mk_at_direction("alpha", flag=FLAG_NONE_ESCAPE)
        self._assert_allowed("alpha")

    # -- scope: the guard is bounded by the freeze gate that precedes it --
    def test_freeze_precedes_flag_check(self):
        # phase-collapse-3 folded the whole front into ONE phase (`direction`), so there is
        # no separate "below the build boundary" hop left to prove the flag check doesn't
        # fire early on (a fresh task's only next crossing IS the guarded one). What still
        # holds: inside `_build_entry` the freeze gate runs BEFORE the flag check — an
        # UNFROZEN (DRAFT) §3 with no flag refuses on `contract_not_frozen`, never
        # `unflagged_freeze`, proving the flag check's scope stays bounded to a FROZEN §3.
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", "beta", "--title", "beta"])   # stays at direction
        self._task_md("beta").write_text(self._body("beta", flag="", frozen=False), encoding="utf-8")
        out, err, code = self._advance("beta")                   # direction -> build
        self.assertNotEqual(code, 0, out + err)
        self.assertIn("contract_not_frozen", out + err)
        self.assertNotIn("unflagged_freeze", out + err)
        self.assertEqual(self._state()["tasks"]["beta"]["phase"], "direction")


# ============================================================================
# Prose accord — the freeze guide must state the enforcement, synced ×3
# ============================================================================
class ProseAccordTest(unittest.TestCase):
    REL = ("skill", "add", "phases", "direction.md")

    def test_contract_guide_states_guard(self):
        canon = HERE.parent.joinpath(*self.REL)
        self.assertIn(GUIDE_ANCHOR, canon.read_text(encoding="utf-8"), canon)
        dogfood = REPO / ".claude" / "skills" / "add" / "phases" / "direction.md"
        for twin in (dogfood, BUNDLE.joinpath(*self.REL)):
            self.assertEqual(canon.read_bytes(), twin.read_bytes(),
                             f"divergence: {twin}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
