════════════════════════════════════════════════════════════════════════
 v10 · Dogfood parallel-streams on fold-support tooling
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  4/4 met
 GATES     2 PASS             WAIVERS   none

 goal  Validate the new streams orchestration by shipping two
       independent fold-support features through it

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 deltas-report               done      PASS 0     ●●●●●●●●
 deltas-lint                 done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (5 carried)
   • ADD · open · cmd_deltas duplicated the delta grammar as a new
     module-level _DELTA_RE instead of reusing the existing one — two
     unguarded sources of truth for the regex (evidence: worker A
     residue; _DELTA_RE added alongside the original ~add.py:1079).
   • TDD · open · the report shows only a delta's first line; a
     multi-line open delta's text is truncated (evidence:
     onboarding-align's wrapped open delta; report tests do not cover
     the multi-line shape).
   • ADD · open · the streams spawn forked the worker's worktree from a
     STALE base (e7e2171, pre-v10), not current HEAD — the worker had to
     recreate the frozen test byte-identically; streams.md should add
     "verify worktree base == HEAD after committing the front"
     (evidence: worker A worktree HEAD = e7e2171).
   • ADD · open · the conservative autonomy dial got its first real
     parallel-run exercise: worker B returned ESCALATE (not PASS) and a
     human recorded the verify gate — the dial's "stop for the human"
     row works (evidence: v10 deltas-lint gate is human-recorded;
     deltas-report ran auto in the same milestone).
   • TDD · open · linting a grammar needs TWO regexes — a broad
     attempt-detector and the strict valid-shape one; conflating them
     would either miss malformed attempts or false-skip them (evidence:
     worker B's _TAG_BROAD_RE vs _DELTA_RE split, accepted at review as
     distinct abstractions).
════════════════════════════════════════════════════════════════════════