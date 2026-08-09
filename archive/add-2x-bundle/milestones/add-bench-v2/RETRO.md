════════════════════════════════════════════════════════════════════════
 add-bench-v2 · Add Bench V2
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  5/5 met
 GATES     4 PASS             WAIVERS   none

 goal  measure ADD's actual value proposition — regression safety,
       gaming resistance, resumability, direction-mining, security
       floors, traceability — on the pinned meter, deterministically
       scored, and report cost-per-TRUSTED-feature alongside v1's raw
       cost; if a competing flow also holds the floors, report that
       honestly
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 v2-meter-fixes              done      PASS 197†  ●●●●●●●●●
 v2-wv1-longitudinal         done      PASS 197†  ●●●●●●●●●
 v2-wv2-hostile-change       done      PASS 0     ●●●●●●●●●
 v2-scoring-report           done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   v2-meter-fixes           PASS Tin Dang <tindang.ht97@gmail.com>
   v2-wv1-longitudinal      PASS Tin Dang <tindang.ht97@gmail.com>
   v2-wv2-hostile-change    PASS Tin Dang <tindang.ht97@gmail.com>
   v2-scoring-report        PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (10 carried)
   • TDD · open · when a frozen contract SUPERSEDES sibling tests'
     pinned semantics, the honest path is a TESTS re-cross that
     STRENGTHENS each pin to the new behavior — never an in-build edit,
     never a deletion (evidence: 4 v1 pins amended, suite 154/154)
   • ADD · open · ground before design: the "missing" deterministic
     probes already existed as unscored oracle suites — grounding turned
     an invention task into a wiring task (evidence: §0 Touches)
   • SDD · open · a metric whose MEANING changes needs a self-describing
     artifact on every record (regression_source), or archived numbers
     silently mix semantics (evidence: M7)
   • ADD · open · IDENTICAL scores across independent arms indict the
     METER, not the arms — both wm3 defects (denominator ceiling,
     survivors fallback) were caught by that smell alone; cheap-looking
     runs ($0.4/WM vs $3-6 expected) are the same class of smell
     (evidence: meter defects #3-#5, 2026-07-10)
   • ADD · open · a headless meter must be environmentally
     SELF-SUFFICIENT — model pin, permission grant, state isolation;
     ambient operator config changed mid-campaign and voided two arms
     (evidence: rep0-VOID-permdefect/WHY-VOID.md)
   • TDD · open · validate a probe against a KNOWN-GOOD control app
     before believing it about arms under test — the goodapp control
     separated probe defects from arm failures in minutes (evidence:
     scratchpad goodapp 2/2 while all arms failed, 2026-07-10)
   • TDD · open · a probe's control app must be DERIVED from the track's
     own prompts, not the probe author's mental model — the end_time
     controls validated my assumption, not the contract (meter defect
     #6) (evidence: commit 3fef517)
   • ADD · open · the identical-score/impossible-ceiling smell caught
     its 6th meter defect ONE record into a campaign — treat any
     anomalous score as a meter indictment first, an arm verdict second
     (evidence: add hv3 0.25 -> 4/4 on the corrected oracle)
   • TDD · open · a build expectation that predicts the DATA's shape
     (not the code's behavior) can be wrong while the code is right —
     record the deviation and prove the unexercised branch live instead
     of editing the expectation (evidence: honest-outcome tie line
     absent on both real archives, proven on a tie fixture at the gate)
   • ADD · open · a stricter mechanical metric layered over a prior
     human judgment must carry the judgment as context, not overwrite it
     — raw + adjusted + caveat rendered together kept both truths
     visible (evidence: 4 weakened cells vs the hand-diff, §6
     refute-read item 5)

 SPEC DELTAS    27 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone add-bench-v2
════════════════════════════════════════════════════════════════════════