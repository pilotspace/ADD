════════════════════════════════════════════════════════════════════════
 v13 · Decision-seam reports — decisive facts first, engine-sourced
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  4/4 met
 GATES     3 PASS             WAIVERS   none

 goal  A reviewer at any decision seam (contract approval · verify gate
       · milestone-done) gets the decisive facts first from one
       rendered, engine-sourced report — instead of digging through chat
       prose or a 250-line phase dump.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 decide-digest               done      PASS 18†   ●●●●●●●●
 tests-declared-fallback     done      PASS 8†    ●●●●●●●●
 fence-safe-wrap             done      PASS 7†    ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (6 carried)
   • ADD · folded · DECIDE NEXT is state-only, so
     planned-but-unscaffolded MILESTONE.md tasks are invisible — it said
     "fold + archive v13" with 2 of 3 planned tasks not yet created;
     consider a "n planned tasks not yet scaffolded" hint sourced from
     MILESTONE.md (evidence: report v13 right after decide-digest PASS)
   • TDD · folded · a red suite can under-cover its own §4 coverage
     target — two §4-mandated branches (3rd marker prefix, milestone
     --json key-set) were only caught at verify; at the tests phase,
     diff the §4 target nouns against the test list before declaring the
     suite red-complete (evidence: decide-digest §6 [~] disclosure)
   • SDD · folded · the `Tests live in:` grammar (backticked tokens,
     sibling shorthand) is engine-parsed but nowhere written as spec —
     the TASK.md template/§4 guide should state it (evidence: §1 ⚠ flag
     had to infer the sibling rule from 3 observed lines)
   • SDD · folded · declared tokens can name paths outside the project
     root (read-only, leaks only a def-count integer — reviewed at §6,
     no finding); a confinement Reject rule is a candidate for a future
     contract version (evidence: §6 security note, gate PASS)
   • ADD · folded · an item the AI itself wrote on the §6 security line
     was auto-reclassified "no finding" and auto-gated —
     security-category judgment always belongs to the human gate,
     whatever the apparent severity (evidence: gate record correction,
     Tin confirmed PASS post-hoc)
   • TDD · folded · making a red test fail for the RIGHT reason
     sometimes needs the fixture to exceed a hidden threshold (lines
     under the render width were already verbatim — only over-width
     lines exposed the wrap/collapse); name the threshold in the test
     constants (evidence: LONG_FENCED/SPACED deliberately > width 72, 4
     red as predicted)

 DECIDE NEXT  fold learnings + archive-milestone v13
════════════════════════════════════════════════════════════════════════