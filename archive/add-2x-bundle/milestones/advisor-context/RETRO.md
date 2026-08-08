════════════════════════════════════════════════════════════════════════
 advisor-context · Advisor Context
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  5/5 met
 GATES     3 PASS             WAIVERS   none

 goal  every ADD step carries richer AI-facing context — a tool-agnostic
       advisor strategy for spawning a plan-following subagent, and an
       advisory confidence self-score rubric — so any agent driving the
       loop knows when to delegate and how to self-assess, without the
       engine ever spawning or gating on it

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 confidence-rubric           done      PASS 8†    ●●●●●●●●●
 advisor-strategy            done      PASS 8†    ●●●●●●●●●
 per-step-hooks              done      PASS 5†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 5/5 met

 LEARNINGS (4 carried)
   • ADD · open · authoring the implementation during the SPECIFY phase
     makes the tests->build scope snapshot capture an already-built
     tree, so the scope-gate becomes a no-op — author code IN the build
     phase so the gate meaningfully checks touched ⊆ declared (evidence:
     advisor-strategy built pre-advance; task 1 confidence-rubric was
     caught by the scope-gate when a guard edit was undeclared)
     (evidence: scope_violation heal on confidence-rubric)
   • SDD · open · a new skill engine doc silently breaks two guards that
     pin the surface inventory — test_xml_convention.ENGINE_FILES
     (registration) and test_wording_lint surface COUNT — both must be
     declared in §5 Scope BEFORE tests->build (evidence:
     confidence-rubric scope_violation on test_wording_lint.py)
   • ADD · open · richer per-step AI context is best delivered as a THIN
     per-guide pointer to a shared strategy/rubric doc, not inline prose
     — progressive disclosure keeps the 8 guides minimal while the depth
     lives in advisor.md/confidence.md (evidence: 8 one-line hooks + 2
     docs delivered the whole enhancement with no guide bloat)
   • TDD · open · a content guard that enumerates the FULL set it covers
     (all 8 guides) + asserts mutual distinctness blocks both the
     missing-item cheat and the boilerplate cheat — a count/membership
     guard is the test-pattern for "every X has Y" doc requirements
     (evidence: test_per_step_hooks.test_every_guide_hooked +
     test_hooks_distinct)

 DECIDE NEXT  consolidate learnings + archive-milestone advisor-context
════════════════════════════════════════════════════════════════════════