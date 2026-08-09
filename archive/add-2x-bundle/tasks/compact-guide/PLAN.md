# TASK: compact-foundation.md ritual (per-spec sections) + SKILL milestone-close cue

slug: compact-guide · created: 2026-06-15 · stage: mvp
autonomy: conservative   <!-- additive method-doc (new guide ×3 + SKILL cue ×3), not a frozen-invariant amend — risk normal, but the milestone runs conservative so the human gates the live-method addition. -->
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
  - NEW `compact-foundation.md` in 3 CANONICAL skill homes (byte-identical, like fold.md): `add-method/skill/add/` · `add-method/src/add_method/_bundled/skill/add/` · `.claude/skills/add/` — the per-spec compaction ritual realizing the frozen contract.
  - `SKILL.md` ×3 (same 3 homes) — add the milestone-close cue at L88–89 (right after "run the retrospective consolidation … read `fold.md`") → "then (or on demand) compact stable entries — read `compact-foundation.md`".
  - the frozen contract `./.add/tasks/compact-contract/compaction-contract.md` (FROZEN @ v1) — the source the ritual procedural-izes (eligibility · 5 per-spec shapes · newest-first · preservation · the door · 3 reject codes).
  - `fold.md` (already amended by invariant-amend) — the SIBLING ritual whose form/voice compact-foundation.md mirrors (fold appends/prepends; compaction collapses the tail — separate steps).
Context (working folder): the guide-home set (`.claude/skills/add/*.md`: fold · intake · run · loop …) — compact-foundation.md joins it; book ch. `09-the-loop.md` is compact-book-align's, not this task's.
Honors (patterns / conventions): mirror-clause-all-copies (guide + SKILL edited in all 3 homes, md5-parity) · fold.md's "AI proposes, human confirms" voice · the ritual is convention-guided (no engine command) · compaction is SEPARATE from fold — task-delta only, defers to the frozen contract.
Anchors the contract cites: `compact-foundation.md` (the new ritual) · the SKILL.md milestone-close cue line · the frozen compaction-contract · fold.md (the sibling).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: compact-foundation.md — the convention-guided compaction ritual (one section per spec) realizing the frozen contract, plus a SKILL.md milestone-close cue; both mirrored byte-identical across the 3 skill homes.
Framings weighed: ONE guide with a section per spec (chosen — mirrors fold.md's single-ritual shape; the maintainer reads one place) · 5 separate guides (over-surface) · fold it into fold.md (rejected — compaction is SEPARATE from fold per the contract)
Must:
<must>
  - THE RITUAL: compact-foundation.md states the steps — gather eligible entries → propose the per-spec rolled line → human confirms → write the settled line at the TAIL — in fold.md's "AI proposes, human confirms" voice.
  - PER-SPEC SECTIONS: one section each for PROJECT §Spec · PROJECT §Key-Decisions · CONVENTIONS · GLOSSARY · MODEL_REGISTRY, each naming that spec's rolled-line shape from the frozen contract.
  - RESTATE THE CONTRACT: the ritual restates eligibility (shipped + zero open residues), newest-first (settled line at the tail), and preservation (never delete · git/archive pointer survives · OPEN residues stay).
  - REJECT CODES: name the 3 reject codes (open-residue-version · trail-loss · wrong-order) as judgment checks.
  - SKILL CUE: SKILL.md (3 homes) cues compact-foundation.md at milestone close, AFTER the fold cue, naming compaction as separate-from-fold.
  - MIRROR PARITY: compact-foundation.md + SKILL.md are byte-identical across the 3 skill homes; the engine is untouched.
</must>
Reject:
<reject>
  - compact-foundation.md or SKILL.md is not byte-identical across the 3 homes -> "mirror-drift"
  - the ritual's eligibility / shapes / reject codes diverge from the frozen contract -> "contract-drift"
  - the ritual introduces an add.py command or check enforcement -> "engine-creep"
</reject>
After:
<after>
  - compact-foundation.md exists in 3 byte-identical homes with a section per spec realizing the frozen contract; SKILL.md cues it at milestone close in all 3 homes; add.py is unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ one guide with per-spec sections (not 5 guides) is right — lowest confidence because the GLOSSARY/MODEL_REGISTRY sections are near-empty today and could read as filler; if wrong: two thin sections. Mitigation: keep each to 1–2 forward-looking lines (the milestone's minimal/forward-looking guard).
  - [ ] the SKILL cue belongs after the fold cue (L88–89), not as a new section — placement; treated settled (compaction follows fold at close).
  - [ ] compact-foundation.md mirrors fold.md's voice + length — style; treated settled.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the ritual realizes the frozen contract
  Given compact-foundation.md
  When a maintainer reads it
  Then it states eligibility (shipped + zero open residues), newest-first (settled line at the tail), preservation (never delete + git pointer), and the 3 reject codes
  And these match the frozen compaction-contract (no divergence)

Scenario: one section per spec, each with its shape
  Given the ritual
  When read
  Then it has a section for each of PROJECT §Spec, PROJECT §Key-Decisions, CONVENTIONS, GLOSSARY, MODEL_REGISTRY
  And each names that spec's rolled-line shape

Scenario: SKILL cues compaction at milestone close
  Given SKILL.md
  When read at the milestone-close guidance
  Then it points to compact-foundation.md after the fold cue
  And names compaction as separate-from-fold

Scenario: the guide + cue are byte-identical across the 3 homes
  Given the 3 skill homes
  When the guide and SKILL cue land
  Then compact-foundation.md and SKILL.md are md5-identical across all 3
  And a home left out of sync is rejected with "mirror-drift"

Scenario: the ritual stays convention-guided
  Given the ritual
  When reviewed for engine surface
  Then it introduces no add.py command or check enforcement
  And add.py is unchanged (rejected with "engine-creep" otherwise)

Scenario: the ritual does not drift from the contract
  Given the ritual's eligibility, shapes, and reject codes
  When compared to the frozen contract
  Then they match exactly
  And a divergence is rejected with "contract-drift"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
COMPACT-GUIDE CONTRACT — realizes compaction-contract.md @ v1 (convention-guided)

deliverable: compact-foundation.md (NEW), byte-identical in 3 homes —
  add-method/skill/add · add-method/src/.../_bundled/skill/add · .claude/skills/add

structure (the ritual document):
  # Foundation compaction — collapse the stable tail
  ## When        — at milestone close (after fold) or on demand; a convention, NO add.py command
  ## Eligibility  — shipped + zero open residues  (else `open-residue-version`)
  ## The ritual   — gather eligible → propose the per-spec rolled line → human confirms → write at the TAIL (newest-first)
  ## Per-spec shapes (one section each, from the frozen contract):
       PROJECT §Spec · PROJECT §Key-Decisions · CONVENTIONS · GLOSSARY (forward-looking) · MODEL_REGISTRY (forward-looking)
  ## Preservation — never delete · git/archive pointer survives · OPEN residues stay  (else `trail-loss`)
  ## Reject       — `open-residue-version` · `trail-loss` · `wrong-order`
  ## Seam         — distinct from engine `add.py compact`; mirrors fold's "AI proposes, human confirms"

SKILL.md cue (3 homes, byte-identical): at milestone close, AFTER the fold cue (≈L88–89) add
  "then (or on demand) compact the stable tail — read `compact-foundation.md` (separate from fold)".

mirror parity: compact-foundation.md + SKILL.md md5-identical across 3 homes.  drift -> "mirror-drift"
engine: UNCHANGED — no add.py edit (else "engine-creep").
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-15
Least-sure flag surfaced at freeze: [spec] the GLOSSARY/MODEL_REGISTRY sections risk reading as filler (near-empty today) — kept to 1–2 forward-looking lines per the milestone's minimal guard.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: each Must + each Reject has a test; assert the guide structure + md5 parity + contract fidelity (behavioral, not bare token).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_exists_3_homes: assert compact-foundation.md exists in all 3 skill homes
  - test_guide_mirror_parity: md5 the 3 homes / assert all equal [guards mirror-drift]
  - test_per_spec_sections: assert the guide names all 5 spec sections (PROJECT §Spec · §Key-Decisions · CONVENTIONS · GLOSSARY · MODEL_REGISTRY) + their rolled-line shapes
  - test_ritual_realizes_contract: assert the guide states eligibility (shipped + zero open residues), newest-first/tail, preservation (never delete + git), and the 3 reject codes — matching the frozen contract [guards contract-drift]
  - test_skill_cue_3_homes: assert SKILL.md (3 homes) cues compact-foundation.md at milestone close after fold, byte-identical
  - test_no_engine_creep: assert add.py (both homes) gained no compaction command/reject-code enforcement [guards engine-creep]
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/compact-foundation.md` `add-method/src/add_method/_bundled/skill/add/compact-foundation.md` `.claude/skills/add/compact-foundation.md` `add-method/skill/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/tooling/test_per_step_hooks.py` `add-method/tooling/test_wording_lint.py` `./tests/`   — new guide ×3 + SKILL cue ×3 + the 2 wording-lint inventory guards (register the new surface file: count 24→25 + membership assert; NOT engine behavior — add.py untouched) + this task's guard tests. NO `add.py` (convention-guided seam).
Strategy (ordered batches): 1. write `./tests/` red · 2. write compact-foundation.md ONCE → copy byte-identical to the 3 homes (md5) · 3. add the SKILL cue ONCE → apply byte-identical to the 3 SKILL.md homes (md5) · 4. run green.
Safety rule (feature-specific): each mirrored file is written from ONE source (write-once-copy) so md5 parity is STRUCTURAL; never edit the frozen contract to fit.
Code lives in: the 3 compact-foundation.md homes + the 3 SKILL.md homes
Constraints: do NOT change any test or the frozen contract; no `add.py`/engine edit; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — compact-guide suite 6/6 GREEN (`tests/test_compact_guide.py`); full engine suite 1027/1027 OK (`add-method/tooling`).
- [x] coverage did not decrease — STRENGTHENED: `test_wording_lint.py` gained `assertIn("compact-foundation.md", names)`; no assert removed.
- [⚠] no test or contract was altered during build — the FROZEN §3 and this task's red suite are UNCHANGED (tamper-tripwire clean). DISCLOSED: 2 PRE-EXISTING engine guards were UPDATED to REGISTER the new surface file — `test_per_step_hooks.py` (count 24→25) + `test_wording_lint.py` (count 24→25 + membership assert). Additive registration of a deliberately-added skill-surface guide, NOT a weakening; declared in §5 Scope and re-anchored via a tests→build re-cross (scope_violation cleared). Independent refute-read confirmed: "additive membership registrations … no existing check was disabled or loosened."
- [x] the green was EARNED, not gamed — independent adversarial refute-read (general-purpose subagent) VERDICT: tests behavioral not vacuous (PASS), no engine-creep (PASS, grep clean both add.py homes), mirror parity real (PASS, md5 5c9a2812 / 877808b9), no weakened guard (PASS). One disclosed deviation surfaced below (heading) — escalated to the human gate, not auto-passed.
- [x] concurrency / timing — N/A: static method-doc prose (no runtime path).
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: prose guide; engine untouched.
- [x] layering & dependencies follow CONVENTIONS.md — mirror-clause-all-copies honored (guide ×3 + SKILL ×3 byte-identical); convention-guided boundary preserved (no `add.py` command/enforcement — `test_no_engine_creep` green).
- [x] a person reviewed and approved the change — Tin Dang, verify gate 2026-06-15: PASS, accepting the heading deviation (the wording-guard outranks the literal `## Seam` sketch).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read `compact-foundation.md` end-to-end + the SKILL cue + the FROZEN compaction-contract. Confirmed the ritual restates eligibility (shipped + zero open residues), newest-first (settled line at the TAIL, live records on top), preservation (never delete + surviving git/archive pointer + OPEN residues stay), all 3 reject codes (`open-residue-version` · `trail-loss` · `wrong-order`), 5 per-spec shape sections, and the convention-guided boundary vs engine `add.py compact`. Wording-lint: 0 findings (banned slang seam/fold/survivor absent from prose; `fold.md` kept as a code-spanned reference). No internal contradiction; no broken cross-ref.
  ⚠ DISCLOSED DEVIATION (human call): the frozen §3 sketch names the final section `## Seam`; the shipped guide titles it **`## Distinct from \`add.py compact\``**. FORCED, not chosen — the frozen ubiquitous-language guard BANS "seam" on the skill surface, so the contract's literal heading is unshippable (would turn the engine suite red). Content is faithful and the task's `contract-drift` reject code (scoped to eligibility/shapes/reject-codes) is NOT triggered; only the literal heading differs. Options at the gate: PASS (accept the compliant heading — recommended) · or a change-request to re-freeze §3's heading sketch.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-15
Note: PASS accepts the disclosed `## Seam` → `## Distinct from \`add.py compact\`` heading deviation (forced by the frozen ubiquitous-language guard; content faithful, no reject code triggered). The 2 wording-lint inventory guards were updated additively to register the new surface file (declared in §5, re-anchored).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): wording-lint banned_idiom/slang findings over the skill surface · mirror-parity md5 drift across the 3 homes · scope_violation on tasks that add a skill guide.
Spec delta for the next loop: a "new skill-surface guide" change has a fixed engine-registration cost (wording-lint count + membership) — the next such task should declare the 2 guard files in §5 from the start, not discover it at the gate.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [ADD · folded] a frozen contract's prose sketch (a section heading) can collide with a SEPARATE frozen engine guard discovered only at build; the realization honors the harder engine guard and DISCLOSES the deviation at the gate, never silently — and the human, not the AI, accepts it (evidence: §3 sketched `## Seam`, engine `test_slang_absent_extended_surface` bans "seam" on the surface → shipped `## Distinct from add.py compact`, escalated + human-PASSed at the verify gate).
  - [SDD · folded] adding a new skill-surface guide is not free: the wording-lint inventory guards count surface files, so a new guide REQUIRES a count+membership registration in those guards — fold that into §5 Scope up front (evidence: the new guide turned the engine suite 1027→6-fail; `test_wording_surface_count_unchanged` 24→25 + `test_surface_files_cover_the_contract` membership assert).
  - [TDD · folded] §5 Scope is anchored into state.json at the tests→build crossing; amending §5 AFTER the crossing requires a tests→build re-cross to re-anchor the declared list, else the scope-gate refuses the verify gate against the stale anchor (evidence: scope_violation persisted after the §5 edit until `phase tests` + `advance` re-snapshotted; check 14→13 warnings).
  - [UDD · folded] the ubiquitous-language ban is PROSE-ONLY — a banned term survives inside a `code span` or fence; user-facing guides reference doc names as code-spans (`fold.md`) and use domain terms ("retrospective consolidation", "foundation spec") in prose (evidence: `fold.md` code-spans pass the scan; bare "fold"/"survivor"/"seam" prose failed `test_slang_absent_extended_surface`).
