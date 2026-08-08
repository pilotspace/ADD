# TASK: Confidence self-score rubric guideline

slug: confidence-rubric · created: 2026-06-14 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from the project default (auto): this scope is method-defining (it edits the method's own trust surface — how confidence relates to autonomy/gating), so the high-risk guard requires a lowered rung. The verify gate stays human. -->
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
  - `add-method/skill/add/confidence.md` — NEW: the deliverable guideline doc (does not exist yet)
  - `add-method/skill/add/streams.md:185-186` — the existing confidence self-score SEED line ("Score confidence (0-1) on Completeness · Clarity · Practicality · Optimization · EdgeCases · Self-Eval; if any < 0.9, refine") — this rubric generalizes it; the streams worker prompt keeps citing it
  - `add-method/skill/add/run.md:33-43` — the "lowest-confidence flag" section + run.md:42 ("a self-asserted gate would just move the unread approval one level up") — the constraint this rubric MUST honor: confidence never gates
  - `add-method/skill/add/phases/1-specify.md:31-36` — the lowest-confidence-first FLAG the rubric feeds (a distinct, existing concept — must not be conflated or redefined)
  - `add-method/tooling/test_xml_convention.py:28-30` (VOCAB = {prompt, exit_gate, constraints, reject_codes, output_format}) and `:193-257` (ENGINE_FILES registry) — a new engine doc carrying a `<constraints>` block must be REGISTERED here (extends the guard = strengthening, not weakening)
Context (working folder):
  - `.add/GLOSSARY.md:23` — defines "lowest-confidence flag"; the new "confidence self-score" must be a DISTINCT, non-conflicting term (ubiquitous language; test_ubiquitous_language.py)
  - `add-method/CONTRIBUTING.md` — the edit-then-sync model: a new `skill/add/*.md` needs prepare_bundle.py + mirror propagation to `.claude/skills/add` (deferred to per-step-hooks, but the parity guards see it)
  - NEW content-assertion test this task adds (e.g. `add-method/tooling/test_confidence_rubric.py`) — the red suite for §4
Honors (patterns / conventions):
  - the frozen XML vocabulary (test_xml_convention) — confidence.md uses ONLY the 5-tag set outside code fences; if it carries `<constraints>`, register it in ENGINE_FILES
  - wording-lint (test_wording_lint) + ubiquitous language (test_ubiquitous_language) — terms stay consistent; "confidence self-score" is distinct from "lowest-confidence flag"
  - minimalism (PROJECT.md core value; memory: lean over doc-heavy) — keep the doc THIN; progressive disclosure (a hook points here, this doc holds the detail)
  - "the AI never asserts a gate it cannot prove" (run.md) — the rubric is advisory-only
Anchors the contract cites: `confidence.md` (new) · the six dimensions · the 0-1 scale · the refine-if-<0.9 threshold · the "feeds the lowest-confidence flag" link · the "advisory-only / never a gate" rule · the `<constraints>` block + ENGINE_FILES registration · the new content test

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `confidence.md` — the confidence self-score rubric guideline. A shared, advisory AI self-assessment (0-1 across six dimensions) the agent computes on its own drafted artifact at a decision point: it sharpens the work, feeds the lowest-confidence flag, and may recommend lowering autonomy — but it is NEVER a gate.
Framings weighed: a separate thin `confidence.md` the per-step hooks point to (chosen — progressive disclosure, one source of truth) · inline the rubric into each of the 8 phase guides (rejected — bloats every guide, violates minimalism + DRY) · append it to run.md's lowest-confidence section (rejected — conflates the private self-score with the public flag; run.md is already dense)
Must:
<must>
  - define a 0-1 self-score across EXACTLY six named dimensions: Completeness · Clarity · Practicality · Optimization · Edge cases · Self-evaluation
  - state the refine rule: if ANY dimension scores < 0.9, refine the artifact before presenting it / returning from a spawned subagent
  - state that the self-score FEEDS the lowest-confidence flag (cite run.md / 1-specify.md; the lowest-scoring point becomes the ⚠ flag) — cite, never redefine the existing term
  - state that a persistently low score MAY recommend lowering autonomy (auto -> conservative/manual) — recommend-only language, never "must"/"forces"
  - carry a `<constraints>` block: the rubric is advisory-only — never a gate, never an auto-PASS, never a substitute for evidence or the human decision point
  - register `confidence.md` in test_xml_convention ENGINE_FILES (tags={constraints}) so the frozen-vocab guard covers it (strengthening, per the test_setup_lock precedent)
  - stay THIN — the detail lives here; a per-step hook (per-step-hooks task) only points here
</must>
Reject:
<reject>
  - the doc lets the score GATE — auto-PASS, auto-block, or stand in for evidence/the human decision point -> "confidence_as_gate"
  - a paired convention tag outside the frozen 5-tag vocab appears in the doc -> "vocab_offmidiom"
  - the doc redefines or conflates the existing "lowest-confidence flag" term -> "term_conflict"
</reject>
After:
<after>
  - `add-method/skill/add/confidence.md` exists with the six-dimension 0-1 rubric + refine-if-<0.9 + the feeds-flag link + the may-recommend-autonomy line + the advisory-only `<constraints>` block
  - test_xml_convention is green with confidence.md registered as an engine doc (tags ⊆ {constraints})
  - `add-method/tooling/test_confidence_rubric.py` asserts every required anchor + the reject codes; RED before confidence.md exists, GREEN after
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ✓ [RESOLVED @ freeze] confidence.md is a NEW standalone engine doc (carrying `<constraints>`, registered in ENGINE_FILES) rather than a section appended to run.md — human chose the standalone doc when approving the bundle as drafted; the registry edit only ADDS coverage (strengthens).
  - [x] the six dimensions are exactly those six, with these names (Completeness · Clarity · Practicality · Optimization · Edge cases · Self-evaluation) — confirmed at freeze (approved as drafted)
  - [x] the refine threshold is < 0.9 — confirmed at freeze (approved as drafted)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the six dimensions are defined
  Given confidence.md
  When an agent reads it
  Then it names exactly six 0-1 dimensions: Completeness, Clarity, Practicality, Optimization, Edge cases, Self-evaluation

Scenario: the refine threshold is stated
  Given confidence.md
  When an agent reads it
  Then it states "if any dimension < 0.9, refine before presenting / returning"

Scenario: the self-score feeds the lowest-confidence flag
  Given confidence.md
  When an agent reads it
  Then it cites the lowest-confidence flag (run.md / 1-specify.md) as where the lowest-scoring point surfaces
  And the existing "lowest-confidence flag" definition in GLOSSARY.md is unchanged

Scenario: low confidence may recommend lowering autonomy
  Given confidence.md
  When an agent reads it
  Then it says a persistently low score MAY recommend lowering autonomy (recommend-only language)
  And it does NOT make lowering autonomy mandatory

Scenario: the rubric is advisory-only (the hard rule)
  Given confidence.md
  When an agent reads it
  Then a <constraints> block states the score is never a gate, never an auto-PASS, never a substitute for evidence or the human decision point

Scenario: the frozen XML vocabulary still holds
  Given the skill tree with confidence.md registered in ENGINE_FILES
  When test_xml_convention runs
  Then it is green, with confidence.md's paired convention tags ⊆ {constraints}

Scenario: a gate-shaped draft is rejected
  Given a draft of confidence.md that lets the score auto-PASS verify
  When test_confidence_rubric runs
  Then it fails "confidence_as_gate"
  And the advisory-only rule remains the only stated behavior of the score

Scenario: an off-vocabulary tag is rejected
  Given confidence.md carrying a paired top-level tag outside the frozen vocab
  When test_xml_convention runs
  Then it fails "vocab_offmidiom"
  And the frozen 5-tag VOCAB set is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC  add-method/skill/add/confidence.md   (a skill ENGINE doc; mirrored byte-for-byte to .claude/skills/add/confidence.md + _bundled/)
  REQUIRED anchors (each asserted by test_confidence_rubric):
    - intro names it the "confidence self-score" and the word "advisory"
    - the six dimensions, each named: Completeness · Clarity · Practicality · Optimization · Edge cases · Self-evaluation
    - the 0-1 scale AND the rule "if any < 0.9, refine before presenting / returning"
    - a line citing the lowest-confidence flag (mentions run.md or 1-specify.md) — reference, not redefinition
    - a "MAY recommend lowering autonomy" line (contains "recommend"; does NOT contain "must lower"/"forces")
    - a <constraints> block containing "never a gate" (and never auto-PASS / never substitutes for evidence or the human decision point)
  VOCAB: paired convention tags (code fences stripped) ⊆ {constraints}
  REGISTRY: confidence.md ∈ test_xml_convention.ENGINE_FILES with tags={"constraints"}
  Reject codes: confidence_as_gate · vocab_offmidiom · term_conflict

TEST  add-method/tooling/test_confidence_rubric.py   — asserts every REQUIRED anchor + VOCAB + REGISTRY; RED before confidence.md exists, GREEN after.
PROPAGATION (in THIS task — parity guards are global, so they cannot be deferred): after creating confidence.md canonical, run prepare_bundle.py (regenerates _bundled/) and mirror-copy to .claude/skills/add/confidence.md, so test_tree_parity + test_bundle_parity stay green at this task's verify.
```

Least-sure flag surfaced at freeze: ⚠ [contract] confidence.md as a NEW standalone engine doc + a test_xml_convention registry edit (vs. appending to run.md) — most likely wrong because it adds a file + touches the guard; if wrong: needless churn. Resolved: human chose the standalone doc; the registry edit only ADDS coverage (strengthens, never weakens).

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-14
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every REQUIRED anchor + each reject code has an assertion (content test, not %-coverage).
Plan (one test per scenario, asserting observable doc content):
<test_plan>
  - test_six_dimensions: read confidence.md / assert all six dimension names present (Completeness, Clarity, Practicality, Optimization, Edge cases, Self-evaluation)
  - test_scale_and_refine_threshold: assert "0-1"/"0 to 1" scale AND "if any ... < 0.9 ... refine" present
  - test_feeds_lowest_confidence_flag: assert the doc cites the lowest-confidence flag (mentions run.md or 1-specify.md) — and that GLOSSARY.md's flag definition is unchanged (term_conflict guard)
  - test_may_recommend_autonomy: assert a recommend-only autonomy line ("recommend" present; "must lower"/"forces" absent)
  - test_advisory_only_constraints_block: assert a <constraints> block containing "never a gate" (confidence_as_gate guard)
  - test_vocab_subset: paired tags (fences stripped) in confidence.md ⊆ {constraints}  (vocab_offmidiom guard)
  - test_registered_in_engine_files: confidence.md ∈ test_xml_convention.ENGINE_FILES with tags={"constraints"} (the guard actually covers the new doc)
  - test_xml_convention_still_green: import + run the xml-convention engine-doc checks; confidence.md passes them
</test_plan>

Tests live in: `add-method/tooling/test_confidence_rubric.py` · MUST run red (missing confidence.md + missing registration) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/confidence.md` · `add-method/tooling/test_xml_convention.py` · `add-method/tooling/test_confidence_rubric.py` · `add-method/tooling/test_wording_lint.py` · `add-method/src/add_method/_bundled/skill/add/confidence.md` · `.claude/skills/add/confidence.md`
Strategy (ordered batches): 1. write the red suite test_confidence_rubric.py (RED — confidence.md absent, not registered). 2. author confidence.md canonical. 3. register confidence.md in test_xml_convention ENGINE_FILES (tags={constraints}) — STRENGTHENS the guard (test_setup_lock precedent). 4. propagate: prepare_bundle.py + mirror-copy to .claude/skills/add — all parity green.
Scope note (build-discovered, disclosed at the gate): `add-method/tooling/test_wording_lint.py` joined scope — `test_surface_files_cover_the_contract` pins the exact skill-file COUNT (was 22), so adding confidence.md needs the count bumped to 23 + a `confidence.md` membership assert. This STRENGTHENS the guard (one more file linted, confidence.md cannot silently escape the wording lint) — it does not weaken it (rule #3 holds). It is the documented inventory-growth pattern (the test's own `+loop.md @ v20, +graduate.md @ v22` note). The §0 GROUND anticipated the parity/lint guards would "see" a new skill file.
Safety rule (feature-specific): the edits to test_xml_convention.py (ENGINE_FILES registration) and test_wording_lint.py (count bump) only ADD confidence.md to each guard's coverage — they never relax VOCAB, ENGINE_SUBSET, the lint rubric, or any existing assertion (no test weakened; rule #3 holds).
Code lives in: `add-method/skill/add/confidence.md` (canonical) + its two mirrors; tests in `add-method/tooling/`.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib unittest); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — the 7 affected guards are green (54/54: test_confidence_rubric 8 · test_xml_convention · test_wording_lint · test_ubiquitous_language · test_tree_parity · test_book_parity · test_bundle_parity). Full suite: 1007 pass / 8 fail — all 8 are the node/npx/pip subprocess tests CONTRIBUTING.md names (test_installer_handoff · test_v8_install · test_shared_engine_pin's cascade), environmental (no node/npx/pip in this sandbox), untouched by this change.
- [x] coverage did not decrease — added test_confidence_rubric.py (8 assertions); net increase
- [x] no test or contract was altered during build — the frozen §3 contract is unchanged; the two guard edits (test_xml_convention ENGINE_FILES registration — contracted; test_wording_lint count bump — build-discovered, §5) only ADD confidence.md to coverage (strengthen, never weaken; rule #3 holds)
- [x] the green was EARNED, not gamed — adversarial refute-read done inline (the change is tiny + fully inspectable, so no subagent spawned — same judgment the advisor doc will encode): the assertions check real content (six dimension names · the < 0.9 threshold · a <constraints> block literally forbidding gating/auto-PASS · vocab subset · registration), none tautological; confidence.md is the actual deliverable prose, not a stub; no test weakened
- [x] concurrency / timing — N/A: a static markdown doc + content tests; no runtime/concurrent path
- [x] no exposed secrets, injection openings, or unexpected dependencies — new test imports stdlib only (importlib · re · unittest · pathlib); no secrets; no security surface
- [x] layering & dependencies follow CONVENTIONS.md — confidence.md follows the established engine-doc pattern (like run.md), is registered in the vocab guard, and honors CONTRIBUTING's edit-then-sync (canonical + both mirrors propagated)
- [x] a person reviewed and approved the change — Tin Dang approved PASS at the verify gate 2026-06-14

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new test methods are collected/run by unittest discovery; ENGINE_FILES["confidence.md"] is consumed by test_xml_convention's loops AND by test_confidence_rubric.test_registered_in_engine_files. No unreferenced symbol.
- [x] DEAD-CODE (code) — no orphaned code. NOTE (disclosed): confidence.md is itself not yet referenced by any phase guide — by design, the per-step-hooks task (task 3) wires it in; the doc carries a forward pointer ("Used per step …"). Orphan-until-task-3 is the breadth-first decomposition, not a dead end.
- [x] SEMANTIC (prose) — read confidence.md in full: it states the six dimensions, the 0–1 scale, the < 0.9 refine rule, the feeds-the-lowest-confidence-flag link (run.md · 1-specify.md, citing not redefining), the recommend-only autonomy line, and the advisory-only <constraints> block (never a gate / never auto-PASS / never substitutes for evidence or the human decision point). Matches every frozen §3 anchor.

Dogfood — confidence self-score on this task's own deliverable (confidence.md): Completeness 0.95 · Clarity 0.95 · Practicality 0.95 · Optimization 0.9 · Edge cases 0.9 · Self-evaluation 0.95 → all ≥ 0.9, no refine pass needed.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-14

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
