════════════════════════════════════════════════════════════════════════
 ground-phase · Ground phase — build against the real codebase
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  A task's contract, tests and build are grounded in the real
       current codebase: a new ground phase (a phase-0 preamble before
       the seven steps) gathers the actual files, symbols, signatures,
       patterns and conventions the work touches, surfaced as anchors
       the frozen contract cites — so the AI builds against reality, not
       assumption.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 ground-phase-engine         done      PASS 14†   ●●●●●●●●●
 ground-bundle-wiring        done      PASS 0     ●●●●●●●●●
 ground-prose-align          done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (12 carried)
   • ADD · open · the ground phase shipped with ZERO lived dogfood — all
     3 milestone tasks were grandfathered at `specify` (created before
     ground existed); test_ground_phase proves the mechanics, but the
     first task to actually START at ground is next-milestone (accepted
     ceiling, recorded not skipped) (evidence: ground-bundle-wiring +
     ground-prose-align both sit at phase `specify`, never `ground`)
   • ADD · open · grounding the contract in the REAL engine (reading
     PHASES + every keyed function before drafting §3) pre-caught four
     shipping defects the spec alone would have missed (evidence: the
     decide_data else→`gate` seam mislabel, the render_decide seam_label
     KeyError, the PHASES[:7] structural slices, and
     header-parsed-vs-positional numbering — each surfaced during §0
     grounding / the advisor pass, before build)
   • TDD · open · inserting at index 0 of an ordered tuple silently
     shifts every ABSOLUTE index/slice (PHASES[:7], names[n-1],
     i=p["n"]-1) while RELATIVE logic (PHASES.index) stays safe — grep
     the absolute forms before mutating an ordered constant (evidence:
     the drill marker off-by-one passed the engine edits but failed
     test_phase_detail's `> N` marker assertion)
   • ADD · open · the book diagram + CHECKLIST are coupled to the ladder
     shape, so an engine ladder change must make a MINIMAL diagram edit
     to keep the suite green while deferring the narrative to the prose
     task (evidence: test_flow_diagram iterates `add.PHASES`, so adding
     `ground` forced the ch02 mermaid S0 node)
   • ADD · open · the strongest position for an additive engine surface
     is to make CURRENT output byte-unchanged — suppressing the
     None/legacy case means every existing task's status is identical,
     so zero existing output-tests need conforming and the live dogfood
     `check` count is unmoved (evidence: status silent for legacy tasks;
     full suite 780 OK with no status/check output-test edits; dogfood
     check stayed 264/0)
   • ADD · open · a measure-not-block surface has an established SHAPE
     worth copying verbatim — goal-ready's "human-readable status line +
     never-red WARN riding the existing warnings array, no new --json
     key" mirrored exactly avoided the json_surface_unsanctioned_key
     landmine and the design churn (evidence:
     test_no_new_json_key_on_check green; the WARN rides `warnings` like
     goal_not_auto_ready)
   • TDD · open · a prose checklist guarded by an exact COUNT + a line
     BUDGET (test_review_checklist: ==6 items, ≤16 lines) makes "gains
     one line" a precise, self-checking change — the new bullet had to
     be ONE physical line and the count test had to move 6→7 in lockstep
     (evidence: 16 ≤ 16 non-blank held; test_review_checklist conformed
     6→7, shape preserved)
   • ADD · open · retrofitting a §0 GROUND map onto a grandfathered task
     at build dogfoods the new surface honestly (records the grounding
     that informed §3) WITHOUT claiming the task flowed through the
     ground phase — the "zero lived runs starting at ground" ceiling
     still stands for the next milestone (evidence: ground-bundle-wiring
     shows `grounded ✓` live yet started at `specify`, not `ground`)
   • SDD · open · a byte-sync test written for a NEW term surfaced a
     PRE-EXISTING drift no prior test caught — the repo-root appendix-c
     mirror had silently fallen behind canonical (missing a whole term);
     a "synced ×N" guard pays for itself beyond the change that adds it
     (evidence: test_book_glossary_synced_x4 was red on the stale root
     before any ground edit; root was 2 lines + the "Auto-ready goal"
     term behind canonical)
   • ADD · open · a phase-0 PREAMBLE earns prose in the flow chapter,
     not a step-chapter — keeping ground in 02-the-flow.md (vs a
     dedicated chapter + a PHASE_GUIDE retarget) preserves the "seven
     steps" brand and the lean-over-GSD rule, and the engine pointer was
     already correct (evidence: PHASE_GUIDE["ground"]→02-the-flow.md
     left unchanged; test_flow_diagram green with "seven steps"
     retained; reverses ground-phase-engine §7's "retarget" note with
     rationale)
   • TDD · open · deriving a test's expected set from the engine
     constant (FLOW_PHASES = [p for p in add.PHASES if p != "done"])
     means a ladder change auto-propagates the prose requirement —
     adding ground to PHASES made test_flow_diagram REQUIRE ground in
     the mermaid+CHECKLIST without a test edit (evidence:
     test_flow_diagram stayed green through ground-phase-engine because
     the mermaid/CHECKLIST were updated to satisfy the engine-derived
     set)
   • ADD · open · retrofitting a §0 map onto each grandfathered
     milestone task at build let all three tasks dogfood `grounded ✓`
     live, turning the "zero lived dogfood" ceiling into "zero lived
     runs STARTING at ground" — a narrower, more honest residual
     (evidence: ground-bundle-wiring + ground-prose-align both show
     `grounded ✓` yet started at `specify`)

 DECIDE NEXT  consolidate learnings + archive-milestone ground-phase
════════════════════════════════════════════════════════════════════════