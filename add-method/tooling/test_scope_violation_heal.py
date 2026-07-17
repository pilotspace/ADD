#!/usr/bin/env python3
"""Red/green tests for routing scope refusals into the bounded self-heal loop
(task scope-violation-heal, build-scope-lock 3/3).

scope-gate-enforce made _scope_guard REFUSE a completing gate when the build
touched outside its declared §5 Scope — but it died in place (exit 1). This task
reroutes the RECOVERABLE findings through the SAME _heal_or_escalate the tamper
tripwire uses: an out-of-scope touch (source "scope") and a present-but-wrong
sidecar (diverged/unparseable, source "scope-tamper") RETURN TO BUILD for an
honest redo (exit 3), counting against the ONE shared per-task HEAL_CAP; the
(CAP+1)th confirmed finding HARD-STOPs. The ERASED baselines stay die-in-place
(a redo cannot recreate trust): a missing sidecar is scope_snapshot_tampered, an
erased anchor under a present sidecar is scope_anchor_missing — both exit 1, no
heal recorded (tripwire_missing parity).

GREEN pins at write (must hold BEFORE and after the rewire): sidecar-missing-dies
· anchor-missing-dies · check-never-heals · mirrors/pin. The other five are red
(today the guard dies exit 1 where the contract now routes to heal exit 3).

Run: python3 -m unittest test_scope_violation_heal -v
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
import engine_pin

HERE = Path(__file__).resolve().parent           # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

HEAL_CAP = add.HEAL_CAP
WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2099-01-01"]
SCOPED_SRC = "Scope (may touch): `src/`"


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (the scope-gate-enforce idiom),
    with a small project tree to touch: src/app.py · lib/helpers.py · other/readme.txt."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-heal-scope-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")
        for rel, body in (("src/app.py", "APP = 1\n"),
                          ("lib/helpers.py", "H = 1\n"),
                          ("other/readme.txt", "hello\n")):
            p = self.tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- CLI helpers ------------------------------------------------------
    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _task_state(self, slug: str) -> dict:
        return self._state()["tasks"][slug]

    def _heal(self, slug: str) -> dict:
        return self._task_state(slug).get("heal") or {}

    def _attempts(self, slug: str) -> int:
        return self._heal(slug).get("attempts", 0)

    def _sidecar(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "scope-snapshot.json"

    # ---- arrangement (verbatim from test_scope_gate_enforce) --------------
    _CONTRACT_BODY = "shape: scope gate { declared, snapshot_md5 }"

    def _write_task(self, slug: str, *, scope_line=None):
        five = ["Strategy (ordered batches): 1. build", "Safety rule (feature-specific): none",
                "Code lives in: `./src/`"]
        if scope_line is not None:
            five.insert(0, scope_line)
        lines = [
            f"# TASK: {slug}",
            f"slug: {slug} · created: 2026-06-12 · stage: mvp",
            "phase: ground",
            "",
            *_section(0, "GROUND", "Anchors the contract cites: cmd_advance · cmd_gate"),
            *_section(1, "SPECIFY", "Feature: f"),
            *_section(2, "SCENARIOS", "(none)"),
            *_section(3, "CONTRACT",
                      "```", self._CONTRACT_BODY, "```",
                      "Status: FROZEN @ v1 — approved by Tester 2026-06-12.",
                      "Least-sure flag surfaced at freeze: [contract] the snapshot "
                      "lives in agent-writable files — accepted as an honest ceiling."),
            *_section(4, "TESTS",
                      "Coverage target: behavior",
                      "Tests live in: `./tests/`"),
            *_section(5, "BUILD", *five),
            *_section(6, "VERIFY", "checks"),
            *_section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug: str):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text(
            "def test_one():\n    assert compute(2) == 4\n", encoding="utf-8")

    def _arm(self, slug: str, scope_line):
        """Create the task with the given §5 Scope line and CROSS tests->build —
        the snapshot + anchor are born here under whatever engine is live."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug, scope_line=scope_line)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build
        return self._task_state(slug)

    def _to_verify_and_gate(self, slug, *gate_args):
        """advance (build->verify) then gate. Reused for the honest-redo step: a
        heal leaves phase=build, so the same advance re-enters verify."""
        self._silent("advance", slug)
        outcome, *flags = gate_args or ("PASS",)
        return self._run("gate", outcome, slug, *flags)

    def _seed_heal(self, slug: str, attempts: int, source: str):
        """Inject a pre-existing heal counter from another cheat source, straight
        into state.json — the lever that proves the cap is SHARED, not per-source."""
        full = self._state()
        full["tasks"][slug]["heal"] = {
            "attempts": attempts,
            "history": [{"at": "2026-01-01T00:00:00+00:00",
                         "reason": f"{source}_detected:x", "source": source}],
        }
        (self._root() / "state.json").write_text(json.dumps(full), encoding="utf-8")


# ── recoverable: an out-of-scope touch returns to build ──────────────────────
class ViolationHealsTest(_Board):

    def test_violation_returns_to_build(self):
        st = self._arm("alpha", SCOPED_SRC)
        side_before = self._sidecar("alpha").read_bytes()
        anchor_before = dict(st["scope"])
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 3, "a recoverable violation is a redo signal (exit 3)")
        blob = out + err
        self.assertIn("return_to_build", blob)
        self.assertIn("scope_violation", blob, "the named code rides the heal reason")
        self.assertIn("other/readme.txt", blob, "the offending path is still named")
        st2 = self._task_state("alpha")
        self.assertEqual(st2["phase"], "build", "the violation returns the task to build")
        self.assertEqual(st2["gate"], "none", "a heal records no completing outcome")
        self.assertEqual(self._attempts("alpha"), 1, "one attempt spent")
        hist = self._heal("alpha").get("history") or []
        self.assertTrue(hist and hist[-1].get("source") == "scope",
                        "a scope violation is sourced 'scope'")
        self.assertEqual(self._sidecar("alpha").read_bytes(), side_before,
                         "the sidecar is evidence — untouched by a heal")
        self.assertEqual(self._task_state("alpha")["scope"], anchor_before,
                         "the anchor is evidence — never re-armed by a heal")

    def test_cap_is_shared_across_sources(self):
        # a scope violation arriving at a cap already SPENT by a tamper cheat
        # escalates at once — proving ONE shared per-task counter, not a parallel loop.
        self._arm("alpha", SCOPED_SRC)
        self._seed_heal("alpha", HEAL_CAP, "tamper")
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertNotEqual(code, 0)
        self.assertIn("heal_exhausted", out + err)
        st = self._task_state("alpha")
        self.assertEqual(st["gate"], "HARD-STOP", "the shared cap escalates the next cheat")
        self.assertNotEqual(st["phase"], "done", "a gamed green is never auto-passed")
        hist = self._heal("alpha").get("history") or []
        self.assertTrue(hist and hist[-1].get("source") == "scope",
                        "the escalating arrival is the scope violation")

    def test_honest_redo_passes(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")    # heal -> build
        self.assertEqual(code, 3, "the violation first returns to build")
        # honest redo: revert the offending file to its snapshot bytes
        (self.tmp / "other" / "readme.txt").write_text("hello\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "PASS")
        self.assertEqual(self._attempts("alpha"), 1,
                         "the counter only moves on a cheat — monotonic, no reset on success")


# ── recoverable: a present-but-wrong sidecar heals; a restored one passes ─────
class SidecarTamperHealsTest(_Board):

    def test_sidecar_diverged_heals_then_restores(self):
        self._arm("alpha", SCOPED_SRC)
        side = self._sidecar("alpha")
        original = side.read_bytes()
        snap = json.loads(original.decode("utf-8"))
        snap["files"]["src/app.py"] = "deadbeef" * 4              # rewrite -> md5 diverges
        side.write_text(json.dumps(snap), encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 3, "a present-but-wrong sidecar is revertable — it heals")
        self.assertIn("scope_snapshot_tampered", out + err)
        self.assertEqual(self._task_state("alpha")["phase"], "build")
        hist = self._heal("alpha").get("history") or []
        self.assertTrue(hist and hist[-1].get("source") == "scope-tamper",
                        "a tampered sidecar is sourced 'scope-tamper'")
        # restore the ORIGINAL sidecar bytes -> md5 matches the anchor again -> passes
        side.write_bytes(original)
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "PASS")


# ── erased baselines still die in place (GREEN pins — tripwire_missing parity) ─
class ErasedBaselineDiesTest(_Board):

    def test_sidecar_missing_still_dies(self):
        self._arm("alpha", SCOPED_SRC)
        self._sidecar("alpha").unlink()
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 1, "an erased sidecar dies in place, not exit-3 heal")
        blob = out + err
        self.assertIn("scope_snapshot_tampered", blob)
        self.assertIn("missing", blob)
        self.assertEqual(self._task_state("alpha")["phase"], "verify",
                         "no return-to-build for an unrecoverable baseline")
        self.assertNotIn("heal", self._task_state("alpha"),
                         "an erased baseline records no heal attempt")

    def test_anchor_missing_still_dies(self):
        st = self._arm("alpha", SCOPED_SRC)
        self.assertIn("scope", st, "the anchor must exist before it can be erased")
        side_bytes = self._sidecar("alpha").read_bytes()
        full = self._state()
        full["tasks"]["alpha"].pop("scope")
        (self._root() / "state.json").write_text(json.dumps(full), encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 1, "an erased anchor dies in place, not exit-3 heal")
        self.assertIn("scope_anchor_missing", out + err)
        self.assertNotIn("heal", self._task_state("alpha"),
                         "an erased anchor records no heal attempt")
        self.assertEqual(self._sidecar("alpha").read_bytes(), side_bytes,
                         "the co-witness sidecar is evidence — untouched by the refusal")


# ── the cheat is never launderable, the monitor never heals ──────────────────
class NoLaunderTest(_Board):

    def test_waiver_never_lands_on_heal(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "RISK-ACCEPTED", *WAIVER)
        self.assertEqual(code, 3, "the heal fires BEFORE the waiver write")
        self.assertIn("scope_violation", out + err)
        self.assertNotIn("waiver", json.dumps(self._task_state("alpha")),
                         "no waiver is recorded on a healed violation")

    def test_check_never_heals(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._run("check")
        self.assertEqual(code, 0, "the standing monitor is never-red")
        self.assertIn("scope_violation", out + err, "check WARNs on the pending violation")
        self.assertNotIn("heal", self._task_state("alpha"),
                         "the monitor is read-only — it never spends an attempt")


# ── the discipline: ×3 parity + pin (GREEN pin, survives the re-pin) ─────────


if __name__ == "__main__":
    unittest.main(verbosity=2)
