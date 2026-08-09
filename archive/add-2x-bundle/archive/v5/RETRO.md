════════════════════════════════════════════════════════════════════════
 v5 · The Self-Improving Foundation
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  1/5 met
 GATES     3 PASS             WAIVERS   none

 goal  Turn ADD's five competencies into a self-improving loop: each
       task's learnings, tagged by competency and human-confirmed, fold
       into a versioned PROJECT.md that sharpens DDD·SDD·UDD·TDD·ADD
       across milestones

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 competency-deltas           done      PASS 0     ●●●●●●●●
 foundation-update-loop      done      PASS 0     ●●●●●●●●
 cospecify-lift              done      PASS 0     ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done

 EXIT CRITERIA  ●●○○○○○○○○ 1/5 met

 LEARNINGS (6 carried)
   • ADD · folded · the dogfood `.add/tooling` template can silently
     diverge from the canonical `add-method` copy; no test guards the
     parity (evidence: md5 mismatch caught manually this build)
   • TDD · folded · structural tests guard canonical artifacts but not
     their git-tracked dogfood twins — 3rd recurrence of this gap class
     (evidence: scope-loop OBSERVE note + this build)
   • TDD · folded · a contract that lists a shipped artifact MUST also
     list its guard test, or the artifact ships unguarded (evidence:
     this task's v1 contract enumerated the "Foundation version"
     glossary entry as an artifact but not as a test → disclosed gap →
     required a v2 change-request). Folded 2026-06-03 via the
     change-request that added test 12 (entry-presence in all 3 doc
     trees).
   • ADD · folded · the human↔AI brainstorm was specified only at task
     §1; lifting the same three-move to the milestone (scope.md) and
     foundation (0-setup.md) altitudes closed the "template-driven, not
     dialogue-driven" gap at intake/setup (evidence: this task —
     scope.md + 0-setup.md now teach diverge-before-draft). [folded
     foundation-version 7 → CONVENTIONS.md "Co-specify at every
     altitude"]
   • SDD · folded · the spec/foundation is shaped by elicitation
     quality, not just template prompts; naming the five diverge seeds
     and four foundation lenses makes the SDD layer's "ask before draft"
     enforceable (evidence: test_cospecify_lift asserts the seeds/lenses
     are present). [folded foundation-version 7 → PROJECT.md §Spec "SDD
     is elicitation-driven"]
   • TDD · folded · prose-guide tasks are red/green-testable too: assert
     content anchors + cross-tree byte-identity instead of behavior
     (evidence: test_cospecify_lift went red→green; test_bundle_parity
     backstops drift). [folded foundation-version 7 → CONVENTIONS.md
     "Prose-guide tasks are red→green-testable"]
════════════════════════════════════════════════════════════════════════