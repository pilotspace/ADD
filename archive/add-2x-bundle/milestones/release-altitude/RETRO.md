════════════════════════════════════════════════════════════════════════
 release-altitude · Release altitude — cut a versioned, watched ship
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  4/4 met
 GATES     4 PASS             WAIVERS   none

 goal  A project can cut a versioned, user-facing release that bundles
       one or more closed milestones — the AI drafts evidence-backed
       notes from folded deltas, the engine records the cut behind a
       security-hard-stop readiness floor, and the human owns the
       tag/publish — so shipping a version is a first-class 5th ADD
       altitude, not an ad-hoc ritual.

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 release-guide               done      PASS 11    ●●●●●●●●●
 release-report              done      PASS 8     ●●●●●●●●●
 release-command             done      PASS 12    ●●●●●●●●●
 release-docs-align          done      PASS 6†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (17 carried)
   • ADD · open · a new skill-surface guide must clear TWO wording
     fences, not one — the phrase-level `wording_lint`/WORDING_RUBRIC
     AND the stricter bare-word `test_ubiquitous_language` (bans
     `fold`/`altitude` as whole words in prose, code-span-exempt);
     clearing only the first leaves the engine suite red (evidence:
     tmp/release.md passed wording_lint 0-findings but
     test_slang_absent_extended_surface flagged fold+altitude until the
     prose was purged)
   • ADD · open · the inline-code-span exemption in
     `test_ubiquitous_language` is PER-LINE — a backtick span that wraps
     across two physical lines leaves its first-line banned tokens
     exposed to the bare-word fence (evidence: the `milestone-done →
     fold → …` order arc wrapped two lines → `fold` flagged until the
     whole arc was placed on one line)
   • TDD · open · the §3 freeze flag label is a parsed MACHINE TOKEN —
     the `unflagged_freeze` guard requires the literal `Least-sure flag
     surfaced at freeze:` and rejects any reworded label, blocking the
     tests→build crossing (evidence: `add.py advance` refused with
     unflagged_freeze until the reworded "Lowest-confidence flag
     surfaced for freeze" was restored verbatim)
   • TDD · open · a guide-task's "engine untouched" guard must assert a
     DURABLE invariant (the engine never references the guide FILE),
     never "no <feature> command", when a sibling task will legitimately
     add that command — else the guard reddens on the sibling's landing
     (evidence: test_no_engine_creep scoped to `release.md` not the
     `release` command, so the future release-command task will not turn
     it red)
   • ADD · open · adding a skill guide is not free — it auto-joins the
     wording-lint surface, so BOTH surface-count guards (count +
     membership) must bump in the SAME build; declare them in §5 up
     front (evidence: reused the compact-guide lesson — both guards
     bumped 27→28 with no gate surprise)
   • ADD · open · the §5 scope gate reads `declared` from the state.json
     ANCHOR frozen at tests→build, NOT live §5 — a legitimate mid-build
     scope expansion must amend §5 AND re-cross tests→build to
     re-snapshot, not just edit the prose (evidence: `check` stayed red
     on test_min_pillar.py after the live §5 edit, cleared only after
     `phase tests` → `advance` re-snapshot)
   • ADD · open · a new subcommand redds
     test_min_pillar.test_every_subcommand_is_covered (the
     self-maintaining census) — register it additively in LIFECYCLE,
     exactly as §5's "DISCOVER at build" line pre-warned (evidence: the
     full engine suite went 1 failure → 0 after `LIFECYCLE +=
     release-report`)
   • TDD · open · mirroring the graduation_data harness (temp project +
     add.main capture + direct state seeding) produced 8 honest
     RED-first tests with zero throwaway scaffolding (evidence: the 5
     behavioral tests were RED for the right reason — argparse exit 2 /
     no cue — then GREEN unchanged after build)
   • SDD · open · attribution-via-RELEASES.md-membership (vs a
     per-milestone `released_in:` marker) keeps the cue read-only over
     compacted milestones (evidence: dogfood `status → releasable: 38`
     read only state.json + RELEASES.md, never opened a milestone file)
   • ADD · open · release is a WRITER guarded like cmd_stage with ONE
     divergence — the security reject runs FIRST and has NO `not forced`
     guard, so `--force` can never reach it; modeling "the un-forceable
     reject" as an unguarded leading check is the clean encoding
     (evidence: test_security_hardstop_unforceable + dogfood step 6 both
     refuse under --force)
   • ADD · open · the engine stays tool-agnostic + decoupled by
     RECORDING only (2 markdown files) and NEVER writing state.json —
     attribution lives in RELEASES.md membership, so the cue re-reads
     the ledger and release is a pure 2-file write (evidence:
     test_green_cut_does_not_touch_state + the dogfood cue clears with
     state.json byte-unchanged)
   • ADD · open · `release` writes CHANGELOG.md at the project ROOT, but
     a repo can carry a different changelog convention — this dogfood's
     root CHANGELOG.md is a deliberate POINTER to
     add-method/CHANGELOG.md; release prepends above it (preserving it
     via _prepend_block's header-detection), creating a hybrid that
     contradicts the pointer's intent (evidence: a real `release 9.9.9`
     on this repo prepended a release block above the pointer; the
     generic root-CHANGELOG decision is correct, the nested-package case
     needs doc/awareness — task 4)
   • TDD · open · design-for-failure rollback is testable by
     monkeypatching _atomic_write to fail on the 2nd write — assert the
     1st file is rolled back + state unchanged (evidence:
     test_failed_second_write_rolls_back_first)
   • ADD · open · a tool-agnostic engine cannot run the suite, so
     `release_tests_red` is a recorded-evidence proxy (in-flight build
     w/o a green gate) + the human's real run is the release.md
     readiness backstop (evidence: the §3 freeze flag; accepted at the
     conservative gate)
   • ADD · open · an appended book chapter cannot repair the prior
     chapter's nav footer — chapters 00–15 are byte-frozen, so ch.16
     chains forward-only and the Contents index is the authoritative
     link; an append-friendly book trades perfect prev/next nav for
     byte-stability (evidence: ch.15 still reads "Next: Appendix A" by
     design, test_book_parity green)
   • SDD · open · the wrapped-backtick-arc hazard recurs whenever a
     code-span lifecycle arc wraps to a second source line —
     test_ubiquitous_language's per-line stripper only exempts spans
     closed on the SAME physical line, so a bare "fold" inside
     `milestone-done → fold → …` leaked until the span was single-lined
     (evidence: 16-releasing.md:64 fence hit, fixed by putting the arc
     on one line)
   • TDD · open · a docs-accord guard that asserts the flow arc appears
     VERBATIM in BOTH the book and its source guide buys a real "rename
     re-reds" property cheaply, without duplicating byte-parity (owned
     by the parity tests) (evidence: the RED run failed the book-half
     while the release.md-half already passed — the guard has teeth on
     both sides)

 DECIDE NEXT  consolidate learnings + archive-milestone
              release-altitude
════════════════════════════════════════════════════════════════════════