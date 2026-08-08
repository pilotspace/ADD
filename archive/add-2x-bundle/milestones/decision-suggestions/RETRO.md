════════════════════════════════════════════════════════════════════════
 decision-suggestions · Decision suggestions — a recommended pick + described alternatives at every human gate
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  At every human decision point (baseline-lock, contract freeze,
       verify, intake, scope, milestone close, graduation, release,
       human-gated advance) ADD presents a highlighted recommended
       choice plus its real described alternatives, so the human decides
       with the recommendation and its consequences in view instead of a
       bare next-step line.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 suggestion-block            done      PASS 7     ●●●●●●●●●
 gate-wiring                 done      PASS 5     ●●●●●●●●●
 suggest-book-align          done      PASS 5     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (10 carried)
   • ADD · open · the decision-suggestion convention dogfooded its own
     gates — the milestone-confirm, the §3 freeze, and the verify gate
     all rendered as guided choices (▶ recommended-first + per-option
     descriptions) in the very convention being built (evidence: the
     three AskUserQuestion asks in this run used the recommended-pick +
     described-alternatives shape)
   • SDD · open · a prose-convention contract freezes a TOKEN SET +
     structural invariants, not an HTTP shape — §3's checkable seam
     (tokens T1–T6 + invariants I1–I4 + 3 reject codes) is the
     dependable gate the two downstream tasks build against (evidence:
     test_suggestion_block asserts the token set; engine byte-identical,
     bundle-parity green)
   • TDD · open · for a prose feature the red suite splits into RED
     feature-token tests + STAY-GREEN invariant guards (five-block ·
     no-new-tag · home-parity) — "red for the right reason" comes from
     the feature tokens while the invariants guard regression during the
     3-home edit (evidence: 3 fail / 4 pass at the red run → 7/7 after
     build)
   • ADD · open · `after EVIDENCE` and `Least-sure flag surfaced at
     freeze:` are PARSED prose tokens an automated guard reads — the
     freeze guard refused `advance` until the literal label was present
     (evidence: unflagged_freeze on the first tests→build advance
     attempt)
   • TDD · open · a guide-tag lint that greps `</?tag>` false-positives
     on prose PLACEHOLDERS (`<name>`, `<slug>`) — match CLOSING tags
     only (`</tag>`), since real block tags are paired but placeholders
     never close (evidence: test_no_new_tag first failed on
     `<assumption>`/`<slug>`; fixed to closing-only)
   • SDD · open · the on-demand guides (intake.md · scope.md ·
     release.md) carry the engine-doc tags `constraints`/`reject_codes`,
     not just the phase-guide trio — a per-guide tag-vocab check must
     use the FULL closed-5 vocab, not the phase-guide subset (evidence:
     test_no_new_tag failed on intake.md's `</reject_codes>` until the
     set was widened)
   • ADD · open · a MILESTONE.md exit criterion can over-enumerate the
     work (a phantom "human-gated-advance" 9th gate) — the wiring task
     reconciled EC2 to the real 8 guides, the recorded change-as-method
     move (evidence: M5 reconcile; test_milestone_ec2_reconciled went
     red→green)
   • ADD · open · task 2 ran `auto` (method-APPLYING) where task 1 ran
     conservative (method-DEFINING) — the same milestone discriminates
     autonomy by which kind of change a task makes, not by milestone
     theme (evidence: gate-wiring auto-resolved verify; suggestion-block
     human-gated)
   • SDD · open · a docs-accord task that DESCRIBES a convention (vs
     specifies it) verifies by own-entry-regex + cross-tree md5 + a
     points-at-source assertion — the book stays a pointer, never a
     second source of truth (evidence:
     test_book_points_at_report_template asserts the entry references
     report-template.md, not the rules) (evidence:
     test_suggest_book_align 5/5)
   • ADD · open · the decision-point UX now has a complete trail —
     convention (report-template.md) → 8 gate cues → book+glossary — so
     a reader meets "guided decision" at the flow narrative, the
     glossary, and every guide (evidence: decision-suggestions milestone
     3/3 across suggestion-block · gate-wiring · suggest-book-align)

 DECIDE NEXT  consolidate learnings + archive-milestone
              decision-suggestions
════════════════════════════════════════════════════════════════════════