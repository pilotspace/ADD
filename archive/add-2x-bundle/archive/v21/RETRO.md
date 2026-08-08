════════════════════════════════════════════════════════════════════════
 v21 · V21
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  a reader of the ADD book can trace the method's intellectual
       lineage — recursive self-improvement, spec-driven development,
       agentic + tests-first research — and see ADD as the human-gated,
       evidence-trusted instance of 'closing the loop', grounded in
       verified, citable sources woven through the book

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 references-appendix         done      PASS 7†    ●●●●●●●●
 foundations-chapter         done      PASS 9†    ●●●●●●●●
 inline-citations            done      PASS 16†   ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (12 carried)
   • ADD · open · the instrument-reaction prediction in the contract
     parity-note was INCOMPLETE — a new `add-method/docs/*.md` trips the
     ubiquitous-language EXTENDED surface (`extended_surface()` globs
     all docs + skill + templates + diagrams + README +
     GETTING-STARTED), not just the 19-file wording-lint surface the
     note named. Evidence: build hit 2 ubiquitous-language failures
     (`fold` / `collapses to`) on the new appendix, fixed via code-span
     exemption. Fold: when a task adds a doc, predict the EXTENDED lint
     surface, not only the wording-lint count.
   • TDD · open · the frozen invariant "exactly one entry per cite-key"
     has NO test enforcing uniqueness —
     `test_every_entry_is_well_formed` asserts each entry HAS a key, not
     that keys are DISTINCT; a duplicate key would ship green. Evidence:
     advisor review. Fix: add a key-uniqueness assertion to
     `test_references_appendix.py`.
   • SDD · open · cite-key suffix-assignment ORDER (2025a/b/c, 2026a/b)
     is deterministic-by-appendix-lookup but UNDOCUMENTED in "How to
     cite"; the 2 downstream tasks lock to these keys. Evidence: advisor
     review. Fix: a one-line "suffixes assigned in reading order" note
     hardens foundations-chapter + inline-citations.
   • ADD · open · VERIFY teeth must extend past link-resolution to
     load-bearing FIGURES for a grounding doc — the §6 SEMANTIC line
     over-claimed ("read in full") until the 2 citable numbers (PGR 0.97
     / 5-days-vs-7 · >80% Claude-authored / four-month doubling) were
     spot-checked against primary sources this pass; both confirmed
     verbatim. Evidence: advisor caught the overclaim. Fold: add
     "spot-check load-bearing quantitative claims" to the verification
     mechanism for citation/grounding docs.
   • TDD · open · the resolution test
     (`test_every_inline_cite_resolves`) matches one `[Author Year]` per
     bracket, so it reads appendix-g's `;`-joined multi-cite form `[A;
     B]` as a single dangling key — directly blocks task 3's inline
     weave (evidence: 2 red→green build fixes where `[GitHub 2025; GSD
     2025]` and `[Anthropic 2025c; Anthropic 2026b]` had to be rewritten
     to single-key brackets to stay green).
   • ADD · open · a frozen offline resolution test proves cites RESOLVE
     but is silent on internal narrative consistency — two counting
     contradictions ("three currents" vs the four-currents heading;
     "three measured facts" enumerated as two) passed 642-green and were
     caught only by an advisor-assisted human read pre-gate; the VERIFY
     SEMANTIC check for a PROSE deliverable must include a
     counting/consistency pass, not just "read in full" (evidence: 2
     pre-gate prose fixes, no test ever flagged them).
   • UDD · open · the dogfood book copy `.add/docs/` drifts silently —
     it is gitignored and NOT covered by `test_bundle_parity` (which
     guards only canonical↔`_bundled`), so its README had pre-existing
     drift (missing the ch.14 line) discovered only while wiring ch.15;
     either extend parity to the dogfood README or accept it as a
     known-throwaway install artifact (evidence: ch.14 line restored in
     `.add/docs/README.md` at this boundary).
   • SDD · open · the §1 assumption modeled the chapter as a "sparse
     subset" of appendix-g, but a lineage/survey chapter's natural
     density is near-complete — it wove 26/27 keys, each load-bearing; a
     survey-chapter spec should predict near-full coverage, not a subset
     (evidence: 26/27 keys cited, 0 dangling, no bare name-drops).
   • TDD · open · a green resolver proves cites RESOLVE but is BLIND to
     citation APTNESS — whether the source grounds the claim. The fix is
     a §6 PRIMARY-SOURCE check for any claim more specific than the
     appendix annotation; annotation-match suffices only when the claim
     is no more specific (evidence: `[Yuan et al. 2024]`'s "drifts"
     overstatement passed 649-green and was caught only by WebFetch of
     arxiv 2401.10020 — the paper shows self-rewarding *improves*).
   • ADD · open · the aptness blind-spot is the THIRD instance of the
     teeth/aptness lesson this milestone — task 1 a FORM test missed
     link-existence (URL teeth), task 2 a RESOLUTION test missed
     narrative consistency (two contradictions passed 642-green), task 3
     the resolution test missed aptness. The pattern: a passing
     structural test reads as sufficient when it is only necessary; the
     standing fix is a named human SEMANTIC check the resolver is
     declared blind to (evidence: §1 ⚠ flag + §6 SEMANTIC across all
     three tasks).
   • SDD · open · a per-task FROZEN scope (here 02/03/09) correctly
     bounds the deliverable but can leave the SAME defect in an
     out-of-scope committed chapter (15) un-fixed — the method needs a
     "cross-task finding → reopen" path so a defect found while working
     task N can be fixed in already-done task M without silently editing
     outside scope (evidence: chapter 15 line 41 carries the same Yuan
     framing; surfaced at this gate, sequenced as a foundations-chapter
     reopen).
   • ADD · open · the annotation-vs-source distinction is now explicit:
     task 1's appendix annotation verified existence + title + author,
     NOT characterization depth — so a chapter claim leaning on the
     *characterization* must go to the primary source, not the
     annotation (evidence: chapter-15 annotation is apt while its prose
     overstated — same source, two fidelity levels).

 DECIDE NEXT  consolidate learnings + archive-milestone v21
════════════════════════════════════════════════════════════════════════