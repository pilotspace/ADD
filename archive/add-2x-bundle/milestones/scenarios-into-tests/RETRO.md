════════════════════════════════════════════════════════════════════════
 scenarios-into-tests · Fold §2 SCENARIOS into §4 TESTS & SCENARIOS
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  0/0 met
 GATES     2 PASS             WAIVERS   none

 goal  Retire the standalone §2 SCENARIOS section by folding its role
       into a retitled §4 'TESTS & SCENARIOS', and shift §4 rigor to
       primary-only — one red test per §1 Must/Reject; minor behaviors
       are prose build-guidance, not gated. Keep §3–§7 numbers, the
       freeze parser, and the whole test corpus untouched.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 fold-scenarios-tests        done      PASS 2236† ●●●●
 book-de-scenarios           done      PASS 0     ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   fold-scenarios-tests     PASS Tin Dang <tindang.ht97@gmail.com>
   book-de-scenarios        PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ○○○○○○○○○○ 0/0 met

 LEARNINGS (3 carried)
   • ADD · open · Retire-in-place beats renumber for a number-keyed
     §-schema: delete §2 + retitle §4 = 1 task; the engine tolerates a
     non-contiguous §1→§3 doc because `_phase_spans` is dict-keyed, not
     ordinal. A contiguous renumber would have rewritten the freeze
     parser + ~380 refs + the whole test corpus. (evidence: freeze
     parser + 2236-floor untouched; task shipped in one bundle)
   • ADD · open · A schema change under-counts its coupled tests at
     freeze — beyond the 2 obvious conformance suites, 4 more fixtures
     encoded the old §2; the SIGNED re-cross is the sanctioned
     scope-widening, not a defect. (evidence: 6 suites migrated;
     re-cross re-armed tripwire+scope)
   • TDD · open · A "migrated" fixture can go vacuous — when a helper
     targets a retired section, make it SYNTHESIZE the legacy shape so
     the still-supported branch stays genuinely exercised. (evidence:
     rule_id_coverage._set_section builds a legacy §2; advisor confirmed
     non-vacuous)

 SPEC DELTAS    46 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone
              scenarios-into-tests
════════════════════════════════════════════════════════════════════════