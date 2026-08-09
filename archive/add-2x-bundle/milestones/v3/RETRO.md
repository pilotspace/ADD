════════════════════════════════════════════════════════════════════════
 v3 · Correct · Shippable
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  2/2 met
 GATES     1 PASS             WAIVERS   none

 goal  Make ADD correct under misuse and safe to publish: refuse unsafe
       gates, guard the docs/build invariants, ship clean

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 ship-clean                  done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (2 carried)
   • TDD · open · a publish-time hook can be proven WITHOUT publishing —
     run the hook command as a subprocess and assert it executed the
     guard and exited 0; it reds on broken/misspelled wiring but cannot
     prove npm honors the hook (evidence:
     test_prepublish_hook_runs_the_guard; ship-clean §6 ⚠ wiring-vs-live
     limit).
   • ADD · open · a planned-but-unscaffolded milestone (v3, 0 TASK.md)
     is best closed by a SCOPE AUDIT against shipped code — 3 of 5
     original tasks were already superseded/delivered/obsolete; only 2
     residuals were real (evidence: v3 MILESTONE.md scope-audit table,
     2026-06-03).
════════════════════════════════════════════════════════════════════════