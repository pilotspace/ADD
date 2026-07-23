════════════════════════════════════════════════════════════════════════
 persona-gepa-loop · Persona GEPA loop — routes that learn from run outcomes
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  2/2 met
 GATES     1 PASS             WAIVERS   none

 goal  The persona's routing rules EVOLVE from evidence — every gated
       task records a route-outcome trace (route taken · turns · heals ·
       gate result), and at fold-time the PM persona reflects on the
       traces GEPA-style, proposing route-rule deltas (keep what cut
       turns without gate regressions, prune rules that never fired)
       that the human folds into the persona file — the method literally
       improves per project.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 route-scoreboard            done      PASS 0     ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   route-scoreboard         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS      none

 SPEC DELTAS    46 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone
              persona-gepa-loop
              2 planned not yet scaffolded: route-scoreboard ·
              persona-rollup
════════════════════════════════════════════════════════════════════════