#!/usr/bin/env python3
"""Behavioral proof of `add.py graduation-report` (task: graduation-analytics, v22).

CONTRACT (frozen @ v1): a READ-ONLY subcommand that GATHERS the MVP loop's evidence into
FIVE labeled record-sets — open_deltas · waivers · retros · residue_gates · residue_disclosed
· coverage_gaps (+ summary) — and JUDGES nothing (no readiness/score/ranking/theme anywhere).
  - text + `--json`; exit 0 ALWAYS (a gather, not a gate); only `_require_root` dies (no_project).
  - waivers sorted by expiry soonest-first; a RISK-ACCEPTED is ONE record's two facets
    (waivers[] expiry-facet + residue_gates[] residue-class-facet), never two findings.
  - two tiers: LIVE (in-state) fine-grained; CONSOLIDATED (compacted) = RETRO record only,
    with the boundary stated (summary.milestones_consolidated). No silent cap.
  - residue_disclosed = in-state §6 `- [⚠]` list items. coverage_gaps = §7 Watch still "<error rate".
  - read-only: state.json + every file byte-identical; no file written; unreadable source skipped.

RED until `graduation-report` exists (today argparse rejects the subcommand → non-zero exit).
Run from repo root:
  PYTHONPATH=add-method/tooling python3 -m unittest test_graduation_report -v
"""
import contextlib
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

STATE = Path(".add/state.json")
PROJECT = Path(".add/PROJECT.md")
# judgment tokens the gather must NEVER emit (case-insensitive) — gather-not-judge invariant
FORBIDDEN = ("readiness", "recommend", "ranking", "verdict", "score")


def _run(argv):
    """Run add.main(argv) in the temp project, capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _load() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8"))


def _save(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def _make_task(slug, milestone="v1", phase="done", gate="PASS",
               delta=None, residue_line=None, watch=None, waiver=None):
    """Precondition seeding: write an in-state task's TASK.md AND register it in state.json
    (the real post-build shape). `delta` is a full `[COMP · open] text (evidence: e)` body;
    `watch` defaults to the unfilled placeholder; `waiver` forces gate=RISK-ACCEPTED."""
    d = Path(".add/tasks") / slug
    d.mkdir(parents=True, exist_ok=True)
    watch_val = watch if watch is not None else "<error rate / per-rejection rate / latency>"
    body = [
        f"# TASK: {slug}", "", f"slug: {slug}", f"phase: {phase}", "",
        "## 6 · VERIFY", "",
        (f"- [⚠] {residue_line}" if residue_line else "- [x] all tests pass"), "",
        "## 7 · OBSERVE", "",
        f"Watch (reuse scenarios as monitors): {watch_val}", "",
        "### Competency deltas", "",
        (f"- {delta}" if delta else ""),
    ]
    (d / "TASK.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    s = _load()
    t = {"milestone": milestone, "phase": phase, "gate": gate, "title": slug}
    if waiver:
        t["waiver"] = waiver
        t["gate"] = "RISK-ACCEPTED"
    s.setdefault("tasks", {})[slug] = t
    s.setdefault("milestones", {}).setdefault(milestone, {"status": "active", "title": milestone})
    _save(s)


def _make_retro(mslug, carried=0, archived=False, bak_waiver=None):
    """Write a RETRO.md (live under milestones/, or consolidated under archive/). When archived,
    register the milestone in state['archived'] and optionally drop a structured .bak waiver
    (which the live harvest must NOT surface — archived_summarized)."""
    base = Path(".add/archive" if archived else ".add/milestones") / mslug
    base.mkdir(parents=True, exist_ok=True)
    (base / "RETRO.md").write_text(
        f"RETRO {mslug}\n\n LEARNINGS ({carried} carried)\n", encoding="utf-8")
    if archived:
        s = _load()
        s.setdefault("archived", []).append({
            "slug": mslug, "title": mslug, "tasks": 1, "task_slugs": [f"{mslug}-t"],
            "archived": "2026-01-01", "compacted": "2026-01-02"})
        _save(s)
        if bak_waiver:
            (base / "pre-archive-state.bak.json").write_text(json.dumps(
                {"milestone": {"status": "done"},
                 "tasks": {f"{mslug}-t": {"gate": "RISK-ACCEPTED", "waiver": bak_waiver}}},
                indent=2), encoding="utf-8")


class GraduationReportTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-grad-report-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "v1", "--goal", "ship the core loop"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- Must -------------------------------------------------------------
    def test_emits_five_record_sets(self):                                   # M2
        _make_task("t-delta", delta="[DDD · open] missed a case (evidence: scn_x)")
        _make_task("t-waiver", waiver={"owner": "o", "ticket": "T-1", "expires": "2026-09-01"})
        _make_task("t-residue", residue_line="concurrency residue carried to gate")
        _make_task("t-gap", watch="<error rate / per-rejection rate / latency>")
        _make_retro("v1", carried=2)
        code, out, _ = _run(["graduation-report"])
        self.assertEqual(code, 0)
        low = out.lower()
        for label in ("open deltas", "waiver", "retro", "residue", "coverage"):
            self.assertIn(label, low, f"the {label!r} record-set must be labeled in the text")
        for bad in FORBIDDEN:
            self.assertNotIn(bad, low, f"gather-not-judge: must not emit {bad!r}")

    def test_exit_zero_always(self):                                         # M1
        for i in range(3):
            _make_task(f"t{i}", delta=f"[TDD · open] lesson {i} (evidence: e{i})",
                       waiver={"owner": "o", "ticket": f"T-{i}", "expires": "2026-1%d-01" % (i + 1)})
        heavy, _, _ = _run(["graduation-report"])
        self.assertEqual(heavy, 0, "heavy evidence still exits 0 (a gather, not a gate)")
        # a project with no accumulated evidence: still exit 0
        empty_dir = tempfile.mkdtemp(prefix="add-grad-empty-")
        self.addCleanup(shutil.rmtree, empty_dir, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(empty_dir)
        add.main(["init", "--name", "empty"])
        empty, _, _ = _run(["graduation-report"])
        os.chdir(self.tmp)
        self.assertEqual(empty, 0, "no evidence still exits 0")

    def test_json_one_object_keyed(self):                                    # M5
        _make_task("t1", delta="[ADD · open] x (evidence: y)")
        _make_retro("v1", carried=1)
        code, out, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)                                  # one valid object, nothing else
        for key in ("open_deltas", "waivers", "retros", "residue_gates",
                    "residue_disclosed", "coverage_gaps", "summary"):
            self.assertIn(key, obj, f"--json must carry the {key!r} record-set")

    def test_waivers_sorted_by_expiry(self):                                 # M2b
        _make_task("t-late", waiver={"owner": "o", "ticket": "L", "expires": "2026-12-01"})
        _make_task("t-soon", waiver={"owner": "o", "ticket": "S", "expires": "2026-07-01"})
        code, out, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        waivers = json.loads(out)["waivers"]
        self.assertEqual([w["expires"] for w in waivers][:2], ["2026-07-01", "2026-12-01"],
                         "waivers must sort by expiry, soonest first")

    def test_risk_accepted_two_facets(self):                                 # M2d (⚠#2)
        _make_task("t-ra", waiver={"owner": "o", "ticket": "T-9", "expires": "2026-08-01"})
        code, out, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        self.assertIn("t-ra", [w["slug"] for w in obj["waivers"]], "expiry facet")
        self.assertIn("t-ra", [g["slug"] for g in obj["residue_gates"]], "residue-class facet")
        # counted independently per list — never summed into one combined risk number
        self.assertEqual(obj["summary"]["waivers"], 1)
        self.assertEqual(obj["summary"]["residue_gates"], 1)

    def test_two_tiers_boundary_stated(self):                                # M3
        _make_task("t-live", delta="[SDD · open] live lesson (evidence: z)")
        _make_retro("v1", carried=1)                          # live RETRO
        _make_retro("vA", carried=3, archived=True)           # consolidated (compacted) RETRO
        code, out, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        tiers = {r["milestone"]: r["tier"] for r in obj["retros"]}
        self.assertEqual(tiers.get("vA"), "consolidated", "compacted milestone -> consolidated tier")
        self.assertGreaterEqual(obj["summary"]["milestones_consolidated"], 1,
                                "the compacted boundary must be stated (no silent cap)")

    def test_coverage_gaps_proxy(self):                                      # M2e
        _make_task("t-placeholder")                            # default Watch = "<error rate ...>"
        _make_task("t-filled", watch="latency < 200ms; error rate < 1%")  # filled, uses '<' as less-than
        code, out, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        gaps = [g["slug"] for g in json.loads(out)["coverage_gaps"]]
        self.assertIn("t-placeholder", gaps, "unfilled Watch -> monitor not declared")
        self.assertNotIn("t-filled", gaps, "a filled monitor using '<' must not false-positive")

    def test_read_only(self):                                               # M4
        _make_task("t1", delta="[UDD · open] q (evidence: r)",
                   waiver={"owner": "o", "ticket": "T", "expires": "2026-10-01"})
        _make_retro("v1", carried=1)
        watched = [STATE, PROJECT, Path(".add/tasks/t1/TASK.md"), Path(".add/milestones/v1/RETRO.md")]
        before = {p: _md5(p) for p in watched}
        n_before = sum(1 for _ in Path(".add").rglob("*"))
        _run(["graduation-report"])
        _run(["graduation-report", "--json"])
        for p in watched:
            self.assertEqual(_md5(p), before[p], f"{p} must be byte-identical (read-only)")
        self.assertEqual(sum(1 for _ in Path(".add").rglob("*")), n_before,
                         "graduation-report must write no file")

    # ---- Reject (each asserts what stays unchanged) -----------------------
    def test_no_project(self):                                              # no_project
        clean = tempfile.mkdtemp(prefix="add-grad-noproj-")   # OUTSIDE any .add/ tree
        self.addCleanup(shutil.rmtree, clean, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(clean)
        before = sorted(os.listdir(clean))
        code, _, err = _run(["graduation-report"])
        os.chdir(self.tmp)
        self.assertNotEqual(code, 0, "no project -> non-zero exit")
        self.assertIn("no_project", err)
        self.assertEqual(sorted(os.listdir(clean)), before, "no file created")

    def test_unreadable_source_skipped(self):                              # source_unreadable
        _make_task("t1", delta="[DDD · open] keep (evidence: e)")
        _make_retro("v1", carried=1)                          # readable retro
        (Path(".add/milestones/vBad")).mkdir(parents=True, exist_ok=True)
        (Path(".add/milestones/vBad/RETRO.md")).mkdir()       # a DIRECTORY at a RETRO path
        before = _md5(STATE)
        code, out, err = _run(["graduation-report"])
        self.assertEqual(code, 0, "an unreadable source must not crash the report")
        self.assertNotIn("Traceback", err)
        self.assertIn("open deltas", out.lower(), "the other record-sets still render")
        self.assertEqual(_md5(STATE), before, "state.json byte-identical")

    def test_archived_summarized(self):                                    # archived_summarized
        _make_retro("vArch", carried=4, archived=True,
                    bak_waiver={"owner": "ghost", "ticket": "OLD-1", "expires": "2026-12-31"})
        bundle = Path(".add/archive/vArch")
        before = {p: _md5(p) for p in bundle.rglob("*") if p.is_file()}
        code, out, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        self.assertNotIn("OLD-1", [w.get("ticket") for w in obj["waivers"]],
                         "an archived .bak waiver must NOT surface in the live fine-grained set")
        self.assertIn("vArch", [r["milestone"] for r in obj["retros"]],
                      "the compacted milestone appears as its RETRO record")
        for p, h in before.items():
            self.assertEqual(_md5(p), h, f"{p} archive bundle untouched")

    def test_never_readiness_verdict(self):                                # would_be_judging
        _make_task("t1", delta="[ADD · open] all (evidence: e)",
                   waiver={"owner": "o", "ticket": "T", "expires": "2026-09-09"})
        _make_retro("v1", carried=1)
        s = _load(); stage_before = s.get("stage"); state_md5 = _md5(STATE)
        _, text, _ = _run(["graduation-report"])
        code, js, _ = _run(["graduation-report", "--json"])
        self.assertEqual(code, 0)
        blob = (text + js).lower()
        for bad in FORBIDDEN:
            self.assertNotIn(bad, blob, f"no {bad!r} anywhere — the report decides nothing")
        self.assertEqual(_load().get("stage"), stage_before, "stage unchanged")
        self.assertEqual(_md5(STATE), state_md5, "state.json unchanged (the report decides nothing)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
