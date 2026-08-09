════════════════════════════════════════════════════════════════════════
 next-step-seams · Next Step Seams
════════════════════════════════════════════════════════════════════════
 VERDICT   DONE
 TASKS     3/3 done           CRITERIA  3/3 met
 GATES     3 PASS             WAIVERS   none

 goal  after every mutating engine verb both the human and the AI see
       the engine-sourced next step and who drives it — next: footer
       plus [you drive] / [human gate] marker

 TASK                        PHASE     GATE TESTS PROGRESS
 ───────────────────────────────────────────────────────────────────────
 next-footer-engine          done      PASS 12†   ●●●●●●●●●
 gate-owner-marker           done      PASS 15†   ●●●●●●●●●
 ux-stale-followups          done      PASS 8†    ●●●●●●●●●
 legend  ● reached  ◉ current  ○ pending   spec→…→done
 † counted at the §4-declared path

 EXIT CRITERIA  ●●●●●●●●●● 3/3 met

 LEARNINGS (14 carried)
   • ADD · open · a task's §3 verb-set can silently collide with a PRIOR
     task's frozen exact-stdout test, and the collision surfaces only at
     full-suite run — not at the contract freeze — forcing a
     change-request after build (evidence: converging init per §3 v1
     would have failed test_brownfield_scan v1's pinned
     greenfield/brownfield output; caught only at the 909-test run,
     resolved by re-freezing §3 v2)
   • SDD · open · "every mutating verb" over-reached as a contract
     phrase — it swept setup/lifecycle verbs (init) whose bespoke
     onboarding output must NOT converge; name the verb CLASS (workflow
     vs setup vs control), not "every" (evidence: §3 v2 carves init out
     as a setup-class EXCEPTION while keeping advance/gate/new-task/… in
     the workflow class)
   • TDD · open · a sweep test that tamper-snapshots its own verb list
     (COMPLETING_VERBS) makes a late "exempt verb X" self-contradictory
     — X ∈ the frozen sweep still demands a next: line — so the
     exemption costs a contract change, not a quick carve-out (evidence:
     exempting lock would have broken test_next_footer_engine's own
     sweep; lock kept the footer and test_setup_lock was strengthened
     instead)
   • ADD · open · the declared §5 scope is FROZEN into state.json's
     anchor at tests→build, so editing §5 prose alone cannot clear a
     scope violation — only a tests→build re-cross re-baselines it
     (evidence: add.py check held the scope_violation until
     reopen→contract→advance re-crossed; the gate reads anchor.declared,
     not live §5)
   • ADD · open · an engine-pin re-aim must CARRY the immediately-prior
     task's "re-aimed @ <slug>" marker because that prior task's
     annotation test asserts it survives (evidence:
     test_scope_violation_heal::test_pin_annotation_names_this_task went
     red when the marker was overwritten; fixed by "supersedes re-aimed
     @ scope-violation-heal" in engine_pin.py)
   • TDD · open · the engine-pin self-test (`re-aimed @ <slug>`) is part
     of the pin idiom, not optional — the red suite must include it from
     ground rather than discover the gap at the verify gate (evidence:
     gate-owner-marker's red suite omitted
     test_pin_annotation_names_this_task; caught at verify, closed by
     re-crossing tests→build→verify with the engine byte-identical, md5
     a4dcc0b unchanged)
   • ADD · open · the driver marker's guide-TEXT (`[you drive]` at
     verify-auto) diverges from the frozen machine-state-json guide
     --json `stop=true`; reconcile via a deliberate change-request
     against the machine-state-json contract, never an in-place edit of
     the frozen JSON (evidence: Option F freeze decision on §3 v1;
     test_machine_state locks JSON `stop = owner != "ai"` per phase)
   • ADD · open · no mutating verb re-aims `active_milestone` — it still
     reads udd-design-foundation while next-step-seams is the active
     work; fold the re-aim into ux-stale-followups (evidence: `add.py
     status` shows active_milestone=udd-design-foundation while
     gate-owner-marker is active under next-step-seams)
   • SDD · open · a §3 contract that broadens an engine verb-set must
     first map which frozen tests lock the old shape; surfacing that
     collision early turned a freeze-blocker into the smaller Option F
     (evidence: the reconcile-with-advisor pivot from "unify JSON stop"
     — blocked by test_machine_state — to Option F, which kept that
     suite green)
   • TDD · open · a contracted-but-unused parameter is a forward-risk a
     self-test should pin — `_effective_autonomy(root, state, slug)`
     ignores `state`, so a future caller passing a stale `state` would
     be silently dropped (evidence: refute-read flagged it low-severity;
     documented in the docstring + §6 DEAD-CODE check, no test guards
     the contract today)
   • SDD · open · `_section0_anchors` registers grounding only from
     INLINE content after "Anchors the contract cites:" on the SAME line
     — a §0 ground map written as a bulleted list below that line reads
     as ungrounded, so the §0 template's multi-line shape invites a fill
     the grounded-check silently rejects; either teach the parser the
     list form or make "inline on the Anchors line" explicit in the
     guide (evidence: ux-stale-followups froze with a
     `task_not_grounded` WARN from `add.py check` until the §0 anchors
     were inlined onto the Anchors line, which cleared it)
   • TDD · open · a literal multi-word assertion against prose is
     vacuously green when the prose line-wraps — the substring never
     matches the wrapped text, so an absence-check passes for the wrong
     reason; prose assertions must collapse whitespace first via `"
     ".join(text.split())` (evidence: test_stale_notes_retired was only
     3/4 red — vacuously green on "Two UX follow-ups for v21" because
     PROJECT.md wrapped it as "for⏎v21" — until whitespace-normalized,
     then 4/4 red for the right reason)
   • UDD · open · the `GOAL_UNSET` sentinel text "(unset — add a 'goal:'
     line to PROJECT.md)" went slightly stale after this soften: an
     empty `goal:` line now DOES exist post-init, so the imperative "add
     a 'goal:' line" misdescribes the fix (it should say "fill in the
     goal:" value); a deferred wording refine the human accepted at the
     freeze (assumption #3) (evidence: dogfood fresh-init prints `goal :
     (unset — add a 'goal:' line to PROJECT.md)` while the template now
     ships the `goal:` line present-but-empty)
   • ADD · open · CARRY-FORWARD (still open, frozen OUT of this task's
     template/doc-only scope): no mutating verb re-aims
     `active_milestone` — it still reads udd-design-foundation while
     next-step-seams is the active milestone; it remains a separate
     engine change for a future task (evidence: `add.py status` m-goal
     line reads `(← udd-design-foundation)` while next-step-seams shows
     2/3 status=active)

 DECIDE NEXT  consolidate learnings + archive-milestone next-step-seams
════════════════════════════════════════════════════════════════════════