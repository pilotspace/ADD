# TASK: TASK.md.tmpl §6 + 6-verify.md: AI-filled build-expectations block

slug: verify-build-expectations · created: 2026-06-18 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from auto: editing TASK.md.tmpl + a phase guide is a method/trust-layer change (high-risk residue) — verify escalates to a human gate, never an auto-pass. -->
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
  - `tooling/templates/TASK.md.tmpl` ×3 parity (`.add/tooling/templates` · `add-method/tooling/templates` · `add-method/src/add_method/_bundled/tooling/templates`) — the `## 6 · VERIFY` section; today it has a checklist + a `### Deep checks` subsection + `### GATE RECORD`. The new `### Build expectations` block lands here, mirroring the `### Deep checks` shape.
  - `skill/add/phases/6-verify.md` ×3 parity (dogfood · canonical · `_bundled`) — the verify guide; add a cue to FILL the expectations before build and CONFIRM each at verify.
  - `tooling/test_template_form_tags.py` — pins TASK.md.tmpl's 6 form-tag regions {must·reject·after·assumptions·scenarios·test_plan} + engine seams + labels; the new block must NOT touch a parsed seam (engine reads the scaffold unchanged). Extend with a `### Build expectations` presence assertion.
  - `tooling/test_tree_parity.py` (guide: canon↔dogfood) + the bundle/packaging parity guard (canon↔_bundled) — catch a missed copy.
  - `tooling/wording_lint.py` + `tooling/test_wording_lint.py` — the new guide prose must pass.
Context (working folder):
  - TASK.md.tmpl `## 2 · SCENARIOS` + `## 3 · CONTRACT` sections — the expectations are DERIVED from these; the block cross-references them.
  - TASK.md.tmpl §6 existing line "the green was EARNED, not gamed …" — the new block COMPLEMENTS it (proactive expectations vs the adversarial refute-read).
  - `docs/08-step-6-verify.md` (book) — check for a scope-drafting/verify description needing a minimal accord touch (checked at build).
Honors (patterns / conventions):
  - 3-tree template parity (TASK.md.tmpl) + 3-tree guide parity (phases/6-verify.md), md5-equal.
  - the engine-reads-scaffold-unchanged seam (test_template_form_tags) — the new block is plain markdown, NOT a parsed region.
  - wording-lint clean; method/trust-layer edit = high-risk residue → verify is a human gate (conservative).
Anchors the contract cites:
  - TASK.md.tmpl §6 `### Build expectations` heading + its fill-before-build cue + the observable+confirmed-by row shape.
  - phases/6-verify.md the fill+confirm cue.
  - `tooling/test_template_form_tags.py` new `### Build expectations` assertion (+ seam-untouched proof).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §6 VERIFY gains an AI-filled "Build expectations" block so verify confirms the build is CORRECT, not merely test-green.
Framings weighed: a new `### Build expectations` subsection in §6 (chosen — mirrors `### Deep checks`, engine-agnostic) · a new top-level §6.5 phase (rejected — changes the 8-phase flow, heavy) · fold it into the existing "earned green" line (rejected — that's an adversarial refute-read, not a proactive expectation declaration).
Must:
<must>
  - TASK.md.tmpl §6 VERIFY gains a `### Build expectations` block the AI fills BEFORE build, with each row an OBSERVABLE outcome a correct build must produce + a `confirmed by <how/where>`, DERIVED from §2 SCENARIOS + §3 CONTRACT.
  - The block carries a one-line cue stating expectations are evidence-you-can-SEE (not a restatement of a test name) and are written before build, confirmed at verify.
  - phases/6-verify.md cues the AI to (a) fill the expectations before build and (b) confirm each at the gate — tying the gate to build-correctness, not just "tests pass".
  - The block is plain markdown mirroring §6's existing `### Deep checks` — it does NOT add or alter any engine-parsed seam or form-tag region (the engine reads the scaffold unchanged).
  - All 3 TASK.md.tmpl copies + all 3 phases/6-verify.md copies stay md5-equal; the guide passes wording-lint; add.py is untouched (ENGINE_MD5 holds); the existing §6 checklist + Deep-checks + GATE RECORD are retained.
</must>
Reject:
<reject>
  - an expectation row with no observable evidence / no `confirmed by` -> "unobservable_expectation"  (the cue must forbid a vacuous restatement)
  - the block edits or shadows an engine-parsed seam / form-tag region -> "parsed_seam_touched"
  - a parity copy is left un-updated (template or guide) -> "parity_broken"
</reject>
After:
<after>
  - A task author fills §6 Build expectations before build; at verify each row is confirmed against real evidence, catching a test-green-but-wrong build.
  - test_template_form_tags asserts the `### Build expectations` block exists and the engine-parsed seams are untouched; all parity copies md5-equal; wording-lint + suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The block stays AI-filled markdown, NOT an engine-enforced field — lowest confidence because a reader may expect the engine to GATE on unfilled expectations; if wrong: scope creep into add.py (a parser + a new reject) that this task explicitly defers. Mitigation: §6's existing checklist/Deep-checks are also AI/human-filled and un-parsed — this mirrors them; an engine gate is a separate future task.
  - [x] placement INSIDE §6 keeps the 8-phase flow unchanged — CONFIRMED: kept in §6, full suite 1276 green, no flow change.
  - [x] book-accord — CLOSED before PASS (the human chose close-before-gate): docs/08's "Part one" + "The verification checklist" now name the pre-declared build-expectation confirmation; mirrored across all 4 copies (add-method/docs · repo-root · .add/docs · _bundled), md5-equal; suite 1276 green.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: build-expectations block present in §6
  Given TASK.md.tmpl's §6 VERIFY section
  When it is read
  Then a "### Build expectations" block exists with a fill-before-build cue and an observable + "confirmed by" row shape
  And the existing §6 checklist, "### Deep checks", and "### GATE RECORD" remain

Scenario: derived-from-2-and-3 cue
  Given the Build expectations block
  When its cue is read
  Then it states expectations are derived from §2 SCENARIOS + §3 CONTRACT and are evidence-you-can-see (not a test-name restatement)

Scenario: verify guide cues fill-and-confirm
  Given phases/6-verify.md
  When it is read
  Then it cues filling the expectations BEFORE build and confirming each at the gate (build-correctness, not just green)

Scenario: engine reads the scaffold unchanged
  Given a real project scaffolded from the amended template
  When add.py parses it
  Then no engine-parsed seam or form-tag region changed (parsed_seam_touched stays impossible)

Scenario: parity and lint hold
  Given the template + guide are edited
  When the suite runs
  Then all 3 TASK.md.tmpl copies and all 3 phases/6-verify.md copies are md5-equal, wording-lint is clean
  And add.py is unchanged (ENGINE_MD5 pin holds)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: tooling/templates/TASK.md.tmpl  (×3 parity) + skill/add/phases/6-verify.md (×3 parity)
  A template/guide-convention contract: the checkable seam is a STRUCTURAL block + a cue,
  asserted by test_template_form_tags.py. NOT an HTTP shape, NOT an engine field.

Structural invariants (all must hold):
  - TASK.md.tmpl §6 contains a "### Build expectations" block (heading present), shaped like
    the existing "### Deep checks": a fill-before-build cue + observable rows each with "confirmed by"
  - the block's cue names the derivation (§2 SCENARIOS + §3 CONTRACT) and "evidence-you-can-see"
  - phases/6-verify.md cues fill-before-build AND confirm-each-at-gate
  - RETAINED: §6 checklist · "### Deep checks" · "### GATE RECORD" · the 6 form-tag regions
  - SEAM: no engine-parsed seam / form-tag region added or shadowed (engine reads scaffold unchanged)
  - PARITY: md5 equal across the 3 TASK.md.tmpl copies AND the 3 phases/6-verify.md copies
  - LINT: wording-lint clean
  - ENGINE: add.py ENGINE_MD5 unchanged (no engine edit)

Frozen tokens (must appear verbatim):
  "### Build expectations"  ·  "confirmed by"  ·  "before build"

reject codes -> { unobservable_expectation | parsed_seam_touched | parity_broken }
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-18)
Least-sure flag surfaced at freeze: [spec] the build-expectations block stays AI-filled markdown, NOT an engine-gated field; if wrong: scope creep into add.py (a parser + a new reject) this task defers. Mitigated: it mirrors §6's existing un-parsed "### Deep checks"; an engine gate is a separate future task.
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

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/skill/add/phases/6-verify.md` `.claude/skills/add/phases/6-verify.md` `add-method/src/add_method/_bundled/skill/add/phases/6-verify.md` `add-method/docs/08-step-6-verify.md` `add-method/src/add_method/_bundled/docs/08-step-6-verify.md`   <TASK.md.tmpl §6 + the 6-verify guide + the docs/08 book accord, each across its parity trees>
Strategy (ordered batches): 1. add the §6 Build-expectations block to `TASK.md.tmpl` 2. add the matching cue to the `6-verify.md` phase guide 3. mirror the docs/08 book accord — all across their parity trees (TASK.md.tmpl ×3 incl. the walk-excluded `.add/tooling/templates`; docs/08 ×4 incl. the walk-excluded `.add/docs` + the repo-root `08-step-6-verify.md` declarable only as a bare name).
Safety rule (feature-specific): every parity set stays md5-equal after each edit; the §6 placeholders stay multi-word so the frozen `</?([a-z_]+)>` tag census is unchanged; the engine (add.py) is never touched.
Code lives in: the template + guide + book parity trees (a template/guide/prose edit — no `./src/`).
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

- [x] all tests pass — full suite 1276 green
- [x] coverage did not decrease — added BuildExpectationsBlock (5 tests); removed none
- [x] no test or contract was altered during build — §3 frozen; template + guide edited, tests only ADDED
- [x] the green was EARNED, not gamed — tests assert the real block + seam-untouched + 3-tree parity; a template without the block goes red (proven RED-first)
- [x] concurrency / timing of the risky operation is safe — N/A (static template/guide edit)
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A (prose; no deps)
- [x] layering & dependencies follow CONVENTIONS.md — block is plain markdown mirroring `### Deep checks`; no engine-parsed seam touched; ENGINE_MD5 holds
- [x] a person reviewed and approved the change — Tin Dang approved PASS at the verify gate (2026-06-18)

### Build expectations — what "correct" looks like (confirmed at this gate)
- [x] TASK.md.tmpl §6 carries a "### Build expectations" block (fill-before-build cue, observable+confirmed-by rows) — confirmed by test_build_expectations_block_present_in_section6 + test_block_cue_is_observable_and_derived
- [x] phases/6-verify.md cues fill-before-build + confirm-at-gate — confirmed by test_verify_guide_cues_fill_and_confirm
- [x] engine reads the scaffold unchanged; 3 template + 3 guide copies md5-equal — confirmed by test_engine_seams_untouched_by_the_block + test_template_and_guide_parity_three_trees + the full suite (1276 green)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — N/A (no new code symbols; template + guide + test edit)
- [ ] DEAD-CODE (code) — N/A
- [x] SEMANTIC (prose / non-code) — read the amended §6 + 6-verify.md + the docs/08 book accord (Part one + The verification checklist) in full: the Build-expectations block is additive (checklist · Deep checks · GATE RECORD all retained), the placeholders are multi-word so the frozen tag census is unchanged, the guide cue ties the gate to build-correctness, and docs/08 now states the same in the book (4 copies md5-equal). This very §6 block is the feature dogfooding itself.

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
