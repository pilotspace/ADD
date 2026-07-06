════════════════════════════════════════════════════════════════════════
 persona-domain-fit · Persona domain-fit nudge
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  1/1 met
 GATES     1 PASS             WAIVERS   none

 goal  a new milestone/task whose domain doesn't fit any existing
       project persona gets a concrete nudge to draft a fitting one, not
       just a one-time zero-personas nudge
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 persona-fit-nudge           done      PASS 24†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   persona-fit-nudge        PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 1/1 met

 LEARNINGS (2 carried)
   • ADD · open · a §5 Scope amendment made mid-build now has THREE
     known trigger shapes this session (a wrapped multi-line
     declaration, a Scope addition after tests→build crossed, and — new
     this task — an OUT-OF-DECLARED-SCOPE doc file, `.add/SEAMS.md`,
     whose pinned `path:line` anchor silently drifted from an EARLIER,
     in-scope edit elsewhere in the same file it anchors into, `add.py`)
     — the engine has no way to warn "this edit may invalidate a
     line-number anchor elsewhere in the docs," so the drift was caught
     only by a full-suite run, not by `add.py check` at build time
     (evidence: `test_seams_doc.py::test_every_anchor_resolves` only
     failed once the full 2967-test suite ran, well after the targeted
     slice had already gone green)
   • TDD · open · a broad substring-ban static-inspection test (banning
     "overlap" anywhere in add.py) produced a false positive against
     unrelated, pre-existing prose ("...only overlaps builds...") —
     narrowed to scan just the new function's body instead of the whole
     file; a static-inspection test should always scope its search to
     the code it's actually asserting about, not the whole source file
     (evidence: `test_no_content_heuristic_in_source` first FAILed for
     the wrong reason before being narrowed)

 SPEC DELTAS    6 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              persona-domain-fit
════════════════════════════════════════════════════════════════════════