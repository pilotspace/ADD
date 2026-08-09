════════════════════════════════════════════════════════════════════════
 v9-1 · Phase-detail drill-down
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  2/2 met
 GATES     1 PASS             WAIVERS   none

 goal  A person can drill into one task and read each phase's actual
       result — rules, scenarios, frozen contract, test plan, gate +
       evidence, observe delta — rendered read-only from its TASK.md,
       without opening the file

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 phase-detail-render         done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (4 carried)
   • SDD · open · "smart single positional" (milestone-first, else task)
     beat the drafted two-arg CLI at the one-approval gate — the advisor
     caught that the draft made drill-down UNREACHABLE (argparse binds a
     lone positional to the 1st name). Lesson: trace argparse binding
     when a contract adds an optional positional; the obvious shape can
     silently strand a code path. (evidence: §3 routing line was
     internally inconsistent until reconciled before freeze)
   • ADD · open · the v9 "freeze the DATA seam, not presentation" delta
     PAID OFF here: the ragged 72-wide wrap shipped as disclosed
     presentation debt, NOT a gate-blocker, because the frozen contract
     is task_phases' fields + fail-closed rule, not the block layout.
     (evidence: PASS with a known cosmetic gap, no re-freeze needed to
     fix it later)
   • TDD · open · the v9 retro utf-8 lesson generalized to the READ
     side: pinning encoding + an OSError fail-closed guard on the
     TASK.md read was added BEFORE the gate (not after a locale bug),
     and locked by test_unreadable_file_failclosed. (evidence:
     design-for-failure check passed with a test, not a promise)
   • UDD · open · a drill-down is a READ surface where line-structure
     (scenarios, contract code) matters more than column alignment — so
     it preserves physical lines + soft-wraps, unlike the rollup which
     collapses prose. Two render idioms now coexist by purpose.
     (evidence: _detail_body vs _wrap diverged deliberately)
════════════════════════════════════════════════════════════════════════