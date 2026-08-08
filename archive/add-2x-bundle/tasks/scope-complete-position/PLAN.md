# TASK: scope.md: full-template coverage + Position-the-goal step (E1+E2)

slug: scope-complete-position · created: 2026-06-18 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from auto: editing scope.md is a method/trust-layer change (high-risk residue) — verify escalates to a human gate, never an auto-pass. -->
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
  - `skill/add/scope.md` ×3 parity trees — `.claude/skills/add/scope.md` (dogfood) · `add-method/skill/add/scope.md` (canonical) · `add-method/src/add_method/_bundled/skill/add/scope.md` (pip bundle). The guide being rewritten; its "Drafting … (section by section)" covers 6 of the template's 9 sections today.
  - `tooling/templates/MILESTONE.md.tmpl` — the 9-section shape scope.md must fully cover: header(goal · rationale · stage) · Scope · Shared decisions · Shared contracts · Tasks · Exit criteria · Close—ship review · Release steps. (Template is COMPLETE; only the GUIDE drifted — template is OUT of scope.)
  - `skill/add/intake.md:` the upstream classifier (4 buckets + reject codes not_classified/frozen_scope/split_required, the active-milestone "covers this?" test). scope.md must POINT AT it, not restate it; the new `duplicate_goal` reject is a DRAFTING (positioning) concern, distinct from intake's `frozen_scope`.
  - `tooling/test_scope_loop.py:ScopeLoopTest` — the structure test. `REJECT_CODES = {not_classified, dangling_criterion, no_milestone}` and `OUTCOME_TOKENS`, md5 parity (canon↔dogfood), worked-example-names-a-real-milestone. New assertions extend HERE.
  - `tooling/test_tree_parity.py` (canon↔dogfood, whole tree) + `tooling/test_bundle_parity.py` (canon↔_bundled) — the guards that catch a missed copy.
  - `tooling/wording_lint.py` + `tooling/test_wording_lint.py` — the guide must pass (no bare status/process slang; backtick lifecycle terms).
Context (working folder):
  - `.add/milestones/*/MILESTONE.md` + `.add/archive/*` — the asset the Position-the-goal step greps for existing goals (each carries a `goal:` line); ~28 active + ~28 archived.
  - `.add/PROJECT.md` — the "ground the goal in current assets" half (domain · spec · UI/UX).
  - `docs/` book — check whether a chapter describes scope drafting (book-accord); minimal touch only if so (checked at build).
Honors (patterns / conventions):
  - 3-tree scope.md parity (md5-equal) — enforced by test_tree_parity (canon↔dogfood) + test_bundle_parity (canon↔_bundled).
  - wording-lint clean (PROJECT.md SDD lesson: the domain wording-lint rejects status-name slang — document the grammar abstractly).
  - method/trust-layer edit = high-risk residue → verify escalates to a human (autonomy conservative).
  - the guide DESCRIBES/PRESCRIBES and POINTS AT intake.md — it must not become a second source of truth for classification (decision-suggestions SDD lesson: a docs artifact verifies by own-entry + cross-tree md5 + points-at-source).
Anchors the contract cites:
  - scope.md headings: the new "Position the goal" step · the section-by-section 9-section list · the reject-codes block (`duplicate_goal`) · the draft well-formedness gate.
  - `tooling/test_scope_loop.py:REJECT_CODES` (extended to 4) + the new test methods.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: scope.md — full-template coverage (E1) + a Position-the-goal first step & duplicate_goal reject (E2).
Framings weighed: extend scope.md in place (chosen) · a separate positioning.md guide (rejected — fragments the scope-drafting flow) · push positioning into intake.md (rejected — intake CLASSIFIES the bucket, scope DRAFTS the goal; positioning informs the goal sentence, a drafting concern).
Must:
<must>
  - E1a — scope.md's "section by section" names ALL 9 MILESTONE.md.tmpl sections, including `rationale` (carry the confirmed bucket+reason into the header).
  - E1b — it explicitly marks `Close — ship review` + `Release steps` as drafted-BLANK at scope time, owned by the close/release flows (`fold.md` / `release.md`) — so a drafter neither fills them prematurely nor reads the draft as "incomplete".
  - E1c — it carries a draft well-formedness gate (a checklist a draft passes BEFORE it is proposed): goal is one outcome sentence · every exit criterion maps to a task slug · rationale records the relationship + bucket · Close/Release left as template.
  - E2a — it adds a "Position the goal" step as the FIRST move of scope drafting (before Diverge): ground the goal in current assets (PROJECT.md · code · docs) AND cross-reference every existing+archived milestone goal to capture the relationship (extends / depends-on / overlaps / duplicates), recorded in `rationale`.
  - E2b — it adds a `duplicate_goal` reject code: a goal already delivered by an existing milestone is NOT forked — route as a `task`/`change-request`, create nothing.
  - Parity/cleanliness — all 3 scope.md copies stay md5-equal; the guide passes wording-lint; the engine (add.py) is untouched (ENGINE_MD5 holds); the retained content (4 intake outcomes · confirm-before-create · exit→slug · worked example naming a real milestone) survives.
</must>
Reject:
<reject>
  - goal already delivered by an existing milestone -> "duplicate_goal"   (new — don't fork; route as task/change-request)
  - request not yet classified by intake -> "not_classified"             (retained)
  - a drafted exit criterion maps to no declared task slug -> "dangling_criterion"   (retained)
  - intake routed the request to task/change-request -> "no_milestone"   (retained)
</reject>
After:
<after>
  - A drafter following scope.md fills all 9 sections correctly (Close/Release left blank by design) and positions the goal against assets + the milestone map before drafting the goal sentence.
  - test_scope_loop asserts the new step + `duplicate_goal` + 9-section coverage + the well-formedness gate; all 3 copies are md5-equal; wording-lint + the suite are green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The positioning step belongs in scope.md, not intake.md — lowest confidence because it partly overlaps intake's "does an active milestone's goal cover this?" bucket test; if wrong: duplicated guidance across two guides (drift risk). Mitigation: scope.md POINTS AT intake's bucket test and adds only the asset-grounding + archived-milestone relationship that intake does not do.
  - [x] "all 9 sections" counts goal · rationale as named items — CONFIRMED: test_covers_all_nine_template_sections passes with both counted.
  - [x] book-accord — SKIPPED (honest): no `docs/` chapter enumerates the scope-drafting steps; the guide scope.md is the source. The book describes task-level co-specify (docs/03), not the milestone step list.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: full-template coverage
  Given the MILESTONE.md template has 9 sections
  When scope.md's section-by-section is read
  Then it names all 9 (incl. rationale, Close ship-review, Release steps)
  And the 4 intake outcomes table + confirm-before-create invariant remain documented

Scenario: Close and Release marked drafted-blank
  Given Close ship-review + Release steps are filled at close/release, not at draft
  When scope.md describes those two sections
  Then it marks them drafted-blank and names their owning flow (fold.md / release.md)

Scenario: draft well-formedness gate present
  Given a drafter about to PROPOSE a MILESTONE.md
  When they consult scope.md
  Then a well-formedness checklist is present (one-sentence goal · exit→slug · rationale · Close/Release blank)

Scenario: position-the-goal is the first step
  Given a classified new-major/sub-milestone request
  When scope drafting begins
  Then scope.md's FIRST step grounds the goal in assets AND cross-references existing+archived milestone goals, recording the relationship in rationale

Scenario: duplicate_goal reject
  Given a goal already delivered by an existing milestone
  When the drafter positions it
  Then scope.md directs a duplicate_goal reject (route as task/change-request, create nothing)
  And the other 3 reject codes (not_classified · dangling_criterion · no_milestone) remain documented

Scenario: 3-tree parity and lint hold
  Given scope.md is edited
  When the suite runs
  Then md5(canonical) == md5(dogfood) == md5(_bundled) and wording-lint is clean
  And add.py is unchanged (ENGINE_MD5 pin holds)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: skill/add/scope.md   (×3 parity trees — dogfood · canonical · _bundled)
  A prose-convention contract: the checkable seam is a TOKEN SET + structural invariants
  (not an HTTP shape). test_scope_loop.py asserts it.

Structural invariants (all must hold):
  - the section-by-section enumerates all 9 MILESTONE.md.tmpl sections
  - `Close — ship review` AND `Release steps` are marked drafted-blank / filled-later
  - a "Position the goal" step exists as the FIRST scope-drafting move (heading present),
    citing current assets AND the existing+archived milestone map
  - a draft well-formedness gate (checklist) is present
  - reject codes == { not_classified, dangling_criterion, no_milestone, duplicate_goal }   (4th added)
  - RETAINED: 4-outcome table · confirm-before-create · exit-criterion→task-slug · worked
    example names a real milestone slug
  - PARITY: md5(canonical) == md5(dogfood) == md5(_bundled)
  - LINT: wording-lint clean
  - ENGINE: add.py ENGINE_MD5 unchanged (no engine edit)

Frozen tokens (must appear verbatim in scope.md):
  "Position the goal"  ·  "duplicate_goal"  ·  "drafted-blank"  ·  "well-formedness"

reject codes -> { not_classified | dangling_criterion | no_milestone | duplicate_goal }
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-18)
Least-sure flag surfaced at freeze: [spec] positioning lives in scope.md not intake.md — overlaps intake's active-milestone "covers this?" test; if wrong: duplicated guidance across two guides (drift). Mitigated: scope.md points at intake and adds only asset-grounding + the archived-milestone relationship intake does not do.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/scope.md` `.claude/skills/add/scope.md` `add-method/src/add_method/_bundled/skill/add/scope.md`   <the scope.md guide across its 3 parity trees — canonical · dogfood · pip bundle>
Strategy (ordered batches): 1. edit the canonical `add-method/skill/add/scope.md` 2. mirror byte-for-byte to the dogfood (`.claude/skills/add`) + bundle (`_bundled/skill/add`) copies so all 3 are md5-equal.
Safety rule (feature-specific): all 3 scope.md copies stay md5-equal after every edit; the engine (add.py) is never touched (ENGINE_MD5 holds).
Code lives in: the 3 `skill/add/scope.md` parity trees (a guide edit — no `./src/`).
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

- [x] all tests pass — full suite 1276 green (`python3 -m unittest discover -s tooling`)
- [x] coverage did not decrease — added 5 assertions to test_scope_loop; removed none
- [x] no test or contract was altered during build — §3 frozen; scope.md edited, tests only ADDED
- [x] the green was EARNED, not gamed — tests assert real scope.md content (frozen tokens · 9 sections · 3-tree md5), not vacuous; a stub scope.md goes red
- [x] concurrency / timing of the risky operation is safe — N/A (static guide edit, no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A (prose; no deps added)
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree parity honored; engine untouched (ENGINE_MD5 holds)
- [x] a person reviewed and approved the change — Tin Dang approved PASS at the verify gate (2026-06-18)

### Build expectations — what "correct" looks like (confirmed at this gate)
- [x] scope.md has a "Position the goal" step grounding in assets + the milestone map — confirmed by test_position_the_goal_is_the_first_drafting_step + a full read of scope.md
- [x] all 9 template sections named · Close/Release drafted-blank · well-formedness gate present — confirmed by test_covers_all_nine_template_sections + test_marks_close_and_release_drafted_blank + test_well_formedness_gate_present
- [x] duplicate_goal documented · 3 copies md5-equal — confirmed by test_documents_all_reject_codes + test_scope_md5_parity_across_three_trees

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — N/A (no new code symbols; a guide + test edit)
- [ ] DEAD-CODE (code) — N/A
- [x] SEMANTIC (prose / non-code) — read scope.md in full after edit: the "Position the goal" step, the rationale bullet, the Close/Release drafted-blank note, the well-formedness gate, and the duplicate_goal reject are present, coherent, and POINT AT intake.md (not a second classification source); the retained 4-outcome table + worked example survive.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-18

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
