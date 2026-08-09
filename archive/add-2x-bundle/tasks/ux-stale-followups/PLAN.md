# TASK: fold the v20 leftovers — soften the fresh-init placeholder goal + retire the stale milestone-done note

slug: ux-stale-followups · created: 2026-06-12 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/templates/PROJECT.md.tmpl` (×3 mirrors: `add-method/tooling/…`, `.add/tooling/…`,
    `add-method/src/add_method/_bundled/tooling/…`) — the foundation template. The goal line (≈L11) renders
    `goal: <the one durable outcome this whole project runs toward — set this at setup; …>` — a NON-empty `<…>`
    placeholder value, so a fresh init echoes the verbose `<…>` raw. **This is follow-up #2's fix locus.**
  - `add-method/tooling/add.py:_project_goal(root) -> str` (def L1834) — reads the first `goal:` line value,
    `… .split(":",1)[1].strip() or GOAL_UNSET`. **DISPLAY-ONLY**: exactly 2 callers, both `print(...)` —
    `cmd_status` (L1081 `goal   :`) and the guide/report orientation block (L907 `goal    :`). NOT read by
    graduation / goal-gate / any control flow. So an UNFILLED goal already degrades to the sentinel via the
    existing `or GOAL_UNSET` — no code change needed, only the template's default value.
  - `add-method/tooling/add.py:GOAL_UNSET` (L33) = `"(unset — add a 'goal:' line to PROJECT.md)"` — the friendly
    sentinel a missing/blank goal degrades to (orientation never blanks/crashes). NOT modified.
  - `add-method/tooling/add.py:cmd_milestone_done` (L1503) — its success tail (L1542-1551) already ends in
    `_next_footer` (next-footer-engine converged the old "Confirm … archive/start the next" hint, comment at
    L1550). A whole-file `confirm` grep returns only unrelated heal/checklist comments — **NO "confirm the boxes"
    prose remains.** So follow-up #1 reduces to RETIRING THE STALE NOTE + a regression guard.
  - `.add/PROJECT.md` (the live foundation) L302-309 — the two stale v21 UX-follow-up notes ("the `milestone-done`
    success line still asks the human to confirm the boxes the gate now ENFORCES"; "a fresh `init`'s `status`
    prints the template placeholder `goal: <…>` verbatim"). **Retiring these = exit criterion 3.**

Context (working folder):
  - The two follow-ups are documented ONLY in `.add/PROJECT.md` L302-309 (a "Key Insights" prose bullet, tagged
    "Two UX follow-ups for v21") — they are NOT in `add.py deltas` (they predate delta tracking). Editing
    `.add/PROJECT.md` touches the HUMAN-OWNED foundation — show the diff at the freeze (show-before-ask), don't
    treat as a routine build edit. Scope-walk-safe (`.add/` excluded), so this is ownership courtesy, not a gate.
  - Style precedent for the softened goal line: the template's `autonomy: auto   <!-- project default … -->` line
    (≈L10) — a value followed by an inline HTML-comment prompt. The softened goal line mirrors that shape.
  - WORDING guards ([SDD] delta from scope-decl-template): a prose-surface edit must pass WORDING_RUBRIC.md +
    the ubiquitous-language / wording-lint suites + the template comment budget — sweep them, not just structure.

Honors (patterns / conventions):
  - SINGLE-SOURCE goal (v20): the goal lives in PROJECT.md, read LIVE by `_project_goal` (never copied to
    state.json). The fix keeps that — it only makes an UNFILLED template goal degrade to the sentinel via the
    EXISTING `or GOAL_UNSET`. `_project_goal`'s return for a REAL goal and a STRIPPED goal is UNCHANGED.
  - ×3 mirror parity (`test_bundle_parity.py`) — a template edit lands BYTE-identical in all three template trees.
  - ADDITIVE (the v20 idiom): every existing PROJECT.md / status / guide line stays; the softened goal line still
    matches `^goal:` so `test_project_goal.py::test_project_template_has_goal_line` stays green.
  - next-footer-engine OWNS the milestone-done tail — #1 honors that boundary: no re-touch of the success line,
    only the stale NOTE goes + a guard pins the absence of "confirm the boxes" prose.
  - EXCLUDED (scope discipline): the `active_milestone` re-aim ([ADD] delta from gate-owner-marker) is a separate
    mechanism (a new verb), not one of the two named v20 follow-ups — left as the recorded delta, not folded here.

Anchors the contract cites: `PROJECT.md.tmpl` `goal:` line (×3) · `_project_goal` + `GOAL_UNSET` · `cmd_milestone_done` success tail · `.add/PROJECT.md` L302-309 · `test_project_goal.py` · `test_bundle_parity.py`. In detail:
  - the `PROJECT.md.tmpl` `goal:` line (×3) — softened to an empty value + inline HTML-comment prompt (mirrors the
    `autonomy:` line), so `_project_goal`'s existing `or GOAL_UNSET` surfaces the sentinel on fresh init.
  - `_project_goal` + `GOAL_UNSET` (the existing empty→sentinel path the fix LEANS ON; both UNCHANGED).
  - `cmd_milestone_done` success tail (already footer-converged — the no-stale-"confirm"-prose guard target).
  - `.add/PROJECT.md` L302-309 (the two stale notes to retire).
  - `test_project_goal.py` (the frozen surface the new red tests extend) · `test_bundle_parity.py` (the ×3 guard).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: retire the two stale v20/v21 UX follow-ups — (a) a fresh `init`'s `status`/`guide` shows the friendly
goal sentinel instead of the raw template placeholder, (b) `milestone-done`'s success output carries no stale
"confirm the boxes" prose (the goal-gate now enforces them), and (c) both stale notes in `.add/PROJECT.md` are retired.

Framings weighed: template-soften (chosen) · code-sentinel in `_project_goal` · shorten-the-placeholder.
  - CHOSEN template-soften: render the template `goal:` line with an EMPTY value + the prompt demoted to an inline
    HTML comment (mirrors the `autonomy:` line), leaning on `_project_goal`'s EXISTING `… .strip() or GOAL_UNSET`.
    `_project_goal` is DISPLAY-ONLY (2 print callers, no control flow) and the PROJECT.md `goal:` line has no other
    reader — so an empty default surfaces the sentinel with ZERO add.py change, no engine_pin ceremony, collision-free.
  - code-sentinel: teach `_project_goal` to detect a placeholder value and return `GOAL_UNSET`. Keeps the inline
    prompt on the goal line, but costs the ×3 add.py byte-sync + engine_pin re-aim + a pin self-test for a
    DISPLAY-ONLY accessor — a blast radius this milestone has been bitten by twice. Rejected unless the human
    wants the inline prompt / code-level robustness (the freeze fork).
  - shorten-the-placeholder: trim the `<…>` text. Rejected — `status` still echoes a raw `<…>` at the most-lost
    moment; it does not fix the root.

Must:
<must>
  - After a fresh `init` with no human-set goal, `status` AND `guide` show the goal sentinel
    (`(unset — add a 'goal:' line to PROJECT.md)`), never the raw `<…>` template placeholder, never blank, exit 0.
  - The template `goal:` line renders an EMPTY value with an inline HTML-comment prompt, and still matches `^goal:`
    (the scaffold carries a goal line — `test_project_template_has_goal_line` stays green).
  - All three `PROJECT.md.tmpl` mirrors stay byte-identical (`test_bundle_parity` green).
  - A REAL (human-set) goal and a STRIPPED goal line keep their existing `_project_goal` behavior UNCHANGED —
    display the goal, resp. the sentinel. `_project_goal`, `GOAL_UNSET`, and `add.py` are NOT modified (ENGINE_MD5
    unchanged; no engine_pin re-aim).
  - `milestone-done`'s success output carries NO "confirm the boxes"-style prose; a regression guard pins the absence.
  - The two stale v21 UX-follow-up notes in `.add/PROJECT.md` (L302-309) are retired (the foundation no longer
    claims these are open) — exit criterion 3.
</must>
Reject:
<reject>
  - none NEW — refinement only; no new error code or control-flow branch. The existing fail-closed invariant
    stands (and is reused, not re-added): an unfilled/blank goal degrades to the sentinel via `or GOAL_UNSET` —
    never blank, never the raw placeholder, orientation never raises (exit 0).
</reject>
After:
<after>
  - fresh-init orientation shows a friendly, actionable goal sentinel; the human is told to set a goal, not shown
    a raw placeholder at the most-lost moment.
  - `milestone-done`'s success line is current — no stale "confirm" prose contradicting the enforced goal-gate.
  - `.add/PROJECT.md` no longer carries the two stale follow-up notes; the engine and its md5 are untouched.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ THE FORK — template-soften (chosen) vs code-sentinel in `_project_goal`. Lowest confidence because it is a
    cost-vs-consistency judgment the human owns, not a testable fact: template-soften is cheaper and collision-free
    (display-only accessor + existing `or GOAL_UNSET`), but demotes the goal prompt to an HTML comment; code-sentinel
    keeps the inline prompt and matches a placeholder-declining idiom but costs the add.py ×3 + pin ceremony. If the
    chosen path is wrong, the cost is re-freezing to the other (a contained change-request — the scenarios/tests
    target the BEHAVIOR, which is identical either way; no thrown work). → surfaced at the §3 freeze.
  - [ ] No OTHER test asserts the exact goal-prompt string beyond `test_project_goal.py`'s `^goal:` — confirm by the
    full-suite run at tests (the frozen-test collision check, per the [ADD] delta). If wrong: a hidden test reddens.
  - [ ] The sentinel wording ("add a 'goal:' line to PROJECT.md") still reads coherently though an EMPTY `goal:` line
    now exists — confirm at the freeze; if it grates, a wording refine is a separate add.py change, deferred.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: fresh-init status shows the goal sentinel, not the raw placeholder
  Given a freshly initialised project whose human has not set a goal
  When I run `add.py status`
  Then the goal line reads "(unset — add a 'goal:' line to PROJECT.md)"
  And the verbose placeholder text "the one durable outcome" does NOT appear
  And the command exits 0 with the rest of status intact

Scenario: fresh-init guide shows the goal sentinel, not the raw placeholder
  Given a freshly initialised project with a task but no human-set goal
  When I run `add.py guide`
  Then the goal line reads the sentinel
  And the verbose placeholder text "the one durable outcome" does NOT appear

Scenario: a human-set goal still renders verbatim (unchanged behavior)
  Given the human sets the PROJECT.md goal line to "ship the thing"
  When I run `add.py status`
  Then the goal line reads "ship the thing"
  And the sentinel does NOT appear

Scenario: a stripped goal line still degrades to the sentinel (unchanged behavior)
  Given the PROJECT.md goal line is removed entirely
  When I run `add.py status`
  Then the goal line reads the sentinel
  And the command exits 0

Scenario: the scaffold still carries a goal line and its foundation sections
  Given a freshly initialised project
  When I read the rendered PROJECT.md
  Then it still contains a line matching ^goal:
  And the Domain (DDD) / Spec / UDD foundation sections are still present

Scenario: the three template mirrors stay byte-identical
  Given the softened PROJECT.md.tmpl
  When I compare the canonical, dogfood, and bundled mirrors
  Then all three are byte-for-byte identical

Scenario: milestone-done success output carries no stale confirm-the-boxes prose
  Given a milestone whose tasks are all done and whose exit criteria are all met
  When I run `add.py milestone-done <ms>`
  Then the success output contains no "confirm the boxes"-style prose
  And it still prints the engine-sourced next-step footer

Scenario: the two stale follow-up notes are retired from the foundation
  Given the live .add/PROJECT.md after this task
  When I read its Key-Insights prose
  Then the "Two UX follow-ups for v21" stale note is gone
  And the surrounding foundation prose is otherwise intact
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Behavioral contract — CLI render + template shape (no HTTP). The frozen surface:

TEMPLATE  tooling/templates/PROJECT.md.tmpl  (×3 mirrors, byte-identical)
  goal line := "goal:" + EMPTY value + an inline `<!-- … -->` prompt   # mirrors the `autonomy:` line
    -> still matches ^goal:  ·  Domain(DDD)/Spec/UDD sections unchanged

_project_goal(root) -> str        # UNCHANGED — pinned by contract, NOT edited
  human "goal: X"      -> "X"
  blank / absent goal  -> GOAL_UNSET = "(unset — add a 'goal:' line to PROJECT.md)"
    # the empty template default now flows through the blank branch -> the sentinel

status / guide   (display surfaces — add.py code UNCHANGED)
  fresh init, no human goal  -> goal line shows GOAL_UNSET; the placeholder text
                                "the one durable outcome" does NOT appear; exit 0
  human goal set             -> shows the goal verbatim (sentinel absent)
  goal line stripped         -> shows GOAL_UNSET; exit 0

milestone-done <ms>  success output
  -> contains NO "confirm the boxes"-style prose  ·  still prints the engine next-step footer

FOUNDATION  .add/PROJECT.md
  -> the "Two UX follow-ups for v21" stale note retired; surrounding prose intact

ENGINE  add.py UNCHANGED — ENGINE_MD5 a4dcc0b… unchanged; NO engine_pin re-aim; GLOSSARY GOAL term unchanged
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-12. Resolution: THE FORK → template-soften (A) — render the
  template goal line with an EMPTY value + an inline comment prompt, leaning on the existing `or GOAL_UNSET`;
  `add.py` UNTOUCHED (ENGINE_MD5 unchanged, no engine_pin re-aim). The `active_milestone` re-aim stays EXCLUDED
  (a separate verb, kept as the recorded [ADD] delta).
Least-sure flag surfaced at freeze: [contract] THE FORK — template-soften (chosen) vs a code-sentinel in
  `_project_goal`. Chosen because `_project_goal` is display-only and the PROJECT.md goal line has no other reader,
  so an empty template default + the EXISTING `or GOAL_UNSET` fixes it with NO add.py change, no engine_pin
  ceremony, and collision-free (the add.py route bit this milestone twice). Cost if wrong: re-freeze to the
  code-sentinel — contained, since §2 scenarios + §4 tests target the BEHAVIOR (identical either way), so no work
  is thrown. Biggest residual risk: demoting the goal prompt to an HTML comment is a UX judgment, not a testable
  fact — that is what the human owns at this freeze.
<!-- Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen contract = change request to SPECIFY. -->


---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior — one test per §2 scenario (8), render-blind (drive the real CLI; read stdout / file bytes).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fresh_init_status_shows_sentinel: init (no goal) / `status` / assert GOAL_UNSET present + the placeholder
    text "the one durable outcome" ABSENT + exit 0.
  - test_fresh_init_guide_shows_sentinel: init + new-task / `guide` / assert sentinel present + placeholder ABSENT.
  - test_human_goal_renders_verbatim: set goal "ship the thing" / `status` / assert the goal shown + sentinel ABSENT.
  - test_stripped_goal_shows_sentinel: remove the goal line / `status` / assert sentinel + exit 0 (unchanged degrade).
  - test_template_carries_goal_line_and_sections: rendered PROJECT.md / assert matches ^goal: + Domain(DDD)/Spec/UDD.
  - test_template_mirrors_byte_identical: canonical · dogfood · bundled PROJECT.md.tmpl / assert byte-identical +
    each renders the goal value EMPTY (no "the one durable outcome" placeholder text).
  - test_milestone_done_no_confirm_prose: milestone + 1 done task (zero exit-criteria) / `milestone-done` /
    assert stdout has NO "confirm the boxes"-style prose + DOES print the engine `next:` footer.
  - test_stale_notes_retired: read .add/PROJECT.md / assert the "Two UX follow-ups for v21" note is ABSENT.
</test_plan>

Tests live in: `add-method/tooling/test_ux_stale_followups.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/PROJECT.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/PROJECT.md.tmpl` `.add/tooling/templates/PROJECT.md.tmpl` `.add/PROJECT.md` `add-method/tooling/test_ux_stale_followups.py`
Strategy (ordered batches): 1. soften the canonical `PROJECT.md.tmpl` goal line — `goal:` with an EMPTY value + an inline `<!-- … -->` prompt (mirrors the `autonomy:` line). 2. mirror byte-identical into the bundled + dogfood template trees (`test_bundle_parity` / `test_tree_parity` green). 3. retire the two stale "Two UX follow-ups for v21" notes in `.add/PROJECT.md`.
Safety rule (feature-specific): the goal line still matches `^goal:`; the three templates stay BYTE-identical; `add.py` and `ENGINE_MD5` are UNTOUCHED (no engine change, no engine_pin re-aim) — a template/doc-only change.
Code lives in: the templates (no `./src/` — this task writes NO Python; the engine is unchanged).
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **932** on python3.14 + python3.10 (both `OK`, 0 fail/0 error); the 8 new tests (test_ux_stale_followups.py) green ×2; `add.py check` 289 passed / 0 failed (13 pre-existing WARNs, none ux-stale-followups — the task_not_grounded WARN was CLEARED by inlining the §0 Anchors line).
- [x] coverage did not decrease — +8 new tests; nothing removed; `test_project_goal.py` / `test_bundle_parity.py` / `test_tree_parity.py` stay green (no frozen-test collision).
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unchanged since the freeze; the red suite (test_ux_stale_followups.py) byte-unchanged since the tests→build snapshot; build touched ONLY the 3 templates + `.add/PROJECT.md` (not a test, not §3). build→verify crossed clean (scope + tripwire passed).
- [x] the green was EARNED — manual adversarial refute (Rule 5; a template+doc change, no engine logic → manual review proportional, not a subagent). 4 refutations HELD: (1) the stale note is ACTUALLY gone — `grep -c "Two UX follow-ups for"` = 0 (the whitespace-normalize fix turned a vacuous-green into a genuine red→green; it was RED for the wrong reason until the line-wrap was handled); (2) `add.py` md5 `a4dcc0b…` UNCHANGED — the engine is truly untouched (no engine_pin re-aim); (3) this repo's REAL goal still renders in full (the template change did not break existing goals); (4) the diff = EXACTLY the declared scope. The 4 new-behavior tests were RED before build, GREEN after; the 4 regression pins green throughout (the red/green partition).
- [x] concurrency / timing — N/A: a static template-text change + one doc edit; pure render, no shared mutable state, no I/O ordering.
- [x] no exposed secrets, injection openings, or unexpected dependencies — template text + a foundation note only; stdlib; no new dependency; the goal prompt is a fixed HTML-comment literal.
- [x] layering & dependencies follow conventions — template-only change; `add.py` UNTOUCHED (ENGINE_MD5 `a4dcc0b…`, no engine_pin re-aim); ×3 template mirrors byte-identical (md5 `a4bfc31…`); the durable goal-gate insight kept, only the stale TODO retired.
- [x] a person reviewed and approved the change   ← the gate (autonomy auto allowed an auto-PASS; presented for a human verdict because the edit touches the human-owned foundation `.add/PROJECT.md` — Tin Dang answered **PASS** and, on the foundation note, chose **pure-delete** over the closure-record alternative; suite re-confirmed 932 OK ×2 after the delete)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — NO new code symbol. The new behavior wires through the EXISTING `_project_goal` `… .strip() or GOAL_UNSET` path: the softened template renders an empty goal value, which flows through the blank branch to the sentinel. Confirmed by the green fresh-init tests + the live dogfood (a fresh init's `status` AND `guide` print `goal : (unset — …)`).
- [x] DEAD-CODE (code) — no new symbol introduced; `add.py` byte-unchanged. No orphan.
- [x] SEMANTIC (prose) — read in full: the template goal region (empty `goal:` + comment, ×3 byte-identical), the `.add/PROJECT.md` edit (the stale "Two UX follow-ups for v21" TODO **pure-deleted** at the gate — the human chose lean-delete over the closure-record draft, so the bullet now ends at "…BEFORE the boxes were checked." and the closure moves to §7/RETRO; the durable v20·UDD goal-gate insight kept), and the sentinel wording. Disclosed residue (assumption #3): the sentinel says "add a 'goal:' line" though an empty `goal:` line now exists — a UX imperfection the human accepted at the freeze; a deferred wording refine → §7.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-13

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a fresh `add.py init` on a no-goal project — `status`/`guide` must surface the `GOAL_UNSET` sentinel, never the raw `<…>` placeholder (the regression pins in test_ux_stale_followups.py double as the monitor).
Spec delta for the next loop: both v21 UX follow-ups are now CLOSED — next-footer-engine had already converged the `milestone-done` tail onto the footer (retiring the "confirm the boxes" prose), and this task softened the template `goal:` line to render EMPTY so a fresh init surfaces the sentinel instead of the placeholder. (This is the closure note the human chose NOT to keep in `.add/PROJECT.md` at the gate — it lives here and folds into RETRO.)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] `_section0_anchors` registers grounding only from INLINE content after "Anchors the contract cites:" on the SAME line — a §0 ground map written as a bulleted list below that line reads as ungrounded, so the §0 template's multi-line shape invites a fill the grounded-check silently rejects; either teach the parser the list form or make "inline on the Anchors line" explicit in the guide (evidence: ux-stale-followups froze with a `task_not_grounded` WARN from `add.py check` until the §0 anchors were inlined onto the Anchors line, which cleared it)
- [TDD · folded] a literal multi-word assertion against prose is vacuously green when the prose line-wraps — the substring never matches the wrapped text, so an absence-check passes for the wrong reason; prose assertions must collapse whitespace first via `" ".join(text.split())` (evidence: test_stale_notes_retired was only 3/4 red — vacuously green on "Two UX follow-ups for v21" because PROJECT.md wrapped it as "for⏎v21" — until whitespace-normalized, then 4/4 red for the right reason)
- [UDD · folded] the `GOAL_UNSET` sentinel text "(unset — add a 'goal:' line to PROJECT.md)" went slightly stale after this soften: an empty `goal:` line now DOES exist post-init, so the imperative "add a 'goal:' line" misdescribes the fix (it should say "fill in the goal:" value); a deferred wording refine the human accepted at the freeze (assumption #3) (evidence: dogfood fresh-init prints `goal : (unset — add a 'goal:' line to PROJECT.md)` while the template now ships the `goal:` line present-but-empty)
- [ADD · folded] CARRY-FORWARD (still open, frozen OUT of this task's template/doc-only scope): no mutating verb re-aims `active_milestone` — it still reads udd-design-foundation while next-step-seams is the active milestone; it remains a separate engine change for a future task (evidence: `add.py status` m-goal line reads `(← udd-design-foundation)` while next-step-seams shows 2/3 status=active)
