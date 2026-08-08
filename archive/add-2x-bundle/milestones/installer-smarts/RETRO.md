════════════════════════════════════════════════════════════════════════
 installer-smarts · Smart onboarding installer
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  5/5 met
 GATES     4 PASS             WAIVERS   none

 goal  On first run in a real terminal, add init onboards the user
       (brand, feature showcase, readiness, global-first scope, optional
       intent handoff to /add) instead of a silent file-drop;
       non-interactive/CI stays byte-identical.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 onboarding-brand            done      PASS 10†   ●●●●●●●●●
 readiness-and-detect        done      PASS 14†   ●●●●●●●●●
 global-first-scope          done      PASS 8†    ●●●●●●●●●
 intent-handoff              done      PASS 11†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS      none

 SPEC DELTAS    14 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              installer-smarts
════════════════════════════════════════════════════════════════════════