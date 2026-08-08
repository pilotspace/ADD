════════════════════════════════════════════════════════════════════════
 v17 · prompt-clarity
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     5/5 done           CRITERIA  5/5 met
 GATES     5 PASS             WAIVERS   none

 goal  Rewrite the agent-facing prompt surface to be literal, direct,
       and positively-framed — with semantics provably preserved —
       without breaking the method's defined vocabulary

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 wording-rubric              done      PASS 31†   ●●●●●●●●
 semantic-inventory          done      PASS 37†   ●●●●●●●●
 rewrite-core                done      PASS 517†  ●●●●●●●●
 rewrite-guides              done      PASS 517†  ●●●●●●●●
 clarity-greenstate          done      PASS 517†  ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (13 carried)
   • TDD · folded · F3 keep-term presence is near-vacuous for SHORT
     substring-prone keep terms like `ADD`/`PASS`/`DDD`/`TDD`/`Role:` —
     they appear so widely a real global rename could leave the
     lowercase substring present and F3 would stay green; F3 guards a
     TOTAL loss, never a PARTIAL rename. Don't oversell F3 in the v17
     retro — semantic-inventory (task 2) + human review own
     rename-safety for these terms; a per-term occurrence-count fix is a
     metric, refused here, so its home is semantic-inventory's per-file
     unit diff (evidence: F3 is a lenient lowercase-substring presence
     check over the whole surface — keep_term_findings in
     wording_lint.py)
   • ADD · folded · §3 carried an internal contradiction —
     substring-of-keep mapped to TWO reject codes, line 49 to
     `ambiguous_ban` and lines 53–54 to `rubric_self_collision` — that
     survived the one-approval contract freeze and was caught only at
     build. A freeze-time self-consistency lint over the CONTRACT's own
     reject-code table, not just the rubric, would have caught it before
     the seam; cheap to add when a contract carries a code table
     (evidence: §6 Disclosed Refinement #2 records the contradiction and
     its resolution)
   • ADD · folded · the gate is near-silent on the surface files that
     carry NO frozen unit — most phase guides hold zero token_layer
     entries + zero invariants, so a GREEN there means "nothing was
     checked", not "meaning preserved"; rewrite-guides must inherit this
     as an explicit input — on those files review + wording-lint + the
     indicative behavioral eval are the ENTIRE safety net, the semantic
     gate adds nothing (evidence: SEMANTIC_INVENTORY.md token_layer
     names 11 files; the surface is 19 — the ~8 unnamed files have no
     semantic-gate coverage by construction).
   • ADD · folded · build ORDER must be derived from a frozen contract's
     BINDING PROPERTIES, not its prose staging order: §3 staged "run.md
     restructure → CR-1", but the binding invariants (CR-1 isolated AND
     gates green after every commit) uniquely forced CR-1 to land BEFORE
     Win 2 — tagging the sections while still listed as narrative would
     have tripped test_engine_narrative_untagged (evidence: commit
     64ebe30 + the green-after-every-commit verification trail)
   • TDD · folded · a deterministic preservation gate is
     NECESSARY-not-SUFFICIENT and must be paired with a human-led
     conservative verify: semantic_inventory proves tokens/anchors
     survived but is blind to an inversion AROUND surviving anchors (an
     added "unless"/scope-narrowing that keeps every anchor word), so
     the conservative verify gate's human diff-read is the real
     protection for that class (evidence: §6 GATE RECORD —
     semantic_inventory 0 findings while the SKILL.md trim still
     required the human's read)
   • SDD · folded · a word-count figure in a contract ("trim ~290
     words") is an ESTIMATE, not a spec obligation: the safe trim was
     180 words and stopping short of the number to avoid cutting
     load-bearing prose was correct — express such targets as "remove
     duplicative content" not a hard count (evidence: trim variance
     disclosed at the verify gate, 180 removed vs ~290 estimated;
     remainder rolls to rewrite-guides)
   • ADD · folded · a staged-by-risk plan can have a LEGITIMATE no-op
     stage and it must be recorded as a finding, not silently skipped: 7
     of the 10 core files were already rubric-clean, so the planned
     "positivize the other core files" commit was a true no-op
     (evidence: commit-2 no-op — 0 wording_lint findings on those 7
     files before any edit)
   • TDD · folded · on a guard-dense surface the per-commit battery must
     grep the tooling tests for pinned needles of EVERY edited line (or
     run the whole suite per commit) — boundary-scoped guard lists miss
     out-of-boundary pins (evidence: test_no_ceremony collision surfaced
     only at task-close → CR-2).
   • ADD · folded · empty-diff-as-evidence: a gate-blind protected class
     is verified by byte-identity, not by gates — show the empty diff at
     the gate as the proof (evidence: `git diff e10150b..HEAD` empty on
     5-build/6-verify/4-tests carried the ⚠ SECURITY escalation to
     resolution).
   • ADD · folded · the conservative gate's human read catches what no
     gate can: of 4 positivizations all gates-green, the human reverted
     exactly the one whose obligation moved (evidence: CR-3 on 0-setup
     L31, directed at the gate with lint/inventory/suite green
     throughout).
   • SDD · folded · positivization has a boundary: when the negative IS
     the obligation ("never clobber"), rewording shifts semantics —
     guide prose should mirror engine semantics verbatim (evidence:
     add.py:353 "never clobber an existing one" matched the original
     L31; the reword silently diverged).
   • ADD · folded · a milestone close needs an exit-criteria ROLL-UP
     with deviations surfaced — a criterion met-with-deviation must be
     ruled on at the close seam, not buried in a delta (evidence: the
     ~290 W→180 W trim deviation lived only in an SDD delta until this
     close).
   • ADD · folded · a behavioral spot-check is steering-evidence, never
     preservation-proof — preservation lives in the review leg of the
     three-leg record (evidence: 9/9 met on over-determined hard-stops,
     with no pre-rewrite baseline to compare against).

 DECIDE NEXT  fold learnings + archive-milestone v17
════════════════════════════════════════════════════════════════════════