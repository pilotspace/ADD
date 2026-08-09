# TASK: Folds + extras become AI-proposed, human-confirmed next tasks; goal-gated milestone-done

slug: dynamic-task-loop · created: 2026-06-08 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — changes the MILESTONE lifecycle contract: milestone-done now refuses to close while
     the milestone's exit criteria are unmet (the goal-gate that holds the loop open). A trust-layer edit:
     the dial drops to conservative so a human owns the verify gate; the engine refuses an unguarded
     high-risk completion (`unguarded_high_risk_auto`, run.md guard). The slug-line fields ARE the declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a milestone self-drives toward its GOAL. Two engine changes + a guide tie the v20 loop shut: (1) `milestone-done <slug>` REFUSES to close while the milestone's exit criteria are not all met — the goal-gate that HOLDS the loop open; (2) the status rollup's decide-next line, when every task is done but the goal is unmet, STOPS saying "archive" and instead names the feed-forward inventory (open deltas + planned-but-unscaffolded tasks + reopened tasks) as the source of the next round — so folds + extras become the next tasks, looping until the goal is met. The exit-criteria checkbox IS the human's goal-met affirmation: the engine reads the `- [x]`/`- [ ]` tally, it never judges whether the goal is met. A guide documents the AI-proposes → human-confirms loop; the engine ENFORCES the hold because a guide-only hold is silently bypassable — the exact failure reopen-transition closed for `done`.
Framings weighed: lean hybrid — engine goal-gate on milestone-done (exit-criteria boxes) + decide-next points to the inventory; the propose→confirm loop lives in a guide reusing `_collect_open_deltas`/`_planned_unscaffolded` (chosen — the leanest shape that still ENFORCES the gate; reuses `_exit_criteria`, already built) · an engine `next`/`propose` command that emits next-task stubs (rejected: the engine would JUDGE which deltas become tasks — against "the engine enforces/surfaces, the AI judges, the human confirms") · a guide-only loop with no engine gate (rejected: a hold enforced only by prose is silently bypassable — precisely what reopen made engine-enforced for `done`; the method's value is that the engine enforces, not that the AI is told to behave)
Must:
<must>
  - `milestone-done <slug>` REFUSES to close while the milestone has exit criteria and not all are met (`_exit_criteria` returns total>0 and met<total) -> "milestone_goal_unmet"; the existing all-tasks-done precondition stays — a milestone closes only when BOTH its tasks are done AND its exit criteria are met
  - the exit-criteria checkbox IS the human's goal-met affirmation — the engine READS the `- [x]`/`- [ ]` tally (`_exit_criteria`), it never judges whether the goal is met (same trust model as reading a `gate=PASS`); checking the boxes is the deliberate human act that releases the gate
  - a milestone with NO exit criteria (total==0) closes as before — the gate fires ONLY when criteria EXIST, so every already-done milestone and the existing close path stay valid (the template ships an unchecked placeholder box, so a real milestone has total>0 by default)
  - when every task is done but the goal is unmet (total>0, met<total), the status rollup's decide-next line STOPS saying "archive-milestone" and instead names the feed-forward inventory + how to see it (open deltas via `add.py deltas`; the planned-but-unscaffolded plan-vs-state hint already in the rollup) — the loop's "what next" while the milestone is held open
  - the feed-forward inventory the loop draws from = open deltas (`_collect_open_deltas`) + planned-but-unscaffolded tasks (`_planned_unscaffolded`) + reopened tasks (not-done, carry a `reopens` history); the AI PROPOSES them as next tasks, the human CONFIRMS, the existing `new-task` creates them — turning folds + extras into the next round (no new engine command; the inventory already exists)
  - a guide (skill `loop.md`) documents the dynamic loop: task-complete-but-goal-unmet → gather inventory → AI proposes next tasks → human confirms → `new-task` → … → human checks the exit criteria (goal met) → `milestone-done` succeeds. The milestone-reactivation residual is DEFERRED, recorded not dropped (subsumed: in-loop reopens occur while the milestone is still `active` because the gate held it open; the only residual — reopen in an already-closed milestone — is already surfaced by `check`)
  - the book's loop chapter (`docs/09-the-loop.md`) names the goal-gated milestone close (a milestone holds until its exit criteria are met; folds + extras become its next tasks), mirrored across all 4 book copies
  - INSTRUMENT REACTIONS pre-declared — all THREE guard classes a CLI change trips (reopen-transition's headline lesson, CONVENTIONS:286-298): (1) milestone-done's new precondition ripples to EVERY test that scaffolds a milestone and drives it to done — the `new-milestone` template ships an unchecked exit-criteria box, so each such test must now check it first; KNOWN reactor: `test_min_pillar` LIFECYCLE census (the `milestone-done mvp` step), and the FULL suite during TESTS enumerates the rest; (2) `engine_pin.ENGINE_MD5` re-aimed + add.py mirrored across all 3 copies (canonical · _bundled · dogfood); (3) the new string literals (the reject message, the decide-next line) avoid the ubiquitous-language prose-ban — NO "fold" slang (use "open deltas + unscaffolded plan" / "carried items")
</must>
Reject:
<reject>
  - `milestone-done` on a milestone whose tasks are all done but whose exit criteria are not all met -> "milestone_goal_unmet"
  - (existing, unchanged) `milestone-done` on a milestone with unfinished tasks -> "milestone_incomplete"
</reject>
After:
<after>
  - `milestone-done <slug>` succeeds only when all tasks are done AND (the milestone has no exit criteria OR every exit-criteria box is checked); otherwise it refuses with `milestone_goal_unmet` and the milestone stays `active`; the decide-next rollup, when task-complete-but-goal-unmet, names the feed-forward inventory instead of "archive"; a guide (`loop.md`) documents the propose→confirm loop; the book's loop chapter names the goal-gate; add.py mirrored across trees, `engine_pin` re-aimed, the full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] the goal-gate fires ONLY when exit criteria EXIST (total>0); a milestone with zero criteria closes as before — lowest confidence because it leaves a dodge (a milestone created with no exit criteria is never held by the gate), and "milestone-done holds while GOAL unmet" could be read as "every milestone MUST have criteria"; chosen fire-only-when-present for backward-compat (14 already-done milestones + every milestone-done test predate criteria enforcement) and because forcing criteria-to-exist is a SEPARATE, stricter reject (`milestone_no_criteria`) belonging to its own change; if wrong: add that stricter reject later — a clean addition, no rework of this gate
  ⚠ [contract/test] the instrument reaction is WIDE and has TWO ripples — because the template ships an unchecked `- [ ]` exit-criteria box, (1) EVERY test that scaffolds a milestone and CLOSES it breaks under the gate, and (2) the decide-next change breaks any test asserting the "archive-milestone" rollup line on a task-complete milestone; enumerated known reactors: test_min_pillar (LIFECYCLE census), test_archive_compaction, test_milestone_archive, test_state_hardening (closers) + test_decide_digest::test_footer_done_milestone_fold_archive (decide-next); the FULL suite during TESTS confirms the set; chosen to pre-declare BOTH ripples + enumerate (reopen-transition's headline lesson applied — pre-declare the class AND name instances, don't under-count); cost honesty: each fix is a fixture FILE-WRITE (check or strip the exit-criteria box in the test's MILESTONE.md), NOT a one-line argv append — the LIFECYCLE census is an argv-only loop, so its box is checked/stripped in setUp; bounded and mechanical, but a file-write per reactor
  - [ ] "extras" = open deltas + planned-unscaffolded + reopened tasks (the existing inventory), NOT a separate new channel — confirmed in Diverge; high confidence
  - [ ] the propose→confirm orchestration is GUIDE-level (the AI proposes, the human confirms via existing `new-task`), not a new engine command — confirmed (Framing A); high confidence
  - [ ] the gate touches neither already-done nor archived milestones — it fires only on the `milestone-done` ACTION; retroactive state is untouched (archived slugs are absent from `state["milestones"]`); high confidence
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: milestone-done holds while exit criteria are unmet
  Given a milestone whose tasks are all done
  And its "## Exit criteria" section has an unchecked "- [ ]" box
  When I run `add.py milestone-done <slug>`
  Then it refuses with error "milestone_goal_unmet"
  And the milestone status stays "active" (not "done")
  And no RETRO.md is written (the close did not commit)

Scenario: checking the exit criteria releases the gate
  Given a milestone whose tasks are all done
  And every "## Exit criteria" box is checked "- [x]"
  When I run `add.py milestone-done <slug>`
  Then it succeeds and the milestone status becomes "done"
  And RETRO.md is written

Scenario: a milestone with no exit criteria closes as before
  Given a milestone whose tasks are all done
  And its "## Exit criteria" section has zero checkbox lines (total == 0)
  When I run `add.py milestone-done <slug>`
  Then it succeeds and the milestone status becomes "done"

Scenario: unfinished tasks still block the close (existing, unchanged)
  Given a milestone with at least one not-done task
  When I run `add.py milestone-done <slug>`
  Then it refuses with error "milestone_incomplete"
  And the milestone status stays "active"

Scenario: decide-next names the inventory when task-complete but goal-unmet
  Given a milestone whose tasks are all done
  And its exit criteria are not all met
  When I read the decide-next line of `add.py status`
  Then it does NOT say "archive-milestone"
  And it names the feed-forward inventory (open deltas / unscaffolded plan) as the next step

Scenario: decide-next returns to "archive" once the criteria are met
  Given a milestone whose tasks are all done
  And every exit-criteria box is checked
  When I read the decide-next line of `add.py status`
  Then it says "consolidate learnings + archive-milestone <slug>"

Scenario: the loop guide documents the propose then confirm cycle
  Given the skill guide set
  When I open `loop.md`
  Then it documents task-complete-but-goal-unmet → gather inventory → AI proposes → human confirms via new-task → check exit criteria → milestone-done
  And it records the milestone-reactivation residual as deferred (check surfaces it)

Scenario: the book loop chapter names the goal-gate
  Given the four book copies of "09-the-loop.md"
  When I read the loop chapter
  Then each names that a milestone holds until its exit criteria are met (folds + extras become its next tasks)
  And all four copies are byte-identical

Scenario: the LIFECYCLE census closes a milestone with checked criteria (instrument reaction)
  Given the test_min_pillar LIFECYCLE census drives a milestone to milestone-done
  When the census runs under the goal-gate
  Then it checks the milestone's exit-criteria box before closing
  And the "milestone-done mvp" step still succeeds (the census stays green)

Scenario: the engine change re-anchors the pin and stays mirrored (instrument reaction)
  Given add.py changed (the goal-gate + decide-next line)
  When the suite runs
  Then engine_pin.ENGINE_MD5 matches the new digest
  And all three add.py copies are byte-identical
  And no new add.py string literal uses banned "fold" vocabulary
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py milestone-done <slug>
  ok  (all tasks done AND (no exit criteria OR every box checked)):
        state.milestones[slug].status = "done", .updated = now
        RETRO.md rendered+persisted BEFORE the status flip (fail-closed — existing behavior)
        prints the done summary + the open-delta consolidation nudge (unchanged)
  err "unknown_milestone"    (existing) -> slug not in state.milestones
  err "milestone_incomplete" (existing) -> any task not done, OR no tasks attached
  err "milestone_goal_unmet" (NEW)      -> all tasks done, but _exit_criteria(root, slug) = (met, total)
                                           with total > 0 and met < total; status stays "active";
                                           NO RETRO.md written (refuse BEFORE any write)

Goal-gate precedence (milestone-done): unknown_milestone -> milestone_incomplete (tasks)
  -> milestone_goal_unmet (exit criteria) -> ok. Tasks-first: an unfinished-tasks milestone
  reports milestone_incomplete even when its criteria are also unmet (existing message unchanged).

No back door (verified): `milestone-done` is the SOLE status -> "done" transition. The two downstream
  actions already refuse a non-done milestone — `archive-milestone` dies "milestone_not_done" unless
  status=="done"; `compact` dies "milestone_not_archived" unless already light-archived. So the goal-gate
  cannot be bypassed by archiving an active milestone; enforcing at milestone-done is sufficient.

Exit-criteria read: _exit_criteria(root, slug) -> (met, total) = the `- [x]`/`- [ ]` tally of the
  "## Exit criteria" section of milestones/<slug>/MILESTONE.md (ALREADY implemented; read-only).
  total == 0 (no checkbox lines) -> gate does NOT fire (closes as before).

decide-next (status rollup, _decide_next_base) — when summary.tasks_done == tasks_total:
  - milestone has criteria and they are not all met (total>0, met<total):
        -> "goal not met ({met}/{total} exit criteria) — propose next tasks from open deltas /
            the unscaffolded plan (add.py deltas)"          (NEW branch; the loop's what-next)
  - else (no criteria, or all met):
        -> "consolidate learnings + archive-milestone {ms}" (UNCHANGED)
  Precedence above this branch (HARD-STOP) is unchanged; the line carries no "fold" vocabulary.
  decide-next reads met/total from report data (threaded into d via decide_data/report_data).

Schema (state.json): UNCHANGED — no new field. The gate is computed from MILESTONE.md (the exit-
  criteria checkboxes) + existing task state; milestone status stays {active|done}. No migration.

Prose deliverables (judged in the SEMANTIC deep-check, not in state):
  - skill `loop.md` — the propose→confirm loop + the deferred reactivation residual.
  - book `docs/09-the-loop.md` (×4 copies, byte-identical) — names the goal-gated milestone close.

Engine parity + Instrument reaction — all THREE guard classes, pre-declared + enumerated (reopen lesson):
  - add.py mirrored across all 3 copies (canonical · _bundled · dogfood); engine_pin.ENGINE_MD5 re-aimed.
  - TWO behavioral ripples, both the census/caller guard class:
      (a) milestone-done's new precondition — every test that scaffolds a milestone and CLOSES it must
          check/strip its exit-criteria box first. KNOWN: test_min_pillar (LIFECYCLE census),
          test_archive_compaction, test_milestone_archive, test_state_hardening.
      (b) the decide-next change — every test asserting the "archive-milestone" rollup line on a
          task-complete milestone. KNOWN: test_decide_digest::test_footer_done_milestone_fold_archive.
    Each fix is a fixture FILE-WRITE (write `- [x]`, or remove the box), NOT an argv append; the FULL
    suite during TESTS confirms the set (per §1 ⚠).
  - prose-ban: the new reject message + the new decide-next line carry no banned "fold" vocabulary —
    covered by the existing test_ubiquitous_language (the real ban list), run in the full suite.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-08 (the goal-gated milestone lifecycle, Rule 3; bundle §1–§4 approved at this one freeze; the two ⚠ flags — the total==0 dodge and the WIDE 2-ripple instrument reaction — were surfaced and accepted)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every new branch (the milestone_goal_unmet gate + the decide-next goal-unmet branch) covered; the new add.py lines exercised by a behavioral test.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_holds_while_criteria_unmet: arrange a milestone, all tasks done, an unchecked "- [ ]" exit-criteria box / act `milestone-done` / assert it dies "milestone_goal_unmet" + status stays "active" + no RETRO.md written
  - test_checked_criteria_releases_gate: arrange all tasks done + every exit-criteria box "- [x]" / act `milestone-done` / assert status becomes "done" + RETRO.md written
  - test_no_criteria_closes_as_before: arrange all tasks done + an Exit-criteria section with zero checkbox lines (total==0) / act `milestone-done` / assert status becomes "done" (gate does not fire)
  - test_unfinished_tasks_still_block: arrange a not-done task / act `milestone-done` / assert it dies "milestone_incomplete" + status stays "active" (existing precedence unchanged — tasks before criteria)
  - test_decide_next_names_inventory: arrange all tasks done + criteria unmet / act read the decide-next line of report data / assert it does NOT contain "archive" + names the inventory ("exit criteria" / "deltas")
  - test_decide_next_archive_when_met: arrange all tasks done + criteria all met / act read the decide-next line / assert it says "consolidate learnings + archive-milestone <slug>"
  - test_goal_unmet_message_names_criteria: arrange all tasks done + criteria unmet / act read the milestone_goal_unmet message / assert it guides the human (names "exit criteria" + the met/total count) so the hold is self-explaining (the prose-ban itself is covered by the existing test_ubiquitous_language, not re-asserted here)
  - test_loop_guide_documents_cycle: arrange the skill guide set / act read `loop.md` / assert it documents the propose→confirm cycle (inventory → propose → confirm → new-task → check criteria → milestone-done) + records the reactivation residual as deferred
  - test_book_loop_chapter_names_gate: arrange the 4 book copies of `09-the-loop.md` / act read each / assert each names the goal-gated close (milestone holds until exit criteria met) + all 4 byte-identical
  - test_engine_repinned: arrange add.py changed / act md5 the 3 copies + read engine_pin.ENGINE_MD5 / assert all 3 add.py copies identical AND equal to the pin literal
</test_plan>
<!-- The WIDE instrument reaction (census + the 4 enumerated closer/decide-next reactors) is NOT a test
     here — it is the build-time fixture file-write that keeps the FULL suite green; "stays green" is
     verified by running test_min_pillar etc., never by a meta-test that asserts another test passes. -->

Tests live in: `add-method/tooling/test_dynamic_task_loop.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 616 → 626 green (10 new test_dynamic_task_loop tests, 0 regressions), exit 0
- [x] coverage did not decrease — every Must/Reject has a behavioral test through the real CLI; both new branches (the milestone_goal_unmet gate + the decide-next goal-unmet branch) are exercised
- [x] no test or contract was altered during build — the FROZEN §3 is untouched. The build touched ~12 test files, but every change is the PRE-DECLARED WIDE instrument reaction (§1 ⚠ b + §3 note): each test that scaffolds a milestone (template ships an unchecked box) and CLOSES it gained exit-criteria-meeting setup; the two decide-next reactors gained the same. ALL purely ADDITIVE — `git diff --numstat` shows 0 deletions across the 9 fixture files; NO assertion weakened (independently verified). Plus the surface-count contract (test_wording_lint 19→20, +loop.md), the LIFECYCLE census box-check (test_min_pillar), and the wording_lint docstring count — instrument-reaction maintenance, not weakenings.
- [x] concurrency / timing — N/A: the gate is one read of `_exit_criteria` then the existing single-writer `save_state`; it REFUSES before any write (no RETRO.md on a held milestone), the same model as the existing close path.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new import in add.py; the reject message + decide-next line interpolate only the slug + the met/total counts, never shell.
- [x] layering & dependencies follow CONVENTIONS.md — the gate REUSES `_exit_criteria` (already built); decide-next reads `d["summary"]["exit_criteria"]` (already populated by `report_data`); the engine stays judgment-free (it reads the checkbox tally, it never decides the goal is met); all parity guards green (bundle/tree parity + engine_pin).
- [x] a person reviewed and approved the change — Tin Dang owned the conservative gate and resolved PASS (2026-06-08), consciously re-affirming that the ~12-file WIDE instrument reaction is additive-only (0 deletions, 0 assertions weakened) — the pre-declared reaction the frozen contract approved

### Deep checks — do not skim (this task produced BOTH code and prose — both paths apply)
- [x] WIRING (code) — the goal-gate is wired into `cmd_milestone_done` (the SOLE status→done path; refuses before `_write_retro`); the decide-next branch in `_decide_next_base` reads `d["summary"]["exit_criteria"]`, which `report_data` already populates via `_exit_criteria`. Every new branch is read by a passing test (holds / decide_next_names_inventory / decide_next_archive_when_met / goal_unmet_message). No new symbol added (reuses `_exit_criteria`) — nothing orphaned.
- [x] DEAD-CODE (code) — clean. No new function; the gate is an inline precondition, the decide-next branch is reached and covered. `loop.md` is referenced from `SKILL.md` (discoverable, not an orphan guide).
- [x] SEMANTIC (prose — loop.md + the book) — read in full, not skimmed: `loop.md` (3 skill trees, byte-identical) documents the gather→propose→confirm→new-task loop, the goal-gate, the reopen-is-the-verb tie, and the DEFERRED reactivation residual; the book `09-the-loop.md` (4 copies, byte-identical) names the goal-gated close ("holds until its exit criteria are met"); `SKILL.md` points at `loop.md`. Confirmed by reading each edit — the wording matches the frozen §3 (the gate holds; the checkbox is the human's affirmation; the engine never judges the goal). `loop.md` is on the wording-lint surface and passes (no banned idioms).
- [x] SECURITY — no finding (else mandatory HARD-STOP). No secrets / injection / network / new dependency; the gate is read-only on MILESTONE.md plus a refuse-before-write; add.py md5 == engine_pin (27192f00…, re-aimed; 3 copies + parity green).

### GATE RECORD
Outcome: PASS (conservative, human-gated — Tin Dang owned the gate; the high-risk MILESTONE-lifecycle change earned an explicit human PASS, not an auto-resolve). The evidence: full suite 626 OK exit 0 (616→626, 0 regressions); both new branches behaviorally covered; engine re-pinned 27192f00 (3 add.py copies byte-identical, dogfood carries the gate); every instrument reaction resolved (census + engine_pin + prose-ban + bundle/tree parity + wording-lint surface-count + the WIDE ~12-file milestone-closer reaction — all additive, 0 assertions weakened); §6 Deep checks (WIRING / DEAD-CODE / SEMANTIC / SECURITY) dogfooded; no security finding.
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the `milestone_goal_unmet` rejection rate (a milestone driven to close before its goal is met — a HIGH rate means goals are being treated as a formality, the gate working as designed); the decide-next "goal not met" line appearing in the rollup (the loop is live, consuming its inventory). The two new scenarios — `holds_while_criteria_unmet` + `decide_next_names_inventory` — ARE the monitors.
Spec delta for the next loop: the goal-gate splits "all tasks done" from "milestone done" into two distinct states — the gap between them (task-complete-but-goal-unmet) is now the NORMAL working state of an active milestone, not an error. The next loop should treat the feed-forward inventory (open deltas + unscaffolded plan + reopened tasks) as the milestone's BACKLOG that the loop consumes until the goal is met — the dynamic workflow the milestone v20 goal asked for.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] HEADLINE — the instrument-reaction guard-class set is ARTIFACT-DEPENDENT and LARGER than [[reopen-transition]]'s "three classes" lesson named. A CLI VERB trips three: (1) subcommand census, (2) engine_pin re-aim + 3-copy mirror, (3) ubiquitous-language prose-ban. A NEW SKILL/DOC FILE additionally trips TWO the frozen §3 gestured at ("mirrored across trees") but did NOT name as reaction classes: (4) bundle/tree parity (the file-SET match + byte-identity across the 3 skill trees) and (5) the wording-lint surface-COUNT contract. Evidence: shipping `loop.md` turned test_bundle_parity / test_tree_parity / test_wording_lint::test_surface_files_cover_the_contract (19→20) red until each was updated. Generalize the pre-declaration rubric BY ARTIFACT TYPE — CLI verb → census + engine_pin + prose-ban; new skill/doc file → + bundle/tree parity + surface-count. Fold into CONVENTIONS:286-298 (the "all three guard classes" note) as "the classes depend on what you ship."
- [ADD · folded] the WIDE milestone-closer reaction touched ~12 test files (9 fixtures + test_min_pillar census + test_decide_digest decide-next + test_wording_lint surface-count), confirming §1 ⚠ b's "WIDE 2-ripple" prediction at full scale: a change to a lifecycle PRECONDITION ripples to every test that drives that lifecycle to close, and the cost is one fixture FILE-WRITE per reactor (not an argv append). Root cause is a design choice — the new-milestone template ships an unchecked placeholder box, which (intentionally) makes total>0 by default so the gate is real; that same default is what makes the reaction universal. Evidence: full suite 616→626, every closer test required exit-criteria-meeting setup; all additive (git numstat 0 deletions across the 9 fixtures, 0 assertions weakened).
- [UDD · folded] the `milestone-done` SUCCESS message (add.py:1088 "Confirm the MILESTONE.md exit criteria are checked, then archive/start the next") is now STALE — it asks the human to confirm what the gate (add.py:1070) already ENFORCES: by the time that line prints, every box IS checked (or total==0). Clean prose-only follow-up: drop the redundant "confirm the boxes" ask, keep the archive/next nudge. Evidence: read add.py:1069-1088 — the gate dies before the success path, so the post-success "confirm" can never fail.
- [SDD · folded] the total==0 dodge (§1 ⚠ a, accepted at freeze): a milestone with zero exit-criteria boxes is never held by the gate. The template's placeholder box keeps real milestones at total>0, but a hand-stripped MILESTONE.md reopens it. A stricter follow-up reject `milestone_no_criteria` (refuse milestone-done when total==0) is a clean ADDITION belonging to its own change — it would trip the same WIDE reaction across the 14 pre-v20 done milestones + every criteria-less test, so it needs its own bundle. Recorded as the open candidate, deliberately not built here.
- [UDD · folded] the gate's correctness rests on the human writing REAL, checkable exit-criteria lines — a placeholder box checked without a real goal behind it is goal-met theater (the same failure mode the method warns about for an unearned `gate=PASS`). v20's OWN close is the first dogfood: v20's MILESTONE.md exit criteria must be observable lines or the gate (correctly) holds v20 open. Connects to the project-goal task's "criteria must be checkable" lesson; the trust model (human discipline, surfaced in loop.md) is the only mitigation — the engine reads the tally, it cannot judge whether the box was earned.
