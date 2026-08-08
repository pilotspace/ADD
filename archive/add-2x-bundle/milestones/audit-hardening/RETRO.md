════════════════════════════════════════════════════════════════════════
 audit-hardening · Audit hardening — close gate/atomicity/coverage gaps
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  5/5 met
 GATES     5 PASS             WAIVERS   none

 goal  make the engine enforce at gate-time the invariants the post-hoc
       audit catches — no PASS against an unfrozen or stale contract,
       crash-safe state writes, and a monotonic heal counter — closing
       the gaps the 2026-06-25 deep audit surfaced
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 phase-build-guard           done      PASS 7†    ●●●●●●●●●
 consumer-stale-gate         done      PASS 20†   ●●●●●●●●●
 setup-tests-before-build    done      PASS 5†    ●●●●●●●●●
 save-state-harden           done      PASS 11†   ●●●●●●●●●
 force-preserve-heal         done      PASS 14†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   phase-build-guard        PASS Tin Dang <tindang.ht97@gmail.com>
   consumer-stale-gate      PASS Tin Dang <tindang.ht97@gmail.com>
   setup-tests-before-build PASS Tin Dang <tindang.ht97@gmail.com>
   save-state-harden        PASS Tin Dang <tindang.ht97@gmail.com>
   force-preserve-heal      PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (3 carried)
   • ADD · open · a scope-correct mid-build discovery (needing an
     out-of-scope file — here the lean fence) is resolved by declaring
     it in §5 AND surgically patching `state.scope.declared`, NOT by
     re-crossing tests→build — re-crossing re-walks the DIRTY tree and
     neuters the touch baseline (evidence: F6 — test_skill_lean.py
     rebaseline added mid-build, sidecar md5 preserved).
   • ADD · open · a deliberate, contract-approved content addition that
     busts a lean-fence pool is absorbed by REBASELINING the baseline by
     surface÷ratio (ratio kept), not by token-golfing the new prose
     thinner (evidence: F6 +302 B → phases baseline 37920→38298, the won
     ground untouched).
   • ADD · open · before "preserving" state across a re-create, check
     whether the engine RE-DERIVES it downstream — a carry-forward of
     re-derived state (tripwire) is a hollow guard; only state owned by
     a single writer (heal ← _heal_or_escalate) survives meaningfully
     (evidence: F8 — the approved tripwire fold-in was withdrawn after
     reading _build_entry's unconditional re-snapshot).

 SPEC DELTAS    54 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone audit-hardening
════════════════════════════════════════════════════════════════════════