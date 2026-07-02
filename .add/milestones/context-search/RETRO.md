════════════════════════════════════════════════════════════════════════
 context-search · Context search
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  2/2 met
 GATES     2 PASS             WAIVERS   none

 goal  Give the AI a fast, keyword-searchable index over the project's
       milestone/task corpus, surfaced at new-scope drafting and inside
       the specify/scenarios phase guides, so related prior work is
       found before drafting -- not after a conflicting design ships.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 search-index                done      PASS 30†   ●●●●●●●●●
 phase-search-wiring         done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   search-index             PASS Tin Dang <tindang.ht97@gmail.com>
   phase-search-wiring      PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 2/2 met

 LEARNINGS (4 carried)
   • ADD · open · running two `add-build`/`add-verify` agent pairs in
     parallel in the SAME working tree (no worktree isolation) caused
     two real cross-task collisions this loop: (1) a line-number anchor
     in a THIRD task's artifact (`seams-doc`'s `.add/SEAMS.md`) drifted
     mid-build because this task's own `cmd_search` insertion shifted
     every symbol after it in `add.py` — caught and disclosed, not
     silent; (2) a scope-lock false-positive fired against `seams-doc`'s
     gate for a file (`test_min_pillar.py`) legitimately touched only by
     THIS task, requiring the established tests→build→advance re-cross
     recovery twice. Parallel streams sharing one working tree are
     viable but need either the re-cross recovery playbook on standby,
     or `isolation: "worktree"` when two tasks' scopes both touch shared
     engine files (evidence: this loop, 2 separate incidents).
   • TDD · open · a refute-read that runs the implementation against
     REAL project data (not just synthetic fixtures) found a genuine,
     untested-by-fixture edge case (`_own_status` falling back to
     `"(unknown)"` for a milestone with no status header) that 30
     passing tests missed — worth a standing verify-agent instruction to
     always spot-check against live data when the corpus is available,
     not just the fixture suite (evidence: this loop's refute-read).
   • ADD · open · a verify pass that independently re-derives a build's
     own disclosed arithmetic (not just re-running its tests) catches a
     class of error fixture-based refute-reads miss: here the rebaseline
     formula (`old + ceil(surface/ratio)`) was recomputed from scratch
     in a fresh Python shell against the raw byte-deltas, confirming the
     shipped literals (20666/75314) to the byte rather than trusting the
     disclosed match — worth keeping as a standing verify-agent habit
     whenever a gate's evidence includes a formula-derived number, not
     just a test-pass count (evidence: this verify pass; no discrepancy
     found, but the check was substantive, not rubber-stamped)
   • ADD · open · `.add/CONVENTIONS.md`'s append-only newest-first
     ordering means a task's Ground-time citation of an older precedent
     (here foundation-version 51, line ~85) can coexist with a NEWER,
     narrower refinement of the same topic (here foundation-version 57's
     "reclaim from the guide's own gloss" carve-out for reframe-only
     edits) without either being wrong — a verify pass should check
     whether a newer entry NARROWS or CONTRADICTS the cited precedent
     before accepting the citation at face value, not just confirm the
     cited line exists (evidence: this verify pass found both entries,
     confirmed they address different edit shapes — new-surface addition
     vs. reframe-only — and neither invalidates the other for this
     task's case)

 SPEC DELTAS    18 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone context-search
════════════════════════════════════════════════════════════════════════