════════════════════════════════════════════════════════════════════════
 loop-steering · Loop Steering
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  4/4 met
 GATES     1 PASS             WAIVERS   none

 goal  make the dynamic loop GUIDED, not just gated: the orient surfaces
       an agent reads first (status, guide) must route into the loop
       when an active milestone's tasks are all done but its goal is
       unmet — today only report<ms> carries that cue
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 loop-aware-orient           done      PASS 9†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   loop-aware-orient        PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS      none

 SPEC DELTAS    43 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone loop-steering
════════════════════════════════════════════════════════════════════════