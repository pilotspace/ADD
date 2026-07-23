════════════════════════════════════════════════════════════════════════
 engine-hygiene · Engine hygiene: perf/dedup cleanup + wire milestone-relations
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  3/3 met
 GATES     2 PASS             WAIVERS   none

 goal  Land the value-dense engine cleanup a read-only sweep found —
       behavior-preserving perf hoists + duplication removal (cmd_check
       TOML re-reads/dead recompute, 5x snapshot-hash helper with
       unified exceptions, static-regex hoist, milestone-resolve DRY)
       and finish-wiring the never-surfaced _milestone_relations feature
       — with the existing ~3600-test fence as the safety net
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 wire-milestone-relations    done      PASS 0     ●●●●
 hygiene-bundle              done      PASS 0     ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   wire-milestone-relations PASS Tin Dang <tindang.ht97@gmail.com>
   hygiene-bundle           PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS      none

 SPEC DELTAS    46 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone engine-hygiene
════════════════════════════════════════════════════════════════════════