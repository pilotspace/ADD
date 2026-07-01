# TASK: Fold 3 MUST-have TASK.md.tmpl gaps: glossary deltas, scenario IDs, live-verify evidence block

slug: template-structural-gaps · created: 2026-07-01 · stage: mvp
milestone: traceability-ids
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/templates/TASK.md.tmpl` (203 lines) — the canonical template, plus its 2
    byte-identical mirrors `.add/tooling/templates/TASK.md.tmpl` (dogfood) and
    `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` (npm-bundled) — confirmed
    byte-identical via `diff` before this task started. §2 SCENARIOS (l.55-69) has no scenario-ID
    slot (`Scenario: <short name>` only). §3 CONTRACT (l.73-89) ends at `Schema: <tables/fields
    touched, and access pattern>` with no glossary-delta line; carries exactly 1 ``
    comment (l.83-89, the freeze-instruction block). §6 VERIFY (l.134-183) sub-blocks run, in
    order: checklist bullets → `### Build expectations` → `### Deep checks` → `### Refute-read
    verdict` → `### Advisor 3-lens verdict` → `### GATE RECORD`.
  - `add-method/tooling/test_template_form_tags.py` (380 lines, read in full) — the highest-risk
    test for any template edit. Pins: `FORM_TAGS = {must, reject, after, assumptions, scenarios,
    test_plan}`, each opening/closing on its OWN line (`inline_fill`/`label_dropped` rejects);
    `LABELS` (`Must:`, `Reject:`, `After:`, `Assumptions — lowest-confidence first:`, `Framings
    weighed:`) must survive verbatim; 7 engine-parsed `SEAM_PATTERNS` (`phase_marker`, `title`,
    `status_draft`, `outcome`, `tests_live_in`, `security_checklist`, `gate_record`) must never
    break (`parsed_seam_touched`); `test_lean_pass_single_freeze_comment` requires EXACTLY 1
    `` block.
  - the scenario-ID convention must not collide with `LABELS`/`FORM_TAGS` — it lives inside the
    `<scenarios>` tag's gherkin example prose, not a new tag.
  - all 3 template trees must be edited identically (canonical + dogfood mirror + npm-bundled) or
    `test_template_tree_parity_all_seven` / `BuildExpectationsBlock`'s 3-tree check fails.
Related intent: originating request (mid-session, 2026-07-01) — user: "investigate to capture this
  task ~/workspaces/tind-repo/ai-proxy/.add/tasks/openrouter-embeddings-routing/TASK.md to enhance
  TASK.md.tmpl", followed by a cross-project TASK.md quality review (6 real task files audited
  against live code) that named 3 concrete, low-risk template gaps as the highest-leverage fixes:
  (1) TASK.md.tmpl gains a `Glossary deltas:` line in §3 CONTRACT so a new domain term introduced
  by a task is declared at the freeze, not silently left for a reader to notice matches (or
  doesn't) `.add/GLOSSARY.md`; (2) §2 SCENARIOS gains a stable per-scenario ID/back-reference
  convention (the review's #1 finding was "line numbers rot; symbols/IDs don't" — several real
  tasks already do this ad hoc, e.g. `phase-agents-lean`'s `# M1`/`# M2` trailing comments); (3) §6
  VERIFY gains a `### Live-verify evidence` block confirming §0 GROUND's anchors still resolve
  against the CURRENT tree at gate time, not just at ground time (closing the loop the previously-
  shipped `Ground SHA:` field opened but did not itself verify). A 4th, larger finding (auto-
  refreshing line numbers, promoting cross-task shared seams) was explicitly scoped OUT as a
  future SPEC delta, not this task (see Reject: scope_creep_beyond_three_gaps).
Ground SHA: afc09a1

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `templates/TASK.md.tmpl` (all 3 trees) folds 3 additive MUST-have structural gaps
  surfaced by a cross-project TASK.md quality review — a `Glossary deltas:` line in §3 CONTRACT,
  a stable scenario-ID convention in §2 SCENARIOS, and a `### Live-verify evidence` block in §6
  VERIFY — with zero regression to any existing engine-parsed seam or frozen invariant.
Framings weighed: **all 3 as ONE task** (chosen — small, additive, tightly-scoped template edits
  sharing one blast-radius survey and one companion test file; splitting into 3 tasks would
  triple the freeze/gate ceremony for changes this small) · 3 separate tasks, one per gap
  (rejected — the user's own scoping picked "the MUST-have items" as a single set, and all 3 land
  in the same file across the same 3 trees) · folding in the review's other, larger findings too
  (auto-refreshing §0 line numbers at close, promoting cross-task shared seams into one
  milestone doc) — rejected, explicitly scoped OUT as future SPEC deltas, not MUST-have gaps.
Must:
<must>
  - M1: §3 CONTRACT gains a `Glossary deltas:` line (plain prose, `Term: definition` grammar
    matching `.add/GLOSSARY.md`'s own entry format, or the literal word `none`) placed between the
    fenced shape block and the `Status:` line.
  - M2: §2 SCENARIOS' `Scenario: <short name>` placeholder gains a trailing back-reference slot
    (e.g. `# M1` / `# R1`) naming which §1 Must/Reject item the scenario covers — formalizing the
    ad hoc convention already used by real tasks (e.g. `phase-agents-lean`).
  - M3: §6 VERIFY gains a `### Live-verify evidence` block, placed after `### Deep checks` and
    before `### Refute-read verdict`, confirming every symbol §3 CONTRACT cites still resolves
    against the CURRENT tree (not just the §0 Ground SHA) — closing the loop the Ground SHA field
    opened without itself re-verifying at gate time.
  - M4: all 3 edits land byte-identically across all 3 template trees (canonical, dogfood mirror,
    npm-bundled).
  - M5: the §3 CONTRACT comment count stays at exactly 1 (the existing freeze-instruction block,
    text may extend but no new `` pair is added); the template's TOTAL `` comment appears anywhere in §3 CONTRACT (2nd comment in that section) ->
    "second_freeze_comment"
  - the template's total `

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: §3 CONTRACT carries a Glossary deltas line   # M1
  Given templates/TASK.md.tmpl (any of the 3 trees)
  When the §3 CONTRACT section is read between the fenced shape block and `Status:`
  Then a `Glossary deltas:` placeholder line is present
   And it uses `Term: definition` grammar (or the literal placeholder for "none")

Scenario: §2 SCENARIOS carries a scenario-ID back-reference slot   # M2
  Given templates/TASK.md.tmpl's `Scenario: <short name>` placeholder
  When the line is read
  Then it carries a trailing back-reference slot naming the Must/Reject item it covers
   And the existing Given/When/Then/And lines are unchanged

Scenario: §6 VERIFY carries a Live-verify evidence block in the right slot   # M3
  Given templates/TASK.md.tmpl's §6 VERIFY section
  When the section is scanned for `###` sub-block headers in order
  Then `### Live-verify evidence` appears immediately after `### Deep checks`
   And immediately before `### Refute-read verdict`

Scenario: all 3 edits land byte-identically across the 3 template trees   # M4
  Given add-method/tooling/templates/TASK.md.tmpl, .add/tooling/templates/TASK.md.tmpl, and
        add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl after the build
  When each pair is diffed
  Then all 3 are byte-identical

Scenario: the §3 comment ceiling holds   # M5
  Given templates/TASK.md.tmpl after the build
  When the §3 CONTRACT section's `<!--` markers are counted, and the template's total is counted
  Then §3 CONTRACT contains exactly 1 `<!--` marker
   And the template's total `<!--` count stays below 12

Scenario: no new bracketed tag is introduced   # M6
  Given templates/TASK.md.tmpl after the build
  When the file is scanned for tag-like `<name>...</name>` pairs
  Then the tag set is still exactly FORM_TAGS (must, reject, after, assumptions, scenarios,
       test_plan) — no new tag, no INSTRUCTION_TAGS

Scenario: test_template_structural_gaps.py pins the 3 additions and the existing suite stays green   # M7
  Given add-method/tooling/test_template_structural_gaps.py (new)
  When `python3 -m unittest test_template_structural_gaps -v` runs, then the full add-method suite
  Then presence, position, and 3-tree parity of all 3 additions all pass
   And test_template_form_tags.py, test_refute_record_required.py, test_advisor_review_step.py,
       and test_fast_lane_template.py all still pass unedited

Scenario: a second §3 comment is rejected
  Given a synthetic edit adds a 2nd `<!-- -->` block inside §3 CONTRACT
  When test_lean_pass_single_freeze_comment (or its structural equivalent) runs
  Then it fails with "second_freeze_comment"
   And the shipped template is unaffected

Scenario: crossing the total comment ceiling is rejected
  Given a synthetic edit pushes the template's total `<!--` count to 12
  When the comment-ceiling check runs
  Then it fails with "comment_ceiling_breached"
   And the shipped template's real count (11) is unaffected

Scenario: a misplaced Live-verify evidence block is rejected
  Given a synthetic edit moves `### Live-verify evidence` to before `### Deep checks`
  When test_template_structural_gaps.py's position test runs
  Then it fails with "live_verify_misplaced"
   And the shipped template's real placement is unaffected

Scenario: a drifted template tree is rejected
  Given `.add/tooling/templates/TASK.md.tmpl` differs by even one byte from the canonical tree
  When the 3-tree parity test runs
  Then it fails with "template_tree_drift"
   And the other 2 trees are reported as still matching

Scenario: editing an existing test file to force the new content green is rejected
  Given this task's diff touches test_template_form_tags.py, test_refute_record_required.py, or
        test_advisor_review_step.py
  When the build is reviewed against its declared §5 Scope
  Then it is rejected with "existing_test_edited"
   And those 3 files remain byte-unchanged from before this task started

Scenario: folding in the review's larger findings is rejected
  Given this task's diff adds line-number auto-refresh logic or a cross-task shared-seam doc
  When the build is reviewed against its declared §5 Scope
  Then it is rejected with "scope_creep_beyond_three_gaps"
   And only the 3 declared MUST-have gaps are present in the diff
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
template-structural-gaps — frozen shape @ v1

All 3 edits below land identically in all 3 trees:
  add-method/tooling/templates/TASK.md.tmpl
  .add/tooling/templates/TASK.md.tmpl
  add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl

1. §2 SCENARIOS — the gherkin example's scenario line changes from
     Scenario: <short name>
   to
     Scenario: <short name>   # <Must/Reject item this covers, e.g. M1 or R1>
   Given/When/Then/And lines directly below it are UNCHANGED.

2. §3 CONTRACT — one new line inserted between the closing ``` of the fenced shape block and the
   `Status: DRAFT` line:
     Glossary deltas: <new domain term(s) this task introduces, `Term: definition` — or "none">
   The existing single `` freeze-instruction comment gains one clause to its EXIT
   line (still the same one comment block, no new `` pair):
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY (new
     terms declared as a Glossary delta) + the bundle's lowest-confidence flag was surfaced at
     the freeze (or an honest "none material").

3. §6 VERIFY — one new `###` sub-block inserted between `### Deep checks` and `### Refute-read
   verdict`:
     ### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
     > §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves
     > during build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the
     > CURRENT tree (not the Ground SHA) so a stale anchor is caught here, not by a future
     > reader chasing a moved line.
     - [ ] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by <how>
     - [ ] any anchor that moved/renamed since Ground SHA is named here, not left silent
   Uses the SAME `>`-blockquote cue-line style as `### Build expectations`/`### Deep checks` —
   NOT an HTML comment block (adds zero new HTML comments).

add-method/tooling/test_template_structural_gaps.py — new file, one test class per edit:
  - GlossaryDeltaLineTest — all 3 trees contain `Glossary deltas:` between the fenced §3 block
    and `Status:`; §3's HTML-comment count stays exactly 1.
  - ScenarioIdSlotTest — all 3 trees' `Scenario: <short name>` line carries the trailing
    back-reference slot; the Given/When/Then/And lines are byte-unchanged from before.
  - LiveVerifyEvidenceBlockTest — all 3 trees contain `### Live-verify evidence` positioned
    strictly after `### Deep checks` and strictly before `### Refute-read verdict`.
  - CommentCeilingTest — the template's total HTML-comment count is < 12 (currently 11, +0 new).
  - TagClassUnchangedTest — the FORM_TAGS set found in the template is unchanged (no new tag).
  - ThreeTreeParityTest — all 3 trees byte-identical after the build.

Invariants: test_template_form_tags.py, test_refute_record_required.py,
test_advisor_review_step.py, test_fast_lane_template.py, and every other pre-existing test file
receive NO edits; full add-method suite green afterward.
```

Glossary deltas: none — this task adds a template FIELD named "Glossary deltas", it does not
  itself introduce a new PROJECT.md domain term.
Least-sure flag surfaced at freeze: [contract] the `# M1`/`# R1` trailing-comment scenario-ID
  convention (M2) — why: no existing test pins any specific ID shape, so this is the one part of
  the frozen shape most likely to be restyled later; if wrong: a future task restyles the ID slot
  (plain example prose, not a parsed field) at near-zero cost, no engine seam touched.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the frozen §3 shape (presence · position · 3-tree parity · comment
  ceiling · tag-class invariance) — a template-content task, not a code path.
Plan (one test class per scenario group, asserting template content not internals):
<test_plan>
  - GlossaryDeltaLineTest.test_present_between_fence_and_status_all_trees: arrange the 3 tree
    copies / act extract §3 via add._phase_spans / assert `Glossary deltas:` present and precedes
    `Status: DRAFT` (M1)
  - GlossaryDeltaLineTest.test_section3_has_exactly_one_html_comment: assert §3's `

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` · `.add/tooling/templates/TASK.md.tmpl` · `add-method/tooling/test_template_structural_gaps.py`
Strategy (ordered batches): 1. edit the canonical `add-method/tooling/templates/TASK.md.tmpl`
  with the 3 frozen edits (§2 scenario-ID slot, §3 Glossary deltas line + extended EXIT comment,
  §6 Live-verify evidence block) 2. copy byte-identically into the other 2 trees 3. run
  `test_template_structural_gaps.py` to green 4. run the full add-method suite, confirm zero
  edits needed to any pre-existing test file.

Persona (optional): none seeded (method/tooling authorship, not a domain feature) — generic
  technical-writer-engineer stance atop SOUL.md.
Known-problem fixes: risk of a bare unmatched `` `` `` example) accidentally merging with a LATER real comment under
  the engine's own naive `` strip regex — already hit and fixed once in this very
  task's own §3 CONTRACT text (the freeze failed with `unflagged_freeze` until reworded) — the
  template edit must avoid the same trap by keeping every `

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full add-method suite: 2595 tests, `OK` (was 2586 pre-build; +9 for
      `test_template_structural_gaps.py`)
- [x] coverage did not decrease — +9 new tests, 0 removed/skipped
- [x] no test or contract was altered during build — `git diff --stat` confirms only the 3
      template-tree copies and the new test file changed
- [x] the green was EARNED, not gamed — see Refute-read verdict below (self-reviewed; EARNED)
- [x] concurrency / timing of the risky operation is safe — n/a, static template/test content,
      no concurrent/async/timing-sensitive code introduced
- [x] no exposed secrets, injection openings, or unexpected dependencies — CLEAR, no new
      dependency, no secret, no I/O beyond reading/writing existing repo files
- [x] layering & dependencies follow CONVENTIONS.md — follows the established 3-tree template
      mirror convention and the "one dedicated test file per template delta" pattern
- [x] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (no
      residue); reviewed by Tin Dang at the gate below

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] opening a fresh `new-task` scaffold shows a `Glossary deltas:` line in §3, a scenario-ID
      back-reference slot in §2, and a `### Live-verify evidence` block in §6 between Deep
      checks and Refute-read verdict — confirmed by manual read of all 3 template trees and by
      `test_template_structural_gaps.py`'s 9 tests.
- [x] every pre-existing engine-parsed seam, label, and tag-class invariant survives unchanged —
      confirmed by `test_template_form_tags.py`, `test_refute_record_required.py`,
      `test_advisor_review_step.py`, and `test_fast_lane_template.py` all passing with ZERO edits
      to those files.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — n/a, no executable src beyond the new test file (see its own green run)
- [ ] DEAD-CODE (code) — n/a, no executable src beyond the new test file
- [x] SEMANTIC (prose / non-code) — all 3 template edits read in full, twice (once while
      drafting against the frozen §3 shape, once again against the invariants named in
      `test_template_form_tags.py`); confirmed the scenario-ID slot sits inline with the existing
      Given/When/Then/And lines unchanged, the Glossary-deltas line sits between the fence and
      `Status:` with the single §3 comment only EXTENDED (not duplicated), and the Live-verify
      block uses the same `>`-blockquote style as its siblings, correctly positioned.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: this is a small, bounded template/test-content task, so I
  self-reviewed rather than spawning a subagent (matching the `fresh-checkout-skip-tolerance`
  precedent for similarly mechanical fixes this session). Checked for the 3 classic earned-green
  failure modes: (1) overfit-to-fixture — the 9 new tests assert against the REAL 3 template
  trees via `add._phase_spans` (the engine's own canonical section extractor), not a synthetic
  string the test constructs itself, so they can't be gamed by a fixture that only matches its
  own assertions; (2) vacuous asserts — each test names a SPECIFIC substring/ordering/count
  (e.g. `assertLess(i_deep, i_live, ...)`), not a bare truthy check; (3) stubbed-away logic — n/a,
  no runtime logic exists to stub, this is static content. Also re-ran the FULL suite twice: once
  surfaced a genuine miss (a bare `<how>` placeholder collided with `test_scope_decl_template.py`'s
  frozen v16 tag census — fixed to `<how / where>`, matching the sibling Build-expectations
  block's existing style), the second run was clean (2595/2595). Confirmed via `git diff --stat`
  that ONLY the 3 template copies + the new test file changed — no pre-existing test file touched
  to force the new content green.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no new dependency, no secret, no runtime/data-mutating code; static
   template/test content only.
2. Concurrency: CLEAR — no concurrent, async, or timing-sensitive code introduced.
3. Architecture: CLEAR — follows the established 3-tree template mirror convention and the
   "one dedicated test file per template delta" pattern; confirmed `add.py`'s trio stays
   byte-identical to `engine_pin.ENGINE_MD5` (unpinned, unchanged) via
   `test_scope_decl_template.py`'s own guard.
Verdict: PASS
Residue: none
Binding: advisory — mechanical (no `risk: high` declared; prose/template-only change, not routed
  through the high-risk gate-relax path)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under `autonomy: auto` — no residue: no security/concurrency/
  architecture finding; refute-read EARNED, self-reviewed; full 2595-test suite green) · date:
  2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): future tasks scaffolded from this template — confirm the
  Glossary-deltas line, scenario-ID slot, and Live-verify evidence block are actually FILLED (not
  left as placeholders) by real tasks over the next few milestones.

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned.
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under `autonomy: auto` — no residue: no security/concurrency/)

### Spec delta
- [SPEC · open] the engine's "strip live-phase instruction comments from a closed TASK.md" feature
  also strips legitimate prose that quotes literal `<!--...-->` syntax inside backticks (not just
  the template's own instructional comments), garbling completed tasks' §0/§1 text that documents
  HTML-comment syntax (evidence: this very task's own closed TASK.md now reads "carries exactly 1
  `` comment" instead of "carries exactly 1 `<!--...-->` comment" after gating).

### Competency deltas
- [TDD · open] a test that scans a template for placeholder tags must reuse the EXISTING frozen
  tag-census logic (`test_scope_decl_template.py`'s bare `[a-z_]+` word census), not invent a new
  placeholder word ad hoc — a bare `<how>` collided with that unrelated pre-existing invariant and
  was only caught by running the FULL suite, not the new test file alone (evidence:
  `test_scope_decl_template.py::test_mirrors_and_engine_untouched` failure, fixed to `<how / where>`
  matching the sibling Build-expectations block's existing style).
- [ADD · open] a §5 Scope declaration split across multiple physical lines is silently truncated
  to just its first line by the engine's snapshot parser — reaffirms the fv29-era "declare §5
  Scope on ONE physical line" convention, hit twice in one session across two different tasks
  (evidence: both `phase-agents-lean` and this task needed a `phase tests <slug>` reopen to
  re-anchor the scope snapshot after an initially multi-line declaration under-captured).

