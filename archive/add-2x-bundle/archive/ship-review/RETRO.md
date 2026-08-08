════════════════════════════════════════════════════════════════════════
 ship-review · ship-review
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  4/4 met
 GATES     3 PASS             WAIVERS   none

 goal  at milestone close the AI fills a whole-milestone cross-task ship
       review (ship-by-domain manifest, per-task evidence, goal-met
       mapping) that the existing engine gate reads, and defines the
       milestone's release steps (merge is one small step) as hints in
       MILESTONE.md feeding release.md — no new gate, no new engine
       command, no new dependency

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 close-section-template      done      PASS 5     ●●●●●●●●●
 close-guide                 done      PASS 4     ●●●●●●●●●
 close-book-accord           done      PASS 4     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (7 carried)
   • TDD · open · a presence-only assertion can pass for the WRONG
     reason when the artifact already holds similar tokens — S4's first
     form leaned on the pre-existing `## Tasks` checkboxes (`whole_boxes
     > exit_boxes` was true before any build); pin the NEW artifact's
     contribution specifically (count Close+Release boxes), not a
     whole-file delta (evidence: S4 green-at-red until tightened)
   • ADD · open · the freeze flag must be PERSISTED in TASK.md §3 as
     `Least-sure flag surfaced at freeze:`, not only surfaced in chat —
     the `unflagged_freeze` guard blocks tests→build until the line
     exists (evidence: `advance` rejected with `unflagged_freeze`
     despite the flag being shown at the freeze report)
   • SDD · open · the wording-lint scans skill guides for bare
     status/process slang AND exempts code spans — the lifecycle
     `milestone-done → fold → compact → archive` must be backticked (as
     release.md does), not bare prose; a bare "fold" turned the full
     suite red (evidence: test_slang_absent_extended_surface term='fold'
     until the code-span reword)
   • ADD · open · "point, don't duplicate" between two guides is
     testable as a structural proxy — assert the pointer (the other file
     is named) AND the absence of the other file's distinctive tokens
     (its reject codes) — rather than trying to prove non-duplication
     directly (evidence: test_L2 design)
   • SDD · open · one glossary term touches 9 files across 3 sync
     regimes (book ×4 · template ×3 · dogfood ×1) and must be written in
     EACH type's native format (appendix `**T** — d` · template/dogfood
     `t: d`) — parity guards catch byte-divergence but the per-type
     FORMAT is a manual judgment the test must pin per type (evidence:
     test_B2 asserts format-by-type)
   • ADD · open · this milestone dogfooded itself — the ship-review
     machinery (template task 1 · guide task 2 · book task 3) is
     exercised by the milestone's OWN close, the honest first-lived-run
     pattern that proves the feature on its author (evidence: exit
     criterion 4 fills the very `## Close — ship review` section task 1
     shipped)
   • ADD · open · the §5 scope-gate caught a real declaration gap and is
     anchored at the tests→build crossing: a repo-root file needs the
     `add-method/../<file>` climb (a "/"-bearing FILE token — bare names
     resolve as siblings) and the wholesale `_bundled/` tree a single
     directory token; a §5 fix after build requires RE-CROSSING
     tests→build to re-anchor the snapshot (editing §5 alone is not
     picked up). Disclosed tradeoff: re-anchoring after the edits means
     that gate run re-diffs nothing — integrity here rests on the green
     suite + parity + tamper-tripwire, not the scope diff (evidence:
     scope_violation returned-to-build attempt 1→2 until the re-cross)

 DECIDE NEXT  consolidate learnings + archive-milestone ship-review
════════════════════════════════════════════════════════════════════════