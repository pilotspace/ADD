# TASK: Close ship-review + Release-steps hints in MILESTONE.md.tmpl

slug: close-section-template · created: 2026-06-17 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
- `add-method/tooling/templates/MILESTONE.md.tmpl` — CANONICAL MILESTONE template (the file we edit). Sections today: `## Scope` · `## Shared decisions & glossary deltas` · `## Shared / risky contracts` · `## Tasks` · `## Exit criteria`. Rendered by `_render_template("MILESTONE.md", title=, goal=, stage=, date=)`.
- `.add/tooling/templates/MILESTONE.md.tmpl` + `add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl` — the DOGFOOD + BUNDLED mirrors; all three byte-identical today (md5 784aee967be42d56d8a5f7a877b5ef26). Edit propagates to all three.
- `add-method/tooling/add.py:_exit_criteria` (≈L2669) & `_exit_criteria_cited` (≈L2688) — BOTH bound on `re.search(r"## Exit criteria.*?(?=\n## |\Z)", …)`. The lookahead stops at the next `## ` heading → new `## Close…`/`## Release steps` sections placed AFTER `## Exit criteria` keep their `- [ ]` lines OUT of the goal tally. **No change to these functions.**
- `add-method/tooling/add.py:cmd_new_milestone` (≈L2061) — renders the template; UNCHANGED (template-only task).

Context (working folder):
- `add-method/scripts/prepare_bundle.py` — regenerates `_bundled/` from canonical; run after editing the template.
- `add-method/tooling/test_bundle_parity.py` — always-on guard: `_bundled` template ≡ canonical (md5). Re-run after sync.
- new red test home → `.add/tasks/close-section-template/tests/test_milestone_template_close_section.py` (task-local).
- `.add/milestones/ship-review/MILESTONE.md` — THIS milestone's own doc; its Close section is dogfooded at close (milestone exit-criterion 4).

Honors (patterns / conventions):
- 3-tree byte-identical lockstep for tooling/templates (release-gate pattern; `test_bundle_parity`).
- SDD domain wording-lint — document the grammar abstractly; never spell status-name slang in template prose (CONVENTIONS.md §SDD).
- Additive ⊆ frozen: new sections are ADDITIVE; the frozen seam to preserve is the `## Exit criteria` parse (goal tally + goal-auto-ready), not the template's prose.
- Tool-agnostic invariant: the engine never renders binary assets and never performs the outward git act → the docx export + PR are HINTS in the template, never engine behavior.
- Method/trust-layer edit = a residue category → VERIFY escalates this to the human even under autonomy:auto (PROJECT.md §Domain v6).

Anchors the contract cites:
- `MILESTONE.md.tmpl` — the new `## Close — ship review` (3 domains · cross-task evidence row · goal-met map) + `## Release steps` (AI-defined hints; merge = one step), placed AFTER `## Exit criteria`.
- `_exit_criteria` / `_exit_criteria_cited` regex `## Exit criteria.*?(?=\n## |\Z)` — the invariant the new sections must not perturb (goal tally unchanged; goal-auto-ready unchanged).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Close ship-review + Release-steps hint sections in the MILESTONE template.
Framings weighed: additive `##` sections AFTER `## Exit criteria` (chosen — rides the existing
  `(?=\n## )` lookahead, zero engine change) · a separate per-milestone `CLOSE.md` sibling file
  (more files, breaks the thin single-MILESTONE doc, needs new engine read paths) · close
  sub-bullets INSIDE `## Exit criteria` (rejected — pollutes the goal tally / goal-auto-ready).
Must:
<must>
  - `new-milestone` renders a `## Close — ship review` section with: a Ship-by-domain block naming
    exactly the three bounded contexts `tooling` · `skill` · `book`; a Cross-task evidence row shape
    (`<slug> : gate=… · tests=… · residue=…`); and a Goal-met map tying each Exit criterion to evidence.
  - `new-milestone` renders a `## Release steps` section — AI-defined ordered `- [ ]` hints, with
    `merge` as one small step and a portable-doc/export hint (e.g. pandoc); prose only.
  - both new sections render AFTER `## Exit criteria` (so the goal-tally lookahead bounds them out).
  - the new sections' `- [ ]` lines are EXCLUDED from `_exit_criteria` and `_exit_criteria_cited`:
    a freshly rendered milestone's goal tally AND goal-auto-ready are byte-for-byte what they were
    before the sections existed.
  - the three template copies (canonical · dogfood · `_bundled`) stay byte-identical (bundle parity).
  - the section prose passes the SDD wording-lint (grammar described abstractly; no status-name slang).
</must>
Reject:
<reject>
  - a Close/Release `- [ ]` counted by the goal tally (section misplaced at/before Exit criteria) -> "goal_tally_drift"
  - a template copy diverges across the three trees -> "tree_drift"
  - the engine performs the PR / export itself (a real `gh`/docx call lands in the template or add.py) -> "engine_performs_outward_act"
</reject>
After:
<after>
  - a freshly created milestone carries empty Close + Release-steps scaffolds the AI fills at close,
    and `_goal_auto_ready` still computes from `## Exit criteria` alone (unchanged).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Placing the sections AFTER `## Exit criteria` is SUFFICIENT to keep their checkboxes out of the
    goal tally — lowest confidence because the regex `## Exit criteria.*?(?=\n## |\Z)` relies on the
    NEXT `## ` heading existing; a future reorder, or a sub-heading that drops the `## ` prefix, could
    let the tally swallow close checkboxes. If wrong: goal-auto-ready miscounts → a milestone wrongly
    reads auto-ready (or not). Mitigation: §4 asserts TALLY-PARITY (render with vs without the new
    sections returns the same tally), not merely heading presence.
  - [x] the three domains tooling · skill · book are the right fixed taxonomy — confirmed from PROJECT.md §Domain bounded contexts.
  - [x] "Release steps" belongs in MILESTONE.md (merge as one step), not only in release.md — confirmed by the human this session.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Close section renders with the three domains and a goal-met map
  Given a fresh `add.py new-milestone demo`
  When I read the rendered MILESTONE.md
  Then it contains `## Close — ship review` placed after `## Exit criteria`
  And the Close section names tooling, skill, and book and a Goal-met map referencing "Exit criteria"

Scenario: Release-steps section renders with merge as one small step
  Given a fresh new-milestone
  When I read the rendered MILESTONE.md
  Then it contains `## Release steps` with a `merge` step and a portable-doc export hint
  And the section is prose hints only — no engine command is named to perform them

Scenario: the goal tally is unchanged by the new sections
  Given a rendered MILESTONE.md whose `## Exit criteria` has N cited criteria
  When `_exit_criteria` and `_exit_criteria_cited` run on it
  Then both return totals counted from `## Exit criteria` ALONE (N total / N cited)
  And `_goal_auto_ready` is True exactly as before the sections existed

Scenario: a checkbox inside Release steps is not counted as an exit criterion   # reject: goal_tally_drift
  Given the Close + Release sections sit AFTER `## Exit criteria`
  When the goal tally runs
  Then a `- [ ]` line in `## Release steps` does NOT increment the exit-criteria total
  And the exit-criteria count is unchanged

Scenario: the three template copies stay byte-identical   # reject: tree_drift
  Given the template edited and `prepare_bundle.py` run
  When parity is checked
  Then md5(canonical) == md5(dogfood) == md5(_bundled) for MILESTONE.md.tmpl
  And no test file leaked into the bundle
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
RENDER  add.py new-milestone <slug> --goal <g> --stage <s>  ->  milestones/<slug>/MILESTONE.md
  (a prose contract: the frozen seam is a TOKEN SET + structural invariants, not an HTTP shape)

Structural invariants (the frozen seam):
  S1 ORDER     headings present & ordered:  `## Exit criteria` < `## Close — ship review` < `## Release steps`
  S2 CLOSE     `## Close — ship review` contains the domain tokens {tooling, skill, book},
               a cross-task evidence row `<slug> : gate=… · tests=… · residue=…`,
               and a Goal-met map line referencing "Exit criteria"
  S3 RELEASE   `## Release steps` contains ≥1 ordered `- [ ]` hint, names "merge" as one step,
               and a portable-doc/export hint — prose only, NO engine verb
  S4 TALLY     _exit_criteria(render) and _exit_criteria_cited(render) depend ONLY on the
               `## Exit criteria` section — adding/removing Close+Release changes NEITHER tally
  S5 PARITY    md5(canonical) == md5(dogfood) == md5(_bundled) for MILESTONE.md.tmpl

Frozen token set: "## Close — ship review", "## Release steps", "tooling", "skill", "book", "merge"
Reject labels:    goal_tally_drift (S4 violated) · tree_drift (S5 violated) · engine_performs_outward_act (S3 violated)
Out of seam (iterates freely, no re-freeze): the wording/prose inside each section, ordering of the
  release-step hints, the example export command — presentation, not the checkable seam.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-17)
Least-sure flag surfaced at freeze: [contract/test] S4 (tally-parity) — the "no new gate, goal-ready unchanged" promise rests on the existing regex `## Exit criteria.*?(?=\n## )` stopping at the next heading; if a future reorder or a non-`##` sub-heading slipped in, a Close checkbox could be miscounted and goal-auto-ready would drift. Mitigation in §4: test_S4 renders the template and asserts the goal tally counts the Exit-criteria slice ALONE while the Close/Release sections carry their own (excluded) checkboxes. Everything else is additive prose ⊆ the frozen exit-criteria seam.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 5 structural invariants S1–S5 (one test each).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_close_section_renders_three_domains: render a milestone in tmp / assert S1 order + S2 tokens {tooling,skill,book} + goal-met map
  - test_release_steps_merge_and_export_hint: render / assert S3 — `## Release steps`, a `merge` step, an export hint, no engine verb
  - test_goal_tally_unchanged_by_new_sections: import add.py / assert _exit_criteria + _exit_criteria_cited count from `## Exit criteria` alone (S4); _goal_auto_ready True
  - test_release_checkbox_not_counted: render with a `- [ ]` in Release steps / assert exit-criteria total unchanged (S4, reject goal_tally_drift)
  - test_template_tree_parity: assert md5(canonical)==md5(dogfood)==md5(_bundled) for MILESTONE.md.tmpl (S5, reject tree_drift)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/MILESTONE.md.tmpl` `tooling/templates/MILESTONE.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl`
Strategy (ordered batches): 1. edit the canonical `add-method/tooling/templates/MILESTONE.md.tmpl` (add the two sections after `## Exit criteria`). 2. mirror byte-for-byte into the dogfood `.add/tooling/templates/` copy. 3. run `python3 add-method/scripts/prepare_bundle.py` to regenerate `_bundled/`. 4. run test_bundle_parity.
Safety rule (feature-specific): NO add.py logic change; sections strictly AFTER `## Exit criteria`; the three copies end byte-identical (S5).
Code lives in: the three `MILESTONE.md.tmpl` copies (template-only; no `./src/`).
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

- [x] all tests pass — task suite 5/5 green; full engine suite 1189 tests OK (14.7s)
- [x] coverage did not decrease — N/A (no src/); the 5 new tests add coverage of S1–S5
- [x] no test or contract was altered during build — only the 3 template copies changed; tests + §3 untouched
- [x] the green was EARNED, not gamed — refute-read: tests assert the REAL template text AND the LIVE engine tally (dogfood `new-milestone` render showed `0/1 exit criteria` — Close/Release checkboxes excluded); S4 counts new-section checkboxes specifically, not the pre-existing Tasks boxes (that weak assert was caught + fixed at red). Not overfit.
- [x] concurrency / timing — N/A; no concurrent operation. Template renders via the engine's existing atomic writes.
- [x] no exposed secrets, injection openings, or unexpected dependencies — template prose only; NO new dependency; `test_no_engine_outward_act` green (no `gh`/docx shell-out added)
- [x] layering & dependencies follow CONVENTIONS.md — additive prose ⊆ frozen exit-criteria seam; 3-tree byte parity held (md5 98d4ccc…); engine logic untouched
- [ ] a person reviewed and approved the change — ESCALATED (residue below)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read the full rendered MILESTONE.md from a live `new-milestone`. Confirmed: S1 order (Exit < Close < Release), S2 the three domains + evidence row + goal-met map referencing "Exit criteria", S3 merge step + pandoc/docx export hint as prose-only hints (no engine verb), S4 live goal tally still `0/1` (unchanged), S5 md5 parity across the 3 trees. No dead/orphaned content; the docx/PR remain HINTS the human runs.

### Residue — escalated (not auto-resolved)
- METHOD / TRUST-LAYER edit: this changes the MILESTONE template — a method surface every future milestone inherits. Per PROJECT.md §Domain (v6), method/trust-layer edits are a residue category that escalates to a human even under `autonomy: auto`. NOT a security/concurrency/architecture finding; evidence is complete and green. Human gate on the method change itself.

### GATE RECORD
Outcome: PASS   (pending human confirmation of the method-edit residue)
Reviewed by: Tin Dang · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): future `new-milestone` renders carry the two sections AND the goal tally stays bound to `## Exit criteria` alone (S4) · the 3 template copies stay md5-equal (S5).

### Spec delta
- [SPEC · seeded] the close-guide (task 2) must CUE these template sections — the guide tells the AI HOW to fill Ship-by-domain + Cross-task evidence + Goal-met map + Release steps (evidence: this task ships the scaffold; the orchestration is task 2's scope)

### Competency deltas
- [TDD · folded] a presence-only assertion can pass for the WRONG reason when the artifact already holds similar tokens — S4's first form leaned on the pre-existing `## Tasks` checkboxes (`whole_boxes > exit_boxes` was true before any build); pin the NEW artifact's contribution specifically (count Close+Release boxes), not a whole-file delta (evidence: S4 green-at-red until tightened) [folded foundation-version 37]
- [ADD · folded] the freeze flag must be PERSISTED in TASK.md §3 as `Least-sure flag surfaced at freeze:`, not only surfaced in chat — the `unflagged_freeze` guard blocks tests→build until the line exists (evidence: `advance` rejected with `unflagged_freeze` despite the flag being shown at the freeze report) [folded foundation-version 37]
