════════════════════════════════════════════════════════════════════════
 engine-minimalism · Engine output diet — cut add.py's re-read cache weight
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  3/3 met
 GATES     2 PASS             WAIVERS   none

 goal  Reduce the engine_output share of an ADD run's cache-read (WM1
       baseline 38.4% / 5.48M residency-weight) by trimming the
       highest-residency add.py command outputs (--help, default status,
       new-task/init orientation) without losing the resume point,
       next-call hint, or guide pointer the AI needs, re-measured by the
       token_anatomy harness.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 help-diet                   done      PASS 0     ●●●●●●
 status-brief-adoption       done      PASS 0     ●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   help-diet                PASS Tin Dang <tindang.ht97@gmail.com>
   status-brief-adoption    PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS      none

 SPEC DELTAS    29 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              engine-minimalism
              1 planned not yet scaffolded: orient-diet
════════════════════════════════════════════════════════════════════════