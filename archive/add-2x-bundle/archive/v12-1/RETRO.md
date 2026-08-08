════════════════════════════════════════════════════════════════════════
 v12-1 · Foundation-fold follow-ups
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  Clear the 3 actionable deltas the v10/v12 fold routed out of the
       foundation: surface the unlocked→lock step in status, stop
       truncating multi-line deltas, and collapse the duplicated
       delta-grammar regex to one source.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 delta-grammar-dedup         done      PASS 0     ●●●●●●●●
 status-lock-hint            done      PASS 0     ●●●●●●●●
 deltas-multiline-render     done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (5 carried)
   • ADD · open · comment text must not repeat regex enumeration
     literals — a source-scan test counts all matching lines including
     comments, so a comment containing the pattern registers as a
     phantom duplicate; strip the literal from comment prose (evidence:
     delta-grammar-dedup build, comment line required rewrite to keep
     grep count at 1)
   • ADD · open · when deduplicating a regex, the canonical must absorb
     the deleted copy's form (strict vs permissive) — the old _DELTA_RE
     was strict while _delta_start was permissive; the contract required
     the permissive form because _task_prose feeds un-stripped lines
     (evidence: delta-grammar-dedup §3 CONTRACT v1;
     test_task_prose_recognizes_indented_tag_line)
   • ADD · open · a stream worker's worktree must be VERIFIED to fork
     from the frozen-front HEAD before the run starts — stream B's
     worktree forked one commit behind the front (7f7ee54 vs c896698),
     forcing an in-run cherry-pick of the front and a cherry-pick (not
     merge) integration; streams.md names this check but the
     orchestrator did not run it pre-spawn (evidence: stream B residue
     disclosure; deliverable 16d59a2 parented on a duplicated front
     commit)
   • UDD · open · at the user's most-lost moment the status surface must
     show exactly ONE next step — the unlocked window previously offered
     the generic "/add" or resume hint, competing with the only correct
     move (review SETUP-REVIEW.md, then lock) (evidence:
     test_unlocked_no_tasks_shows_lock_hint red before the build;
     autonomous-setup-guide ADD delta)
   • ADD · open · a fold can route an already-closed delta as an open
     follow-up; the fold ritual should verify a routed delta's gap still
     exists against current code before scoping it (evidence:
     deltas-multiline-render arrived open but was already delivered by
     v11 `1b817c0`)
════════════════════════════════════════════════════════════════════════