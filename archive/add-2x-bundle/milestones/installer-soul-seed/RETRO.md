════════════════════════════════════════════════════════════════════════
 installer-soul-seed · Installer seeds SOUL.md on install and update
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  1/1 met
 GATES     1 PASS             WAIVERS   none

 goal  When ADD is installed or updated, .add/SOUL.md is seeded from the
       bundled template if it does not yet exist — so the voice file is
       present from the first session without waiting for add.py init.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 soul-seed-on-install        done      PASS 5†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 1/1 met

 LEARNINGS      none

 SPEC DELTAS    13 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              installer-soul-seed
════════════════════════════════════════════════════════════════════════