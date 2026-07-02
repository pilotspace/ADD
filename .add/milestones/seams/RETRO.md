════════════════════════════════════════════════════════════════════════
 seams · Seams
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  2/2 met
 GATES     5 PASS             WAIVERS   none

 goal  Promote symbols ≥2 tasks touch into a milestone-level SEAMS.md
       that §0 references, so a shared contract has one home instead of
       being re-derived per task.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 seams-doc                   done      PASS 15†   ●●●●●●●●●
 seams-template-wiring       done      PASS 0     ●●●●●●●●●
 fix-flag-fence-aware        done      PASS 2712† ●●●●●●●●●
 status-task-filter          done      PASS 0     ●●●●●●●●●
 seam-term-carveout          done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   seams-doc                PASS Tin Dang <tindang.ht97@gmail.com>
   seams-template-wiring    PASS Tin Dang <tindang.ht97@gmail.com>
   fix-flag-fence-aware     PASS Tin Dang <tindang.ht97@gmail.com>
   status-task-filter       PASS Tin Dang <tindang.ht97@gmail.com>
   seam-term-carveout       PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (3 carried)
   • TDD · open · a shape-only test suite (asserts field ORDER +
     kebab-case-shaped strings) went 15/15 green while shipping a
     factual defect (a Citations example that doesn't actually match its
     own entry's stated grep method) — the assert validated the SHAPE of
     "≥2 named examples" but never that the examples are genuine; a
     spot-checked scenario (only 1 of 5 entries got a live re-run) is
     not equivalent to full coverage of a mechanically-checkable claim
     (evidence: `phase-body-extraction`'s `extract-predicates`
     misattribution, caught only by the verify agent's independent
     re-run of all 5, not by the build's own green suite)
   • ADD · open · running two `add-build` agents in parallel in the same
     working tree (no worktree isolation) caused a real anchor drift
     mid-build and a scope-lock false-positive at gate time — recovered
     both times via the established `phase tests`→`phase
     build`→`advance` re-cross (evidence: `_declared_scope`'s line
     number shifted mid-build from `search-index`'s concurrent edit to
     `add.py`; `add.py gate PASS` rejected once with `scope_violation:
     ... test_min_pillar.py`, a file entirely inside `search-index`'s
     own declared Scope, not this task's)
   • ADD · open · a milestone's own seed research should be treated as a
     strong LEAD, not ground truth, and "verify, don't trust" needs to
     apply recursively at every stage, not just once at grounding
     (evidence: this task's build+verify stages together overturned 3 of
     5 seed numbers from the milestone AND found one further defect, a
     misattributed Citations example, that had survived into the frozen
     contract itself)

 SPEC DELTAS    18 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone seams
════════════════════════════════════════════════════════════════════════