#!/usr/bin/env python3
"""Red/green tests for engine-merge-base-enforcement - the engine EXECUTES the
wave-ledger fork-base rule streams.md only states.

Two surfaces (A+B, human-chosen at co-specify 2026-06-11):
  A) `add.py check` validates every existing `.add/milestones/*/WAVE.md`, status-aware:
     a FILLED fork-base echo != base is FAIL `unverified_fork_base` at ANY status;
     a pending/placeholder row is FAIL at `status: merging` (merge-time strictness)
     but only WARN `fork_base_pending` at `status: live` (measure-not-block);
     an unparseable ledger is FAIL `wave_ledger_malformed` (fail-closed, names the piece).
  B) `add.py wave-verify [milestone]` - the explicit merge-time gate: read-only,
     judgment-free, strict at any status; exit 0 only when EVERY roster echo matches
     base; refusals: unverified_fork_base | wave_ledger_malformed | wave_not_found |
     wave_ambiguous. NEVER mutates WAVE.md or state.json.

sha match := exact, or prefix-match with both tokens >=7 hex chars (git short-sha).

Asserts are RENDER-BLIND (vocab tokens + exit codes, never exact layout) per the
vocab-test-blind-to-render convention. Arrange-through-CLI-contracts where the engine
has a contract; the WAVE.md artifact itself is hand-written by the orchestrator per
the streams.md template, so tests write the fixture file directly (that IS the input
contract). ASCII-safe asserts (house rule).
Run: python3 -m unittest test_merge_base_enforcement -v
"""
from __future__ import annotations

import hashlib
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin
import test_min_pillar

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

# add.py copies the shared pin guards (must stay byte-identical and == ENGINE_MD5).
ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]

BASE = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"        # the wave base sha (40 hex)
OTHER = "ffff000011112222333344445555666677778888"       # a mismatching echo
PLACEHOLDER = "<paste `git -C <wt> rev-parse HEAD` output>"


def _wave_md(status: str = "live", base: str = BASE, rows=None) -> str:
    """A WAVE.md per the streams.md template grammar."""
    rows = rows if rows is not None else [("t1", "wt-a", base)]
    lines = [
        "# WAVE.md - transient wave ledger (orchestrator-owned)",
        f"wave: 1 · opened: 2026-06-11 · status: {status}",
        f"base: {base}",
        "",
        "### Roster (lease ledger)",
        "| task | lease (worker) | fork-base (pasted) | autonomy | spawned | timeout |",
        "|------|----------------|--------------------|----------|---------|---------|",
    ]
    for slug, lease, echo in rows:
        lines.append(f"| {slug} | {lease} | {echo} | auto | 10:00 | 30m |")
    lines += ["", "### Mid-wave decisions", "- none", "",
              "### Merge order (serial; integration Verify per merge)", "1. t1", ""]
    return "\n".join(lines)


class WaveBoard(unittest.TestCase):
    """A live board arranged through the real CLI; WAVE.md written per template."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-wave-gate-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["lock", "--force"])
            add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _wave_path(self, m: str = "mvp") -> Path:
        return self.tmp / ".add" / "milestones" / m / "WAVE.md"

    def _write_wave(self, content: str, m: str = "mvp") -> Path:
        p = self._wave_path(m)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def _run(self, *argv):
        """Run an add.main call; return (out+err text, exit-code)."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue() + err.getvalue(), code

    # ---- A: the standing monitor (check) -----------------------------------
    def test_check_red_on_mismatched_echo(self):
        p = self._write_wave(_wave_md(status="live", rows=[("t1", "wt-a", OTHER)]))
        before = p.read_bytes()
        out, code = self._run("check")
        self.assertNotEqual(code, 0, "a FILLED mismatched echo must be red at ANY status")
        self.assertIn("unverified_fork_base", out)
        self.assertEqual(p.read_bytes(), before, "check must never mutate the ledger")

    def test_check_red_on_pending_at_merging(self):
        self._write_wave(_wave_md(status="merging", rows=[("t1", "wt-a", PLACEHOLDER)]))
        out, code = self._run("check")
        self.assertNotEqual(code, 0, "merge-time strictness: a pending row at merging is red")
        self.assertIn("unverified_fork_base", out)

    def test_check_warns_on_pending_at_live(self):
        self._write_wave(_wave_md(status="live", rows=[("t1", "wt-a", PLACEHOLDER)]))
        out, code = self._run("check")
        self.assertIn("fork_base_pending", out, "a pending row at live is a WARN")
        self.assertNotIn("unverified_fork_base", out,
                         "a pending row at live must NOT raise the red finding")
        self.assertEqual(code, 0, "WARN is measure-not-block - never red on its own")

    def test_check_fail_closed_malformed(self):
        self._write_wave(_wave_md(base="<orchestrator HEAD at spawn>",
                                  rows=[("t1", "wt-a", BASE)]))
        out, code = self._run("check")
        self.assertNotEqual(code, 0, "an unparseable base is fail-closed, never skipped")
        self.assertIn("wave_ledger_malformed", out)

    def test_check_silent_without_ledger(self):
        out, code = self._run("check")
        self.assertEqual(code, 0, "a clean board stays green without a ledger")
        self.assertNotIn("wave_", out, "no WAVE.md -> no wave output (regression-silent)")

    # ---- B: the merge-time gate (wave-verify) ------------------------------
    def test_wave_verify_passes_full_roster(self):
        p = self._write_wave(_wave_md(status="merging",
                                      rows=[("t1", "wt-a", BASE), ("t2", "wt-b", BASE)]))
        before = p.read_bytes()
        out, code = self._run("wave-verify")
        self.assertEqual(code, 0, f"all echoes match base -> exit 0; out={out!r}")
        self.assertIn("t1", out)
        self.assertIn("t2", out, "the pass report is per-row")
        self.assertEqual(p.read_bytes(), before, "wave-verify is read-only")

    def test_wave_verify_refuses_mismatch(self):
        for echo in (OTHER, PLACEHOLDER):
            with self.subTest(echo=echo[:12]):
                p = self._write_wave(_wave_md(status="live", rows=[("t1", "wt-a", echo)]))
                before = p.read_bytes()
                out, code = self._run("wave-verify")
                self.assertNotEqual(code, 0, "strict at any status")
                self.assertIn("unverified_fork_base", out)
                self.assertEqual(p.read_bytes(), before, "refusal must not mutate")

    def test_wave_verify_target_resolution(self):
        out, code = self._run("wave-verify")
        self.assertNotEqual(code, 0)
        self.assertIn("wave_not_found", out, "no ledger anywhere -> wave_not_found")
        # two live ledgers + a bare call -> ambiguous, names both
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            add.main(["new-milestone", "m2", "--goal", "g2", "--stage", "mvp"])
        self._write_wave(_wave_md(), "mvp")
        self._write_wave(_wave_md(), "m2")
        out, code = self._run("wave-verify")
        self.assertNotEqual(code, 0)
        self.assertIn("wave_ambiguous", out)
        # an explicit milestone argument resolves
        out, code = self._run("wave-verify", "mvp")
        self.assertEqual(code, 0, f"explicit milestone must resolve; out={out!r}")

    def test_short_sha_prefix_matches(self):
        self._write_wave(_wave_md(rows=[("t1", "wt-a", BASE[:12])]))
        out, code = self._run("wave-verify")
        self.assertEqual(code, 0, "a 12-hex prefix of the 40-hex base is a match")
        out, code = self._run("check")
        self.assertEqual(code, 0)
        self.assertNotIn("unverified_fork_base", out)

    # ---- v2 (re-freeze 2026-06-11): ambiguity refusal + drift-vector pins ---
    def test_ambiguity_refusal_decoy_column(self):
        """v2 RED driver: two fork-base-matching header columns must refuse.

        A decoy `fork-base-prev` column filled with base-matching shas may not
        steal the echo from the real `fork-base (pasted)` column holding a
        MISMATCH - never first-wins on a hand-written artifact.
        """
        content = (
            "# WAVE.md - transient wave ledger (orchestrator-owned)\n"
            "wave: 1 · opened: 2026-06-11 · status: live\n"
            f"base: {BASE}\n"
            "\n"
            "### Roster (lease ledger)\n"
            "| task | lease (worker) | fork-base-prev | fork-base (pasted) | autonomy |\n"
            "|------|----------------|----------------|--------------------|----------|\n"
            f"| t1 | wt-a | {BASE} | {OTHER} | auto |\n"
        )
        p = self._write_wave(content)
        before = p.read_bytes()
        for argv in (("check",), ("wave-verify",)):
            with self.subTest(surface=argv[0]):
                out, code = self._run(*argv)
                self.assertNotEqual(
                    code, 0,
                    ">1 fork-base-matching header column is ambiguous - refuse, "
                    "never pick first-wins")
                self.assertIn("wave_ledger_malformed", out)
        self.assertEqual(p.read_bytes(), before, "refusal must not mutate")

    def test_drift_vectors_stay_closed(self):
        """v2 pins: each heal-1/2/3 vector keeps its NAMED refusal code (both surfaces)."""
        header = (
            "| task | lease (worker) | fork-base (pasted) | autonomy | spawned | timeout |\n"
            "|------|----------------|--------------------|----------|---------|---------|\n")
        roster = "### Roster (lease ledger)\n" + header
        vectors = [
            # heal-1 FG-1: a drift-note cell (mismatch token + base-prefix token)
            ("drift-note-cell", "unverified_fork_base",
             "wave: 1 · opened: 2026-06-11 · status: live\n"
             f"base: {BASE}\n\n" + roster +
             f"| t1 | wt-a | {OTHER} (was {BASE[:12]}) | auto | 10:00 | 30m |\n"),
            # heal-1 FG-2: body prose cannot rescue a status-less header
            ("body-prose-status-rescue", "wave_ledger_malformed",
             "wave: 1 · opened: 2026-06-11\n"
             f"base: {BASE}\n\nnote - status: live is prose here, not the header\n\n"
             + roster + f"| t1 | wt-a | {BASE} | auto | 10:00 | 30m |\n"),
            # heal-2 FG-3: a LATER wave:-prefixed body line cannot rescue either
            ("later-wave-line-status-rescue", "wave_ledger_malformed",
             "wave: 1 · opened: 2026-06-11\n"
             f"base: {BASE}\n\nwave: footnote status: live\n\n"
             + roster + f"| t1 | wt-a | {BASE} | auto | 10:00 | 30m |\n"),
            # heal-3 P1: an extra leading column may not hide a mismatched echo
            ("shifted-column", "unverified_fork_base",
             "wave: 1 · opened: 2026-06-11 · status: live\n"
             f"base: {BASE}\n\n### Roster (lease ledger)\n"
             "| wave | task | lease (worker) | fork-base (pasted) | autonomy |\n"
             "|------|------|----------------|--------------------|----------|\n"
             f"| 1 | t1 | wt-a | {OTHER} | auto |\n"),
            # heal-3 P2b: a headerless roster is malformed, never a silent skip
            ("headerless-roster", "wave_ledger_malformed",
             "wave: 1 · opened: 2026-06-11 · status: live\n"
             f"base: {BASE}\n\n### Roster (lease ledger)\n"
             f"| t1 | wt-a | {OTHER} | auto | 10:00 | 30m |\n"),
            # heal-3 Pex: an empty base: line may not borrow the next line's sha
            ("empty-base-line", "wave_ledger_malformed",
             "wave: 1 · opened: 2026-06-11 · status: live\n"
             f"base:\n{BASE}\n\n" + roster +
             f"| t1 | wt-a | {BASE} | auto | 10:00 | 30m |\n"),
        ]
        for name, token, content in vectors:
            with self.subTest(vector=name):
                p = self._write_wave(content)
                before = p.read_bytes()
                for argv in (("check",), ("wave-verify",)):
                    out, code = self._run(*argv)
                    self.assertNotEqual(
                        code, 0, f"vector {name} must stay refused on {argv[0]}")
                    self.assertIn(token, out,
                                  f"vector {name} must keep its NAMED code on {argv[0]}")
                self.assertEqual(p.read_bytes(), before, "refusal must not mutate")

    # ---- v3 (re-freeze 2026-06-11): strict status terminator ----------------
    def test_status_placeholder_is_malformed(self):
        """v3 RED driver: the literal unfilled template text `status: live|merging`
        is never parsed as `live` — refused wave_ledger_malformed on BOTH surfaces,
        at ANY echo state, with no fork_base_pending WARN downgrade."""
        for echo, label in ((BASE, "matching-echo"), (PLACEHOLDER, "pending-row")):
            with self.subTest(echo=label):
                p = self._write_wave(_wave_md(status="live|merging",
                                              rows=[("t1", "wt-a", echo)]))
                before = p.read_bytes()
                for argv in (("check",), ("wave-verify",)):
                    out, code = self._run(*argv)
                    self.assertNotEqual(
                        code, 0,
                        f"an unfilled status field must refuse on {argv[0]} "
                        f"({label}) - never parse as its valid prefix")
                    self.assertIn("wave_ledger_malformed", out)
                    self.assertNotIn(
                        "fork_base_pending", out,
                        "the standing monitor must never downgrade an "
                        "unfilled-status ledger to a WARN")
                self.assertEqual(p.read_bytes(), before, "refusal must not mutate")

    def test_status_suffix_drift_is_malformed(self):
        """v3 RED driver: `live`/`merging` must be the exact token - a suffixed
        variant terminated by a non-word char is NOT its valid prefix."""
        for status in ("live-ish", "merging-soon"):
            with self.subTest(status=status):
                p = self._write_wave(_wave_md(status=status,
                                              rows=[("t1", "wt-a", BASE)]))
                before = p.read_bytes()
                for argv in (("check",), ("wave-verify",)):
                    out, code = self._run(*argv)
                    self.assertNotEqual(
                        code, 0,
                        f"status {status!r} is not a valid token on {argv[0]}")
                    self.assertIn("wave_ledger_malformed", out)
                self.assertEqual(p.read_bytes(), before, "refusal must not mutate")

    # ---- v4 (re-freeze 2026-06-11): status label left anchor ----------------
    def test_status_label_left_anchored(self):
        """v4 RED driver: an EMBEDDED status-like label (`substatus: live`) is
        not a status field - a header with no real status field is malformed,
        never silently parsed through the embedded substring."""
        content = (
            "# WAVE.md - transient wave ledger (orchestrator-owned)\n"
            "wave: 1 · opened: 2026-06-11 · substatus: live\n"
            f"base: {BASE}\n"
            "\n"
            "### Roster (lease ledger)\n"
            "| task | lease (worker) | fork-base (pasted) | autonomy |\n"
            "|------|----------------|--------------------|----------|\n"
            f"| t1 | wt-a | {BASE} | auto |\n"
        )
        p = self._write_wave(content)
        before = p.read_bytes()
        for argv in (("check",), ("wave-verify",)):
            with self.subTest(surface=argv[0]):
                out, code = self._run(*argv)
                self.assertNotEqual(
                    code, 0,
                    "an embedded substatus: label must never anchor the "
                    "status parse - no real status field means malformed")
                self.assertIn("wave_ledger_malformed", out)
        self.assertEqual(p.read_bytes(), before, "refusal must not mutate")

    # ---- census + scope guard ----------------------------------------------
    def test_census_and_pin(self):
        covered = {argv[0] for argv in test_min_pillar.LIFECYCLE}
        self.assertIn("wave-verify", covered,
                      "the new verb must be census-classified (closed census)")
        self.assertIn("wave-verify", test_min_pillar._NONZERO_OK,
                      "wave-verify is a refusal verb on the no-wave lifecycle board")
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match the re-aimed engine_pin.ENGINE_MD5")


if __name__ == "__main__":
    unittest.main()
