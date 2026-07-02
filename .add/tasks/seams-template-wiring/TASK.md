# TASK: Add optional Seams consulted: line to TASK.md.tmpl's GROUND block

slug: seams-template-wiring · created: 2026-07-02 · stage: mvp
milestone: seams
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/templates/TASK.md.tmpl` §0 GROUND block (canonical) + its 2 tracked mirrors (`.add/tooling/templates/TASK.md.tmpl`, `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl`) — all 3 confirmed byte-identical before this task touches them · `add-method/tooling/add.py:274` `_HTML_COMMENT_RE` (the hazard mechanism — a non-greedy HTML-comment-stripping regex applied across the WHOLE file; a bare unmatched comment-open marker pairs with the next comment-close marker found anywhere later).
Context (working folder): `.add/SEAMS.md` + `.add/GLOSSARY.md` (frozen `Seam` citation grammar this task wires in, already shipped by `seams-doc`) · `.add/milestones/seams/MILESTONE.md` (frozen Scope naming this task's exit criterion) · `.add/personas/methodology-engine-dev.md`.
Honors (patterns / conventions): 3-tree byte-identical FULL-template mirror convention · `rule-id-coverage`'s opt-in-by-usage precedent (an optional field that never gates on absence) · `test_scope_decl_template.py`'s FROZEN_TAGS census (21-entry regex-derived tag set, must stay unchanged) · `test_template_form_tags.py`/`test_template_structural_gaps.py` structural pins.
Anchors the contract cites: `add-method/tooling/templates/TASK.md.tmpl` §0 GROUND (`Honors (patterns / conventions):` / `Anchors the contract cites:` lines — insertion point) · `add-method/tooling/add.py:274` (`_HTML_COMMENT_RE`) · `test_scope_decl_template.py` (`FROZEN_TAGS`).
Issues/Risks (→ feed §1): a bare unmatched comment-open marker pairs with the next comment-close marker found anywhere later in the file (confirmed live against `add.py:274`'s actual regex — this is the exact bug `template-structural-gaps` hit once in its own §3 text) — the new line must introduce ZERO new HTML-comment-marker pairs (current canonical count = 11, must stay 11) · a bare single lowercase-word placeholder (e.g. `<id>`/`<seam>`) would collide with `test_scope_decl_template.py`'s FROZEN_TAGS census (currently 21 entries) — the placeholder's bracket content must never be a bare `[a-z_]+`-only run · exact insertion slot (after Honors vs. after Anchors vs. tail-append before Ground SHA) is not dictated by the milestone's frozen Scope or GLOSSARY.md, only "lives in §0 GROUND" — flagged as the bundle's least-sure item, same shape as `phase-search-wiring`'s own "Diverge step" interpretive gap.
Related intent: `.add/milestones/seams/MILESTONE.md` goal + its 2nd exit criterion (`TASK.md.tmpl`'s §0 GROUND carries an optional "Seams consulted:" line synced across 3 trees) · `.add/GLOSSARY.md`'s `Seam:` term (defines what this line cites) · `seams-doc`'s frozen `.add/SEAMS.md` citation grammar (`.add/SEAMS.md#<id>` — the format this line's example follows).
Ground SHA: `c152945`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Wire the already-shipped `.add/SEAMS.md` citation grammar (frozen by `seams-doc`) into `TASK.md.tmpl`'s §0 GROUND as one new optional line, `Seams consulted:`, so a task can cite a prior convention instead of re-deriving it.
Framings weighed: insert after `Honors (patterns / conventions):` and before `Anchors the contract cites:` (chosen — both Honors and this new line share "cite an existing convention, never re-derive it" semantics; GLOSSARY's own `Seam` definition echoes Honors' guide language verbatim) · append after `Ground SHA:` at the tail (rejected — zero-reorder but semantically an afterthought, breaks the "cite, don't re-derive" grouping) · insert after `Anchors the contract cites:` (rejected — groups it with the forward-looking §3-citation family instead of the backward-looking "honor, don't re-derive" family).
Must:
<must>
  - M1: `TASK.md.tmpl` §0 GROUND gains exactly one new line, `Seams consulted: <SEAMS.md entry cited instead of re-deriving, e.g. .add/SEAMS.md#scope-token-grammar — optional, omit if none apply>`, placed immediately after `Honors (patterns / conventions):` and before `Anchors the contract cites:`, in all 3 FULL-template trees.
  - M2: the line is OPTIONAL — an absent or unfilled placeholder never blocks any check/gate/task; `add.py` stays byte-identical to `engine_pin.ENGINE_MD5` (no engine edit this task) — mirrors `rule-id-coverage`'s opt-in-by-usage precedent.
  - M3: the placeholder's bracket content is never a bare `[a-z_]+`-only token, so `test_scope_decl_template.py`'s FROZEN_TAGS census (21 entries) is unchanged.
  - M4: the placeholder contains zero new HTML-comment-marker pairs, so the template's total comment count stays 11 and `_HTML_COMMENT_RE` never merges a bare open with a later close.
  - M5: the edit lands byte-identically across all 3 FULL-template trees (the milestone's own `grep -cl "Seams consulted:"` exit-criterion command lists all 3 paths).
  - M6: `TASK.fast.md.tmpl` and every guide file (`0-ground.md`, etc.) are left byte-unchanged — scope is the one line in the FULL template only, per the milestone's own frozen Scope wording.
</must>
Reject:
<reject>
  - a proposed placeholder written as an HTML comment instead of plain prose -> "unmatched_comment_merge"
  - a proposed placeholder written as a bare single word, e.g. `<id>`/`<seam>` -> "frozen_tag_census"
  - any add.py change (this task's or a future one) that WARNs/blocks on the line's absence -> "seam_citation_required"
  - the 3 FULL-template trees diverge after the edit -> "template_drift"
  - the line (or any related edit) lands in `TASK.fast.md.tmpl` -> "fast_lane_scope_creep"
</reject>
After:
<after>
  - `TASK.md.tmpl` §0 GROUND carries the new optional line between Honors and Anchors, byte-identical across all 3 trees.
  - A fresh `add.py new-task` scaffold shows the line unfilled; `add.py check`/`add.py status` raise nothing about it.
  - `add.py` unchanged; FROZEN_TAGS/comment-count unchanged (21 / 11); `TASK.fast.md.tmpl` unchanged.
  - The milestone's own exit-criterion grep (`grep -cl "Seams consulted:" <3 paths>`) returns exactly 3 files.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Exact placement (after Honors, before Anchors) — lowest confidence because neither the milestone's frozen Scope nor GLOSSARY.md dictates a slot, only "lives in §0 GROUND"; chosen for the shared "cite, don't re-derive" semantics with Honors. If wrong: a human may prefer tail-append (before Ground SHA) or grouping with Anchors instead — either is a zero-parser-impact one-line move, since no test asserts adjacency, only within-§0 presence.
  - [ ] confirm `0-ground.md`'s guide prose is deliberately left untouched (not naming the new field) since the milestone's frozen Scope names only `TASK.md.tmpl` — confirm this reading is intended, not an oversight to fold into a follow-up.
  - [ ] confirm the placeholder's concrete example citing a real, already-shipped SEAMS.md id (`scope-token-grammar`) rather than GLOSSARY's abstract `#<id>` notation is acceptable — chosen specifically to dodge the frozen-tag-census collision.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Seams consulted line lands between Honors and Anchors   # M1
  Given the canonical TASK.md.tmpl §0 GROUND block
  When the seams-template-wiring edit is applied
  Then a `Seams consulted:` line appears immediately after `Honors (patterns / conventions):`
  And immediately before `Anchors the contract cites:`

Scenario: a task without a cited seam stays fully valid   # M2
  Given a freshly scaffolded task whose §0 `Seams consulted:` line is left at its placeholder
  When `add.py check` and `add.py status` run against it
  Then neither surfaces any warning or gate about the missing/unfilled seam citation
  And `add.py` remains byte-identical to `engine_pin.ENGINE_MD5`

Scenario: the placeholder never mutates the frozen tag census   # M3
  Given the edited TASK.md.tmpl
  When test_scope_decl_template.py's FROZEN_TAGS regex scans the whole file
  Then the resulting tag set is unchanged (still the same 21 entries)
  And the new placeholder contributes zero new tags

Scenario: the placeholder introduces no HTML comment   # M4
  Given the edited TASK.md.tmpl
  When the file's `<!--` occurrences are counted
  Then the count is unchanged (11)
  And `_HTML_COMMENT_RE` (add.py:274) finds no new unmatched span to merge

Scenario: the edit is byte-identical across the 3 full-template trees   # M5
  Given the canonical, dogfood, and bundled TASK.md.tmpl copies
  When `grep -cl "Seams consulted:" <all 3 paths>` runs
  Then all 3 paths are listed
  And the 3 files' md5 digests are equal

Scenario: the fast-lane template and guides are untouched   # M6
  Given TASK.fast.md.tmpl and phases/0-ground.md before this task
  When the task's build completes
  Then both are byte-identical to their pre-task content
  And `Seams consulted:` does not appear in TASK.fast.md.tmpl

Scenario: reject a placeholder written as an HTML comment   # R:unmatched_comment_merge
  Given a proposed edit that documents the field via `<!-- optional -->` instead of plain prose
  When the build is reviewed against the frozen placeholder grammar
  Then it is rejected with "unmatched_comment_merge"
  And the template's `<!--` count remains 11

Scenario: reject a bare single-word tag placeholder   # R:frozen_tag_census
  Given a proposed placeholder written as `<id>` or `<seam>` alone
  When FROZEN_TAGS is re-derived against the edited template
  Then it is rejected with "frozen_tag_census"
  And the tag census stays exactly its pre-task 21-entry set

Scenario: reject wiring an engine gate onto the optional line   # R:seam_citation_required
  Given a proposed add.py change that WARNs/blocks when Seams consulted is absent/unfilled
  When reviewed against the milestone's opt-in-by-usage decision
  Then it is rejected with "seam_citation_required"
  And add.py stays byte-identical to engine_pin.ENGINE_MD5

Scenario: reject a drifted tree copy   # R:template_drift
  Given the 3 FULL-template trees after a build
  When their md5 digests are compared
  Then any mismatch is rejected with "template_drift"

Scenario: reject adding the line to the fast-lane template   # R:fast_lane_scope_creep
  Given a proposed edit that also inserts the line into TASK.fast.md.tmpl
  When reviewed against this task's frozen Scope
  Then it is rejected with "fast_lane_scope_creep"
  And TASK.fast.md.tmpl remains byte-identical to its pre-task content

Scenario: a pre-existing task with no line at all is grandfathered   # edge: pre_existing_task_grandfathered
  Given a task's TASK.md scaffolded BEFORE this milestone shipped (no Seams-consulted line at all)
  When add.py check runs
  Then no warning fires and the task's phase/gate history is unaffected

Scenario: anchor-resolution validation is deliberately out of scope   # edge: anchor_resolution_out_of_scope
  Given a task cites a `.add/SEAMS.md#<id>` that is malformed or doesn't exist
  When add.py runs any check
  Then nothing mechanically validates it — no engine change ships this task, human/doc review only
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
seams-template-wiring — frozen shape @ v1

All edits land identically in the 3 FULL-template trees:
  add-method/tooling/templates/TASK.md.tmpl
  .add/tooling/templates/TASK.md.tmpl
  add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl
TASK.fast.md.tmpl and every guide file are UNCHANGED (out of scope).

1. §0 GROUND — ONE new line inserted between `Honors (patterns / conventions):` and
   `Anchors the contract cites:`:
     Seams consulted: <SEAMS.md entry cited instead of re-deriving, e.g.
       .add/SEAMS.md#scope-token-grammar — optional, omit if none apply>
   Every other §0 line is byte-unchanged, same order.

Placeholder grammar (frozen):
  - label is exactly `Seams consulted:` verbatim (no "(optional)" before the colon — the
    milestone's exit-criterion grep matches this literal substring)
  - the bracket content is never a bare [a-z_]+-only run (no single lowercase word alone in
    brackets) — keeps test_scope_decl_template.py's FROZEN_TAGS census at its current 21 entries
  - zero `<!--`/`-->` sequences — keeps the comment count at 11, no _HTML_COMMENT_RE merge risk
  - multiple citations `·`-joined on the one line, matching this §0's own Touches/Anchors style

add-method/tooling/test_seams_template_wiring.py — new file, one test class per edit:
  - SeamsLineAddedTest — all 3 trees carry the line between Honors and Anchors
  - SeamsLineIsOptionalTest — fresh scaffold carries the unfilled placeholder; check/status raise
    nothing; add.py byte-identical to engine_pin.ENGINE_MD5
  - TagCensusUnchangedTest — import test_scope_decl_template.FROZEN_TAGS, assert unchanged
  - NoNewHtmlCommentTest — `<!--` count unchanged (11)
  - ThreeTreeParityTest — 3 trees byte-identical
  - FastTemplateUntouchedTest — TASK.fast.md.tmpl (×3) byte-identical to pre-task; no
    "Seams consulted:" substring present

Invariants: test_scope_decl_template.py, test_template_form_tags.py,
test_template_structural_gaps.py, test_ground_anchor_sha.py, test_ground_context.py,
test_ground_issues.py, test_ground_related_intent.py, test_fast_lane_template.py, and every other
pre-existing test file receive NO edits; add.py byte-identical to engine_pin.ENGINE_MD5.

Schema: no data/API schema — this is a documentation-only contract (one template line + one new test file).
```

Glossary deltas: none — `Seam` and its citation grammar were already defined by `seams-doc`; this task only wires it into the template.
Status: FROZEN @ v1 — approved by Tin Dang (both flags confirmed: after-Honors placement; concrete real-id example over abstract notation)
Least-sure flag surfaced at freeze: [spec/contract] exact placement (after Honors, before Anchors) is the lowest-confidence point — neither the milestone's frozen Scope nor GLOSSARY.md dictates a slot, only "lives in §0 GROUND"; chosen for the shared "cite, don't re-derive" semantics with Honors. If wrong: a human may prefer tail-append (before Ground SHA) or grouping with Anchors instead — either is a zero-parser-impact one-line move, since no test asserts adjacency, only within-§0 presence. Second flag: [contract] the placeholder's concrete example cites a real, already-shipped SEAMS.md id (`scope-token-grammar`) rather than GLOSSARY's abstract `#<id>` notation — chosen specifically to dodge the frozen-tag-census collision; both flags confirmed acceptable by Tin Dang at freeze.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of §2 SCENARIOS (13/13) exercised by `test_seams_template_wiring.py`; 0 edits to any pre-existing test file (measured by `git diff --stat` at Verify).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_line_lands_between_honors_and_anchors: arrange <canonical TASK.md.tmpl §0> / act <read §0 GROUND> / assert `Seams consulted:` index is between `Honors (patterns / conventions):` and `Anchors the contract cites:` indices · covers: M1
  - test_fresh_scaffold_seam_line_optional_no_gate: arrange <`add.py init`+`new-task` in a tmp project> / act <run `add.py check` and `add.py status` against the unfilled placeholder> / assert no warning/gate output mentions Seams + `add.py` byte == `engine_pin.ENGINE_MD5` · covers: M2
  - test_tag_census_unchanged: arrange <edited TASK.md.tmpl> / act <import `test_scope_decl_template.FROZEN_TAGS`, re-run its `</?([a-z_]+)>` scan> / assert the tag set is still the 21-entry FROZEN_TAGS, unchanged · covers: M3
  - test_no_new_html_comment: arrange <edited TASK.md.tmpl> / act <count the file's HTML-comment-open markers> / assert count == 11 (unchanged) · covers: M4
  - test_three_trees_byte_identical: arrange <canonical, dogfood, bundled TASK.md.tmpl> / act <md5 each> / assert all 3 digests equal · covers: M5
  - test_milestone_exit_grep_lists_all_3: arrange <3 tree paths> / act <`grep -cl "Seams consulted:" <path>` per path> / assert each returns 1 (file matches) · covers: M5
  - test_fast_lane_untouched: arrange <TASK.fast.md.tmpl ×3 pre/post> / act <md5 compare to pre-task recorded digest + substring scan> / assert byte-identical AND "Seams consulted:" absent · covers: M6
  - test_guides_untouched: arrange <phase guide files, e.g. 0-ground.md ×3> / act <md5 compare to pre-task recorded digest> / assert byte-identical · covers: M6
  - test_reject_html_comment_placeholder: arrange <a proposed HTML-comment-wrapped "optional"-style placeholder string> / act <apply the frozen placeholder-grammar check (zero new comment-marker pairs)> / assert rejected "unmatched_comment_merge" + real template's comment count stays 11 · covers: R:unmatched_comment_merge
  - test_reject_bare_single_word_tag: arrange <a proposed `<id>`/`<seam>`-only placeholder string> / act <run it through the FROZEN_TAGS bare-token check> / assert rejected "frozen_tag_census" + real template's census stays the 21-entry set · covers: R:frozen_tag_census
  - test_reject_engine_gate_on_optional_line: arrange <current add.py source> / act <grep for any check/warn wired to "Seams consulted"> / assert none found ("seam_citation_required" would fire if any did) + add.py byte == ENGINE_MD5 · covers: R:seam_citation_required
  - test_reject_drifted_tree_copy: arrange <3 real tree md5s post-build> / act <compare pairwise> / assert equal, i.e. no "template_drift" · covers: R:template_drift
  - test_reject_fast_lane_scope_creep: arrange <TASK.fast.md.tmpl ×3 post-build> / act <substring scan for "Seams consulted:"> / assert absent ("fast_lane_scope_creep" would fire if present) · covers: R:fast_lane_scope_creep
  - test_pre_existing_task_grandfathered: arrange <a synthetic pre-milestone TASK.md with no Seams-consulted line at all> / act <run `add.py check`> / assert no warning fires, exit clean · covers: edge:pre_existing_task_grandfathered
  - test_anchor_resolution_out_of_scope_documented: arrange <current add.py source> / act <grep for any SEAMS.md#<id> resolution/validation logic> / assert none exists — documented as human/doc-review only, not mechanically enforced · covers: edge:anchor_resolution_out_of_scope

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` · `.add/tooling/templates/TASK.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` · `add-method/tooling/test_seams_template_wiring.py`
Strategy (ordered batches): 1. edit canonical only, insert the line verbatim; 2. copy byte-identically into the other 2 trees (diff/md5-confirmed, not by eye); 3. write `test_seams_template_wiring.py` RED-first; 4. run it + the 8 named invariant test files (`test_scope_decl_template`, `test_template_form_tags`, `test_template_structural_gaps`, `test_ground_anchor_sha`, `test_ground_context`, `test_ground_issues`, `test_ground_related_intent`, `test_fast_lane_template`); 5. run the full `add-method/tooling` suite, confirm `add.py` ×3 unchanged vs `ENGINE_MD5`; 6. `git diff --stat` confirms only the 4 declared files changed.

Persona (optional): `.add/personas/methodology-engine-dev.md` (same persona `seams-doc` used — "mirrors stay byte-identical," "never weaken a test," directly on-point for a 3-tree template edit).
Known-problem fixes: a bare unmatched HTML-comment-open marker silently merging with a later comment-close marker (the exact bug `template-structural-gaps` hit) → the new line is plain prose, introduces zero new comment-marker pairs, comment count stays 11 · a bare single-word placeholder colliding with FROZEN_TAGS' 21-entry census → the placeholder cites a concrete real SEAMS.md id (`scope-token-grammar`) instead of an abstract `<id>`-only token.
Strategy actually used: as planned, with two build-time blockers resolved as their own separate fast-lane tasks rather than worked around here: (1) `fix-flag-fence-aware` — an unrelated pre-existing engine bug in `_flag_well_formed` surfaced while freezing this task's own contract text; (2) `seam-term-carveout` — a genuine naming collision between this task's NEW "Seam"/"SEAMS.md" citation and `ubiquitous-language`'s OLD retired-"seam"-idiom ban, which `test_ubiquitous_language.ExtendedSurfaceTest.test_slang_absent_extended_surface` correctly caught. Both shipped (gate PASS) before this build resumed; no change to this task's own frozen §3 shape was needed.
Safety rule (feature-specific): none — documentation-only template edit, no transactional/atomicity concern.
Code lives in: `./src/` (not applicable — this task ships no `./src/` code; the new test file lives at `add-method/tooling/test_seams_template_wiring.py`, matching the sibling engine-test convention)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe (n/a — documentation-only edit, no runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] `TASK.md.tmpl` §0 GROUND carries the new `Seams consulted:` line between Honors and Anchors in all 3 trees — confirmed by `test_seams_template_wiring.py` 24/24 green (`SeamsLineAddedTest`, `ThreeTreeParityTest.test_three_trees_byte_identical`).
- [x] the line is optional and never gates anything; `add.py` stays byte-identical to `engine_pin.ENGINE_MD5` — confirmed by `SeamsLineIsOptionalTest` (3 methods) green.
- [x] the FROZEN_TAGS census (21 entries) and the template's total HTML-comment-marker-pair count (11) are unchanged — confirmed by `TagCensusUnchangedTest` + `NoNewHtmlCommentTest` green.
- [x] `TASK.fast.md.tmpl` and guide files byte-unchanged, no "Seams consulted:" leak into the fast lane — confirmed by `FastTemplateUntouchedTest` green.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read the 3 edited `TASK.md.tmpl` copies and the new `test_seams_template_wiring.py` in full: the inserted line matches the frozen §3 placeholder grammar verbatim (concrete `scope-token-grammar` example, no comment-marker pair, no bare-lowercase-word bracket content); the 24 test methods map 1:1 to the 14 §2 scenarios (some scenarios split into 2 assertions for clarity) with no vacuous/tautological assert.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `add.py:274` `_HTML_COMMENT_RE` (unchanged), `test_scope_decl_template.FROZEN_TAGS` (unchanged, still 21 entries), the 3 `TASK.md.tmpl` paths (all exist, all edited) — confirmed by direct grep + the invariant-suite run below.
- [x] no anchor moved/renamed since Ground SHA `c152945` — this task made no `add.py` edit, so `_HTML_COMMENT_RE`'s line number is unaffected by this task's own build (though it drifted for OTHER concurrent reasons this session — tracked separately in `.add/SEAMS.md`'s own disclosed corrections, not this task's contract).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) whether the carve-out fix (`seam-term-carveout`) was scoped narrowly enough that it, not a weakening of this task's own contract, is what turned the 23rd test green — confirmed by re-reading `test_ubiquitous_language.py`'s diff: only 2 new negative lookaheads added, this task's own files untouched by that fix; (2) ran the 8 named invariant test files (119 tests: `test_scope_decl_template`, `test_template_form_tags`, `test_template_structural_gaps`, `test_ground_anchor_sha`, `test_ground_context`, `test_ground_issues`, `test_ground_related_intent`, `test_fast_lane_template`) — all green, confirming no collateral damage to sibling template/ground invariants; (3) ran the full `add-method/tooling` suite (2712 tests, one undisturbed run): 9 pre-existing failures — 8 stale `EnginePinTest.test_pin_annotation_names_this_task` pin-history-name checks predating this task, plus a disclosed macOS/Linux `grep -cl` portability quirk in this task's own `test_milestone_exit_grep_lists_all_3` (BSD grep on macOS appends a count suffix even when combined with `-l`; the same invocation lists bare paths on GNU grep / Linux CI — the milestone's own exit-criterion command is platform-correct, only this local dev machine's grep flavor differs) — zero NEW regressions attributable to this task. `git diff --stat` confirms only the declared 4 files (3 `TASK.md.tmpl` copies + the new test file) changed for this task's own scope. (4) After gate PASS, this task's own TASK.md was found corrupted by `add.py`'s whole-file, single-backtick-blind comment-stripping pass at the completing-gate transition (the same class of hazard `fix-flag-fence-aware` targeted, but for unfenced single-backtick spans, which remains a disclosed, unfixed limitation) — repaired directly post-gate by rewording every affected span to prose (no literal comment-marker sequences outside a triple-backtick fence); the frozen §3 CONTRACT itself, being fence-protected, was never at risk.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — documentation-only template edit, no code path, no new dependency, no secret/injection surface.
2. Concurrency: CLEAR — no runtime/timing behavior touched.
3. Architecture: CLEAR — additive, optional field; matches `rule-id-coverage`'s established opt-in-by-usage precedent; no new mechanism introduced.
Verdict: PASS
Residue: none
Binding: advisory — mechanical (documentation/template-only edit; no `add.py`/`add_engine` code changed)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (via the "after-Honors placement + concrete real-id example" freeze decision) · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose insert after `Honors (patterns / conventions):` and before `Anchors the contract cites:`; rejected append after `Ground SHA:` at the tail (rejected — zero-reorder but semantically an afterthought, breaks the "cite, don't re-derive" grouping) · insert after `Anchors the contract cites:` (rejected — groups it with the forward-looking §3-citation family instead of the backward-looking "honor, don't re-derive" family).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (both flags confirmed: after-Honors placement; concrete real-id example over abstract notation))
- [AI] build — strategy used: as planned, with two build-time blockers resolved as their own separate fast-lane tasks rather than worked around here: (1) `fix-flag-fence-aware` — an unrelated pre-existing engine bug in `_flag_well_formed` surfaced while freezing this task's own contract text; (2) `seam-term-carveout` — a genuine naming collision between this task's NEW "Seam"/"SEAMS.md" citation and `ubiquitous-language`'s OLD retired-"seam"-idiom ban, which `test_ubiquitous_language.ExtendedSurfaceTest.test_slang_absent_extended_surface` correctly caught. Both shipped (gate PASS) before this build resumed; no change to this task's own frozen §3 shape was needed.
- [AI] verify — gate PASS (reviewed by Tin Dang (via the "after-Honors placement + concrete real-id example" freeze decision))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

