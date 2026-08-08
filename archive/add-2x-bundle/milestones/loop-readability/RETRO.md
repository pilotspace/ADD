════════════════════════════════════════════════════════════════════════
 loop-readability · ADD loop readability — human-scannable output across every phase
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  3/3 met
 GATES     2 PASS             WAIVERS   none

 goal  every report/ask the AI gives a human at a phase's decision point
       (the ARC +
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 report-shape-scan-audit     done      PASS 0     ●●●●●●●●●
 skill-banner-cue            done      PASS 0     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 GATED BY
   report-shape-scan-audit  PASS Tin Dang <tindang.ht97@gmail.com>
   skill-banner-cue         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (4 carried)
   • ADD · open · always run `add.py freeze --by "<name>"` for a
     contract approval, never hand-edit `Status: DRAFT` → `FROZEN` — the
     command's own `_flag_well_formed` pre-check catches a malformed
     lowest-confidence-flag label BEFORE presenting to the human, and
     its write path records the structured `state.json` freeze entry a
     hand-edit silently skips (evidence: this task's freeze was
     hand-stamped, and the label mismatch it let through wasn't caught
     until `add.py advance` refused the tests→build crossing).
   • ADD · open · the established "Least-sure flag surfaced at freeze:"
     convention (singular "flag", colon immediately after, "Second
     flag:" for a 2nd point) is enforced by an exact-string engine
     regex, not just a style preference — a hand-drafted §3 that
     paraphrases this heading (e.g. plural "flags" + a parenthetical
     before the colon) reads fine to a human but fails
     `_flag_well_formed` silently until the build-crossing gate
     (evidence: this task's own §3, confirmed against 10+ other frozen
     tasks in `.add/tasks/*/TASK.md` all using the identical exact
     phrasing).
   • ADD · open · the §5 "Scope (may touch):" declaration parser
     (`_declared_scope` in add.py) reads ONLY the first physical line
     after the label — `re.search(r"^\s*Scope \(may touch\):.*$", body,
     re.M)` has no `DOTALL`, so `.` never crosses a `\n`. A Scope line
     wrapped across multiple physical lines (readable to a human,
     matches how §0/§1/§3 prose wraps everywhere else in this same file)
     silently drops every token past line 1 from `declared` — no
     warning, no lint, just a quiet gap that only surfaces later as a
     `scope_violation` at the gate. Always keep the token list on ONE
     physical line; wrap explanatory prose onto a SEPARATE following
     line instead (evidence: this task's own v1 draft dropped its 3rd
     mirror path this way, caught at `gate PASS`).
   • ADD · open · the §5 scope-lock's protection is only as real as its
     SEQUENCING: `declared` + the touch-baseline snapshot are captured
     ONCE, at the tests→build phase crossing (`_build_entry`'s
     scope-snapshot block) — never re-derived at gate time. Editing
     files BEFORE crossing tests→build (e.g. applying the AMEND while
     still nominally in `tests`) means those edits are already baked
     into the snapshot, so the gate sees zero delta and the check
     silently no-ops — a clean `gate PASS` in that case proves nothing
     about scope discipline. Editing files AFTER the crossing (the
     documented/correct order) is what actually exercises the check.
     Evidence: the sibling task `report-shape-scan-audit` edited all 6
     mirrored files before ever calling `advance` into build, so its own
     scope-lock never fired despite 4 of its 6 touched files also being
     undeclared past line 1 — an accidental pass, not a verified one.
     This task followed the correct order and the check caught a real
     gap. `add.py phase build <slug>` re-runs the identical guard stack
     on demand — the documented recovery path (matches the project's own
     prior `build_tampered` re-cross precedent), not a workaround.

 SPEC DELTAS    25 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              loop-readability
════════════════════════════════════════════════════════════════════════