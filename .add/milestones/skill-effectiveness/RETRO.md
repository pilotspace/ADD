════════════════════════════════════════════════════════════════════════
 skill-effectiveness · lean-pass M1 · skill effectiveness
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  5/5 met
 GATES     4 PASS             WAIVERS   none

 goal  every skill guide is the most effective prompt for its job —
       clearer routing, sharper decisions, same flow and engine behavior
       — at materially lower token cost
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 skill-core-compact          done      PASS 0     ●●●●●●●●●
 orchestration-fold          done      PASS 0     ●●●●●●●●●
 phase-guides-trim           done      PASS 0     ●●●●●●●●●
 reference-trim              done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   skill-core-compact       PASS Tin Dang <tindang.ht97@gmail.com>
   orchestration-fold       PASS Tin Dang <tindang.ht97@gmail.com>
   phase-guides-trim        PASS Tin Dang <tindang.ht97@gmail.com>
   reference-trim           PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (5 carried)
   • ADD · open · a token-reduction TARGET can collide with the
     effectiveness floor; the honest resolution is a human-approved
     change-request that re-specs the number, NEVER weakening the test
     or gutting the prompt (evidence: v1 ≥25% re-specced to ≥12% on
     build evidence; full suite stayed green).
   • ADD · open · the tamper tripwire fires when a frozen §3 + red test
     are edited in place at verify — even for a LEGITIMATE re-spec; the
     method-correct flow is to re-cross tests→build so the snapshot
     re-takes cleanly (evidence:
     `tamper_detected:contract_tampered,build_tampered` → `phase
     tests`→`advance`×2 cleared it; `reopen` is for DONE tasks only).
   • SDD · open · the suite IS the behavior contract for a prose
     compaction — 2 wording slips ("Tie-break order", "never the
     artifact") were caught only by the FULL suite, not the 33-subset
     (evidence: gate-on-full-suite mitigation paid off).
   • ADD · open · a 25% pure-compaction tends to land EQUIVALENT, not
     CLEARER — the realistic effectiveness bar for already-tight guides
     is "no rule/nuance lost + leaner", and a quality-review subagent
     reliably surfaces the dropped sidebars to restore (evidence: review
     flagged 5, all restored, suite stayed green).
   • ADD · open · test-pinned per-phase guides have an effectiveness
     floor like the always-loaded core — set the target at the realistic
     ceiling (20%) UP-FRONT with rationale, rather than freezing 25% and
     re-speccing after build (saves the tamper/reopen cycle); the
     tree-wide 25% is carried by the load-on-demand reference pool
     (evidence: 20% hit cleanly, CLEARER, no re-spec needed).

 SPEC DELTAS    38 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              skill-effectiveness
════════════════════════════════════════════════════════════════════════