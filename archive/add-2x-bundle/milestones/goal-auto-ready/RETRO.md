════════════════════════════════════════════════════════════════════════
 goal-auto-ready · Goal-auto-ready — goal-clarity earns autonomy
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     2/2 done           CRITERIA  3/3 met
 GATES     2 PASS             WAIVERS   none

 goal  a goal is auto-ready when its acceptance criteria are concrete
       enough for the engine to self-verify the result against — so
       autonomy is earned by goal-clarity, not assumed (with auto seeded
       as the project default)

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 init-auto-default           done      PASS 8†    ●●●●●●●●
 goal-auto-ready-gate        done      PASS 13†   ●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (7 carried)
   • ADD · open · a declaration-token reader must anchor to a
     declaration POSITION (line-start or `·`-separator) — a freeform H1
     title or quoted prose containing `token: value` must never be read
     as a declaration, and the symmetric hazard (a title faking a
     lowered rung) can defeat a guard (evidence: init-auto-default
     titled "…autonomy: auto…" read as `auto` despite declaring
     `conservative`, `_autonomy_level -> auto`; fixed @ 55d64d9,
     anchoring both the autonomy and risk readers).
   • SDD · open · a project's autonomy posture is a project-level
     INHERITABLE default (`auto`), declared in PROJECT.md and surfaced
     in status — not a constant buried in the task template; `new-task`
     inherits the declared rung, fail-SAFE (absent→auto,
     garbled→conservative) (evidence: init-auto-default shipped
     `_project_autonomy` + the load-bearing
     `test_non_auto_default_inherited`).
   • SDD · open · an `init --autonomy <level>` CLI knob (a non-auto
     project default set at init) was DEFERRED as YAGNI for "auto
     default" — record it so a future "configurable default" need is not
     re-discovered from scratch (evidence: weighed + rejected in the
     init-auto-default framings at freeze).
   • ADD · open · the build must stay INSIDE the frozen contract even
     for "harmless additive" changes — a bonus `project_autonomy` key on
     `status --json` was caught by the frozen-surface guard and
     reverted, not test-edited (evidence: test_json_surface_frozen fired
     `json_surface_unsanctioned_key`; the JSON key was removed, the
     frozen test left intact).
   • TDD · open · a "live-only" guard must key on the milestone's
     terminal STATUS, not just the active-pointer + dict-membership —
     the build missed the done-but-not-yet-archived window (status=done
     stays the active pointer until `archive` clears it), so the WARN
     briefly fired on a closed milestone; the verify adversarial pass
     caught the Must #4 violation and closed it test-first (evidence:
     `test_done_active_milestone_not_flagged` RED before the `status !=
     "done"` guard → full suite 747 OK after).
   • ADD · open · verifier-citation RAISES the goal-clarity floor but
     cannot PROVE a citation is honest — `(verify: it works)` passes the
     lint (citation-theater); the irreducible-floor rule accepts this,
     and the stronger bar (resolve a cited test in the suite / shell a
     cited command) is the deferred upgrade (evidence: §3 freeze flag;
     `test_empty_verify_paren_does_not_count` guards only emptiness,
     never honesty).
   • ADD · open · `_exit_criteria_cited` guards `exists()` but not
     `read_text()` against OSError, diverging from the sibling
     `_project_autonomy_token` which DOES (the design-for-failure rule);
     left as a recorded ceiling — it mirrors the `_exit_criteria`
     convention, so hardening one read-path without the other would
     split the convention (evidence: advisor non-blocking note; both
     classifier read-paths currently unguarded).

 DECIDE NEXT  consolidate learnings + archive-milestone goal-auto-ready
════════════════════════════════════════════════════════════════════════