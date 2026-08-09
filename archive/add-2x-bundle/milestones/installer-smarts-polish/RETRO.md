════════════════════════════════════════════════════════════════════════
 installer-smarts-polish · Installer Smarts Polish
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     1/1 done           CRITERIA  1/1 met
 GATES     1 PASS             WAIVERS   none

 goal  Close the PTY-only-reachable interactive-coverage gaps the
       installer-smarts gates disclosed: a reusable PTY test helper that
       drives clack select/confirm so the agent-select step and the
       clack happy-path prompts are exercised in CI (today they are
       node-syntax-checked + logic-unit-tested only).

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 pty-clack-harness           done      PASS 6†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 1/1 met

 LEARNINGS (5 carried)
   • TDD · folded · interactive-TUI tests need a non-zero PTY winsize
     (e.g. 80×24 via TIOCSWINSZ) or the emulator wraps per-character and
     substring markers never match (evidence: happy-path raised
     prompt_timeout until the winsize was set in pty_clack.py) [folded
     foundation-version 40]
   • ADD · folded · a flag-first freeze flag naming the riskiest unknown
     ("clack under a stdlib PTY") localized the ACTUAL bug site —
     flag-first paid off (evidence: the §3 ⚠ assumption was exactly the
     winsize defect) [folded foundation-version 40]
   • TDD · folded · a test that greps its OWN source for a literal token
     is self-referential and unpassable; assert object identity /
     `__module__` instead (evidence: HelperReuseTest had to be
     redesigned mid-build) [folded foundation-version 40]
   • ADD · folded · the tamper tripwire correctly forced human review of
     build/verify test edits; the human-approved re-baseline (phase
     tests → re-advance to re-snapshot) is the sanctioned path, not a
     launder (evidence: gate PASS blocked until re-baseline this loop)
     [folded foundation-version 40]
   • ADD · folded · the engine measures §0 grounding from content INLINE
     on the `Anchors the contract cites:` line — a following bullet list
     reads as empty → false `task_not_grounded` (evidence: check warned
     not-grounded until the anchors were inlined on that line) [folded
     foundation-version 40]

 SPEC DELTAS    15 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              installer-smarts-polish
════════════════════════════════════════════════════════════════════════