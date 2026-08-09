════════════════════════════════════════════════════════════════════════
 portable-roster · Portable phase-roster for other coding agent tools
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  4/4 met
 GATES     2 PASS             WAIVERS   none

 goal  non-Claude coding tools receive the ADD phase-roster's roles and
       boundaries through the AGENTS.md the installer already drops
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 roster-portable-shape       done      PASS 10†   ●●●●●●●●●
 roster-onboarding-wiring    done      PASS 61†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   roster-portable-shape    PASS Tin Dang <tindang.ht97@gmail.com>
   roster-onboarding-wiring PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (3 carried)
   • SDD · open · the guideline block has TWO lean guards, not one —
     `test_guidelines` pins NO byte budget but
     `test_v8_onramp::test_block_stays_a_pointer` caps the WHOLE block
     at ≤22 non-blank lines (markers included); a freeze that measures
     only the first mis-sizes an inline addition (evidence: this bundle
     froze inline-compact against `test_guidelines` and missed the ≤22
     line budget, surfacing only at build as `30 not ≤ 22`)
   • ADD · open · a §5-scope widening discovered mid-build is NOT a
     contract change — an `add_engine/*.py` edit moves `ENGINE_PKG_MD5`
     across 3 mirror trees, so expand §5 + re-cross tests→build to
     re-anchor while §3 stays frozen (the external shape is unchanged)
     (evidence: the 1-file scope became 4 tracked files + a pin re-aim,
     resolved without reopening the freeze)
   • ADD · open · surface the TRUE blast radius at the human verify
     gate, not the original one-file story — the human gates on the real
     scope (evidence: the widened 4-file + engine-pin touch-set was
     disclosed in §6 FLAGS + the gate report, and Tin gated PASS on that
     scope)

 SPEC DELTAS    23 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone portable-roster
════════════════════════════════════════════════════════════════════════