════════════════════════════════════════════════════════════════════════
 v20 · Goal-Driven Dynamic Loop
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  4/4 met
 GATES     4 PASS             WAIVERS   none

 goal  a milestone self-drives toward its GOAL — verify proves each
       task's code is wired and dead-code-free (or, for prose,
       semantically read not skimmed), reopens any task that misses a
       criterion, and turns folds + extras into the next tasks, looping
       until the goal is met

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 project-goal                done      PASS 9†    ●●●●●●●●
 verify-deepen               done      PASS 10†   ●●●●●●●●
 reopen-transition           done      PASS 11†   ●●●●●●●●
 dynamic-task-loop           done      PASS 10†   ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (13 carried)
   • UDD · folded · a freshly-`init`'d project's `status` prints the
     PROJECT.md template's literal `goal: <the one durable outcome…>`
     placeholder verbatim, at the most-lost moment — colliding with the
     UDD principle "one clear next step at the most-lost moment"
     (evidence: template ships an angle-bracket placeholder;
     `goal_unset` rejects only absent/blank, so a placeholder passes
     through; goal line prints before the first-run panel).
     Contract-compliant (mapping placeholder→GOAL_UNSET would be a
     contract change, not a fix), so it did NOT block this gate — it is
     the first real feed-forward item for **dynamic-task-loop** to turn
     into a follow-up task (soften the template text to drop the
     brackets, or teach `_project_goal` a placeholder sentinel).
   • ADD · folded · the deep-check has teeth: its WIRING path caught a
     real defect on its OWN task — §4 declared `./tests/` (empty) so
     `_declared_tests_count` reported 0 while the real 10-test suite
     lived in `tooling/`; fixed pre-gate (evidence: count 0 → 10). A
     plausible-looking §4 can silently count zero tests.
   • ADD · folded · reopen-transition AND dynamic-task-loop TASK.md were
     scaffolded from the pre-v20 template — they carry NO §6 Deep checks
     block; each must gain it when it reaches verify, else it gates
     without the rubric it is downstream of (evidence: both files
     predate this task's template edit).
   • TDD · folded · a drift sentinel across hard-wrapped prose surfaces
     needs whitespace-normalized matching, not byte-equality — "stated
     identically" means same wording, and each surface wraps at its own
     column (evidence: `_norm` added so the long anchor matches across
     guide/book/run.md line-wraps while different words still fail).
   • ADD · folded · A CLI-verb contract must pre-declare **all three**
     instrument-reaction guard classes — (1) the subcommand census
     (`test_min_pillar` LIFECYCLE), (2) the `engine_pin` re-aim, AND (3)
     the ubiquitous-language **prose-ban** on add.py string literals. §3
     here pre-declared only the first two; the prose-ban surfaced during
     the build's full-suite run (a `cmd_reopen` docstring word "folds"
     tripped `test_ubiquitous_language`), forcing a reactive source edit
     + a second pin re-aim. By the v18 rule (found pre-freeze →
     contracted; found post-build → residue) that third class was
     residue. Evidence: the build's full-suite run went
     0d72a2dd→611fa233 (two pin re-aims, not one). Fix: the next
     verb-adding contract enumerates all three guard classes in its
     Instrument-reaction note up front. (CONVENTIONS.md:286-298.)
   • ADD · folded · `dynamic-task-loop` inherits the
     milestone-reactivation handoff from this task — reopen deliberately
     scoped out the TRIGGER (the human left the generic `cmd_phase`
     marker-set hatch open as the documented override). The loop owns:
     reading the deepened-verify "criterion unmet" signal, firing
     `reopen`, re-activating the now-`done` milestone, and re-queuing
     the task. Evidence: §1 framings rejected "auto-reopen wired into
     the verify gate" as out-of-scope (verb vs trigger separation).
   • ADD · folded · The §6 **Deep checks** block now travels —
     verify-deepen's observe flagged that downstream v20 tasks lacked
     it; reopen-transition adopted it (WIRING / DEAD-CODE / SEMANTIC /
     SECURITY all recorded). `dynamic-task-loop`'s TASK.md must carry
     the same block. Evidence: the block on this task proved the rubric
     portable (it re-confirmed wiring + no dead code; nothing new found,
     but the discipline is now standard).
   • SDD · folded · §3 over-anticipated the mirror topology — it said
     "engine_pin.py copies kept identical", but there is ONE canonical
     `engine_pin.py` (a single `ENGINE_MD5` literal, 7 importers
     re-anchor). Trivially satisfied, not violated. A contract should
     name the real mirror counts: add.py ×3 (canonical · `_bundled` ·
     dogfood), book ×4, but engine_pin ×1 and test_min_pillar ×1.
     Evidence: parity verified one pin, not copies.
   • ADD · folded · HEADLINE — the instrument-reaction guard-class set
     is ARTIFACT-DEPENDENT and LARGER than [[reopen-transition]]'s
     "three classes" lesson named. A CLI VERB trips three: (1)
     subcommand census, (2) engine_pin re-aim + 3-copy mirror, (3)
     ubiquitous-language prose-ban. A NEW SKILL/DOC FILE additionally
     trips TWO the frozen §3 gestured at ("mirrored across trees") but
     did NOT name as reaction classes: (4) bundle/tree parity (the
     file-SET match + byte-identity across the 3 skill trees) and (5)
     the wording-lint surface-COUNT contract. Evidence: shipping
     `loop.md` turned test_bundle_parity / test_tree_parity /
     test_wording_lint::test_surface_files_cover_the_contract (19→20)
     red until each was updated. Generalize the pre-declaration rubric
     BY ARTIFACT TYPE — CLI verb → census + engine_pin + prose-ban; new
     skill/doc file → + bundle/tree parity + surface-count. Fold into
     CONVENTIONS:286-298 (the "all three guard classes" note) as "the
     classes depend on what you ship."
   • ADD · folded · the WIDE milestone-closer reaction touched ~12 test
     files (9 fixtures + test_min_pillar census + test_decide_digest
     decide-next + test_wording_lint surface-count), confirming §1 ⚠ b's
     "WIDE 2-ripple" prediction at full scale: a change to a lifecycle
     PRECONDITION ripples to every test that drives that lifecycle to
     close, and the cost is one fixture FILE-WRITE per reactor (not an
     argv append). Root cause is a design choice — the new-milestone
     template ships an unchecked placeholder box, which (intentionally)
     makes total>0 by default so the gate is real; that same default is
     what makes the reaction universal. Evidence: full suite 616→626,
     every closer test required exit-criteria-meeting setup; all
     additive (git numstat 0 deletions across the 9 fixtures, 0
     assertions weakened).
   • UDD · folded · the `milestone-done` SUCCESS message (add.py:1088
     "Confirm the MILESTONE.md exit criteria are checked, then
     archive/start the next") is now STALE — it asks the human to
     confirm what the gate (add.py:1070) already ENFORCES: by the time
     that line prints, every box IS checked (or total==0). Clean
     prose-only follow-up: drop the redundant "confirm the boxes" ask,
     keep the archive/next nudge. Evidence: read add.py:1069-1088 — the
     gate dies before the success path, so the post-success "confirm"
     can never fail.
   • SDD · folded · the total==0 dodge (§1 ⚠ a, accepted at freeze): a
     milestone with zero exit-criteria boxes is never held by the gate.
     The template's placeholder box keeps real milestones at total>0,
     but a hand-stripped MILESTONE.md reopens it. A stricter follow-up
     reject `milestone_no_criteria` (refuse milestone-done when
     total==0) is a clean ADDITION belonging to its own change — it
     would trip the same WIDE reaction across the 14 pre-v20 done
     milestones + every criteria-less test, so it needs its own bundle.
     Recorded as the open candidate, deliberately not built here.
   • UDD · folded · the gate's correctness rests on the human writing
     REAL, checkable exit-criteria lines — a placeholder box checked
     without a real goal behind it is goal-met theater (the same failure
     mode the method warns about for an unearned `gate=PASS`). v20's OWN
     close is the first dogfood: v20's MILESTONE.md exit criteria must
     be observable lines or the gate (correctly) holds v20 open.
     Connects to the project-goal task's "criteria must be checkable"
     lesson; the trust model (human discipline, surfaced in loop.md) is
     the only mitigation — the engine reads the tally, it cannot judge
     whether the box was earned.

 DECIDE NEXT  consolidate learnings + archive-milestone v20
════════════════════════════════════════════════════════════════════════