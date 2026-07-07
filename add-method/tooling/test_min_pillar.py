#!/usr/bin/env python3
"""Behavioral proof of the Minimal pillar (task: minimalism-audit, milestone v2).

FINDING-A: the book claims "the Story is never auto-loaded" (01-principles.md; the
ETH-Zurich auto-context note in add.py). That claim was WRITTEN but UNPROVED —
`test_two_surface` only pins the prose string, so a regression that made a command
read a docs/ chapter would not turn any test red (it fails the circularity bar).

These tests pin the BEHAVIOR, not the words:
  - docs-absent : a project with no docs/ at all runs the whole lifecycle -> Story is
                  not REQUIRED at runtime.
  - read-spy    : no command's read_text resolves under a docs/ dir -> Story is not
                  READ at runtime. This is the non-vacuity guard: inject a docs/ read
                  into any command and this test goes red (verified during build, then
                  reverted).
  - coverage    : LIFECYCLE (+ init) covers EVERY subcommand the parser exposes, so
                  the read-spy's "no command" claim is universal, not a subset. A new
                  subcommand fails this until it is classified (exercised or excluded).

Assumption (worth knowing if a regression slips past): the spy patches only
Path.read_text. Every read site in add.py uses read_text today; a future read via
open(p).read() would evade the guard.
Run: python3 -m unittest test_min_pillar -v
"""
import argparse
import os
import pathlib
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. The new-milestone template ships one unchecked placeholder box; a census
    that drives a milestone to close must satisfy it first (the contracted instrument
    reaction). Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")

# The FULL public surface: every subcommand `add.py` exposes, driven in one valid
# order, so the read-spy below observes EVERY command — not a convenient subset.
# (`guide` is included on purpose: it only PRINTS chapter pointers, it must not read
# them. `sync-guidelines` reads AGENTS.md/CLAUDE.md — State at the project root, never
# a docs/ chapter.) `init` is the one command not here: it runs in setUp, and the
# docs-absent assertion fires immediately after it. test_every_subcommand_is_covered
# proves this list (plus init) equals the parser's whole command set — so a NEW
# subcommand fails that test until it is classified here.
LIFECYCLE = [
    ["lock", "--force"],                       # setup lock-down: reads/writes state.json, never docs/
                                               # (--force: a plain-init project is grandfathered-locked)
    ["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"],
    ["milestone-confirm", "mvp"],              # confirm-parent gate (opt-in): the human gate that
                                               # opens new-task for mvp — here mvp was created without
                                               # --await-confirm (no key, grandfathered), so this is an
                                               # idempotent confirm that exercises the verb (reads/writes
                                               # state, never docs/)
    ["new-task", "t", "--title", "Feature"],   # auto-linked to mvp
    ["autonomy"],                              # read-only dial view of active task t (reads TASK/PROJECT/state, never docs/)
    ["streams"],                               # read-only run-mode streams view (persist-run-mode): reads PROJECT.md, never docs/
    ["todo", "a captured idea"],               # backlog capture (todo-capture): appends state["todos"], never docs/
    ["whoami"],                                # read-only actor resolve (git config -> OS user; reads state, never docs/)
    ["assign", "t"],                            # ownership writer: set owner+assignee on t to self (reads/writes state, never docs/)
    ["unassign", "t"],                          # ownership writer: clear owner+assignee on t (reads/writes state, never docs/)
    ["status"],
    ["guide"],
    ["stage", "mvp"],
    ["set-milestone", "t", "none"], ["set-milestone", "t", "mvp"],
    ["use", "t"],                              # set active_task to an existing slug (read/writes state, not docs/)
    ["activate", "mvp"],                        # multi-active SET writer: mvp already active -> idempotent refocus (reads/writes state, never docs/)
    ["deactivate", "mvp"],                      # multi-active SET writer: drop mvp from the active set (pops its task entry; reads/writes state, never docs/)
    ["use", "t"],                              # re-focus t -> milestone-aware use re-activates mvp + restores active_task for the rest of the run
    ["phase", "specify", "t"],
    ["advance", "t"], ["advance", "t"], ["advance", "t"],
    ["advance", "t"], ["advance", "t"],        # specify -> ... -> verify
    ["heal", "t", "--reason", "lifecycle: a reported earned-green cheat"],  # bounded self-heal:
                                               # the semantic entry — returns t to build (exit 3,
                                               # tolerated), exercised under the read-spy (reads
                                               # state/TASK.md, never docs/)
    ["advance", "t"],                          # heal returned t to build; advance back to verify
    ["audit"],                                 # read-only seam audit (no recorded seams yet ->
                                               # clean exit 0; reads TASK.md/state, never docs/)
    ["gate", "PASS", "t"],
    ["reopen", "t", "--to", "verify", "--reason", "census"],  # done -> verify (recorded, gate reset)
    ["gate", "PASS", "t"],                                    # re-complete so milestone-done stays valid
    ["status"],
    ["check"],
    ["doctor"],                                # read-only state.json integrity diagnosis (reads
                                               # state only, never docs/; healthy board -> exit 0)
    ["mine"],                                  # read-only per-actor lens across active milestones
                                               # (reads state only, never docs/; empty -> exit 0)
    ["wave-verify"],                           # merge-time fork-base gate: read-only; no WAVE.md
                                               # on this board -> wave_not_found (expected nonzero,
                                               # tolerated below; reads WAVE.md/state, never docs/)
    ["ready"],
    ["waves"],                                 # read-only DAG schedule of the active milestone
                                               # (reads state only, never docs/; mvp is active so exit 0)
    ["dag-plan"],                              # record-only DAG-plan snapshot of the active milestone
                                               # (persist-dag-plan): reads state, writes the dag-plan.json
                                               # under the milestone dir, never docs/; mvp active -> exit 0
    ["guide", "t"],
    ["report"], ["report", "mvp"],             # read-only dashboard (reads MILESTONE/TASK, not docs/)
    ["deltas"],                                # read-only: open competency deltas report
    ["compact-foundation", "--propose"],       # read-only: settled-line preview (delta-drain)
    ["drop-delta", "t"],                       # SPEC-delta dismiss verb: task t holds no open
                                               # SPEC delta here -> refuses no_open_spec_delta
                                               # (expected nonzero, tolerated; reads TASK.md, never docs/)
    ["carry-delta", "t", "--reason", "x"],     # SPEC-delta defer verb: task t holds no open SPEC
                                               # delta here -> refuses no_open_spec_delta
                                               # (expected nonzero, tolerated; reads TASK.md, never docs/)
    ["reopen-delta", "t"],                      # SPEC-delta re-activate verb: task t holds no carried
                                               # SPEC delta here -> refuses no_carried_spec_delta
                                               # (expected nonzero, tolerated; reads TASK.md, never docs/)
    ["freeze", "t"],                           # §3 contract-freeze write-seam: task t's §3 is still
                                               # the unfilled template here -> refuses contract_not_drafted
                                               # (expected nonzero, tolerated; reads TASK.md/state, never docs/)
    ["re-cross", "t", "--by", "Tester"],       # post-freeze re-cross verb: t is done at this slot,
                                               # not build/verify -> refuses recross_wrong_phase
                                               # (expected nonzero, tolerated; reads TASK.md/state, never docs/)
    ["worktree-prep", "t"],                    # spawn-isolation prep: this board is not a git repo
                                               # -> refuses worktree_prep_no_git (expected nonzero,
                                               # tolerated; reads state + runs git only, never docs/)
    ["fold"],                                  # consolidation verb: this board has no open competency
                                               # lesson -> refuses no_open_deltas (expected nonzero,
                                               # tolerated; reads TASK/PROJECT/CONVENTIONS, never docs/)
    ["federate", "pull", "x"],                 # multi-repo pull verb: this board declares no
                                               # [federation.x] -> refuses federation_unknown (expected
                                               # nonzero, tolerated; reads components.toml, never docs/)
    ["components"],                             # registry reader/validator: this board has no
                                               # components.toml -> friendly single-component no-op,
                                               # exit 0 (reads components.toml, never docs/)
    ["search", "mvp"],                          # read-only keyword/substring corpus scan
                                               # (context-search, search-index): scans
                                               # MILESTONE.md/TASK.md title/goal/rationale
                                               # or title/Feature lines only, never docs/;
                                               # always exit 0 (matches or "no matches for:")
    ["graduation-report"], ["graduation-report", "--json"],  # read-only harvest (reads TASK/RETRO/state, never docs/)
    ["release-report"], ["release-report", "--json"],  # read-only release inventory (reads state/RELEASES.md/TASK, never docs/)
    ["release", "0.0.0"],                      # guarded record-only cut: no milestone is closed yet
                                               # here -> refuses release_no_closed_milestone (expected
                                               # nonzero, tolerated below; reads state/RELEASES.md, never docs/)
    ["project"],                               # read-only: prints PROJECT.md, reads no docs/ chapter
    ["sync-guidelines"],
    ["milestone-done", "mvp"],
    ["archive-milestone", "mvp"],              # mvp is done by now -> archivable
    ["compact", "mvp"],                        # heavy archive: moves the archived files
                                               # (reads TASK.md/state for the delta scan, never docs/)
]

# init runs in setUp (it refuses to re-run on an existing project), so it is exercised
# under the docs-absent assertion rather than inside LIFECYCLE.
_EXERCISED_IN_SETUP = {"init"}

# heal is a loop/refusal verb (heal-then-escalate): a CONFIRMED cheat never completes with
# exit 0 — it returns to build (exit 3) or escalates (exit 1). The lifecycle exercises it
# (proving it reads no docs/ chapter) and tolerates its expected non-zero exit.
# wave-verify is likewise a refusal verb on this board: no WAVE.md exists, so the
# merge-time gate refuses (wave_not_found) — exercised under the read-spy, nonzero tolerated.
# release is guarded: no closed-unreleased milestone exists at its lifecycle slot, so it refuses
# (release_no_closed_milestone) — exercised under the read-spy (reads state/RELEASES.md, never docs/).
# drop-delta is a refusal verb on this board: task t holds no open SPEC delta, so it refuses
# (no_open_spec_delta) — exercised under the read-spy (reads TASK.md/state, never docs/).
# fold is likewise a refusal verb here: no open competency lesson exists, so it refuses
# (no_open_deltas) — exercised under the read-spy (reads TASK/PROJECT/CONVENTIONS, never docs/).
# federate is a refusal verb on this board: no [federation.x] is declared, so `federate pull x`
# refuses (federation_unknown) — exercised under the read-spy (reads components.toml, never docs/).
# freeze is a refusal verb here: task t's §3 is still the unfilled template, so `freeze t`
# refuses (contract_not_drafted) — exercised under the read-spy (reads TASK.md/state, never docs/).
_NONZERO_OK = {"heal", "wave-verify", "release", "drop-delta", "carry-delta", "reopen-delta",
               "fold", "federate", "freeze", "re-cross", "worktree-prep"}


class MinimalPillarTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-min-pillar-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _freeze(self, slug):
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _docs_dirs(self):
        return list(Path(self.tmp).rglob("docs"))

    def test_full_lifecycle_runs_with_no_story(self):
        # init scaffolds no book; the Story is referenced by path, never installed.
        self.assertEqual(self._docs_dirs(), [], "init must not scaffold a docs/ Story")
        for argv in LIFECYCLE:
            if argv[:2] == ["milestone-done", "mvp"]:
                _meet_exit_criteria("mvp")   # v20 goal-gate: meet criteria before close
            try:
                add.main(argv)
            except SystemExit as e:
                if e.code and argv[0] not in _NONZERO_OK:
                    self.fail(f"command {argv} failed (exit {e.code}) with no Story present")
            if argv[0] == "new-task":
                self._freeze(argv[1])  # freeze-gate-universal: stamp §3 FROZEN after task creation
        # the flow completing never created a Story either
        self.assertEqual(self._docs_dirs(), [], "no command may create a docs/ Story")

    def test_no_command_reads_a_docs_chapter(self):
        # Spy on every read_text during the whole lifecycle; assert none resolves
        # under a 'docs' directory. Goes red the moment a command auto-loads Story.
        orig = pathlib.Path.read_text
        reads: list[str] = []

        def spy(self, *a, **k):
            reads.append(str(self))
            return orig(self, *a, **k)

        pathlib.Path.read_text = spy
        try:
            for argv in LIFECYCLE:
                if argv[:2] == ["milestone-done", "mvp"]:
                    _meet_exit_criteria("mvp")   # v20 goal-gate: meet criteria before close
                try:
                    add.main(argv)
                except SystemExit as e:
                    if e.code and argv[0] not in _NONZERO_OK:
                        self.fail(f"command {argv} failed during read-spy (exit {e.code})")
                if argv[0] == "new-task":
                    self._freeze(argv[1])  # freeze-gate-universal: stamp §3 FROZEN after task creation
        finally:
            pathlib.Path.read_text = orig

        story_reads = [p for p in reads if "docs" in Path(p).parts]
        self.assertEqual(story_reads, [],
                         f"a command auto-loaded the Story (read under docs/): {story_reads}")
        self.assertTrue(reads, "the spy must have observed reads (else it caught nothing)")

    def test_every_subcommand_is_covered(self):
        # Self-maintaining guard: the read-spy claim is "NO command reads a docs/
        # chapter", so the spy must run EVERY command. Derive the full command set
        # from the parser and assert LIFECYCLE (+ init in setUp) covers it exactly.
        # A new subcommand fails here until it is added to LIFECYCLE — closing the
        # gap where the claim is universal but the proof is a subset.
        parser = add.build_parser()
        sub = [a for a in parser._actions
               if isinstance(a, argparse._SubParsersAction)][0]
        all_cmds = set(sub.choices)
        covered = _EXERCISED_IN_SETUP | {argv[0] for argv in LIFECYCLE}
        self.assertEqual(
            all_cmds - covered, set(),
            f"subcommand(s) never run under the read-spy: {sorted(all_cmds - covered)}")
        self.assertEqual(
            covered - all_cmds, set(),
            f"LIFECYCLE names a command the parser does not expose: {sorted(covered - all_cmds)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
