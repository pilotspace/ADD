════════════════════════════════════════════════════════════════════════
 git-merge-safety · Git-merge safety
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  2/2 met
 GATES     2 PASS             WAIVERS   none

 goal  a team merging parallel branches never silently corrupts
       .add/state.json — ADD recognizes a conflicted or inconsistent
       state at load and via a doctor command, and guides reconciliation
       instead of crashing or proceeding on bad data
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 merge-guard                 done      PASS 0     ●●●●●●●●●
 state-doctor                done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   merge-guard              PASS Tin Dang <tindang.ht97@gmail.com>
   state-doctor             PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (4 carried)
   • ADD · open · a fail-closed guard that REPLACES a generic error with
     a specific one belongs at the single shared read seam, routed into
     every caller — not duplicated per call site; the callers' existing
     `except` must catch only the GENERIC failure (Exception subclasses)
     so the specific `_die`/SystemExit propagates past them (evidence:
     merge-guard routed 3 read sites through one `_state_text_or_die`;
     the review's #1 refutation target was a swallowed SystemExit —
     avoided precisely because SystemExit ⊄ Exception).
   • TDD · open · a "no-false-positive" test must build its fixture
     through the REAL constructor (CLI/new-task), not a hand-rolled
     partial record — a partial dict passes the guard then crashes a
     DOWNSTREAM consumer, masking what the test means to prove
     (evidence: the first regex-false-positive test built a task dict
     missing `gate` → cmd_status KeyError, not the guard; fixed by
     `new-task`).
   • ADD · open · a "REPORTS instead of aborts" diagnostic must be
     tested against TYPE-corrupt (not just parse-corrupt) state — the
     refute-read found an AttributeError path the 6 contracted scenarios
     missed; the design-for-failure promise only holds with an explicit
     type-robustness scenario (evidence:
     test_doctor_reports_not_aborts_on_type_corrupt_state added
     post-review)
   • TDD · open · a substring assert on a 1-char slug (`assertIn("t",
     out)`) is vacuous — incidental letters in the PASS line satisfy it;
     assert the QUOTED form (`"'t'"`) so the test actually pins
     provenance (evidence: refute-read Finding 2, tightened in this
     build)

 SPEC DELTAS    30 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              git-merge-safety
════════════════════════════════════════════════════════════════════════