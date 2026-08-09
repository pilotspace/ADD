════════════════════════════════════════════════════════════════════════
 v13-1 · Report hardening
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  4/4 met
 GATES     3 PASS             WAIVERS   none

 goal  close v13's disclosed residue: declaration grammar stated,
       declared paths confined, DECIDE NEXT plan-aware

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 declare-grammar-doc         done      PASS 5†    ●●●●●●●●
 declared-path-confinement   done      PASS 7†    ●●●●●●●●
 decide-planned-hint         done      PASS 7†    ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (5 carried)
   • TDD · folded · a scaffold-template change is testable BEHAVIORALLY,
     not just by file anchors — run the scaffolder in a tmp project and
     assert the generated artifact carries the change (evidence:
     test_scaffold_carries_grammar caught nothing extra this time, but
     pins the template→scaffold copy path that a pure file-anchor test
     would miss)
   • ADD · folded · the security-line-always-escalates rule works in
     practice and is CHEAP — the note (resolve() metadata touch) took
     one question to adjudicate; writing the nuance on the line instead
     of self-clearing it kept the human gate honest (evidence: this
     task's GATE RECORD, first escalation since the rule was folded at
     foundation-version 11)
   • SDD · folded · pathlib absolute-join is a quiet escape hatch —
     `root / "/abs"` IS `/abs`; any future path-resolving seam should
     name absolute tokens explicitly in its contract (evidence:
     test_absolute_token_zero was red pre-build, the hole was live in
     v1)
   • TDD · folded · a fixture that REUSES the scaffolded template
     inherits its example rows — the first red run counted the
     template's "User can…" exit criterion as a planned task; scope a
     prose parser to its section and make a guard of the template's own
     placeholders (evidence: phantom "User" slug in the first red run,
     fixed by ## Tasks scoping)
   • ADD · folded · a convention can be written to RETIRE:
     foundation-v11's decide-next cross-check named its own sunset
     condition ("until the engine grows a hint"), making the fold-out
     decision mechanical once this task shipped (evidence: this task +
     the v11 convention text)

 DECIDE NEXT  fold learnings + archive-milestone v13-1
════════════════════════════════════════════════════════════════════════