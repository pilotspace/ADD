════════════════════════════════════════════════════════════════════════
 foundation-compaction · Foundation compaction — every survivor spec shrinks too
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  6/6 met
 GATES     5 PASS             WAIVERS   none

 goal  A maintainer can keep every foundation spec relevant-first and
       one-screen as the project grows past v50 — append-only records
       read NEWEST-FIRST (recent decisions on top), and at milestone
       close shipped-and-stable entries collapse upward into a per-spec
       rolled-up settled tail while every OPEN residue and the audit
       trail stay live.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 compact-contract            done      PASS 6     ●●●●●●●●●
 invariant-amend             done      PASS 8     ●●●●●●●●●
 compact-guide               done      PASS 6     ●●●●●●●●●
 apply-compaction            done      PASS 7     ●●●●●●●●●
 compact-book-align          done      PASS 7     ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●●●●●●●●● 6/6 met

 LEARNINGS (16 carried)
   • SDD · folded · foundation specs need a PER-SPEC rolled-line
     dialect, not one generalized shape — the four specs' append-only
     forms differ structurally (evidence: compact-contract froze 5
     distinct shapes for 5 spec sections)
   • ADD · folded · a convention-guided method contract (engine stays
     judgment-free) is still TDD-able via a prose contract doc +
     structural asserts (evidence: compact-contract shipped 6 green
     prose-contract tests with zero engine edit)
   • SDD · folded · newest-first ordering and compaction compose into
     ONE invariant amendment (newest on top, settled tail at bottom),
     not two themes (evidence: the ordering enhancement folded into
     invariant-amend mid-intake without a new task)
   • ADD · folded · amending a frozen-invariant DOC means reconciling
     EVERY position-describing sentence, not just the named clause —
     coherence spans the whole ritual (evidence: the clause-only red
     suite missed step5/L34/L39; the added coherence guard caught them)
   • TDD · folded · a byte-identical multi-home edit is provable by an
     md5-parity test + a fail-closed verbatim-transform script
     (evidence: invariant-amend wrote 3 fold.md homes from one source,
     md5 5fdc1c72 across all)
   • ADD · folded · a disclosed boundary AT the verify gate lets the
     human rule the reach explicitly instead of the AI guessing it
     (evidence: PASS accepted the routing-table-verbs boundary at the
     gate)
   • ADD · folded · a frozen contract's prose sketch (a section heading)
     can collide with a SEPARATE frozen engine guard discovered only at
     build; the realization honors the harder engine guard and DISCLOSES
     the deviation at the gate, never silently — and the human, not the
     AI, accepts it (evidence: §3 sketched `## Seam`, engine
     `test_slang_absent_extended_surface` bans "seam" on the surface →
     shipped `## Distinct from add.py compact`, escalated + human-PASSed
     at the verify gate).
   • SDD · folded · adding a new skill-surface guide is not free: the
     wording-lint inventory guards count surface files, so a new guide
     REQUIRES a count+membership registration in those guards — fold
     that into §5 Scope up front (evidence: the new guide turned the
     engine suite 1027→6-fail; `test_wording_surface_count_unchanged`
     24→25 + `test_surface_files_cover_the_contract` membership assert).
   • TDD · folded · §5 Scope is anchored into state.json at the
     tests→build crossing; amending §5 AFTER the crossing requires a
     tests→build re-cross to re-anchor the declared list, else the
     scope-gate refuses the verify gate against the stale anchor
     (evidence: scope_violation persisted after the §5 edit until `phase
     tests` + `advance` re-snapshotted; check 14→13 warnings).
   • UDD · folded · the ubiquitous-language ban is PROSE-ONLY — a banned
     term survives inside a `code span` or fence; user-facing guides
     reference doc names as code-spans (`fold.md`) and use domain terms
     ("retrospective consolidation", "foundation spec") in prose
     (evidence: `fold.md` code-spans pass the scan; bare
     "fold"/"survivor"/"seam" prose failed
     `test_slang_absent_extended_surface`).
   • ADD · folded · foundation compaction is real and safe on living
     docs: reverse-to-newest-first + roll-the-shipped-tail collapsed the
     foundation 1088→575 lines (−47%) with ZERO data loss, verified by
     an independent refute-read against git history (evidence:
     PROJECT.md 399→215, CONVENTIONS.md 689→360; all 58/27/123 records
     byte-match db98f9a).
   • TDD · folded · a destructive in-place transform is made safe by a
     FROZEN pre-state snapshot + a shared parser used by BOTH test and
     transform, so "newest-first kept run reversed" is a list-equality
     assertion (catches any drop/reorder), not a vacuous set check
     (evidence: snapshot_before.json + compaction_lib.split;
     test_reverse_then_roll_order is exact-list).
   • SDD · folded · a per-sequence eligibility predicate beats a single
     global cutoff: §Spec keys on un-fv-stamped prose, §Key-Decisions on
     date, §Method-learnings on max-foundation-version — same "v1–v20"
     intent, three structural tests (evidence: cl.is_rolled branches;
     §Spec rolled 18 None-maxfv bullets where a date/fv cutoff would
     have rolled 0).
   • ADD · folded · a frozen contract's ILLUSTRATIVE integers can be
     miscounted at freeze; honor the binding RULE, implement correctly,
     and disclose the integer drift at the gate rather than retrofit the
     frozen prose (evidence: §3 said §Spec 19→9, the rule rolled 18→10;
     human PASSed the rule-faithful output, §3 left frozen).
   • ADD · folded · the §0 GROUND map undercounted the book mirror
     topology as ×3 when the engine mandates ×4 (the repo-root copy too)
     — grounding a mirror-parity task must enumerate homes from the
     engine's own `test_ground_prose._doc_trees`, not a hand-count
     (evidence: 6 engine sync-guard failures surfaced mid-build + the §3
     ×3→×4 disclosure at verify)
   • TDD · folded · a glossary-term guard that asserts bare substring
     presence is vacuous — the term string recurs inside other entries'
     bodies, so a deleted own-entry still greens; pin the OWN ENTRY by
     the home's native format (bold em-dash / `term:` colon) (evidence:
     refute-read mutation — deleting the `rolled-up settled line` bold
     entry passed the old test, FAILS the hardened one)

 DECIDE NEXT  consolidate learnings + archive-milestone
              foundation-compaction
════════════════════════════════════════════════════════════════════════