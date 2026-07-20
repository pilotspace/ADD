# TASK: Propagate the design-definition loop + glossary terms to the book and ×3 trees

slug: book-glossary-align · created: 2026-06-16 · stage: mvp · risk: high
autonomy: conservative   <!-- method-normative-surface scope: edits the published book + GLOSSARY across 4 byte-identical trees; risk:high forces the human verify gate (an unguarded `auto` would refuse — `unguarded_high_risk_auto`). -->
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
- `docs/14-foundation.md` — the book's UDD home: the "## Three concerns, one foundation" UDD bullet (currently "user flows · UI states · a design source of truth"; no design-definition loop yet). Add a concise loop description here (audit-trail "why", with a pointer to the `design.md` guide for the "how"). The book lives in **4 byte-identical trees**: canonical `add-method/docs/`, bundled `add-method/src/add_method/_bundled/docs/`, dogfood `.add/docs/`, repo-root `./14-foundation.md`.
- `docs/appendix-c-glossary.md` — the GLOSSARY: single-line entries `**Term** — definition.`, blank-line separated; `DDD · SDD · UDD · TDD · ADD` competencies named but NO `wireframe / mock / capture / design-confirm` entries. Add the 4 entries (same 4 trees). 4-way md5 currently identical (`3bfa10c6…`).
- `add-method/tooling/test_docs_accord.py` — NEW content test for this task (book describes the loop · the 4 glossary terms exist · they accord with the shipped `design.md` wording).
- READ-ONLY sources of canonical wording (already shipped, do NOT re-edit): `add-method/skill/add/design.md` (the loop `review-domain → research-components → wireframe → render-capture-confirm`; capture at `.add/design/captures/<name>.<ext>`; `missing_capture` WARN; `@json-render/image`) and `tooling/templates/udd-wireframe.md` (Stage A wireframe · Stage B HTML mock).

Context (working folder):
- `.add/milestones/udd-design-loop/MILESTONE.md` — exit criterion 5 + the glossary deltas (`wireframe` · `design mock` · `capture` · `design-confirm`).
- task-3 (`capture-evidence`) §7 spec delta — the glossary should also surface the **capture location** (`.add/design/captures/<name>.<ext>`), **`@json-render/image`** default, and the **`missing_capture`** WARN — woven INTO the `capture`/`design-confirm` entries, not as standalone terms (keep the glossary lean).

Honors (patterns / conventions):
- **Audit-trail vs working-state** (PROJECT.md / GLOSSARY) — the book is the read-once "why", never auto-loaded: it gets a *conceptual* loop description + a pointer; the operational recipe stays in the skill guides. Do not relocate the recipe into the book.
- **×N-tree byte-identical (no-drift invariant)** — every book/glossary edit lands in all 4 trees; `test_book_parity` (canon↔root) and `test_bundle_parity::test_docs_tree_byte_identical` (canon↔bundle) go red on any drift; the dogfood `.add/docs` is unguarded but synced for correctness.
- **Ubiquitous language** — glossary term names match the shipped `design.md`/`udd-wireframe.md` wording exactly. `test_ubiquitous_language::GlossaryBridgeTest` governs only RENAMED terms (its `TERMS` list); these 4 are net-new → not added to `TERMS` → no bridge entry needed.
- **capability-as-prose-recommendation / engine-never-renders** — the book frames the loop as method; the engine only MEASURES (the `missing_capture` WARN).

Anchors the contract cites: `appendix-c-glossary.md` (4 new entries) · `14-foundation.md` (UDD design-loop ¶) · `add-method/tooling/test_docs_accord.py` (content assertions) · the 4 byte-identical book trees. Detail:
- `appendix-c-glossary.md` — the 4 new `**Term** — …` entries (`wireframe` · `design mock` · `capture` · `design-confirm`).
- `14-foundation.md` — the UDD section's design-definition-loop paragraph (the 4 ordered beats + capture-as-design-confirm-evidence + pointer to `design.md`).
- `add-method/tooling/test_docs_accord.py` — the content assertions.
- the 4 book trees (canonical · bundled · dogfood · root) held byte-identical by `test_book_parity` + `test_bundle_parity`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Propagate the UDD design-definition loop into the book + GLOSSARY (×4 byte-identical trees), closing the milestone — the loop is now described where a person learns ADD, not only in the agent's skill guide.

Framings weighed: conceptual-in-book + pointer-to-guide (chosen) · full-recipe-in-book · glossary-only-no-prose
- chosen — the book (audit trail, read once) gains a CONCISE loop description (the 4 named beats + capture-as-design-confirm) and POINTS to `design.md` for the recipe; the GLOSSARY gains 4 lean entries. Honors audit-trail-vs-working-state; no drift surface duplicated.
- full-recipe-in-book — relocate the kit/CSS/render recipe into chapter 14. Rejected: bloats the read-once book, duplicates `udd-wireframe.md`, creates a second copy that drifts.
- glossary-only — add 4 terms, no book prose. Rejected: exit criterion 5 says "Book + GLOSSARY describe the loop".

Must:
<must>
  - The book's UDD home (chapter `14-foundation.md`) names the design-definition loop with its 4 ordered beats — `review-domain → research-components → wireframe → render-capture-confirm` — frames the captured image as the human **design-confirm** evidence seen **before build**, and POINTS to the `design.md` skill guide for the operational recipe (not the recipe itself).
  - The GLOSSARY (`appendix-c-glossary.md`) defines all four terms — `wireframe`, `design mock`, `capture`, `design-confirm` — each as a single-line `**Term** — …` entry, with names matching the shipped `design.md` / `udd-wireframe.md` wording.
  - The `capture` and/or `design-confirm` entries also surface the capture location (`.add/design/captures/<name>.<ext>`), the `@json-render/image` named default, and the never-red `missing_capture` WARN — woven in, not as standalone terms.
  - Every book + glossary edit lands byte-identical in all four trees: canonical `add-method/docs/`, bundled `_bundled/docs/`, dogfood `.add/docs/`, repo-root `./`.
  - A new `test_docs_accord.py` asserts the book names the loop's 4 ordered beats AND the 4 glossary terms exist AND they accord with `design.md` (the beat names are not re-invented).
</must>
Reject:
<reject>
  - a book/glossary edit in one tree but missing or divergent in another -> "tree_drift"  (caught by test_book_parity / test_bundle_parity)
  - the operational recipe (kit classes, CSS vars, render/screenshot steps) copied into the book instead of a pointer -> "recipe_in_book"
  - a glossary term whose headword diverges from the shipped guide wording -> "term_mismatch"  (breaks ubiquitous language)
  - the 4 net-new terms added to GlossaryBridgeTest's rename-list (`TERMS`) -> "false_bridge"  (they are net-new, not renames)
</reject>
After:
<after>
  - `test_docs_accord`, `test_book_parity`, `test_bundle_parity` all green; the 4 book trees byte-identical; grep finds all 4 terms in the GLOSSARY.
  - exit criterion 5 met -> milestone `udd-design-loop` goal met (5/5) -> ready to fold + open the milestone PR.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] The Stage-B mock's glossary HEADWORD — `design mock` vs bare `mock`. The milestone's glossary-delta line says "**design mock** (Stage B hi-fi self-contained HTML render)"; exit criterion 5 + the task title abbreviate to "mock". Lowest confidence because the two milestone references disagree on the headword. Plan: headword **`Design mock`** (matches the delta; "mock" is a substring so a "mock" grep still hits) — `test_docs_accord` greps for `design mock` + the other three. If wrong (human wants bare `Mock`): rename one headword + the test's expected string; cost ~2 min, one tree-sweep.
  - [ ] Book home is chapter 14 (UDD foundation), not chapter 09 (the loop) — 14 is the UDD competency's home; 09 is the observe/lessons loop. If wrong: relocate one paragraph.
  - [ ] appendix-f (requirements matrix) + `PROJECT.md` UDD sketch are OUT of scope — exit criterion 5 needs only the book chapter + glossary. If wrong: a follow-up change-request, not a re-freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: book names the design-definition loop          # Must 1
  Given chapter 14-foundation.md's UDD section
  When a reader reads it
  Then it names the 4 ordered beats review-domain → research-components → wireframe → render-capture-confirm
  And it frames the captured image as the human design-confirm seen before build
  And it points to the design.md skill guide for the operational recipe

Scenario: glossary defines all four terms                # Must 2
  Given appendix-c-glossary.md
  When searched for the UDD design-loop terms
  Then each of wireframe, design mock, capture, design-confirm has a single-line **Term** — … entry
  And every headword matches the shipped design.md / udd-wireframe.md wording

Scenario: capture entries carry location, default, and WARN   # Must 3
  Given the capture / design-confirm glossary entries
  When read
  Then they surface .add/design/captures/<name>.<ext>, @json-render/image, and the missing_capture WARN
  And these appear woven into existing entries, not as standalone terms

Scenario: book trees stay byte-identical                 # Must 4
  Given the book + glossary edits
  When md5-compared across canonical, bundled, dogfood, and repo-root trees
  Then all four copies of each edited file are byte-identical

Scenario: docs-accord test passes                        # Must 5
  Given test_docs_accord.py
  When run with python3 -m unittest
  Then it asserts the book names the 4 ordered beats AND the 4 glossary terms exist AND they accord with design.md
  And it passes green

Scenario: a one-tree edit is rejected as drift           # Reject tree_drift
  Given a book/glossary edit applied to the canonical tree only
  When test_book_parity / test_bundle_parity run
  Then they go red naming the divergent file ("tree_drift")
  And no other tree was silently mutated to hide the drift

Scenario: the recipe is not copied into the book         # Reject recipe_in_book
  Given chapter 14-foundation.md after the edit
  When read
  Then it carries a POINTER to design.md, not the kit-class / CSS-var / screenshot recipe
  And udd-wireframe.md remains the single home of that recipe (unchanged)

Scenario: a divergent headword is rejected               # Reject term_mismatch
  Given a glossary headword that diverges from the design.md wording
  When test_docs_accord runs
  Then it goes red ("term_mismatch")
  And the shipped design.md wording is unchanged (the glossary conforms to the guide, not vice-versa)

Scenario: net-new terms are not added to the rename-bridge   # Reject false_bridge
  Given the 4 net-new terms
  When test_ubiquitous_language::GlossaryBridgeTest runs
  Then it stays green because the terms are NOT in the TERMS rename-list
  And the existing rename-bridge entries are unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT CONTRACT — book + GLOSSARY propagation (docs/method; content shape frozen, no code API)

GLOSSARY  appendix-c-glossary.md — 4 net-new single-line entries, format `**Headword** — definition.`:
  **Wireframe** — Stage-A low-fidelity structural map of one screen (regions + component slots) derived
      from `prototypes/<name>.json` BEFORE any color/type/spacing; answers "what goes where".
  **Design mock** — Stage-B high-fidelity SELF-CONTAINED HTML render of a screen: the catalog kit bound
      to `tokens.json`, populated with mock data, openable offline + screenshot-able; the visible evidence.
  **Capture** — the real rendered image (PNG/SVG) of a design mock = the design-confirm EVIDENCE artifact;
      lives at `.add/design/captures/<name>.<ext>`, attached/mentioned in the feature's TASK.md;
      `@json-render/image` (Satori→PNG/SVG) is the named default; `add.py check` raises a never-red
      `missing_capture` WARN for a prototype with no capture; the engine MEASURES presence, never renders.
  **Design-confirm** — the human touchpoint of the loop: approving the captured screen image BEFORE build
      (beat 4 of `design.md`), show-before-ask, so the build matches the layout the human has seen.

BOOK  14-foundation.md (UDD section) — a CONCISE paragraph that:
  - names the loop's 4 ordered beats: review-domain → research-components → wireframe → render-capture-confirm
  - frames the capture as the human design-confirm evidence seen BEFORE build
  - POINTS to the `design.md` skill guide for the operational recipe (NO kit/CSS/screenshot detail in the book)

PROPAGATION — every edited file byte-identical across the 4 book trees:
  add-method/docs/ · add-method/src/add_method/_bundled/docs/ · .add/docs/ · ./ (repo root)

TEST  add-method/tooling/test_docs_accord.py — asserts:
  book(14-foundation.md): the 4 beat tokens appear IN ORDER + "design-confirm" + a `design.md` pointer
  glossary: each of the 4 headwords present as `**Headword** —`
  accord: the beat names + capture location/default/WARN strings are sourced from design.md (not re-invented)
  -> ok 200: {book_loop: described, glossary_terms: 4/4, accord: true}
  -> red  : { error: "tree_drift" | "recipe_in_book" | "term_mismatch" | "false_bridge" }
  (cross-tree byte-identity is left to test_book_parity + test_bundle_parity — not duplicated here)
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-16
Least-sure flag surfaced at freeze: [spec] the Stage-B mock's glossary headword — `design mock` vs bare `mock`; resolved to **`Design mock`** (matches the milestone glossary-delta; "mock" is a substring so a `mock` grep still hits). Cost if wrong: a one-line headword + test-string rename.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavioral content assertions — one test per scenario (the content scenarios drive the NEW test; byte-identity/tree-drift is delegated to the existing test_book_parity + test_bundle_parity, referenced not duplicated).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_book_names_loop_beats_in_order: read canonical 14-foundation.md / assert the 4 beat tokens appear IN ORDER (review-domain, research-components, wireframe, render-capture-confirm) + "design-confirm" + a `design.md` pointer  [Must 1, scenario book-names-loop]
  - test_glossary_defines_four_terms: read appendix-c-glossary.md / assert `**Wireframe** —`, `**Design mock** —`, `**Capture** —`, `**Design-confirm** —` each present  [Must 2, scenario glossary-four-terms]
  - test_capture_entries_carry_location_default_warn: read the capture/design-confirm entries / assert they surface `.add/design/captures/`, `@json-render/image`, `missing_capture`  [Must 3, scenario capture-entries]
  - test_glossary_accords_with_guide: assert the 4 beat names present in the book are the SAME tokens design.md uses (sourced, not re-invented — read design.md, intersect)  [Must 5 + Reject term_mismatch, scenarios docs-accord / term-mismatch]
  - test_recipe_not_copied_into_book: assert 14-foundation.md carries a `design.md` pointer AND omits recipe-only tokens (`:root`, `var(--`, `kit class`, "headless screenshot")  [Reject recipe_in_book, scenario recipe-not-in-book]
  - test_terms_not_in_rename_bridge: import test_ubiquitous_language.TERMS / assert none of the 4 new slugs appear (they are net-new, not renames)  [Reject false_bridge, scenario net-new-not-bridged]
  - (tree_drift + byte-identity across the 4 trees: covered by test_book_parity + test_bundle_parity::test_docs_tree_byte_identical — asserted green in §6, not re-implemented here)
</test_plan>

Tests live in: `add-method/tooling/test_docs_accord.py` · MUST run red (book/glossary not yet edited) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/../14-foundation.md` `add-method/docs/14-foundation.md` `add-method/src/add_method/_bundled/docs/14-foundation.md` `.add/docs/14-foundation.md` `add-method/../appendix-c-glossary.md` `add-method/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `.add/docs/appendix-c-glossary.md` `add-method/tooling/test_docs_accord.py`   — ch14 ×4 (repo-root via the `add-method/..` climb · canonical · bundled · dogfood) + appendix-c glossary ×4 + the new content test. The `.add/…` homes are ride-along (scope-walk excludes `.add/`); the `add-method/…` copies, the repo-root copies, + the test are the gated anchors. NO `add.py`/engine edit — pure docs, convention-guided.
Strategy (ordered batches): 1. write the 4 glossary entries in canonical appendix-c-glossary.md (single source). 2. add the design-definition-loop paragraph to canonical 14-foundation.md. 3. author test_docs_accord.py; run red. 4. propagate both files byte-identical to the 3 other trees (repo-root, _bundled, .add/docs). 5. run test_docs_accord + test_book_parity + test_bundle_parity green.
Safety rule (feature-specific): the canonical `add-method/docs/` copy is the single source; every other tree is a byte-identical propagation of it (cmp-verified) — never hand-edit the copies independently (that is the tree_drift the parity tests catch).
Code lives in: `add-method/docs/` (+ its 3 propagated trees) · the test in `add-method/tooling/`
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

- [x] all tests pass — full suite **1152 green** (`python3 -m unittest discover`); task suite `test_docs_accord` 7/7 + `test_book_parity` + `test_bundle_parity` 8/8.
- [x] coverage did not decrease — docs + one new test added; no source code removed/weakened.
- [x] no test or contract was altered during build — §3 contract FROZEN @ v1 untouched; `test_docs_accord` written in the tests phase, unchanged in build. (The release-gate test migration is a SEPARATE human-approved commit `d8bc376`, not this build — verified by re-anchoring the scope baseline to after it.)
- [x] the green was EARNED, not gamed — refute-read: `test_glossary_defines_four_terms` matches real `**Headword** —` regex on the actual file; `test_book_names_loop_beats_in_order` asserts the 4 beats IN ORDER; `test_beats_are_sourced_from_the_guide` cross-checks design.md so a renamed beat can't pass; `recipe_not_in_book` + `not_in_rename_bridge` are real never-regress guards. No vacuous asserts (the red→green transition proved each fires).
- [x] concurrency / timing — N/A (static docs + a read-only content test).
- [x] no exposed secrets, injection, or unexpected dependencies — docs only; the new test imports stdlib + the in-repo `engine_pin`/`test_ubiquitous_language`.
- [x] layering & dependencies follow CONVENTIONS.md — audit-trail-vs-working-state honored: the book gets a conceptual ¶ + pointer; the recipe stays in `design.md`/`udd-wireframe.md` (enforced by `recipe_not_in_book`). 4-tree byte-identity held (one md5 each).
- [ ] a person reviewed and approved the change — **pending the human verify gate** (risk:high · conservative).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [n/a] WIRING (code) — no new code symbols; the new test's classes/methods are discovered by unittest and run green.
- [n/a] DEAD-CODE (code) — no new source symbols introduced; `test_release_1_4_0.py` retired cleanly (its sole external reference, `test_shared_engine_pin.IMPORTERS`, repointed).
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the rendered ch.14 ¶ + the 4 glossary entries were read end-to-end. Confirmed: the ¶ names the 4 beats in order, frames capture as design-confirm-before-build, points to `design.md`, and inlines NO recipe tokens; the 4 entries match `design.md`/`udd-wireframe.md` wording, the capture entry carries location + `@json-render/image` + `missing_capture`, and all 4 copies of both files are byte-identical (single md5 each across canonical · bundled · dogfood · root).

Scope note: book-glossary-align's scope baseline was re-anchored (the documented `re-advance through tests→build`) AFTER the separate release-gate commit `d8bc376` and after the serena MCP cache settled, so the gate witnesses only this task's footprint (the 6 tracked doc files, all in declared §5 scope) — `add.py check` shows 0 out-of-scope touches.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-16
Evidence: full suite 1152 green (test_docs_accord 7/7 + test_book_parity + test_bundle_parity 8/8); §3 contract untouched; semantic read of the rendered ch.14 ¶ + 4 glossary entries confirmed accord with design.md + no recipe leakage + 4-tree byte-identity; scope re-anchored past the separate release-gate commit → 0 out-of-scope touches.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): test_docs_accord (book ¶ + 4 glossary terms still accord with design.md) · test_book_parity + test_bundle_parity (the 4 book trees stay byte-identical) — any future design.md beat rename re-reds test_docs_accord, forcing the book to follow.
Spec delta for the next loop: a method-concept now ships in FOUR doc homes (canonical · bundled · dogfood · repo-root). The `add-method/..` climb is the established way to scope-declare the repo-root copy; the dogfood `.add/docs` is unguarded (scope-walk excludes `.add/`) and must be synced by hand. A `_DOC_TREES` parity helper covering all four (not just canonical↔bundle and canonical↔root) would close the dogfood gap.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [UDD · folded] the design-definition loop now lives where a PERSON learns it (book ch.14 + GLOSSARY), not only in the agent's skill guide — closing the audit-trail half of the loop's documentation (evidence: test_docs_accord asserts the book names the 4 beats + the 4 terms exist + accord with design.md; 5/5 exit criteria met).
- [ADD · folded] the scope gate flags tool-cache writes: the serena MCP cache (`.serena/cache/`) is not in `_SCOPE_EXCLUDE_DIRS`, so mid-verify serena use shows as out-of-scope touches; worked around by re-anchoring, but adding `.serena` to the exclude set is the durable fix (evidence: `add.py check` raised `scope_violation` for `.serena/cache/...` after a verify-phase serena call).
- [ADD · folded] the release-gate forward-pin migration is a separate, easy-to-forget step from the version bump: cutting 1.5.0 bumped the 3 sources + CHANGELOG but left `test_release_1_4_0.py` pinned, reddening the suite until migrated (evidence: 3 reds on `release/v1.5.0` cleared only by commit d8bc376). A `chore(release)` that bumps versions should migrate the pinned test in the SAME commit.
- [TDD · folded] a docs-content guard (`test_docs_accord`) earns its keep by cross-checking the SOURCE (design.md), not just asserting the target — so a beat rename can't pass by editing only the book (evidence: `test_beats_are_sourced_from_the_guide` intersects book ∩ guide).
