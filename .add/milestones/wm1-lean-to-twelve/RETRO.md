════════════════════════════════════════════════════════════════════════
 wm1-lean-to-twelve · WM1 lean-to-twelve — kill the two measured freeze/scope call sinks
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  0/0 met
 GATES     4 PASS             WAIVERS   none

 goal  The WM1 loop's two 100%-reproducible call sinks die at the
       source: the first freeze no longer fails unflagged_freeze (the
       template carries a drafted-blank flag slot), and a zero-cover
       scope declaration is refused AT the freeze with a paste-ready fix
       (never surfacing later as scope_violation->re-cross). Earned when
       a fresh n=3 WM1 re-measure lands mean add.py calls <= 12 with
       fidelity held.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 freeze-flag-slot            done      PASS 4†    ●●●●
 scope-first-freeze          done      PASS 8†    ●●●●
 scope-walk-prune            done      PASS 5†    ●●●●
 egg-info-prune              done      PASS 2†    ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   freeze-flag-slot         PASS Tin Dang <tindang.ht97@gmail.com>
   scope-first-freeze       PASS Tin Dang <tindang.ht97@gmail.com>
   scope-walk-prune         PASS Tin Dang <tindang.ht97@gmail.com>
   egg-info-prune           PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ○○○○○○○○○○ 0/0 met

 LEARNINGS      none

 SPEC DELTAS    46 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone
              wm1-lean-to-twelve
════════════════════════════════════════════════════════════════════════