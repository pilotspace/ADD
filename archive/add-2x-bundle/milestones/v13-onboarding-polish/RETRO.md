════════════════════════════════════════════════════════════════════════
 v13-onboarding-polish · Onboarding & Orchestration Polish
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     6/6 done           CRITERIA  7/7 met
 GATES     6 PASS             WAIVERS   none

 goal  starting and running an ADD project feels guided and self-tuning
       — setup proposes the run-mode, first milestone, and per-drive
       domain depth; the engine schedules a milestone's tasks by their
       dependency DAG; and the AI's voice (SOUL.md) self-improves toward
       the human's wording

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 dag-scheduler               done      PASS 14†   ●●●●●●●●●
 setup-run-mode              done      PASS 6†    ●●●●●●●●●
 setup-suggest-milestone     done      PASS 5†    ●●●●●●●●●
 setup-domain-deepdive       done      PASS 0     ●●●●●●●●●
 soul-artifact               done      PASS 0     ●●●●●●●●●
 soul-self-improve           done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 7/7 met

 LEARNINGS (13 carried)
   • ADD · open · the verify adversarial refute-read earns its place —
     it caught a real HIGH correctness bug (transitive blocking not
     propagated) that all 9 first-pass tests missed; the gate is not
     ceremony (evidence: refute REFUTED v1 → fixed →
     test_transitive_blocked_dep_is_not_scheduled)
   • TDD · open · when verify reveals a MISSING test, reopen to TESTS
     not build — adding the guard test while in build tripped the tamper
     tripwire (build_tampered); the honest loop is
     reopen→tests→re-snapshot→build (evidence: gate returned
     return_to_build attempt 1/3, cleared by re-crossing tests→build)
   • ADD · open · a read-only reporter that REUSES the existing
     satisfaction predicate (_dep_satisfied) inherits its correctness
     for free — the bug lived only in the NEW transitive layer, never
     the reused base (evidence: the satisfied-dep + archived-dep
     scenarios passed first try)
   • ADD · open · a default-flip is safe to ship as a PROPOSAL +
     comparison table + confirm-to-keep — the human sees the flow before
     owning it; "show before ask" applies to defaults too (evidence:
     setup-run-mode shipped the philosophy shift behind a confirm, floor
     unchanged)
   • SDD · open · the wording lint is a real guard on prose tasks — it
     caught "dial" slang the content tests would have passed; prose
     freezes need the lint in the green bar (evidence:
     test_ubiquitous_language went red on autonomy-dial, fixed to
     "autonomy level")
   • TDD · open · a whole-file substring test is too weak when sibling
     sections share vocabulary — anchor the region on a UNIQUE new
     marker so the suite is genuinely red (evidence: "propose"/"flow"
     pre-existed from setup-run-mode; scoping to the "kickoff" marker
     made the test honest)
   • UDD · open · setup should SUGGEST from what it just read, not
     interrogate — the AI proposes the first milestone
     (goal+flow+scenarios) and the human reacts; show-before-ask applies
     at the foundation altitude too (evidence: setup-suggest-milestone)
   • TDD · open · setup's lens list omitted the trust/"done & trusted"
     drive — the four drives weren't symmetric at foundation level until
     2c named TDD explicitly (evidence: §2b table had
     Domain/Spec/Users/Decisions, no trust lens;
     test_names_all_four_drives now guards all four)
   • ADD · open · auto-mode's "deepen drafting, never the gate" rule now
     applies at SETUP, not just per-task verify — auto-complete
     collapses the deep-dive turns but never the lock (evidence:
     test_preserves_the_baseline_approval_gate)
   • ADD · open · the method had no first-class home for the AI's VOICE
     — tone/style/trust lived only in scattered global instructions;
     SOUL.md makes it a survivor-layer living doc the human owns
     (evidence: SETUP_FILES had no voice doc until this task;
     test_soul_in_setup_files now guards it)
   • ADD · open · identity-owned content can ship as a PROPOSED,
     test-unlocked starter — the gate attests the mechanism while the
     human keeps the voice (evidence: tests assert schema not tone
     words; the §3 freeze explicitly carves the voice prose out of the
     contract)
   • ADD · open · self-improvement now has TWO routed loops — competency
     deltas → foundation (deltas.md/fold.md) and voice deltas → SOUL.md
     (soul.md) — sharing one propose→confirm→write discipline but
     distinct targets (evidence: soul.md mirrors fold.md's lifecycle;
     test_human_only_writer guards the shared floor)
   • ADD · open · the voice loop closes the SOUL.md story task 5 opened
     — task 5 shipped the target schema, task 6 ships the writer;
     together they make the AI's voice a living, human-confirmed doc
     (evidence: SOUL.md.tmpl "Voice deltas" now resolves to soul.md;
     test_soul_template_points_at_loop)

 DECIDE NEXT  consolidate learnings + archive-milestone
              v13-onboarding-polish
════════════════════════════════════════════════════════════════════════