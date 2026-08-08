════════════════════════════════════════════════════════════════════════
 add-bench · Add Bench
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     9/9 done           CRITERIA  5/5 met
 GATES     9 PASS             WAIVERS   none

 goal  a reproducible, automated benchmark under `benchmark/` proving
       (or falsifying) ADD's long-term-project claim — five method arms
       (ADD · vanilla Claude Code · plan-mode-first · GSD · GitHub
       spec-kit) each build the same longitudinal greenfield workload
       (task/booking REST API + CLI, 3 sequential milestones)
       headlessly, and the harness auto-scores regression rate, spec
       fidelity, tokens/cost, context-rot slope, and time-to-first-edit
       into one arm-vs-arm pilot report
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 bench-scaffold              done      PASS 116†  ●●●●●●●●●
 bench-runner                done      PASS 116†  ●●●●●●●●●
 bench-scoring               done      PASS 116†  ●●●●●●●●●
 bench-pilot-report          done      PASS 116†  ●●●●●●●●●
 scope-exclude-test-caches   done      PASS 3209† ●●●●●●●●●
 pilot-live-hardening        done      PASS 116†  ●●●●●●●●●
 pilot-cwd-hardening         done      PASS 116†  ●●●●●●●●●
 bench-judge-median          done      PASS 116†  ●●●●●●●●●
 bench-regression-split      done      PASS 116†  ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   bench-scaffold           PASS Tin Dang <tindang.ht97@gmail.com>
   bench-runner             PASS Tin Dang <tindang.ht97@gmail.com>
   bench-scoring            PASS Tin Dang <tindang.ht97@gmail.com>
   bench-pilot-report       PASS Tin Dang <tindang.ht97@gmail.com>
   scope-exclude-test-cach… PASS Tin Dang <tindang.ht97@gmail.com>
   pilot-live-hardening     PASS Tin Dang <tindang.ht97@gmail.com>
   pilot-cwd-hardening      PASS Tin Dang <tindang.ht97@gmail.com>
   bench-judge-median       PASS Tin Dang <tindang.ht97@gmail.com>
   bench-regression-split   PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (8 carried)
   • TDD · open · a coverage-target miss disclosed at verify is closable
     cheaply via the sanctioned tests→build re-cross (add.py phase
     tests) instead of gating with residue — close-gap-before-gate held
     (evidence: run_record.py 86%→100%, commit "cover run_record
     defensive branches")
   • ADD · open · the engine's freeze-flag vocabulary is
     `[spec|scenario|contract|test]` — `[specify]` is rejected by
     unflagged_freeze; phase-guide names ≠ flag-tag names (evidence: two
     failed advance attempts before the tag fix)
   • SDD · open · benchmark fairness rules (identical
     prompts/model/ceilings, ceremony-in-budget) belong in MILESTONE.md
     shared decisions, not per-task — all 4 remaining tasks consume them
     unchanged (evidence: bench-scaffold TASK.md cites, never restates)
   • TDD · open · a disclosed deviation from a frozen Must is still a
     Must violation — verify escalated CLOSE-GAP-BEFORE-GATE instead of
     accepting the builder's honest §7 delta, and the gap closed in one
     re-cross (evidence: setup_steps finding → shlex list-argv fix,
     41/41 green)
   • ADD · open · a pre-existing test whose fixture can never run for
     real (real pip in an empty sandbox) is a fixture bug, not a
     contract conflict — adapt the fixture to the test's stated intent
     (M7) with human approval, never weaken the assertion (evidence:
     test_add_arm_pin_resolved_to_sha correction)
   • TDD · open · red-first caught a real orchestration bug
     pre-implementation: a blocking readline() loop can never observe a
     deadline against a silent child — subprocess.communicate(timeout=)
     is the correct shape (evidence: build report RED excerpt) - [SPEC ·
     open] `execute_wm` does not execute an arm's `setup_steps`
     (install/init shell lines) — a future task must decide how/where
     arm environment provisioning runs (sandboxed shell? container?)
     without violating the list-form-argv-only security constraint
     (evidence: TASK.md §5 "Strategy actually used").
   • TDD · open · the strongest scorer test was the un-mocked one: a
     real `pytest -m regression` subprocess against a real fixture app
     surfaced a genuine WM1-vs-WM2 auth conflict no mock would have
     shown (evidence: M4 scenario, 2/10 real failures)
   • SDD · open · absorbing a carried delta INTO a frozen bundle (M10's
     exact-assertion tightening named in §1/§2/§5) is the clean way to
     authorize a pre-existing-test edit — no re-cross needed because the
     freeze itself covered it (evidence: verify's git-diff scope check
     passed)

 SPEC DELTAS    10 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone add-bench
════════════════════════════════════════════════════════════════════════