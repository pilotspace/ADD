════════════════════════════════════════════════════════════════════════
 traceability-ids · Traceability-ids
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     4/4 done           CRITERIA  3/3 met
 GATES     4 PASS             WAIVERS   none

 goal  Give every §1 rule a stable ID (M#/R#) that §2 scenarios and §4
       tests reference, and lint coverage so no Must/Reject ships
       unscenarioed or untested.
 closed by Tin Dang <tindang.ht97@gmail.com>

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 delta-task-backlink         done      PASS 9†    ●●●●●●●●●
 fresh-checkout-skip-tolera… done      PASS 12†   ●●●●●●●●●
 template-structural-gaps    done      PASS 0     ●●●●●●●●●
 rule-id-coverage            done      PASS 13†   ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 GATED BY
   delta-task-backlink      PASS Tin Dang <tindang.ht97@gmail.com>
   fresh-checkout-skip-tol… PASS Tin Dang <tindang.ht97@gmail.com>
   template-structural-gaps PASS Tin Dang <tindang.ht97@gmail.com>
   rule-id-coverage         PASS Tin Dang <tindang.ht97@gmail.com>

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (5 carried)
   • TDD · open · a test that scans a template for placeholder tags must
     reuse the EXISTING frozen tag-census logic
     (`test_scope_decl_template.py`'s bare `[a-z_]+` word census), not
     invent a new placeholder word ad hoc — a bare `<how>` collided with
     that unrelated pre-existing invariant and was only caught by
     running the FULL suite, not the new test file alone (evidence:
     `test_scope_decl_template.py::test_mirrors_and_engine_untouched`
     failure, fixed to `<how / where>` matching the sibling
     Build-expectations block's existing style).
   • ADD · open · a §5 Scope declaration split across multiple physical
     lines is silently truncated to just its first line by the engine's
     snapshot parser — reaffirms the fv29-era "declare §5 Scope on ONE
     physical line" convention, hit twice in one session across two
     different tasks (evidence: both `phase-agents-lean` and this task
     needed a `phase tests <slug>` reopen to re-anchor the scope
     snapshot after an initially multi-line declaration under-captured).
   • TDD · open · a new regex-based convention that scans §2/§4 prose
     must be tested against the template's own UNFILLED placeholder
     default, not just filled examples — this task's `covers: <M#,
     R:code — optional>` placeholder contained the literal substring
     `R:code`, false-matching the tag regex and defeating the
     grandfather gate for every freshly-scaffolded task, until a
     regression test (`test_zero_tags_grandfathers_the_task`) caught it
     before build closed (evidence: the fix — stripping bracketed
     `<...>` placeholder spans before tag extraction — was driven
     entirely by that one regression, confirmed load-bearing by
     add-verify's mutation test).
   • ADD · open · the §5 "Scope (may touch):" parser reads ONLY its
     first physical line, and a BARE repo-root filename token resolves
     as a sibling of the PREVIOUS token's directory, not project root
     (use the `add-method/../<name>` climb form) — this is the THIRD
     task in this project's history to independently hit the
     multi-line-Scope truncation (after `phase-agents-lean` and
     `template-structural-gaps`), each needing the same `phase tests
     <slug>` → `phase build` re-anchor recovery; worth a future task
     making the parser read the whole declaration, not just line one
     (evidence: this task's own §5 Scope needed that exact recovery
     twice — once for the line-wrap truncation, once for the bare-token
     repo-root resolution).
   • ADD · open · an orchestrator doing unrelated parallel work (this
     session: editing `add-verify.md` to fix a persona-loading gap)
     inside the SAME repo while a task's build-scope snapshot is active
     gets caught by the scope-lock tripwire as an out-of-scope touch on
     that OTHER task, even though it shares no code with it — the
     recovery (re-cross tests→build to refresh the baseline) is correct
     but consumes one of the bounded `HEAL_CAP` attempts; worth deciding
     whether cross-task noise like this should count against the same
     cap as a real cheat, or be distinguished from one (evidence: this
     task's `gate PASS` was returned to BUILD once for exactly this
     reason, attempt 1 of 3, before the true redo succeeded).

 SPEC DELTAS    18 open deltas — resolve: new-task --from-delta / drop-delta

 DECIDE NEXT  consolidate learnings + archive-milestone
              traceability-ids
════════════════════════════════════════════════════════════════════════