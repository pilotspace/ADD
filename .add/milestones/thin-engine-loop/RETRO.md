════════════════════════════════════════════════════════════════════════
 thin-engine-loop · Thin engine, loop-in-SKILL, 6→3 phases
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     10/10 done         CRITERIA  6/6 met
 GATES     10 PASS            WAIVERS   none

 goal  A task runs read-SKILL→edit→freeze→gate with ≤3 add.py calls
       (from 5), loop driven by the SKILL, mechanical floor intact
       (verify: add-bench call census ≤3 median AND
       test_freeze_*/test_gate_*/test_audit_* stay green)
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 test-corpus-slim            done      PASS 8†    ●●●●
 template-unify              done      PASS 2247† ●●●●
 foundation-split            done      PASS 0     ●●●●
 persona-routes-depth        done      PASS 6†    ●●●●
 fable-thinking-reference    done      PASS 5†    ●●●●
 phase-collapse-3            done      PASS 11†   ●●●●
 lock-probe-ci-realism       done      PASS 0     ●●●●
 fable-floor-reasoning       done      PASS 5†    ●●●●
 round-visible-runs          done      PASS 2247† ●●●●
 skill-loop-fold             done      PASS 2247† ●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   test-corpus-slim         PASS Tin Dang <tindang.ht97@gmail.com>
   template-unify           PASS Tin Dang <tindang.ht97@gmail.com>
   foundation-split         PASS Tin Dang <tindang.ht97@gmail.com>
   persona-routes-depth     PASS Tin Dang <tindang.ht97@gmail.com>
   fable-thinking-reference PASS Tin Dang <tindang.ht97@gmail.com>
   phase-collapse-3         PASS Tin Dang <tindang.ht97@gmail.com>
   lock-probe-ci-realism    PASS Tin Dang <tindang.ht97@gmail.com>
   fable-floor-reasoning    PASS Tin Dang <tindang.ht97@gmail.com>
   round-visible-runs       PASS Tin Dang <tindang.ht97@gmail.com>
   skill-loop-fold          PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 6/6 met

 LEARNINGS (10 carried)
   • TDD · open · a name+token classifier CANNOT clear kill candidates
     alone — asserts hide behavioral guards inside parity-named fns; the
     killed-fn AST diff audit (old-vs-new, flag any non-byte assert) is
     the mandatory second pass (evidence: 16 restored guards after "0
     behavioral suspects")
   • TDD · open · a token scrub over test files must be line-aware AND
     anchor-aware — a pin token can be legitimate CONTENT (a CHANGELOG
     anchor string) (evidence: test_release_1_11_0 red)
   • ADD · open · "untouched by this build" git-diff asserts are vacuous
     at HEAD and false-red every later task touching the file — pin
     CI/file SHAPE, never in-flight worktree state (evidence:
     test_ci_tooling_mirror_gap red on both full runs)
   • ADD · open · seam docs with line-number anchors red on
     consolidation — re-aim SEAMS.md in the same commit that deletes an
     anchored symbol (evidence: test_seams_doc red)
   • TDD · open · a new freeze floor (boundary_unfilled both lanes)
     ripples into EVERY fixture that freezes a rendered scaffold — grep
     the freeze-helper idiom BEFORE the build, not after the full suite
     (evidence: 6 files, 33 reds, all one fixture line)
   • ADD · open · when a red test contradicts its own frozen contract,
     fix the TEST to the contract + re-cross --by — never bend the build
     (evidence: drop-set test's nested-### bug, re-crossed 2026-07-17)
   • ADD · open · a tamper-glint contract clause (state-is-the-witness)
     needs its OWN lint branch — recording the state key alone doesn't
     measure a deleted header line (evidence: R3 red survived the first
     build cut)
   • ADD · open · a guide-path census freezes SHORT: grep the whole test
     dir for the old names BEFORE freezing — the ~17 estimate was 35
     live files / 97 reds (evidence: first targeted run)
   • ADD · open · wording-rubric keep-terms bind across folds — a
     deleted file's sole keep-term carrier (Objective:) must be
     re-homed, not dropped (evidence: wording_lint 4 findings)
   • ADD · open · a "doc-only" contract line can contradict an engine
     comment reserving a re-aim for the same task — grep the engine for
     the task slug at freeze time (evidence: §3 v2 amendment)

 SPEC DELTAS    46 open deltas — resolve: new-task --from-delta (or close in §7)

 DECIDE NEXT  consolidate learnings + archive-milestone
              thin-engine-loop
════════════════════════════════════════════════════════════════════════