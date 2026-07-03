════════════════════════════════════════════════════════════════════════
 install-update-hardening · Install/update hardening — atomic + concurrency-safe writes
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  4/4 met
 GATES     4 PASS             WAIVERS   none

 goal  add.py init/update (both --global and project-scope, pip+npm
       twins) survive a crash or a concurrent run without leaving a
       half-written .add/ tree or a wedged lock
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 global-lock-followups       done      PASS 35†   ●●●●●●●●●
 global-data-restore-harden  done      PASS 36†   ●●●●●●●●●
 project-scope-atomic-recon… done      PASS 27†   ●●●●●●●●●
 project-scope-install-lock  done      PASS 30†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   global-lock-followups    PASS Tin Dang <tindang.ht97@gmail.com>
   global-data-restore-har… PASS Tin Dang <tindang.ht97@gmail.com>
   project-scope-atomic-re… PASS Tin Dang <tindang.ht97@gmail.com>
   project-scope-install-l… PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (16 carried)
   • ADD · open · a parallel-build worktree can be branched before the
     orchestrator finishes that same milestone's Specify→Contract→Freeze
     work, leaving the worker's own `TASK.md`/`state.json` at the blank
     template while the real frozen contract exists only on the
     integration branch — the worker has no way to detect this except by
     re-reading its own `TASK.md` at the start gate. Recommend either
     freezing all of a milestone's task contracts BEFORE cutting worker
     worktrees, or re-pointing each worker worktree onto the integration
     branch immediately before resuming its build agent (evidence: this
     session — 2 of 3 sibling `install-update-hardening` worktrees
     branched at `eb631bc`, confirmed 2 commits behind
     `release/1.15.0`@`cda1a16` which drafted+froze all 3 contracts;
     `git merge-base --is-ancestor eb631bc cda1a16` = NO; both worktrees
     showed zero commits of their own; the divergence was 100% confined
     to `.add/` tracking docs, zero source/test drift)
   • ADD · open · the SAME class of gap recurs one layer deeper and is
     NOT limited to the frozen-contract case above: a fresh `git
     worktree add` never materializes gitignored / untracked content
     (`.add/tooling/add.py`, `.add/docs`) even when the base commit's
     TRACKED files are otherwise current — every worktree spawned this
     session needed a manual copy-in before its own engine commands
     (`add.py phase`/`advance`) would work at all. A worktree-spawn step
     should either materialize these trees automatically, or the spawn
     prompt should include an explicit step-0 check (evidence: found
     independently in `project-scope-atomic-reconcile`'s, this task's,
     AND `global-data-restore-harden`'s worktrees this session — 3 for
     3, not a one-off)
   • TDD · open · the disclosed in-process-thread-only concurrency
     evidence for a `risk: high` task was judged insufficient for
     sign-off by an independent verify pass — closing that gap required
     authoring genuinely NEW multi-process tests (real
     `subprocess.Popen` races), not merely re-running the existing
     suite. A `risk: high` task's own §4 test plan should budget for
     real multi-process coverage up front rather than leaving it to a
     verify-time discovery (evidence: the independent add-verify pass
     authored 2 new tests — 8 trials × 6 processes on the raw lock
     primitive, 6 trials × 8 processes on the full `install()` path —
     after judging the builder's own thread-based evidence insufficient
     for a risk:high gate)
   • TDD · open · `test_concurrent_stale_reclaim_exactly_one_wins`'s own
     `assertGreaterEqual(results.count("acquired"), 1, ...)` stayed
     green through the entire TOCTOU race's lifetime — true even with 2+
     processes simultaneously believing they held the lock. A liveness
     assertion ("someone eventually got in") is not an exclusivity
     assertion ("never more than one at a time"); the gap surfaced only
     via an independent verify pass on a sibling task, not this task's
     own suite (evidence: reopen-round §6,
     `test_global_update_harden.py` shared the identical weak-assertion
     shape as `test_project_scope_lock.py`)
   • ADD · open · a bounded `--lock-timeout` retry loop can be silently
     defeated by an early `continue` sitting on a codepath that never
     reaches its own deadline check — both the "won the ticket" and
     "lost the ticket" branches unconditionally `continue`d past the `if
     deadline...`/`raise BlockingIOError` check, so once a reclaim
     ticket leaked, `--lock-timeout` stopped being enforceable. The loop
     still eventually self-healed, so this reads as merely "slow" rather
     than "hung" on casual observation — worth a dedicated "does every
     loop branch reach its own exit check" review for future
     bounded-wait designs (evidence: reopen round 3 build, the
     `reclaimed`-flag restructuring in `_update_lock`)
   • SDD · open · §6 summary checkboxes drifted stale relative to fresh
     Refute-read/Advisor verdict prose across this task's own multiple
     reopen-round rebuilds — for a `risk: high`/`autonomy: conservative`
     task, that gap directly misrepresents resolved work to the one
     human whose sign-off is mandatory, not merely a cosmetic lag
     (evidence: `add.py report --decide` surfaced 2 stale unchecked
     items this session before manual reconciliation)
   • TDD · open · a self-heal mechanism cannot distinguish "stale from a
     crash" from "live from a concurrent, in-flight sibling call" — a
     nested/interleaved second call's OWN step-0 self-heal can delete
     the FIRST call's still-in-progress staging directory, causing the
     first (outer) call to raise rather than silently corrupt (a
     strictly better failure mode than the pre-task behavior, but worth
     naming explicitly). Consider a liveness signal (e.g. a PID-stamped
     lock) for a future concurrency-focused task (evidence:
     test_persist_two_interleaved_calls_land_one_full_valid_snapshot,
     independently re-traced by hand by the add-verify pass, not merely
     trusted from the builder's account)
   • TDD · open · a fault-injection mock that raises IMMEDIATELY (before
     writing anything) can fail to discriminate "wrote straight to the
     final name" from "wrote to an isolated staged copy" — both old and
     new code leave the same "nothing at the final name" outcome.
     Strengthen it to write partial/garbage content THEN raise, exposing
     old code's real corruption vs new code's safety (evidence:
     test_restore_mid_stage_failure_earlier_committed_entries_survive's
     mock was strengthened from a bare `raise OSError` to a
     write-then-raise specifically because the immediate-raise version
     passed on both old and new code)
   • ADD · open · the SAME parallel-build-worktree-vs-frozen-contract
     gap diagnosed fully in `global-lock-followups`'s own
     §7/OBSERVE-NOTES.md recurred here too — this task's own `TASK.md`
     needed a manual `git checkout cda1a16 --` sync (commit `735343a`)
     before Ground could even be read, after confirming zero source-code
     drift in the 2 upstream commits being pulled (evidence: `735343a`;
     see `global-lock-followups`'s fuller diagnosis + fix recommendation
     rather than duplicating it here)
   • TDD · open · `mock.patch.object(shutil, "copytree")` intercepts
     `shutil.copytree`'s OWN internal recursive re-invocation for each
     subdirectory it walks, not just the top-level call — an assertion
     assuming "fires once" silently asserts against a nested call
     instead; gate on `Path(source) == the original src argument`
     (evidence: test_scn3_strip_tests_applied_before_commit_not_after's
     traceback showed the assertion firing from inside shutil's own
     `_copytree` recursion)
   • TDD · open · an argument-keyed fault-injection mock (e.g. "raise
     when the rename target equals dest") can accidentally also block a
     LATER, legitimate call sharing the same arguments — such as a
     rollback step that (by design) retries the same destination; needs
     a "fire once, then pass through" flag, not a pure argument
     predicate (evidence:
     test_scn6_commit_land_failure_after_aside_rolls_back — the rollback
     rename targeted the same `dest` the intentionally-failed landing
     rename used, so one predicate blocked both)
   • TDD · open · when a freshly-drafted test's expected value is
     ambiguous, cross-check it against an established FROZEN sibling
     test in the same file before assuming the implementation is wrong
     (evidence:
     test_scn7_stale_staging_leftover_swept_before_new_stage's initial
     `{"restored": 0, "refreshed": 1}` expectation was corrected to
     `{"restored": 1, "refreshed": 0}` after cross-checking the
     pre-existing, untouched test_orphan_swept_not_counted)
   • ADD · open · a per-task git worktree branched ONE commit before an
     upstream freeze-stamp-only commit lands on the integration branch
     produces a start-gate that LOOKS unfrozen (phase/status read DRAFT)
     when the human approval already happened upstream — before
     escalating, check whether it's linear-history staleness (`git
     merge-base --is-ancestor` + a diff restricted to the stamp lines)
     rather than guessing or hard-escalating on a
     technically-true-but-unhelpful reading (evidence: this task's own
     worktree showed `phase: ground`/`Status: DRAFT` at spawn; commit
     `6daad53` on `release/1.15.0`, one commit ahead of the branch
     point, was a pure stamp sync to `phase: contract`/`FROZEN @ v1`
     with an otherwise-empty diff) — see the fuller, cross-task
     diagnosis of this SAME root cause in `global-lock-followups`'s own
     §7/OBSERVE-NOTES.md
   • TDD · open · a concurrency test can look like it proves exclusivity
     while actually proving only liveness —
     `assertGreaterEqual(results.count("acquired"), 1, ...)` is silently
     compatible with MULTIPLE simultaneous winners, the exact violation
     it was named to catch (evidence: this session's own
     `test_concurrent_stale_reclaim_exactly_one_wins`, in both this task
     and its sibling, passed green through round 1's real
     double-acquisition bug; only an adversarial verify pass building
     its own repro — not re-reading the test — surfaced the gap; the fix
     was a temporal peak-concurrent-holders check, not a stronger
     count).
   • ADD · open · a self-heal mechanism whose own bookkeeping can itself
     leak (a lock reclaimed via a ticket file; the ticket itself
     un-swept) needs an explicit "does this recursion terminate" check
     at verify — a build round can correctly fix the REPORTED symptom
     while leaving the same bug CLASS one level deeper, and "no further
     bug found" is a different, weaker claim than "this bug class cannot
     recur here, structurally" (evidence: this session's own 3-round arc
     — a TOCTOU race, fixed by a ticket; the ticket itself leaked, fixed
     by a nested self-heal; only a 4th, explicitly-scoped verify pass
     asked whether THAT fix could leak too, and answered with a
     structural argument — the ticket is a contention filter above the
     one real exclusivity primitive, not a second instance of it —
     backed by 1167+ adversarial attempts, not simply another clean test
     run).
   • SDD · open · a task's own §6 summary checkboxes can silently drift
     stale relative to its Refute-read/Advisor verdict prose across
     multiple build-fix rounds, misrepresenting genuinely resolved work
     as an open judgment call to a `report --decide` reader (evidence:
     this exact session, 2 separate tasks — `global-data-restore-harden`
     earlier, `global-lock-followups` this arc — each needed a manual
     checkbox-to-verdict reconciliation pass before their gate report
     was accurate).

 SPEC DELTAS    37 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              install-update-hardening
════════════════════════════════════════════════════════════════════════