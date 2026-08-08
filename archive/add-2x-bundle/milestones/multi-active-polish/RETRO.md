════════════════════════════════════════════════════════════════════════
 multi-active-polish · multi-active-polish — close the genuinely-open parallel-front residuals
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  4/4 met
 GATES     4 PASS             WAIVERS   none

 goal  close the multi-active residuals an audit confirmed still open:
       cross-milestone wave scheduling, a widened ownership lens, doctor
       value-domain validation, and parallel-preserving milestone
       creation.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 waves-merge                 done      PASS 11†   ●●●●●●●●●
 doctor-value-checks         done      PASS 11†   ●●●●●●●●●
 mine-all-lens               done      PASS 6†    ●●●●●●●●●
 new-milestone-add-focus     done      PASS 6†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   waves-merge              PASS Tin Dang <tindang.ht97@gmail.com>
   doctor-value-checks      PASS Tin Dang <tindang.ht97@gmail.com>
   mine-all-lens            PASS Tin Dang <tindang.ht97@gmail.com>
   new-milestone-add-focus  PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (5 carried)
   • ADD · open · a NEW add.py prose string must dodge the reserved
     ubiquitous-language terms (here "fold") — the lint fires at
     FULL-SUITE time, not at write time, so an engine edit that adds
     help/docstring prose should grep the new strings against the ban
     list before the first full run (evidence: `--merge` help +
     docstring used "fold", caught by test_ubiquitous_language, reworded
     → "unify", this task)
   • ADD · open · before adding a doctor/audit check, GREP the real
     long-lived state.json for the values it will judge
     (gates/phases/archived shape) — a check that trips on legitimate
     history is a false-positive that erodes trust; here all 91 tasks +
     45 archived passed, verified pre-build (evidence: the §0 GROUND
     "VERIFIED" note, this task)
   • TDD · open · a fixture that calls `new-task` with no `--milestone`
     does NOT make a loose task — new-task auto-links to the active
     milestone; a "loose" fixture must poke milestone=None explicitly.
     The red test passed its assertion against the WRONG arrange until
     the build surfaced it (evidence:
     test_all_includes_loose_renders_loose showed `[m1]` not `[loose]`)
   • ADD · open · before claiming "helper retained — other callers
     remain" in a contract, GREP the call sites — here the swap removed
     the LAST caller and the §0/§3 "used by deactivate-to-empty"
     rationale was wrong; the retention still held but for a DIFFERENT
     reason (it's a directly-tested accessor), caught only by the verify
     refute-read (evidence: zero non-def call sites +
     test_active_accessors references)
   • ADD · open · doing ALL test edits (new file + premise-fix of an
     invalidated existing test) in the TESTS phase before crossing to
     build avoids the tamper tripwire — contrast mine-all-lens, where a
     build-phase fixture fix tripped it and forced a re-baseline
     (evidence: this task's verify gated clean on the first try)

 SPEC DELTAS    61 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              multi-active-polish
════════════════════════════════════════════════════════════════════════