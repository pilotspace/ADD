════════════════════════════════════════════════════════════════════════
 delta-resolution · Delta Resolution
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  4/4 met
 GATES     4 PASS             WAIVERS   none

 goal  every delta — spec and competency — has a recorded, engine-driven
       resolution event, so a captured lesson is never a silent dangling
       line

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 spec-delta-grammar          done      PASS 11†   ●●●●●●●●●
 seed-and-drop               done      PASS 8†    ●●●●●●●●●
 spec-delta-guards           done      PASS 5†    ●●●●●●●●●
 fold-command                done      PASS 7†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 4/4 met

 LEARNINGS (10 carried)
   • ADD · folded · a §5 BUILD scope for an `add.py` parser change must
     pre-list the test mirrors, `engine_pin.py`, and the 3
     byte-identical dogfood copies up front — the change ripples to all
     of them (evidence: scope under-declared mid-build forced a
     tests→build re-cross to re-anchor the tripwire) [folded
     foundation-version 36]
   • TDD · folded · before removing a template/placeholder field, grep
     its downstream consumers first — observe-reading tests broke on the
     removed legacy `Spec delta for the next loop:` line (evidence:
     test_report.py 2 regressions surfaced only at full-suite run)
     [folded foundation-version 36]
   • SDD · folded · the domain wording-lint rejects status-name slang in
     new docstrings — document the grammar abstractly, not by spelling
     the status words (evidence: test_sync_guidelines_domain_clean
     failed twice before the reword) [folded foundation-version 36]
   • TDD · folded · a new SUBCOMMAND ripples into test_min_pillar's
     LIFECYCLE census, which derives the command set from `sub.choices`
     DYNAMICALLY — grep `LIFECYCLE`/`sub.choices`/`_NONZERO_OK` before
     adding a subcommand, not just `add_parser`/`--help` (evidence:
     `drop-delta` tripped test_every_subcommand_is_covered after a clean
     pre-build grep, forcing a §5 expansion + re-cross) [folded
     foundation-version 36]
   • ADD · folded · verb-vs-flag sizes the census ripple: a new FLAG on
     an existing command (`--from-delta`) adds no subcommand and is
     census-free, but a new SUBCOMMAND (`drop-delta`) costs a LIFECYCLE
     entry — declare the census file in §5 up front whenever a task adds
     a subcommand (evidence: the flag was free, the verb was not)
     [folded foundation-version 36]
   • ADD · folded · pre-freeze downstream analysis (grep exact-match
     assertions + the subcommand census + compact-fixture SPEC
     injection) eliminated ALL mid-build surprises here — task 2 hit a
     census surprise + scope expansion; task 3 pre-checked the same
     classes and hit ZERO. Codify "scan downstream test assertions
     before freezing an additive engine change" as a §0/§5 step
     (evidence: task 3 needed no §5 expansion, no re-cross) [folded
     foundation-version 36]
   • ADD · folded · seed a downstream task from a prior's SPEC delta via
     `new-task --from-delta`, not plain `new-task` — else the source
     delta stays `open` and (now) BLOCKS compaction even though the work
     is done; the live `status` showed 3 open SPEC deltas that tasks 2/3
     had already implemented (evidence: the guard this task shipped
     surfaced its own milestone's un-seeded lineage — resolve at
     delta-resolution close) [folded foundation-version 36]
   • ADD · folded · the §5 scope-walk must prune code-intelligence tool
     caches (`.serena`), else an agent's OWN source edits churn the
     cache, the build-entry snapshot bakes it in, and the gate flags a
     false out-of-scope touch that exhausts the heal loop to a false
     HARD-STOP (evidence: fold-command verify HARD-STOP, attempts 1–3,
     cache empty yet still flagged because the snapshot recorded it).
     [folded foundation-version 36]
   • ADD · folded · a frozen "any failure → write nothing" clause that
     spans N files needs a TWO-PHASE commit (stage-all → rename-all); N
     independent atomic writes give only per-file atomicity and can
     leave a silent partial (evidence: fold-command verify refute-read
     found a flipped-but-untranscribed silent-loss path, closed via
     `_atomic_write_many` + foundation-first ordering). [folded
     foundation-version 36]
   • TDD · folded · run the FULL downstream + tool-ENVIRONMENT scan
     (here: which dirs the scope-walk excludes vs. which tools write to
     the tree) BEFORE freezing — the spec-delta-guards "scan downstream
     before freeze" lesson extends past test assertions to the agent's
     own toolchain side-effects (evidence: the serena-cache HARD-STOP
     would have been foreseen by a pre-freeze tool-artifact scan).
     [folded foundation-version 36]

 DECIDE NEXT  consolidate learnings + archive-milestone
              delta-resolution
════════════════════════════════════════════════════════════════════════