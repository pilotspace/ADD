════════════════════════════════════════════════════════════════════════
 ownership-assignment · Ownership & assignment
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  2/2 met
 GATES     2 PASS             WAIVERS   none

 goal  a user can assign an owner and assignee to any task or milestone
       (to self or a named actor) and SEE who owns and works what in
       status and report — descriptive only, unassigned records
       unchanged
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 ownership-model             done      PASS 0     ●●●●●●●●●
 ownership-surface           done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   ownership-model          PASS Tin Dang <tindang.ht97@gmail.com>
   ownership-surface        PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (3 carried)
   • TDD · open · when a parser NORMALIZES input (extracts a name from
     `"<...>"`), validate the PARSED value, not the raw arg — a raw
     `.strip()` check let `--owner "<>"` write a blank name (evidence:
     review BLOCK on ownership-model; the red test only covered raw
     whitespace, missing the parsed-empty case).
   • DDD · open · "owner/assignee" (mutable, directive) is a genuinely
     distinct concept from the "actor stamp" (immutable, historical)
     even though they share the `{name,email,source}` shape — a new
     `source:"assigned"` value marks human-typed provenance vs
     git/os/override resolution (evidence: ownership-model reused the
     shape but needed the 4th source value to stay honest).
   • ADD · open · a second record-typed field that shares the actor
     `{name,email,source}` shape (owner/assignee, after
     gate_actor/done_actor) confirmed a reusable surface pattern: one
     `_fmt_actor` + a thin per-feature `_fmt_*` wrapper + a present-only
     render guard — adding a surface is now a 3-edit recipe (report_data
     row + render block + status line) (evidence: ownership-surface
     reused identity-in-status's exact shape with zero new primitives).

 SPEC DELTAS    26 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              ownership-assignment
════════════════════════════════════════════════════════════════════════