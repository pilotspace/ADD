#!/usr/bin/env python3
"""Red/green tests for the §5 Scope gate (task scope-gate-enforce, build-scope-lock).

At tests->build the engine parses the frozen §5 `Scope (may touch):` declaration
(_declared_scope) and snapshots the project tree git-free ({rel: md5}) into a
sidecar .add/tasks/<slug>/scope-snapshot.json, anchored in state.json by the
sidecar's md5. At a COMPLETING gate (PASS / RISK-ACCEPTED) it re-walks, diffs
(modified+added+deleted = touched, fail-closed), and refuses `scope_violation`
when any touch falls outside every declared token (whole-subtree containment) —
placed after _tamper_guard, BEFORE the waiver write (never launderable). A
tampered/absent sidecar under a present anchor is `scope_snapshot_tampered`.
UNDECLARED (no Scope line) is grandfathered: no snapshot, no check, no warning.
HARD-STOP is never blocked. `check` WARNs early on a pending violation, never red.

GREEN pins at write (declared in §4): undeclared-skip · in-scope-pass ·
hard-stop-allowed · mirrors/pin — grandfather and non-regression pins that must
hold both before and after the build. Every other test is red (missing seams).

Run: python3 -m unittest test_scope_gate_enforce -v
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

WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2099-01-01"]


def _md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def _section(n: int, name: str, *body: str) -> list[str]:
    return [f"## {n} · {name}", *body, ""]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (the test_tamper_tripwire idiom),
    plus a small project tree to touch: src/app.py · lib/helpers.py · other/readme.txt."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-scope-")).resolve()
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
        # exclusion fixtures: must never appear in a snapshot
        (self.tmp / ".git").mkdir(exist_ok=True)
        (self.tmp / ".git" / "HEAD").write_text("ref: x\n", encoding="utf-8")
        (self.tmp / "src" / "__pycache__").mkdir(exist_ok=True)
        (self.tmp / "src" / "__pycache__" / "app.cpython-312.pyc").write_bytes(b"\x00")
        # a code-intelligence tool cache (serena) — re-writes itself on every source
        # edit, so it must be pruned from the walk or a build edit reads as an
        # out-of-scope touch (the fold-command dogfooding HARD-STOP that added .serena).
        (self.tmp / ".serena" / "cache" / "python").mkdir(parents=True, exist_ok=True)
        (self.tmp / ".serena" / "cache" / "python" / "symbols.pkl").write_bytes(b"\x00\x01")

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

    def _sidecar(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "scope-snapshot.json"

    # ---- arrangement ------------------------------------------------------
    _CONTRACT_BODY = "shape: scope gate { declared, snapshot_md5 }"

    def _write_task(self, slug: str, *, scope_line=None):
        """A full TASK.md with a FROZEN, flagged §3 (no unflagged_freeze death), a §4
        declaring `./tests/`, and a §5 whose Scope line is the test's lever."""
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
        """Create the task with the given §5 Scope line and CROSS tests->build
        (the snapshot seam fires under whatever engine is live)."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug, scope_line=scope_line)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build
        return self._task_state(slug)

    def _to_verify_and_gate(self, slug, *gate_args):
        self._silent("advance", slug)            # build -> verify
        outcome, *flags = gate_args or ("PASS",)
        return self._run("gate", outcome, slug, *flags)

    def _assert_refused(self, out, err, code, slug, token):
        self.assertNotEqual(code, 0, "the gate must refuse")
        self.assertIn(token, out + err)
        st = self._task_state(slug)
        self.assertEqual(st["gate"], "none", "a refusal records no completing outcome")
        self.assertNotEqual(st["phase"], "done")


SCOPED_SRC = "Scope (may touch): `src/`"


# ── the parser: the frozen grammar, UNDECLARED, fail-closed ──────────────────
class ParserTest(_Board):
    def _parser(self):
        self.assertTrue(hasattr(add, "_declared_scope"),
                        "engine seam _declared_scope is missing")
        return add._declared_scope

    def test_parser_resolves_grammar(self):
        self._silent("new-task", "alpha", "--title", "alpha")
        self._write_task("alpha", scope_line=(
            "Scope (may touch): `./src/` `lib/` `helpers.py`"))
        fn = self._parser()
        got = fn(self._root(), "alpha")
        self.assertEqual(sorted(got),
                         sorted([".add/tasks/alpha/src/", "lib/", "lib/helpers.py"]),
                         "./… = task dir · token with / = project root · bare = "
                         "sibling of the previous token's dir; dirs keep a trailing /")

    def test_parser_undeclared_none(self):
        self._silent("new-task", "alpha", "--title", "alpha")
        self._write_task("alpha", scope_line=None)
        self.assertIsNone(self._parser()(self._root(), "alpha"),
                          "no Scope line = UNDECLARED (None), never an empty list")

    def test_parser_outside_root_dropped(self):
        self._silent("new-task", "alpha", "--title", "alpha")
        self._write_task("alpha", scope_line="Scope (may touch): `../outside/`")
        got = self._parser()(self._root(), "alpha")
        self.assertEqual(got, [],
                         "outside-root tokens are dropped fail-closed; a garbage "
                         "declaration is an EMPTY allowlist, distinct from None")


# ── the advance: snapshot + anchor, grandfather, unconditional re-cross ──────
class SnapshotTest(_Board):
    def test_advance_snapshots_declared(self):
        self._arm("alpha", SCOPED_SRC)
        side = self._sidecar("alpha")
        self.assertTrue(side.is_file(), "scope-snapshot.json must be written")
        snap = json.loads(side.read_text(encoding="utf-8"))
        self.assertIn("src/app.py", snap.get("files", {}),
                      "project files are hashed by project-root-relative path")
        for banned in (".git/HEAD", "src/__pycache__/app.cpython-312.pyc",
                       ".serena/cache/python/symbols.pkl"):
            self.assertNotIn(banned, snap.get("files", {}),
                             f"excluded path leaked into the snapshot: {banned}")
        self.assertFalse(any(k.startswith(".add/") for k in snap.get("files", {})),
                         ".add is engine domain — pruned from the walk")
        anchor = self._task_state("alpha").get("scope")
        self.assertIsInstance(anchor, dict, "state.json must carry the scope anchor")
        self.assertEqual(anchor.get("snapshot_md5"), _md5_bytes(side.read_bytes()),
                         "the anchor pins the sidecar bytes")
        self.assertIn("src/", anchor.get("declared", []))

    def test_advance_skips_undeclared(self):
        self._arm("alpha", None)
        self.assertFalse(self._sidecar("alpha").exists(),
                         "UNDECLARED takes no snapshot (grandfather)")
        self.assertNotIn("scope", self._task_state("alpha"),
                         "UNDECLARED leaves no anchor in state.json")

    def test_undeclared_recross_cleans_up(self):
        # v3 (refute-disclosed): a declared->undeclared transition must remove the
        # previous declaration's leftovers at the crossing — UNDECLARED is never
        # refused, on EVERY path, including by a stale anchor.
        st = self._arm("alpha", SCOPED_SRC)
        self.assertIn("scope", st, "the anchor must exist before the transition")
        self._write_task("alpha", scope_line=None)            # Scope line removed
        self._silent("phase", "tests", "alpha")
        self._silent("advance", "alpha")                      # UNDECLARED re-cross
        self.assertNotIn("scope", self._task_state("alpha"),
                         "the stale anchor must be popped at an UNDECLARED crossing")
        self.assertFalse(self._sidecar("alpha").exists(),
                         "the stale sidecar must be unlinked at an UNDECLARED crossing")
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "PASS",
                         "an out-of-OLD-scope touch never refuses an UNDECLARED task")

    def test_recross_resnapshots(self):
        st = self._arm("alpha", SCOPED_SRC)
        self.assertIn("scope", st, "the anchor must exist before a re-cross can renew it")
        first = st["scope"]["snapshot_md5"]
        (self.tmp / "src" / "app.py").write_text("APP = 2\n", encoding="utf-8")
        self._silent("phase", "tests", "alpha")
        self._silent("advance", "alpha")         # re-cross -> unconditional overwrite
        second = self._task_state("alpha")["scope"]["snapshot_md5"]
        self.assertNotEqual(first, second, "a re-crossed change-request re-snapshots")

    def test_advance_excludes_build_artifacts(self):
        # Gitignored BUILD ARTIFACTS must never enter the scope snapshot. A regenerated
        # artifact is not a source touch — e.g. a Next.js `.next/` build, a `coverage/`
        # run, Playwright `test-results/`, or `tsconfig.tsbuildinfo` (whose `incremental`
        # rewrite even races a clean re-snapshot) must not trip a false scope_violation.
        artifacts = (
            "apps/.next/BUILD_ID", "apps/.next/cache/c.json",
            "apps/coverage/lcov.info", "apps/test-results/r.xml",
            "apps/tsconfig.tsbuildinfo", "nested/foo.tsbuildinfo",
        )
        for rel in artifacts:
            p = self.tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x\n", encoding="utf-8")
        self._arm("alpha", SCOPED_SRC)
        snap = json.loads(self._sidecar("alpha").read_text(encoding="utf-8")).get("files", {})
        for banned in artifacts:
            self.assertNotIn(banned, snap,
                             f"build artifact leaked into the scope snapshot: {banned}")
        self.assertIn("src/app.py", snap,
                      "real source must still be tracked (the exclusion is not over-broad)")


# ── the gate: containment, violations, laundering, stop ──────────────────────
class GateTest(_Board):
    def test_gate_in_scope_pass(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "src" / "app.py").write_text("APP = 2\n", encoding="utf-8")
        nested = self.tmp / "src" / "sub" / "new.py"          # whole-subtree cover
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text("N = 1\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "PASS")

    def test_gate_out_of_scope_modify_refused(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_refused(out, err, code, "alpha", "scope_violation")
        self.assertIn("other/readme.txt", out + err,
                      "the refusal names the offending rel path")

    def test_gate_new_and_deleted_refused(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "outside.txt").write_text("new\n", encoding="utf-8")
        (self.tmp / "other" / "readme.txt").unlink()
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_refused(out, err, code, "alpha", "scope_violation")
        for rel in ("outside.txt", "other/readme.txt"):
            self.assertIn(rel, out + err, f"touched-by-{rel} must be named")

    def test_waiver_not_launderable(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "RISK-ACCEPTED", *WAIVER)
        self._assert_refused(out, err, code, "alpha", "scope_violation")
        self.assertNotIn("waiver", json.dumps(self._task_state("alpha")),
                         "a violating RISK-ACCEPTED records no waiver")

    def test_sidecar_tamper_refused(self):
        st = self._arm("alpha", SCOPED_SRC)
        self.assertIn("scope", st, "the anchor must exist for a tamper to be visible")
        anchor_before = dict(st["scope"])
        side = self._sidecar("alpha")
        self.assertTrue(side.is_file(), "the sidecar must exist before it can be tampered")
        snap = json.loads(side.read_text(encoding="utf-8"))
        snap["files"].pop("other/readme.txt", None)           # hide a file, re-write
        side.write_text(json.dumps(snap), encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_refused(out, err, code, "alpha", "scope_snapshot_tampered")
        self.assertEqual(self._task_state("alpha")["scope"], anchor_before,
                         "the anchor is evidence — never rewritten by a refusal")

    def test_anchor_erase_refused(self):
        # v2 (refute-driven): the one-key state.json erase the refute-read reproduced.
        # The sidecar is the co-witness — anchor-less + sidecar-PRESENT is a refusal,
        # restoring single-file-erase parity with the tripwire; only the simultaneous
        # two-file erase remains (the explicitly accepted floor).
        st = self._arm("alpha", SCOPED_SRC)
        self.assertIn("scope", st, "the anchor must exist before it can be erased")
        side_bytes = self._sidecar("alpha").read_bytes()
        full = self._state()
        full["tasks"]["alpha"].pop("scope")
        (self._root() / "state.json").write_text(json.dumps(full), encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "PASS")
        self._assert_refused(out, err, code, "alpha", "scope_anchor_missing")
        self.assertEqual(self._sidecar("alpha").read_bytes(), side_bytes,
                         "the co-witness sidecar is evidence — untouched by the refusal")

    def test_hard_stop_never_blocked(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._to_verify_and_gate("alpha", "HARD-STOP")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self._task_state("alpha")["gate"], "HARD-STOP",
                         "stopping is always allowed")


# ── the standing monitor: WARN early, never red ──────────────────────────────
class StandingMonitorTest(_Board):
    def test_check_warns_pending(self):
        self._arm("alpha", SCOPED_SRC)
        (self.tmp / "other" / "readme.txt").write_text("changed\n", encoding="utf-8")
        out, err, code = self._run("check")
        self.assertEqual(code, 0, "the standing monitor is never-red")
        text = out + err
        self.assertIn("scope_violation", text, "check must WARN on a pending violation")
        self.assertIn("pending", text)


# ── atomic-scope-sidecar (F11): the sidecar write is crash-safe (temp+replace) ─
class AtomicSidecarTest(_Board):
    """The §5 scope sidecar must be written via _atomic_write (temp file + os.replace), like
    state.json — so a crash mid-write can't leave a torn scope-snapshot.json the next gate
    misreads as tamper. The on-disk bytes (and thus snapshot_md5) stay byte-identical."""

    def _spy_atomic_write(self):
        """Wrap add._atomic_write to record the Paths it is called with; returns (calls, restore)."""
        calls = []
        real = add._atomic_write
        def spy(path, text):
            calls.append(Path(path).resolve())
            return real(path, text)
        add._atomic_write = spy
        return calls, (lambda: setattr(add, "_atomic_write", real))

    def test_scope_sidecar_written_atomically(self):
        calls, restore = self._spy_atomic_write()
        try:
            self._arm("atom", SCOPED_SRC)            # declared scope; crosses tests->build
        finally:
            restore()
        self.assertIn(self._sidecar("atom").resolve(), calls,
                      "scope-snapshot.json must be written via _atomic_write, not a raw write_text")

    def test_sidecar_md5_anchor_preserved(self):
        self._arm("anchor", SCOPED_SRC)
        side = self._sidecar("anchor")
        self.assertTrue(side.exists(), "a declared-scope task must write the sidecar")
        self.assertEqual(
            add._md5_text(side.read_text(encoding="utf-8")),
            self._task_state("anchor")["scope"]["snapshot_md5"],
            "the on-disk sidecar md5 must still match the state anchor (no trailing-newline drift)",
        )
        _, _, code = self._to_verify_and_gate("anchor", "PASS")
        self.assertEqual(code, 0, "a clean build with a preserved anchor must gate PASS")

    def test_undeclared_task_writes_no_sidecar(self):
        self._arm("nodecl", None)                    # no §5 Scope line
        self.assertFalse(self._sidecar("nodecl").exists(),
                         "an UNDECLARED task takes no sidecar (the skip/unlink path is unchanged)")


# ── the discipline: ×3 parity + pin (GREEN pin at write, survives the re-pin) ─


if __name__ == "__main__":
    unittest.main(verbosity=2)
